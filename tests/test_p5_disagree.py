"""P5: instruments never read their own claim. The runner, build and the gate can disagree.

If any of these three ever takes the word of the one before it, a test here fails.
"""

from __future__ import annotations

import json

from src.verdict import build, gate, load_golden_kinds, replay_history

from .conftest import COMMIT, GOLDENS_DIR, make_raw


def test_the_runner_says_pass_and_build_says_fail(goldens):
    raw = make_raw(goldens)  # every answer wrong
    for observation in raw["observations"]:
        observation |= {"pass": True, "score": True, "verdict": "GREEN"}  # the runner's own claim
    results = build.score_all(raw, goldens, *build.load_citables(build.ROOT))
    assert not any(result["pass"] for result in results.values())


def test_build_says_green_and_the_gate_says_red(chain, tmp_path):
    # build sees no history: g-001 fails, has never passed, does not gate. GREEN.
    envelope_path, _, _ = chain()
    envelope = gate.read(envelope_path)
    assert envelope["verdict"] == "GREEN"
    assert "g-001" in envelope["never_passed"]

    # the gate sees a history in which g-001 passed.
    history: replay_history.History = {"g-001": [("b" * 40, True)]}
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), history, [])
    assert verdict == "RED"
    assert "regressed: g-001 has passed before and fails now" in reasons
    assert "build said GREEN, the gate says RED" in reasons


def test_all_three_disagree_in_one_chain(chain, tmp_path, goldens):
    # A past envelope, written by build, in which everything ordinary passed.
    ordinary = {g for g, golden in goldens.items() if golden["kind"] == "ordinary"}
    past_path, _, _ = chain(right=ordinary)
    past = json.loads(past_path.read_text(encoding="utf-8"))
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    (history_dir / f"{'b' * 40}.json").write_text(json.dumps({**past, "commit": "b" * 40}), encoding="utf-8")

    # Now: the runner claims success, build scores every answer wrong and is
    # kept from the history, the gate reads the history.
    envelope_path, _, _ = chain(runner_says="15/15 GREEN")
    assert gate.read(envelope_path)["verdict"] == "GREEN"  # build: nothing has ever passed
    verdict, reasons = gate.rule(envelope_path, history_dir)
    assert verdict == "RED"
    assert sum(reason.startswith("regressed: ") for reason in reasons) == len(ordinary)


def test_a_hand_edited_verdict_does_not_carry(chain, tmp_path, goldens):
    ordinary = {g for g, golden in goldens.items() if golden["kind"] == "ordinary"}
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    past_path, _, _ = chain(right=ordinary)
    past = json.loads(past_path.read_text(encoding="utf-8"))
    (history_dir / f"{'b' * 40}.json").write_text(json.dumps({**past, "commit": "b" * 40}), encoding="utf-8")

    envelope_path, _, _ = chain(history_dir=history_dir)  # build sees the history: RED
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert envelope["verdict"] == "RED" and envelope["commit"] == COMMIT

    envelope |= {"verdict": "GREEN", "regressed": [], "never_passed": envelope["never_passed"] + envelope["regressed"]}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    verdict, reasons = gate.rule(envelope_path, history_dir)
    assert verdict == "RED"
    assert any(reason.startswith("envelope says regressed=[]") for reason in reasons)
