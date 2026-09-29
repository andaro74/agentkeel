"""infra/security/ and infra/audit/, synthesised and read (M05 PR 2; cold review F4, security-reviewer on PR 2).

Seeds S2, S3 and S6 are refused by what these stacks render, so what they render is held here, not only by
cdk-nag. Nothing here deploys or calls AWS.
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
AGENT, SECURITY = "581208540944", "897698239547"
BUCKET = f"agentkeel-audit-{SECURITY}"
REFAGENT = f"arn:aws:iam::{AGENT}:role/agentkeel/agents/agentkeel-refagent-RefagentRole5888DB41-i9IqTXU6NVSL"
STANDIN = f"arn:aws:iam::{AGENT}:role/agentkeel/agents/agentkeel-refagent-standin"


def synth(tmp_path_factory, folder: str, stack: str) -> dict[str, Any]:
    out = tmp_path_factory.mktemp(folder)
    done = subprocess.run([sys.executable, str(ROOT / "infra" / folder / "app.py")], cwd=ROOT, capture_output=True,
                          text=True, check=False, env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)})  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / f"{stack}.template.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def security(tmp_path_factory) -> dict[str, Any]:
    return synth(tmp_path_factory, "security", "AgentkeelSecurity")


@pytest.fixture(scope="module")
def audit(tmp_path_factory) -> dict[str, Any]:
    return synth(tmp_path_factory, "audit", "AgentkeelAudit")


def of_type(template: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [r["Properties"] for r in template["Resources"].values() if r["Type"] == kind]


def bucket_policy(security: dict[str, Any]) -> dict[str, dict[str, Any]]:
    (policy,) = of_type(security, "AWS::S3::BucketPolicy")
    return {s.get("Sid"): s for s in policy["PolicyDocument"]["Statement"]}


def test_the_audit_bucket_is_locked_in_compliance_for_one_day_and_versioned(security):
    (bucket,) = of_type(security, "AWS::S3::Bucket")
    assert bucket["BucketName"] == BUCKET and bucket["ObjectLockEnabled"] is True
    assert bucket["ObjectLockConfiguration"]["Rule"]["DefaultRetention"] == {"Mode": "COMPLIANCE", "Days": 1}
    assert bucket["VersioningConfiguration"]["Status"] == "Enabled"


def test_s2s_control_is_an_explicit_deny_naming_both_roles_by_their_whole_arn(security):
    """No pattern in a principal condition: it may read as public, and would admit a look-alike role."""
    statements = bucket_policy(security)
    deny = statements["NoAgentPutsOutsideItsOwnPrefix"]
    assert deny["Effect"] == "Deny" and deny["Action"] == "s3:PutObject"
    assert deny["Condition"] == {"ArnEquals": {"aws:PrincipalArn": [REFAGENT, STANDIN]}}
    assert "NotResource" in deny and "agents/refagent/*" in json.dumps(deny["NotResource"])
    assert statements["RefagentPutsUnderItsOwnPrefix"]["Condition"] == {"ArnEquals": {"aws:PrincipalArn": REFAGENT}}
    assert "ArnLike" not in json.dumps([s for s in statements.values() if "PrincipalArn" in json.dumps(s)])
    assert statements["TheStandinNeverWritesARefusalEvent"]["Effect"] == "Deny"


def test_s6s_grant_is_on_test_only_and_the_lock_is_turned_off_by_nobody_outside(security):
    statements = bucket_policy(security)
    grant = statements["SeedS6TheLockMustRefuseTheseOnTest"]
    assert set(grant["Action"]) == {"s3:PutObject", "s3:GetObjectRetention", "s3:DeleteObjectVersion", "s3:PutObjectRetention"}
    assert json.dumps(grant["Resource"]).endswith('/test/*"]]}')
    lock = statements["NobodyOutsideThisAccountTurnsTheLockOff"]
    assert lock["Action"] == "s3:PutBucketObjectLockConfiguration"
    assert lock["Condition"] == {"StringNotEquals": {"aws:PrincipalAccount": SECURITY}}


def test_an_envelope_is_put_once(security):
    once = bucket_policy(security)["AnEnvelopeIsWrittenOnce"]
    assert once["Effect"] == "Deny" and once["Condition"] == {"Null": {"s3:if-none-match": "true"}}


def selectors(trail: dict[str, Any]) -> str:
    return json.dumps(trail["AdvancedEventSelectors"])


def test_neither_trail_logs_where_the_trails_deliver_and_both_see_iams_events(security, audit):
    """Finding 17, and IAM's global events: a role changed in either account is recorded."""
    for template in (security, audit):
        (trail,) = of_type(template, "AWS::CloudTrail::Trail")
        assert trail["IsMultiRegionTrail"] is True and trail["IncludeGlobalServiceEvents"] is True
        assert trail["S3BucketName"] in (BUCKET, {"Ref": next(iter(k for k, r in security["Resources"].items()
                                                                     if r["Type"] == "AWS::S3::Bucket"))})
        assert "AWSLogs" not in selectors(trail)
        for prefix in ("agents/", "test/", "envelopes/"):
            assert f"{BUCKET}/{prefix}" in selectors(trail)
    (agent_trail,) = of_type(audit, "AWS::CloudTrail::Trail")
    assert "AWS::BedrockAgentCore::Runtime" in selectors(agent_trail)
    assert f"agentkeel-refagent-corpus-{AGENT}/" in selectors(agent_trail)  # open.md row 13


def roles(template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["Properties"]["RoleName"]: r["Properties"] for r in template["Resources"].values()
            if r["Type"] == "AWS::IAM::Role" and "RoleName" in r["Properties"]}  # fmt: skip


def test_the_read_role_reads_three_prefixes_and_the_put_role_trusts_main_only(security):
    both = roles(security)
    put = both["agentkeel-envelope-put"]["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]["StringEquals"]
    assert put["token.actions.githubusercontent.com:sub"] == ["repo:andaro74@3157440/agentkeel@1376369685:ref:refs/heads/main"]
    assert put["token.actions.githubusercontent.com:job_workflow_ref"] == "andaro74/agentkeel/.github/workflows/evals.yml@refs/heads/main"
    policies = {json.dumps(p["Roles"]): p for p in of_type(security, "AWS::IAM::Policy")}
    read = next(p for k, p in policies.items() if "ReadRole" in k)["PolicyDocument"]["Statement"]
    listed = next(s for s in read if "s3:ListBucket" in s["Action"])
    assert listed["Condition"] == {"StringLike": {"s3:prefix": ["AWSLogs/*", "agents/*", "test/*"]}}
    assert all(r.get("PermissionsBoundary") for r in both.values())


def test_the_standin_is_assumed_with_mfa_and_carries_the_constructs_denies(audit):
    from infra.construct.governed_agent import AGENT_DENIES

    (standin,) = [r for r in roles(audit).values()]
    trust = standin["AssumeRolePolicyDocument"]["Statement"][0]
    assert trust["Principal"] == {"AWS": f"arn:aws:iam::{AGENT}:user/hector.acevedo"}
    assert trust["Condition"] == {"Bool": {"aws:MultiFactorAuthPresent": "true"}}
    assert standin["Path"] == "/agentkeel/agents/"
    (policy,) = of_type(audit, "AWS::IAM::Policy")
    (deny,) = [s for s in policy["PolicyDocument"]["Statement"] if s["Effect"] == "Deny"]
    assert set(deny["Action"]) == set(AGENT_DENIES), "infra/audit/ repeats the construct's list; the two must agree"


def test_the_quarantine_denies_everything_and_is_attached_to_nothing(audit):
    quarantine = next(r for r in of_type(audit, "AWS::IAM::ManagedPolicy") if r["ManagedPolicyName"] == "agentkeel-quarantine")
    assert quarantine["PolicyDocument"]["Statement"] == [{"Action": "*", "Effect": "Deny", "Resource": "*", "Sid": "QuarantinedDoesNothing"}]
    assert not quarantine.get("Roles") and not quarantine.get("Users") and not quarantine.get("Groups")


def test_the_flow_log_goes_to_the_audit_bucket_every_minute(audit):
    (flow,) = of_type(audit, "AWS::EC2::FlowLog")
    assert flow["LogDestination"] == f"arn:aws:s3:::{BUCKET}" and flow["MaxAggregationInterval"] == 60
    assert flow["TrafficType"] == "ALL" and flow["ResourceType"] == "VPC"


def test_each_iam5_finding_on_refagents_role_has_a_reason_of_its_own(tmp_path_factory):
    """M03 open.md row 11 item k. Each suppression is in the template's metadata with the one finding it applies
    to; before `appliesTo` each suppressed every finding and the CSV printed one reason for all six."""
    template = synth(tmp_path_factory, "construct", "AgentkeelRefagent")
    policy = next(r for k, r in template["Resources"].items() if r["Type"] == "AWS::IAM::Policy")
    rules = policy["Metadata"]["cdk_nag"]["rules_to_suppress"]
    iam5 = [r for r in rules if r["id"] == "AwsSolutions-IAM5"]
    assert len(iam5) == 6 and all(len(r["applies_to"]) == 1 for r in iam5)
    assert len({r["reason"] for r in iam5}) == 6
