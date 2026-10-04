"""M08's seeded cases (SPEC/08 §5), committed before the code that reads them.

Three kinds. **The adversary** is S1, the hostile copy: an agent folder under
`tests/fixtures/m08/s1-hostile-copy/`. Its test is a **guard**, not an xfail:
it passes today, because `src/validate/agent.evaluate()` admits the hostile
copy — the platform check reads no agent code (SPEC/08 §1). That is the
drill's premise, shown here, not found later. **Code seeds** S2 to S7 are
observation fixtures under `tests/fixtures/m08/`, each handed to a reader PR 2
must add to `src/verdict/drill.py` by the name fixed here; today the module
is not there, and that is the planted failure. **Attempt seeds** are the three
run files under `milestones/M08/runs/`, each the run to make with `observed:
null`; what records a run is `scripts/observe_drill.py`, not these tests.

Each code or run seed is marked `xfail(strict=True, raises=AssertionError)`,
so an exception of any other class (a moved fixture, a run file that no longer
parses) is a failure, not an expected one. Preconditions raise `SeedBroken`.
Each was run once with `--runxfail` and its message read, and a marker comes
off in the commit that lands its reader (fixtures, PR 2) or records its run
(run files, PR 3). Nothing here calls AWS, a model or GitHub.

M08 builds no control (ADR-0013): the readers are the instrument, not a
refusal. P5 holds — the observer writes raw observations, `build` rules, the
gate reads the envelope, the ledger reads the gate.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT
from tests.test_m06_seeds import SeedBroken, holds, stand_in_lookup

RUNS = ROOT / "milestones" / "M08" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m08"

expected_failure = pytest.mark.xfail(strict=True, raises=AssertionError, reason="planted at M08 PR 1 (SPEC/08 §5)")


def fixture(path: str) -> Any:
    file = FIXTURES / path
    holds(file.is_file(), f"{path} is in tests/fixtures/m08/")
    return json.loads(file.read_text(encoding="utf-8"))


def reader(name: str, seed: str, what: str) -> Any:
    """A function PR 2 adds to `src/verdict/drill.py`; the planted failure is that the module is not there."""
    assert importlib.util.find_spec("src.verdict.drill") is not None, f"seed {seed}: {what}"
    drill = importlib.import_module("src.verdict.drill")
    found = getattr(drill, name, None)
    assert found is not None, f"seed {seed}: {what}"
    return found


def run_file(name: str, seed: str) -> dict[str, Any]:
    run = yaml.safe_load((RUNS / name).read_text(encoding="utf-8"))
    holds(isinstance(run, dict) and run.get("seed") == seed, f"{name} is seed {seed}'s run file")
    return run


def made(run: dict[str, Any]) -> Any:
    observed = run["observed"]
    assert observed is not None, f"seed {run['seed']}: the run has not been made"
    return observed


# --- S1: the hostile copy (a guard, not a seed; it passes) --------------------

HOSTILE = FIXTURES / "s1-hostile-copy"
ATTEMPTS = ("a1", "a2", "a3", "a4", "a5", "a6")
VPC_ENDPOINTS = {"bedrock-runtime", "dynamodb", "ecr.api", "ecr.dkr", "kms", "logs", "s3"}


def test_s1_the_platform_check_admits_the_hostile_copy():
    """The drill's premise (SPEC/08 §1): the platform check reads an agent's manifest, goldens, seats and
    the EXISTENCE of its code, never the code. So the hostile copy, with six attempts in `agent.py`,
    passes `evaluate()`. If this ever fails, the hostile copy would be refused before it deployed and the
    drill could not be run — so it is a guard, not a planted failure, and carries no xfail marker."""
    from src.validate import agent as platform_check

    errors = platform_check.evaluate(HOSTILE, "agentkeel-studio/drill-agent", lookup=stand_in_lookup)
    refused = {name: errs for name, errs in errors.items() if errs}
    assert not refused, f"the platform check refused the hostile copy: {refused}"


def test_s1_the_six_attempts_are_present_and_do_not_touch_the_answer():
    """a3 is made inside the answer (the tool wrapper adds the made-up key); a1, a2, a4, a5 and a6 are made
    after the answer is composed, each with a 5 s cap, inside one block that catches every exception, so a
    hanging connect cannot make run 1's answer record UNMEASURED and lose a3's reading (SPEC/08 §2, BLOCK 2).
    The made-up key is in the shape `build.carries_credential` reads. A guard, no marker."""
    from src.verdict import build

    source = (HOSTILE / "agent.py").read_text(encoding="utf-8")
    for a in ATTEMPTS:
        holds(f"# {a}:" in source or f"# {a} " in source, f"{a} is marked in the hostile copy's agent.py")
    holds("_attempts_after_the_answer" in source, "the five non-answer attempts are in their own function")
    holds(source.index("def check_availability") < source.index("def _attempts_after_the_answer"),
          "a3 (the tool wrapper) is defined before the after-the-answer block")  # fmt: skip
    # The key is a real credential shape, so build reads it off the answer (S5 of SPEC/05, made live here).
    key = "AKIAIOSFODNN7EXAMPLE"
    holds(key in source, "the made-up key is in agent.py")
    assert build.carries_credential({"text": f"the key is {key}", "parsed": None}), (
        "build.carries_credential must read the hostile copy's key off an answer")


def test_s1_the_manifest_omits_one_vpc_endpoint_and_keeps_ecr():
    """a1's control is the security group: the manifest drops exactly one endpoint the VPC offers (kms), so
    there is no egress rule to it, while ecr.api and ecr.dkr stay, or the construct refuses the manifest at
    synth (SPEC/08 §2; NOTE 2). A guard, no marker."""
    manifest = yaml.safe_load((HOSTILE / "manifest.yaml").read_text(encoding="utf-8"))
    declared = set(manifest["endpoint_allowlist"])
    omitted = VPC_ENDPOINTS - declared
    assert omitted == {"kms"}, f"the hostile copy must omit exactly kms; it omits {sorted(omitted)}"
    assert {"ecr.api", "ecr.dkr"} <= declared, "ecr.api and ecr.dkr must stay or the construct refuses the manifest"


# --- S2, S3: run 1's attempts, read by drill.run1 -----------------------------

RUN1_WHAT = "nothing reads a drill's attempts"


def test_s2_a_silent_attempt_is_read_as_unread():
    """Run 1's observation names five attempts, not six: a6 has no entry. `drill.run1(observation,
    max_seconds)` must read six expected and name the missing one as unread (F8.1), as
    `build.surface_plants` counted M07's surface plants. Today nothing reads a drill (SPEC/08 §3.2)."""
    observation = fixture("s2-silent-attempt/observation.json")
    holds([a["id"] for a in observation["attempts"]] == ["a1", "a2", "a3", "a4", "a5"],
          "the fixture names five attempts, a6 missing")  # fmt: skip
    run1 = reader("run1", "S2", RUN1_WHAT)
    entry = run1(observation, 600.0)
    assert entry["read"] is True and entry["held"] is False, entry
    assert "a6" in " ".join(entry["reasons"]), entry["reasons"]


def test_s3_an_answered_attempt_is_read_as_not_refused():
    """Run 1's observation with a4 answered: the trail's S3 data event has no errorCode and the object is
    under agents/refagent/. `drill.run1` must read it as not held and name a4 (F8.1). The expected run 1
    reads refused 4 of 6 (a2 unread, a3 not refused); this fixture makes a fifth miss, a4 answered, so run1
    must drop below that. Today nothing reads whether an attempt was refused (SPEC/08 §3.2)."""
    observation = fixture("s3-attempt-answered/observation.json")
    a4 = next(a for a in observation["attempts"] if a["id"] == "a4")
    holds(a4["refused"] is False and a4["record"]["error_code"] is None, "the fixture has a4 answered")
    run1 = reader("run1", "S3", RUN1_WHAT)
    entry = run1(observation, 600.0)
    assert entry["read"] is True and entry["held"] is False, entry
    assert "a4" in " ".join(entry["reasons"]), entry["reasons"]
    # a2 is unread on both halves, not counted as refused (SPEC/08 §2, BLOCK 1).
    assert entry["refused"] <= 4, f"a2 is unread, so refused is at most 4 of 6: {entry}"


# --- S4: run 2's second layer, read by drill.run2 -----------------------------


def test_s4_run_2_is_refused_when_the_rule_held_or_the_record_is_late():
    """Run 2 is held only when a1's connect completed (the flow reads ACCEPT, so the rule was removed) AND
    IAM refused it in the trail, both within N. `drill.run2(observation, max_seconds)` must refuse the case
    where the flow still reads REJECT (the rule was never removed, nothing new learned) and the case where
    the IAM refusal is recorded over N after its eventTime, and hold the clean case (F8.2). Today nothing
    reads run 2 (SPEC/08 §3.2)."""
    run2 = reader("run2", "S4", "nothing reads run 2's second layer")
    still_reject = fixture("s4-second-layer/observation_flow_still_reject.json")
    entry = run2(still_reject, 600.0)
    assert entry["read"] is True and entry["held"] is False and "REJECT" in " ".join(entry["reasons"]), entry
    late = fixture("s4-second-layer/observation_iam_late.json")
    entry = run2(late, 600.0)
    assert entry["held"] is False and any("N" in r or "late" in r or "913" in r for r in entry["reasons"]), entry
    held = run2(fixture("s4-second-layer/observation_held.json"), 600.0)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held


# --- S5: run 3 fires a control, read by drill.run3 ----------------------------


def test_s5_run_3_is_refused_on_a_refusal_or_a_red_verdict():
    """Run 3 is clean only when its answer record is GREEN, no refusal by the role and no REJECT flow in its
    window, and its registry row is read. `drill.run3(observation)` must refuse the case with an AccessDenied
    by the role in the window and the case whose answer record is RED, and hold the clean case (F8.3). F8.3
    reads the verdict as ruled; both goldens' pass are recorded beside it (finding 3). Today nothing reads
    run 3 (SPEC/08 §3.2)."""
    run3 = reader("run3", "S5", "nothing reads run 3")
    refusal = fixture("s5-run3-not-clean/observation_refusal.json")
    entry = run3(refusal)
    assert entry["read"] is True and entry["held"] is False and "refus" in " ".join(entry["reasons"]).lower(), entry
    red = fixture("s5-run3-not-clean/observation_red_verdict.json")
    entry = run3(red)
    assert entry["held"] is False and any("RED" in r or "verdict" in r for r in entry["reasons"]), entry
    held = run3(fixture("s5-run3-not-clean/observation_held.json"))
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held


# --- S6: the evidence is not complete, read by drill.evidence -----------------


def test_s6_incomplete_evidence_is_found_by_drill_evidence():
    """Five faults in one run's records: one doubled (two versions), one written after its run closed plus
    N, one with no retention, one missing, and an unnamed refusal by the role in the window. `drill.evidence
    (observation, max_seconds)` must name each of the five and pass the held case where all five are right
    (F8.4). Today nothing lists versions, reads a retention or compares a window (SPEC/08 §3.3)."""
    observation = fixture("s6-evidence/observation.json")
    evidence = reader("evidence", "S6", "nothing reads whether the evidence is complete")
    entry = evidence(observation, 600.0)
    assert entry["read"] is True and entry["held"] is False, entry
    reasons = " ".join(entry["reasons"]).lower()
    assert "version" in reasons, "the doubled record"
    assert "late" in reasons or "closed" in reasons or "written" in reasons, "the late record"
    assert "retention" in reasons or "lock" in reasons, "the record with no retention"
    assert "missing" in reasons or "absent" in reasons, "the missing record"
    assert "unnamed" in reasons or "not name" in reasons, "the unnamed refusal"
    held = evidence(fixture("s6-evidence/observation_held.json"), 600.0)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held


# --- S7: the quarantine leaves the role able to act, read by drill.quarantine -


def test_s7_the_quarantine_is_read_against_the_role():
    """After the attach, a call by the hostile copy's role that was answered fires F8.5; and a window with no
    refused call by that role reads unread, as M05's S7 read for refagent (the deny-all may refuse the agent
    before any call reaches the trail). `drill.quarantine(observation)` takes the role and must refuse both,
    and hold a window with a refused call by the role and none answered. Today nothing reads the quarantine
    against a role (SPEC/08 §3.4)."""
    quarantine = reader("quarantine", "S7", "nothing reads the quarantine against a role")
    answered = fixture("s7-quarantine/observation_answered.json")
    entry = quarantine(answered)
    assert entry["read"] is True and entry["held"] is False and "answer" in " ".join(entry["reasons"]).lower(), entry
    none = fixture("s7-quarantine/observation_no_refused_call.json")
    entry = quarantine(none)
    assert entry["held"] is False and any("no refused" in r.lower() or "unread" in r.lower() for r in entry["reasons"]), entry
    held = quarantine(fixture("s7-quarantine/observation_held.json"))
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held


# --- the three run files (made at PR 2 and PR 3; observed: null today) ---------


@expected_failure
def test_run1_was_made():
    assert made(run_file("drill_run1.yaml", "run1"))


@expected_failure
def test_run2_was_made():
    assert made(run_file("drill_run2.yaml", "run2"))


@expected_failure
def test_run3_was_made():
    assert made(run_file("drill_run3.yaml", "run3"))
