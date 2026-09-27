"""scripts/rule_swaps.py (M04 PR 3; SPEC/04 §4): the gate's verdict on each swap PR's own envelope.

The envelope ruled here is a real CI-written one on `main`: PR 2's measuring
run, `9e4b559`, committed by the bot as `e6f01b9`. The gate rules it GREEN
from `main` as from a swap's head, which is what lets this test stand in for
a swap PR whose branch may be gone.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import rule_swaps
from src.verdict import ROOT

BOT = "e6f01b9d4a118d1290e2e7116429bb168d3e74f8"
MEASURED = "9e4b559bf7ff8241482ed89bb350a2f6249e8c5c"


def observed(**entry):
    return {"swap": "equivalent", "falsifier": "F4.2", "role": "m04_equivalent_swap", "pr": 26, "found": True,
            "merged": False, "head_sha": BOT, "measured_commit": MEASURED, **entry}  # fmt: skip


def test_the_gate_rules_the_swaps_own_envelope_from_its_head(tmp_path):
    [ruled, missing] = rule_swaps.rule_all({"swaps": [observed(), observed(measured_commit="0" * 40, pr=25)]})
    assert ruled["verdict"] == "GREEN" and ruled["reasons"] == [] and ruled["gate_exit"] == 0, ruled
    assert missing["verdict"] is None and f"no evals/history/{'0' * 40}.json" in missing["note"]


def test_what_cannot_be_read_is_written_unread_never_skipped():
    swaps = [observed(own_pr=True), observed(found=False, note="404"), observed(measured_commit=None),
             observed(head_sha="f" * 40)]  # fmt: skip
    ruled = rule_swaps.rule_all({"swaps": swaps})
    assert [r["verdict"] for r in ruled] == [None] * 4
    assert "never reads itself" in ruled[0]["note"] and ruled[1]["note"] == "404"
    assert "no bot envelope commit" in ruled[2]["note"] and "not in this checkout" in ruled[3]["note"]


def test_the_scratch_worktree_is_removed_and_the_tree_left_clean():
    import subprocess

    before = subprocess.run(["git", "worktree", "list"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    rule_swaps.rule_all({"swaps": [observed()]})
    after = subprocess.run(["git", "worktree", "list"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert after == before


def test_it_rules_on_nothing_itself():
    """P5 (the cold review of M04 PR 2, B1): the verdict is the gate's process's, not this script's."""
    source = (ROOT / "scripts" / "rule_swaps.py").read_text(encoding="utf-8")
    assert "from src" not in source and "import src" not in source
    assert '"-m", "src.verdict.gate"' in source


def test_the_command_line_writes_the_file_build_reads(tmp_path: Path):
    from src.verdict import build

    obs = tmp_path / "swaps.json"
    obs.write_text(json.dumps({"swaps": [observed()]}), encoding="utf-8")
    out = tmp_path / "swaps-ruled.json"
    assert rule_swaps.main([str(obs), "--out", str(out)]) == 0
    [kept] = build.swaps_record(out)
    assert kept["verdict"] == "GREEN" and kept["pr"] == 26 and set(kept) == set(build.SWAP_FIELDS)
