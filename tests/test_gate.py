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
    envelope_path, _, _ = chain(right={"g-010"})
    envelope = gate.read(envelope_path)
    assert {r["scope"] for r in envelope["goldens"].values()} == {"control"}
    assert len(envelope["goldens"]) == 15


def test_the_control_is_never_gated(chain, past, capsys):
    """The control passed g-001 and g-010 once and fails both now. Reported, noted, not RED."""
    history_dir = past(right={"g-001", "g-010"}, agent=False)
    envelope_path, _, _ = chain(history_dir=history_dir)
    envelope = gate.read(envelope_path)
    assert envelope["regressed"] == [] and envelope["verdict"] == "GREEN"
    assert "g-001" not in envelope["never_passed"]  # it has passed; it is not regressed either
    assert gate.rule(envelope_path, history_dir) == ("GREEN", [])
    assert gate.main([str(envelope_path), "--history-dir", str(history_dir)]) == 0
    out = capsys.readouterr().out
    assert "note: control g-001 has passed before and fails now; not gated (Finding F0.4)" in out
    assert "note: control g-010" in out


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
    assert envelope["goldens"]["g-001"] == {"kind": "ordinary", "scope": "agent", "score": True, "cites": True, "pass": True}
    for result in envelope["goldens"].values():
        result["scope"] = "control"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="a control envelope's base is its own card"):
        gate.read(envelope_path)
    # and without the M01 fields, it is an M00 envelope whose base is another commit's card
    for field in ("control_card_ref", "tokens_in"):
        del envelope[field]
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="claim 1 is read on an agent envelope only"):
        gate.read(envelope_path)
    for name in gate.CLAIM_1_CHECKS:  # and without them, its base is another commit's card
        envelope["checks"].pop(name, None)
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="baseline card is for 9407615"):
        gate.read(envelope_path)


def test_a_control_envelope_carries_no_claim_1_check(chain):
    """Cold review F4: with no agent under test, an envelope says nothing about claim 1."""
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["checks"]["F1_1"] = {"status": "pass", "url": URL}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="claim 1 is read on an agent envelope only"):
        gate.read(envelope_path)


def test_one_subject_per_envelope(chain):
    envelope_path, _, _ = chain(agent=True)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["goldens"]["g-001"]["scope"] = "control"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="one subject"):
        gate.read(envelope_path)


@pytest.mark.parametrize("field", ["control_card_ref", "tokens_in"])
def test_an_agent_envelope_needs_both_m01_fields(chain, field):
    """Not required by the schema, so M00's envelopes validate; required of an agent envelope by the gate."""
    envelope_path, _, _ = chain(agent=True)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    del envelope[field]
    assert gate.schema_errors(envelope) == []
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match=f"without {field}"):
        gate.read(envelope_path)


def test_an_agent_envelope_on_another_base_is_rejected(chain):
    envelope_path, card_path, _ = chain(agent=True)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["baseline_card_ref"] = envelope["control_card_ref"]  # this run's card as the base: the base moves
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="not the card at tag m00"):
        gate.read(envelope_path)


def test_an_altered_control_card_is_rejected(chain):
    envelope_path, card_path, _ = chain(agent=True)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card_path.write_text(json.dumps({**card, "tokens_out": 1}), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="control_card_ref .* is not the one the envelope names"):
        gate.read(envelope_path)


def test_the_gate_reads_f1_4_for_itself(chain):
    """P5: build wrote pass and checks.F1_4; the gate works both out again from score and cites."""
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    assert gate.rule(envelope_path, envelope_path.parent / "none")[0] == "GREEN"
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    assert envelope["checks"]["F1_4"]["status"] == "pass"

    envelope["goldens"]["g-001"]["cites"] = False  # an uncited answer that build called a pass
    verdict, reasons = gate.judge(envelope, KINDS, {}, [])
    assert verdict == "RED"
    assert "g-001: pass is not score and cites (F1.4)" in reasons
    assert "envelope says F1_4 is pass, the gate reads fail" in reasons

    del envelope["checks"]["F1_4"]
    assert "checks.F1_4 is missing from an agent envelope" in gate.judge(envelope, KINDS, {}, [])[1]


def test_over_the_cap_is_red_in_the_gate_too(chain):
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert gate.judge(envelope, KINDS, {}, [], cap=9000) == ("GREEN", [])
    verdict, reasons = gate.judge(envelope, KINDS, {}, [], cap=8999)
    assert verdict == "RED"
    assert "cost-cap: 9000 over 8999" in reasons
    assert "build said GREEN, the gate says RED" in reasons


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
    envelope_path, _, _ = chain(right={"g-001", "g-010"})
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "control: traps 1/3 (g-010); ordinary 1/9; guardrail 0/3; mode control; never_passed 13; regressed 0; "
        f"plants 0/0; GREEN; envelope `{'a' * 40}`"
    )
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "agent: traps 0/3; ordinary 1/9; guardrail 0/3; control: traps 0/3; ordinary 0/9; guardrail 0/3; mode runner; "
        f"never_passed 14; regressed 0; plants 0/0; F1_1 pass {URL}; F1_2 pass {URL}; F1_3 pass {URL}; "
        f"F1_4 pass {URL}; GREEN; envelope `{'a' * 40}`; base b0219756"
    )


def test_a_bad_history_file_is_rejected_not_red(chain, capsys):
    envelope_path, _, _ = chain()
    (envelope_path.parent / f"{'b' * 40}.json").write_text("{}", encoding="utf-8")
    assert gate.main([str(envelope_path), "--history-dir", str(envelope_path.parent)]) == 2
    assert "history cannot be replayed" in capsys.readouterr().out


def test_the_cap_is_the_one_that_stood_at_the_envelopes_commit():
    """Ruling m: a later cap change does not re-rule an old envelope.

    `55dadb2` is M00's last envelope commit. `thresholds.yaml` said 20000
    there and says 150000 in the tree; the gate reads 20000 for it.
    """
    m00 = "55dadb2f221e60036bdba0b01fdb6eff025d74bc"
    assert gate.cap_at(m00) == (20000, "55dadb2f221e, the envelope's own commit")
    assert gate.thresholds(gate.THRESHOLDS)["cost_cap"]["tokens_per_run"] == 150000
    # A commit git cannot resolve falls back to the tree, and says so.
    assert gate.cap_at("a" * 40) == (150000, "the working tree")
