"""rule_swaps: the gate's verdict on each M04 swap PR's own envelope, at its commit.

    python scripts/rule_swaps.py SWAPS_OBS --out RULED

SWAPS_OBS is what `scripts/observe_pr.py` wrote for
`milestones/M04/runs/f4_swaps.yaml`: GitHub's record of each swap PR, with
the bot's envelope commit on it and the commit that envelope names (the one
its `evals` run measured). For each swap this takes two files at the bot's
commit, never at the head, so a later commit on the branch cannot change
them (security-reviewer F2 on M04 PR 3): `evals/history/<sha>.json` and
`evals/history/<sha>.baseline-card.json`, the only paths it asks git for.
It asks `verdict.gate` to rule on the envelope.

It rules on nothing and reads no envelope (P5; the cold review of M04 PR 2,
B1, and of PR 3, B2): it copies bytes and runs the gate. The gate runs as its
own process, in a fresh scratch worktree of HEAD for each swap (the tree
under measurement, so the gate is this commit's), with the card written at
its fixed path under `evals/history/` and nowhere else: a path taken from
the envelope let a swap branch put its own code where the gate imports from
(security-reviewer and cold review B1 on PR 3). The process gets no AWS or
GitHub credentials: its environment is `PATH`, the temp and home variables
and `PYTHONPATH`. The gate reads the card where the envelope names it and
checks its hash, so an envelope naming any other path is REJECTED.
Everything else the gate reads it reads at the swap's commit through git,
as for any envelope: the cap, the goldens, the controls, the bars, the pin
and the incumbent, and history from the swap's ancestors in the worktree.

The output is recorded by `build` in the envelope's `swaps` field and gated
by nothing (Product, M04 PR 3; SPEC/04 §4). So nothing on a swap branch may
stop the run: whatever goes wrong for one swap (no PR, no bot commit, a
file that is not there, a gate that hangs or writes nothing usable, any
exception) is written for that swap as `verdict: null` with a note, never
skipped and never raised (cold review F1 on PR 3). Exit 0 when the output
is written, whatever it says; 1 only when the observation file cannot be
read or the output cannot be written.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORY = "evals/history"
VERDICTS = ("GREEN", "RED", "UNMEASURED", "REJECTED")
SHA = re.compile(r"[0-9a-f]{40}")
GATE_SECONDS = 300
# The gate's process gets these and nothing else: no AWS_*, no GITHUB_TOKEN (security-reviewer B1, PR 3).
PASSED_ENV = ("PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR", "LANG")
# What the ledger and the explainer need from GitHub's record, beside the gate's reading.
KEPT = ("swap", "falsifier", "role", "expected", "pr", "found", "own_pr", "state", "merged", "head_sha",
        "envelope_commit", "measured_commit", "evals_on_measured", "required_on_head")  # fmt: skip


def git(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)


def show(commit: str, path: str) -> bytes | None:
    """The bytes of `path` at `commit` in this checkout, or None."""
    done = git("show", f"{commit}:{path}")
    return done.stdout if done.returncode == 0 else None


def gate_env(tree: Path) -> dict[str, str]:
    return {**{k: v for k, v in os.environ.items() if k in PASSED_ENV}, "PYTHONPATH": str(tree)}


def unread(entry: dict[str, Any], note: str) -> dict[str, Any]:
    return entry | {"verdict": None, "reasons": [], "note": note}


def gated(ruled: Path) -> tuple[str, list[str]] | None:
    """The gate's own output, if it is in the shape `--json` writes."""
    try:
        out = json.loads(ruled.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(out, dict) or out.get("verdict") not in VERDICTS or not isinstance(out.get("reasons"), list) \
            or not all(isinstance(r, str) for r in out["reasons"]):  # fmt: skip
        return None
    return out["verdict"], out["reasons"]


def rule_one(observed: dict[str, Any], scratch: Path) -> dict[str, Any]:
    """One swap: GitHub's record, and the gate's verdict on the envelope its bot commit holds."""
    entry = {key: observed.get(key) for key in KEPT}
    if observed.get("own_pr"):
        return unread(entry, "the pull request this run is on: a swap PR never reads itself (SPEC/04 §4)")
    if not observed.get("found"):
        return unread(entry, observed.get("note") or "the pull request was not found")
    bot, sha = observed.get("envelope_commit"), observed.get("measured_commit")
    if not (isinstance(bot, str) and SHA.fullmatch(bot) and isinstance(sha, str) and SHA.fullmatch(sha)):
        return unread(entry, "no bot envelope commit on the pull request: its evals run has not recorded one")
    envelope, card = show(bot, f"{HISTORY}/{sha}.json"), show(bot, f"{HISTORY}/{sha}.baseline-card.json")
    if envelope is None:
        return unread(entry, f"no {HISTORY}/{sha}.json at the bot's commit {bot}, or {bot} is not in this checkout")
    tree = scratch / f"tree-{sha[:12]}"
    added = git("worktree", "add", "--detach", str(tree), "HEAD")
    if added.returncode != 0:
        return unread(entry, f"no scratch worktree: {added.stderr.decode(errors='replace').strip()[-300:]}")
    try:
        path = scratch / f"{sha}.json"
        path.write_bytes(envelope)
        if card is not None:
            target = tree / HISTORY / f"{sha}.baseline-card.json"
            if target.exists():
                return unread(entry, f"{target.relative_to(tree).as_posix()} is already in HEAD's tree: not overwritten")
            target.write_bytes(card)
        ruled = scratch / f"{sha}.gate.json"
        try:
            done = subprocess.run([sys.executable, "-m", "src.verdict.gate", str(path), "--json", str(ruled)], cwd=tree,
                                  capture_output=True, check=False, timeout=GATE_SECONDS, env=gate_env(tree))  # fmt: skip
        except subprocess.TimeoutExpired:
            return unread(entry, f"the gate did not finish in {GATE_SECONDS} s")
        if (verdict := gated(ruled)) is None:
            return unread(entry, f"the gate wrote no verdict (exit {done.returncode}): "
                                 f"{done.stderr.decode(errors='replace').strip()[-300:]}")  # fmt: skip
        return entry | {"verdict": verdict[0], "reasons": verdict[1], "gate_exit": done.returncode}
    finally:
        git("worktree", "remove", "--force", str(tree))


def rule_all(observation: dict[str, Any]) -> list[dict[str, Any]]:
    swaps = observation.get("swaps") if isinstance(observation, dict) else None
    ruled = []
    with tempfile.TemporaryDirectory() as scratch:
        for swap in swaps if isinstance(swaps, list) else []:
            swap = swap if isinstance(swap, dict) else {}
            try:
                ruled.append(rule_one(swap, Path(scratch)))
            except Exception as exc:  # noqa: BLE001 - nothing on a swap branch may stop the run (cold review F1, PR 3)
                ruled.append(unread({key: swap.get(key) for key in KEPT}, f"{type(exc).__name__}: {exc}"[:300]))
    return ruled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("observed", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        observation = json.loads(args.observed.read_text(encoding="utf-8"))
        result = {
            "what": "the gate's verdict on each swap PR's envelope; recorded by build, gated by nothing",
            "observed": args.observed.as_posix(),
            "swaps": rule_all(observation),
        }
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"rule_swaps: {exc}", file=sys.stderr)
        return 1
    for swap in result["swaps"]:
        print(f"#{swap.get('pr')} {swap.get('role')}: {swap.get('verdict')} {swap.get('note') or ''}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
