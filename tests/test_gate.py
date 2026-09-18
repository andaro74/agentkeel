"""verdict.gate: the regression bar (P7, R2), the plant rule, checks."""

from __future__ import annotations

import json

import pytest

from src.verdict import ROOT, gate, load_golden_kinds, plants

from .conftest import GOLDENS_DIR, URL

KINDS = load_golden_kinds(GOLDENS_DIR)


def judged(envelope_path, history=None, plant_ids=()):
    return gate.judge(gate.read(envelope_path), KINDS, history or {}, list(plant_ids))


def test_empty_history_nothing_gates(chain):
    """15 of 15 failing, none has ever passed: reported, not RED. passed == total is not a gate."""
    envelope_path, _, _ = chain()
    envelope = gate.read(envelope_path)
    assert len(envelope["never_passed"]) == 15 and envelope["regressed"] == []
    assert judged(envelope_path) == ("GREEN", [])
    assert gate.main([str(envelope_path), "--history-dir", str(envelope_path.parent / "none")]) == 0


def test_a_golden_that_passed_before_and_fails_now_is_red(chain):
    envelope_path, _, _ = chain(right={"g-001"})
    assert judged(envelope_path, {"g-001": [("b" * 40, True)]})[0] == "GREEN"  # still passing
    verdict, reasons = judged(envelope_path, {"g-002": [("b" * 40, False), ("c" * 40, True)]})
    assert verdict == "RED"
    assert "regressed: g-002 has passed before and fails now" in reasons


def test_a_golden_that_has_only_ever_failed_does_not_gate(chain):
    envelope_path, _, _ = chain()
    assert judged(envelope_path, {"g-002": [("b" * 40, False)]})[0] == "GREEN"


def test_plants_expected_is_zero_at_m00():
    assert plants.CONTROLS == {}
    assert plants.plant_ids(KINDS, ROOT) == []


def test_the_plant_rule_counts_a_plant_once_its_control_exists(monkeypatch):
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "no/such/control"})
    assert plants.plant_ids(KINDS, ROOT) == []
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "Makefile"})  # any path that exists
    assert plants.plant_ids(KINDS, ROOT) == ["g-013", "g-014", "g-015"]


def test_a_silent_plant_is_red(chain):
    envelope_path, _, _ = chain()  # built with plants_expected = 0
    verdict, reasons = judged(envelope_path, plant_ids=["g-013", "g-014", "g-015"])
    assert verdict == "RED"
    assert "silent plant: expected 3, fired 0" in reasons
    assert "envelope says plants_expected=0, the plant rule gives 3" in reasons


def test_a_failed_check_is_red(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["checks"] = {"F0_2": {"status": "pass", "url": URL}, "F0_3": {"status": "fail", "url": URL}}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    verdict, reasons = judged(envelope_path)
    assert verdict == "RED" and f"check F0_3 failed: {URL}" in reasons


def test_a_flipped_pass_is_rejected_against_the_card(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["goldens"]["g-010"] |= {"score": True, "pass": True}
    envelope["never_passed"].remove("g-010")
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="differ from the baseline card"):
        gate.read(envelope_path)


def test_a_dropped_golden_is_red(chain):
    envelope_path, _, _ = chain()
    verdict, reasons = gate.judge(gate.read(envelope_path), {**KINDS, "g-016": "redteam"}, {}, [])
    assert verdict == "RED" and "the envelope's goldens are not the goldens in the tree" in reasons


def test_measured_is_what_the_ledger_cell_must_say(chain):
    envelope_path, _, _ = chain(right={"g-001", "g-012"})
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "traps 1/3 (g-012); ordinary 1/9; guardrail 0/3; never_passed 13; regressed 0; "
        f"plants 0/0; GREEN; envelope `{'a' * 40}`"
    )


def test_a_bad_history_file_is_rejected_not_red(chain, capsys):
    envelope_path, _, _ = chain()
    (envelope_path.parent / f"{'b' * 40}.json").write_text("{}", encoding="utf-8")
    assert gate.main([str(envelope_path), "--history-dir", str(envelope_path.parent)]) == 2
    assert "history cannot be replayed" in capsys.readouterr().out
