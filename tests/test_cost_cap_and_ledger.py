"""cost-cap reads thresholds.yaml; make ledger holds the Measured cell to the envelope."""

from __future__ import annotations

import json

import pytest
import yaml

from src import cost_cap, ledger
from src.verdict import gate

from .conftest import make_raw


@pytest.mark.parametrize(("cap", "code"), [(4500, 0), (4499, 1), (0, 1), ("20000", 1)])
def test_cost_cap(tmp_path, goldens, cap, code):
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps(make_raw(goldens)), encoding="utf-8")  # 15 calls x 300 tokens
    thresholds = tmp_path / "thresholds.yaml"
    thresholds.write_text(f"cost_cap:\n  tokens_per_run: {cap!r}\n", encoding="utf-8")
    assert cost_cap.main(["--raw", str(raw), "--thresholds", str(thresholds)]) == code


def test_the_cap_in_the_repo_is_the_m00_ruling():
    thresholds = yaml.safe_load((cost_cap.ROOT / "thresholds.yaml").read_text(encoding="utf-8"))
    assert thresholds == {"cost_cap": {"tokens_per_run": 20000}}


def test_ledger_reads_every_row():
    rows = ledger.rows()
    assert [row["M"] for row in rows] == [f"M{n:02d}" for n in range(9)]
    assert set(ledger._sentences()) == {row["M"] for row in rows}


def test_ledger_fails_when_the_cell_differs_from_the_envelope(chain):
    envelope_path, _, _ = chain(right={"g-012"})
    history_dir = envelope_path.parent
    cell = gate.measured(gate.read(envelope_path))
    assert ledger.check_measured({"#": "0", "Measured": cell}, history_dir) is None
    assert ledger.check_measured({"#": "0", "Measured": ledger.UNMEASURED}, history_dir) is None

    wrong = cell.replace("traps 1/3", "traps 0/3")
    assert "differs from the envelope" in ledger.check_measured({"#": "0", "Measured": wrong}, history_dir)
    assert "names no envelope" in ledger.check_measured({"#": "0", "Measured": "traps 1/3"}, history_dir)
    gone = cell.replace("a" * 40, "d" * 40)
    assert "unreadable" in ledger.check_measured({"#": "0", "Measured": gone}, history_dir)
