"""The construct itself, and the three checks over the whole stack (S3, S5, S8).

Read `infra/construct/__init__.py` first: it says why the checks are a
stack validation and not a check inside the construct.
"""

from __future__ import annotations

from typing import Any

import aws_cdk as cdk
import jsii
from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_bedrockagentcore as agentcore
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_ssm as ssm
from constructs import Construct, IValidation

from infra.construct import door
from src import manifest as manifest_module
from src.validate import agent_rules

ROOT = manifest_module.ROOT
# M09 PR 2 (SPEC/09 §2, §6; R3): the platform baseline every agent's guardrail carries, and the agent's own
# rules it is merged with. Read at synth from the tree the deploy runs from, which is `main`.
BASELINE = ROOT / "rules" / "baseline.yaml"
RUNTIME_TYPE = agentcore.CfnRuntime.CFN_RESOURCE_TYPE_NAME
AGENT_ROLE_PATH = "/agentkeel/agents/"  # the key policy matches agent roles by path (ruling b)
PORT = 443
INVOKE = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
# Where a `us.` system profile routes, as the eval role has it
# (infra/bootstrap/app.py, PROFILE_REGIONS). Repeated rather than imported:
# the two stacks do not import each other.
PROFILE_REGIONS = ("us-east-1", "us-east-2", "us-west-2")

# Security-owned parameters. The bootstrap stack writes all but the two
# prefix lists, which AWS gives no CloudFormation attribute for; the human
# who deploys the bootstrap stack writes those two, with one command each
# (infra/bootstrap/README.md). A parameter Security has not written is a
# deploy that fails, not a default that is guessed.
BOUNDARY_PARAM = "/agentkeel/security/boundary-arn"
VPC_PARAM = "/agentkeel/security/vpc-id"
SUBNETS_PARAM = "/agentkeel/security/subnet-ids"
ENDPOINT_PARAM = "/agentkeel/security/endpoint/{name}"
PREFIX_LIST_PARAM = "/agentkeel/security/prefix-list/{name}"
# The two the manifest may list that are gateway endpoints, not interface
# ones (ruling e, ADR-0006): egress to them is a prefix list, not a
# security group.
GATEWAY_ENDPOINTS = ("s3", "dynamodb")
# Ruling d, amended at M01 PR 3 (B1). A container runtime in a VPC with no
# way out pulls its image through these two, so a manifest without them is
# refused at synth rather than failing to pull after the deploy. The
# manifest lists them itself: egress the manifest does not list is F1.1.
IMAGE_PULL_ENDPOINTS = ("ecr.api", "ecr.dkr")
RUNTIME_LOG_GROUPS = "/aws/bedrock-agentcore/runtimes/"
# M05 PR 2 (SPEC/05 §6). The security account's audit bucket (infra/security/), named, not imported;
# an agent puts its own record under `agents/<name>/`, and refusal events under `events/` there.
AUDIT_BUCKET = "agentkeel-audit-897698239547"
# The agent role's explicit denies (SPEC/00 §8 M05, SPEC/05 §6). The boundary denies most of them already;
# these are the role's own, so a boundary widened later does not take them with it. infra/audit/'s
# stand-in carries the same list.
GUARDRAIL_DENIED = ["bedrock:Create*Guardrail*", "bedrock:Update*Guardrail*", "bedrock:Delete*Guardrail*",
                    "bedrock:Put*Guardrail*", "bedrock:GetGuardrail", "bedrock:ListGuardrails"]
AGENT_DENIES = ["iam:*", *GUARDRAIL_DENIED, "logs:Delete*", "sts:AssumeRole", "s3:PutBucketPolicy"]

# Until deploy.yml passes the digest of the image it just signed. A stack
# synthesised without one is a synth, never a deploy: the placeholder is
# not a pullable image, so a deploy of it fails at the runtime.
UNPINNED = "sha256:" + "0" * 64

# M06 PR 2 (SPEC/06 section 6, items 5, 7, 8). refagent is the platform's own agent: its key is the
# bootstrap stack's and its runtime keeps the name it was deployed under. An agent from the template
# makes its own key here, and its runtime is named `agentkeel_<name>`, so the deploy role's grant on
# `runtime/agentkeel_*` reaches the platform's agents and none of the other runtimes in the account.
PLATFORM_AGENT = "refagent"
AGENT_TAG = "agentkeel:agent"  # on the agent's role; the audit bucket's policy reads it as aws:PrincipalTag
# The roles no key policy here lets alter, grant on, disable or delete the key (R4), as the bootstrap
# stack's key policy names them, plus every agent role by path. M07 PR 3 (rulings/pr2-security.md item
# 13h; platform-architect F2 on M07 PR 2): the two roles M07 PR 2 added are named too, before any agent
# from the template has a key. After a key is made its policy is not changed by any role here.
PLATFORM_ROLES = ("agentkeel-deploy", "agentkeel-cfn-exec", "agentkeel-evals", "agentkeel-developer",
                  "agentkeel-model-watch", "agentkeel-envelope-row-put")  # fmt: skip
# M10 PR 2 (SPEC/10 §2, §6; R2 door 2 hybrid; milestones/M10/runs/door_probe.md). An agent whose manifest has
# `callers` gets a door: a Cognito user pool of its own (one user per subject, a callers client, a door client with
# a client-credentials scope), the runtime's JWT authoriser admitting the door client ONLY, and an HTTP API in
# front with a Lambda authoriser (the callers' tokens against the manifest's list) and a proxy Lambda that
# exchanges to the door's token and invokes the runtime. The API's access log goes to a log group here and, by a
# subscription, to the security account's destination, which delivers it under calls/agents/<name>/ in the audit
# bucket (infra/security/). The two Lambdas run outside the platform VPC: the runtime's bearer endpoint and the
# pool's token endpoint are public service endpoints the VPC has no way to (stated under Unsure, Security).
SECURITY_ACCOUNT = "897698239547"
CALLS_DESTINATION = f"arn:aws:logs:us-west-2:{SECURITY_ACCOUNT}:destination:agentkeel-calls"
DOOR_LOG_GROUPS = "/agentkeel/doors/"
LAMBDA_LOG_GROUPS = "/aws/lambda/"
DOOR_RUNTIME = "python3.14"  # the latest Lambda runtime cdk-nag knows (L1), as infra/audit's seed function
DOOR_TIMEOUT_MS = 29_000  # API Gateway's integration ceiling; the proxy's own timeout is one second under it
PLATFORM_SCOPE = "invoke"  # the door client's scope on the agent's resource server: <agentkeel-name>/invoke


class GovernedAgent(Construct):
    """One agent: its role, its security group, its inference profile, its runtime.

    A manifest that says `rollout: retired` gets all of them but the runtime (M07 PR 2).

    `bundle` is the agent's directory, e.g. `agents/refagent`. Everything
    the construct needs about the agent comes from the manifest in it: the
    name, the model profile, and the endpoints its security group may
    reach. Nothing is passed in beside it, so two agents cannot differ in
    a way the manifest does not record.

    `role` is for the caller who has a role already. It must carry the
    bootstrap stack's boundary; one without it, or with another, is
    refused at synth (S5). An imported role is refused: CDK cannot see
    whether it has a boundary, and a check that cannot see is not a check.

    `gateway` and `identity` are declared and not wired (SPEC/01 §10,
    ruling SCOPE). Passing either is refused at synth. They are here so
    the seam is visible and so no caller invents its own.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bundle: str,
        role: iam.IRole | None = None,
        image_digest: str | None = None,
        gateway: Any = None,
        identity: Any = None,
    ) -> None:
        super().__init__(scope, construct_id)
        stack = cdk.Stack.of(self)
        rules = install_stack_checks(stack)

        self.manifest = manifest_module.load(ROOT / bundle / "manifest.yaml")
        self.agent_name: str = self.manifest["name"]
        self.runtime_name = (self.agent_name if self.agent_name == PLATFORM_AGENT
                             else f"agentkeel_{self.agent_name}").replace("-", "_")
        # refagent's repository is the bootstrap's; an agent from the template's is made on its first push
        # under the agentkeel/ namespace, which the creation template matches (SPEC/06 section 6, item 4).
        self.image_repository = (f"agentkeel-{self.agent_name}" if self.agent_name == PLATFORM_AGENT
                                 else f"agentkeel/{self.agent_name}")
        self.bundle = bundle

        if gateway is not None:
            rules.refuse(f"{self.node.path}: Gateway is a declared prop and is not wired at M01 (SPEC/01 §10).")
        if identity is not None:
            rules.refuse(f"{self.node.path}: Identity is a declared prop and is not wired at M01 (SPEC/01 §10).")
        # M06 PR 2 (platform-architect N10, N11; rule-owner): refagent is the bundle at agents/refagent and
        # nothing else, and an agent from the template carries a guardrail pin; the construct holds both,
        # not only validate.
        if (self.agent_name == PLATFORM_AGENT) != (bundle.rstrip("/") == f"agents/{PLATFORM_AGENT}"):
            rules.refuse(f"{self.node.path}: the manifest's name is {self.agent_name} and the bundle is {bundle}; "
                         f"only agents/{PLATFORM_AGENT} is {PLATFORM_AGENT}.")
        if self.agent_name != PLATFORM_AGENT and not self.manifest.get("guardrail"):
            rules.refuse(f"{self.node.path}: an agent from the template pins the platform's guardrail "
                         "(SPEC/06 section 6, item 6); this one pins none.")
        # M09 PR 2 (SPEC/09 §2 "The placeholder pin"; R3, R10): an agent with rules/ of its own is guarded by
        # the guardrail this stack builds from them on the baseline, and the manifest's pin is read only to
        # refuse null (above) and refagent's. refagent's own guardrail stays the bootstrap stack's.
        self.own_rules = self.agent_name != PLATFORM_AGENT and (ROOT / bundle / "rules" / "guardrail.yaml").is_file()
        if self.own_rules:
            platform_pin = manifest_module.load(ROOT / "agents" / PLATFORM_AGENT / "manifest.yaml").get("guardrail") or {}
            if (self.manifest.get("guardrail") or {}).get("id") == platform_pin.get("id"):
                rules.refuse(f"{self.node.path}: an agent with rules/ pins a guardrail of its own, built here from them "
                             f"on the baseline; this one pins refagent's {platform_pin.get('id')} (SPEC/09 section 2; R10).")
        if missing := [n for n in IMAGE_PULL_ENDPOINTS if n not in self.manifest["endpoint_allowlist"]]:
            rules.refuse(f"{self.node.path}: endpoint_allowlist lacks {', '.join(missing)}. The runtime pulls its "
                         f"image through them and the VPC has no other way out (ruling d, amended at M01 PR 3).")

        self.boundary_arn = _parameter(self, "Boundary", BOUNDARY_PARAM)
        self.security_group = self._security_group(rules)
        self.rights_table = self._rights_table()
        self.profile = self._inference_profile()  # before the role: the role names its ARN
        # An agent from the template brings its own key (SPEC/06 section 6, item 5); refagent's is the bootstrap's.
        # Made before the role, whose grant names it.
        self.key = None if self.agent_name == PLATFORM_AGENT else self._agent_key()
        # M09 PR 2: the guardrail on the call. For an agent with rules/, the one this stack builds (its ARN and
        # version are tokens the role's condition and the runtime's environment carry); otherwise the manifest's
        # pin, as since M03 PR 2. Made before the role, whose invoke is conditioned on it.
        self.built_guardrail: bedrock.CfnGuardrail | None = None
        self.built_version: bedrock.CfnGuardrailVersion | None = None
        self.rules_digest: str | None = None
        if self.own_rules:
            self._agent_guardrail(rules)
        if self.built_guardrail is not None and self.built_version is not None:
            self.guardrail_arn: str | None = self.built_guardrail.attr_guardrail_arn
            self.guardrail_version: str | None = self.built_version.attr_version
        elif self.guardrail:
            stack_ = cdk.Stack.of(self)
            self.guardrail_arn = f"arn:aws:bedrock:{stack_.region}:{stack_.account}:guardrail/{self.guardrail['id']}"
            self.guardrail_version = str(self.guardrail["version"])
        else:
            self.guardrail_arn = self.guardrail_version = None
        self.role = self._role(role, rules)
        # M07 PR 2 (SPEC/07 section 6; milestones/M07/rulings/pr2-security.md item 11): a retirement is
        # this stack without its runtime. Read from the manifest, as everything else about the agent is:
        # `rollout: retired`, which the platform's own pull request set and the agent's seats merged.
        # Everything else stays in the stack, so the update removes the runtime (CloudFormation calls
        # DeleteAgentRuntime as the execution role, which may already) and grants nothing new.
        # refagent is never retired by this path.
        self.retired = self.manifest.get("rollout") == "retired"
        if self.retired and self.agent_name == PLATFORM_AGENT:
            rules.refuse(f"{self.node.path}: {PLATFORM_AGENT} is the platform's own agent and is never retired "
                         "by a manifest (SPEC/07 section 6).")
        # M10 PR 2 (SPEC/10 §2, §6; R2): the outside subjects the manifest admits (Tool Owner). With any, the
        # agent gets a door: its pool before the runtime, whose authoriser names the pool's door client, and the
        # API after it, whose proxy names the runtime. refagent's `callers` is `[]`: no pool, no authoriser, the
        # eval role's and the deploy role's SigV4 calls as before (SPEC/10 §8).
        self.callers: list[str] = [c["subject"] for c in self.manifest.get("callers") or []]
        if self.callers and self.agent_name == PLATFORM_AGENT:
            rules.refuse(f"{self.node.path}: {PLATFORM_AGENT} is not behind a door at M10 (SPEC/10 section 8); "
                         "its callers must be [].")
        self.pool: cognito.CfnUserPool | None = None
        self.door_client: cognito.CfnUserPoolClient | None = None
        self.callers_client: cognito.CfnUserPoolClient | None = None
        self.door_api: apigw.CfnApi | None = None
        if self.callers and not self.retired:
            self._pool()
        self.runtime = None if self.retired else self._runtime(image_digest or UNPINNED)
        if self.runtime is not None and self.pool is not None:
            self._door(rules)

    # --- the network -------------------------------------------------------

    def _security_group(self, rules: _StackRules) -> ec2.SecurityGroup:
        """Egress to the endpoints the manifest lists, and to nothing else (S3)."""
        vpc = ec2.Vpc.from_vpc_attributes(
            self, "BootstrapVpc",
            vpc_id=_parameter(self, "VpcId", VPC_PARAM),
            availability_zones=cdk.Stack.of(self).availability_zones,
        )  # fmt: skip
        group = ec2.SecurityGroup(
            self, "Sg", vpc=vpc, allow_all_outbound=False,
            description=f"agentkeel {self.agent_name}: egress to the endpoints the manifest lists.",
        )  # fmt: skip

        approved: list[Any] = []
        for name in self.manifest["endpoint_allowlist"]:
            gateway = name in GATEWAY_ENDPOINTS
            template = PREFIX_LIST_PARAM if gateway else ENDPOINT_PARAM
            destination = _parameter(self, f"Endpoint{name.title().replace('-', '').replace('.', '')}",
                                     template.format(name=name))  # fmt: skip
            peer = ec2.Peer.prefix_list(destination) if gateway else ec2.Peer.security_group_id(destination)
            group.add_egress_rule(peer, ec2.Port.tcp(PORT), f"{name}, from the manifest")
            approved.append(destination)
        rules.own_security_group(group, approved)
        return group

    # --- the table ---------------------------------------------------------

    def _rights_table(self) -> dynamodb.Table:
        """The rights table (SPEC/00 §9: the table is the truth, the corpus is the evidence).

        Loaded from `data/rights_table.json` by `scripts/load_rights_table.py`
        after the deploy. The agent may read it and may not write it: the
        role grants GetItem, Query and Scan, and nothing else.

        Encryption is `DEFAULT`, the DynamoDB-owned key (M02 open.md row 9,
        Security). It was `AWS_MANAGED`, the `aws/dynamodb` key, and the
        first deploy failed at CREATE on it: the DynamoDB handler calls
        `kms:CreateGrant` for that key, and `agentkeel-deploy-boundary`
        denies it on every key (R4). `DEFAULT` makes no KMS call, so R4 is
        left as it is. `tests/test_bootstrap.py` reads such a collision
        before a deploy does. The table holds the fictional rights table,
        which is in the repo in clear (`data/rights_table.json`); a
        customer key for it is M05's containment work, not M02's.
        """
        return dynamodb.Table(
            self, "RightsTable",
            table_name=f"agentkeel-{self.agent_name}-rights",
            partition_key=dynamodb.Attribute(name="table_row", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.DEFAULT,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True),
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip

    # --- the role ----------------------------------------------------------

    def _role(self, given: iam.IRole | None, rules: _StackRules) -> iam.IRole:
        """The agent's role, under the agent path, with the boundary on it."""
        if given is not None:
            rules.own_role(given, self.boundary_arn, given=True)
            # A given role is held to what the construct's own is (platform-architect F3 on M05 PR 2):
            # the explicit denies and its own record, added to it, not assumed of it.
            self._contain(given)
            return given
        role = iam.Role(
            self, "Role",
            path=AGENT_ROLE_PATH,  # the key policy matches on it (ruling b)
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                self, "BoundaryPolicy", self.boundary_arn),
            description=f"agentkeel {self.agent_name}: what the runtime runs as, inside the boundary.",
        )  # fmt: skip
        # B2 (M01 PR 3). This used to name the profile by
        # `application-inference-profile/agentkeel-<name>`, but AWS gives an
        # application profile a generated id, so that ARN named nothing, and
        # the runtime was pointed at the system profile, which the role was
        # never granted. Now the role names the ARN CloudFormation returns,
        # and the runtime is given the same one (below).
        #
        # A call through the profile is authorised twice: on the profile, and
        # on the foundation model in whichever region the source profile
        # routes to. The second is conditioned on this profile, so the model
        # is reachable through it and not directly. `bedrock:Converse` was
        # listed here and is not an IAM action; Converse is authorised as
        # InvokeModel.
        profile_arn = self.profile.attr_inference_profile_arn
        # M03 PR 2 (security-reviewer F2 at M03 PR 1): with a guardrail pinned,
        # an invoke that does not carry it, at its pinned version, is refused.
        # Code cannot drop the guardrail; it can only fail to answer.
        # M09 PR 2: for an agent with rules/, the guardrail this stack built, so no other could be on the call.
        guarded = {"bedrock:GuardrailIdentifier": self._guardrail_arn(versioned=True)} if self.guardrail_arn else {}
        role.add_to_policy(iam.PolicyStatement(
            sid="InvokeItsOwnProfileOnly",
            actions=INVOKE,
            resources=[profile_arn],
            conditions={"StringEquals": guarded} if guarded else None,
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="TheModelOnlyThroughItsOwnProfile",
            actions=INVOKE,
            resources=[f"arn:aws:bedrock:{region}::foundation-model/{self._foundation_model()}"
                       for region in PROFILE_REGIONS],
            conditions={"StringEquals": {"bedrock:InferenceProfileArn": profile_arn, **guarded}},
        ))  # fmt: skip
        if self.guardrail_arn:
            # Its own guardrail, the one the manifest pins (or, with rules/, the one this stack built), and its
            # numbered versions; the agent boundary allows ApplyGuardrail as a ceiling.
            role.add_to_policy(iam.PolicyStatement(
                sid="ApplyItsOwnGuardrailOnly",
                actions=["bedrock:ApplyGuardrail"],
                resources=[self._guardrail_arn(versioned=False), f"{self._guardrail_arn(versioned=False)}:*"],
            ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheRightsTableAndNeverWriteIt",
            actions=["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
            resources=[self.rights_table.table_arn],
        ))  # fmt: skip
        # B1 (M01 PR 3). AgentCore pulls the image as this role, and the
        # runtime makes its own log group as it. The pull is read-only and
        # on this agent's repository alone; GetAuthorizationToken and
        # DescribeLogGroups take no resource. The boundary caps all of it.
        stack = cdk.Stack.of(self)
        role.add_to_policy(iam.PolicyStatement(
            sid="PullItsOwnImageOnly",
            actions=["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
            resources=[f"arn:aws:ecr:{stack.region}:{stack.account}:repository/{self.image_repository}"],
        ))  # fmt: skip
        # Its own runtime's log group, by the runtime's name, not every runtime's in this shared account
        # (platform-architect F3 on M06 PR 2): AgentCore names it <runtime id>-<endpoint>, and the id
        # starts with the name and a hyphen, so agentkeel_a-* does not reach agentkeel_a_b's.
        own_logs = f"arn:aws:logs:{stack.region}:{stack.account}:log-group:{RUNTIME_LOG_GROUPS}{self.runtime_name}-*"
        role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogGroup",
            actions=["logs:CreateLogGroup", "logs:DescribeLogStreams"],
            resources=[own_logs],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="NoResourceLevelPermission",
            actions=["ecr:GetAuthorizationToken", "logs:DescribeLogGroups"],
            resources=["*"],
        ))  # fmt: skip
        # These two were one statement on `*` (PR 3 security-reviewer, F6). The
        # log streams are the runtime's own, under AgentCore's prefix. The key
        # is this agent's, named by its alias: `*` reached any key in the
        # account whose policy delegates to IAM. The alias is the bootstrap
        # stack's (`alias/agentkeel-<name>`), which names one key per agent.
        role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogStreams",
            actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[f"{own_logs}:log-stream:*"],
        ))  # fmt: skip
        if self.key is not None:
            # An agent from the template: its own key, in this stack, by ARN.
            role.add_to_policy(iam.PolicyStatement(
                sid="ItsOwnKey", actions=["kms:Decrypt", "kms:GenerateDataKey"], resources=[self.key.attr_arn]))
        else:
            role.add_to_policy(iam.PolicyStatement(
                sid="ItsOwnKeyByAlias",
                actions=["kms:Decrypt", "kms:GenerateDataKey"],
                resources=[f"arn:aws:kms:{stack.region}:{stack.account}:key/*"],
                conditions={"ForAnyValue:StringEquals": {"kms:ResourceAliases": f"alias/agentkeel-{self.agent_name}"}},
            ))  # fmt: skip
        self._contain(role)
        # The audit bucket's policy holds an agent from the template to agents/<this tag>/ (SPEC/06 section 6,
        # item 8). The tag is the manifest's name, set here by CloudFormation from main; no agent role may tag.
        cdk.Tags.of(role).add(AGENT_TAG, self.agent_name)
        rules.own_role(role, self.boundary_arn, given=False)
        return role

    def _agent_key(self) -> kms.CfnKey:
        """An agent from the template's own key (SPEC/06 section 6, item 5; R4).

        The bootstrap's key policy for refagent, repeated: agent roles use the key and never read its
        policy (seed S6's control, by path); no platform role, the execution role that creates this
        included, may alter, grant on, disable or delete it. The account's admin can (the landing zone's,
        SPEC/01 section 1). Because the creating role is denied PutKeyPolicy by the policy it creates,
        KMS's lockout check is bypassed: the account principal still administers the key. Retained."""
        stack = cdk.Stack.of(self)
        account = f"arn:aws:iam::{stack.account}"
        agent_roles = f"{account}:role{AGENT_ROLE_PATH}*"
        policy = {"Version": "2012-10-17", "Statement": [
            {"Sid": "TheAccountAdministersIt", "Effect": "Allow", "Principal": {"AWS": f"{account}:root"},
             "Action": "kms:*", "Resource": "*"},
            # Its own agent's role only, by the tag the platform sets (platform-architect F2, security-reviewer
            # F5 on M06 PR 2): every agent role under the path was a shared surface.
            {"Sid": "ItsAgentUsesTheKeyAndNeverReadsItsPolicy", "Effect": "Allow", "Principal": {"AWS": "*"},
             "Action": ["kms:Decrypt", "kms:GenerateDataKey"], "Resource": "*",
             "Condition": {"ArnLike": {"aws:PrincipalArn": agent_roles},
                           "StringEquals": {"aws:PrincipalAccount": stack.account,
                                            "aws:PrincipalTag/agentkeel:agent": self.agent_name}}},
            {"Sid": "NoAgentReadsThisPolicy", "Effect": "Deny", "Principal": {"AWS": "*"},
             "Action": ["kms:GetKeyPolicy", "kms:ListKeyPolicies"], "Resource": "*",
             "Condition": {"ArnLike": {"aws:PrincipalArn": agent_roles}}},
            {"Sid": "NoPlatformRoleChangesThisKey", "Effect": "Deny", "Principal": {"AWS": "*"},
             # R4's four, and what else would change the key once made (security-reviewer F4 on M06 PR 2).
             "Action": ["kms:PutKeyPolicy", "kms:CreateGrant", "kms:ScheduleKeyDeletion", "kms:DisableKey",
                        "kms:UpdateAlias", "kms:DeleteAlias", "kms:UntagResource", "kms:DisableKeyRotation",
                        "kms:RevokeGrant", "kms:RetireGrant"],
             "Resource": "*",
             "Condition": {"ArnLike": {"aws:PrincipalArn": [agent_roles, *(f"{account}:role/{r}" for r in PLATFORM_ROLES)]}}},
        ]}  # fmt: skip
        key = kms.CfnKey(
            self, "Key",
            # The roles named in PLATFORM_ROLES and every agent role by path: not every role a stack of the
            # platform's makes (the Grafana connector's, the ingest's and the audit's are not in the list;
            # they hold no kms Allow). Until M07 PR 3 this said "no role the platform creates"
            # (platform-architect 5 on M07 PR 3).
            description=f"agentkeel: {self.agent_name}'s key. No platform role its policy names may administer it (R4).",
            enable_key_rotation=True,
            # The execution role may make, rotate and alias a key that carries this tag, and no other.
            tags=[cdk.CfnTag(key=AGENT_TAG, value=self.agent_name)],
            key_policy=policy,
            bypass_policy_lockout_safety_check=True,
        )  # fmt: skip
        key.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        alias = kms.CfnAlias(self, "KeyAlias", alias_name=f"alias/agentkeel-{self.agent_name}", target_key_id=key.ref)
        alias.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        return key

    def _contain(self, role: iam.IRole) -> None:
        """M05 PR 2 (SPEC/05 §6): its own record in the security account, and its own explicit denies.

        The put is under its own prefix; the audit bucket's policy refuses any other (seed S2), and the
        boundary caps it at agents/*. The denies are the role's own, beside the boundary's."""
        role.add_to_principal_policy(iam.PolicyStatement(
            sid="ItsOwnRecordInTheAuditBucket",
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/agents/{self.agent_name}/*"],
        ))  # fmt: skip
        role.add_to_principal_policy(iam.PolicyStatement(
            sid="NeverEscalateNeverEraseItsTracks", effect=iam.Effect.DENY, actions=AGENT_DENIES, resources=["*"]))

    # --- the model ---------------------------------------------------------

    @property
    def guardrail(self) -> dict[str, str] | None:
        """The manifest's guardrail pin (Rule Owner), or None before M03."""
        return self.manifest.get("guardrail")

    def _guardrail_arn(self, *, versioned: bool) -> str:
        """The guardrail on the call, by ARN; with `versioned`, the form bedrock:GuardrailIdentifier carries."""
        assert self.guardrail_arn is not None and self.guardrail_version is not None
        return f"{self.guardrail_arn}:{self.guardrail_version}" if versioned else self.guardrail_arn

    def _agent_guardrail(self, rules: _StackRules) -> None:
        """An agent's own guardrail, built here from its rules merged onto the baseline (M09 PR 2; SPEC/09 §2, §6; R3).

        One Bedrock Guardrail named `agentkeel-<name>`, tagged with the agent's name so the execution role may
        make it and nothing untagged (the bootstrap's deploy boundary and execution role, narrowed at M09
        PR 2), and a numbered version whose description carries the digest of the baseline and the agent's
        rule files, which `scripts/observe_rules.py` computes again from the merge commit (F9.1). The merge
        is the platform check's (`src/validate/agent_rules.py`): a file the check would refuse is refused
        here too, before anything is deployed. The prompt-attack filter is the baseline's and is off, so no
        content policy; a merged spec that turned it on is refused. Retained, as refagent's versions are."""
        bundle = ROOT / self.bundle
        errors = agent_rules.rules_errors(bundle, root=ROOT)
        for error in errors:
            rules.refuse(f"{self.node.path}: {error}")
        if errors:
            return
        baseline = agent_rules.load(BASELINE)
        files = [bundle / "rules" / "guardrail.yaml"]
        if (bundle / "rules" / "redteam.yaml").is_file():
            files.append(bundle / "rules" / "redteam.yaml")
        merged = agent_rules.merge(baseline, agent_rules.load(files[0]))
        if (merged.get("content_filters") or {}).get("prompt_attack") is not False:
            rules.refuse(f"{self.node.path}: the prompt-attack filter is off (the Rule Owner, M03 PR 2; R1); the merged rules say otherwise.")
            return
        self.rules_digest = agent_rules.digest(BASELINE.read_bytes(), *(f.read_bytes() for f in files))
        on_output = merged["topics_apply_to"] == "input and output"
        topics = merged["denied_topics"]
        guardrail = bedrock.CfnGuardrail(
            self, "Guardrail",
            name=f"agentkeel-{self.agent_name}",
            description=f"agentkeel {self.agent_name}: built from rules/baseline.yaml (Rule Owner) and the agent's "
                        f"rules/ at its merge commit, add-only (SPEC/09). Security builds, never scopes.",
            blocked_input_messaging=merged["messages"]["blocked_input"],
            blocked_outputs_messaging=merged["messages"]["blocked_output"],
            topic_policy_config=bedrock.CfnGuardrail.TopicPolicyConfigProperty(topics_config=[
                bedrock.CfnGuardrail.TopicConfigProperty(
                    name=t["name"], definition=t["definition"], type="DENY", examples=t.get("examples"),
                    input_enabled=True, input_action="BLOCK",
                    output_enabled=on_output, output_action="BLOCK" if on_output else "NONE")
                for t in topics]) if topics else None,
            sensitive_information_policy_config=bedrock.CfnGuardrail.SensitiveInformationPolicyConfigProperty(
                pii_entities_config=[bedrock.CfnGuardrail.PiiEntityConfigProperty(type=e["entity"], action=e["action"])
                                     for e in merged["pii"]]) if merged["pii"] else None,
            tags=[cdk.CfnTag(key=AGENT_TAG, value=self.agent_name)],
        )  # fmt: skip
        version = bedrock.CfnGuardrailVersion(
            self, "GuardrailVersion",
            guardrail_identifier=guardrail.attr_guardrail_id,
            description=f"rules sha256 {self.rules_digest}",
        )  # fmt: skip
        # A rules change replaces the version; the one the record names, and old envelopes name, outlives it.
        # Both retained: a stack delete would otherwise take the guardrail and its versions with it
        # (security-reviewer on M09 PR 2). Old guardrails and versions are removed by hand, as refagent's.
        guardrail.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        version.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        self.built_guardrail, self.built_version = guardrail, version

    def _foundation_model(self) -> str:
        """`us.anthropic.claude-sonnet-4-6` -> `anthropic.claude-sonnet-4-6`: the model the profile routes to."""
        profile = self.manifest["model"]["profile"]
        prefix, _, model = profile.partition(".")
        if prefix != "us" or not model:
            raise ValueError(f"{profile}: the construct knows the us. profile's regions only ({PROFILE_REGIONS})")
        return model

    def _inference_profile(self) -> bedrock.CfnApplicationInferenceProfile:
        """One profile per agent, so spend carries the agent's tag (SPEC/01 §6, ruling a)."""
        stack = cdk.Stack.of(self)
        source = f"arn:aws:bedrock:{stack.region}:{stack.account}:inference-profile/{self.manifest['model']['profile']}"
        return bedrock.CfnApplicationInferenceProfile(
            self, "Profile",
            inference_profile_name=f"agentkeel-{self.agent_name}",
            description=f"agentkeel {self.agent_name}: one profile per agent for cost tagging.",
            model_source=bedrock.CfnApplicationInferenceProfile.InferenceProfileModelSourceProperty(
                copy_from=source),
            tags=[cdk.CfnTag(key="agentkeel:agent", value=self.agent_name)],
        )  # fmt: skip

    # --- the runtime -------------------------------------------------------

    def _runtime(self, image_digest: str) -> agentcore.CfnRuntime:
        """VPC mode only. Its subnets and security group are the platform's, not a caller's."""
        stack = cdk.Stack.of(self)
        subnets = ssm.StringListParameter.value_for_typed_list_parameter(self, SUBNETS_PARAM)
        image = (f"{stack.account}.dkr.ecr.{stack.region}.amazonaws.com/"
                 f"{self.image_repository}@{image_digest}")  # fmt: skip
        # M10 PR 2 (SPEC/10 §2, §6; R2 door 2 hybrid; door_probe.md (a), (d)): with a pool, the runtime takes
        # bearer tokens only and admits the door client alone, so a SigV4 call from any principal with the grant,
        # a caller's own token and no token are each refused at the service's edge, before the container. Set
        # on a deployed runtime it updates in place (version n to n+1, the ARN unchanged). Without a pool, as
        # before: IAM is the only check.
        authoriser = None
        if self.pool is not None and self.door_client is not None:
            authoriser = agentcore.CfnRuntime.AuthorizerConfigurationProperty(
                custom_jwt_authorizer=agentcore.CfnRuntime.CustomJWTAuthorizerConfigurationProperty(
                    discovery_url=f"https://cognito-idp.{stack.region}.amazonaws.com/{self.pool.ref}/.well-known/openid-configuration",
                    allowed_clients=[self.door_client.ref]))
        return agentcore.CfnRuntime(
            self, "Runtime",
            agent_runtime_name=self.runtime_name,
            role_arn=self.role.role_arn,
            description=f"agentkeel {self.agent_name}, from the bundle {self.bundle}.",
            authorizer_configuration=authoriser,
            agent_runtime_artifact=agentcore.CfnRuntime.AgentRuntimeArtifactProperty(
                container_configuration=agentcore.CfnRuntime.ContainerConfigurationProperty(container_uri=image)),
            network_configuration=agentcore.CfnRuntime.NetworkConfigurationProperty(
                network_mode="VPC",
                network_mode_config=agentcore.CfnRuntime.VpcConfigProperty(
                    security_groups=[self.security_group.security_group_id], subnets=subnets),
            ),
            environment_variables={
                "AGENTKEEL_BUNDLE": self.bundle,
                # The agent's own profile, which its role may call, not the
                # system profile it copies from, which its role may not (B2).
                "AGENTKEEL_MODEL_PROFILE": self.profile.attr_inference_profile_arn,
                "AGENTKEEL_RIGHTS_TABLE": self.rights_table.table_name,
                # The manifest's guardrail pin, which the server passes to converse (M03 PR 2), as
                # the ARN, not the bare id: the invoke grants' GuardrailIdentifier condition names the
                # ARN, and the request then carries the same string (security-reviewer on PR 2, F1).
                # M09 PR 2: for an agent with rules/, the guardrail this stack built, never the manifest's pin.
                **({"AGENTKEEL_GUARDRAIL_ARN": self._guardrail_arn(versioned=False),
                    "AGENTKEEL_GUARDRAIL_VERSION": self.guardrail_version} if self.guardrail_arn else {}),
                # M05 PR 2 (SPEC/05 §2, §6; seed S4's reader): the manifest's depth ceiling, since the
                # image has no YAML reader, and where the agent writes a refusal event.
                "AGENTKEEL_CEILING_DEPTH": str(self.manifest["ceilings"]["depth"]),
                "AGENTKEEL_AUDIT_BUCKET": AUDIT_BUCKET,
                "AGENTKEEL_AUDIT_PREFIX": f"agents/{self.agent_name}/events/",
            },
        )  # fmt: skip


    # --- the door (M10 PR 2; SPEC/10 §2, §6; R2 door 2 hybrid) -------------------

    def _pool(self) -> None:
        """The agent's own identity pool: one user per subject in `callers`, a callers client and the door client.

        The pool is retained, as the guardrail is: its users' first credentials are set by hand (SPEC/10 §5.1),
        and a redeploy must not lose them; except by the one stack operation that created it (DeletionPolicy
        RetainExceptOnCreate, M10 PR 3): festival-desk's first door deploy failed four times on 2026-10-17 and each
        rollback skipped the new pool, leaving four orphans named for the agent. A pool a rollback made is empty
        of credentials, so nothing is lost by deleting it; the execution role may (DeleteUserPool, tag-held). A
        user's logical id is its subject, so a subject removed from the list removes that user and no other. MFA is off and the password policy is the pool's: a subject is an
        identity for a machine caller whose first credential the owner sets by hand (SPEC/10 §8, "The subject's
        credential"); the pool's advanced security is not bought."""
        stack = cdk.Stack.of(self)
        pool = cognito.CfnUserPool(
            self, "Pool",
            user_pool_name=f"agentkeel-{self.agent_name}",
            admin_create_user_config=cognito.CfnUserPool.AdminCreateUserConfigProperty(allow_admin_create_user_only=True),
            policies=cognito.CfnUserPool.PoliciesProperty(password_policy=cognito.CfnUserPool.PasswordPolicyProperty(
                minimum_length=12, require_lowercase=True, require_uppercase=True, require_numbers=True,
                require_symbols=True, temporary_password_validity_days=1)),
            mfa_configuration="OFF",
            account_recovery_setting=cognito.CfnUserPool.AccountRecoverySettingProperty(recovery_mechanisms=[
                cognito.CfnUserPool.RecoveryOptionProperty(name="admin_only", priority=1)]),
            deletion_protection="INACTIVE",
            user_pool_tags={AGENT_TAG: self.agent_name},
        )  # fmt: skip
        pool.apply_removal_policy(cdk.RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE)
        self.pool = pool
        for subject in self.callers:
            user = cognito.CfnUserPoolUser(
                self, "Caller" + "".join(part.capitalize() for part in subject.split("-")),
                user_pool_id=pool.ref, username=subject, message_action="SUPPRESS",
            )  # fmt: skip
            user.apply_removal_policy(cdk.RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE)
        server = cognito.CfnUserPoolResourceServer(
            self, "ResourceServer", user_pool_id=pool.ref, identifier=f"agentkeel-{self.agent_name}",
            name=f"agentkeel-{self.agent_name}",
            scopes=[cognito.CfnUserPoolResourceServer.ResourceServerScopeTypeProperty(
                scope_name=PLATFORM_SCOPE, scope_description="the platform's own goldens caller, through the door")],
        )  # fmt: skip
        validity = cognito.CfnUserPoolClient.TokenValidityUnitsProperty(access_token="hours", id_token="hours",
                                                                       refresh_token="days")  # fmt: skip
        self.callers_client = cognito.CfnUserPoolClient(
            self, "CallersClient", user_pool_id=pool.ref, client_name="callers", generate_secret=False,
            explicit_auth_flows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
            prevent_user_existence_errors="ENABLED", enable_token_revocation=True,
            access_token_validity=1, id_token_validity=1, refresh_token_validity=1, token_validity_units=validity,
        )  # fmt: skip
        self.door_client = cognito.CfnUserPoolClient(
            self, "DoorClient", user_pool_id=pool.ref, client_name="door", generate_secret=True,
            allowed_o_auth_flows=["client_credentials"], allowed_o_auth_flows_user_pool_client=True,
            allowed_o_auth_scopes=[f"agentkeel-{self.agent_name}/{PLATFORM_SCOPE}"],
            supported_identity_providers=["COGNITO"], enable_token_revocation=True,
            access_token_validity=1, id_token_validity=1, refresh_token_validity=1, token_validity_units=validity,
        )  # fmt: skip
        self.door_client.node.add_dependency(server)
        self.domain_prefix = f"agentkeel-{self.agent_name}-{stack.account}"
        cognito.CfnUserPoolDomain(self, "Domain", user_pool_id=pool.ref, domain=self.domain_prefix)
        self.token_endpoint = f"https://{self.domain_prefix}.auth.{stack.region}.amazoncognito.com/oauth2/token"

    def _door_role(self, construct_id: str, function_name: str, rules: _StackRules) -> iam.Role:
        """A door function's role: under the agent path with the boundary (so the execution role may make it, and
        the stack's S5 check reads it), its own log group and nothing else here."""
        stack = cdk.Stack.of(self)
        role = iam.Role(
            self, construct_id,
            path=AGENT_ROLE_PATH,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(self, f"{construct_id}Boundary", self.boundary_arn),
            description=f"agentkeel {self.agent_name}: the door's {function_name.rsplit('-', 1)[-1]}, inside the boundary.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogStreams", actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[f"arn:aws:logs:{stack.region}:{stack.account}:log-group:{LAMBDA_LOG_GROUPS}{function_name}:*"],
        ))  # fmt: skip
        rules.own_role(role, self.boundary_arn, given=False)
        return role

    def _door(self, rules: _StackRules) -> None:
        """The API in front of the runtime: the authoriser, the proxy, the access log and its delivery."""
        assert self.pool is not None and self.door_client is not None and self.callers_client is not None
        assert self.runtime is not None
        stack = cdk.Stack.of(self)
        region, account = stack.region, stack.account
        names = {"authoriser": f"agentkeel-{self.agent_name}-door-authoriser", "proxy": f"agentkeel-{self.agent_name}-door-proxy"}
        for kind, source in (("authoriser", door.AUTHORISER_SOURCE), ("proxy", door.PROXY_SOURCE)):
            if len(source.encode("utf-8")) > door.ZIPFILE_LIMIT:
                rules.refuse(f"{self.node.path}: the door's {kind} is {len(source.encode('utf-8'))} bytes, over "
                             f"CloudFormation's {door.ZIPFILE_LIMIT} for inline code")  # fmt: skip
        # The three log groups and the subscription are retained: the deploy boundary denies logs:Delete* flat (SPEC/01
        # §6; seed S4), so CloudFormation must never call DeleteLogGroup or DeleteSubscriptionFilter, as it never calls
        # DeleteTable on the rights table. A retired agent's stack keeps them; the access log is the call record's source.
        # Retained on a rollback too (RetainExceptOnCreate would need the delete the boundary denies): a door deploy
        # that fails after making them leaves them, and every retry is refused with "log group already exists" until
        # the owner deletes the three by hand (M10 PR 3; milestones/M10/README.md, the repair detail).
        access_log = logs.CfnLogGroup(self, "DoorAccessLog", log_group_name=f"{DOOR_LOG_GROUPS}{self.agent_name}/access",
                                      retention_in_days=30)  # fmt: skip
        access_log.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        # Every line to the security account's destination, which delivers it under calls/agents/<name>/ (infra/security/).
        # A cross-account subscription to a Logs destination carries no role: the destination's policy admits this account.
        delivery = logs.CfnSubscriptionFilter(self, "DoorCalls", log_group_name=access_log.ref,
                                              destination_arn=CALLS_DESTINATION, filter_pattern="")  # fmt: skip
        delivery.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
        delivery.node.add_dependency(access_log)
        functions: dict[str, lambda_.CfnFunction] = {}
        for kind, source in (("authoriser", door.AUTHORISER_SOURCE), ("proxy", door.PROXY_SOURCE)):
            name = names[kind]
            role = self._door_role(f"Door{kind.capitalize()}Role", name, rules)
            if kind == "proxy":
                # The door client's secret stays in Cognito and is read at call time, by this role and no other
                # (Unsure I on M10 PR 1: no copy in Secrets Manager or SSM).
                role.add_to_policy(iam.PolicyStatement(sid="ReadTheDoorClientsSecret",
                                                       actions=["cognito-idp:DescribeUserPoolClient"],
                                                       resources=[self.pool.attr_arn]))  # fmt: skip
            log_group = logs.CfnLogGroup(self, f"Door{kind.capitalize()}Log", log_group_name=f"{LAMBDA_LOG_GROUPS}{name}",
                                         retention_in_days=30)  # fmt: skip
            log_group.apply_removal_policy(cdk.RemovalPolicy.RETAIN)
            environment = {"REGION": region, "POOL_ID": self.pool.ref, "DOOR_CLIENT_ID": self.door_client.ref}
            if kind == "authoriser":
                environment |= {"CALLERS_CLIENT_ID": self.callers_client.ref, "CALLERS": ",".join(self.callers)}
            else:
                environment |= {"TOKEN_ENDPOINT": self.token_endpoint, "SCOPE": f"agentkeel-{self.agent_name}/{PLATFORM_SCOPE}",
                                "RUNTIME_ARN": self.runtime.attr_agent_runtime_arn}  # fmt: skip
            function = lambda_.CfnFunction(
                self, f"Door{kind.capitalize()}", function_name=name, runtime=DOOR_RUNTIME, handler="index.handler",
                role=role.role_arn, code=lambda_.CfnFunction.CodeProperty(zip_file=source),
                timeout=10 if kind == "authoriser" else DOOR_TIMEOUT_MS // 1000 - 1, memory_size=256,
                environment=lambda_.CfnFunction.EnvironmentProperty(variables=environment),
                description=f"agentkeel {self.agent_name}: the door's {kind} (SPEC/10 section 6).",
                tags=[cdk.CfnTag(key=AGENT_TAG, value=self.agent_name)],
            )  # fmt: skip
            function.node.add_dependency(log_group)
            functions[kind] = function
        api = apigw.CfnApi(self, "Door", name=f"agentkeel-{self.agent_name}-door", protocol_type="HTTP",
                           description=f"agentkeel {self.agent_name}: the door the platform controls (SPEC/10 section 2).",
                           tags={AGENT_TAG: self.agent_name})  # fmt: skip
        self.door_api = api
        authoriser = apigw.CfnAuthorizer(
            self, "DoorAuthorizer", api_id=api.ref, authorizer_type="REQUEST", name="callers",
            authorizer_uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{functions['authoriser'].attr_arn}/invocations",
            authorizer_payload_format_version="2.0", enable_simple_responses=True,
            identity_source=["$request.header.Authorization"], authorizer_result_ttl_in_seconds=0,
        )  # fmt: skip
        integration = apigw.CfnIntegration(
            self, "DoorProxyIntegration", api_id=api.ref, integration_type="AWS_PROXY",
            integration_uri=functions["proxy"].attr_arn, payload_format_version="2.0", timeout_in_millis=DOOR_TIMEOUT_MS,
        )  # fmt: skip
        apigw.CfnRoute(self, "DoorInvocations", api_id=api.ref, route_key="POST /invocations",
                       authorization_type="CUSTOM", authorizer_id=authoriser.ref, target=f"integrations/{integration.ref}")  # fmt: skip
        apigw.CfnStage(
            self, "DoorStage", api_id=api.ref, stage_name="$default", auto_deploy=True,
            access_log_settings=apigw.CfnStage.AccessLogSettingsProperty(
                destination_arn=access_log.attr_arn, format=door.ACCESS_LOG_FORMAT % self.agent_name),
        )  # fmt: skip
        lambda_.CfnPermission(self, "DoorAuthoriserPermission", action="lambda:InvokeFunction",
                              function_name=functions["authoriser"].ref, principal="apigateway.amazonaws.com",
                              source_arn=f"arn:aws:execute-api:{region}:{account}:{api.ref}/authorizers/{authoriser.ref}")  # fmt: skip
        lambda_.CfnPermission(self, "DoorProxyPermission", action="lambda:InvokeFunction",
                              function_name=functions["proxy"].ref, principal="apigateway.amazonaws.com",
                              source_arn=f"arn:aws:execute-api:{region}:{account}:{api.ref}/*/*/invocations")  # fmt: skip
        self.door_url = f"{api.attr_api_endpoint}/invocations"


def _parameter(scope: Construct, construct_id: str, name: str) -> str:
    """A Security-owned SSM parameter, read at deploy. Not CDK context (SPEC/01 §6)."""
    return ssm.StringParameter.value_for_string_parameter(scope, name)


# --- the checks over the whole stack ---------------------------------------


@jsii.implements(IValidation)
class _StackRules:
    """What the stack must be true of, checked after every aspect has run.

    CDK runs validations last, after every aspect and before the template is
    rendered, so anything added to the stack after the construct — S3's
    second form, S8's bare runtime — is in the tree by the time this reads
    it. (`PermissionsBoundary.of(stack).apply()` is not an aspect in this
    version of aws-cdk-lib: it sets a context key the `Role` constructor
    reads. The placement works either way, but do not rely on the aspect
    ordering for it.)

    **Which stack.** `Stack.of(the construct)`, and the constructs below it.
    A rule or a runtime in a sibling or parent stack is out of reach: a
    `CfnSecurityGroupEgress` in another stack naming this security group
    through a cross-stack export is not read here, and neither is a runtime
    in a stack that never installs these checks (`platform-architect`,
    M01 PR 2).
    """

    def __init__(self, stack: cdk.Stack) -> None:
        self.stack = stack
        self.refusals: list[str] = []
        self.groups: list[tuple[ec2.SecurityGroup, list[Any]]] = []
        self.roles: list[tuple[iam.IRole, str, bool]] = []

    def refuse(self, reason: str) -> None:
        self.refusals.append(reason)

    def own_security_group(self, group: ec2.SecurityGroup, approved: list[Any]) -> None:
        self.groups.append((group, approved))

    def own_role(self, role: iam.IRole, boundary_arn: str, *, given: bool) -> None:
        self.roles.append((role, boundary_arn, given))

    # --- IValidation ---

    def validate(self) -> list[str]:
        return [*self.refusals, *self._egress(), *self._boundaries(), *self._runtimes()]

    # --- S3: egress the manifest does not list, however it was added -------

    def _egress(self) -> list[str]:
        found: list[str] = []
        for group, approved in self.groups:
            allowed = [self.stack.resolve(destination) for destination in approved]
            cfn = group.node.default_child
            for rule in self.stack.resolve(cfn.security_group_egress) or []:
                if reason := _egress_refusal(_lower_first(rule), allowed):
                    found.append(f"{group.node.path}: {reason}")
            for node in self.stack.node.find_all():
                # By CloudFormation type, not by Python class: the same rule
                # written as a raw `cdk.CfnResource` of this type is the same
                # rule, and SPEC/01 §3 says "however the rule is added".
                if _resource_type(node) != ec2.CfnSecurityGroupEgress.CFN_RESOURCE_TYPE_NAME:
                    continue
                rule = _lower_first(self.stack.resolve(_properties(node)))
                if rule.get("groupId") != self.stack.resolve(group.security_group_id):
                    continue
                if reason := _egress_refusal(rule, allowed):
                    found.append(f"{node.node.path}: {reason} (added outside the construct)")
        return found

    # --- S5: a role with no boundary, or a different one -------------------

    def _boundaries(self) -> list[str]:
        found: list[str] = []
        for role, boundary_arn, given in self.roles:
            cfn = role.node.default_child if isinstance(role, iam.Role) else None
            if cfn is None:
                found.append(
                    f"{role.node.path if hasattr(role, 'node') else role.role_arn}: an imported role. "
                    "The construct cannot see whether it has the boundary, so it refuses it."
                )
                continue
            on_the_role = self.stack.resolve(cfn.permissions_boundary)
            if on_the_role is None:
                found.append(f"{role.node.path}: no permissions boundary. Every role the construct makes or is "
                             f"given carries the bootstrap stack's ({BOUNDARY_PARAM}).")  # fmt: skip
            elif on_the_role != self.stack.resolve(boundary_arn):
                found.append(f"{role.node.path}: a permissions boundary that is not the bootstrap stack's "
                             f"({BOUNDARY_PARAM}).")  # fmt: skip
            elif given and not str(getattr(cfn, "path", "") or "").startswith(AGENT_ROLE_PATH):
                found.append(f"{role.node.path}: not under {AGENT_ROLE_PATH}. The key policy matches agent roles "
                             f"by path (ruling b), so a role outside it is not denied its own key policy.")  # fmt: skip
        return found

    # --- S8: a runtime that is not an instance of the construct ------------

    def _runtimes(self) -> list[str]:
        found = []
        for node in self.stack.node.find_all():
            if _resource_type(node) != RUNTIME_TYPE:
                continue
            # Identity, not location: a runtime added inside a GovernedAgent's
            # scope is not the construct's own runtime, and the construct
            # built none of its network configuration or its role.
            if not any(isinstance(scope, GovernedAgent) and node is scope.runtime for scope in node.node.scopes):
                found.append(f"{node.node.path}: an {RUNTIME_TYPE} that is not a GovernedAgent's own runtime. "
                             f"An agent on this platform is an instance of the construct "
                             f"(SPEC/01 §2).")  # fmt: skip
        return found


def _resource_type(node: Any) -> str | None:
    return getattr(node, "cfn_resource_type", None)


def _properties(node: Any) -> dict[str, Any]:
    """An L1's properties, whether it is a typed class or a raw `CfnResource`.

    `_toCloudFormation` is not public, so this reads the two places CDK keeps
    them: `cfn_properties` on a typed L1, and the `properties` a raw resource
    was given.
    """
    for attribute in ("_cfn_properties", "cfn_properties"):
        if isinstance(value := getattr(node, attribute, None), dict):
            return value
    return {}


def _lower_first(rule: Any) -> dict[str, Any]:
    """CFN-cased or CDK-cased, one shape: `CidrIp` and `cidrIp` both read as `cidrIp`."""
    if not isinstance(rule, dict):
        return {}
    return {key[:1].lower() + key[1:]: value for key, value in rule.items()}


def _egress_refusal(rule: dict[str, Any], allowed: list[Any]) -> str | None:
    """Why this egress rule is not one the manifest lists, or None."""
    if rule.get("cidrIp") == "255.255.255.255/32":
        return None  # CDK's own placeholder for a security group that allows no egress
    for field in ("cidrIp", "cidrIpv6"):
        if rule.get(field):
            return (f"egress to {rule[field]}: a destination the manifest cannot name. The manifest lists AWS "
                    f"service names, and each is one endpoint of the platform's VPC (ruling d).")  # fmt: skip
    destination = rule.get("destinationSecurityGroupId") or rule.get("destinationPrefixListId")
    if destination is None:
        return "an egress rule with no destination: an absent destination is 0.0.0.0/0 (SPEC/01 §6)."
    if destination not in allowed:
        return f"egress to {destination}: not an endpoint the manifest's endpoint_allowlist names."
    if rule.get("fromPort") != PORT or rule.get("toPort") != PORT \
            or (rule.get("ipProtocol") or "").lower() != "tcp":  # fmt: skip
        return (f"egress on {rule.get('ipProtocol')} {rule.get('fromPort')}-{rule.get('toPort')}: "
                f"the endpoints are reached on tcp {PORT} and nothing else.")  # fmt: skip
    return None


def install_stack_checks(stack: cdk.Stack) -> _StackRules:
    """The stack's copy of the checks. Installed once, by whoever gets there first."""
    rules = getattr(stack, "_agentkeel_rules", None)
    if rules is None:
        rules = _StackRules(stack)
        stack.node.add_validation(rules)
        stack._agentkeel_rules = rules
    return rules


def refuse_outside_construct(stack: cdk.Stack) -> _StackRules:
    """Install the checks on a stack that has no GovernedAgent in it (S8).

    `GovernedAgent` installs them itself. A stack that makes an AgentCore
    runtime without one has nothing to install them, which is the hole
    this closes: the check belongs to the platform, not to the construct.
    """
    return install_stack_checks(stack)
