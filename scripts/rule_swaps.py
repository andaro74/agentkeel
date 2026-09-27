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
(security-reviewer and cold review B1 on PR 3). The gate is run with
`--strict-cards`, so it opens a card only at that fixed path and REJECTs an
envelope naming any other before opening anything. The process gets no AWS
or GitHub credentials: its environment is `PASSED_ENV` below and
`PYTHONPATH`.
Everything else the gate reads it reads at the swap's commit through git,
as for any envelope: the cap, the goldens, the controls, the bars, the pin
and the incumbent, and history from the swap's ancestors in the worktree.

The output is recorded by `build` in the envelope's `swaps` field and gated
by nothing (Product, M04 PR 3; SPEC/04 §4). So nothing on a swap branch may
stop the run: whatever goes wrong for one swap (no PR, no bot commit, a
file that is not there, a gate that hangs or writes nothing usable, any
exception) is written for that swap as `verdict: null` with a note, never
skipped and never raised (cold review F1 on PR 3). All swaps together have
`BUDGET_SECONDS`, and each git call `GIT_SECONDS`, so the read cannot run
the job out of its 15 minutes. A verdict's reasons are cut to
`MAX_REASONS` of `MAX_REASON_CHARS` each, since their text can repeat what
a swap's envelope says (security-reviewer, second read). Exit 0 when the output
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
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HISTORY = "evals/history"
VERDICTS = ("GREEN", "RED", "UNMEASURED", "REJECTED")
SHA = re.compile(r"[0-9a-f]{40}")
BUDGET_SECONDS = 240  # every swap together; the job has 15 minutes and must also run the agent twice
GIT_SECONDS = 60
MAX_REASONS = 50
MAX_REASON_CHARS = 300
# The gate's process gets these and nothing else: no AWS_*, no GITHUB_TOKEN (security-reviewer B1, PR 3).
PASSED_ENV = ("PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR", "LANG")
# What the ledger and the explainer need from GitHub's record, beside the gate's reading.
KEPT = ("swap", "falsifier", "role", "expected", "pr", "found", "own_pr", "state", "merged", "head_sha",
        "envelope_commit", "measured_commit", "evals_on_measured", "required_on_head")  # fmt: skip


def git(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[bytes]:
    # No LFS smudge: a worktree of HEAD needs no video (security-reviewer, second read).
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False, timeout=GIT_SECONDS, env=env)


def show(commit: str, path: str) -> bytes | None:
    """The bytes of `path` at `commit` in this checkout, or None."""
    done = git("show", f"{commit}:{path}")
    return done.stdout if done.returncode == 0 else None


def gate_env(tree: Path) -> dict[str, str]:
    return {**{k: v for k, v in os.environ.items() if k in PASSED_ENV}, "PYTHONPATH": str(tree)}


def plain(text: str) -> str:
    """One line, no workflow command, cut: what reaches the job log and the envelope from a note."""
    return " ".join(text.split()).replace("::", ": :")[:MAX_REASON_CHARS]


def unread(entry: dict[str, Any], note: str) -> dict[str, Any]:
    return entry | {"verdict": None, "reasons": [], "note": plain(note)}


def run_gate(envelope: Path, ruled: Path, tree: Path, seconds: float) -> subprocess.CompletedProcess[bytes]:
    """The gate, as its own process, in `tree`, with no credentials and a card only at its fixed path."""
    return subprocess.run([sys.executable, "-m", "src.verdict.gate", str(envelope), "--json", str(ruled),
                           "--strict-cards"], cwd=tree, capture_output=True, check=False, timeout=seconds,
                          env=gate_env(tree))  # fmt: skip


def gated(ruled: Path) -> tuple[str, list[str]] | None:
    """The gate's own output, if it is in the shape `--json` writes."""
    try:
        out = json.loads(ruled.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(out, dict) or out.get("verdict") not in VERDICTS or not isinstance(out.get("reasons"), list) \
            or not all(isinstance(r, str) for r in out["reasons"]):  # fmt: skip
        return None
    reasons = [plain(r) for r in out["reasons"][:MAX_REASONS]]
    if len(out["reasons"]) > MAX_REASONS:
        reasons.append(f"and {len(out['reasons']) - MAX_REASONS} more reasons, not kept")
    return out["verdict"], reasons


def rule_one(observed: dict[str, Any], scratch: Path, seconds: float = BUDGET_SECONDS) -> dict[str, Any]:
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
    tree = Path(tempfile.mkdtemp(prefix=f"tree-{sha[:12]}-", dir=scratch))  # its own, even for the same sha
    added = git("worktree", "add", "--detach", str(tree), "HEAD")
    if added.returncode != 0:
        return unread(entry, f"no scratch worktree: {added.stderr.decode(errors='replace').strip()[-300:]}")
    try:
        path = scratch / f"{sha}.json"
        path.write_bytes(envelope)
        if card is not None:
            target = tree / HISTORY / f"{sha}.baseline-card.json"
            # Compared as git holds it, not as checked out: a checkout may rewrite line endings.
            at_head = show("HEAD", f"{HISTORY}/{sha}.baseline-card.json")
            if at_head is None:
                target.write_bytes(card)
            elif at_head != card:
                return unread(entry, f"{target.relative_to(tree).as_posix()} is in HEAD's tree with other bytes: "
                                     "not overwritten")  # fmt: skip
        ruled = scratch / f"{sha}.gate.json"
        try:
            done = run_gate(path, ruled, tree, max(seconds, 1))
        except subprocess.TimeoutExpired:
            return unread(entry, f"the gate did not finish in the {max(seconds, 1):.0f} s left of the read's budget")
        if (verdict := gated(ruled)) is None:
            return unread(entry, f"the gate wrote no verdict (exit {done.returncode}): "
                                 f"{done.stderr.decode(errors='replace').strip()[-300:]}")  # fmt: skip
        return entry | {"verdict": verdict[0], "reasons": verdict[1], "gate_exit": done.returncode}
    finally:
        git("worktree", "remove", "--force", str(tree))


def rule_all(observation: dict[str, Any]) -> list[dict[str, Any]]:
    swaps = observation.get("swaps") if isinstance(observation, dict) else None
    ruled = []
    deadline = time.monotonic() + BUDGET_SECONDS
    with tempfile.TemporaryDirectory() as scratch:
        for swap in swaps if isinstance(swaps, list) else []:
            swap = swap if isinstance(swap, dict) else {}
            left = deadline - time.monotonic()
            try:
                if left <= 0:
                    ruled.append(unread({key: swap.get(key) for key in KEPT}, "the read's budget was spent"))
                    continue
                ruled.append(rule_one(swap, Path(scratch), left))
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
