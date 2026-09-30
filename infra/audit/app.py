"""Delivery to the security account, from the agent account: AgentkeelAudit (Security seat; SPEC/05 §6).

Deployed by the human with admin, by hand, in the agent account
(581208540944), after `infra/security/` is deployed in the security
account: the audit bucket's policy must admit this stack's trail and flow
log before either can deliver. No workflow and no platform role deploys it.
Outside the bootstrap on purpose: the bootstrap template had 2,093 bytes
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
  it with the other;
- **seed S1's origin, tried and removed** (M05 PR 2): `agentkeel-seed-s1`,
  a Lambda in one isolated subnet with refagent's security group, which
  opened one TCP connection to 1.1.1.1:443 at 13:54:22Z on 2026-09-29 and
  timed out. Its ENI recorded NODATA throughout, as the CloudShell VPC
  environment's had at 12:56:42Z. Two origins, one absence: the VPC has no
  route out, so the packet is dropped by routing before the security group
  or the network ACL sees it, and that drop leaves no flow record. S1 is
  refused and cannot be recorded; that is the finding (`rulings/pr2.md`
  ruling 9; SPEC/05 §5, §8). `S1_ORIGIN = False`: the next deploy deletes
  the function and its role. The code stays as the record of what ran.

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
from aws_cdk import aws_lambda as lambda_
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
# True until seeds S2 and S3 were read: S2 by M05 PR 2's run (388dbcf), S3 by PR 3's (5a5fe1e, refused, 199 s).
# False from M05 PR 3; the human redeploys this stack, which deletes the role and its policy (Security's constraint).
STANDIN = False
QUARANTINE_NAME = "agentkeel-quarantine"
# Seed S1's origin (M05 PR 2): tried at 13:54:22Z, 2026-09-29, and removed once it had shown that no flow record
# of S1 can exist in a VPC with no route out (rulings/pr2.md ruling 9). False deletes the function and its role.
S1_ORIGIN = False
S1_FUNCTION = "agentkeel-seed-s1"
# One subnet, so the function has one ENI and the run file names the one that carried the connect
# (security-reviewer on b167dd2, F2): the isolated subnet the CloudShell attempt used.
S1_SUBNET = "subnet-00008bbb7a11551a0"
# refagent's security group, which the construct makes: egress to the manifest's endpoints and nothing else.
# Named by id, read 2026-09-29 (describe-network-interfaces on refagent's runtime ENI); the construct does not
# publish it. If the construct ever replaces the group, this still names the old one and nothing notices, so
# the human records refagent's runtime ENI's group beside the invoke (security-reviewer on b167dd2, F1).
REFAGENT_SG = "sg-003ad866687089f27"
# The bootstrap stack's deploy boundary: the right kind for a role that is not an agent's, but an allow-all
# less a deny-list, so it caps nothing the inline grant does not; the inline grant is the ceiling (N1).
DEPLOY_BOUNDARY_NAME = "agentkeel-deploy-boundary"
S1_PROBE = '"""Seed S1\'s origin (SPEC/05 section 5): one TCP connect to 1.1.1.1:443 from the platform VPC. Decides nothing."""\nimport socket\nimport time\nfrom datetime import datetime, timezone\n\n\ndef handler(event, context):\n    started = datetime.now(timezone.utc).isoformat(timespec="seconds")\n    clock = time.monotonic()\n    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    sock.settimeout(5)\n    try:\n        sock.connect(("1.1.1.1", 443))\n        result = "connected"\n    except OSError as exc:\n        result = f"{type(exc).__name__}: {exc}"\n    finally:\n        sock.close()\n    return {"destination": "1.1.1.1", "port": 443, "connected": result == "connected", "result": result,\n            "started": started, "elapsed_s": round(time.monotonic() - clock, 1)}\n'
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
        if S1_ORIGIN:
            cdk.CfnOutput(self, "SeedS1Function", value=self._s1_origin().ref)

    def _s1_origin(self) -> lambda_.CfnFunction:
        """Seed S1's origin: in the platform VPC, behind refagent's security group, and nothing more."""
        # What Lambda needs to place its ENI in the subnet (AWS's VPC access permissions), and no more. Inline, in
        # the role itself: as a separate policy it was created after the function, and Lambda's
        # CreateNetworkInterface was refused six times (13:41:07 to 13:41:15Z, 2026-09-29) before it landed at
        # 13:41:21, so the function failed to stabilise and the deploy rolled back.
        place = iam.PolicyDocument(statements=[iam.PolicyStatement(
            sid="PlaceItsNetworkInterface",
            actions=["ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DescribeSubnets",
                     "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses"],
            resources=["*"],
        )])  # fmt: skip
        role = iam.Role(
            self, "SeedS1Role", role_name=f"{S1_FUNCTION}-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_name(self, "DeployBoundary",
                                                                            DEPLOY_BOUNDARY_NAME),
            inline_policies={"PlaceItsNetworkInterface": place},
            description="agentkeel: seed S1's origin, a Lambda in the platform VPC. Removed once S1 is read.",
        )  # fmt: skip
        return lambda_.CfnFunction(
            self, "SeedS1", function_name=S1_FUNCTION, role=role.role_arn, runtime="python3.14",
            handler="index.handler", timeout=15, memory_size=128,
            code=lambda_.CfnFunction.CodeProperty(zip_file=S1_PROBE),
            vpc_config=lambda_.CfnFunction.VpcConfigProperty(
                security_group_ids=[REFAGENT_SG],
                subnet_ids=[S1_SUBNET]),
            description="agentkeel M05 seed S1: one TCP connect to 1.1.1.1:443 from the platform VPC.",
        )  # fmt: skip

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
    "SeedS1Role/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6 as amended at M05 PR 2, seed S1's origin: the EC2 network-interface actions Lambda needs to "
        "place its ENI in a VPC, on *, as AWS's own VPC access policy grants them. Describe takes no resource; "
        "Create, Delete, Assign and Unassign could be scoped to the platform VPC and were not tried scoped, "
        "because a refused create would leave S1 unmade (security-reviewer on b167dd2, F3). No other grant; "
        "removed once S1 is read.",
    ),
    "Standin/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6, refagent's stand-in: its own policy grants what seeds S2 and S3 attempt, on the whole audit "
        "bucket and on every runtime log group, so that only the control named for each can refuse it. The "
        "wildcard on * is in the Deny, refagent's explicit denies, which must cover every resource.",
    ),
}
for path, (rule, reason) in SUPPRESSIONS.items():
    if path.startswith("SeedS1Role/") and not S1_ORIGIN:
        continue  # the seed's role is not made once S1 is read
    if path.startswith("Standin/") and not STANDIN:
        continue  # nor the stand-in, once S2 and S3 are read (M05 PR 3)
    NagSuppressions.add_resource_suppressions_by_path(stack, f"AgentkeelAudit/{path}", [{"id": rule, "reason": reason}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
