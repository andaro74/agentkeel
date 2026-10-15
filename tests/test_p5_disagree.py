"""P5: instruments never read their own claim. The runner, build and the gate can disagree.

If any of these three ever takes the word of the one before it, a test here fails.
The disagreements are about an agent under test: the control is never gated (ADR-0004),
so there is nothing for build and the gate to disagree about on a control run.
"""

from __future__ import annotations

import json

from src.verdict import build, gate, load_golden_kinds, replay_history

from .conftest import COMMIT, GOLDENS_DIR, make_raw


def test_the_runner_says_pass_and_build_says_fail(goldens):
    raw = make_raw(goldens)  # every answer wrong
    for observation in raw["observations"]:
        observation |= {"pass": True, "score": True, "scope": "control", "verdict": "GREEN"}  # the runner's own claims
    results = build.score_all(raw, goldens, *build.load_citables(build.ROOT))
    assert not any(result["pass"] for result in results.values())
    assert not any("scope" in result for result in results.values())  # scope is build's to work out


def test_build_says_green_and_the_gate_says_red(chain):
    # build sees no history: g-001 fails, has never passed, does not gate. GREEN.
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    assert "g-001" in envelope["never_passed"]

    # the gate sees a history in which the agent passed g-001.
    history: replay_history.History = {("agent", "g-001"): [("b" * 40, True)]}
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), history, [])
    assert verdict == "RED"
    assert "regressed: g-001 has passed before and fails now" in reasons
    assert "build said GREEN, the gate says RED" in reasons


def test_all_three_disagree_in_one_chain(chain, past, goldens):
    # A past envelope, written by build, in which the agent passed everything ordinary.
    ordinary = {g for g, golden in goldens.items() if golden["kind"] == "ordinary"}
    history_dir = past(right=ordinary, agent=True)

    # Now: the runner claims success, build scores every answer wrong and is
    # kept from the history, the gate reads the history.
    envelope_path, _, _ = chain(agent=True, runner_says="15/15 GREEN")
    assert gate.read(envelope_path)["verdict"] == "GREEN"  # build: nothing has ever passed
    verdict, reasons = gate.rule(envelope_path, history_dir)
    assert verdict == "RED"
    assert sum(reason.startswith("regressed: ") for reason in reasons) == len(ordinary)


def test_a_hand_edited_verdict_does_not_carry(chain, past, goldens):
    ordinary = {g for g, golden in goldens.items() if golden["kind"] == "ordinary"}
    history_dir = past(right=ordinary, agent=True)

    envelope_path, _, _ = chain(agent=True, history_dir=history_dir)  # build sees the history: RED
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert envelope["verdict"] == "RED" and envelope["commit"] == COMMIT

    envelope |= {"verdict": "GREEN", "regressed": [], "never_passed": envelope["never_passed"] + envelope["regressed"]}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    verdict, reasons = gate.rule(envelope_path, history_dir)
    assert verdict == "RED"
    assert any(reason.startswith("envelope says regressed=[]") for reason in reasons)


# --- M04 PR 2 (SPEC/04 §4, P5): a case for each new check ---------------------


def test_the_runner_says_grounded_and_build_says_not(goldens):
    """S1's reading: a right answer that says it used the tool, with no successful call, is not correct for the agent."""
    raw = make_raw(goldens, right={"g-001"})
    g001 = next(o for o in raw["observations"] if o["id"] == "g-001")
    g001["tool_calls"] = [{**g001["tool_calls"][0], "status": "error"}]  # the schema refused it
    g001["grounded"] = True  # the runner's own claim
    results = build.score_all(raw, goldens, *build.load_citables(build.ROOT))
    assert results["g-001"]["grounded"] is False
    assert build.as_the_agent_is_scored(results)["g-001"]["pass"] is False


def test_build_says_f4_4_pass_and_the_gate_reads_the_bar(chain):
    """S4's reading: build wrote F4_4 pass; the gate's own reading of the bars says the run is over."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    envelope["checks"]["F4_4"] = {"status": "pass", "url": envelope["checks"]["F1_4"]["url"]}
    over = ["F4_4: p95_ms 1500 is 3.00x the incumbent's median 500 over 3 envelopes (fixture), over relative.p95_ratio_max 2.0"]
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], bars=over)
    assert verdict == "RED"
    assert over[0] in reasons
    assert "envelope says F4_4 is pass, the gate reads fail" in reasons
    assert "build said GREEN, the gate says RED" in reasons
    # and at a commit with bars, an envelope with no F4_4 is not one that passed it
    del envelope["checks"]["F4_4"]
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], bars=[])
    assert verdict == "RED" and any("checks.F4_4 is missing" in reason for reason in reasons)


def test_build_says_f4_3_pass_and_the_gate_reads_a_vs_a(chain):
    """S3's reading: an a_vs_a that names a golden cannot stand beside F4_3 pass, and neither stands alone."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    url = envelope["checks"]["F1_4"]["url"]
    kinds = load_golden_kinds(GOLDENS_DIR)
    flaky = {**envelope, "a_vs_a": {"agent": ["g-006"], "control": None},
             "checks": {**envelope["checks"], "F4_3": {"status": "pass", "url": url}}}  # fmt: skip
    verdict, reasons = gate.judge(flaky, kinds, {}, [])
    assert verdict == "RED" and any("a_vs_a names ['g-006']" in reason for reason in reasons)
    alone = {**envelope, "a_vs_a": {"agent": [], "control": None}}
    assert "a_vs_a without checks.F4_3" in gate.judge(alone, kinds, {}, [])[1]
    unread = {**envelope, "checks": {**envelope["checks"], "F4_3": {"status": "pass", "url": url}}}
    assert any("without a_vs_a" in reason for reason in gate.judge(unread, kinds, {}, [])[1])


def test_build_writes_no_claim_4_checks_and_the_gate_requires_them(chain):
    """F4_1, F4_2 and F4_4 from M04's readers, and F4_3 on a swap: build says GREEN without them, the gate does not."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_4_CHECKS + ("F4_3",)
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED"
    for name in ("F4_1", "F4_2", "F4_3", "F4_4"):
        assert f"checks.{name} is missing from an agent envelope" in reasons


def test_build_writes_no_claim_5_check_and_the_gate_requires_it(chain):
    """F5_1 from M05's readers (2c88265): build says GREEN without it, the gate does not (SPEC/05 section 4)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_5_CHECKS
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED" and "checks.F5_1 is missing from an agent envelope" in reasons


def test_the_gate_requires_f5_1_from_m05s_readers_and_not_before():
    assert "F5_1" in gate.required_checks("HEAD")
    assert "F5_1" not in gate.required_checks("5a5720e")  # M05 PR 1's merge, before the readers


def test_build_writes_no_claim_6_checks_and_the_gate_requires_them(chain):
    """F6_1 and F6_4 from M06's readers: build says GREEN without them, the gate does not (SPEC/06 section 4)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_6_CHECKS
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED"
    for name in ("F6_1", "F6_4"):
        assert f"checks.{name} is missing from an agent envelope" in reasons


def test_the_gate_requires_f6_1_and_f6_4_from_m06s_readers_and_not_before():
    assert {"F6_1", "F6_4"} <= set(gate.required_checks("HEAD"))
    assert "F6_1" not in gate.required_checks("ef7e48e")  # M06 PR 1's merge, before the readers


# --- M07 PR 2 (SPEC/07 §4, P5): a case for each new reading ---------------------


def test_the_observer_says_held_and_taken_and_build_reads_unread():
    """The observer writes raw records. A verdict it writes about itself is not one build reads."""
    from src.verdict import upgrade

    from .test_m07_upgrade import HISTORY, THRESHOLDS, observation

    seen = observation(held=True, taken={"n": 3, "of": 3}, F7_0={"read": True, "held": True})  # the observer's own claims
    seen["s2"] = {"held": True, "retirement": {"held": True, "read": True}}
    reading = upgrade.record(seen, THRESHOLDS, HISTORY)
    assert reading["taken"]["n"] == 0
    assert reading["F7_0"]["read"] is False and reading["F7_2"]["read"] is False and reading["F7_2"]["held"] is None


def test_build_holds_an_upgrade_and_row_7_reads_it_again_at_the_commits_bars():
    """build ruled on the bars it was given; the gate's row 7 reading holds each time again to the bars at
    the envelope's commit, and counts `taken` again from its kinds (tests/test_m07_envelope.py has the rest)."""
    from src.verdict import upgrade

    from .test_m07_upgrade import HISTORY, TEMPLATE, THRESHOLDS, full

    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    assert reading["F7_2"]["held"] is True and reading["taken"]["n"] == 3  # build: held, 3 of 3
    tighter = {"arrive_max_seconds": 4500.0, "deploy_max_seconds": 3600.0, "retire_max_seconds": 300.0}
    misses = gate.upgrade_misses({"upgrade": reading}, tighter, "the envelope's commit")
    assert "F7_2: build held 600 s, over the commit's bar 300 s" in misses  # the gate: not at this commit's bar
    forged = {**reading, "taken": {**reading["taken"], "n": 3, "retirement": None}}
    assert "taken: the envelope says 3, its three kinds count 2" in gate.upgrade_misses({"upgrade": forged}, tighter, "here")


def test_build_says_every_claim_7_check_passed_and_the_gate_still_requires_each(chain):
    """F7_0 to F7_5 come from tests the gate is not given. What it holds: none may be absent, and F7_5 may
    not say pass beside counts that differ (the silent-plant case is in tests/test_m07_envelope.py)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    carried = {**envelope, "checks": {**envelope["checks"], **{name: {"status": "pass", "url": "u"} for name in gate.CLAIM_7_CHECKS[:5]}}}
    verdict, reasons = gate.judge(carried, load_golden_kinds(GOLDENS_DIR), {}, [],
                                  required=gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_7_CHECKS)  # fmt: skip
    assert verdict == "RED" and "checks.F7_5 is missing from an agent envelope" in reasons


# --- M08 PR 2 (SPEC/08 §4, P5): a case for each new check ---------------------


def test_the_observer_claims_refused_and_build_reads_the_record():
    """observe_drill writes raw records; drill rules. An attempt the observer marked refused, whose record
    shows no error, is read as not refused by build, and run 1 names it (F8.1)."""
    from src.verdict import drill

    observation = {"attempts": [
        {"id": "a1", "refused": True, "record": {"found": True, "kind": "flow", "flow_action": "REJECT",
            "event_time": "2026-10-20T10:00:05Z", "last_modified": "2026-10-20T10:03:00Z"}},
        {"id": "a2", "refused": None, "record": {"found": False}},
        {"id": "a3", "refused": False, "record": {"found": True, "kind": "answer"}},
        {"id": "a4", "refused": True, "record": {"found": True, "kind": "trail", "error_code": None,  # the observer lied
            "event_time": "2026-10-20T10:00:06Z", "last_modified": "2026-10-20T10:04:00Z"}},
        {"id": "a5", "refused": True, "record": {"found": True, "kind": "trail", "error_code": "AccessDenied",
            "event_time": "2026-10-20T10:00:07Z", "last_modified": "2026-10-20T10:04:30Z"}},
        {"id": "a6", "refused": True, "record": {"found": True, "kind": "trail", "error_code": "AccessDenied",
            "event_time": "2026-10-20T10:00:08Z", "last_modified": "2026-10-20T10:05:00Z"}},
    ]}
    entry = drill.run1(observation, 600.0)
    assert entry["held"] is False and "a4" in " ".join(entry["reasons"])
    assert entry["refused"] == 3  # a1, a5, a6: a4's record shows no error, whatever the observer wrote


def test_build_writes_no_claim_8_checks_and_the_gate_requires_them(chain):
    """F8_1 to F8_5 from M08's readers: build says GREEN without them, the gate does not (SPEC/08 §4)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_8_CHECKS
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED"
    for name in ("F8_1", "F8_2", "F8_3", "F8_4", "F8_5"):
        assert f"checks.{name} is missing from an agent envelope" in reasons


def test_build_holds_a_drill_and_row_8_reads_it_again_at_the_commits_n():
    """build ruled the drill on the N it was given; the gate's row 8 reading holds the counts and each run
    again, and the two known misses (a2 unread, a3 not refused) keep run 1 short of six, so row 8 is RED."""
    import json

    from src.verdict import drill

    observation = {"looked_up_at": "2026-10-20T10:30:00Z", "readable": True,
        "run1": json.loads((build.ROOT / "tests/fixtures/m08/s3-attempt-answered/observation.json").read_text()),
        "run2": json.loads((build.ROOT / "tests/fixtures/m08/s4-second-layer/observation_held.json").read_text()),
        "run3": json.loads((build.ROOT / "tests/fixtures/m08/s5-run3-not-clean/observation_held.json").read_text()),
        "evidence": json.loads((build.ROOT / "tests/fixtures/m08/s6-evidence/observation_held.json").read_text()),
        "quarantine": json.loads((build.ROOT / "tests/fixtures/m08/s7-quarantine/observation_held.json").read_text())}
    reading = drill.record(observation, 600.0)
    misses = gate.drill_misses({"drill": reading}, 600.0, "the envelope's commit")
    assert any("refused" in m and "of 6" in m for m in misses)  # short of six: row 8 RED
    # the gate reads N again: a drill read against another N is a miss
    assert any("read against N" in m for m in gate.drill_misses({"drill": reading}, 900.0, "here"))


def test_the_gate_requires_f8_checks_from_m08s_readers_and_not_before():
    assert {"F8_1", "F8_2", "F8_3", "F8_4", "F8_5"} <= set(gate.required_checks("HEAD"))
    assert "F8_1" not in gate.required_checks("1083722")  # M08 PR 1's merge, before the readers


# --- M09 PR 2 (SPEC/09 §4, P5): a case for each new check ---------------------


def test_the_observer_claims_fired_and_build_reads_the_trace():
    """observe_rules writes raw records; agent_rules rules. A plant the observer wrote as fired, whose observation
    shows another rule in the trace, is read as silent by build, and the reason names it (F9.3)."""
    from src.verdict import agent_rules

    record = {"guardrail": {"id": "fd7k2m9q1x0b", "version": "1"}, "fired": 1, "held": True,  # the observer's own claims
              "observations": {"g-030": {"stop_reason": "guardrail_intervened", "guardrail_topics": ["some-other-rule"],
                                         "parsed": None, "fired": True}}}  # fmt: skip
    reading = agent_rules.plants(record, {"g-030": "unannounced-selection-leak"})
    assert reading["fired"] == 0 and reading["held"] is False
    assert any("g-030" in r and "some-other-rule" in r for r in reading["reasons"])


def test_build_writes_no_claim_9_checks_and_the_gate_requires_them(chain):
    """F9_1 to F9_5 from M09's readers: build says GREEN without them, the gate does not (SPEC/09 §4)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_9_CHECKS
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED"
    for name in ("F9_1", "F9_2", "F9_3", "F9_4", "F9_5"):
        assert f"checks.{name} is missing from an agent envelope" in reasons


def test_build_says_f9_5_pass_and_the_gate_reads_its_own_plant_count(chain):
    """F9.5's second source is build's own count of refagent's plants; the gate counts again (P5): a pass beside
    a silent plant, or beside no plant, is read as a fail."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    url = envelope["checks"]["F1_4"]["url"]
    said = {**envelope, "checks": {**envelope["checks"], "F9_5": {"status": "pass", "url": url}}}
    kinds = load_golden_kinds(GOLDENS_DIR)
    verdict, reasons = gate.judge(said, kinds, {}, ["g-013"])  # g-013 fails in this fixture: a silent plant
    assert verdict == "RED" and "envelope says F9_5 is pass, the gate reads plants 0/1" in reasons
    verdict, reasons = gate.judge(said, kinds, {}, [])
    assert "envelope says F9_5 is pass, the gate reads plants 0/0" in reasons
    # and build's own join: a run whose plants are whole passes, one short of the controls' does not
    whole = build.both({"F9_5": {"status": "pass", "url": url}}, "F9_5", {"status": "pass", "url": url})
    assert whole["F9_5"]["status"] == "pass"
    assert build.both({"F9_5": {"status": "pass", "url": url}}, "F9_5", {"status": "fail", "url": url})["F9_5"]["status"] == "fail"


def test_build_holds_a_plant_run_and_row_9_reads_it_again():
    """build ruled the run; row 9's reading holds the top-level count to F9_3's own and n to m (P5)."""
    from src.verdict import agent_rules

    from .test_m09_readers import observation

    reading = agent_rules.record(observation())
    assert gate.rules_misses({"agent_rules": reading}) == []
    forged = {**reading, "F9_3": {**reading["F9_3"], "fired": 0}}
    misses = gate.rules_misses({"agent_rules": forged})
    assert any("the envelope says 1 of 1, F9_3 counts 0 of 1" in m for m in misses)
    assert "planted rules fired 0 of 1" in misses


def test_the_gate_requires_f9_checks_from_m09s_readers_and_not_before():
    assert {"F9_1", "F9_2", "F9_3", "F9_4", "F9_5"} <= set(gate.required_checks("HEAD"))
    assert "F9_1" not in gate.required_checks("460990b")  # M09 PR 1's merge, before the readers


# --- M10 PR 2 (SPEC/10 §4, P5): a case for each new check ---------------------


def test_the_observer_claims_admitted_and_build_reads_the_record():
    """observe_caller writes raw records; caller rules. A record the observer stepped as the admitted call whose
    line names another subject is read as naming a caller other than the one that called (F10.3)."""
    from src.verdict import caller

    from .test_m10_readers import access_lines
    from .test_m10_seeds import CALLERS, MAX_SECONDS, STATED

    line = {**access_lines()["lantern-desk"], "step": "admitted", "admitted": True}  # the observer's own claim
    line["raw"] = {**line["raw"], "subject": "box-office"}
    reading = caller.calls([{**caller.from_raw(line), "step": "admitted"}], STATED, CALLERS, MAX_SECONDS)
    assert reading["held"] is False and reading["admitted"] == 0
    assert any("other than the one that called: 'box-office'" in r for r in reading["reasons"])


def test_build_writes_no_claim_10_checks_and_the_gate_requires_them(chain):
    """F10_1 to F10_5 from M10's readers: build says GREEN without them, the gate does not (SPEC/10 §4)."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    required = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_10_CHECKS
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [], required=required)
    assert verdict == "RED"
    for name in ("F10_1", "F10_2", "F10_3", "F10_4", "F10_5"):
        assert f"checks.{name} is missing from an agent envelope" in reasons


def test_build_holds_a_caller_run_and_row_10_reads_it_again():
    """build ruled the run; row 10's reading holds the counts, N and refagent's plants again (P5)."""
    from src.verdict import caller

    from .test_m10_readers import observation
    from .test_m10_seeds import MAX_SECONDS

    reading = caller.record(observation(), MAX_SECONDS)
    envelope = {"caller": reading, "plants_fired": 7, "plants_expected": 7}
    assert gate.caller_misses(envelope, MAX_SECONDS, "the tree") == []
    forged = {**envelope, "caller": {**reading, "refused": 3, "F10_4": {**reading["F10_4"], "held": False, "reasons": ["x"]}}}
    assert any(m.startswith("F10_4 not held") for m in gate.caller_misses(forged, MAX_SECONDS, "the tree"))
    assert any("calls refused 2 of 3" in m for m in gate.caller_misses({**envelope, "caller": {**reading, "refused": 2}}, MAX_SECONDS, "x"))


def test_the_gate_requires_f10_checks_from_m10s_readers_and_not_before():
    from src import verdict

    if verdict.M10_READERS is None:
        assert "F10_1" not in gate.required_checks("HEAD")  # not yet named: the commit after the readers names it
        return
    assert {"F10_1", "F10_2", "F10_3", "F10_4", "F10_5"} <= set(gate.required_checks("HEAD"))
    assert "F10_1" not in gate.required_checks("a67de63")  # M10 PR 1's merge, before the readers
