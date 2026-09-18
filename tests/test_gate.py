"""verdict.gate: the regression bar (P7, R2), scope (ADR-0004), the plant rule, checks."""

from __future__ import annotations

import json

import pytest

from src.verdict import ROOT, gate, load_golden_kinds, plants

from .conftest import GOLDENS_DIR, URL

KINDS = load_golden_kinds(GOLDENS_DIR)
B, C = "b" * 40, "c" * 40


def judged(envelope_path, history=None, plant_ids=()):
    return gate.judge(gate.read(envelope_path), KINDS, history or {}, list(plant_ids))


def test_empty_history_nothing_gates(chain):
    """15 of 15 failing, none has ever passed: reported, not RED. passed == total is not a gate."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert len(envelope["never_passed"]) == 15 and envelope["regressed"] == []
    assert judged(envelope_path) == ("GREEN", [])
    assert gate.main([str(envelope_path), "--history-dir", str(envelope_path.parent / "none")]) == 0


def test_an_agent_golden_that_passed_before_and_fails_now_is_red(chain):
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    assert judged(envelope_path, {("agent", "g-001"): [(B, True)]})[0] == "GREEN"  # still passing
    verdict, reasons = judged(envelope_path, {("agent", "g-002"): [(B, False), (C, True)]})
    assert verdict == "RED"
    assert "regressed: g-002 has passed before and fails now" in reasons


def test_a_golden_that_has_only_ever_failed_does_not_gate(chain):
    envelope_path, _, _ = chain(agent=True)
    assert judged(envelope_path, {("agent", "g-002"): [(B, False)]})[0] == "GREEN"


# --- scope (ADR-0004) -----------------------------------------------------------


def test_at_m00_every_result_is_the_controls(chain):
    envelope_path, _, _ = chain(right={"g-012"})
    envelope = gate.read(envelope_path)
    assert {r["scope"] for r in envelope["goldens"].values()} == {"control"}
    assert len(envelope["goldens"]) == 15


def test_the_control_is_never_gated(chain, past, capsys):
    """The control passed g-001 and g-012 once and fails both now. Reported, noted, not RED."""
    history_dir = past(right={"g-001", "g-012"}, agent=False)
    envelope_path, _, _ = chain(history_dir=history_dir)
    envelope = gate.read(envelope_path)
    assert envelope["regressed"] == [] and envelope["verdict"] == "GREEN"
    assert "g-001" not in envelope["never_passed"]  # it has passed; it is not regressed either
    assert gate.rule(envelope_path, history_dir) == ("GREEN", [])
    assert gate.main([str(envelope_path), "--history-dir", str(history_dir)]) == 0
    out = capsys.readouterr().out
    assert "note: control g-001 has passed before and fails now; not gated (Finding F0.4)" in out
    assert "note: control g-012" in out


def test_the_controls_luck_is_not_the_agents_bar(chain):
    """History keys on (scope, id): a control pass on g-001 does not make an agent fail a regression."""
    envelope_path, _, _ = chain(agent=True)
    verdict, _ = judged(envelope_path, {("control", "g-001"): [(B, True)]})
    assert verdict == "GREEN"
    assert "g-001" in gate.read(envelope_path)["never_passed"]


def test_an_agent_cannot_call_itself_the_control(chain):
    """Relabel a regressed agent result as control to get out from under the bar: rejected."""
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert envelope["goldens"]["g-001"] == {"kind": "ordinary", "scope": "agent", "score": True, "cites": False, "pass": True}
    for result in envelope["goldens"].values():
        result["scope"] = "control"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="g-001 says scope control and differs from the baseline card"):
        gate.read(envelope_path)


def test_a_card_that_is_not_the_control_is_rejected(chain):
    envelope_path, card_path, _ = chain()
    card = json.loads(card_path.read_text(encoding="utf-8"))
    del card["scope"]
    card_path.write_text(json.dumps(card), encoding="utf-8")
    with pytest.raises(gate.Rejected):  # the hash no longer matches either; both must hold
        gate.read(envelope_path)


def test_scope_is_required_and_has_two_values(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["goldens"]["g-001"]["scope"] = "shadow"
    assert any("g-001/scope" in e for e in gate.schema_errors(envelope))
    del envelope["goldens"]["g-001"]["scope"]
    assert any("'scope' is a required property" in e for e in gate.schema_errors(envelope))


# --- plants -----------------------------------------------------------------------


def test_plants_expected_is_zero_at_m00():
    assert plants.CONTROLS == {}
    assert plants.plant_ids(KINDS, ROOT) == []


def test_the_plant_rule_counts_a_plant_once_its_control_exists(monkeypatch):
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "no/such/control"})
    assert plants.plant_ids(KINDS, ROOT) == []
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "Makefile"})  # any path that exists
    assert plants.plant_ids(KINDS, ROOT) == ["g-013", "g-014", "g-015"]


def test_a_silent_plant_is_red_for_the_agent_and_not_for_the_control(chain):
    three = ["g-013", "g-014", "g-015"]
    envelope_path, _, _ = chain(agent=True)  # built with plants_expected = 0
    verdict, reasons = judged(envelope_path, plant_ids=three)
    assert verdict == "RED"
    assert "silent plant: expected 3, fired 0" in reasons
    assert "envelope says plants_expected=0, the plant rule gives 3" in reasons

    # The baseline has no guardrail and never will. Its plants are not counted.
    envelope_path, _, _ = chain()
    assert judged(envelope_path, plant_ids=three) == ("GREEN", [])


# --- checks, tampering, the ledger cell ---------------------------------------------


def test_a_failed_check_is_red_whatever_the_scope(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["checks"] = {"F0_2": {"status": "pass", "url": URL}, "F0_3": {"status": "fail", "url": URL}}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    verdict, reasons = judged(envelope_path)
    assert verdict == "RED" and f"check F0_3 failed: {URL}" in reasons


def test_a_flipped_control_pass_is_rejected_against_the_card(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["goldens"]["g-010"] |= {"score": True, "pass": True}
    envelope["never_passed"].remove("g-010")
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="g-010 says scope control and differs"):
        gate.read(envelope_path)


def test_a_dropped_golden_is_red(chain):
    envelope_path, _, _ = chain()
    verdict, reasons = gate.judge(gate.read(envelope_path), {**KINDS, "g-016": "redteam"}, {}, [])
    assert verdict == "RED" and "the envelope's goldens are not the goldens in the tree" in reasons


def test_measured_is_what_the_ledger_cell_must_say(chain):
    envelope_path, _, _ = chain(right={"g-001", "g-012"})
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "control: traps 1/3 (g-012); ordinary 1/9; guardrail 0/3; never_passed 13; regressed 0; "
        f"plants 0/0; GREEN; envelope `{'a' * 40}`"
    )
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    assert gate.measured_at(envelope_path, envelope_path.parent).startswith(
        "agent: traps 0/3; ordinary 1/9; guardrail 0/3; never_passed 14; "
    )


def test_a_bad_history_file_is_rejected_not_red(chain, capsys):
    envelope_path, _, _ = chain()
    (envelope_path.parent / f"{'b' * 40}.json").write_text("{}", encoding="utf-8")
    assert gate.main([str(envelope_path), "--history-dir", str(envelope_path.parent)]) == 2
    assert "history cannot be replayed" in capsys.readouterr().out
