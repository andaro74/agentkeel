"""verdict.gate: the regression bar (P7, R2), scope (ADR-0004), the plant rule, checks."""

from __future__ import annotations

import json
import subprocess

import pytest

from src.verdict import ROOT, gate, load_golden_kinds, plants, text_at

from .conftest import GOLDENS_DIR, URL

KINDS = load_golden_kinds(GOLDENS_DIR)
B, C = "b" * 40, "c" * 40


def judged(envelope_path, history=None, plant_ids=()):
    return gate.judge(gate.read(envelope_path), KINDS, history or {}, list(plant_ids))


def test_empty_history_nothing_gates(chain):
    """20 of 20 failing, none has ever passed: reported, not RED. passed == total is not a gate."""
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert len(envelope["never_passed"]) == 20 and envelope["regressed"] == []
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
    assert len(envelope["goldens"]) == 20


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
    with pytest.raises(gate.Rejected, match="claims 1 and 2 are read on an agent envelope only"):
        gate.read(envelope_path)
    for name in gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS:  # and without them, its base is another commit's card
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
    with pytest.raises(gate.Rejected, match="claims 1 and 2 are read on an agent envelope only"):
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


# --- claim 2's checks, from M02 PR 2's merge (SPEC/02 §4; M02 PR 3) ------------------


def test_the_claim_2_constant_is_pr_2s_merge_commit_on_main():
    """The commit the checks are required from is #12's merge commit, and it is on main."""
    shown = subprocess.run(["git", "show", "-s", "--format=%P %s", gate.M02_PR2_MERGE], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()  # fmt: skip
    assert len(shown) >= 2 and len(shown[0]) == 40 and len(shown[1]) == 40, "a merge commit has two parents"
    assert "#12" in " ".join(shown)
    assert subprocess.run(["git", "merge-base", "--is-ancestor", gate.M02_PR2_MERGE, "origin/main"], cwd=ROOT).returncode == 0


def test_an_agent_envelope_after_pr_2s_merge_must_carry_claim_2s_checks(chain):
    """Before the merge: claim 1's four. From it: those and F2_1, F2_2. A commit git cannot place: held to both."""
    before = "e97125e970ccfc6d044612eb006cdbdbcdb99337"  # M01's Measured envelope, an ancestor of the merge
    assert gate.required_checks(before) == gate.CLAIM_1_CHECKS
    assert gate.required_checks(gate.M02_PR2_MERGE) == gate.CLAIM_1_CHECKS
    m03_open = "d2d1e6de29d85d2e566afb913c46c7780ec3467c"  # after the merge, before M03's readers
    assert gate.required_checks(m03_open) == gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS
    assert gate.required_checks("a" * 40) == gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS

    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert envelope["checks"]["F2_1"]["status"] == "pass" and envelope["checks"]["F2_2"]["status"] == "pass"
    assert gate.rule(envelope_path, envelope_path.parent / "none") == ("GREEN", [])
    for name in gate.CLAIM_2_CHECKS:
        forgot = json.loads(json.dumps(envelope))
        del forgot["checks"][name]
        assert f"checks.{name} is missing from an agent envelope" not in gate.judge(forgot, KINDS, {}, [])[1]  # claim 1 alone
        verdict, reasons = gate.judge(forgot, KINDS, {}, [], required=gate.required_checks("a" * 40))
        assert verdict == "RED" and f"checks.{name} is missing from an agent envelope" in reasons


def test_an_agent_envelope_from_m03s_readers_must_carry_claim_3s_checks():
    """SPEC/03 section 4: F3_1, F3_2, F3_3, F3_5, F3_6, from f82a02a (the last reader) and every descendant."""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    everything = gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_3_CHECKS
    assert gate.required_checks(head) == everything
    assert gate.required_checks(gate.M03_READERS) == everything
    assert gate.CLAIM_3_CHECKS == ("F3_1", "F3_2", "F3_3", "F3_5", "F3_6")
    envelope = json.loads((ROOT / "evals" / "history" / "8033c2a7a0588e557df577464c190e64a435e88a.json")
                          .read_text(encoding="utf-8"))  # fmt: skip
    kinds = {g: r["kind"] for g, r in envelope["goldens"].items()}
    verdict, reasons = gate.judge(envelope, kinds, {}, [], required=everything)
    assert verdict == "RED" and all(f"checks.{n} is missing from an agent envelope" in reasons
                                    for n in gate.CLAIM_3_CHECKS)  # fmt: skip


def test_the_three_branch_envelopes_before_the_constant_are_red_under_it():
    """12b4646, 47258f2 and 6daf6c4 are agent envelopes after the merge that carry F2_1 alone (PR 3's
    branch before this constant). The gate rules them RED now, as SPEC/02 §4 says a run that forgot
    the checks must be; no Measured cell cites them."""
    for commit in ("12b4646d666dbbcc208a54bac20499146469b43e", "47258f2f690d80d52a245ee8d294167045bcc047",
                   "6daf6c4f369bea52f80e210b6bf80d3029dc5af1"):  # fmt: skip
        path = gate.HISTORY / f"{commit}.json"
        if not path.exists():
            pytest.skip(f"{commit[:7]} is not in history here")
        verdict, reasons = gate.rule(path)
        assert verdict == "RED" and "checks.F2_2 is missing from an agent envelope" in reasons


def test_a_control_envelope_carries_no_claim_2_check(chain):
    envelope_path, _, _ = chain()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["checks"]["F2_2"] = {"status": "pass", "url": URL}
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(gate.Rejected, match="read on an agent envelope only"):
        gate.read(envelope_path)


def test_over_the_cap_is_red_in_the_gate_too(chain):
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    assert gate.judge(envelope, KINDS, {}, [], cap=12000) == ("GREEN", [])
    verdict, reasons = gate.judge(envelope, KINDS, {}, [], cap=11999)
    assert verdict == "RED"
    assert "cost-cap: 12000 over 11999" in reasons
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


def test_plants_expected_is_zero_at_m00_and_seven_from_m03_pr2():
    """The controls are read at the commit: none existed at M00's last envelope (55dadb2)."""
    assert plants.plant_ids(KINDS, ROOT, "55dadb2f221e60036bdba0b01fdb6eff025d74bc") == []
    assert plants.plant_ids(KINDS, ROOT, "HEAD") == ["g-013", "g-015", "g-016", "g-017", "g-018", "g-019", "g-020"]


def test_the_plant_rule_counts_the_plants_its_control_names(monkeypatch, tmp_path):
    """SPEC/03 §5.1: a golden is a plant when its kind's control is there and names it by id.

    `tmp_path` is not a repository, so the made-up commit is read from that tree, as a test's is.
    """
    commit = "a" * 40
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "rules/guardrail.yaml"})
    assert plants.plant_ids(KINDS, tmp_path, commit) == []  # not there: no plants
    (tmp_path / "rules").mkdir()
    # g-014 is left out as it is at M03; g-001 is not the control's kind and is not counted.
    (tmp_path / "rules" / "guardrail.yaml").write_text("plants: [g-013, g-015, g-001]\n", encoding="utf-8")
    assert plants.plant_ids(KINDS, tmp_path, commit) == ["g-013", "g-015"]


def test_a_control_that_lists_no_plants_is_refused(monkeypatch, tmp_path):
    """Read as naming none, it would be a control whose plants nobody could see go silent."""
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "guardrail.yaml"})
    (tmp_path / "guardrail.yaml").write_text("guardrail:\n  denied_topics: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must list its plants by id"):
        plants.plant_ids(KINDS, tmp_path, "a" * 40)


def test_the_plant_rule_reads_the_control_at_the_commit_not_the_tree(monkeypatch):
    """Seed S6's rule on a real commit: a file in today's tree that was not there at the commit is absent.

    `Makefile` is in the tree; at M00's first commit it was not, and no golden could be a plant there.
    """
    first = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.split()[0]  # fmt: skip
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "Makefile"})
    assert (ROOT / "Makefile").exists()
    assert text_at(first, "Makefile", ROOT) == (None, f"{first[:12]}, the envelope's own commit")
    assert plants.plant_ids(KINDS, ROOT, first) == []


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
    verdict, reasons = gate.judge(gate.read(envelope_path), {**KINDS, "g-022": "redteam"}, {}, [])
    assert verdict == "RED" and "the envelope's goldens are not the goldens in the tree" in reasons


def test_measured_is_what_the_ledger_cell_must_say(chain):
    envelope_path, _, _ = chain(right={"g-001", "g-010"})
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "control: traps 1/3 (g-010); ordinary 1/9; guardrail 0/3; redteam 0/5; mode control; never_passed 18; regressed 0; "
        f"plants 0/0; GREEN; envelope `{'a' * 40}`"
    )
    envelope_path, _, _ = chain(right={"g-001"}, agent=True)
    assert gate.measured_at(envelope_path, envelope_path.parent) == (
        "agent: traps 0/3; ordinary 1/9; guardrail 0/3; redteam 0/5; control: traps 0/3; ordinary 0/9; guardrail 0/3; "
        f"redteam 0/5; mode runner; never_passed 19; regressed 0; plants 0/0; F1_1 pass {URL}; F1_2 pass {URL}; F1_3 pass {URL}; "
        f"F1_4 pass {URL}; F2_1 pass {URL}; F2_2 pass {URL}; GREEN; envelope `{'a' * 40}`; base b0219756"
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
