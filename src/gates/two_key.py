"""`two-key` (SPEC/00 §5, SPEC/02 §2 and §6): a relaxation needs rulings from two distinct seats.

    python -m src.gates.two_key --base <sha> --pr <number> [--tree <dir>]

A relaxation is one of the closed list in SPEC/02 §2, read against the
base ref and the history:

- a bar in `thresholds.yaml` moved in the direction its `relaxes:` entry
  names (a bar with no entry cannot be moved with one key either);
- a golden's `retired` set from null;
- a golden's `expected` changed on an id that has ever passed in
  `evals/history/`;
- a file under `rules/**` or `agents/*/rules/**` deleted, or a manifest's
  guardrail version moved down;
- a manifest's `memory.retention_days` shortened, or memory removed;
- a change under `evals/history/**` in a commit that is not the bot's.

Two keys are two ruling files with this PR's `pr:`, their `seat:` distinct.
The file of the seat that owns the path covers it (SPEC/02 §2 "Covers");
the other names the path in its `authorises:` or its body (M01 PR 1, ruling
B). Two files from one seat are one key: the gate counts seats, not files.
Engineering's file counts like any other seat's (SPEC/02 §2).

Exit 1 with every unkeyed relaxation listed. Adding to the list is a
SPEC/00 §5 amendment, not an edit here.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.gates import HISTORY, Tree, bot_only, changed, owner_table, rulings
from src.verdict import ROOT, replay_history

THRESHOLDS = "thresholds.yaml"
GOLDEN = re.compile(r"^evals/goldens/v[0-9]+/g-[0-9]{3}\.yaml$")
RULES = re.compile(r"^(rules/|agents/[^/]+/rules/).+")
MANIFEST = re.compile(r"^agents/[^/]+/manifest\.yaml$")


@dataclass(frozen=True)
class Relaxation:
    path: str
    what: str
    seat: str | None  # the path's owner under the base's CODEOWNERS


def _load(text: str | None) -> dict[str, Any]:
    if text is None:
        return {}
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return doc if isinstance(doc, dict) else {}


def bars(thresholds: dict[str, Any]) -> dict[str, Any]:
    """`section.name` -> value for every numeric leaf. `baseline_card` is a pin, not a bar; `relaxes` is the map."""
    out: dict[str, Any] = {}
    for section, value in thresholds.items():
        if section in ("baseline_card", "relaxes") or not isinstance(value, dict):
            continue
        for name, leaf in value.items():
            if isinstance(leaf, (int, float)) and not isinstance(leaf, bool):
                out[f"{section}.{name}"] = leaf
    return out


def threshold_moves(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """Each bar that moved in the direction that relaxes it, with the move spelled out."""
    relaxes = {**(after.get("relaxes") or {}), **(before.get("relaxes") or {})}  # the base's word wins
    old, new = bars(before), bars(after)
    moves = []
    for bar in sorted(set(old) & set(new)):
        if old[bar] == new[bar]:
            continue
        direction = relaxes.get(bar)
        if direction == "up" and new[bar] > old[bar] or direction == "down" and new[bar] < old[bar]:
            moves.append(f"{bar} {old[bar]} -> {new[bar]} relaxes it (relaxes: {direction})")
        elif direction not in ("up", "down"):
            moves.append(f"{bar} {old[bar]} -> {new[bar]} with no relaxes: entry, so the direction that relaxes it is unknown")
    return moves


def _history(tree: Tree, base: Tree) -> replay_history.History:
    for candidate in (tree, base):
        if candidate.dir is not None:
            return replay_history.load(candidate.dir / "evals" / "history")
    return replay_history.load(ROOT / "evals" / "history")


def _ever_passed(history: replay_history.History, golden_id: str) -> list[str]:
    return sorted(scope for scope in ("agent", "control") if replay_history.ever_passed(history, scope, golden_id))


def _version_key(value: Any) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", str(value)))


def relaxations(tree: Tree, base: Tree) -> list[Relaxation]:
    owners, _ = owner_table(base, tree)
    found: list[Relaxation] = []
    history: replay_history.History | None = None
    for path in changed(base, tree):
        owner = owners.owner(path)
        if path == THRESHOLDS:
            for move in threshold_moves(_load(base.text(path)), _load(tree.text(path))):
                found.append(Relaxation(path, move, owner))
        elif GOLDEN.match(path) and path in base.files() and path in tree.files():
            before, after = _load(base.text(path)), _load(tree.text(path))
            golden_id = str(before.get("id"))
            if before.get("retired") is None and after.get("retired") is not None:
                found.append(Relaxation(path, f"{golden_id} retired (retired: {after.get('retired')})", owner))
            if before.get("expected") != after.get("expected"):
                history = _history(tree, base) if history is None else history
                if scopes := _ever_passed(history, golden_id):
                    found.append(Relaxation(
                        path, f"expected changed on {golden_id}, which has passed in evals/history ({', '.join(scopes)})", owner
                    ))  # fmt: skip
        elif RULES.match(path) and path in base.files() and path not in tree.files():
            found.append(Relaxation(path, "a rule deleted", owner))
        elif MANIFEST.match(path):
            before, after = _load(base.text(path)), _load(tree.text(path))
            old_guard, new_guard = before.get("guardrail") or {}, after.get("guardrail") or {}
            versions = old_guard.get("version"), new_guard.get("version")
            if None not in versions and _version_key(versions[1]) < _version_key(versions[0]):
                found.append(Relaxation(path, f"guardrail version {versions[0]} -> {versions[1]} moved down", "Rule Owner"))
            old_mem, new_mem = before.get("memory"), after.get("memory")
            if isinstance(old_mem, dict):
                if new_mem is None and "memory" in after:
                    found.append(Relaxation(path, "memory removed (retention shortened to nothing)", owner))
                elif isinstance(new_mem, dict) and (new_mem.get("retention_days") or 0) < (old_mem.get("retention_days") or 0):
                    found.append(Relaxation(
                        path, f"memory.retention_days {old_mem.get('retention_days')} -> {new_mem.get('retention_days')} shortened", owner
                    ))  # fmt: skip
        elif path.startswith(HISTORY) and not bot_only(tree, base, path):
            found.append(Relaxation(path, f"changed under {HISTORY} by a commit that is not {'github-actions[bot]'}'s", owner))
    return found


def unkeyed(tree: Tree, base: Tree, pr: int) -> list[str]:
    keys = rulings(tree, pr)
    lines = []
    for r in relaxations(tree, base):
        owner_keys = [k for k in keys if k.covers(r.path, r.seat)]
        other_keys = [k for k in keys if k.seat is not None and k.seat != r.seat and k.names(r.path)]
        seats = sorted({k.seat for k in owner_keys + other_keys if k.seat})
        if owner_keys and len(seats) >= 2:
            continue
        held = ", ".join(f"{k.seat} ({k.path})" for k in owner_keys + other_keys) or "none"
        count = {0: "no seat holds a key", 1: "one seat holds a key"}.get(len(seats), f"{len(seats)} seats hold keys")
        need = "" if owner_keys else f"; the owner seat {r.seat} holds none"
        lines.append(
            f"{r.path}: {r.what}; two keys from two distinct seats are needed and {count}: {held}{need}. "
            "Two files from the same seat are one key."
        )
    return lines


def refusal(tree: str | Path, base: str | Path = ROOT, pr: int = 0) -> str | None:
    lines = unkeyed(Tree(tree), Tree(base), pr)
    if not lines:
        return None
    return "\n".join([f"two-key: {len(lines)} relaxation(s) without two keys:", *(f"  unkeyed {line}" for line in lines)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="the base ref: a commit, or a checkout directory")
    parser.add_argument("--tree", default=str(ROOT), help="the PR's merge ref as a checkout (default: this tree)")
    parser.add_argument("--pr", required=True, type=int)
    args = parser.parse_args(argv)
    found = relaxations(Tree(args.tree), Tree(args.base))
    if (refused := refusal(args.tree, args.base, args.pr)) is None:
        what = "; ".join(f"{r.path}: {r.what}" for r in found) or "no relaxation in the diff"
        print(f"two-key: {what}" + (f" (two keys with pr: {args.pr} found)" if found else ""))
        return 0
    print(refused)
    return 1


if __name__ == "__main__":
    sys.exit(main())
