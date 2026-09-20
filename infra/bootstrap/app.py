"""The M01 bootstrap stack (Security seat; SPEC/01 §6, feasibility.md §2.6 a, b, d, e, f).

Deployed once, to the agent account, by a human with admin, during M01 PR 2
and before PR 2's first CI run — as `infra/eval-role` was at M00. Nothing
else may change it.

    cd infra/bootstrap && npx cdk diff && npx cdk deploy

What it makes:

- **two permission boundaries** (ruling s). `agentkeel-boundary` is the agent
  plane's allow-list: attached to nothing here, published as a parameter, and
  put on the agent role by `GovernedAgent`. It is what S5 and S6 read.
  `agentkeel-deploy-boundary` is the deploy plane's deny-list, applied
  stack-wide (`PermissionsBoundary.of`) so every role this stack synthesises
  carries it, not only the ones named here — including the flow-log role and
  the Budgets action role;
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
- a **Budgets action** on Bedrock spend at `daily_usd: 10` (ruling a);
- the **ECR repository** the runtime image is pulled from, tag-immutable, so
  a digest cannot be moved to other bytes (SPEC/01 §6, "at load");
- the **Security-owned parameters** `GovernedAgent` reads: the boundary ARN,
  the VPC, the subnets and the three interface endpoints' security groups.
  The two gateway-endpoint prefix lists have no CloudFormation attribute; the
  human who deploys this stack writes those two parameters, with one command
  each (`infra/bootstrap/README.md`).

What it does not do: wire Gateway or Identity (cut at open), reach the
security account (cut 2), or hold anything M05 owns.
"""

from __future__ import annotations

import os
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_budgets as budgets
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_ssm as ssm
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

REPO = "andaro74/agentkeel"
SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"  # the immutable subject, as at M00
REGION = "us-west-2"
AGENT_ROLE_PATH = "/agentkeel/agents/"  # ruling b: the key policy matches agent roles by path
BOUNDARY_NAME = "agentkeel-boundary"  # the agent plane's allow-list (S5, S6)
DEPLOY_BOUNDARY_NAME = "agentkeel-deploy-boundary"  # the deploy plane's deny-list (ruling s)
EVAL_ROLE_NAME = "agentkeel-evals"  # ruling f; replaces agentkeel-m00-evals
# What GovernedAgent reads. The names are the construct's; they are repeated
# here rather than imported, because the bootstrap stack is deployed by hand
# and must not depend on the construct's code being importable.
BOUNDARY_PARAM = "/agentkeel/security/boundary-arn"
VPC_PARAM = "/agentkeel/security/vpc-id"
SUBNETS_PARAM = "/agentkeel/security/subnet-ids"
ENDPOINT_PARAM = "/agentkeel/security/endpoint/{name}"
DAILY_USD = 10  # Threshold Owner (ruling a); the action attaches a Deny to the eval role

MODELS = ["amazon.nova-micro-v1:0", "anthropic.claude-sonnet-4-6"]  # ruling p
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

        self.endpoint_groups: dict[str, ec2.ISecurityGroup] = {}
        boundary = self._boundary()
        deploy_boundary = self._deploy_boundary()
        # Stack-wide, and it is the DEPLOY boundary, not the agent one (ruling
        # s). This stack creates no role under /agentkeel/agents/: the roles
        # here deploy the platform, and capping them with the agent plane's
        # allow-list left the execution role able to create nothing. Every role
        # this stack makes carries this one, named here or not — the flow-log
        # role and the Budgets action role included.
        iam.PermissionsBoundary.of(self).apply(deploy_boundary)

        provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self, "GitHubOidc",
            f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com",
        )  # fmt: skip

        vpc = self._vpc()
        execution_role = self._execution_role(boundary)
        self._deploy_role(provider)
        self._developer_role()
        eval_role = self._eval_role(provider)
        self._agent_key(eval_role)
        self._budget(eval_role)

        self._image_repository()
        self._parameters(boundary, vpc)

        cdk.CfnOutput(self, "ExecutionRoleArn", value=execution_role.role_arn)
        cdk.CfnOutput(self, "VpcId", value=vpc.vpc_id)
        cdk.CfnOutput(self, "BoundaryArn", value=boundary.managed_policy_arn)
        cdk.CfnOutput(self, "DeployBoundaryArn", value=deploy_boundary.managed_policy_arn)

    # --- the boundary ------------------------------------------------------

    def _boundary(self) -> iam.ManagedPolicy:
        """The agent plane's ceiling: what an agent role may never exceed (R3, ruling s).

        An allow-list, and it is attached to nothing in this stack. Roles
        under `/agentkeel/agents/` carry it, and `GovernedAgent` is what
        attaches it, by ARN, from the parameter published below. Seeds S5
        and S6 read this policy; the deploy plane has its own, and the two
        must not be confused, because an allow-list on a role that deploys
        caps it to nothing.
        """
        return iam.ManagedPolicy(
            self, "Boundary",
            managed_policy_name=BOUNDARY_NAME,
            description="agentkeel: the ceiling on every role the platform creates (R3).",
            document=iam.PolicyDocument(statements=[
                iam.PolicyStatement(
                    sid="WhatAnyPlatformRoleMayDo",
                    actions=["bedrock:Invoke*", "bedrock-agentcore:*", "dynamodb:GetItem", "dynamodb:Query",
                             "kms:Decrypt", "kms:GenerateDataKey", "logs:CreateLogStream", "logs:PutLogEvents",
                             "s3:GetObject", "cloudformation:Describe*", "sts:AssumeRoleWithWebIdentity",
                             # Seed S6, and the only reason it is here (ruling t).
                             # An allow-list caps by omission, so leaving this
                             # out would have made the BOUNDARY refuse S6 and
                             # F1.3 a check that cannot fail. A ceiling is not a
                             # grant: no agent role's own policy allows it, and
                             # the key policy denies it by role path (ruling b).
                             "kms:GetKeyPolicy"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="NeverEscalateNeverEraseNeverOpenTheNetwork",
                    effect=iam.Effect.DENY,
                    actions=["iam:CreateUser", "iam:DeleteRolePermissionsBoundary", "iam:PutUserPolicy",
                             "logs:Delete*", "bedrock:*Guardrail*", "s3:PutBucketPolicy", "kms:PutKeyPolicy",
                             "kms:ScheduleKeyDeletion", "kms:DisableKey",
                             # kms:GetKeyPolicy is not here, and it is in the Allow above:
                             # the key policy is what must refuse S6 (ruling t).
                             "ec2:CreateInternetGateway", "ec2:AttachInternetGateway", "ec2:CreateNatGateway",
                             "ec2:CreateVpc", "ec2:CreateVpcPeeringConnection"],
                    resources=["*"],
                ),
            ]),
        )  # fmt: skip

    def _deploy_boundary(self) -> iam.ManagedPolicy:
        """The deploy plane's ceiling: everything, less what no deployer may ever do (ruling s).

        A deny-list, not an allow-list, and that is the whole point. The
        execution role has to be able to create a VPC endpoint, a table, a
        security group and an agent runtime; an allow-list of the agent's
        ten actions capped it to nothing, so the stack deployed and could
        then deploy nothing (`platform-architect` BLOCK 1).

        Two actions are deliberately **not** denied here, and each would
        undo a control if it were:

        - `iam:*` as a whole. It would cap `iam:CreateRole` on the execution
          role and `iam:PassRole` on the deploy role, which is the hole this
          policy exists to close. The escalation primitives are denied by
          name instead, and creating a role is still conditioned on the
          agent boundary in the execution role's own policy.
        - `sts:AssumeRole`. The developer role holds it on purpose, so that
          seed S4's first two attempts are refused by the deploy role's
          **trust policy** and by nothing nearer. A boundary that refused
          the assume would be the wrong control firing, which is the defect
          repaired in `c5bfdd1`, one level up.

        R4 is held by the four key-policy actions below, which is what R4
        names: no deploy-plane role may alter, grant on, disable or delete
        a key.
        """
        return iam.ManagedPolicy(
            self, "DeployBoundary",
            managed_policy_name=DEPLOY_BOUNDARY_NAME,
            description="agentkeel: the ceiling on every role that deploys the platform (R3, R4).",
            document=iam.PolicyDocument(statements=[
                iam.PolicyStatement(
                    sid="WhatADeployerMayDo",
                    actions=["*"], resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="NeverEscalate",
                    effect=iam.Effect.DENY,
                    actions=["iam:CreateUser", "iam:PutUserPolicy", "iam:AttachUserPolicy",
                             "iam:CreateAccessKey", "iam:CreateLoginProfile", "iam:UpdateLoginProfile",
                             "iam:PutRolePermissionsBoundary", "iam:DeleteRolePermissionsBoundary",
                             "iam:CreatePolicyVersion", "iam:SetDefaultPolicyVersion"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="NeverTouchAKeyPolicyNeverEraseEvidenceNeverOpenTheNetwork",
                    effect=iam.Effect.DENY,
                    actions=["kms:PutKeyPolicy", "kms:CreateGrant", "kms:ScheduleKeyDeletion", "kms:DisableKey",
                             "logs:Delete*", "bedrock:*Guardrail*", "s3:PutBucketPolicy",
                             "ec2:CreateInternetGateway", "ec2:AttachInternetGateway",
                             "ec2:CreateNatGateway", "ec2:CreateVpcPeeringConnection"],
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
            self.endpoint_groups[name] = endpoint.connections.security_groups[0]
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
        # Seed S4 attempts the assume, and the thing that must refuse it is the
        # deploy role's TRUST policy, not this role's own Deny. So the assume is
        # allowed here, exactly as S6 grants kms:GetKeyPolicy in the agent role's
        # own policy for its attempt. If the trust conditions are ever relaxed,
        # the assume succeeds and S4 fires.
        role.add_to_policy(iam.PolicyStatement(
            sid="AssumeIsAllowedHereSoTheTrustPolicyIsWhatRefusesIt",
            actions=["sts:AssumeRole"],
            resources=[f"arn:aws:iam::{self.account}:role/agentkeel-deploy",
                       f"arn:aws:iam::{self.account}:role/agentkeel-cfn-exec"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="NeverDeploy",
            effect=iam.Effect.DENY,
            actions=["cloudformation:CreateStack", "cloudformation:UpdateStack", "cloudformation:DeleteStack",
                     "cloudformation:ExecuteChangeSet", "iam:PassRole",
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
            # R4: not the deploy role, not the execution role. `agentkeel-security`
            # does not exist yet, so in practice the only principal left is the
            # account root — the break-glass admin SPEC/01 §1 puts out of scope.
            # The half this does hold is the deploy role and the execution role,
            # and SPEC/01 §9 lists it as a control with no seeded case.
            sid="OnlyRootAndSecurityChangeThisKey",
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
        # CloudFormation requires at least one subscriber. The address is not
        # in the repo: the human passes it at deploy (README.md).
        subscriber = cdk.CfnParameter(
            self, "BudgetSubscriberEmail",
            description="Who Budgets notifies when Bedrock spend passes the daily figure.",
            allowed_pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        )
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
            subscribers=[budgets.CfnBudgetsAction.SubscriberProperty(
                address=subscriber.value_as_string, type="EMAIL")],
        )  # fmt: skip
        return budget


# A fixed output directory, so `make validate` reads the NagReport of the
# synth it just ran. The cdk CLI sets CDK_OUTDIR; a plain python run does not.
    def _image_repository(self) -> ecr.Repository:
        """Where the runtime image is pulled from. Tag-immutable: a digest is the bytes (SPEC/01 §6)."""
        return ecr.Repository(
            self, "RefagentImage",
            repository_name="agentkeel-refagent",
            image_tag_mutability=ecr.TagMutability.IMMUTABLE,
            image_scan_on_push=True,
            encryption=ecr.RepositoryEncryption.AES_256,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip

    def _parameters(self, boundary: iam.ManagedPolicy, vpc: ec2.Vpc) -> None:
        """The Security-owned parameters `GovernedAgent` reads (SPEC/01 §6).

        Not CDK context: a construct that read context would take whatever
        the synthesising machine had in `cdk.context.json`. These are
        written by this stack, in the account, and only this stack changes
        them.

        The two gateway endpoints are missing on purpose. AWS gives no
        CloudFormation attribute for a managed prefix list id, so inventing
        one here would be a guess; the human who deploys this stack writes
        those two parameters (README.md), and a deploy of an agent stack
        fails while they are absent.
        """
        ssm.StringParameter(
            self, "ParamBoundary", parameter_name=BOUNDARY_PARAM, string_value=boundary.managed_policy_arn,
            description="agentkeel: the permission boundary every platform role carries.",
        )  # fmt: skip
        ssm.StringParameter(
            self, "ParamVpc", parameter_name=VPC_PARAM, string_value=vpc.vpc_id,
            description="agentkeel: the platform VPC. An agent runs in this one or in none.",
        )  # fmt: skip
        ssm.StringListParameter(
            self, "ParamSubnets", parameter_name=SUBNETS_PARAM,
            string_list_value=[subnet.subnet_id for subnet in vpc.isolated_subnets],
            description="agentkeel: the isolated subnets. No internet gateway, no NAT.",
        )  # fmt: skip
        for name, group in self.endpoint_groups.items():
            ssm.StringParameter(
                self, f"ParamEndpoint{name.title().replace('-', '')}",
                parameter_name=ENDPOINT_PARAM.format(name=name),
                string_value=group.security_group_id,
                description=f"agentkeel: the {name} interface endpoint. An agent reaches it and nothing else.",
            )  # fmt: skip


app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = BootstrapStack(
    app, "AgentkeelBootstrap",
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M01 bootstrap: boundary, roles, VPC, key, budget. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
# One suppression per resource, and each one names what it serves: the
# seeded case (S3, S4, S5, S6, S8) or the line of SPEC/01 §6 that requires
# the wildcard. A suppression that names neither is a finding, not a
# suppression: remove it and let the rule fail until a seat rules on it
# (Security, M01 PR 2). A stack-wide suppression would silence IAM5 on an
# Allow added later, which is the rule worth keeping.
CEILING = ("A ceiling, not a grant: a Deny must cover every resource, including ones that do not exist "
           "yet, or a later attach slips past it.")
SUPPRESSIONS = {
    "DeployBoundary/Resource": (
        "SPEC/01 §6: 'two permission boundaries, one per plane'. This is the deploy plane's, and it is a "
        "deny-list: Allow * with the escalation, key-policy, evidence and network primitives denied by name. "
        "It is what makes seed S4 readable at all — the developer role keeps sts:AssumeRole, so the deploy "
        "role's trust policy is what refuses the attempt — and R4 is held by its four kms denies. An "
        "allow-list here capped the execution role to creating nothing (ruling s)."
    ),
    "Boundary/Resource": (
        "SPEC/01 §6: 'the permission boundary, on every role either stack synthesises, applied "
        "stack-wide'. This is that boundary, and it is what seed S5 reads: a role handed to GovernedAgent "
        f"without it is refused at synth. {CEILING}"
    ),
    "ExecutionRole/DefaultPolicy/Resource": (
        "SPEC/01 §6: 'the CloudFormation execution role the deploy passes, which carries the "
        "boundary and may create a role only with the boundary attached'. iam:CreateRole is scoped to "
        f"{AGENT_ROLE_PATH} and conditioned on iam:PermissionsBoundary; the wildcard is in the Deny. It is "
        f"half of what seed S4 reads: the laptop cannot reach CloudFormation, and CloudFormation cannot "
        f"exceed this. {CEILING}"
    ),
    "DeployRole/DefaultPolicy/Resource": (
        "SPEC/01 §6: 'the deploy role, trusted with StringEquals on aud, the immutable sub for "
        "refs/heads/main, and job_workflow_ref'. Seed S4 is an attempt to do from a laptop what only this "
        "role may do. cloudformation:* is scoped to stack/agentkeel-*, the set of stacks this platform "
        "deploys; AWS appends the stack id suffix, which cannot be named in advance."
    ),
    "DeveloperRole/DefaultPolicy/Resource": (
        "SPEC/01 §6: 'the developer role (§1), boundary on'. This is seed S4's principal. "
        "The Allow is read-only describe and list; the wildcard is in the Deny that refuses the deploy. "
        f"{CEILING}"
    ),
    "EvalRole/DefaultPolicy/Resource": (
        "SPEC/01 §6: 'the eval role, absorbed from infra/eval-role/ under a new name, with its Deny "
        "statement (item 33) and trust conditions as they stand'. The two profiles and the foundation "
        "models are named by ARN; runtime/refagent* covers the versioned runtime name AgentCore assigns, "
        f"which does not exist until the deploy. The five-action Deny is the ceiling. {CEILING}"
    ),
}
for path, reason in SUPPRESSIONS.items():
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelBootstrap/{path}", [{"id": "AwsSolutions-IAM5", "reason": reason}])
# Not an IAM wildcard: cdk-nag cannot resolve these rules at all. They are
# CDK's own endpoint security groups, and their source is the VPC's CIDR,
# an intrinsic function at synth.
for name in ("EndpointBedrockRuntime", "EndpointKms", "EndpointLogs"):
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelBootstrap/Vpc/{name}/SecurityGroup/Resource",
        [{"id": "CdkNagValidationFailure",
          "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to "
                    "the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own "
                    "CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and "
                    "nothing else, and the VPC has no way out."}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
