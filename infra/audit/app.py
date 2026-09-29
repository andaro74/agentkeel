"""Delivery to the security account, from the agent account: AgentkeelAudit (Security seat; SPEC/05 §6).

Deployed by the human with admin, by hand, in the agent account
(581208540944), after `infra/security/` is deployed in the security
account: the audit bucket's policy must admit this stack's trail and flow
log before either can deliver. No workflow and no platform role deploys it.
Outside the bootstrap on purpose: the bootstrap template has 2,027 bytes
left (milestones/M05/runs/bootstrap_size.md; finding 15).

    cd infra/audit && npx aws-cdk@2 diff

What it makes, each named in SPEC/05 §6 before this file:

- **the trail** `agentkeel-audit`, every region, delivering to the audit
  bucket under `AWSLogs/581208540944/`: management events (the refusals of
  seeds S3 and S6, S7's attach and its model call; IAM's are global, so the
  trail is multi-region); the audit bucket's object events under `agents/`,
  `test/` and `envelopes/` (S2, S6, S4's refusal event and who wrote it),
  but not under `AWSLogs/`, where it delivers, so its own writes make no
  events (finding 17); the production corpus bucket's object events
  (`open.md` row 13); and AgentCore runtime invocations, which CloudTrail
  records as data events only (S4's and S7's calls);
- **the VPC's flow log** to the audit bucket at one-minute aggregation
  (seed S1). The bootstrap's flow log to CloudWatch in this account stays
  as it is;
- **refagent's stand-in** (SPEC/05 §2), `agentkeel-refagent-standin` under
  `/agentkeel/agents/`, with the agent boundary and refagent's explicit
  denies, and in its own policy the two actions seeds S2 and S3 attempt, so
  that the refusal can only be the control named for each: the audit
  bucket's policy for S2, the explicit denies for S3. Assumable by the
  human's admin user with MFA and by nothing else. It is not refagent: it
  carries refagent's denies, not refagent's grants, neither of which either
  attempt uses (SPEC/05 §8). Removed after S2 and S3 are read (`STANDIN`
  below; Security's constraint on PR 2);
- **the quarantine** (seed S7): `agentkeel-quarantine`, a policy that
  denies everything, attached to nothing. The human attaches it to
  refagent's own role with the one command `README.md` names, and detaches
  it with the other.

Every name here is fixed, so the security account's policy can name it
before it exists.
"""

from __future__ import annotations

import os
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_cloudtrail as cloudtrail
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

REGION = "us-west-2"
AGENT_ACCOUNT = "581208540944"
SECURITY_ACCOUNT = "897698239547"  # milestones/M05/runs/security_account.md
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"  # infra/security/; named, not imported
PRODUCTION_BUCKET = f"agentkeel-refagent-corpus-{AGENT_ACCOUNT}"  # infra/ingest/
TRAIL_NAME = "agentkeel-audit"  # the security account's bucket policy names this trail
VPC_PARAM = "/agentkeel/security/vpc-id"  # the bootstrap stack's
AGENT_ROLE_PATH = "/agentkeel/agents/"
BOUNDARY_NAME = "agentkeel-boundary"  # the agent plane's, the bootstrap stack's
STANDIN_NAME = "agentkeel-refagent-standin"  # the security account's bucket policy names this role
# Who may become the stand-in: the human's admin user in this account, with MFA (Unsure G on M05 PR 1).
ADMIN = f"arn:aws:iam::{AGENT_ACCOUNT}:user/hector.acevedo"
# True until seeds S2 and S3 are read (S3 after M05 PR 2's merge deploy, read at PR 3). The PR that
# reads S3 sets it False and the human redeploys this stack, which deletes the role.
STANDIN = True
QUARANTINE_NAME = "agentkeel-quarantine"
RUNTIME_LOG_GROUPS = f"arn:aws:logs:{REGION}:{AGENT_ACCOUNT}:log-group:/aws/bedrock-agentcore/runtimes/*"
# refagent's explicit denies, as the construct puts them on refagent's role (SPEC/05 §6). Repeated, not
# imported: the construct is deployed from main by the deploy role, this stack by hand.
GUARDRAIL_DENIED = ["bedrock:Create*Guardrail*", "bedrock:Update*Guardrail*", "bedrock:Delete*Guardrail*",
                    "bedrock:Put*Guardrail*", "bedrock:GetGuardrail", "bedrock:ListGuardrails"]
AGENT_DENIES = ["iam:*", *GUARDRAIL_DENIED, "logs:Delete*", "sts:AssumeRole", "s3:PutBucketPolicy"]
# The audit bucket's object events this trail logs: not AWSLogs/, where the trails and the flow log deliver.
LOGGED_PREFIXES = ["agents/", "test/", "envelopes/"]


class AuditStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        trail = self._trail()
        flow_log = ec2.CfnFlowLog(
            self, "FlowLogToTheAuditBucket",
            resource_id=ssm.StringParameter.value_for_string_parameter(self, VPC_PARAM),
            resource_type="VPC", traffic_type="ALL", log_destination_type="s3",
            log_destination=f"arn:aws:s3:::{AUDIT_BUCKET}", max_aggregation_interval=60,
            tags=[cdk.CfnTag(key="agentkeel:seed", value="M05 S1")],
        )  # fmt: skip
        quarantine = iam.ManagedPolicy(
            self, "Quarantine", managed_policy_name=QUARANTINE_NAME,
            description="agentkeel: attached by hand to an agent's own role, it denies that role everything (seed S7).",
            document=iam.PolicyDocument(statements=[iam.PolicyStatement(
                sid="QuarantinedDoesNothing", effect=iam.Effect.DENY, actions=["*"], resources=["*"])]),
        )  # fmt: skip
        cdk.CfnOutput(self, "TrailArn", value=trail.attr_arn)
        cdk.CfnOutput(self, "FlowLogId", value=flow_log.attr_id)
        cdk.CfnOutput(self, "QuarantinePolicyArn", value=quarantine.managed_policy_arn)
        if STANDIN:
            cdk.CfnOutput(self, "StandinRoleArn", value=self._standin().role_arn)

    def _trail(self) -> cloudtrail.CfnTrail:
        selector = cloudtrail.CfnTrail.AdvancedFieldSelectorProperty
        event = cloudtrail.CfnTrail.AdvancedEventSelectorProperty

        def objects(name: str, arns: list[str]) -> cloudtrail.CfnTrail.AdvancedEventSelectorProperty:
            return event(name=name, field_selectors=[
                selector(field="eventCategory", equal_to=["Data"]),
                selector(field="resources.type", equal_to=["AWS::S3::Object"]),
                selector(field="resources.ARN", starts_with=arns),
            ])  # fmt: skip

        return cloudtrail.CfnTrail(
            self, "Trail", trail_name=TRAIL_NAME, s3_bucket_name=AUDIT_BUCKET, is_logging=True,
            is_multi_region_trail=True, include_global_service_events=True, enable_log_file_validation=True,
            advanced_event_selectors=[
                event(name="Management events", field_selectors=[selector(field="eventCategory", equal_to=["Management"])]),
                objects("The audit bucket's attempts and evidence, not its delivery",
                        [f"arn:aws:s3:::{AUDIT_BUCKET}/{p}" for p in LOGGED_PREFIXES]),
                objects("The production corpus bucket (open.md row 13)", [f"arn:aws:s3:::{PRODUCTION_BUCKET}/"]),
                event(name="AgentCore runtime invocations", field_selectors=[
                    selector(field="eventCategory", equal_to=["Data"]),
                    selector(field="resources.type", equal_to=["AWS::BedrockAgentCore::Runtime"]),
                ]),
            ],
        )  # fmt: skip

    def _standin(self) -> iam.Role:
        """refagent's stand-in for seeds S2 and S3 (SPEC/05 §2): refagent's boundary and denies, and the attempt."""
        role = iam.Role(
            self, "Standin", role_name=STANDIN_NAME, path=AGENT_ROLE_PATH,
            assumed_by=iam.ArnPrincipal(ADMIN).with_conditions({"Bool": {"aws:MultiFactorAuthPresent": "true"}}),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_name(self, "AgentBoundary", BOUNDARY_NAME),
            max_session_duration=cdk.Duration.hours(1),
            description="agentkeel: refagent's stand-in for M05 seeds S2 and S3. Removed once both are read.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="RefagentsExplicitDenies", effect=iam.Effect.DENY, actions=AGENT_DENIES, resources=["*"]))
        # Granted here so that only the control named for each attempt can refuse it.
        role.add_to_policy(iam.PolicyStatement(
            sid="SeedS2PutAnywhereInTheAuditBucket", actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/*"]))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="SeedS3DeleteARuntimeLogStream", actions=["logs:DeleteLogStream"],
            resources=[RUNTIME_LOG_GROUPS, f"{RUNTIME_LOG_GROUPS}:log-stream:*"]))  # fmt: skip
        return role


app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = AuditStack(
    app, "AgentkeelAudit",
    env=cdk.Environment(account=AGENT_ACCOUNT, region=REGION),
    description="agentkeel M05: the trail and flow log to the security account, the stand-in, the quarantine. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
SUPPRESSIONS = {
    "Standin/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6, refagent's stand-in: its own policy grants what seeds S2 and S3 attempt, on the whole audit "
        "bucket and on every runtime log group, so that only the control named for each can refuse it. The "
        "wildcard on * is in the Deny, refagent's explicit denies, which must cover every resource.",
    ),
}
for path, (rule, reason) in SUPPRESSIONS.items():
    NagSuppressions.add_resource_suppressions_by_path(stack, f"AgentkeelAudit/{path}", [{"id": rule, "reason": reason}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
