"""scripts/rule_swaps.py (M04 PR 3; SPEC/04 §4): the gate's verdict on each swap PR's own envelope.

The envelope ruled here is a real CI-written one on `main`: PR 2's measuring
run, `9e4b559`, committed by the bot as `e6f01b9`. The gate rules it GREEN
from `main` as from a swap's bot commit, which is what lets this test stand
in for a swap PR whose branch may be gone. The hostile cases are the cold
review's and security-reviewer's B1 and F1 on PR 3, each tried.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import rule_swaps
from src.verdict import ROOT

BOT = "e6f01b9d4a118d1290e2e7116429bb168d3e74f8"
MEASURED = "9e4b559bf7ff8241482ed89bb350a2f6249e8c5c"
ENVELOPE = f"evals/history/{MEASURED}.json"
CARD = f"evals/history/{MEASURED}.baseline-card.json"


def observed(**entry):
    return {"swap": "equivalent", "falsifier": "F4.2", "role": "m04_equivalent_swap", "pr": 26, "found": True,
            "merged": False, "head_sha": "d" * 40, "envelope_commit": BOT, "measured_commit": MEASURED,
            **entry}  # fmt: skip


def worktrees() -> str:
    return subprocess.run(["git", "worktree", "list"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def test_the_gate_rules_the_swaps_own_envelope_at_the_bots_commit():
    [ruled, missing] = rule_swaps.rule_all({"swaps": [observed(), observed(measured_commit="0" * 40, pr=25)]})
    assert ruled["verdict"] == "GREEN" and ruled["reasons"] == [] and ruled["gate_exit"] == 0, ruled
    assert ruled["envelope_commit"] == BOT
    assert missing["verdict"] is None and f"no evals/history/{'0' * 40}.json at the bot's commit" in missing["note"]


def test_what_cannot_be_read_is_written_unread_never_skipped():
    swaps = [observed(own_pr=True), observed(found=False, note="404"), observed(envelope_commit=None),
             observed(envelope_commit="f" * 40), observed(measured_commit="../../x")]  # fmt: skip
    ruled = rule_swaps.rule_all({"swaps": swaps})
    assert [r["verdict"] for r in ruled] == [None] * 5
    assert "never reads itself" in ruled[0]["note"] and ruled[1]["note"] == "404"
    assert "no bot envelope commit" in ruled[2]["note"] and "not in this checkout" in ruled[3]["note"]
    assert "no bot envelope commit" in ruled[4]["note"]  # a named commit that is not a sha is not a path


def test_an_envelope_naming_another_card_path_cannot_put_code_where_the_gate_imports(monkeypatch):
    """B1 (security-reviewer and cold review, PR 3): the card path came from the envelope, so a swap branch
    could write its own `src/verdict/gate.py` into the worktree before the gate imported it. Now only the
    two fixed paths are ever asked for, and the gate REJECTs an envelope whose card is not where it says."""
    real = subprocess.run(["git", "show", f"{BOT}:{ENVELOPE}"], cwd=ROOT, capture_output=True, check=True).stdout
    hostile = json.loads(real)
    hostile["control_card_ref"]["path"] = "src/verdict/gate.py"
    asked = []

    def show(commit, path):
        asked.append(path)
        served = {ENVELOPE: json.dumps(hostile).encode(), "src/verdict/gate.py": b"raise SystemExit('the branch ran')"}
        return served.get(path)

    monkeypatch.setattr(rule_swaps, "show", show)
    [ruled] = rule_swaps.rule_all({"swaps": [observed()]})
    assert asked == [ENVELOPE, CARD]
    assert ruled["verdict"] == "REJECTED" and "control_card_ref" in ruled["reasons"][0], ruled


def test_nothing_on_a_swap_branch_stops_the_run(monkeypatch):
    """F1 (cold review and security-reviewer, PR 3): an envelope that is not JSON is the gate's to REJECT;
    any exception is that swap's `verdict: null`, and the next swap is still read."""
    served = {ENVELOPE: b"\xff not json"}
    monkeypatch.setattr(rule_swaps, "show", lambda commit, path: served.get(path))
    [ruled] = rule_swaps.rule_all({"swaps": [observed()]})
    assert ruled["verdict"] == "REJECTED" and "unreadable" in ruled["reasons"][0], ruled

    def boom(commit, path):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "planted")

    monkeypatch.setattr(rule_swaps, "show", boom)
    ruled = rule_swaps.rule_all({"swaps": [observed(), "not a mapping"]})
    assert [r["verdict"] for r in ruled] == [None, None] and "UnicodeDecodeError" in ruled[0]["note"]
    assert rule_swaps.rule_all(["not", "a", "mapping"]) == []


def test_the_gate_gets_no_credentials(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "planted")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "planted")
    monkeypatch.setenv("GITHUB_TOKEN", "planted")
    env = rule_swaps.gate_env(tmp_path)
    assert env["PYTHONPATH"] == str(tmp_path)
    assert not [k for k in env if k.startswith(("AWS_", "GITHUB_"))]


def test_the_scratch_worktrees_are_removed():
    before = worktrees()
    rule_swaps.rule_all({"swaps": [observed(), observed(pr=25)]})
    assert worktrees() == before


def test_it_reads_no_envelope_and_rules_on_nothing_itself():
    """P5 (the cold review of M04 PR 2, B1; of PR 3, B2): bytes copied, the gate's process asked."""
    source = (ROOT / "scripts" / "rule_swaps.py").read_text(encoding="utf-8")
    assert "from src" not in source and "import src" not in source
    assert '"-m", "src.verdict.gate"' in source
    assert "json.loads(envelope" not in source and "control_card_ref\")" not in source


@pytest.mark.parametrize("swaps", [[], None])
def test_the_command_line_writes_the_file_build_reads(tmp_path: Path, swaps):
    from src.verdict import build

    obs = tmp_path / "swaps.json"
    obs.write_text(json.dumps({"swaps": [observed()] if swaps is None else swaps}), encoding="utf-8")
    out = tmp_path / "swaps-ruled.json"
    assert rule_swaps.main([str(obs), "--out", str(out)]) == 0
    kept = build.swaps_record(out)
    if swaps == []:
        assert kept == []
        return
    [kept] = kept
    assert kept["verdict"] == "GREEN" and kept["pr"] == 26 and set(kept) == set(build.SWAP_FIELDS)
