"""M09 PR 2's builder: the agent's own guardrail in its stack, and the bootstrap's narrowed grants (SPEC/09 §6; R3, R4).

The seed tests say the platform check admits the fixture agent and reads its
rules. These say what the construct and the bootstrap do with them: the
guardrail built in the fixture's stack from the merged rules, tagged, with the
digest on its version, the call conditioned on it and the placeholder pin
nowhere; a file the merge refuses refused at synth; refagent's spec merged
onto the baseline with the rules unchanged and the digest over three files;
the deploy boundary and the execution role narrowed to a tagged guardrail; the
eval role's read-back on a tagged guardrail only. Nothing here calls AWS.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.validate import agent_rules

from .test_bootstrap import (
    APP as BOOTSTRAP_APP,
    GUARDRAIL_ADMIN,
    actions,
    denies_by_pattern,
    eval_role_policy,
    named,
    of_type,
    statements,
    template as bootstrap_template,  # noqa: F401  (the fixture, by its name)
)

ROOT = Path(__file__).resolve().parents[1]
CONSTRUCT_APP = ROOT / "infra" / "construct" / "app.py"
FIXTURE = ROOT / "tests" / "fixtures" / "m09" / "s1-festival-desk"
WEAKENED = ROOT / "tests" / "fixtures" / "m09" / "s2-weakened-baseline" / "weakened.yaml"
BASELINE = ROOT / "rules" / "baseline.yaml"
TAG = "agentkeel:agent"


def synth(bundle: Path, out: Path) -> tuple[int, str, dict[str, Any] | None]:
    """The construct's app over `bundle`, as deploy.yml runs it, in its own interpreter."""
    done = subprocess.run(
        [sys.executable, str(CONSTRUCT_APP)], cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out), "AGENTKEEL_BUNDLE": bundle.as_posix()},
    )  # fmt: skip
    template_path = out / "AgentkeelAgent.template.json"
    template = json.loads(template_path.read_text(encoding="utf-8")) if done.returncode == 0 and template_path.is_file() else None
    return done.returncode, done.stderr.strip() or done.stdout.strip(), template


@pytest.fixture(scope="module")
def fixture_template(tmp_path_factory) -> dict[str, Any]:
    code, said, template = synth(FIXTURE.relative_to(ROOT), tmp_path_factory.mktemp("festival-desk"))
    assert code == 0, said
    return template


def the_one(template: dict[str, Any], kind: str) -> tuple[str, dict[str, Any]]:
    found = list(of_type(template, kind).items())
    assert len(found) == 1, (kind, len(found))
    return found[0][0], found[0][1]["Properties"]


# --- the fixture's stack: its own guardrail, built from the merged rules (R3) ----------------------


def test_the_fixture_agents_stack_builds_its_own_guardrail_from_the_merged_rules(fixture_template):
    logical, built = the_one(fixture_template, "AWS::Bedrock::Guardrail")
    assert built["Name"] == "agentkeel-festival-desk"
    assert {"Key": TAG, "Value": "festival-desk"} in built["Tags"]
    rules = yaml.safe_load((FIXTURE / "rules" / "guardrail.yaml").read_text(encoding="utf-8"))
    topics = built["TopicPolicyConfig"]["TopicsConfig"]
    assert [(t["Name"], t["Type"], t["InputAction"], t["OutputEnabled"]) for t in topics] == [
        ("unannounced-selection-leak", "DENY", "BLOCK", False)]  # the agent's one topic, on the question only
    assert topics[0]["Definition"] == rules["denied_topics"][0]["definition"]
    # the baseline's two entities, which the agent file does not carry and could not remove
    assert built["SensitiveInformationPolicyConfig"]["PiiEntitiesConfig"] == [
        {"Type": "PHONE", "Action": "ANONYMIZE"}, {"Type": "EMAIL", "Action": "ANONYMIZE"}]
    assert "ContentPolicyConfig" not in built  # the prompt-attack filter is the baseline's, off
    assert built["BlockedInputMessaging"] == rules["messages"]["blocked_input"]  # the agent's messages replace the defaults


def test_the_version_carries_the_digest_of_the_baseline_and_the_agents_files_and_is_retained(fixture_template):
    _, version = the_one(fixture_template, "AWS::Bedrock::GuardrailVersion")
    digest = agent_rules.digest(BASELINE.read_bytes(), (FIXTURE / "rules" / "guardrail.yaml").read_bytes())
    assert version["Description"] == f"rules sha256 {digest}"
    for kind in ("AWS::Bedrock::GuardrailVersion", "AWS::Bedrock::Guardrail"):
        (resource,) = of_type(fixture_template, kind).values()
        assert resource.get("DeletionPolicy") == "Retain" and resource.get("UpdateReplacePolicy") == "Retain", kind
    outputs = fixture_template["Outputs"]
    assert outputs["GuardrailDigest"]["Value"] == digest
    assert {"GuardrailId", "GuardrailVersion"} <= set(outputs)


def test_the_call_is_conditioned_on_the_stacks_own_guardrail_and_the_placeholder_is_nowhere(fixture_template):
    """SPEC/09 §2 'The placeholder pin': the construct reads the manifest's pin only to refuse null and refagent's."""
    guardrail, _ = the_one(fixture_template, "AWS::Bedrock::Guardrail")
    version, _ = the_one(fixture_template, "AWS::Bedrock::GuardrailVersion")
    rendered = json.dumps(fixture_template)
    assert "fest1va1desk" not in rendered
    invokes = [s for policy in of_type(fixture_template, "AWS::IAM::Policy").values()
               for s in policy["Properties"]["PolicyDocument"]["Statement"]
               if s["Effect"] == "Allow" and "bedrock:InvokeModel" in actions(s)]  # fmt: skip
    assert len(invokes) == 2
    for statement in invokes:
        identifier = statement["Condition"]["StringEquals"]["bedrock:GuardrailIdentifier"]
        assert identifier == {"Fn::Join": ["", [{"Fn::GetAtt": [guardrail, "GuardrailArn"]}, ":", {"Fn::GetAtt": [version, "Version"]}]]}
    runtime = next(iter(of_type(fixture_template, "AWS::BedrockAgentCore::Runtime").values()))["Properties"]
    env = runtime["EnvironmentVariables"]
    assert env["AGENTKEEL_GUARDRAIL_ARN"] == {"Fn::GetAtt": [guardrail, "GuardrailArn"]}
    assert env["AGENTKEEL_GUARDRAIL_VERSION"] == {"Fn::GetAtt": [version, "Version"]}


def test_a_rules_file_the_merge_refuses_is_refused_at_synth_naming_the_rule(tmp_path):
    """Seed S2's weakened file as the agent's rules: the stack is not synthesised, and the reason names EMAIL."""
    bundle = tmp_path / "festival-desk"
    shutil.copytree(FIXTURE, bundle)
    shutil.copy(WEAKENED, bundle / "rules" / "guardrail.yaml")
    code, said, _ = synth(bundle, tmp_path / "out")
    assert code != 0 and "EMAIL" in said and "ANONYMIZE to NONE" in said


def test_an_agent_with_rules_that_pins_refagents_guardrail_is_refused_at_synth(tmp_path):
    bundle = tmp_path / "festival-desk"
    shutil.copytree(FIXTURE, bundle)
    manifest = yaml.safe_load((bundle / "manifest.yaml").read_text(encoding="utf-8"))
    manifest["guardrail"] = {"id": "1088aw3ujhyd", "version": "5"}
    (bundle / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    code, said, _ = synth(bundle, tmp_path / "out")
    assert code != 0 and "pins refagent's" in said


def test_an_agent_without_rules_keeps_the_manifests_pin_and_builds_no_guardrail(tmp_path):
    """M06's path, unchanged: no rules/, refagent's pin, the call conditioned on it by ARN."""
    bundle = tmp_path / "plain-desk"
    shutil.copytree(FIXTURE, bundle)
    shutil.rmtree(bundle / "rules")
    (bundle / "goldens" / "g-030.yaml").unlink()
    manifest = yaml.safe_load((bundle / "manifest.yaml").read_text(encoding="utf-8"))
    manifest["name"], manifest["guardrail"] = "plain-desk", {"id": "1088aw3ujhyd", "version": "5"}
    (bundle / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    code, said, template = synth(bundle, tmp_path / "out")
    assert code == 0, said
    assert not of_type(template, "AWS::Bedrock::Guardrail") and "GuardrailId" not in template["Outputs"]
    assert "guardrail/1088aw3ujhyd:5" in json.dumps(template)


# --- the bootstrap: refagent's spec on the baseline (R2), the narrowed grants (R3), the read-back (R4) -----


def test_refagents_guardrail_is_the_same_rules_with_the_digest_over_the_baseline_first(bootstrap_template, tmp_path_factory):
    """R2: the entries stay in refagent's file, the merge dedupes them, the id is kept and the digest is new."""
    import importlib.util

    os.environ.setdefault("CDK_OUTDIR", str(tmp_path_factory.mktemp("bootstrap-m09")))
    spec = importlib.util.spec_from_file_location("bootstrap_app_m09", BOOTSTRAP_APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    built = module.guardrail_spec()
    rules = yaml.safe_load((ROOT / "agents" / "refagent" / "rules" / "guardrail.yaml").read_text(encoding="utf-8"))
    assert [t["name"] for t in built["topics"]] == [t["name"] for t in rules["denied_topics"]]
    assert built["pii"] == rules["pii"] and built["messages"] == rules["messages"]
    files = [ROOT / "agents" / "refagent" / "rules" / n for n in ("guardrail.yaml", "redteam.yaml")]
    assert built["digest"] == agent_rules.digest(BASELINE.read_bytes(), *(f.read_bytes() for f in files))
    _, version = the_one(bootstrap_template, "AWS::Bedrock::GuardrailVersion")
    assert version["Description"] == f"rules sha256 {built['digest']}"
    _, guardrail = the_one(bootstrap_template, "AWS::Bedrock::Guardrail")
    assert "Tags" not in guardrail  # refagent's is the bootstrap's, untagged: no agent stack's role may reach it


def test_the_deploy_boundary_denies_a_guardrail_action_unless_the_guardrail_is_a_tagged_agents_own(bootstrap_template):
    boundary = named(bootstrap_template, "agentkeel-deploy-boundary")
    conditioned = [s for s in statements(boundary, "Deny") if any(a.startswith("bedrock:") and "Guardrail" in a for a in actions(s))
                   and s.get("Condition")]  # fmt: skip
    assert len(conditioned) == 1
    assert conditioned[0]["Condition"] == {"Null": {f"aws:RequestTag/{TAG}": "true", f"aws:ResourceTag/{TAG}": "true"}}
    assert all(denies_by_pattern(actions(conditioned[0]), a) for a in GUARDRAIL_ADMIN - {"bedrock:ListGuardrails"})
    flat = [s for s in statements(boundary, "Deny") if not s.get("Condition")]
    assert any("bedrock:ListGuardrails" in actions(s) for s in flat)
    assert not any(denies_by_pattern(actions(s), "bedrock:CreateGuardrail") for s in flat)


def test_the_execution_role_makes_a_guardrail_only_with_the_tag_and_touches_only_a_tagged_one(bootstrap_template):
    found = [s for policy in of_type(bootstrap_template, "AWS::IAM::Policy").values()
             if "ExecutionRole" in json.dumps(policy["Properties"]["Roles"])
             for s in policy["Properties"]["PolicyDocument"]["Statement"]
             if s["Effect"] == "Allow" and (any("Guardrail" in a for a in actions(s)) or "Guardrail" in s.get("Sid", ""))]  # fmt: skip
    by_sid = {s["Sid"]: s for s in found}
    assert set(by_sid) == {"MakeAnAgentsGuardrailOnlyWithItsTag", "TagAnAgentsGuardrailAtCreateOnly",
                           "ReadUpdateVersionAndRemoveATaggedAgentsGuardrailOnly"}  # fmt: skip
    # M09 PR 3 (R3-a, the Service Authorization Reference for Amazon Bedrock read 2026-10-11): CreateGuardrail
    # takes no `guardrail` resource type, so a statement on guardrail/* never applied to it and the first deploy
    # of an agent with rules/ would have been refused on CreateGuardrail. Resource *, held by the request tag.
    make = by_sid["MakeAnAgentsGuardrailOnlyWithItsTag"]
    assert actions(make) == {"bedrock:CreateGuardrail"} and make["Resource"] == "*"
    assert make["Condition"] == {"Null": {f"aws:RequestTag/{TAG}": "false"}}
    # The CreateGuardrail operation authorises bedrock:TagResource too when the request carries tags, and the
    # create handler tags the new guardrail before it carries one (describe-type, tagOnCreate): TagResource on
    # guardrail/*, held to the request tag, and nothing else in that statement. (At PR 2 CreateGuardrail stood
    # alone on the request-tag side so a tagged request could not tag refagent's untagged guardrail, F3; the
    # boundary now denies that by ARN, below.)
    tag_at_create = by_sid["TagAnAgentsGuardrailAtCreateOnly"]
    assert actions(tag_at_create) == {"bedrock:TagResource"}
    assert "guardrail/*" in json.dumps(tag_at_create["Resource"]) and "profile" not in json.dumps(tag_at_create["Resource"])
    assert tag_at_create["Condition"] == {"Null": {f"aws:RequestTag/{TAG}": "false"}}
    tagging = [s for s in statements(named(bootstrap_template, "agentkeel-deploy-boundary"), "Deny")
               if "bedrock:TagResource" in actions(s)]  # fmt: skip
    assert len(tagging) == 2 and all(actions(s) == {"bedrock:TagResource", "bedrock:UntagResource"} for s in tagging)
    by_boundary_sid = {s["Sid"]: s for s in tagging}
    untagged = by_boundary_sid["NeverTagAGuardrailThatIsNotATaggedAgentsOwn"]
    assert untagged["Condition"] == {"Null": {f"aws:RequestTag/{TAG}": "true", f"aws:ResourceTag/{TAG}": "true"}}
    assert "guardrail/*" in json.dumps(untagged["Resource"]) and "profile" not in json.dumps(untagged["Resource"])
    # F3 closed by name: refagent's guardrail, the bootstrap's own, may not be tagged or untagged by any role the
    # deploy boundary caps, whatever the request carries. Flat: no condition.
    refagent = by_boundary_sid["NeverTagRefagentsGuardrail"]
    assert "Condition" not in refagent
    guardrail_logical, _ = the_one(bootstrap_template, "AWS::Bedrock::Guardrail")
    # Both ARN forms the Apply grant names (security-reviewer F2 on PR 3): the guardrail's and its versions'.
    arn = {"Fn::GetAtt": [guardrail_logical, "GuardrailArn"]}
    assert refagent["Resource"] == [arn, {"Fn::Join": ["", [arn, ":*"]]}], refagent["Resource"]
    assert by_sid["ReadUpdateVersionAndRemoveATaggedAgentsGuardrailOnly"]["Condition"] == {"Null": {f"aws:ResourceTag/{TAG}": "false"}}
    assert "bedrock:ListGuardrails" not in {a for s in found for a in actions(s)}


# What CloudFormation's handlers call for the two resource types the fixture's stack adds, as `describe-type`
# gave them on 2026-10-11 (AWS::Bedrock::Guardrail create: CreateGuardrail, GetGuardrail, TagResource,
# ListTagsForResource and four kms calls the construct's guardrail, built with no customer key, does not make;
# AWS::Bedrock::GuardrailVersion create: CreateGuardrailVersion, GetGuardrail and two kms calls likewise). The
# bootstrap tests' NEEDED_BY_TYPE is refagent's stack's and does not list these (refagent's guardrail is the
# bootstrap's). By action: a grant's resource and condition are read by the test above, not here.
GUARDRAIL_HANDLERS_NEED = {
    "AWS::Bedrock::Guardrail": {"bedrock:CreateGuardrail", "bedrock:GetGuardrail", "bedrock:TagResource",
                                "bedrock:ListTagsForResource", "bedrock:UpdateGuardrail", "bedrock:UntagResource",
                                "bedrock:DeleteGuardrail"},
    "AWS::Bedrock::GuardrailVersion": {"bedrock:CreateGuardrailVersion", "bedrock:GetGuardrail", "bedrock:DeleteGuardrail"},
}  # fmt: skip


def test_the_execution_role_may_make_the_fixture_stacks_guardrail_and_its_version(bootstrap_template, fixture_template):
    """Every action the two handlers call is granted to the execution role, and the boundary's flat denies on
    Resource * deny none of them (the conditioned and the named-resource denies fire on a guardrail that is
    not the agent's own, which the agent's new one is not)."""
    granted = {a for policy in of_type(bootstrap_template, "AWS::IAM::Policy").values()
               if "ExecutionRole" in json.dumps(policy["Properties"]["Roles"])
               for s in policy["Properties"]["PolicyDocument"]["Statement"] if s["Effect"] == "Allow" for a in actions(s)}  # fmt: skip
    flat = {a for s in statements(named(bootstrap_template, "agentkeel-deploy-boundary"), "Deny")
            if not s.get("Condition") and s["Resource"] == "*" for a in actions(s)}  # fmt: skip
    rendered = {r["Type"] for r in fixture_template["Resources"].values()}
    assert set(GUARDRAIL_HANDLERS_NEED) <= rendered
    for kind, needs in GUARDRAIL_HANDLERS_NEED.items():
        assert needs <= granted, (kind, sorted(needs - granted))
        assert not [a for a in needs if denies_by_pattern(flat, a)], kind


def test_the_eval_role_reads_a_tagged_agents_guardrail_back_and_no_other(bootstrap_template):
    """R4: GetGuardrail on a guardrail tagged as an agent's own; refagent's, untagged, stays denied."""
    allowing = [s for s in eval_role_policy(bootstrap_template) if s["Effect"] == "Allow" and "bedrock:GetGuardrail" in actions(s)]
    assert len(allowing) == 1 and actions(allowing[0]) == {"bedrock:GetGuardrail"}
    assert allowing[0]["Condition"] == {"Null": {f"aws:ResourceTag/{TAG}": "false"}}
    denying = [s for s in eval_role_policy(bootstrap_template) if s["Effect"] == "Deny" and "bedrock:GetGuardrail" in actions(s)]
    assert len(denying) == 1 and denying[0]["Condition"] == {"Null": {f"aws:ResourceTag/{TAG}": "true"}}
    flat = {a for s in eval_role_policy(bootstrap_template) if s["Effect"] == "Deny" and not s.get("Condition") for a in actions(s)}
    assert "bedrock:GetGuardrail" not in flat and denies_by_pattern(flat, "bedrock:CreateGuardrail")
