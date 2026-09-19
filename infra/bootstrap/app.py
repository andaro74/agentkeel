"""The M01 bootstrap stack (Security seat; SPEC/01 §6, feasibility.md §2.6 a, b, d, e, f).

Deployed once, to the agent account, by a human with admin, during M01 PR 2
and before PR 2's first CI run — as `infra/eval-role` was at M00. Nothing
else may change it.

    cd infra/bootstrap && npx cdk diff && npx cdk deploy

What it makes:

- the **permission boundary**, applied stack-wide (`PermissionsBoundary.of`)
  so every role either stack synthesises carries it, not only the ones named
  here (`platform-architect` finding);
- the **CloudFormation execution role** the deploy passes, which carries the
  boundary and may create a role only with the boundary attached. Without it
  the deploy role would act as admin (`platform-architect` BLOCK 1);
- the **deploy role**, trusted by `deploy.yml` on `refs/heads/main` only:
  `aud` and the immutable `sub` with `StringEquals`, and `job_workflow_ref`
  with `StringEquals`, not `StringLike` (item 35's lesson);
- the **developer role**, boundary on: the laptop principal of S4
  (SPEC/01 §1). It may read, and may not deploy;
- the **eval role** `agentkeel-evals`, absorbed from `infra/eval-role/`
  (ruling f): the two pinned profiles, the five-action Deny,
  `bedrock-agentcore:InvokeAgentRuntime` on refagent's runtime only;
- a **VPC with no internet gateway and no NAT**: interface endpoints for
  bedrock-runtime, kms and logs, gateway endpoints for s3 and dynamodb
  (ruling e, ADR-0006), each with a policy scoped to this account;
- one **KMS key per agent**, whose policy denies key-policy changes to
  everyone but Security, and denies `kms:GetKeyPolicy` to the agent role
  path `/agentkeel/agents/*` (ruling b, seed S6);
- a **Budgets action** on Bedrock spend at `daily_usd: 10` (ruling a).

What it does not do: wire Gateway or Identity (cut at open), reach the
security account (cut 2), or hold anything M05 owns.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_budgets as budgets
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

REPO = "andaro74/agentkeel"
SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"  # the immutable subject, as at M00
REGION = "us-west-2"
AGENT_ROLE_PATH = "/agentkeel/agents/"  # ruling b: the key policy matches agent roles by path
BOUNDARY_NAME = "agentkeel-boundary"
EVAL_ROLE_NAME = "agentkeel-evals"  # ruling f; replaces agentkeel-m00-evals
DAILY_USD = 10  # Threshold Owner (ruling a); the action attaches a Deny to the eval role

MODELS = ["amazon.nova-micro-v1:0", "anthropic.claude-sonnet-5"]
PROFILE_REGIONS = ["us-east-1", "us-east-2", "us-west-2"]
INVOKE = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
DENY = ["iam:*", "sts:AssumeRole", "logs:Delete*", "bedrock:*Guardrail*", "s3:PutBucketPolicy"]
EVAL_WORKFLOWS = [
    f"{REPO}/.github/workflows/evals.yml@refs/pull/*/merge",
    f"{REPO}/.github/workflows/evals.yml@refs/heads/main",
]
DEPLOY_WORKFLOW = f"{REPO}/.github/workflows/deploy.yml@refs/heads/main"
# The five service names a manifest may list (ruling d). Interface endpoints,
# except s3 and dynamodb, which AWS offers as gateway endpoints (ruling e).
INTERFACE_ENDPOINTS = {
    "bedrock-runtime": ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME,
    "kms": ec2.InterfaceVpcEndpointAwsService.KMS,
    "logs": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
}
GATEWAY_ENDPOINTS = {
    "s3": ec2.GatewayVpcEndpointAwsService.S3,
    "dynamodb": ec2.GatewayVpcEndpointAwsService.DYNAMODB,
}


class BootstrapStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        boundary = self._boundary()
        # Stack-wide: every role this stack makes carries it, named or not.
        iam.PermissionsBoundary.of(self).apply(boundary)

        provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self, "GitHubOidc",
            f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com",
        )  # fmt: skip

        vpc = self._vpc()
        self._execution_role(boundary)
        self._deploy_role(provider)
        self._developer_role()
        eval_role = self._eval_role(provider)
        self._agent_key(eval_role)
        self._budget(eval_role)

        cdk.CfnOutput(self, "VpcId", value=vpc.vpc_id)
        cdk.CfnOutput(self, "BoundaryArn", value=boundary.managed_policy_arn)

    # --- the boundary ------------------------------------------------------

    def _boundary(self) -> iam.ManagedPolicy:
        """What no role the platform creates may ever exceed (R3)."""
        return iam.ManagedPolicy(
            self, "Boundary",
            managed_policy_name=BOUNDARY_NAME,
            description="agentkeel: the ceiling on every role the platform creates (R3).",
            document=iam.PolicyDocument(statements=[
                iam.PolicyStatement(
                    sid="WhatAnyPlatformRoleMayDo",
                    actions=["bedrock:Invoke*", "bedrock-agentcore:*", "dynamodb:GetItem", "dynamodb:Query",
                             "kms:Decrypt", "kms:GenerateDataKey", "logs:CreateLogStream", "logs:PutLogEvents",
                             "s3:GetObject", "cloudformation:Describe*", "sts:AssumeRoleWithWebIdentity"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="NeverEscalateNeverEraseNeverOpenTheNetwork",
                    effect=iam.Effect.DENY,
                    actions=["iam:CreateUser", "iam:DeleteRolePermissionsBoundary", "iam:PutUserPolicy",
                             "logs:Delete*", "bedrock:*Guardrail*", "s3:PutBucketPolicy", "kms:PutKeyPolicy",
                             "kms:ScheduleKeyDeletion", "kms:DisableKey", "kms:GetKeyPolicy",
                             "ec2:CreateInternetGateway", "ec2:AttachInternetGateway", "ec2:CreateNatGateway",
                             "ec2:CreateVpc", "ec2:CreateVpcPeeringConnection"],
                    resources=["*"],
                ),
            ]),
        )  # fmt: skip

    # --- the network -------------------------------------------------------

    def _vpc(self) -> ec2.Vpc:
        """No internet gateway, no NAT: private subnets and endpoints only (SPEC/01 §6)."""
        vpc = ec2.Vpc(
            self, "Vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.20.0.0/16"),
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(
                name="isolated", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=24,
            )],
            flow_logs={"all": ec2.FlowLogOptions(traffic_type=ec2.FlowLogTrafficType.ALL)},
        )  # fmt: skip

        # Every endpoint policy is scoped to this account: an endpoint is not a
        # way out to another account's bucket or table (`platform-architect`).
        def this_account() -> iam.PolicyStatement:
            return iam.PolicyStatement(
                principals=[iam.AnyPrincipal()], actions=["*"], resources=["*"],
                conditions={"StringEquals": {"aws:ResourceAccount": self.account}},
            )

        for name, interface in INTERFACE_ENDPOINTS.items():
            endpoint = vpc.add_interface_endpoint(
                f"Endpoint{name.title().replace('-', '')}", service=interface, private_dns_enabled=True)
            endpoint.add_to_policy(this_account())
        for name, gateway in GATEWAY_ENDPOINTS.items():
            vpc.add_gateway_endpoint(f"Endpoint{name.title()}", service=gateway).add_to_policy(this_account())
        return vpc

    # --- the roles ---------------------------------------------------------

    def _execution_role(self, boundary: iam.ManagedPolicy) -> iam.Role:
        """What CloudFormation runs as. Not admin, and it may create a role only with the boundary."""
        role = iam.Role(
            self, "ExecutionRole",
            role_name="agentkeel-cfn-exec",
            assumed_by=iam.ServicePrincipal("cloudformation.amazonaws.com"),
            description="agentkeel: CloudFormation runs the deploy as this role, inside the boundary.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="CreateRolesOnlyInsideTheBoundary",
            actions=["iam:CreateRole", "iam:PutRolePolicy", "iam:AttachRolePolicy"],
            resources=[f"arn:aws:iam::{self.account}:role{AGENT_ROLE_PATH}*"],
            conditions={"StringEquals": {"iam:PermissionsBoundary": boundary.managed_policy_arn}},
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="NeverTouchTheBoundaryOrAKeyPolicy",
            effect=iam.Effect.DENY,
            actions=["iam:DeleteRolePermissionsBoundary", "iam:CreatePolicyVersion", "iam:DeletePolicy",
                     "kms:PutKeyPolicy", "ec2:CreateInternetGateway", "ec2:AttachInternetGateway",
                     "ec2:CreateNatGateway"],
            resources=["*"],
        ))  # fmt: skip
        return role

    def _github_principal(self, provider: iam.IOpenIdConnectProvider, subjects: list[str],
                          workflows: list[str], exact: bool) -> iam.FederatedPrincipal:  # fmt: skip
        """GitHub OIDC, `aud` and `sub` exact; the workflow exact for a deploy, by pattern for evals."""
        workflow_match = {"StringEquals" if exact else "StringLike": {
            "token.actions.githubusercontent.com:job_workflow_ref": workflows}}  # fmt: skip
        conditions: dict = {
            "StringEquals": {
                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                "token.actions.githubusercontent.com:sub": subjects,
            }
        }
        if exact:
            conditions["StringEquals"].update(workflow_match["StringEquals"])
        else:
            conditions["StringLike"] = workflow_match["StringLike"]
        return iam.FederatedPrincipal(
            provider.open_id_connect_provider_arn, conditions=conditions,
            assume_role_action="sts:AssumeRoleWithWebIdentity",
        )  # fmt: skip

    def _deploy_role(self, provider: iam.IOpenIdConnectProvider) -> iam.Role:
        """Only deploy.yml on main, and only through the execution role."""
        role = iam.Role(
            self, "DeployRole",
            role_name="agentkeel-deploy",
            max_session_duration=cdk.Duration.hours(1),  # IAM's floor
            assumed_by=self._github_principal(
                provider, [f"{SUBJECT}:ref:refs/heads/main"], [DEPLOY_WORKFLOW], exact=True),
            description="agentkeel: the only principal that may create or update an agent stack.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="DeployThroughCloudFormationOnly",
            actions=["cloudformation:CreateStack", "cloudformation:UpdateStack", "cloudformation:Describe*",
                     "cloudformation:GetTemplate", "cloudformation:CreateChangeSet",
                     "cloudformation:ExecuteChangeSet"],
            resources=[f"arn:aws:cloudformation:{REGION}:{self.account}:stack/agentkeel-*/*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="PassTheExecutionRoleAndNothingElse",
            actions=["iam:PassRole"],
            resources=[f"arn:aws:iam::{self.account}:role/agentkeel-cfn-exec"],
        ))  # fmt: skip
        return role

    def _developer_role(self) -> iam.Role:
        """S4's principal: a person, from any machine, inside the boundary. It may not deploy."""
        role = iam.Role(
            self, "DeveloperRole",
            role_name="agentkeel-developer",
            assumed_by=iam.AccountPrincipal(self.account),
            description="agentkeel: what a developer has. Seed S4 attempts a deploy with it and is refused.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadOnly", actions=["cloudformation:Describe*", "cloudformation:GetTemplate",
                                     "logs:Get*", "logs:Describe*", "bedrock:List*"],
            resources=["*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="NeverDeployNeverAssumeTheDeployRole",
            effect=iam.Effect.DENY,
            actions=["cloudformation:CreateStack", "cloudformation:UpdateStack", "cloudformation:DeleteStack",
                     "cloudformation:ExecuteChangeSet", "sts:AssumeRole", "iam:PassRole",
                     "bedrock-agentcore:CreateAgentRuntime", "bedrock-agentcore:UpdateAgentRuntime"],
            resources=["*"],
        ))  # fmt: skip
        return role

    def _eval_role(self, provider: iam.IOpenIdConnectProvider) -> iam.Role:
        """agentkeel-evals: what `make evals` runs as (ruling f). Absorbs infra/eval-role."""
        role = iam.Role(
            self, "EvalRole",
            role_name=EVAL_ROLE_NAME,
            max_session_duration=cdk.Duration.hours(1),
            assumed_by=self._github_principal(
                provider,
                [f"{SUBJECT}:pull_request", f"{SUBJECT}:ref:refs/heads/main"],
                EVAL_WORKFLOWS, exact=False),
            description="agentkeel: GitHub Actions runs make evals. Replaces agentkeel-m00-evals.",
        )  # fmt: skip

        profiles = [f"arn:aws:bedrock:{REGION}:{self.account}:inference-profile/us.{model}" for model in MODELS]
        role.add_to_policy(iam.PolicyStatement(sid="InvokePinnedProfiles", actions=INVOKE, resources=profiles))
        role.add_to_policy(iam.PolicyStatement(
            sid="InvokePinnedModelsThroughProfilesOnly", actions=INVOKE,
            resources=[f"arn:aws:bedrock:{region}::foundation-model/{model}"
                       for model in MODELS for region in PROFILE_REGIONS],
            conditions={"StringEquals": {"bedrock:InferenceProfileArn": profiles}},
        ))  # fmt: skip
        # Ruling f: refagent's runtime, and no other. The name is the agent's;
        # the construct makes it, and `make evals` calls it on main.
        role.add_to_policy(iam.PolicyStatement(
            sid="InvokeRefagentRuntimeOnly",
            actions=["bedrock-agentcore:InvokeAgentRuntime"],
            resources=[f"arn:aws:bedrock-agentcore:{REGION}:{self.account}:runtime/refagent*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="DenyEscalationAndEvidenceDeletion", effect=iam.Effect.DENY,
            actions=DENY, resources=["*"],
        ))  # fmt: skip
        cdk.CfnOutput(self, "EvalRoleArn", value=role.role_arn)
        return role

    # --- the key -----------------------------------------------------------

    def _agent_key(self, eval_role: iam.Role) -> kms.Key:
        """refagent's key. Its policy is Security's, and the agent cannot read it (S6, ruling b)."""
        key = kms.Key(
            self, "RefagentKey",
            alias="alias/agentkeel-refagent",
            enable_key_rotation=True,
            description="agentkeel: refagent's key. Only Security may change this policy (R4).",
        )  # fmt: skip
        agent_roles = f"arn:aws:iam::{self.account}:role{AGENT_ROLE_PATH}*"
        key.add_to_resource_policy(iam.PolicyStatement(
            sid="AgentsUseTheKeyAndNeverReadItsPolicy",
            principals=[iam.AnyPrincipal()], actions=["kms:Decrypt", "kms:GenerateDataKey"],
            resources=["*"],
            conditions={"ArnLike": {"aws:PrincipalArn": agent_roles}},
        ))  # fmt: skip
        key.add_to_resource_policy(iam.PolicyStatement(
            sid="NoAgentReadsThisPolicy",  # seed S6: the refusal can only come from here
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            actions=["kms:GetKeyPolicy", "kms:ListKeyPolicies"],
            resources=["*"],
            conditions={"ArnLike": {"aws:PrincipalArn": agent_roles}},
        ))  # fmt: skip
        key.add_to_resource_policy(iam.PolicyStatement(
            sid="OnlySecurityChangesThisKey",  # R4: not the deploy role, not the execution role
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            actions=["kms:PutKeyPolicy", "kms:CreateGrant", "kms:ScheduleKeyDeletion", "kms:DisableKey"],
            resources=["*"],
            conditions={"ArnNotLike": {"aws:PrincipalArn": [
                f"arn:aws:iam::{self.account}:role/agentkeel-security",
                f"arn:aws:iam::{self.account}:root",
            ]}},
        ))  # fmt: skip
        key.grant_decrypt(eval_role)
        return key

    # --- spend -------------------------------------------------------------

    def _budget(self, eval_role: iam.Role) -> budgets.CfnBudget:
        """Bedrock spend for the account, daily (ruling a). The action attaches a Deny to the eval role.

        Budgets data refreshes up to three times a day, so the worst case this
        bounds is up to one refresh interval at the account quota. No smaller
        figure is invented here.
        """
        deny_invoke = iam.ManagedPolicy(
            self, "BudgetStop",
            managed_policy_name="agentkeel-budget-stop",
            description="Attached by the Budgets action when Bedrock spend passes the daily figure.",
            document=iam.PolicyDocument(statements=[iam.PolicyStatement(
                sid="NoMoreBedrockToday", effect=iam.Effect.DENY,
                actions=["bedrock:Invoke*"], resources=["*"],
            )]),
        )  # fmt: skip
        action_role = iam.Role(
            self, "BudgetActionRole",
            assumed_by=iam.ServicePrincipal("budgets.amazonaws.com"),
            description="agentkeel: what Budgets assumes to attach the stop policy.",
        )  # fmt: skip
        action_role.add_to_policy(iam.PolicyStatement(
            actions=["iam:AttachRolePolicy"], resources=[eval_role.role_arn]))
        budget = budgets.CfnBudget(
            self, "BedrockDaily",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="agentkeel-bedrock-daily",
                budget_type="COST",
                time_unit="DAILY",
                budget_limit=budgets.CfnBudget.SpendProperty(amount=DAILY_USD, unit="USD"),
                cost_filters={"Service": ["Amazon Bedrock"]},
            ),
        )  # fmt: skip
        budgets.CfnBudgetsAction(
            self, "BedrockDailyStop",
            action_threshold=budgets.CfnBudgetsAction.ActionThresholdProperty(type="PERCENTAGE", value=100),
            action_type="APPLY_IAM_POLICY",
            approval_model="AUTOMATIC",
            budget_name=budget.budget.budget_name,
            definition=budgets.CfnBudgetsAction.DefinitionProperty(
                iam_action_definition=budgets.CfnBudgetsAction.IamActionDefinitionProperty(
                    policy_arn=deny_invoke.managed_policy_arn, roles=[eval_role.role_name])),
            execution_role_arn=action_role.role_arn,
            notification_type="ACTUAL",
            subscribers=[],
        )  # fmt: skip
        return budget


app = cdk.App()
stack = BootstrapStack(
    app, "AgentkeelBootstrap",
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M01 bootstrap: boundary, roles, VPC, key, budget. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
# One suppression per resource, each with the reason that resource needs it.
# A stack-wide suppression would silence IAM5 on an Allow added later, which
# is the rule worth keeping. Every Allow in this stack names its resources.
CEILING = ("A ceiling, not a grant: a Deny that must cover every resource, including ones that do not "
           "exist yet. Narrowing it to named ARNs would let a later attach slip past it.")
for path, reason in [
    ("AgentkeelBootstrap/Boundary/Resource",
     f"The permission boundary itself. {CEILING}"),
    ("AgentkeelBootstrap/ExecutionRole/DefaultPolicy/Resource",
     f"iam:CreateRole is scoped to the agent role path and conditioned on the boundary; the Deny is a "
     f"ceiling. {CEILING}"),
    ("AgentkeelBootstrap/DeployRole/DefaultPolicy/Resource",
     "cloudformation:* is scoped to stack/agentkeel-*, which is the set of stacks this platform deploys; "
     "the stack id suffix is AWS's and cannot be named in advance."),
    ("AgentkeelBootstrap/DeveloperRole/DefaultPolicy/Resource",
     f"A read-only Allow over describe and list calls, and a Deny on deploying. {CEILING}"),
    ("AgentkeelBootstrap/EvalRole/DefaultPolicy/Resource",
     f"The pinned profiles and foundation models are named; runtime/refagent* covers the versioned runtime "
     f"name AgentCore assigns. The five-action Deny is a ceiling. {CEILING}"),
]:
    NagSuppressions.add_resource_suppressions_by_path(
        stack, path, [{"id": "AwsSolutions-IAM5", "reason": reason}])
# The endpoint security groups are CDK's own, and their rule is the VPC's CIDR,
# which cdk-nag cannot resolve at synth (it reads as an intrinsic function).
for name in ("EndpointBedrockRuntime", "EndpointKms", "EndpointLogs"):
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelBootstrap/Vpc/{name}/SecurityGroup/Resource",
        [{"id": "CdkNagValidationFailure", "reason": "AwsSolutions-EC23 cannot resolve the rule: the source "
                                                     "is the VPC's own CIDR, an intrinsic function at synth. "
                                                     "The rule allows 443 from inside this VPC and nothing else."}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
