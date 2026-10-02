"""cost-cap reads thresholds.yaml; make ledger holds the Measured cell to the envelope."""

from __future__ import annotations

import json

import pytest
import yaml

from src import cost_cap, ledger
from src.verdict import gate

from .conftest import make_raw


@pytest.mark.parametrize(("cap", "code", "said"), [(5700, 0, "ok"), (5699, 0, "OVER"), (0, 1, "FAIL"), ("20000", 1, "FAIL")])
def test_cost_cap(tmp_path, goldens, capsys, cap, code, said):
    """From M01 over the cap is a recorded RED, written by build (item 22): cost-cap prints it and exits 0."""
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")  # 19 calls x 300 tokens (g-016 to g-020 from M03 PR 2; g-021 retired at M04 PR 2)
    thresholds = tmp_path / "thresholds.yaml"
    thresholds.write_text(f"cost_cap:\n  tokens_per_run: {cap!r}\n", encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw), "--thresholds", str(thresholds)]) == code
    assert capsys.readouterr().out.startswith(said)


def test_cost_cap_counts_as_build_does(tmp_path, goldens, capsys):
    """In plus out; totalTokens can carry cache writes, and build does not read it."""
    raw_doc = make_raw(goldens)
    for observation in raw_doc["observations"]:
        observation["usage"]["totalTokens"] = 10_000
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(raw_doc), encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw)]) == 0
    assert "5,700 tokens this run" in capsys.readouterr().out


def test_the_gate_does_not_read_a_deleted_cap_as_no_cap(chain, monkeypatch):
    envelope_path, _, _ = chain()  # a control envelope: its read needs no pinned base, so only the cap is missing
    # thresholds.yaml with the cap deleted, wherever the gate reads it (M03 PR 2: through text_at)
    real = gate.text_at
    monkeypatch.setattr(gate, "text_at", lambda commit, path, root=gate.ROOT: (
        ("cost_cap: {}\n", "the working tree") if path == "thresholds.yaml" else real(commit, path, root)))
    with pytest.raises(gate.Rejected, match="tokens_per_run"):
        gate.rule(envelope_path, envelope_path.parent / "none")


def test_cost_cap_counts_both_subjects(tmp_path, goldens, capsys):
    control, agent = tmp_path / "control.json", tmp_path / "agent.json"
    for raw in (control, agent):
        raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")
    assert cost_cap.main(["--raw", str(control), "--raw", str(agent)]) == 0
    assert "11,400 tokens this run" in capsys.readouterr().out


def test_a_reply_with_no_usage_fails_the_cap(tmp_path, goldens):
    raw_doc = make_raw(goldens)
    del raw_doc["observations"][0]["usage"]
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(raw_doc), encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw)]) == 1
    # a failed call has no usage and is not a reply
    raw_doc["observations"][0] = {"id": "g-001", "kind": "ordinary", "question": "q", "error": "Throttled"}
    raw.write_text(json.dumps(raw_doc), encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw)]) == 0


def test_the_repo_has_a_cap_the_code_can_read():
    thresholds = yaml.safe_load((cost_cap.ROOT / "thresholds.yaml").read_text(encoding="utf-8"))
    cap = thresholds["cost_cap"]["tokens_per_run"]  # the number is the Threshold Owner's, not this test's
    assert isinstance(cap, int) and cap > 0


def test_ledger_reads_every_row():
    rows = ledger.rows()
    assert [row["M"] for row in rows] == [f"M{n:02d}" for n in range(9)]
    assert set(ledger._sentences()) == {row["M"] for row in rows}


def row(measured, state="OPEN"):
    return {"#": "0", "Measured": measured, "State": state}


def test_ledger_fails_when_the_cell_differs_from_the_envelope(chain):
    envelope_path, _, _ = chain(right={"g-010"})
    history_dir = envelope_path.parent
    cell = gate.measured_at(envelope_path, history_dir)
    assert ledger.check_measured(row(cell), history_dir) is None
    assert ledger.check_measured(row(cell, "GREEN"), history_dir) is None
    assert ledger.check_measured(row(ledger.UNMEASURED), history_dir) is None

    wrong = cell.replace("traps 1/2", "traps 0/2")
    assert "differs from the envelope" in ledger.check_measured(row(wrong), history_dir)
    assert "names no envelope" in ledger.check_measured(row("traps 1/2"), history_dir)
    gone = cell.replace("a" * 40, "d" * 40)
    assert "unreadable" in ledger.check_measured(row(gone), history_dir)


def test_ledger_holds_state_to_the_measurement(chain):
    envelope_path, _, _ = chain()
    history_dir = envelope_path.parent
    cell = gate.measured_at(envelope_path, history_dir)  # GREEN
    assert "with no measurement" in ledger.check_measured(row(ledger.UNMEASURED, "GREEN"), history_dir)
    assert ledger.check_measured(row(ledger.UNMEASURED, "RED"), history_dir) is None  # closed unmeasured is RED
    assert "is not the verdict" in ledger.check_measured(row(cell, "RED"), history_dir)


def test_ledger_sides_with_the_gate_not_with_build(chain, past, goldens):
    """The cold review's probe: build, kept from the history, says GREEN; the gate says RED."""
    ordinary = {g for g, golden in goldens.items() if golden["kind"] == "ordinary"}
    history_dir = past(right=ordinary, agent=True)
    envelope_path, _, _ = chain(agent=True)  # now everything fails, built with no history
    assert json.loads(envelope_path.read_text(encoding="utf-8"))["verdict"] == "GREEN"

    cell = gate.measured_at(envelope_path, history_dir)
    assert "; RED; " in cell and "; GREEN; " not in cell
    green_cell = cell.replace("; RED; ", "; GREEN; ")
    # the cell cites the envelope by commit; put the envelope where the ledger looks
    (history_dir / envelope_path.name).write_text(envelope_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert "differs from the envelope" in ledger.check_measured(row(green_cell, "GREEN"), history_dir)


def test_a_row_read_as_unmeasured_closes_red_and_never_green():
    """SPEC/00 section 7 (M01 PR 4). Row 1's cell reads UNMEASURED: the second half of
    claim 1 was never read in the runtime. RED may stand beside it; GREEN may not."""
    history = gate.HISTORY
    envelope = history / "e97125e970ccfc6d044612eb006cdbdbcdb99337.json"
    cell = gate.measured_at(envelope, history, milestone="M01")
    assert "; UNMEASURED; " in cell
    as_row = {"#": "1", "M": "M01", "Measured": cell}
    assert ledger.check_measured({**as_row, "State": "RED"}, history) is None
    assert "GREEN beside an UNMEASURED reading" in ledger.check_measured({**as_row, "State": "GREEN"}, history)


def test_row_4_reads_the_swaps_and_closes_red_on_f4_2():
    """SPEC/04 §7 (M04 PR 4): the swaps gate no pull request, but row 4 reads them. 12ebb54's run is
    GREEN on its own; #26, the equivalent swap, recorded RED with g-005 regressed, so row 4 reads RED."""
    history = gate.HISTORY
    envelope = history / "12ebb54ca3fb3a13e8807f8f5bca37a83b0e4df1.json"
    assert "; GREEN; " in gate.measured_at(envelope, history)
    cell = gate.measured_at(envelope, history, milestone="M04")
    assert "; swap #26 equivalent missed: RED, expected GREEN; RED; " in cell and "; GREEN; " not in cell
    assert "breaking missed" not in cell
    # A later row that reads neither the runtime, the swaps, the attempts, the template nor the upgrades reads
    # the envelope alone. Not M05 from M05 PR 2: row 5 reads `containment` (READ_THE_CONTAINMENT), and this
    # envelope has none. Not M06 from M06 PR 2: row 6 reads `template` (READ_THE_TEMPLATE), which it has not
    # either. Not M07 from M07 PR 2: row 7 reads `upgrade` (READ_THE_UPGRADE).
    assert gate.measured_at(envelope, history, milestone="M08") == gate.measured_at(envelope, history)
    assert "containment not read" in gate.measured_at(envelope, history, milestone="M05")
    assert "template not read" in gate.measured_at(envelope, history, milestone="M06")
    assert "upgrade not read: the envelope records no attempt; RED; " in gate.measured_at(envelope, history, milestone="M07")
    as_row = {"#": "4", "M": "M04", "Measured": cell}
    assert ledger.check_measured({**as_row, "State": "RED"}, history) is None
    assert "is not the verdict" in ledger.check_measured({**as_row, "State": "GREEN"}, history)


GREEN_CHECKS = {"evals_on_measured": "success", "required_on_head": {"checks": "success", "evals": "success"}}


def _swap(name, verdict, reasons=(), **seen):
    seen = {**GREEN_CHECKS, **seen} if name == "equivalent" else seen
    return {"swap": name, "pr": 25 if name == "breaking" else 26, "verdict": verdict, "reasons": list(reasons), **seen}


REGRESSED = ["regressed: g-001 has passed before and fails now"]
OK = _swap("equivalent", "GREEN")


@pytest.mark.parametrize(("swaps", "misses"), [
    ([_swap("breaking", "RED", REGRESSED), OK], []),
    ([_swap("breaking", "GREEN"), OK], ["swap #25 breaking missed: GREEN, expected RED"]),
    ([_swap("breaking", "RED", ["check F4_1 failed: x"]), OK],
     ["swap #25 breaking missed: RED with no citing golden regressed"]),
    ([_swap("breaking", "RED", ["regressed: g-016 has passed before and fails now"]), OK],
     ["swap #25 breaking missed: RED with no citing golden regressed"]),
    ([_swap("breaking", "RED", [*REGRESSED, "cost-cap: 160000 over 150000"]), OK],
     ["swap #25 breaking missed: RED over the cost cap"]),
    ([_swap("breaking", "RED", [*REGRESSED, "and 3 more reasons, not kept"]), OK],
     ["swap #25 breaking missed: reasons cut, so no cost cap cannot be read"]),
    ([_swap("breaking", "REJECTED"), OK], ["swap #25 breaking missed: REJECTED, expected RED"]),
    ([_swap("breaking", "RED", REGRESSED), _swap("equivalent", None)], ["swap equivalent missed: not read"]),
    ([_swap("breaking", "RED", REGRESSED), _swap("equivalent", "GREEN", evals_on_measured="failure")],
     ["swap #26 equivalent missed: GREEN with evals (measured) not green"]),
    ([_swap("breaking", "RED", REGRESSED),
      _swap("equivalent", "GREEN", required_on_head={"checks": "failure", "evals": None})],
     ["swap #26 equivalent missed: GREEN with checks, evals not green"]),
    ([_swap("breaking", "RED", REGRESSED), _swap("equivalent", "GREEN", required_on_head=None)],
     ["swap #26 equivalent missed: no required check read on its head"]),
    ([], ["swap breaking missed: not read", "swap equivalent missed: not read"]),
])  # fmt: skip
def test_a_swap_that_misses_its_falsifier_or_is_unread_is_named(swaps, misses):
    """SPEC/04 §7, and the cold review of M04 PR 4 (F1, F2): a RED on the cost cap, or with no citing
    golden, is not F4.1's RED; an equivalent GREEN with a required check red does not promote."""
    assert gate.swap_misses(swaps) == misses
