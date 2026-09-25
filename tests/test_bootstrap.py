"""The bootstrap stack's two boundaries, read from the rendered template (ruling s, ruling t).

BLOCK B: one allow-list boundary was applied to every role in the stack, so
the CloudFormation execution role could create nothing and the Budgets stop
could not attach. The split is what these tests hold:

- the **agent plane's** `agentkeel-boundary` is an allow-list, attached to
  roles under `/agentkeel/agents/` — of which this stack makes none — and it
  allows `kms:GetKeyPolicy`, so the key policy is what refuses S6;
- the **deploy plane's** `agentkeel-deploy-boundary` is a deny-list, on every
  role this stack makes, and it denies neither `iam:*` nor `sts:AssumeRole`,
  because denying either would be the wrong control firing.

Synthesised here rather than read from `cdk.out`, for the same reason as
`tests/test_construct.py`: that folder is gitignored and written by
`make validate`, so reading it would let these pass on an older template.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "infra" / "bootstrap" / "app.py"
AGENT_PATH = "/agentkeel/agents/"


@pytest.fixture(scope="module")
def template(tmp_path_factory) -> dict[str, Any]:
    out = tmp_path_factory.mktemp("bootstrap")
    done = subprocess.run(
        [sys.executable, str(APP)], cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)},
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / "AgentkeelBootstrap.template.json").read_text(encoding="utf-8"))


def of_type(template: dict[str, Any], kind: str) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in template["Resources"].items() if v["Type"] == kind}


def named(template: dict[str, Any], policy_name: str) -> dict[str, Any]:
    """The managed policy with this name, and the logical id CDK gave it."""
    for logical, resource in of_type(template, "AWS::IAM::ManagedPolicy").items():
        if resource["Properties"].get("ManagedPolicyName") == policy_name:
            return {"logical": logical, **resource["Properties"]}
    raise AssertionError(f"no managed policy named {policy_name}")


def actions(statement: dict[str, Any]) -> set[str]:
    action = statement.get("Action", [])
    return set(action if isinstance(action, list) else [action])


def statements(policy: dict[str, Any], effect: str) -> list[dict[str, Any]]:
    return [s for s in policy["PolicyDocument"]["Statement"] if s["Effect"] == effect]


def denied(policy: dict[str, Any]) -> set[str]:
    return {a for s in statements(policy, "Deny") for a in actions(s)}


def allowed(policy: dict[str, Any]) -> set[str]:
    return {a for s in statements(policy, "Allow") for a in actions(s)}


# --- every role carries one, and it is the right one -----------------------


def test_every_role_this_stack_makes_carries_the_deploy_boundary(template):
    """Including the two CDK makes for us: the flow-log role and the Budgets action role."""
    roles = of_type(template, "AWS::IAM::Role")
    deploy_boundary = {"Ref": named(template, "agentkeel-deploy-boundary")["logical"]}
    assert len(roles) >= 6
    for logical, role in roles.items():
        boundary = role["Properties"].get("PermissionsBoundary")
        assert boundary, f"{logical} carries no permissions boundary"
        assert boundary == deploy_boundary, f"{logical} carries the agent allow-list, which caps it to nothing"


def test_this_stack_makes_no_role_on_the_agent_path(template):
    """The agent plane's roles are the construct's. If one appeared here it would need the other boundary."""
    paths = {role["Properties"].get("Path") for role in of_type(template, "AWS::IAM::Role").values()}
    assert not any((path or "/").startswith(AGENT_PATH) for path in paths)


def test_a_role_the_deploy_creates_is_capped_by_the_agent_boundary(template):
    """The execution role may create a role only with the AGENT boundary on it (SPEC/01 §6)."""
    agent_boundary = {"Ref": named(template, "agentkeel-boundary")["logical"]}
    conditions = [
        statement["Condition"]
        for logical, policy in of_type(template, "AWS::IAM::Policy").items()
        if "Execution" in logical
        for statement in policy["Properties"]["PolicyDocument"]["Statement"]
        if statement.get("Condition")
    ]
    assert {"StringEquals": {"iam:PermissionsBoundary": agent_boundary}} in conditions


# --- the agent plane's allow-list ------------------------------------------


def test_the_agent_boundary_allows_the_action_seed_s6_attempts(template):
    """Ruling t: an allow-list caps by omission, so leaving it out would refuse S6 here, not at the key."""
    agent = named(template, "agentkeel-boundary")
    assert "kms:GetKeyPolicy" in allowed(agent)
    assert "kms:GetKeyPolicy" not in denied(agent)
    # It is a ceiling, not a grant: the key policy still denies it by role path.
    key = next(iter(of_type(template, "AWS::KMS::Key").values()))
    key_denies = [s for s in key["Properties"]["KeyPolicy"]["Statement"] if s["Effect"] == "Deny"]
    assert any("kms:GetKeyPolicy" in actions(s) for s in key_denies)


def test_the_agent_boundary_is_still_an_allow_list(template):
    """If it ever became Allow *, S5 would stop meaning anything."""
    agent = named(template, "agentkeel-boundary")
    assert allowed(agent) and "*" not in allowed(agent)


# --- the deploy plane's deny-list ------------------------------------------


def test_the_deploy_boundary_lets_a_deployer_deploy(template):
    deploy = named(template, "agentkeel-deploy-boundary")
    assert allowed(deploy) == {"*"}


@pytest.mark.parametrize("action, why", [
    ("iam:*", "it would cap iam:CreateRole on the execution role and iam:PassRole on the deploy role"),
    ("sts:AssumeRole", "the developer role holds it so that seed S4 is refused by the deploy role's trust policy"),
])  # fmt: skip
def test_the_deploy_boundary_does_not_deny_what_would_be_the_wrong_control(template, action, why):
    assert action not in denied(named(template, "agentkeel-deploy-boundary")), why


def test_the_deploy_boundary_holds_r4_and_the_escalation_primitives(template):
    deploy = denied(named(template, "agentkeel-deploy-boundary"))
    # R4: no deploy-plane role may alter, grant on, disable or delete a key.
    assert {"kms:PutKeyPolicy", "kms:CreateGrant", "kms:ScheduleKeyDeletion", "kms:DisableKey"} <= deploy
    # Escalation, by name rather than by iam:*.
    assert {"iam:CreateUser", "iam:PutUserPolicy", "iam:AttachUserPolicy", "iam:CreateAccessKey",
            "iam:PutRolePermissionsBoundary", "iam:DeleteRolePermissionsBoundary",
            "iam:CreatePolicyVersion", "iam:SetDefaultPolicyVersion"} <= deploy  # fmt: skip
    # Evidence, and the network the VPC has no way out of.
    assert {"logs:Delete*", "s3:PutBucketPolicy", "ec2:CreateInternetGateway", "ec2:CreateNatGateway"} <= deploy


# --- the eval role ---------------------------------------------------------


def eval_role_policy(template: dict[str, Any]) -> list[dict[str, Any]]:
    for logical, policy in of_type(template, "AWS::IAM::Policy").items():
        if "EvalRole" in logical:
            return policy["Properties"]["PolicyDocument"]["Statement"]
    raise AssertionError("no policy on the eval role")


def test_the_eval_role_may_ask_cloudtrail_what_happened(template):
    """Ruling i. `observe_attempt.py` runs as this role; without the permission
    it records "not found" for attempts CloudTrail has, and F1_1 and F1_3 fail
    for want of a permission rather than for want of a refusal."""
    allowed_here = {a for s in eval_role_policy(template) if s["Effect"] == "Allow" for a in actions(s)}
    assert "cloudtrail:LookupEvents" in allowed_here


def test_the_eval_role_may_not_change_what_cloudtrail_says(template):
    """Read is the whole grant. An instrument that could edit the record it reads
    would not be evidence of anything (P5)."""
    allowed_here = {a for s in eval_role_policy(template) if s["Effect"] == "Allow" for a in actions(s)}
    for action in allowed_here:
        assert not action.startswith("cloudtrail:") or action == "cloudtrail:LookupEvents", (
            f"{action} lets the instrument write the record it reads"
        )


def test_the_eval_role_may_read_which_bytes_the_runtime_runs_and_nothing_more(template):
    """ADR-0007, P1: three reads, on refagent alone, and no write among them."""
    reads = {"cloudformation:DescribeStacks": "stack/agentkeel-refagent/*",
             "bedrock-agentcore:GetAgentRuntime": "runtime/refagent*",
             "ecr:DescribeImages": "repository/agentkeel-refagent"}  # fmt: skip
    statements_ = eval_role_policy(template)
    for action, resource in reads.items():
        granting = [s for s in statements_ if s["Effect"] == "Allow" and action in actions(s)]
        assert len(granting) == 1, action
        assert json.dumps(granting[0]["Resource"]).endswith(f':{resource}"]]}}'), action
    allowed_here = {a for s in statements_ if s["Effect"] == "Allow" for a in actions(s)}
    assert not {a for a in allowed_here if a.startswith(("cloudformation:", "ecr:"))} - set(reads)
    assert not {a for a in allowed_here if a.startswith("bedrock-agentcore:")} - {
        "bedrock-agentcore:GetAgentRuntime", "bedrock-agentcore:InvokeAgentRuntime"}


# --- the key policy --------------------------------------------------------


def key_policy(template: dict[str, Any]) -> list[dict[str, Any]]:
    key = next(iter(of_type(template, "AWS::KMS::Key").values()))
    return key["Properties"]["KeyPolicy"]["Statement"]


def test_the_key_policy_can_be_created_at_all(template):
    """KMS refuses a key whose policy locks its creator out of kms:PutKeyPolicy.

    The first version denied the four admin actions with `ArnNotLike` on a
    Security role that nothing creates, plus the account root. An IAM admin
    is neither, so the deny covered the human running the deploy and the
    key could not be created: "The new key policy will not allow you to
    update the key policy in the future" (2026-09-20).

    The rule that keeps it creatable: the deny names the principals it
    refuses, rather than excepting the ones it allows.
    """
    admin = [s for s in key_policy(template)
             if s["Effect"] == "Deny" and "kms:PutKeyPolicy" in actions(s)]  # fmt: skip
    assert len(admin) == 1
    assert "ArnNotLike" not in admin[0].get("Condition", {}), (
        "an ArnNotLike deny on kms:PutKeyPolicy covers every principal the list does not name, "
        "including whoever deploys the stack, and KMS will refuse to create the key"
    )
    assert "ArnLike" in admin[0]["Condition"]


def test_no_role_the_platform_creates_may_administer_the_key(template):
    """R4, first half, and it is named principal by principal."""
    admin = next(s for s in key_policy(template)
                 if s["Effect"] == "Deny" and "kms:PutKeyPolicy" in actions(s))  # fmt: skip
    assert actions(admin) == {"kms:PutKeyPolicy", "kms:CreateGrant",
                              "kms:ScheduleKeyDeletion", "kms:DisableKey"}  # fmt: skip
    covered = json.dumps(admin["Condition"]["ArnLike"]["aws:PrincipalArn"])
    for role in ("agentkeel/agents/*", "agentkeel-deploy", "agentkeel-cfn-exec",
                 "agentkeel-evals", "agentkeel-developer"):  # fmt: skip
        assert role in covered, f"{role} may administer the key"


def test_an_agent_role_is_denied_its_own_key_policy(template):
    """Seed S6. The agent boundary allows the action (ruling t) so this is what refuses it."""
    reads = [s for s in key_policy(template)
             if s["Effect"] == "Deny" and "kms:GetKeyPolicy" in actions(s)]  # fmt: skip
    assert len(reads) == 1
    assert "agentkeel/agents/*" in json.dumps(reads[0]["Condition"]["ArnLike"]["aws:PrincipalArn"])


# --- the budgets -----------------------------------------------------------


def test_the_stop_hangs_off_the_monthly_budget_because_aws_allows_no_other(template):
    """Ruling a asked for the action on the daily budget. AWS refuses to build that:

    "AWS Budgets Actions don't support daily granularity budget for now"
    (Budgets, 400, 2026-09-20). So the daily figure notifies and the monthly
    figure stops, and the two are not the same figure.
    """
    budgets = {b["Properties"]["Budget"]["BudgetName"]: b["Properties"]["Budget"]
               for b in of_type(template, "AWS::Budgets::Budget").values()}  # fmt: skip
    assert budgets["agentkeel-bedrock-daily"]["TimeUnit"] == "DAILY"
    assert budgets["agentkeel-bedrock-monthly"]["TimeUnit"] == "MONTHLY"

    actions_on = [a["Properties"]["BudgetName"] for a in of_type(template, "AWS::Budgets::BudgetsAction").values()]
    assert actions_on == ["agentkeel-bedrock-monthly"], "a Budgets Action on a daily budget will not deploy"


def test_the_daily_budget_still_tells_somebody(template):
    """It stops nothing, so if it did not notify it would do nothing at all."""
    daily = next(b["Properties"] for b in of_type(template, "AWS::Budgets::Budget").values()
                 if b["Properties"]["Budget"]["BudgetName"] == "agentkeel-bedrock-daily")  # fmt: skip
    subscribers = daily["NotificationsWithSubscribers"]
    assert len(subscribers) == 1
    assert subscribers[0]["Subscribers"][0]["SubscriptionType"] == "EMAIL"


def test_both_budgets_count_bedrock_and_nothing_else(template):
    for budget in of_type(template, "AWS::Budgets::Budget").values():
        assert budget["Properties"]["Budget"]["CostFilters"] == {"Service": ["Amazon Bedrock"]}
        assert budget["Properties"]["Budget"]["BudgetType"] == "COST"


# --- BLOCK F: what the execution role may make (M01 PR 3) -------------------
#
# Until PR 3 its whole grant was iam:CreateRole, PutRolePolicy and
# AttachRolePolicy under the agent path. The construct makes a security
# group, a table, a profile and a runtime, so the first deploy would have
# failed on its first non-IAM resource. These tests hold the grant to the
# construct's own template in both directions: every type it renders is
# covered, and nothing is granted that no type needs.

CONSTRUCT_APP = ROOT / "infra" / "construct" / "app.py"

# What CloudFormation calls to create, read and delete each resource type
# refagent's stack renders: the handler permissions AWS publishes, from
# `aws cloudformation describe-type --type RESOURCE --type-name <T>`, read
# 2026-09-21, less the calls only a feature the template does not use makes
# (Kinesis streaming, table import, replicas, a customer key, S3 code
# artifacts, capacity providers). The key set must equal the template's types.
NEEDED_BY_TYPE = {
    "AWS::EC2::SecurityGroup": {"ec2:CreateSecurityGroup", "ec2:DescribeSecurityGroups", "ec2:RevokeSecurityGroupEgress",
                                "ec2:AuthorizeSecurityGroupEgress", "ec2:CreateTags", "ec2:DeleteSecurityGroup",
                                "ec2:DescribeInstances"},
    "AWS::EC2::SecurityGroupEgress": {"ec2:AuthorizeSecurityGroupEgress", "ec2:RevokeSecurityGroupEgress",
                                      "ec2:DescribeSecurityGroupRules"},
    "AWS::DynamoDB::Table": {"dynamodb:CreateTable", "dynamodb:DescribeTable", "dynamodb:DescribeTimeToLive",
                             "dynamodb:UpdateContinuousBackups", "dynamodb:DescribeContinuousBackups",
                             "dynamodb:DescribeContributorInsights", "dynamodb:DescribeKinesisStreamingDestination",
                             "dynamodb:ListTagsOfResource", "dynamodb:GetResourcePolicy"},
    "AWS::IAM::Role": {"iam:CreateRole", "iam:PutRolePolicy", "iam:GetRolePolicy", "iam:TagRole", "iam:UntagRole",
                       "iam:GetRole", "iam:ListAttachedRolePolicies", "iam:ListRolePolicies", "iam:DeleteRole",
                       "iam:DetachRolePolicy", "iam:DeleteRolePolicy"},
    "AWS::IAM::Policy": {"iam:GetRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy"},
    "AWS::Bedrock::ApplicationInferenceProfile": {"bedrock:CreateInferenceProfile", "bedrock:GetInferenceProfile",
                                                  "bedrock:TagResource", "bedrock:ListTagsForResource",
                                                  "bedrock:DeleteInferenceProfile"},
    "AWS::BedrockAgentCore::Runtime": {"bedrock-agentcore:CreateAgentRuntime", "bedrock-agentcore:CreateAgentRuntimeEndpoint",
                                       "bedrock-agentcore:GetAgentRuntime", "bedrock-agentcore:GetAgentRuntimeEndpoint",
                                       "bedrock-agentcore:CreateWorkloadIdentity", "bedrock-agentcore:TagResource",
                                       "bedrock-agentcore:ListTagsForResource", "iam:CreateServiceLinkedRole",
                                       "iam:PassRole", "vpc-lattice:GetResourceConfiguration",
                                       "vpc-lattice:CreateServiceNetworkResourceAssociation",
                                       "vpc-lattice:GetServiceNetworkResourceAssociation",
                                       "vpc-lattice:ListServiceNetworkResourceAssociations",
                                       "vpc-lattice:AssociateViaAWSService", "ec2:DescribeVpcs", "ec2:DescribeSubnets",
                                       "ec2:DescribeSecurityGroups", "ec2:CreateNetworkInterface",
                                       "bedrock-agentcore:DeleteAgentRuntime", "bedrock-agentcore:DeleteAgentRuntimeEndpoint",
                                       "bedrock-agentcore:DeleteWorkloadIdentity"},
}  # fmt: skip


@pytest.fixture(scope="module")
def construct_template(tmp_path_factory) -> dict[str, Any]:
    out = tmp_path_factory.mktemp("construct")
    done = subprocess.run(
        [sys.executable, str(CONSTRUCT_APP)], cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)},
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / "AgentkeelRefagent.template.json").read_text(encoding="utf-8"))


def role_statements(template: dict[str, Any], role_logical_prefix: str) -> list[dict[str, Any]]:
    for logical, policy in of_type(template, "AWS::IAM::Policy").items():
        if logical.startswith(role_logical_prefix):
            return policy["Properties"]["PolicyDocument"]["Statement"]
    raise AssertionError(f"no policy on {role_logical_prefix}")


def allowed_actions(statements_: list[dict[str, Any]]) -> set[str]:
    return {a for s in statements_ if s["Effect"] == "Allow" for a in actions(s)}


def test_every_resource_type_the_construct_renders_is_one_the_grant_knows(construct_template):
    """A new resource in GovernedAgent must come with its grant, or this fails before the deploy does."""
    rendered = {r["Type"] for r in construct_template["Resources"].values()}
    assert rendered == set(NEEDED_BY_TYPE), (
        f"the construct renders {sorted(rendered - set(NEEDED_BY_TYPE))} with no grant on agentkeel-cfn-exec, "
        f"or the grant covers {sorted(set(NEEDED_BY_TYPE) - rendered)} that it no longer renders"
    )


@pytest.mark.parametrize("kind", sorted(NEEDED_BY_TYPE))
def test_the_execution_role_may_make_what_the_construct_renders(template, kind):
    granted = allowed_actions(role_statements(template, "ExecutionRole"))
    assert NEEDED_BY_TYPE[kind] <= granted, f"{kind}: missing {sorted(NEEDED_BY_TYPE[kind] - granted)}"


# --- what a handler calls only when a property asks for it -----------------
# NEEDED_BY_TYPE leaves out the calls "only a feature the template does not
# use makes". The first deploy (run 35683865472, 2026-09-22; M02 open.md
# row 9) showed the template used one: `TableEncryption.AWS_MANAGED` renders
# `SSESpecification: {SSEEnabled: true}` with no key id, which is the
# `aws/dynamodb` key, and the DynamoDB handler calls `kms:CreateGrant` on it.
# `agentkeel-deploy-boundary` denies that on every key (R4), so the table
# failed at CREATE, after the change set, and the stack rolled back. The
# refusal came from a deny that is meant to be there; what was wrong was a
# resource that needed it. This table names such calls per property, so the
# collision is read here, before a deploy, and never again at CREATE.
#
# Each row: resource type, a predicate on the rendered Properties, and the
# actions the handler then needs on top of NEEDED_BY_TYPE. From the same
# `describe-type` handler permissions as NEEDED_BY_TYPE.
NEEDED_BY_PROPERTY: list[tuple[str, Any, set[str]]] = [
    ("AWS::DynamoDB::Table",
     lambda p: p.get("SSESpecification", {}).get("SSEEnabled") is True,
     {"kms:CreateGrant", "kms:DescribeKey", "kms:ListAliases"}),
    ("AWS::DynamoDB::Table",
     lambda p: "KinesisStreamSpecification" in p,
     {"kinesis:DescribeStream", "kinesis:PutRecords", "dynamodb:EnableKinesisStreamingDestination"}),
    ("AWS::DynamoDB::Table",
     lambda p: "ImportSourceSpecification" in p,
     {"dynamodb:ImportTable", "dynamodb:DescribeImport", "s3:GetObject", "s3:ListBucket"}),
]  # fmt: skip


def handler_needs(resource: dict[str, Any]) -> set[str]:
    needs = set(NEEDED_BY_TYPE.get(resource["Type"], set()))
    properties = resource.get("Properties", {})
    for kind, when, extra in NEEDED_BY_PROPERTY:
        if resource["Type"] == kind and when(properties):
            needs |= extra
    return needs


def test_no_construct_resource_needs_an_action_the_deploy_boundary_denies(template, construct_template):
    """The deploy boundary is a deny-list on the execution role, and a deny wins over the grant.

    A resource whose handler needs a denied action is not refused at synth, at
    `cdk diff` or at the change set; it fails at CREATE, as the rights table
    did on 2026-09-22 (`kms:CreateGrant`, run 35683865472). That is R4 holding
    against our own template. This test reads the collision before a deploy
    does. It is not a grant check: `test_the_execution_role_may_make_what_the_construct_renders`
    is, and a granted action the boundary denies is still denied.
    """
    deny = denied(named(template, "agentkeel-deploy-boundary"))
    collisions: dict[str, list[str]] = {}
    for logical, resource in construct_template["Resources"].items():
        hit = sorted(a for a in handler_needs(resource) if any(fnmatch.fnmatch(a, d) for d in deny))
        if hit:
            collisions[logical] = hit
    assert not collisions, (
        f"the deploy boundary denies what these resources' handlers call, so CREATE fails after the change set: "
        f"{collisions}"
    )


def test_the_execution_role_may_resolve_the_security_parameters(template, construct_template):
    """Every SSM-typed parameter the construct reads is under the path the grant names (ten since B1)."""
    ssm_params = [p for p in construct_template["Parameters"].values() if p["Type"].startswith("AWS::SSM::")]
    assert ssm_params
    assert all(p["Default"].startswith("/agentkeel/security/") for p in ssm_params)
    reads = [s for s in role_statements(template, "ExecutionRole") if "ssm:GetParameters" in actions(s)]
    assert len(reads) == 1
    assert json.dumps(reads[0]["Resource"]).endswith(':parameter/agentkeel/security/*"]]}')


def test_the_execution_role_grants_no_service_wildcard_and_no_delete_of_the_table(template):
    granted = allowed_actions(role_statements(template, "ExecutionRole"))
    assert not any(a == "*" or a.endswith(":*") for a in granted), "a service wildcard is not what the construct makes"
    # The table is RETAIN: CloudFormation never calls DeleteTable, so it is not granted.
    assert "dynamodb:DeleteTable" not in granted
    assert not {"dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:BatchWriteItem"} & granted, (
        "the execution role makes the table; loading it is the deploy role's"
    )


def test_the_execution_role_makes_security_groups_in_the_platform_vpc_only(template):
    groups = [s for s in role_statements(template, "ExecutionRole")
              if "ec2:DeleteSecurityGroup" in actions(s)]  # fmt: skip
    assert len(groups) == 1
    assert "security-group/*" in json.dumps(groups[0]["Resource"])
    assert "Vpc" in json.dumps(groups[0]["Condition"]["ArnEquals"]["ec2:Vpc"])  # this stack's VPC, by Ref


def test_no_create_is_conditioned_on_a_key_the_new_resource_does_not_have_yet(template):
    """Read on the deployed role, not in the template: ec2:Vpc on the new security group and the
    new interface, and runtime/* for CreateAgentRuntime, each refused the create (M01 PR 3)."""
    for s in role_statements(template, "ExecutionRole"):
        if s["Effect"] != "Allow":
            continue
        resources = json.dumps(s["Resource"])
        if "ec2:CreateSecurityGroup" in actions(s):
            assert "Condition" not in s, "a new group has no ec2:Vpc: the VPC resource holds the create"
            assert "vpc/" in resources and "Ref" in resources  # this stack's VPC, and no other
        if "ec2:CreateNetworkInterface" in actions(s) and "network-interface/" in resources:
            assert "Condition" not in s, "a new interface has no ec2:Vpc: the subnet and group hold the create"
    runtime = [s for s in role_statements(template, "ExecutionRole") if "bedrock-agentcore:CreateAgentRuntime" in actions(s)]
    assert len(runtime) == 1
    assert runtime[0]["Resource"] == "*", "CreateAgentRuntime takes no resource-level permission"
    assert "bedrock-agentcore:subnets" in runtime[0]["Condition"]["ForAllValues:StringEquals"]
    assert runtime[0]["Condition"]["Null"] == {"bedrock-agentcore:subnets": "false"}


def test_the_execution_role_passes_an_agent_role_to_agentcore_only(template):
    passes = [s for s in role_statements(template, "ExecutionRole") if "iam:PassRole" in actions(s)]
    assert len(passes) == 1
    assert passes[0]["Condition"] == {"StringEquals": {"iam:PassedToService": "bedrock-agentcore.amazonaws.com"}}
    assert AGENT_PATH in json.dumps(passes[0]["Resource"])


def test_every_iam_write_on_the_execution_role_is_on_the_agent_path(template):
    """Nothing writes IAM outside /agentkeel/agents/, except the one service-linked
    role AgentCore's VPC mode needs, by service name; creating a role stays
    conditioned on the agent boundary."""
    for s in role_statements(template, "ExecutionRole"):
        if s["Effect"] != "Allow":
            continue
        writes = {a for a in actions(s) if a.startswith("iam:") and not a.startswith("iam:Get")}
        if not writes:
            continue
        if writes == {"iam:CreateServiceLinkedRole"}:
            assert s["Condition"]["StringEquals"]["iam:AWSServiceName"] == "network.bedrock-agentcore.amazonaws.com"
            continue
        assert AGENT_PATH in json.dumps(s["Resource"]), f"{s.get('Sid')}: {sorted(writes)} off the agent path"
        if writes & {"iam:CreateRole", "iam:PutRolePolicy", "iam:AttachRolePolicy"}:
            assert "iam:PermissionsBoundary" in s["Condition"]["StringEquals"], s.get("Sid")


# --- B1: the runtime can pull its image (M01 PR 3, ruling d amended) -------

ECR_PULL = {"ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:GetAuthorizationToken"}


def test_the_agent_boundary_allows_the_pull_and_no_ecr_write(template):
    """A ceiling wide enough to pull, and no wider: an agent never pushes or deletes an image."""
    agent = allowed(named(template, "agentkeel-boundary"))
    assert ECR_PULL <= agent
    assert {"logs:CreateLogGroup", "logs:DescribeLogStreams", "logs:DescribeLogGroups"} <= agent
    assert not {a for a in agent if a.startswith("ecr:")} - ECR_PULL
    # S6 still reads the same way: allowed by the ceiling, denied by the key policy.
    assert "kms:GetKeyPolicy" in agent


def endpoints(template: dict[str, Any]) -> list[dict[str, Any]]:
    return [r["Properties"] for r in of_type(template, "AWS::EC2::VPCEndpoint").values()]


def test_the_vpc_has_the_two_endpoints_an_image_pull_needs(template):
    names = json.dumps([e["ServiceName"] for e in endpoints(template)])
    assert "ecr.api" in names and "ecr.dkr" in names
    interface = [e for e in endpoints(template) if e.get("VpcEndpointType") == "Interface"]
    assert len(interface) == 5


def test_both_are_published_for_the_construct(template):
    published = {p["Properties"]["Name"] for p in of_type(template, "AWS::SSM::Parameter").values()}
    assert {"/agentkeel/security/endpoint/ecr.api", "/agentkeel/security/endpoint/ecr.dkr"} <= published


def test_the_s3_endpoint_reaches_outside_the_account_for_the_image_layers_only(template):
    """The one statement not scoped to this account: GetObject on ECR's own layer bucket."""
    gateways = [e for e in endpoints(template) if e.get("VpcEndpointType") == "Gateway"]
    s3 = next(e for e in gateways if json.dumps(e["ServiceName"]).endswith('.s3"]]}'))
    unscoped = [s for s in s3["PolicyDocument"]["Statement"] if "Condition" not in s]
    assert len(unscoped) == 1
    assert unscoped[0]["Action"] == "s3:GetObject"
    assert unscoped[0]["Resource"] == "arn:aws:s3:::prod-us-west-2-starport-layer-bucket/*"


# --- BLOCK F: what the deploy role may do (M01 PR 3) -----------------------

DEPLOY_YML = ROOT / ".github" / "workflows" / "deploy.yml"

# deploy.yml's steps, and what each calls as the deploy role.
DEPLOY_STEPS = {
    "amazon-ecr-login": {"ecr:GetAuthorizationToken"},
    "reuse an image already pushed under this tag": {"ecr:BatchGetImage"},
    "docker push": {"ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload", "ecr:PutImage"},
    "cloudformation deploy": {"cloudformation:CreateChangeSet", "cloudformation:ExecuteChangeSet",
                              "cloudformation:DescribeStacks", "iam:PassRole"},
    # The update path (M02, the second deploy, run 35734541276 rerun): the CDK
    # CLI reads the deployed template's summary before it makes the change
    # set, and deletes a change set that turns out empty. The first deploy
    # created the stack and never called either; the second updated it and
    # was refused on GetTemplateSummary.
    "cloudformation deploy, update path": {"cloudformation:GetTemplateSummary", "cloudformation:DeleteChangeSet"},
    "load_rights_table.py": {"dynamodb:PutItem", "dynamodb:DescribeTable"},
    "the load check": {"bedrock-agentcore:InvokeAgentRuntime", "cloudformation:DescribeStacks"},
}  # fmt: skip


def deploy_granted(template: dict[str, Any]) -> set[str]:
    granted = allowed_actions(role_statements(template, "DeployRole"))
    # cloudformation:Describe* is granted as a pattern.
    return granted | ({"cloudformation:DescribeStacks"} if "cloudformation:Describe*" in granted else set())


@pytest.mark.parametrize("step", sorted(DEPLOY_STEPS))
def test_the_deploy_role_may_do_what_each_step_of_deploy_yml_calls(template, step):
    missing = DEPLOY_STEPS[step] - deploy_granted(template)
    assert not missing, f"{step}: {sorted(missing)}"


def test_the_deploy_role_may_not_delete_or_batch_write(template):
    """No image delete, no table delete, no batch write. DeleteItem only on the rights tables (M03 PR 2)."""
    granted = deploy_granted(template)
    assert not any(a.startswith("ecr:Delete") or a == "ecr:BatchDeleteImage" for a in granted)
    assert not {"dynamodb:BatchWriteItem", "dynamodb:DeleteTable"} & granted
    assert not any(a == "*" or a.endswith(":*") for a in granted)
    deleting = [s for s in role_statements(template, "DeployRole") if "dynamodb:DeleteItem" in actions(s)]
    assert len(deleting) == 1 and json.dumps(deleting[0]["Resource"]).endswith(':table/agentkeel-*-rights"]]}')


def test_the_deploy_role_makes_the_table_the_file(template):
    """S1's reader (SPEC/03 §6): load_rights_table.py scans and deletes rows the file lacks, and sets the marker."""
    granted = deploy_granted(template)
    assert {"dynamodb:Scan", "dynamodb:DeleteItem", "dynamodb:PutItem", "ssm:PutParameter"} <= granted
    marker = [s for s in role_statements(template, "DeployRole") if "ssm:PutParameter" in actions(s)]
    assert len(marker) == 1 and actions(marker[0]) == {"ssm:PutParameter"}
    assert json.dumps(marker[0]["Resource"]).endswith(':parameter/agentkeel/marker/refagent/rights-table-digest"]]}')


# --- the guardrail deny, narrowed (M03 PR 2, SPEC/03 §6) ------------------------

# Every guardrail action the wildcard denied but Apply, by the names Bedrock has today.
GUARDRAIL_ADMIN = {"bedrock:CreateGuardrail", "bedrock:UpdateGuardrail", "bedrock:DeleteGuardrail",
                   "bedrock:CreateGuardrailVersion", "bedrock:GetGuardrail", "bedrock:ListGuardrails"}


def denies_by_pattern(denied_actions: set[str], action: str) -> bool:
    """IAM's own matching: `*` in an action name matches any run of characters."""
    import fnmatch

    return any(fnmatch.fnmatchcase(action, pattern) for pattern in denied_actions)


@pytest.mark.parametrize("where", ["agentkeel-boundary", "agentkeel-deploy-boundary", "the eval role"])
def test_apply_guardrail_is_no_longer_denied_and_the_admin_actions_still_are(template, where):
    """security-reviewer F1 at M03 PR 1: the guardrail cannot be on the call under `bedrock:*Guardrail*`."""
    if where == "the eval role":
        denied_here = {a for s in eval_role_policy(template) if s["Effect"] == "Deny" for a in actions(s)}
    else:
        denied_here = denied(named(template, where))
    assert not denies_by_pattern(denied_here, "bedrock:ApplyGuardrail"), where
    assert all(denies_by_pattern(denied_here, a) for a in GUARDRAIL_ADMIN), where
    assert "bedrock:*Guardrail*" not in denied_here, where


def test_the_developer_role_may_not_list_guardrails(template):
    """security-reviewer on e2839f2, FINDING 2: its `bedrock:List*` reached ListGuardrails once the wildcard went."""
    developer = {a for s in role_statements(template, "DeveloperRole") if s["Effect"] == "Allow" for a in actions(s)}
    assert "bedrock:List*" in developer, "the grant the boundary has to cap"
    assert denies_by_pattern(denied(named(template, "agentkeel-deploy-boundary")), "bedrock:ListGuardrails")


def test_a_later_admin_verb_on_a_guardrail_is_denied_without_being_listed(template):
    """FINDING 3: the verbs are patterns, so a Put or a new Create on a guardrail is denied as it lands."""
    for where in ("agentkeel-boundary", "agentkeel-deploy-boundary"):
        denied_here = denied(named(template, where))
        for action in ("bedrock:PutGuardrailPolicy", "bedrock:CreateGuardrailAlias", "bedrock:DeleteGuardrailVersion"):
            assert denies_by_pattern(denied_here, action), (where, action)


def test_the_agent_ceiling_allows_apply_guardrail_and_no_admin_action(template):
    ceiling = allowed(named(template, "agentkeel-boundary"))
    assert "bedrock:ApplyGuardrail" in ceiling
    assert not any(denies_by_pattern(ceiling, a) for a in GUARDRAIL_ADMIN)


def test_the_eval_role_reads_the_table_marker_and_writes_nothing_in_ssm(template):
    allowed_here = {a for s in eval_role_policy(template) if s["Effect"] == "Allow" for a in actions(s)}
    assert {a for a in allowed_here if a.startswith("ssm:")} == {"ssm:GetParameter"}


def test_no_agent_role_can_read_the_table_marker(template):
    """The agent must not answer from, or see, the marker that says which table it answers from."""
    assert not any(a.startswith("ssm:") for a in allowed(named(template, "agentkeel-boundary")))


def test_the_deploy_role_calls_refagents_runtime_and_no_other(template):
    invoke = [s for s in role_statements(template, "DeployRole")
              if "bedrock-agentcore:InvokeAgentRuntime" in actions(s)]  # fmt: skip
    assert len(invoke) == 1
    assert json.dumps(invoke[0]["Resource"]).endswith(':runtime/refagent*"]]}')


def stack_names(workflow: str) -> list[str]:
    """Every `--stack-name` a step runs. Comment lines are not commands."""
    commands = "\n".join(line for line in workflow.splitlines() if not line.lstrip().startswith("#"))
    return re.findall(r"--stack-name\s+(\S+)", commands)


def test_every_stack_deploy_yml_names_is_one_the_deploy_role_may_touch(template):
    """Item 7. `--stack-name AgentkeelBootstrap` against a grant on `stack/agentkeel-*/*`:
    IAM ARN matching is case-sensitive, so that call would have been refused mid-deploy."""
    grant = next(s for s in role_statements(template, "DeployRole") if "cloudformation:CreateStack" in actions(s))
    pattern = json.dumps(grant["Resource"]).split(":stack/")[1].split("/")[0]
    assert pattern == "agentkeel-*"
    names = stack_names(DEPLOY_YML.read_text(encoding="utf-8"))
    assert names, "deploy.yml names no stack"
    for name in names:
        assert fnmatch.fnmatchcase(name, pattern), f"deploy.yml names {name}, which stack/{pattern}/* does not match"


def test_every_action_the_construct_grants_the_agent_role_is_under_the_agent_boundary(template, construct_template):
    """The boundary is a ceiling: a grant it does not list is a grant that fails at the call, not at synth.

    The first deploy on which refagent's runtime answered (M02 PR 2's merge,
    run 35817173042) returned AccessDeniedException on dynamodb:Scan for all
    fifteen goldens: the construct grants Scan on the rights table and the
    boundary listed only GetItem and Query. Nothing compared the two.
    """
    ceiling = allowed(named(template, "agentkeel-boundary")) - denied(named(template, "agentkeel-boundary"))
    granted = allowed_actions(role_statements(construct_template, "RefagentRole"))
    over = sorted(a for a in granted if a not in ceiling and not any(
        c.endswith("*") and a.startswith(c[:-1]) for c in ceiling))
    assert not over, f"the construct grants the agent role actions the boundary does not allow: {over}"
    # the ceiling allows bedrock-agentcore:* and the wildcard test above would pass any action under it
    # (platform-architect on M02 PR 3, N2); the construct grants the agent role none, and this holds it
    assert not [a for a in granted if a.startswith("bedrock-agentcore:")], granted


# --- refagent's guardrail (M03 PR 2, SPEC/03 §6) ---------------------------------

RULES = ROOT / "agents" / "refagent" / "rules"


@pytest.fixture(scope="module")
def bootstrap_module(tmp_path_factory):
    """app.py as a module, for guardrail_spec. Importing it synthesises once, into a temporary folder."""
    import importlib.util

    os.environ.setdefault("CDK_OUTDIR", str(tmp_path_factory.mktemp("bootstrap-module")))
    spec = importlib.util.spec_from_file_location("bootstrap_app", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def the_one(template: dict[str, Any], kind: str) -> dict[str, Any]:
    found = list(of_type(template, kind).values())
    assert len(found) == 1, (kind, len(found))
    return found[0]["Properties"]


def test_the_guardrail_is_built_from_the_rule_files_and_nothing_else(template):
    """One guardrail from guardrail.yaml (rule-owner F6); the prompt-attack filter off, so no content policy."""
    import yaml

    rules = yaml.safe_load((RULES / "guardrail.yaml").read_text(encoding="utf-8"))
    built = the_one(template, "AWS::Bedrock::Guardrail")
    topics = built["TopicPolicyConfig"]["TopicsConfig"]
    assert [(t["Name"], t["Definition"], t["Examples"], t["Type"]) for t in topics] == [
        (t["name"], t["definition"], t["examples"], "DENY") for t in rules["denied_topics"]]
    assert built["SensitiveInformationPolicyConfig"]["PiiEntitiesConfig"] == [
        {"Type": e["entity"], "Action": e["action"]} for e in rules["pii"]]
    assert "ContentPolicyConfig" not in built and "WordPolicyConfig" not in built
    assert "AutomatedReasoningPolicyConfig" not in built  # security-reviewer NOTE 1 on e2839f2


def test_every_attack_names_a_rule_the_guardrail_builds(template):
    import yaml

    blocks = yaml.safe_load((RULES / "redteam.yaml").read_text(encoding="utf-8"))["blocks"]
    built = {t["Name"] for t in the_one(template, "AWS::Bedrock::Guardrail")["TopicPolicyConfig"]["TopicsConfig"]}
    assert set(blocks.values()) <= built


def test_the_version_is_a_number_that_moves_with_the_rules(template, bootstrap_module):
    """rule-owner F4: the manifest pins a version, never DRAFT; a rules change makes a new one."""
    version = the_one(template, "AWS::Bedrock::GuardrailVersion")
    assert version["Description"] == f"rules sha256 {bootstrap_module.guardrail_spec()['digest']}"
    outputs = template["Outputs"]
    assert {"GuardrailIdForTheManifest", "GuardrailVersionForTheManifest"} <= set(outputs)


def test_the_eval_role_applies_this_guardrail_and_no_other(template):
    applying = [s for s in eval_role_policy(template) if s["Effect"] == "Allow" and "bedrock:ApplyGuardrail" in actions(s)]
    assert len(applying) == 1 and actions(applying[0]) == {"bedrock:ApplyGuardrail"}
    arn = {"Fn::GetAtt": [next(iter(of_type(template, "AWS::Bedrock::Guardrail"))), "GuardrailArn"]}
    assert applying[0]["Resource"] == [arn, {"Fn::Join": ["", [arn, ":*"]]}]


def test_an_old_guardrail_version_is_kept_when_the_rules_change(template):
    """security-reviewer on 0bb1d4a, F1: the version the manifest pins must outlive its replacement."""
    (version,) = of_type(template, "AWS::Bedrock::GuardrailVersion").values()
    assert version.get("DeletionPolicy") == "Retain" and version.get("UpdateReplacePolicy") == "Retain"


@pytest.mark.parametrize(("change", "refused"), [
    (lambda g, r: r["blocks"].update({"g-016": "no-such-rule"}), "does not build"),
    (lambda g, r: g["denied_topics"][0].update({"definition": "x" * 201}), "outside Bedrock's limits"),
    (lambda g, r: g["denied_topics"][0].update({"examples": ["x" * 101]}), "outside Bedrock's limits"),
    (lambda g, r: g["denied_topics"].append(dict(g["denied_topics"][0])), "each once"),
    (lambda g, r: g.update({"content_filters": {"prompt_attack": "HIGH"}}), "prompt-attack filter is off"),
])  # fmt: skip
def test_rule_files_the_guardrail_cannot_be_built_from_are_refused_at_synth(tmp_path, bootstrap_module, change, refused):
    import yaml

    guardrail = yaml.safe_load((RULES / "guardrail.yaml").read_text(encoding="utf-8"))
    redteam = yaml.safe_load((RULES / "redteam.yaml").read_text(encoding="utf-8"))
    change(guardrail, redteam)
    (tmp_path / "guardrail.yaml").write_text(yaml.safe_dump(guardrail), encoding="utf-8")
    (tmp_path / "redteam.yaml").write_text(yaml.safe_dump(redteam), encoding="utf-8")
    with pytest.raises(ValueError, match=refused):
        bootstrap_module.guardrail_spec(tmp_path)


def test_the_topics_are_assessed_on_the_question_only_and_the_pii_on_both(template):
    """guardrail.yaml topics_apply_to: input (M03 PR 2, after make evals-local at 6d49b79 blocked every answer)."""
    for topic in the_one(template, "AWS::Bedrock::Guardrail")["TopicPolicyConfig"]["TopicsConfig"]:
        assert (topic["InputEnabled"], topic["InputAction"]) == (True, "BLOCK"), topic["Name"]
        assert (topic["OutputEnabled"], topic["OutputAction"]) == (False, "NONE"), topic["Name"]
    for entity in the_one(template, "AWS::Bedrock::Guardrail")["SensitiveInformationPolicyConfig"]["PiiEntitiesConfig"]:
        assert not {"InputEnabled", "OutputEnabled"} & set(entity), "the PII rule keeps Bedrock's default: both sides"


def test_where_the_topics_apply_must_be_said(tmp_path, bootstrap_module):
    import yaml

    guardrail = yaml.safe_load((RULES / "guardrail.yaml").read_text(encoding="utf-8"))
    del guardrail["topics_apply_to"]
    (tmp_path / "guardrail.yaml").write_text(yaml.safe_dump(guardrail), encoding="utf-8")
    shutil.copy(RULES / "redteam.yaml", tmp_path / "redteam.yaml")
    with pytest.raises(ValueError, match="topics_apply_to"):
        bootstrap_module.guardrail_spec(tmp_path)
