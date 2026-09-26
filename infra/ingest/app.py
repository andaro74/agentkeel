"""refagent's corpus ingest stack, AgentkeelIngest (Security seat; SPEC/03 §6, seed S5's pipeline).

Deployed by the human with admin, from a clean checkout, as the bootstrap
stack is; no workflow and no platform role deploys it (the deploy role may
touch `stack/agentkeel-*` only, the developer role deploys nothing).
SPEC/03 §6 names every part before this file:

    cd infra/ingest && npx aws-cdk@2 diff && npx aws-cdk@2 deploy

Every name carries the agent's (`agentkeel-refagent-*`): the corpus is
refagent's, scanned with refagent's guardrail, and M05 allows no surface
shared between agents (platform-architect on 2e93d27, F5).

- **quarantine**: versioned, private, TLS only. The human uploads here, and
  every new object version invokes the promoter. The eval role may read
  versions, so "in quarantine" is S3's word, not only the promoter's;
- **the promoter**: one Lambda (`promoter.py`, inlined: the account is not
  CDK-bootstrapped, so there is no asset bucket). It takes the sha256,
  scans the text with refagent's pinned guardrail and records the result,
  and copies the bytes to production under `<sha256><extension>` only if
  `data/corpus/admitted.yaml` names that sha256 (the extension is the
  admitted key's, so M04's knowledge base can parse it). The list is read
  here, at synth; each record carries its fingerprint, so what the
  deployed promoter held can be compared with `admitted.yaml` at a commit;
- **production**: versioned, private, TLS only, Object Lock COMPLIANCE for
  1 day (the human as Security, 2026-09-25). Its policy lets only the
  promoter put, lets nobody delete, replicate into it, hold or re-date an
  object, or change its lock, and lets the eval role read objects and
  versions. The admin can still remove the policy: that bypass is named in
  SPEC/03 §8 and is a landing-zone control (an SCP), deferred;
- **the record**: one item per object version that reached quarantine,
  written once, with deletion protection; its resource policy lets the
  eval role read it.

Every role here carries the deploy boundary, as the bootstrap stack's do.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import aws_cdk as cdk
import yaml
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

from src.verdict import fingerprint_of

REGION = "us-west-2"
AGENT = "refagent"
ROOT = Path(__file__).resolve().parents[2]
PROMOTER = Path(__file__).parent / "promoter.py"
ADMITTED = ROOT / "data" / "corpus" / "admitted.yaml"
MANIFEST = ROOT / "agents" / AGENT / "manifest.yaml"
DEPLOY_BOUNDARY_NAME = "agentkeel-deploy-boundary"  # the bootstrap stack's; named, not imported
EVAL_ROLE_NAME = "agentkeel-evals"
LOCK_DAYS = 1  # COMPLIANCE; the human as Security, 2026-09-25. Lowering it is a relaxation (pr1.md ruling 5)
INLINE_MAX = 4096  # CloudFormation's limit on a Lambda's inline code
# What nobody may do to a promoted object, the promoter included: hide it behind a
# delete marker, write around the promoter by replication, pin it past its day, or
# change the lock (security-reviewer F1 and platform-architect F3 on 2e93d27).
NOBODY = ["s3:DeleteObject", "s3:DeleteObjectVersion", "s3:ReplicateObject", "s3:ReplicateDelete",
          "s3:PutObjectLegalHold", "s3:PutObjectRetention", "s3:PutBucketObjectLockConfiguration"]


def admitted_extensions(path: Path = ADMITTED) -> dict[str, str]:
    """sha256 -> the extension of its admitted key (`.md`). The promoter's whole list."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {e["sha256"]: Path(e["key"]).suffix for e in sorted(entries, key=lambda e: e["sha256"])}


def admitted_fingerprint(path: Path = ADMITTED) -> str:
    """The corpus fingerprint of the list the promoter is built with (SPEC/03 §2)."""
    return fingerprint_of(path.read_text(encoding="utf-8"))


def promoter_source(path: Path = PROMOTER) -> str:
    source = path.read_text(encoding="utf-8")
    if len(source.encode("utf-8")) > INLINE_MAX:
        raise ValueError(f"{path.name} is {len(source.encode('utf-8'))} bytes; an inline Lambda takes {INLINE_MAX}")
    return source


class IngestStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        iam.PermissionsBoundary.of(self).apply(iam.ManagedPolicy.from_managed_policy_name(
            self, "DeployBoundary", DEPLOY_BOUNDARY_NAME))  # fmt: skip
        eval_role = iam.ArnPrincipal(f"arn:aws:iam::{self.account}:role/{EVAL_ROLE_NAME}")
        pin = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["guardrail"]
        guardrail = f"arn:aws:bedrock:{self.region}:{self.account}:guardrail/{pin['id']}"
        prefix = f"agentkeel-{AGENT}"

        quarantine_name = f"{prefix}-quarantine-{self.account}"
        quarantine = s3.Bucket(
            self, "Quarantine", bucket_name=quarantine_name, versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL, enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED, removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip
        production = s3.Bucket(
            self, "Production", bucket_name=f"{prefix}-corpus-{self.account}", versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL, enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED, removal_policy=cdk.RemovalPolicy.RETAIN,
            object_lock_enabled=True,
            object_lock_default_retention=s3.ObjectLockRetention.compliance(cdk.Duration.days(LOCK_DAYS)),
        )  # fmt: skip
        record = dynamodb.Table(
            self, "Record", table_name=f"{prefix}-ingest-record",
            partition_key=dynamodb.Attribute(name="key", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="version_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True),
            deletion_protection=True, removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip

        role = iam.Role(
            self, "PromoterRole", role_name=f"{prefix}-promoter",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="agentkeel: refagent's corpus promoter. Promotes only what admitted.yaml names (SPEC/03 §6).",
        )  # fmt: skip
        log_group = logs.LogGroup(self, "PromoterLogs", log_group_name=f"/agentkeel/{AGENT}/ingest/promoter",
                                  retention=logs.RetentionDays.ONE_YEAR, removal_policy=cdk.RemovalPolicy.RETAIN)
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadQuarantine", actions=["s3:GetObject", "s3:GetObjectVersion"],
            # By name, not by reference: the bucket waits on the promoter's permission.
            resources=[f"arn:aws:s3:::{quarantine_name}/*"]))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="WriteProduction", actions=["s3:PutObject"], resources=[production.arn_for_objects("*")]))
        role.add_to_policy(iam.PolicyStatement(
            sid="WriteTheRecord", actions=["dynamodb:PutItem"], resources=[record.table_arn]))
        role.add_to_policy(iam.PolicyStatement(
            sid="ScanWithRefagentsGuardrail", actions=["bedrock:ApplyGuardrail"],
            resources=[guardrail, f"{guardrail}:*"]))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogs", actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[f"{log_group.log_group_arn}"]))  # fmt: skip

        # No reserved concurrency: an account at the new-account quota of 10 may
        # reserve none, and a refused create leaves the retained resources behind
        # (security-reviewer on 2e93d27, F7). Uploads are a handful, by hand.
        function = lambda_.Function(
            self, "Promoter", function_name=f"{prefix}-promoter", role=role,
            runtime=lambda_.Runtime.PYTHON_3_14, handler="index.handler",
            code=lambda_.Code.from_inline(promoter_source()), timeout=cdk.Duration.seconds(60),
            memory_size=256, log_group=log_group,
            description=f"refagent's corpus promoter; admitted fingerprint {admitted_fingerprint()[:12]}",
            environment={
                "ADMITTED": json.dumps(admitted_extensions()), "ADMITTED_FINGERPRINT": admitted_fingerprint(),
                "PRODUCTION": production.bucket_name, "RECORD": record.table_name,
                "GUARDRAIL_ID": pin["id"], "GUARDRAIL_VERSION": pin["version"],
            },
        )  # fmt: skip

        # Quarantine invokes the promoter on every new object version. Wired on the
        # CfnBucket, not add_event_notification: that renders a custom-resource
        # Lambda from an asset, and this account has no asset bucket.
        invoke = lambda_.CfnPermission(
            self, "QuarantineInvokesPromoter", action="lambda:InvokeFunction",
            function_name=function.function_arn, principal="s3.amazonaws.com",
            source_arn=f"arn:aws:s3:::{quarantine_name}", source_account=self.account,
        )  # fmt: skip
        cfn_quarantine = quarantine.node.default_child
        cfn_quarantine.notification_configuration = s3.CfnBucket.NotificationConfigurationProperty(
            lambda_configurations=[s3.CfnBucket.LambdaConfigurationProperty(
                event="s3:ObjectCreated:*", function=function.function_arn)])  # fmt: skip
        cfn_quarantine.add_resource_dependency(invoke)
        quarantine.add_to_resource_policy(iam.PolicyStatement(
            sid="TheEvalRoleReadsVersions", principals=[eval_role],
            actions=["s3:GetObjectVersion", "s3:ListBucketVersions"],
            resources=[quarantine.bucket_arn, quarantine.arn_for_objects("*")],
        ))  # fmt: skip

        # Production: only the promoter puts; nobody deletes, replicates in, holds,
        # re-dates or re-locks; the eval role reads objects and versions.
        production.add_to_resource_policy(iam.PolicyStatement(
            sid="OnlyThePromoterPromotes", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=["s3:PutObject"], resources=[production.arn_for_objects("*")],
            conditions={"ArnNotEquals": {"aws:PrincipalArn": role.role_arn}},
        ))  # fmt: skip
        production.add_to_resource_policy(iam.PolicyStatement(
            sid="NobodyHidesOrReLocksAPromotedObject", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=NOBODY, resources=[production.bucket_arn, production.arn_for_objects("*")],
        ))  # fmt: skip
        production.add_to_resource_policy(iam.PolicyStatement(
            sid="TheEvalRoleReads", principals=[eval_role],
            actions=["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket", "s3:ListBucketVersions"],
            resources=[production.bucket_arn, production.arn_for_objects("*")],
        ))  # fmt: skip
        record.add_to_resource_policy(iam.PolicyStatement(
            sid="TheEvalRoleReadsTheRecord", principals=[eval_role],
            actions=["dynamodb:GetItem", "dynamodb:Query"], resources=["*"],
        ))  # fmt: skip

        cdk.CfnOutput(self, "QuarantineBucket", value=quarantine.bucket_name)
        cdk.CfnOutput(self, "ProductionBucket", value=production.bucket_name)
        cdk.CfnOutput(self, "RecordTable", value=record.table_name)
        cdk.CfnOutput(self, "AdmittedFingerprint", value=admitted_fingerprint())


app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = IngestStack(
    app, "AgentkeelIngest",
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M03 corpus ingest for refagent: quarantine, promoter, locked production, record. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
# One suppression per resource, each naming the case it serves: M03's seed S5, the
# unsigned amendment this stack exists to keep out, and SPEC/03 §6's line.
SUPPRESSIONS = {
    "PromoterRole/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/03 §6, the promoter, which keeps M03's seed S5 (the unsigned amendment) out of production. Four "
        "wildcards, each one bucket's, one guardrail's or one log group's: GetObject on quarantine/* because any "
        "key may be uploaded; PutObject on production/* because the key is the sha256 of the bytes; "
        "ApplyGuardrail on refagent's guardrail and <arn>:*, its numbered versions; its own log group's "
        "streams (:*). The role carries the deploy boundary.",
    ),
    "Quarantine/Resource": (
        "AwsSolutions-S1",
        "SPEC/03 §6: M03's seed S5 is read from the promoter's record (one item per object version) and from "
        "S3's own versions of this bucket and of production, not from access logs. S3 access logs and data "
        "events on the corpus buckets are M05's, evidence integrity (security-reviewer NOTE 6 at M03 PR 1, "
        "extended to quarantine at M03 PR 2).",
    ),
    "Production/Resource": (
        "AwsSolutions-S1",
        "SPEC/03 §6: M03's seed S5 is read from the promoter's record and from this bucket's versions. Every "
        "object here is locked (COMPLIANCE, 1 day), only the promoter may put one, and nobody may delete one. "
        "S3 access logs and data events are M05's (security-reviewer NOTE 6 at M03 PR 1).",
    ),
}
for path, (rule, reason) in SUPPRESSIONS.items():
    NagSuppressions.add_resource_suppressions_by_path(stack, f"AgentkeelIngest/{path}", [{"id": rule, "reason": reason}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
