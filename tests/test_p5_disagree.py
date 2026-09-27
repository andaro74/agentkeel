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
