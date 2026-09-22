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
  `bedrock-agentcore:InvokeAgentRuntime` on refagent's runtime only, and
  three reads of which bytes that runtime runs (ADR-0007, P1);
- a **VPC with no internet gateway and no NAT**: interface endpoints for
  bedrock-runtime, kms, logs, ecr.api and ecr.dkr, gateway endpoints for s3
  and dynamodb (ruling e, ADR-0006), each with a policy scoped to this
  account. The one exception is s3's read of ECR's own layer bucket (B1);
- one **KMS key per agent**, whose policy denies key-policy changes to
  everyone but Security, and denies `kms:GetKeyPolicy` to the agent role
  path `/agentkeel/agents/*` (ruling b, seed S6);
- **two Budgets budgets** on Bedrock spend (ruling a, amended): a daily one
  at `daily_usd` that notifies and stops nothing, and a monthly one that
  carries the Deny action. AWS Budgets Actions do not support a daily
  budget, so the figure that was ruled and the figure that stops anything
  are not the same figure;
- the **ECR repository** the runtime image is pulled from, tag-immutable, so
  a digest cannot be moved to other bytes (SPEC/01 §6, "at load");
- the **Security-owned parameters** `GovernedAgent` reads: the boundary ARN,
  the VPC, the subnets and the five interface endpoints' security groups.
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
DAILY_USD = 10  # Threshold Owner (ruling a). At M01 this is an alert, not a stop: see below.
# AWS Budgets Actions do not support a daily budget ("AWS Budgets Actions
# don't support daily granularity budget for now", 2026-09-20), so the
# mechanical stop has to hang off a monthly budget. 30 x the ruled daily
# figure is the literal translation and nothing more; the Threshold Owner
# re-rules it against measured spend (ruling a, amended).
MONTHLY_USD = DAILY_USD * 30

MODELS = ["amazon.nova-micro-v1:0", "anthropic.claude-sonnet-4-6"]  # ruling p
PROFILE_REGIONS = ["us-east-1", "us-east-2", "us-west-2"]
INVOKE = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
DENY = ["iam:*", "sts:AssumeRole", "logs:Delete*", "bedrock:*Guardrail*", "s3:PutBucketPolicy"]
EVAL_WORKFLOWS = [
    f"{REPO}/.github/workflows/evals.yml@refs/pull/*/merge",
    f"{REPO}/.github/workflows/evals.yml@refs/heads/main",
]
DEPLOY_WORKFLOW = f"{REPO}/.github/workflows/deploy.yml@refs/heads/main"
# The seven service names a manifest may list (ruling d, amended at M01 PR 3).
# Interface endpoints, except s3 and dynamodb, which AWS offers as gateway
# endpoints (ruling e).
INTERFACE_ENDPOINTS = {
    "bedrock-runtime": ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME,
    "kms": ec2.InterfaceVpcEndpointAwsService.KMS,
    "logs": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
    # Ruling d, amended at M01 PR 3 (B1): a runtime in a VPC with no way out
    # pulls its image through these two, and AWS lists both as required.
    "ecr.api": ec2.InterfaceVpcEndpointAwsService.ECR,
    "ecr.dkr": ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
}
# The regional bucket ECR keeps image layers in. AWS owns it, so the S3
# endpoint's this-account policy refused it; it is named here and nowhere
# else is outside the account (B1, from AgentCore's VPC documentation).
ECR_LAYER_BUCKET = f"prod-{REGION}-starport-layer-bucket"
GATEWAY_ENDPOINTS = {
    "s3": ec2.GatewayVpcEndpointAwsService.S3,
    "dynamodb": ec2.GatewayVpcEndpointAwsService.DYNAMODB,
}


def endpoint_id(name: str) -> str:
    """`bedrock-runtime` -> `BedrockRuntime`, `ecr.api` -> `EcrApi`. The three older ids are unchanged,
    so their endpoints and parameters are not replaced on redeploy."""
    return name.title().replace("-", "").replace(".", "")


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
        execution_role = self._execution_role(boundary, vpc)
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
                             # B1, ruling d amended (M01 PR 3): the runtime
                             # pulls its own image and makes its own log
                             # group, as its role. Read-only on ECR: no push,
                             # no delete. AgentCore's documented execution role.
                             "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:GetAuthorizationToken",
                             "logs:CreateLogGroup", "logs:DescribeLogStreams", "logs:DescribeLogGroups",
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
                f"Endpoint{endpoint_id(name)}", service=interface, private_dns_enabled=True)
            endpoint.add_to_policy(this_account())
            self.endpoint_groups[name] = endpoint.connections.security_groups[0]
        for name, gateway in GATEWAY_ENDPOINTS.items():
            endpoint = vpc.add_gateway_endpoint(f"Endpoint{name.title()}", service=gateway)
            endpoint.add_to_policy(this_account())
            if name == "s3":
                # B1: the image's layers, read-only, from ECR's own bucket.
                endpoint.add_to_policy(iam.PolicyStatement(
                    sid="EcrImageLayersOnly",
                    principals=[iam.AnyPrincipal()], actions=["s3:GetObject"],
                    resources=[f"arn:aws:s3:::{ECR_LAYER_BUCKET}/*"],
                ))  # fmt: skip
        return vpc

    # --- the roles ---------------------------------------------------------

    def _execution_role(self, boundary: iam.ManagedPolicy, vpc: ec2.Vpc) -> iam.Role:
        """What CloudFormation runs as. Not admin, and it may create a role only with the boundary.

        BLOCK F (M01 PR 3). Until then its whole grant was the IAM statement
        below, and the construct makes a security group, a table, an
        inference profile and a runtime, so refagent's stack would have
        failed on its first non-IAM resource. The grants below are what
        `GovernedAgent` renders and nothing more, resource type by resource
        type (`tests/test_bootstrap.py` holds the list against the construct's
        template):

        | Construct resource | Grant |
        |---|---|
        | 8 `AWS::SSM::Parameter::Value` | `ssm:GetParameters`, `/agentkeel/security/*` |
        | `AWS::EC2::SecurityGroup`, 2 `SecurityGroupEgress` | create, egress, delete, in this VPC only |
        | `AWS::DynamoDB::Table` | create, describe, PITR, tags; no delete (RETAIN) |
        | `AWS::IAM::Role`, `AWS::IAM::Policy` | under `/agentkeel/agents/`, boundary-conditioned |
        | `AWS::Bedrock::ApplicationInferenceProfile` | create, read, tag, delete, `agentkeel-*` |
        | `AWS::BedrockAgentCore::Runtime` | runtime and its workload identity; pass the agent role to AgentCore only |

        Nothing here grants `dynamodb:DeleteTable`: the table is RETAIN, so
        CloudFormation never calls it, and a rollback leaves the table
        rather than failing on it.
        """
        role = iam.Role(
            self, "ExecutionRole",
            role_name="agentkeel-cfn-exec",
            assumed_by=iam.ServicePrincipal("cloudformation.amazonaws.com"),
            description="agentkeel: CloudFormation runs the deploy as this role, inside the boundary.",
        )  # fmt: skip
        agent_roles = f"arn:aws:iam::{self.account}:role{AGENT_ROLE_PATH}*"
        role.add_to_policy(iam.PolicyStatement(
            sid="CreateRolesOnlyInsideTheBoundary",
            actions=["iam:CreateRole", "iam:PutRolePolicy", "iam:AttachRolePolicy",
                     "iam:DeleteRolePolicy", "iam:DetachRolePolicy"],
            resources=[agent_roles],
            conditions={"StringEquals": {"iam:PermissionsBoundary": boundary.managed_policy_arn}},
        ))  # fmt: skip
        # The IAM::Role read and delete handlers (describe-type, 2026-09-21).
        # None takes a boundary key; all are on the agent path and nowhere
        # else. Without the two List calls a rollback leaves the role
        # DELETE_FAILED, which is the half-built stack `refuse` exists to stop.
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadAndRollBackAgentRoles",
            actions=["iam:GetRole", "iam:GetRolePolicy", "iam:DeleteRole", "iam:ListRolePolicies",
                     "iam:ListAttachedRolePolicies", "iam:TagRole", "iam:UntagRole"],
            resources=[agent_roles],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="PassAnAgentRoleToAgentCoreOnly",
            actions=["iam:PassRole"],
            resources=[agent_roles],
            conditions={"StringEquals": {"iam:PassedToService": "bedrock-agentcore.amazonaws.com"}},
        ))  # fmt: skip
        # A runtime in VPC mode places its ENIs through AgentCore's
        # service-linked role, created on first use by whoever creates the
        # first runtime. That one role, by service name.
        role.add_to_policy(iam.PolicyStatement(
            sid="AgentCoreNetworkServiceLinkedRole",
            actions=["iam:CreateServiceLinkedRole"],
            resources=[f"arn:aws:iam::{self.account}:role/aws-service-role/"
                       "network.bedrock-agentcore.amazonaws.com/*"],
            conditions={"StringEquals": {"iam:AWSServiceName": "network.bedrock-agentcore.amazonaws.com"}},
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheSecurityParameters",
            actions=["ssm:GetParameters"],
            resources=[f"arn:aws:ssm:{REGION}:{self.account}:parameter/agentkeel/security/*"],
        ))  # fmt: skip

        # The security group, in this stack's VPC and no other.
        vpc_arn = f"arn:aws:ec2:{REGION}:{self.account}:vpc/{vpc.vpc_id}"
        # CreateSecurityGroup authorises on the VPC and on the new group. The
        # group does not exist yet, so IAM has no `ec2:Vpc` for it, and a
        # condition on that key refuses every create; simulate-principal-policy
        # read exactly that on the deployed role (M01 PR 3). The VPC resource
        # is what holds creation to the platform VPC, as AWS's own examples do.
        role.add_to_policy(iam.PolicyStatement(
            sid="CreateSecurityGroupsInThePlatformVpcOnly",
            actions=["ec2:CreateSecurityGroup"],
            resources=[vpc_arn, f"arn:aws:ec2:{REGION}:{self.account}:security-group/*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ManageSecurityGroupsInThePlatformVpcOnly",
            actions=["ec2:DeleteSecurityGroup", "ec2:CreateTags",
                     "ec2:AuthorizeSecurityGroupEgress", "ec2:RevokeSecurityGroupEgress"],
            resources=[f"arn:aws:ec2:{REGION}:{self.account}:security-group/*"],
            conditions={"ArnEquals": {"ec2:Vpc": vpc_arn}},
        ))  # fmt: skip
        # The runtime in VPC mode places its interface in the platform's
        # subnets, behind the construct's group, and in no other VPC.
        # All three resources must be allowed. The new interface has no
        # `ec2:Vpc` until it exists (the same defect as CreateSecurityGroup,
        # read on the deployed role), so the subnet and the group carry the
        # condition and the interface does not.
        role.add_to_policy(iam.PolicyStatement(
            sid="RuntimeInterfacesInThePlatformVpcOnly",
            actions=["ec2:CreateNetworkInterface"],
            resources=[f"arn:aws:ec2:{REGION}:{self.account}:{kind}/*" for kind in ("subnet", "security-group")],
            conditions={"ArnEquals": {"ec2:Vpc": vpc_arn}},
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="TheNewInterfaceItself",
            actions=["ec2:CreateNetworkInterface"],
            resources=[f"arn:aws:ec2:{REGION}:{self.account}:network-interface/*"],
        ))  # fmt: skip
        # An egress rule is a resource of its own for authorisation. The
        # prefix list it names is not: AWS's service reference lists
        # security-group and security-group-rule for these two, and no more.
        role.add_to_policy(iam.PolicyStatement(
            sid="EgressRulesAsResources",
            actions=["ec2:AuthorizeSecurityGroupEgress", "ec2:RevokeSecurityGroupEgress"],
            resources=[f"arn:aws:ec2:{REGION}:{self.account}:security-group-rule/*"],
        ))  # fmt: skip
        # Describe calls take no resource-level permission.
        role.add_to_policy(iam.PolicyStatement(
            sid="DescribeTheNetwork",
            actions=["ec2:DescribeSecurityGroups", "ec2:DescribeSecurityGroupRules",
                     "ec2:DescribeVpcs", "ec2:DescribeSubnets", "ec2:DescribeInstances"],
            resources=["*"],
        ))  # fmt: skip

        role.add_to_policy(iam.PolicyStatement(
            sid="TheRightsTableAndNoDelete",
            actions=["dynamodb:CreateTable", "dynamodb:DescribeTable", "dynamodb:UpdateTable",
                     "dynamodb:DescribeContinuousBackups", "dynamodb:UpdateContinuousBackups",
                     "dynamodb:DescribeTimeToLive", "dynamodb:ListTagsOfResource",
                     "dynamodb:TagResource", "dynamodb:UntagResource",
                     # The read handler, which CloudFormation runs after create.
                     "dynamodb:DescribeContributorInsights", "dynamodb:DescribeKinesisStreamingDestination",
                     "dynamodb:GetResourcePolicy"],
            resources=[f"arn:aws:dynamodb:{REGION}:{self.account}:table/agentkeel-*-rights"],
        ))  # fmt: skip

        profiles = f"arn:aws:bedrock:{REGION}:{self.account}:application-inference-profile/*"
        role.add_to_policy(iam.PolicyStatement(
            sid="OneInferenceProfilePerAgent",
            actions=["bedrock:CreateInferenceProfile", "bedrock:GetInferenceProfile",
                     "bedrock:DeleteInferenceProfile", "bedrock:TagResource",
                     "bedrock:UntagResource", "bedrock:ListTagsForResource"],
            resources=[profiles],
        ))  # fmt: skip
        # The profile copies from a pinned system profile (ruling p), and no other.
        role.add_to_policy(iam.PolicyStatement(
            sid="CopyFromThePinnedProfilesOnly",
            actions=["bedrock:CreateInferenceProfile", "bedrock:GetInferenceProfile"],
            resources=[f"arn:aws:bedrock:{REGION}:{self.account}:inference-profile/us.{model}" for model in MODELS]
                      + [f"arn:aws:bedrock:{region}::foundation-model/{model}"
                         for model in MODELS for region in PROFILE_REGIONS],
        ))  # fmt: skip

        agentcore = f"arn:aws:bedrock-agentcore:{REGION}:{self.account}"
        role.add_to_policy(iam.PolicyStatement(
            sid="TheRuntimeAndItsWorkloadIdentity",
            actions=["bedrock-agentcore:GetAgentRuntime",
                     "bedrock-agentcore:UpdateAgentRuntime", "bedrock-agentcore:DeleteAgentRuntime",
                     "bedrock-agentcore:CreateAgentRuntimeEndpoint", "bedrock-agentcore:GetAgentRuntimeEndpoint",
                     "bedrock-agentcore:UpdateAgentRuntimeEndpoint", "bedrock-agentcore:DeleteAgentRuntimeEndpoint",
                     "bedrock-agentcore:CreateWorkloadIdentity", "bedrock-agentcore:DeleteWorkloadIdentity",
                     "bedrock-agentcore:TagResource", "bedrock-agentcore:UntagResource",
                     "bedrock-agentcore:ListTagsForResource"],
            resources=[f"{agentcore}:runtime/*",
                       f"{agentcore}:workload-identity-directory/default",
                       f"{agentcore}:workload-identity-directory/default/workload-identity/*"],
        ))  # fmt: skip
        # CreateAgentRuntime takes no resource-level permission (AWS service
        # reference: resource `*` only), so `runtime/*` never matched it, and
        # simulate-principal-policy read implicitDeny on the deployed role.
        # It does take `bedrock-agentcore:subnets`, so the create is held to
        # the platform's own subnets instead, and must name subnets at all:
        # no runtime outside the platform VPC, enforced by IAM as well as by
        # the construct's synth check (S8).
        role.add_to_policy(iam.PolicyStatement(
            sid="CreateRuntimesInThePlatformSubnetsOnly",
            actions=["bedrock-agentcore:CreateAgentRuntime"],
            resources=["*"],
            conditions={
                "ForAllValues:StringEquals": {
                    "bedrock-agentcore:subnets": [s.subnet_id for s in vpc.isolated_subnets]},
                "Null": {"bedrock-agentcore:subnets": "false"},
            },
        ))  # fmt: skip
        # The Runtime create handler's VPC-mode calls (describe-type,
        # 2026-09-21). Not scoped further because the handler does not say
        # which lattice resources it names; flagged in pr3.md, Unsure 3.
        role.add_to_policy(iam.PolicyStatement(
            sid="RuntimeVpcModeLattice",
            actions=["vpc-lattice:GetResourceConfiguration", "vpc-lattice:CreateServiceNetworkResourceAssociation",
                     "vpc-lattice:GetServiceNetworkResourceAssociation",
                     "vpc-lattice:ListServiceNetworkResourceAssociations", "vpc-lattice:AssociateViaAWSService"],
            resources=["*"],
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
        # BLOCK F, the deploy role's half (M01 PR 3): what deploy.yml's own
        # steps call, step by step, and nothing a step does not call.
        #
        # `amazon-ecr-login`: GetAuthorizationToken, which takes no resource.
        role.add_to_policy(iam.PolicyStatement(
            sid="LogInToEcr", actions=["ecr:GetAuthorizationToken"], resources=["*"]))
        # `docker push`, and the layer check it makes first. The repository is
        # tag-immutable, so PutImage writes a tag once. No ecr:Delete*.
        role.add_to_policy(iam.PolicyStatement(
            sid="PushTheAgentImage",
            actions=["ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
                     "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:BatchGetImage",
                     "ecr:GetDownloadUrlForLayer"],
            resources=[f"arn:aws:ecr:{REGION}:{self.account}:repository/agentkeel-*"],
        ))  # fmt: skip
        # `scripts/load_rights_table.py`: put_item per row, then describe_table.
        # Not BatchWriteItem, which it does not call. Not DeleteItem.
        role.add_to_policy(iam.PolicyStatement(
            sid="LoadTheRightsTable",
            actions=["dynamodb:PutItem", "dynamodb:DescribeTable"],
            resources=[f"arn:aws:dynamodb:{REGION}:{self.account}:table/agentkeel-*-rights"],
        ))  # fmt: skip
        # The load check: `src.agent.run` calls the runtime it just deployed,
        # once per golden. refagent's runtime, as the eval role's grant is.
        role.add_to_policy(iam.PolicyStatement(
            sid="CallTheRuntimeItJustDeployed",
            actions=["bedrock-agentcore:InvokeAgentRuntime"],
            resources=[f"arn:aws:bedrock-agentcore:{REGION}:{self.account}:runtime/refagent*"],
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
        # ADR-0007, P1 (Option B): which bytes the deployed runtime runs, so a
        # pull request's run measures in the runtime only when they are the
        # tree's (`scripts/runtime_for_tree.py`). Three reads, each on refagent
        # alone: the stack's RuntimeArn output, the image digest the runtime
        # pins, and that image's tags. Nothing here can change what it reads.
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadWhichBytesTheRuntimeRuns",
            actions=["cloudformation:DescribeStacks"],
            resources=[f"arn:aws:cloudformation:{REGION}:{self.account}:stack/agentkeel-refagent/*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheRuntimesImage",
            actions=["bedrock-agentcore:GetAgentRuntime"],
            resources=[f"arn:aws:bedrock-agentcore:{REGION}:{self.account}:runtime/refagent*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheImagesTags",
            actions=["ecr:DescribeImages"],
            resources=[f"arn:aws:ecr:{REGION}:{self.account}:repository/agentkeel-refagent"],
        ))  # fmt: skip
        # Ruling i: the human makes S4's and S6's attempts, and this role asks
        # CloudTrail whether AWS refused each request id
        # (`scripts/observe_attempt.py`). Without this the instrument cannot
        # do its job: `LookupEvents` was an implicit deny, the lookup returned
        # "0 of 3 attempts recorded as AccessDenied" for attempts CloudTrail
        # had, and F1_1 and F1_3 failed for want of a permission rather than
        # for want of a refusal (M01 PR 2, run 35539363797).
        #
        # Read only, and that is the whole point: this role may ask what
        # happened and may not change the answer. `DENY` below already refuses
        # `logs:Delete*`, and nothing here grants `cloudtrail:Delete*`,
        # `PutEventSelectors` or `StopLogging`. `LookupEvents` takes no
        # resource-level condition, so the resource is `*` (P5: the instrument
        # reads AWS's record, it does not write it).
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadCloudTrailForTheSeedAttempts",
            actions=["cloudtrail:LookupEvents"], resources=["*"],
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="DenyEscalationAndEvidenceDeletion", effect=iam.Effect.DENY,
            actions=DENY, resources=["*"],
        ))  # fmt: skip
        cdk.CfnOutput(self, "EvalRoleArn", value=role.role_arn)
        return role

    # --- the key -----------------------------------------------------------

    def _agent_key(self, eval_role: iam.Role) -> kms.Key:
        """refagent's key. No platform role may administer it, and the agent cannot read its policy.

        Two separate things, and only one of them has a seeded case:

        - **S6, F1.3**: an agent role is denied `kms:GetKeyPolicy` by this
          policy, matched by role path (ruling b). The agent boundary allows
          the action (ruling t) so that this deny is what refuses it.
        - **R4, first half**: no role the platform creates may alter, grant
          on, disable or delete the key. SPEC/01 §9 lists that as a control
          with no seeded case, and it stays there.

        The human with admin can still administer the key. That is not an
        oversight: stopping them takes a service control policy, which
        SPEC/01 §1 puts in the landing zone, and a key policy that tried to
        stop them cannot be created at all (see the deny below).
        """
        key = kms.Key(
            self, "RefagentKey",
            alias="alias/agentkeel-refagent",
            enable_key_rotation=True,
            description="agentkeel: refagent key. No role the platform creates may administer it (R4).",
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
            # R4, first half: no role this platform creates may alter, grant on,
            # disable or delete this key. Named principals, not "everyone except".
            #
            # It was `ArnNotLike` on `agentkeel-security` and the account root,
            # and that was wrong twice. `agentkeel-security` is a role nothing
            # creates, so the policy read as "only root may administer this key"
            # while appearing to name a seat (`security-reviewer` F6,
            # `platform-architect` finding 9). And an IAM admin is neither root
            # nor that role, so the deny covered the human deploying the stack:
            # KMS refused to create the key at all, because a key policy that
            # locks its creator out of `kms:PutKeyPolicy` fails the lockout
            # safety check ("The new key policy will not allow you to update the
            # key policy in the future", 2026-09-20).
            #
            # Naming the principals says the same thing about the platform and
            # says it truthfully: the admin who deploys this stack can still
            # administer the key, which SPEC/01 §1 already concedes is
            # landing-zone work, and no role the platform runs as can.
            sid="NoPlatformRoleChangesThisKey",
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            actions=["kms:PutKeyPolicy", "kms:CreateGrant", "kms:ScheduleKeyDeletion", "kms:DisableKey"],
            resources=["*"],
            conditions={"ArnLike": {"aws:PrincipalArn": [
                agent_roles,
                f"arn:aws:iam::{self.account}:role/agentkeel-deploy",
                f"arn:aws:iam::{self.account}:role/agentkeel-cfn-exec",
                f"arn:aws:iam::{self.account}:role/{EVAL_ROLE_NAME}",
                f"arn:aws:iam::{self.account}:role/agentkeel-developer",
            ]}},
        ))  # fmt: skip
        key.grant_decrypt(eval_role)
        return key

    # --- spend -------------------------------------------------------------

    def _budget(self, eval_role: iam.Role) -> budgets.CfnBudget:
        """Bedrock spend for the account: a daily alert, and a monthly stop (ruling a, amended).

        Ruling a asked for one daily budget whose action attaches a Deny on
        `bedrock:Invoke*` to the eval role. **AWS will not build that.** A
        Budgets Action cannot hang off a daily budget:

            AWS Budgets Actions don't support daily granularity budget for
            now. (Service: Budgets, Status Code: 400)

        So the two halves are separated, and only one of them is a control:

        - **daily, `daily_usd`**: a notification to the human. No action.
          This is the figure the Threshold Owner ruled, and at M01 it tells
          somebody; it stops nothing.
        - **monthly, `MONTHLY_USD`**: the Deny action, at 100% of the
          budget. This is the only mechanical stop, and a month is a coarse
          bound: a run that spent the whole month's figure in an afternoon
          is stopped after it, not during it.

        Two lags, and neither is invented here. Budgets data refreshes up
        to three times a day, so the worst case the monthly stop bounds is
        one refresh interval of Bedrock spend at the account quota, on top
        of the month's own granularity.

        What the number should be is the Threshold Owner's, and the first
        measurement now exists: refagent plus the control is 54,250 tokens
        a run (run 35532168520), which on Sonnet 4.6's published rates is
        about USD 0.23. 30 x the daily figure is three hundred runs' worth
        of headroom and is almost certainly far looser than this milestone
        needs. It is the literal translation of what was ruled, and it is
        flagged rather than quietly narrowed.
        """
        deny_invoke = iam.ManagedPolicy(
            self, "BudgetStop",
            managed_policy_name="agentkeel-budget-stop",
            description="Attached by the Budgets action when Bedrock spend passes the monthly figure.",
            document=iam.PolicyDocument(statements=[iam.PolicyStatement(
                sid="NoMoreBedrockThisMonth", effect=iam.Effect.DENY,
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

        # CloudFormation requires at least one subscriber. The address is not
        # in the repo: the human passes it at deploy (README.md).
        subscriber = cdk.CfnParameter(
            self, "BudgetSubscriberEmail",
            description="Who Budgets notifies when Bedrock spend passes the daily or monthly figure.",
            allowed_pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        )
        bedrock_only = {"Service": ["Amazon Bedrock"]}

        # The daily figure, as ruled. It notifies and it does not stop.
        budgets.CfnBudget(
            self, "BedrockDaily",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="agentkeel-bedrock-daily",
                budget_type="COST", time_unit="DAILY",
                budget_limit=budgets.CfnBudget.SpendProperty(amount=DAILY_USD, unit="USD"),
                cost_filters=bedrock_only,
            ),
            notifications_with_subscribers=[budgets.CfnBudget.NotificationWithSubscribersProperty(
                notification=budgets.CfnBudget.NotificationProperty(
                    comparison_operator="GREATER_THAN", notification_type="ACTUAL",
                    threshold=100, threshold_type="PERCENTAGE"),
                subscribers=[budgets.CfnBudget.SubscriberProperty(
                    address=subscriber.value_as_string, subscription_type="EMAIL")],
            )],
        )  # fmt: skip

        # The monthly figure, which is the only one an action may hang off.
        monthly = budgets.CfnBudget(
            self, "BedrockMonthly",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="agentkeel-bedrock-monthly",
                budget_type="COST", time_unit="MONTHLY",
                budget_limit=budgets.CfnBudget.SpendProperty(amount=MONTHLY_USD, unit="USD"),
                cost_filters=bedrock_only,
            ),
        )  # fmt: skip
        budgets.CfnBudgetsAction(
            self, "BedrockMonthlyStop",
            action_threshold=budgets.CfnBudgetsAction.ActionThresholdProperty(type="PERCENTAGE", value=100),
            action_type="APPLY_IAM_POLICY",
            approval_model="AUTOMATIC",
            budget_name=monthly.budget.budget_name,
            definition=budgets.CfnBudgetsAction.DefinitionProperty(
                iam_action_definition=budgets.CfnBudgetsAction.IamActionDefinitionProperty(
                    policy_arn=deny_invoke.managed_policy_arn, roles=[eval_role.role_name])),
            execution_role_arn=action_role.role_arn,
            notification_type="ACTUAL",
            subscribers=[budgets.CfnBudgetsAction.SubscriberProperty(
                address=subscriber.value_as_string, type="EMAIL")],
        )  # fmt: skip
        monthly.node.add_dependency(deny_invoke)
        return monthly


    def _image_repository(self) -> ecr.Repository:
        """Where the runtime image is pulled from. Tag-immutable: a digest is the bytes (SPEC/01 Â§6)."""
        return ecr.Repository(
            self, "RefagentImage",
            repository_name="agentkeel-refagent",
            image_tag_mutability=ecr.TagMutability.IMMUTABLE,
            image_scan_on_push=True,
            encryption=ecr.RepositoryEncryption.AES_256,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip

    def _parameters(self, boundary: iam.ManagedPolicy, vpc: ec2.Vpc) -> None:
        """The Security-owned parameters `GovernedAgent` reads (SPEC/01 Â§6).

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
                self, f"ParamEndpoint{endpoint_id(name)}",
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
        f"exceed this. BLOCK F's grants are what GovernedAgent renders, one statement per resource type: "
        f"managing security-group/* is conditioned on ec2:Vpc being this stack's VPC, and creating one is held "
        f"by the VPC resource, because a new group has no ec2:Vpc yet; a new network-interface/* likewise, "
        f"held by its subnet and group; CreateAgentRuntime takes no resource-level permission and is held to "
        f"this stack's subnets by bedrock-agentcore:subnets; runtime/*, application-inference-profile/* and "
        f"the agent role path name resources whose ids AWS assigns at create; ec2:Describe* takes no "
        f"resource-level permission; security-group-rule/* is the egress rule's own resource; the five "
        f"vpc-lattice actions are the Runtime create handler's VPC-mode calls, which name no resource "
        f"in advance. The action lists are CloudFormation's published handler permissions (describe-type). "
        f"{CEILING}"
    ),
    "DeployRole/DefaultPolicy/Resource": (
        "SPEC/01 §6: 'the deploy role, trusted with StringEquals on aud, the immutable sub for "
        "refs/heads/main, and job_workflow_ref'. Seed S4 is an attempt to do from a laptop what only this "
        "role may do. cloudformation:* is scoped to stack/agentkeel-*, the set of stacks this platform "
        "deploys; AWS appends the stack id suffix, which cannot be named in advance. BLOCK F: "
        "ecr:GetAuthorizationToken takes no resource; the push is on repository/agentkeel-*, the table load "
        "on table/agentkeel-*-rights, and the load check's InvokeAgentRuntime on runtime/refagent*, the "
        "versioned name AgentCore assigns at create."
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
        "which does not exist until the deploy. The five-action Deny is the ceiling. Seeds S4 and S6: "
        "cloudtrail:LookupEvents is on * because CloudTrail takes no resource-level condition for it, "
        "and ruling i has this role ask CloudTrail whether the human's attempts were refused. It is the "
        "only cloudtrail action granted, so the instrument may read the record and may not change it. "
        "ADR-0007 (P1): stack/agentkeel-refagent/* is the stack id suffix AWS appends, and runtime/refagent* "
        "the versioned name; DescribeStacks, GetAgentRuntime and ecr:DescribeImages are reads on refagent alone. "
        f"{CEILING}"
    ),
}
for path, reason in SUPPRESSIONS.items():
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelBootstrap/{path}", [{"id": "AwsSolutions-IAM5", "reason": reason}])
# Not an IAM wildcard: cdk-nag cannot resolve these rules at all. They are
# CDK's own endpoint security groups, and their source is the VPC's CIDR,
# an intrinsic function at synth.
for name in (f"Endpoint{endpoint_id(n)}" for n in INTERFACE_ENDPOINTS):
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelBootstrap/Vpc/{name}/SecurityGroup/Resource",
        [{"id": "CdkNagValidationFailure",
          "reason": "SPEC/01 §6: 'a VPC with no internet gateway, endpoints with policies scoped to "
                    "the account'. AwsSolutions-EC23 cannot resolve this rule: the source is the VPC's own "
                    "CIDR, an intrinsic function at synth. The rule allows 443 from inside this VPC and "
                    "nothing else, and the VPC has no way out."}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
