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

import json
import os
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
