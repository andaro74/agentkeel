"""Past envelopes, replayed per (scope, golden id) (R11: ids are immutable; ADR-0004).

Reads `<history_dir>/<40-hex commit>.json` and nothing else: no card, no raw
file, no subfolder. `evals/history/pre-scope/` holds the one envelope written
before `scope` existed; it does not validate now and is not read.
A file that is not a valid envelope stops the replay; it is never skipped.

Control history gates nothing. It is kept for the M04 A-vs-A comparison and
so the gate can report when the control drifts (Finding F0.4).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.verdict import schema_errors

ENVELOPE_NAME = re.compile(r"^([0-9a-f]{40})\.json$")

# (scope, golden id) -> [(commit, passed)], one entry per past envelope
History = dict[tuple[str, str], list[tuple[str, bool]]]


def envelope_paths(history_dir: Path) -> list[Path]:
    if not history_dir.is_dir():
        return []
    return sorted(p for p in history_dir.iterdir() if ENVELOPE_NAME.match(p.name))


def load(history_dir: Path, *, exclude_commit: str | None = None) -> History:
    history: History = {}
    for path in envelope_paths(history_dir):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if errors := schema_errors(envelope):
            raise ValueError(f"{path}: not a valid envelope: {errors[0]}")
        if envelope["commit"] != path.stem:
            raise ValueError(f"{path}: commit {envelope['commit']} is not the file name")
        if envelope["commit"] == exclude_commit:
            continue
        for golden_id, result in envelope["goldens"].items():
            key = (result["scope"], golden_id)
            history.setdefault(key, []).append((envelope["commit"], result["pass"]))
    return history


def ever_passed(history: History, scope: str, golden_id: str) -> bool:
    """A control pass is not an agent pass: the baseline's luck is not the agent's bar."""
    return any(passed for _, passed in history.get((scope, golden_id), []))
