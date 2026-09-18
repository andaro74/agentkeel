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
