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
