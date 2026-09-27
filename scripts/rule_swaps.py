"""rule_swaps: the gate's verdict on each M04 swap PR's own envelope, at its commit.

    python scripts/rule_swaps.py SWAPS_OBS --out RULED

SWAPS_OBS is what `scripts/observe_pr.py` wrote for
`milestones/M04/runs/f4_swaps.yaml`: GitHub's record of each swap PR, with
its head and the commit its last `evals` run measured. For each swap this
takes the envelope that run wrote, and the control card it names, from the
PR's head in this checkout (`git show`; the checkout has every branch,
`fetch-depth: 0`), and asks `verdict.gate` to rule on it.

It rules on nothing itself (P5; the cold review of M04 PR 2, B1). The gate
runs as its own process, in a scratch worktree of HEAD (the tree under
measurement, so the gate is this commit's), with the swap's card put where
the envelope names it. Everything else the gate reads it reads at the
swap's commit through git, as for any envelope: the cap, the goldens, the
controls, the bars, the pin and the incumbent, and history from the swap's
ancestors in this worktree's `evals/history/`. The gate checks the card's
hash against the envelope, so a card taken from the branch is the one the
run wrote or the envelope is REJECTED.

The output is recorded by `build` in the envelope's `swaps` field and gated
by nothing (Product, M04 PR 3; SPEC/04 §4): the equivalent swap's run
regressed `g-005`, F4.2 fired, and a check that failed on every envelope
from then on would block every later pull request for a result that is
already the finding. `F4_1` and `F4_2` stay the seed tests' witnesses.

A swap with no PR number, not found, with no measured commit, or whose head
or envelope is not in this checkout is written with `verdict: null` and a
note, never skipped. Exit 0 when the output is written, whatever it says;
1 only when it could not be.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORY = "evals/history"
# What the ledger and the explainer need from GitHub's record, beside the gate's reading.
KEPT = ("swap", "falsifier", "role", "expected", "pr", "found", "own_pr", "state", "merged", "head_sha",
        "measured_commit", "evals_on_measured", "required_on_head")  # fmt: skip


def git(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def unread(entry: dict[str, Any], note: str) -> dict[str, Any]:
    return entry | {"verdict": None, "reasons": [], "note": note}


def rule_one(observed: dict[str, Any], tree: Path, scratch: Path) -> dict[str, Any]:
    """One swap: GitHub's record, and the gate's verdict on the envelope its head holds for the measured commit."""
    entry = {key: observed.get(key) for key in KEPT}
    if observed.get("own_pr"):
        return unread(entry, "the pull request this run is on: a swap PR never reads itself (SPEC/04 §4)")
    head, sha = observed.get("head_sha"), observed.get("measured_commit")
    if not observed.get("found"):
        return unread(entry, observed.get("note") or "the pull request was not found")
    if not sha:
        return unread(entry, "no bot envelope commit on the pull request: its evals run has not recorded one")
    if git("cat-file", "-e", f"{head}^{{commit}}").returncode != 0:
        return unread(entry, f"the head {head} is not in this checkout")
    envelope = git("show", f"{head}:{HISTORY}/{sha}.json")
    if envelope.returncode != 0:
        return unread(entry, f"no {HISTORY}/{sha}.json at the head {head}")
    path = scratch / f"{sha}.json"
    path.write_text(envelope.stdout, encoding="utf-8")
    ref = (json.loads(envelope.stdout).get("control_card_ref") or {}).get("path")
    if ref:
        card = git("show", f"{head}:{ref}")
        if card.returncode == 0:
            (tree / ref).parent.mkdir(parents=True, exist_ok=True)
            (tree / ref).write_text(card.stdout, encoding="utf-8")
    ruled = scratch / f"{sha}.gate.json"
    done = subprocess.run([sys.executable, "-m", "src.verdict.gate", str(path), "--json", str(ruled)], cwd=tree,
                          capture_output=True, text=True, check=False,
                          env={**os.environ, "PYTHONPATH": str(tree)})  # fmt: skip
    if not ruled.is_file():
        return unread(entry, f"the gate wrote no verdict (exit {done.returncode}): {done.stderr.strip()[-300:]}")
    return entry | json.loads(ruled.read_text(encoding="utf-8")) | {"gate_exit": done.returncode}


def rule_all(observation: dict[str, Any]) -> list[dict[str, Any]]:
    swaps = observation.get("swaps") or []
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch) / "tree"
        added = git("worktree", "add", "--detach", str(tree), "HEAD")
        if added.returncode != 0:
            return [unread({key: s.get(key) for key in KEPT}, f"no scratch worktree: {added.stderr.strip()}")
                    for s in swaps]  # fmt: skip
        try:
            return [rule_one(s, tree, Path(scratch)) for s in swaps]
        finally:
            git("worktree", "remove", "--force", str(tree))


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
    except (OSError, json.JSONDecodeError) as exc:
        print(f"rule_swaps: {exc}", file=sys.stderr)
        return 1
    for swap in result["swaps"]:
        print(f"#{swap.get('pr')} {swap.get('role')}: {swap.get('verdict')} {swap.get('note', '')}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
