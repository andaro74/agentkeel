"""The construct itself, and the three checks over the whole stack (S3, S5, S8).

Read `infra/construct/__init__.py` first: it says why the checks are a
stack validation and not a check inside the construct.
"""

from __future__ import annotations

from typing import Any

import aws_cdk as cdk
import jsii
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_bedrockagentcore as agentcore
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct, IValidation

from src import manifest as manifest_module

ROOT = manifest_module.ROOT
RUNTIME_TYPE = agentcore.CfnRuntime.CFN_RESOURCE_TYPE_NAME
AGENT_ROLE_PATH = "/agentkeel/agents/"  # the key policy matches agent roles by path (ruling b)
PORT = 443

# Security-owned parameters. The bootstrap stack writes all but the two
# prefix lists, which AWS gives no CloudFormation attribute for; the human
# who deploys the bootstrap stack writes those two, with one command each
# (infra/bootstrap/README.md). A parameter Security has not written is a
# deploy that fails, not a default that is guessed.
BOUNDARY_PARAM = "/agentkeel/security/boundary-arn"
VPC_PARAM = "/agentkeel/security/vpc-id"
SUBNETS_PARAM = "/agentkeel/security/subnet-ids"
ENDPOINT_PARAM = "/agentkeel/security/endpoint/{name}"
# The two the manifest may list that are gateway endpoints, not interface
# ones (ruling e, ADR-0006): egress to them is a prefix list, not a
# security group.
GATEWAY_ENDPOINTS = ("s3", "dynamodb")

# Until deploy.yml passes the digest of the image it just signed. A stack
# synthesised without one is a synth, never a deploy: the placeholder is
# not a pullable image, so a deploy of it fails at the runtime.
UNPINNED = "sha256:" + "0" * 64


class GovernedAgent(Construct):
    """One agent: its role, its security group, its inference profile, its runtime.

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
        self.bundle = bundle

        if gateway is not None:
            rules.refuse(f"{self.node.path}: Gateway is a declared prop and is not wired at M01 (SPEC/01 §10).")
        if identity is not None:
            rules.refuse(f"{self.node.path}: Identity is a declared prop and is not wired at M01 (SPEC/01 §10).")

        self.boundary_arn = _parameter(self, "Boundary", BOUNDARY_PARAM)
        self.security_group = self._security_group(rules)
        self.rights_table = self._rights_table()
        self.role = self._role(role, rules)
        self.profile = self._inference_profile()
        self.runtime = self._runtime(image_digest or UNPINNED)

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
            destination = _parameter(self, f"Endpoint{name.title().replace('-', '')}",
                                     ENDPOINT_PARAM.format(name=name))  # fmt: skip
            peer = (ec2.Peer.prefix_list(destination) if name in GATEWAY_ENDPOINTS
                    else ec2.Peer.security_group_id(destination))  # fmt: skip
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
        """
        return dynamodb.Table(
            self, "RightsTable",
            table_name=f"agentkeel-{self.agent_name}-rights",
            partition_key=dynamodb.Attribute(name="table_row", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True),
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip

    # --- the role ----------------------------------------------------------

    def _role(self, given: iam.IRole | None, rules: _StackRules) -> iam.IRole:
        """The agent's role, under the agent path, with the boundary on it."""
        if given is not None:
            rules.own_role(given, self.boundary_arn, given=True)
            return given
        role = iam.Role(
            self, "Role",
            path=AGENT_ROLE_PATH,  # the key policy matches on it (ruling b)
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                self, "BoundaryPolicy", self.boundary_arn),
            description=f"agentkeel {self.agent_name}: what the runtime runs as, inside the boundary.",
        )  # fmt: skip
        profile_arn = self._profile_arn()
        role.add_to_policy(iam.PolicyStatement(
            sid="InvokeItsOwnProfileOnly",
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:Converse"],
            resources=[profile_arn],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheRightsTableAndNeverWriteIt",
            actions=["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
            resources=[self.rights_table.table_arn],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogsAndItsOwnKey",
            actions=["logs:CreateLogStream", "logs:PutLogEvents", "kms:Decrypt", "kms:GenerateDataKey"],
            resources=["*"],
        ))  # fmt: skip
        rules.own_role(role, self.boundary_arn, given=False)
        return role

    # --- the model ---------------------------------------------------------

    def _profile_arn(self) -> str:
        stack = cdk.Stack.of(self)
        return (f"arn:aws:bedrock:{stack.region}:{stack.account}:application-inference-profile/"
                f"agentkeel-{self.agent_name}")  # fmt: skip

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
                 f"agentkeel-{self.agent_name}@{image_digest}")  # fmt: skip
        return agentcore.CfnRuntime(
            self, "Runtime",
            agent_runtime_name=self.agent_name.replace("-", "_"),
            role_arn=self.role.role_arn,
            description=f"agentkeel {self.agent_name}, from the bundle {self.bundle}.",
            agent_runtime_artifact=agentcore.CfnRuntime.AgentRuntimeArtifactProperty(
                container_configuration=agentcore.CfnRuntime.ContainerConfigurationProperty(container_uri=image)),
            network_configuration=agentcore.CfnRuntime.NetworkConfigurationProperty(
                network_mode="VPC",
                network_mode_config=agentcore.CfnRuntime.VpcConfigProperty(
                    security_groups=[self.security_group.security_group_id], subnets=subnets),
            ),
            environment_variables={
                "AGENTKEEL_BUNDLE": self.bundle,
                "AGENTKEEL_MODEL_PROFILE": self.manifest["model"]["profile"],
                "AGENTKEEL_RIGHTS_TABLE": self.rights_table.table_name,
            },
        )  # fmt: skip


def _parameter(scope: Construct, construct_id: str, name: str) -> str:
    """A Security-owned SSM parameter, read at deploy. Not CDK context (SPEC/01 §6)."""
    return ssm.StringParameter.value_for_string_parameter(scope, name)


# --- the checks over the whole stack ---------------------------------------


@jsii.implements(IValidation)
class _StackRules:
    """What the stack must be true of, checked after every aspect has run.

    CDK runs validations after aspects, so the boundary a stack-wide
    `PermissionsBoundary` writes is on the roles by the time this reads
    them. Anything added to the stack after the construct — S3's second
    form, S8's bare runtime — is in the tree by then too.
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
                if not isinstance(node, ec2.CfnSecurityGroupEgress):
                    continue
                if self.stack.resolve(node.group_id) != self.stack.resolve(group.security_group_id):
                    continue
                rule = {
                    "cidrIp": node.cidr_ip, "cidrIpv6": node.cidr_ipv6, "ipProtocol": node.ip_protocol,
                    "fromPort": node.from_port, "toPort": node.to_port,
                    "destinationSecurityGroupId": node.destination_security_group_id,
                    "destinationPrefixListId": node.destination_prefix_list_id,
                }  # fmt: skip
                if reason := _egress_refusal(self.stack.resolve(rule), allowed):
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
            if not any(isinstance(scope, GovernedAgent) for scope in node.node.scopes):
                found.append(f"{node.node.path}: an {RUNTIME_TYPE} outside GovernedAgent. An agent exists on "
                             f"this platform only as an instance of the construct (SPEC/01 §2).")  # fmt: skip
        return found


def _resource_type(node: Any) -> str | None:
    return getattr(node, "cfn_resource_type", None)


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
    if rule.get("toPort") != PORT or (rule.get("ipProtocol") or "").lower() != "tcp":
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
