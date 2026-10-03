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
import yaml

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
    # M06 PR 2 (SPEC/06 section 6, item 8): the only pattern on a principal is an agent from the template's,
    # each statement holding the account as a fixed value (so S3 does not read it as public) and the tag. The
    # look-alike role it would admit is one the agent account's admin or the execution role makes and tags.
    patterned = {sid for sid, s in statements.items() if "aws:PrincipalArn" in json.dumps((s.get("Condition") or {}).get("ArnLike"))}
    assert patterned == {"AnAgentFromTheTemplatePutsUnderItsOwnPrefix", "NoAgentFromTheTemplatePutsOutsideItsOwnPrefix"}
    for sid in patterned:
        assert statements[sid]["Condition"]["StringEquals"]["aws:PrincipalAccount"] == "581208540944"
        assert statements[sid]["Condition"]["Null"] == {"aws:PrincipalTag/agentkeel:agent": "false"}
    assert "${aws:PrincipalTag/agentkeel:agent}" in json.dumps(statements["AnAgentFromTheTemplatePutsUnderItsOwnPrefix"]["Resource"])
    assert statements["AnAgentFromTheTemplatePutsUnderItsOwnPrefix"]["Condition"]["StringNotEquals"] == {
        "aws:PrincipalTag/agentkeel:agent": "refagent"}
    assert statements["TheStandinNeverWritesARefusalEvent"]["Effect"] == "Deny"


def test_the_standins_allow_is_gone_and_its_two_denies_stay(security):
    """M06 open.md row 2, ruled at M06 open: the Allow that named the deleted stand-in is removed."""
    statements = bucket_policy(security)
    assert "TheStandinPutsUnderItsOwnCornerOfIt" not in statements
    assert STANDIN in json.dumps(statements["NoAgentPutsOutsideItsOwnPrefix"])
    assert STANDIN in json.dumps(statements["TheStandinNeverWritesARefusalEvent"])
    allows = [s for s in statements.values() if s["Effect"] == "Allow"]
    assert STANDIN not in json.dumps(allows)


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


def test_the_read_role_reads_its_prefixes_and_the_put_role_trusts_main_only(security):
    both = roles(security)
    put = both["agentkeel-envelope-put"]["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]["StringEquals"]
    assert put["token.actions.githubusercontent.com:sub"] == ["repo:andaro74@3157440/agentkeel@1376369685:ref:refs/heads/main"]
    assert put["token.actions.githubusercontent.com:job_workflow_ref"] == "andaro74/agentkeel/.github/workflows/evals.yml@refs/heads/main"
    # M06 PR 2 (R7; security-reviewer F7): deploy.yml's own role, on main, under envelopes/agents/ alone.
    answer = both["agentkeel-answer-put"]["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]["StringEquals"]
    assert answer["token.actions.githubusercontent.com:job_workflow_ref"] == "andaro74/agentkeel/.github/workflows/deploy.yml@refs/heads/main"
    assert answer["token.actions.githubusercontent.com:sub"] == ["repo:andaro74@3157440/agentkeel@1376369685:ref:refs/heads/main"]
    answer_put = next(p for k, p in {json.dumps(p["Roles"]): p for p in of_type(security, "AWS::IAM::Policy")}.items()
                      if "AnswerPutRole" in k)["PolicyDocument"]["Statement"]  # fmt: skip
    # M07 PR 2 (rulings/pr2-security.md item 11): and the signed bundle of what it deployed, under bundles/.
    assert [s["Action"] for s in answer_put] == ["s3:PutObject", "s3:PutObject"]
    assert "envelopes/agents/*" in json.dumps(answer_put[0]["Resource"]) and "bundles/*" in json.dumps(answer_put[1]["Resource"])
    policies = {json.dumps(p["Roles"]): p for p in of_type(security, "AWS::IAM::Policy")}
    read = next(p for k, p in policies.items() if "ReadRole" in k)["PolicyDocument"]["Statement"]
    listed = next(s for s in read if "s3:ListBucket" in s["Action"])
    # M07 PR 2: observations/ is listed and read; bundles/ is listed only.
    assert listed["Condition"] == {"StringLike": {"s3:prefix": ["AWSLogs/*", "agents/*", "test/*", "envelopes/agents/*",
                                                               "observations/*", "bundles/*"]}}  # fmt: skip
    reading = next(s for s in read if "s3:GetObject" in s["Action"])
    assert "observations/*" in json.dumps(reading["Resource"]) and "bundles/" not in json.dumps(reading["Resource"])
    assert all(r.get("PermissionsBoundary") for r in both.values())


def test_the_standin_is_gone_once_s2_and_s3_are_read(audit):
    """Security's constraint on M05 PR 2: the stand-in is deleted once S2 and S3 are read. S3 was read at M05 PR 3
    (5a5fe1e), so the stack makes no stand-in role and no policy for one. Until then this test held its MFA trust
    and that its denies equal the construct's (M05 PR 2, cold review F4); git log -p shows that version."""
    assert not [r for r in roles(audit).values() if r["RoleName"] == "agentkeel-refagent-standin"]
    assert not [p for p in of_type(audit, "AWS::IAM::Policy") if "Standin" in json.dumps(p.get("Roles"))]


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


def test_s1s_origin_is_removed_once_it_showed_the_finding(audit):
    """M05 PR 2: the Lambda tried as S1's origin timed out and left no flow record, as CloudShell had, because the VPC
    has no route out (rulings/pr2.md ruling 9). S1_ORIGIN = False: the stack makes neither the function nor its role."""
    assert of_type(audit, "AWS::Lambda::Function") == []
    assert "agentkeel-seed-s1-role" not in roles(audit)


# --- M07 PR 2: bundles/ and observations/ (SPEC/07 section 6; rulings/pr2-security.md items 9 and 11) ----


def test_a_bundle_and_an_observation_are_each_put_once(security):
    statements = bucket_policy(security)
    for sid, prefix in (("ABundleIsWrittenOnce", "bundles/*"), ("AnObservationIsWrittenOnce", "observations/*")):
        once = statements[sid]
        assert once["Effect"] == "Deny" and once["Action"] == "s3:PutObject" and once["Principal"] == {"AWS": "*"}
        assert once["Condition"] == {"Null": {"s3:if-none-match": "true"}} and json.dumps(once["Resource"]).endswith(f'/{prefix}"]]}}')
    # No Allow in the bucket's policy for either prefix: the two roles that put there are this account's own.
    assert not [s for s in statements.values() if s["Effect"] == "Allow" and ("bundles/" in json.dumps(s["Resource"])
                                                                               or "observations/" in json.dumps(s["Resource"]))]  # fmt: skip


def test_the_observation_put_role_trusts_observe_yml_on_main_and_puts_under_observations_only(security):
    """M07 PR 4: the putting job runs in the environment platform-observer, so GitHub's `sub` names the
    environment, not the ref; the role trusted the ref form and every keyed run was refused (37119509159)."""
    role = roles(security)["agentkeel-observation-put"]
    on_main = role["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]["StringEquals"]
    assert on_main["token.actions.githubusercontent.com:sub"] == ["repo:andaro74@3157440/agentkeel@1376369685:environment:platform-observer"]
    workflow = yaml.safe_load((ROOT / ".github/workflows/observe.yml").read_text(encoding="utf-8"))
    assert workflow["jobs"]["observe"]["environment"] == "platform-observer", "the trust names the job's environment"
    assert on_main["token.actions.githubusercontent.com:job_workflow_ref"] == "andaro74/agentkeel/.github/workflows/observe.yml@refs/heads/main"
    assert role.get("PermissionsBoundary")
    policy = next(p for k, p in {json.dumps(p["Roles"]): p for p in of_type(security, "AWS::IAM::Policy")}.items()
                  if "ObservationPutRole" in k)["PolicyDocument"]["Statement"]  # fmt: skip
    assert [s["Action"] for s in policy] == ["s3:PutObject"] and json.dumps(policy[0]["Resource"]).endswith('/observations/*"')


def test_the_trail_logs_the_two_new_prefixes_and_still_not_its_own_delivery(security):
    (trail,) = of_type(security, "AWS::CloudTrail::Trail")
    logged = json.dumps(trail["AdvancedEventSelectors"])
    assert f"{BUCKET}/bundles/" in logged and f"{BUCKET}/observations/" in logged and f"{BUCKET}/AWSLogs/" not in logged
    (bucket,) = of_type(security, "AWS::S3::Bucket")
    assert bucket["ObjectLockConfiguration"]["Rule"]["DefaultRetention"] == {"Mode": "COMPLIANCE", "Days": 1}  # no retention changed
