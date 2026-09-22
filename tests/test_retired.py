"""A retired golden is out of the run, the card and the envelope, and the gate reads the goldens at the envelope's commit (M02 PR 2, Door 2).

`g-012` is retired at M02 PR 2 with two keys and `g-021` added. The frozen
control (ADR-0002) still answers `g-012`; build drops that answer. The gate
holds an envelope to the goldens of its own commit, so the M00 and M01
envelopes in history, written over fifteen goldens that included `g-012`,
still read as they did.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from src.verdict import ROOT, build, gate, golden_kinds_at, load_golden_kinds

from .conftest import GOLDENS_DIR, make_raw

GOLDENS_AT_M00 = "9407615dcde09308490f6699c21a18100bfedcd2"  # row 0's envelope commit


def test_the_retired_golden_is_not_among_the_live_ones():
    live = load_golden_kinds(GOLDENS_DIR)
    assert "g-012" not in live and "g-021" in live and len(live) == 15
    assert build.retired_ids(GOLDENS_DIR) == {"g-012"}
    assert yaml.safe_load((GOLDENS_DIR / "g-012.yaml").read_text(encoding="utf-8"))["retired"] == "M02"


def test_the_controls_answer_to_a_retired_golden_is_dropped_not_refused(goldens, capsys):
    raw = make_raw(goldens)
    raw["observations"].append({**raw["observations"][0], "id": "g-012", "kind": "trap"})
    results = build.score_all(raw, goldens, *build.load_citables(ROOT), retired={"g-012"})
    assert set(results) == set(goldens)
    assert "g-012 is retired; its answer is not scored" in capsys.readouterr().err


def test_an_answer_to_an_unknown_golden_is_still_refused(goldens):
    raw = make_raw(goldens)
    raw["observations"].append({**raw["observations"][0], "id": "g-099"})
    try:
        build.score_all(raw, goldens, *build.load_citables(ROOT), retired={"g-012"})
    except build.Refused as refusal:
        assert "extra ['g-099']" in str(refusal)
    else:
        raise AssertionError("an observation for a golden that is not in the tree must be refused")


def test_the_gate_reads_the_goldens_at_the_envelopes_commit():
    then, where = golden_kinds_at(GOLDENS_AT_M00, GOLDENS_DIR, ROOT)
    assert "g-012" in then and "g-021" not in then and len(then) == 15
    assert where.startswith(GOLDENS_AT_M00[:12])
    now, where = golden_kinds_at("a" * 40, GOLDENS_DIR, ROOT)  # not a commit: the tree
    assert now == load_golden_kinds(GOLDENS_DIR) and where == "the working tree"


def test_an_envelope_from_before_the_retirement_still_reads_as_it_did():
    """Row 1's envelope, written over the fifteen goldens of its day, must not go RED for a retirement made later."""
    path = ROOT / "evals" / "history" / "e97125e970ccfc6d044612eb006cdbdbcdb99337.json"
    verdict, reasons = gate.rule(path)
    assert "the envelope's goldens are not the goldens in the tree" not in reasons
    assert verdict == "GREEN", reasons


def test_the_ledger_still_holds_every_measured_cell(tmp_path: Path):
    done = subprocess.run(["uv", "run", "python", "-m", "src.ledger"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout + done.stderr


def test_g_021_is_a_trap_the_control_cannot_pass(goldens):
    golden = goldens["g-021"]
    assert golden["kind"] == "trap" and golden["added"] == "M02" and golden["retired"] is None
    assert golden["expected"]["answer_fields"]["constraints"] == ["sequel_no_inherit"]
    for prompt in (ROOT / "src" / "baseline" / "prompt.txt", ROOT / "agents" / "refagent" / "prompt.txt"):
        assert "sequel_no_inherit" not in prompt.read_text(encoding="utf-8")
    citables = json.loads((ROOT / "data" / "clause_index.json").read_text(encoding="utf-8"))
    assert golden["expected"]["clause_id"] in citables
