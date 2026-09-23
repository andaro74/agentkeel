"""`ruling-cited` (SPEC/00 §5, SPEC/02 §6): every seat-owned path a PR changes is covered by a ruling.

    python -m src.gates.ruling_cited --base <sha> --pr <number> [--tree <dir>]

For every path in the diff between the base and the PR's merge ref, the
CODEOWNERS owner is read **from the base** (never from the PR, so a PR
cannot move a path to a seat whose ruling it carries; the PR that first
adds CODEOWNERS is read against its own table and the output says so).
For each such path there must be a ruling file in the merge ref whose
`pr:` is this PR, whose `seat:` is that owner and whose `authorises:`
matches the path. A ruling file with this PR's `pr:` covers itself
(SPEC/02 §2). A path under `evals/history/**` whose commits are all
`github-actions[bot]`'s is exempt. A manifest is attributed field by field.

Exit 1 with **every** uncovered path listed, never the first alone. Each
is a line `uncovered <path>: ...` in the job log, which
`scripts/observe_pr.py` reads for the seed PRs at M02 PR 3.

What this does not do: judge the ruling. A file with the right seat, the
right glob and the right number is a ruling, whatever it says. R1: every
seat is one person, and no gate waits for a human.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.gates import (
    HISTORY,
    RULING_GLOB,
    Tree,
    bot_only,
    changed,
    owner_table,
    rulings,
    seats_of,
)
from src.verdict import ROOT


def uncovered(tree: Tree, base: Tree, pr: int) -> tuple[list[str], str]:
    """Every changed path that no ruling with this PR's number covers, and where CODEOWNERS was read."""
    owners, where = owner_table(base, tree)
    keys = rulings(tree, pr)
    own = {k.path for k in keys}
    lines: list[str] = []
    for path in changed(base, tree):
        if path.startswith(HISTORY) and bot_only(tree, base, path):
            continue
        if RULING_GLOB.match(path) and path in own:
            continue  # a ruling file with this PR's pr: covers itself
        for seat, detail in seats_of(path, base, tree, owners):
            if seat is None:
                lines.append(f"{path}: no seat owns it (SPEC/00 section 5: a file no seat owns is deleted, not adopted)")
            elif not any(k.covers(path, seat) for k in keys):
                lines.append(f"{path}{detail}: owned by {seat}; no ruling file with pr: {pr} and seat: {seat} authorises it")
    return lines, where


def refusal(tree: str | Path, base: str | Path = ROOT, pr: int = 0) -> str | None:
    """None when every changed seat-owned path is covered; otherwise the whole list, as one string."""
    lines, where = uncovered(Tree(tree), Tree(base), pr)
    if not lines:
        return None
    head = f"ruling-cited: {len(lines)} uncovered path(s) in the diff (CODEOWNERS read from {where}):"
    return "\n".join([head, *(f"  uncovered {line}" for line in lines)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="the base ref: a commit, or a checkout directory")
    parser.add_argument("--tree", default=str(ROOT), help="the PR's merge ref as a checkout (default: this tree)")
    parser.add_argument("--pr", required=True, type=int)
    args = parser.parse_args(argv)
    if (refused := refusal(args.tree, args.base, args.pr)) is None:
        print(f"ruling-cited: every seat-owned path in the diff is covered by a ruling with pr: {args.pr}")
        return 0
    print(refused)
    return 1


if __name__ == "__main__":
    sys.exit(main())
