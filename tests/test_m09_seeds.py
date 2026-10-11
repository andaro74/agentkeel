"""M09's seeded cases (SPEC/09 §5), committed before the code that reads them.

Three kinds. **The fixture agent** is S1, `tests/fixtures/m09/s1-festival-desk/`:
the template's agent folder with `rules/guardrail.yaml` of its own (one denied
topic), one guardrail golden `g-030` planted for it with a `blocks` entry
naming that topic, and a manifest pinning a guardrail of its own, not
refagent's. Two tests are planted on it: the platform check must admit it
(today it refuses the pin and the golden's kind, which is the false state),
and `src.validate.agent_rules.rules_errors` must read its rules (today the
module is not there). One guard holds the fixture to refagent's format.
**Rule-file seeds** S2 and S5 are agent rule files under `tests/fixtures/m09/`
that the merge must refuse or merge as named; their reader is the same
module. **S3** is three answer records read by `src.verdict.agent_rules.plants`.
**S4** is a guard, no fixture: refagent's own rules as they stand, which the
baseline split must leave whole. **The run** is `milestones/M09/runs/
f9_3_plant_run.yaml`, `observed: null`, read by `scripts/observe_rules.py`
after PR 2 merges.

Each planted test is marked `xfail(strict=True, raises=AssertionError)`, so
an exception of any other class (a moved fixture, a file that no longer
parses) is a failure, not an expected one. Preconditions raise `SeedBroken`.
Each was run once with `--runxfail` and its message read, and a marker comes
off in the commit that lands its reader (fixtures, PR 2) or records the run
(PR 3). Nothing here calls AWS, a model or GitHub.

M09 builds one control, the add-only merge and the guardrail built from it
(ADR-0014); these readers are the platform check's and the envelope's. P5
holds: the observer writes raw observations, `build` rules, the gate reads
the envelope, the ledger reads the gate.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT
from tests.test_m06_seeds import SeedBroken, holds, stand_in_lookup

RUNS = ROOT / "milestones" / "M09" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m09"
AGENT = FIXTURES / "s1-festival-desk"
BASELINE = ROOT / "rules" / "baseline.yaml"
REFAGENT_RULES = ROOT / "agents" / "refagent" / "rules"

expected_failure = pytest.mark.xfail(strict=True, raises=AssertionError, reason="planted at M09 PR 1 (SPEC/09 §5)")

# Bedrock's limits on a denied topic, as infra/bootstrap/app.py holds them at synth (not imported here:
# the bootstrap module pulls in aws_cdk, and the guard needs only the numbers).
TOPIC_NAME = re.compile(r"^[0-9a-zA-Z\-_ !?.]{1,100}$")
TOPIC_DEFINITION_MAX, TOPIC_EXAMPLE_MAX, TOPIC_EXAMPLES_MAX = 200, 100, 5


def load_yaml(path: Path) -> Any:
    holds(path.is_file(), f"{path.relative_to(ROOT).as_posix()} is in the tree")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def reader(module: str, name: str, seed: str, what: str) -> Any:
    """A function PR 2 adds to `module`; the planted failure is that the module is not there."""
    assert importlib.util.find_spec(module) is not None, f"seed {seed}: {what}"
    found = getattr(importlib.import_module(module), name, None)
    assert found is not None, f"seed {seed}: {what}"
    return found


def record(name: str) -> dict[str, Any]:
    path = FIXTURES / "s3-silent-plant" / name
    holds(path.is_file(), f"{name} is in tests/fixtures/m09/s3-silent-plant/")
    return json.loads(path.read_text(encoding="utf-8"))


# --- S1: the fixture agent ------------------------------------------------------


def test_s1_guard_the_fixture_is_in_refagents_format():
    """A guard, no marker: the fixture's rules file has the keys refagent's has but `pii` and
    `content_filters` (the baseline supplies those; add-only, SPEC/09 §2), one denied topic within
    Bedrock's limits, `plants` naming g-030, `blocks` naming the topic for it, and g-030 is a guardrail
    golden expected BLOCKED whose question is not the topic's example. If this fails the fixture carries
    a second fault and the planted tests below would fail for the wrong reason."""
    rules = load_yaml(AGENT / "rules" / "guardrail.yaml")
    assert set(rules) == {"plants", "blocks", "topics_apply_to", "denied_topics", "messages"}, sorted(rules)
    assert rules["plants"] == ["g-030"] and rules["blocks"] == {"g-030": "unannounced-selection-leak"}
    assert rules["topics_apply_to"] == "input"
    topics = rules["denied_topics"]
    assert len(topics) == 1 and topics[0]["name"] == "unannounced-selection-leak"
    topic = topics[0]
    assert TOPIC_NAME.match(topic["name"]) and len(topic["definition"]) <= TOPIC_DEFINITION_MAX
    assert len(topic["examples"]) <= TOPIC_EXAMPLES_MAX and all(len(e) <= TOPIC_EXAMPLE_MAX for e in topic["examples"])
    golden = load_yaml(AGENT / "goldens" / "g-030.yaml")
    assert golden["kind"] == "guardrail" and golden["expected"] == "BLOCKED" and golden["id"] == "g-030"
    assert golden["question"].strip() not in topic["examples"], "the plant's question must not be the rule's example"
    manifest = load_yaml(AGENT / "manifest.yaml")
    refagent = load_yaml(ROOT / "agents" / "refagent" / "manifest.yaml")
    assert manifest["guardrail"] and manifest["guardrail"] != refagent["guardrail"], "the pin is the agent's own"
    # The template's minimum beside the plant, citing the full table the template ships (not M08's two rows).
    kinds = sorted(load_yaml(p)["kind"] for p in (AGENT / "goldens").glob("g-*.yaml"))
    assert kinds == ["guardrail", "ordinary", "trap"], kinds


def test_s1_the_platform_check_admits_an_agent_with_its_own_rules():
    """The platform check must admit an agent repository that pins a guardrail of its own and plants a
    guardrail golden for its own rule (F9.1, F9.4). Today `evaluate()` refuses it twice: on the pin
    (src/validate/agent.py:114-116, "one guardrail for every agent at M06") and on g-030's kind
    (src/validate/agent_goldens.py:88-90). That is the false state (SPEC/09 §3.2, §3.4)."""
    from src.validate import agent as platform_check

    errors = platform_check.evaluate(AGENT, "agentkeel-studio/festival-desk", lookup=stand_in_lookup)
    refused = {name: errs for name, errs in errors.items() if errs}
    assert not refused, f"seed S1: the platform check refuses an agent's own pin and its guardrail golden: {refused}"


def test_s1_an_agent_repositorys_rules_are_read():
    """`src.validate.agent_rules.rules_errors(agent_dir)` must read the fixture's rules/guardrail.yaml and
    find nothing wrong with it (F9.1). Today nothing reads an agent repository's rules/ (SPEC/09 §3.1)."""
    rules_errors = reader("src.validate.agent_rules", "rules_errors", "S1",
                          "nothing reads an agent repository's rules/guardrail.yaml")  # fmt: skip
    assert rules_errors(AGENT) == []


# --- S2: a weakened baseline, read by agent_rules.merge and merge_errors -------

MERGE_WHAT = "no platform baseline exists and nothing merges an agent's rules onto one"


def test_s2_a_weakened_baseline_rule_is_refused():
    """`weakened.yaml` lists EMAIL with action NONE. The merge must refuse it, naming EMAIL and the way
    (F9.2). Today rules/baseline.yaml does not exist and no merge reads two files (SPEC/09 §3.3)."""
    weakened = load_yaml(FIXTURES / "s2-weakened-baseline" / "weakened.yaml")
    holds(weakened["pii"] == [{"entity": "EMAIL", "action": "NONE"}], "S2 weakens EMAIL to NONE")
    assert BASELINE.is_file(), f"seed S2: {MERGE_WHAT}"
    merge_errors = reader("src.validate.agent_rules", "merge_errors", "S2", MERGE_WHAT)
    errors = merge_errors(load_yaml(BASELINE), weakened)
    assert errors and all("EMAIL" in e for e in errors), errors


def test_s2_an_empty_list_removes_nothing():
    """`empty_pii.yaml` lists `pii: []`. Add-only: the merged rules must still hold the baseline's PHONE and
    EMAIL as ANONYMIZE, and the agent's own topic beside them (F9.2). Today there is no baseline and no
    merge (SPEC/09 §3.3)."""
    empty = load_yaml(FIXTURES / "s2-weakened-baseline" / "empty_pii.yaml")
    holds(empty["pii"] == [], "S2's second file lists an empty pii")
    assert BASELINE.is_file(), f"seed S2: {MERGE_WHAT}"
    merge = reader("src.validate.agent_rules", "merge", "S2", MERGE_WHAT)
    merged = merge(load_yaml(BASELINE), empty)
    entities = {(e["entity"], e["action"]) for e in merged["pii"]}
    assert {("PHONE", "ANONYMIZE"), ("EMAIL", "ANONYMIZE")} <= entities, entities
    assert "unannounced-selection-leak" in {t["name"] for t in merged["denied_topics"]}


# --- S3: a silent plant, read by agent_rules.plants -------------------------------


def test_s3_a_silent_plant_is_read_from_the_answer_record():
    """Three answer records for the fixture agent. In the first g-030 is blocked with a topic that is not
    its named rule; in the second it is answered. `src.verdict.agent_rules.plants(record, blocks)` must
    read both as not held, naming g-030 and what the trace recorded, and hold the third, where the named
    rule is among the topics (F9.3; membership, not "only", as build reads refagent's plants). Today
    nothing reads an agent's plant from an answer record (SPEC/09 §3.5)."""
    blocks = load_yaml(AGENT / "rules" / "guardrail.yaml")["blocks"]
    plants = reader("src.verdict.agent_rules", "plants", "S3", "nothing reads an agent's plant from an answer record")
    other = plants(record("record_blocked_by_another_rule.json"), blocks)
    assert other["read"] is True and other["held"] is False, other
    assert "g-030" in " ".join(other["reasons"]) and "some-other-rule" in " ".join(other["reasons"]), other["reasons"]
    answered = plants(record("record_answered.json"), blocks)
    assert answered["held"] is False and "g-030" in " ".join(answered["reasons"]), answered
    assert answered["fired"] == 0 and answered["expected"] == 1, answered
    held = plants(record("record_held.json"), blocks)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held
    assert held["fired"] == 1 and held["expected"] == 1, held


# --- S4: refagent's rules after the split (a guard, not a seed; it passes) --------

REFAGENT_TOPICS = {"embargoed-synopsis", "sending-terms-to-a-competitor", "claimed-authority-override",
                   "contract-text-disclosure", "rule-override", "user-supplied-contract-terms"}  # fmt: skip


def test_s4_refagents_rules_are_whole():
    """F9.5's guard: refagent's guardrail.yaml holds its six topics by name and PHONE and EMAIL as ANONYMIZE,
    its two plants with their named rules, and redteam.yaml its five plants. It passes today and must pass
    after the baseline is separated (SPEC/09 §5, §11 R2): a split that moves a rule out of refagent's file
    fails here, and ADR-0009 entry 5 makes that two keys. No marker."""
    guardrail = load_yaml(REFAGENT_RULES / "guardrail.yaml")
    assert {t["name"] for t in guardrail["denied_topics"]} == REFAGENT_TOPICS
    assert {(e["entity"], e["action"]) for e in guardrail["pii"]} == {("PHONE", "ANONYMIZE"), ("EMAIL", "ANONYMIZE")}
    assert guardrail["plants"] == ["g-013", "g-015"] and set(guardrail["blocks"]) == {"g-013", "g-015"}
    assert set(guardrail["blocks"].values()) <= REFAGENT_TOPICS
    redteam = load_yaml(REFAGENT_RULES / "redteam.yaml")
    assert redteam["plants"] == ["g-016", "g-017", "g-018", "g-019", "g-020"]
    assert set(redteam["blocks"].values()) <= REFAGENT_TOPICS


# --- S5: an unnamed plant, read by agent_rules.rules_errors -------------------------


def test_s5_a_plant_with_no_named_rule_is_refused():
    """`no_blocks.yaml` plants g-030 and names no rule for it; `unbuilt_rule.yaml` names a rule its topics
    do not build. `rules_errors` must refuse both, naming the golden and the rule (F9.4). Today nothing
    reads a plant's named rule in an agent repository (SPEC/09 §3.4)."""
    no_blocks = load_yaml(FIXTURES / "s5-unnamed-plant" / "no_blocks.yaml")
    unbuilt = load_yaml(FIXTURES / "s5-unnamed-plant" / "unbuilt_rule.yaml")
    holds("blocks" not in no_blocks and no_blocks["plants"] == ["g-030"], "S5's first file names no rule")
    holds(unbuilt["blocks"]["g-030"] not in {t["name"] for t in unbuilt["denied_topics"]}, "S5's second names an unbuilt rule")
    rules_errors = reader("src.validate.agent_rules", "rules_errors", "S5",
                          "nothing reads a plant's named rule in an agent repository")  # fmt: skip
    first = rules_errors(AGENT, rules=no_blocks)
    assert first and any("g-030" in e for e in first), first
    second = rules_errors(AGENT, rules=unbuilt)
    assert second and any("festival-embargo" in e for e in second), second


# --- the run file (made at PR 3; observed: null today) ----------------------------


@expected_failure
def test_the_plant_run_was_made():
    run = load_yaml(RUNS / "f9_3_plant_run.yaml")
    holds(isinstance(run, dict) and run.get("seed") == "run", "f9_3_plant_run.yaml is the run file")
    holds([s["id"] for s in run["steps"]] == ["first", "deploy", "second", "third"], "the run names its four steps")
    assert run["observed"] is not None, "seed run: the run has not been made"
