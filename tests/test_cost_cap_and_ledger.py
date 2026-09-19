"""cost-cap reads thresholds.yaml; make ledger holds the Measured cell to the envelope."""

from __future__ import annotations

import json

import pytest
import yaml

from src import cost_cap, ledger
from src.verdict import gate

from .conftest import make_raw


@pytest.mark.parametrize(("cap", "code", "said"), [(4500, 0, "ok"), (4499, 0, "OVER"), (0, 1, "FAIL"), ("20000", 1, "FAIL")])
def test_cost_cap(tmp_path, goldens, capsys, cap, code, said):
    """From M01 over the cap is a recorded RED, written by build (item 22): cost-cap prints it and exits 0."""
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")  # 15 calls x 300 tokens
    thresholds = tmp_path / "thresholds.yaml"
    thresholds.write_text(f"cost_cap:\n  tokens_per_run: {cap!r}\n", encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw), "--thresholds", str(thresholds)]) == code
    assert capsys.readouterr().out.startswith(said)


def test_cost_cap_counts_both_subjects(tmp_path, goldens, capsys):
    control, agent = tmp_path / "control.json", tmp_path / "agent.json"
    for raw in (control, agent):
        raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")
    assert cost_cap.main(["--raw", str(control), "--raw", str(agent)]) == 0
    assert "9,000 tokens this run" in capsys.readouterr().out


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
    envelope_path, _, _ = chain(right={"g-012"})
    history_dir = envelope_path.parent
    cell = gate.measured_at(envelope_path, history_dir)
    assert ledger.check_measured(row(cell), history_dir) is None
    assert ledger.check_measured(row(cell, "GREEN"), history_dir) is None
    assert ledger.check_measured(row(ledger.UNMEASURED), history_dir) is None

    wrong = cell.replace("traps 1/3", "traps 0/3")
    assert "differs from the envelope" in ledger.check_measured(row(wrong), history_dir)
    assert "names no envelope" in ledger.check_measured(row("traps 1/3"), history_dir)
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
