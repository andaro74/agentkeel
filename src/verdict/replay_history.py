"""Past envelopes, replayed per (scope, golden id) (R11: ids are immutable; ADR-0004).

Reads `<history_dir>/<40-hex commit>.json` and nothing else: no card, no raw
file, no subfolder. `evals/history/pre-scope/` holds the one envelope written
before `scope` existed; it does not validate now and is not read.
A file that is not a valid envelope stops the replay; it is never skipped.

**Only the ancestors** (SPEC/03 §6, seed S7). Given `ancestors_of`, a
past envelope counts only when its commit is an ancestor of that one: a
pass recorded later, on a descendant or on another branch, is not a pass
"before" the envelope being ruled, and must not turn it RED. When git
cannot resolve `ancestors_of` (a test's made-up sha, a shallow clone) the
whole folder is read, as `text_at` reads the tree, and `ancestry` says so.

Control history gates nothing. It is kept for the M04 A-vs-A comparison and
so the gate can report when the control drifts (Finding F0.4).

**The incumbent's runs** (SPEC/04 §2, M04 PR 2). `incumbent_runs` reads the
same files for the `delta_max` bars: each agent envelope on one pin (its
profile and region) in one `mode`, with its `p95_ms` and the agent's own
tokens. It rules on nothing; build and the gate each compare a run with the
median of these, with their own code (P5).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from src.verdict import ROOT, canonical_sha256, schema_errors

ENVELOPE_NAME = re.compile(r"^([0-9a-f]{40})\.json$")

# (scope, golden id) -> [(commit, passed)], one entry per past envelope
History = dict[tuple[str, str], list[tuple[str, bool]]]


def envelope_paths(history_dir: Path) -> list[Path]:
    if not history_dir.is_dir():
        return []
    return sorted(p for p in history_dir.iterdir() if ENVELOPE_NAME.match(p.name))


def ancestry(commit: str, root: Path = ROOT) -> set[str] | None:
    """Every commit reachable from `commit`, itself included; None when git cannot resolve it."""
    done = subprocess.run(["git", "rev-list", f"{commit}^{{commit}}", "--"], cwd=root, capture_output=True,
                          text=True, check=False)  # fmt: skip
    return set(done.stdout.split()) if done.returncode == 0 else None


def load(history_dir: Path, *, exclude_commit: str | None = None, ancestors_of: str | None = None,
         root: Path = ROOT) -> History:  # fmt: skip
    keep = ancestry(ancestors_of, root) if ancestors_of is not None else None
    history: History = {}
    for path in envelope_paths(history_dir):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if errors := schema_errors(envelope):
            raise ValueError(f"{path}: not a valid envelope: {errors[0]}")
        if envelope["commit"] != path.stem:
            raise ValueError(f"{path}: commit {envelope['commit']} is not the file name")
        if envelope["commit"] == exclude_commit or (keep is not None and envelope["commit"] not in keep):
            continue
        for golden_id, result in envelope["goldens"].items():
            key = (result["scope"], golden_id)
            history.setdefault(key, []).append((envelope["commit"], result["pass"]))
    return history


def ever_passed(history: History, scope: str, golden_id: str) -> bool:
    """A control pass is not an agent pass: the baseline's luck is not the agent's bar."""
    return any(passed for _, passed in history.get((scope, golden_id), []))


def agent_tokens(envelope: dict[str, Any], root: Path = ROOT) -> int | None:
    """The agent's own tokens in one envelope: `agent_tokens` from M04 PR 2, else worked out.

    Before M04 PR 2 an agent envelope's `tokens_in` and `tokens_out` held one
    agent run and this run's control card, so the agent's side is those less
    the card's. None when the card does not resolve to the hash the envelope
    names: an envelope whose tokens cannot be split is not counted.
    """
    if isinstance(envelope.get("agent_tokens"), int):
        return envelope["agent_tokens"]
    ref = envelope.get("control_card_ref")
    if not isinstance(ref, dict) or "tokens_in" not in envelope:
        return None
    path = Path(ref["path"]) if Path(ref["path"]).is_absolute() else root / ref["path"]
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if canonical_sha256(card) != ref.get("sha256"):
        return None
    return envelope["tokens_in"] + envelope["tokens_out"] - card.get("tokens_in", 0) - card.get("tokens_out", 0)


def incumbent_runs(history_dir: Path, *, profile: str, region: str, mode: str, exclude_commit: str | None = None,
                   ancestors_of: str | None = None, root: Path = ROOT) -> list[dict[str, Any]]:  # fmt: skip
    """Each agent envelope on `profile` in `region` and `mode`: its commit, `p95_ms` and agent tokens.

    Only schema version 2 counts: an envelope with no `mode` is not counted
    (threshold-owner F2 on M04 PR 1). The ancestors only, as `load` reads them.
    An envelope whose `checks.F4_4` failed is not counted either (the
    Threshold Owner, ruling on F1 at M04 PR 2): a run over the bar that later
    merged must not lift the median the next run is held to. **Unless every
    counted envelope failed it**: the envelope does not say why, and a pin's
    first runs fail it for having no incumbent, not for being over one.
    Leaving them all out would leave the pin no median, ever; so then all
    are counted, as the only numbers the pin has.
    """
    keep = ancestry(ancestors_of, root) if ancestors_of is not None else None
    runs = []
    for path in envelope_paths(history_dir):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if envelope.get("commit") == exclude_commit or (keep is not None and envelope.get("commit") not in keep):
            continue
        if envelope.get("schema_version") != 2 or envelope.get("mode") != mode:
            continue
        if (envelope.get("model_id"), envelope.get("region")) != (profile, region):
            continue
        if {r.get("scope") for r in envelope.get("goldens", {}).values()} != {"agent"}:
            continue
        runs.append({"commit": envelope["commit"], "p95_ms": envelope.get("p95_ms"),
                     "agent_tokens": agent_tokens(envelope, root),
                     "over": ((envelope.get("checks") or {}).get("F4_4") or {}).get("status") == "fail"})  # fmt: skip
    clean = [r for r in runs if not r["over"]]
    return [{k: v for k, v in r.items() if k != "over"} for r in (clean or runs)]
