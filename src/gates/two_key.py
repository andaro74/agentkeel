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
- a change under `evals/history/**` in a commit that is not the bot's;

and from M03 PR 2 the entries ADR-0009 added:

1. a `relaxes:` entry whose value changes, or which is removed while its
   bar stays;
2. a bar deleted from `thresholds.yaml`, or no longer a numeric leaf;
3. a manifest's `max_tokens_per_session` or `daily_usd` raised, set to
   null, or removed (the Threshold Owner's key);
4. a manifest's `guardrail` set to null or removed from a value, or its
   `id` changed (the Rule Owner's key). Null to a value is not one;
5. in a file under `rules/**` or `agents/*/rules/**`, an entry removed
   from a list or a mapping (a denied topic, a PII type, a plant id, a
   `blocks` entry; a rename is a removal and an addition), an action
   weakened (BLOCK to MASK or NONE, MASK to NONE; ANONYMIZE is MASK), a
   `blocks` entry pointed at another rule, or `topics_apply_to` narrowed
   (`rule-owner` on M03 PR 2: "input and output" to "input" turns the
   answer side's BLOCK to NONE). A definition's wording is not read.

Two keys are two ruling files with this PR's `pr:`, their `seat:` distinct.
The file of the seat that owns the path covers it (SPEC/02 §2 "Covers");
the other names the path, exactly, in its `keys:` (ADR-0009; until M03 PR
2 its `authorises:` or its body, M01 PR 1 ruling B). Two files from one
seat are one key: the gate counts seats, not files. Engineering's file
counts like any other seat's (SPEC/02 §2).

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
    """`section.name[.more]` -> value for every numeric leaf, at any depth. `baseline_card` is a pin, not a bar;
    `relaxes` is the map.

    It read one level deep until M03 PR 2 (M03 open.md row 4): a bar nested
    deeper could move with no key. R10's N and M04's `delta_max` land as bars
    with their `relaxes:` entries when their milestones write them.
    """
    out: dict[str, Any] = {}

    def walk(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for name, leaf in value.items():
                walk(f"{prefix}.{name}", leaf)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            out[prefix] = value

    for section, value in thresholds.items():
        if section not in ("baseline_card", "relaxes") and isinstance(value, dict):
            walk(section, value)
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


# ADR-0009 entry 5: how strong an action is. ANONYMIZE is Bedrock's word for MASK.
ACTION_STRENGTH = {"BLOCK": 3, "BLOCKED": 3, "MASK": 2, "MASKED": 2, "ANONYMIZE": 2, "NONE": 1}
APPLIES_TO_STRENGTH = {"input and output": 2, "input": 1}
# A content filter's strength, as Bedrock names it (the second cold read of PR 2, F2).
FILTER_STRENGTH = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
IDENTITY_KEYS = ("name", "entity", "id", "type")


def _identity(item: Any) -> str:
    """How a list entry is known across two versions of a file: its name, entity, id or type, or itself."""
    if isinstance(item, dict):
        for key in IDENTITY_KEYS:
            if key in item:
                return str(item[key])
        return repr(sorted(item.items()))
    return str(item)


def _entries(node: Any, at: str = "") -> dict[str, Any]:
    """Every entry of a rules file by its path: `a.b`, `a[name]`, `a[name].action`. Values are the leaves."""
    out: dict[str, Any] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{at}.{key}" if at else str(key)
            out[path] = value if not isinstance(value, (dict, list)) else None
            out.update(_entries(value, path))
    elif isinstance(node, list):
        for item in node:
            path = f"{at}[{_identity(item)}]"
            out[path] = item if not isinstance(item, (dict, list)) else None
            out.update(_entries(item, path))
    return out


def rule_relaxations(before_text: str | None, after_text: str | None) -> list[str]:
    """ADR-0009 entry 5, for one file under rules/**: what was removed, weakened or re-pointed."""
    try:
        before = yaml.safe_load(before_text or "")
    except yaml.YAMLError:
        return []  # not YAML on the base (a markdown rule): only its deletion is read, as before
    if not isinstance(before, (dict, list)):
        return []
    try:
        after = yaml.safe_load(after_text or "")
    except yaml.YAMLError:
        return ["the file no longer parses: every entry removed"]  # the second cold read of PR 2, F1
    if not isinstance(after, (dict, list)):
        after = {}  # emptied, or comments only: every entry removed
    old, new = _entries(before), _entries(after)
    found = []
    for path in sorted(old):
        if path not in new:
            found.append(f"{path} removed")
            continue
        was, now = old[path], new[path]
        if was is True and now is False:  # a rule's switch turned off (prompt_attack: on -> off)
            found.append(f"{path} on -> off weakened")
        elif isinstance(was, str) and isinstance(now, str) and was.upper() in FILTER_STRENGTH \
                and now.upper() in FILTER_STRENGTH and was.upper() not in ACTION_STRENGTH:
            if FILTER_STRENGTH[now.upper()] < FILTER_STRENGTH[was.upper()]:
                found.append(f"{path} {was} -> {now} weakened")
        elif isinstance(was, str) and isinstance(now, str):
            key = path.rsplit(".", 1)[-1]
            if was.upper() in ACTION_STRENGTH and now.upper() in ACTION_STRENGTH:
                if ACTION_STRENGTH[now.upper()] < ACTION_STRENGTH[was.upper()]:
                    found.append(f"{path} {was} -> {now} weakened")
            elif key == "topics_apply_to" and APPLIES_TO_STRENGTH.get(now, 0) < APPLIES_TO_STRENGTH.get(was, 0):
                found.append(f"{path} {was!r} -> {now!r} narrowed")
            elif ".blocks." in f".{path}" and was != now:
                found.append(f"{path} {was} -> {now} pointed at another rule")
    return found


def _version_key(value: Any) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", str(value)))


def relaxations(tree: Tree, base: Tree) -> list[Relaxation]:
    owners, _ = owner_table(base, tree)
    found: list[Relaxation] = []
    history: replay_history.History | None = None
    for path in changed(base, tree):
        owner = owners.owner(path)
        if path == THRESHOLDS:
            before_t, after_t = _load(base.text(path)), _load(tree.text(path))
            for move in threshold_moves(before_t, after_t):
                found.append(Relaxation(path, move, owner))
            # ADR-0009 entries 1 and 2.
            old_bars, new_bars = bars(before_t), bars(after_t)
            for bar in sorted(set(old_bars) - set(new_bars)):
                found.append(Relaxation(path, f"{bar} deleted, or no longer a numeric bar (ADR-0009 entry 2)", owner))
            old_rel, new_rel = before_t.get("relaxes") or {}, after_t.get("relaxes") or {}
            for bar in sorted(old_rel):
                if bar in new_rel and new_rel[bar] != old_rel[bar]:
                    found.append(Relaxation(path, f"relaxes.{bar} {old_rel[bar]} -> {new_rel[bar]} (ADR-0009 entry 1)", owner))
                elif bar not in new_rel and bar in new_bars:
                    found.append(Relaxation(path, f"relaxes.{bar} removed while its bar stays (ADR-0009 entry 1)", owner))
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
        elif RULES.match(path) and path in base.files():
            for what in rule_relaxations(base.text(path), tree.text(path)):
                found.append(Relaxation(path, f"{what} (ADR-0009 entry 5)", owner))
        elif MANIFEST.match(path):
            before, after = _load(base.text(path)), _load(tree.text(path))
            old_guard, new_guard = before.get("guardrail") or {}, after.get("guardrail") or {}
            versions = old_guard.get("version"), new_guard.get("version")
            if None not in versions and _version_key(versions[1]) < _version_key(versions[0]):
                found.append(Relaxation(path, f"guardrail version {versions[0]} -> {versions[1]} moved down", "Rule Owner"))
            # ADR-0009 entry 4: a guardrail set to null or removed from a value, or its id changed.
            if before.get("guardrail") and not after.get("guardrail"):
                found.append(Relaxation(path, "guardrail set to null or removed (ADR-0009 entry 4)", "Rule Owner"))
            elif old_guard.get("id") and new_guard.get("id") and old_guard["id"] != new_guard["id"]:
                found.append(Relaxation(path, f"guardrail id {old_guard['id']} -> {new_guard['id']} (ADR-0009 entry 4)",
                                        "Rule Owner"))  # fmt: skip
            # ADR-0009 entry 3: a budget raised, set to null or removed. The Threshold Owner's key.
            for budget in ("max_tokens_per_session", "daily_usd"):
                was, now = before.get(budget), after.get(budget)
                if was is None:
                    continue
                if now is None:
                    found.append(Relaxation(path, f"{budget} {was} set to null or removed (ADR-0009 entry 3)", "Threshold Owner"))
                elif isinstance(now, (int, float)) and isinstance(was, (int, float)) and now > was:
                    found.append(Relaxation(path, f"{budget} {was} -> {now} raised (ADR-0009 entry 3)", "Threshold Owner"))
            old_mem, new_mem = before.get("memory"), after.get("memory")
            if isinstance(old_mem, dict):
                if after.get("memory") is None:  # set to null, or the key deleted outright (cold review of PR 2, F5)
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
