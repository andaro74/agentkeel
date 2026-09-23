"""`validate`: computed semver (SPEC/00 §5 Tool Owner, R7; SPEC/02 §6).

The version a change needs is computed from the diff against the base,
never chosen: a change to a tool schema's `input` or `output` is a major
bump of that schema's own `version`; a change to an agent's edges
(`may_call`, `may_be_called_by`) or a major bump of any of its tool
schemas is a major bump of the manifest's `version`; and an edge
`<agent>@v<N>` names the major of that agent's manifest `version`. A
manifest with no `version` is at `1.0.0` (refagent's, unchanged since M01,
so that its bundle digest does not move for a field nothing reads yet).

`check(tree, base)` fails when the tree asserts a smaller version than the
diff computes to. The base is resolved as `golden_ids.default_base` does.
Cut-list item 3 of SPEC/02 §9; M07's upgrade is its first real case.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from src.gates import Tree
from src.validate.golden_ids import default_base

TOOL = re.compile(r"^agents/([^/]+)/tools/[^/]+\.json$")
MANIFEST = re.compile(r"^agents/([^/]+)/manifest\.yaml$")
EDGE = re.compile(r"^([a-z][a-z0-9-]{2,30})@v([0-9]+)$")
DEFAULT_VERSION = "1.0.0"


def parse_version(value: Any) -> tuple[int, int, int] | None:
    if value is None:
        value = DEFAULT_VERSION
    match = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)\s*$", str(value))
    return (int(match[1]), int(match[2]), int(match[3])) if match else None


def _json(tree: Tree, path: str) -> dict[str, Any] | None:
    text = tree.text(path)
    if text is None:
        return None
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        return None
    return doc if isinstance(doc, dict) else None


def _yaml(tree: Tree, path: str) -> dict[str, Any] | None:
    text = tree.text(path)
    if text is None:
        return None
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def compare(tree: Tree, base: Tree) -> list[str]:
    errors = []
    tools_bumped: dict[str, list[str]] = {}
    for path in sorted(tree.files()):
        if not (match := TOOL.match(path)):
            continue
        after, before = _json(tree, path), _json(base, path)
        if after is None:
            errors.append(f"{path}: not a JSON object")
            continue
        new = parse_version(after.get("version"))
        if new is None:
            errors.append(f"{path}: version {after.get('version')!r} is not major.minor.patch")
            continue
        if before is None:
            continue  # a new schema starts wherever it likes
        old = parse_version(before.get("version")) or (0, 0, 0)
        contract_changed = any(before.get(k) != after.get(k) for k in ("input", "output"))
        if contract_changed:
            tools_bumped.setdefault(match[1], []).append(path)
            if new[0] <= old[0]:
                errors.append(
                    f"{path}: input or output changed, which is a major bump (R7); version {'.'.join(map(str, old))} -> "
                    f"{'.'.join(map(str, new))} asserts less than {old[0] + 1}.0.0"
                )
        elif new < old:
            errors.append(f"{path}: version moved down, {'.'.join(map(str, old))} -> {'.'.join(map(str, new))}")

    # A tool schema on the base and gone from the tree is a contract change
    # too (tool-owner on PR 2, F1): the first draft walked the tree only.
    for path in sorted(base.files() - tree.files()):
        if match := TOOL.match(path):
            tools_bumped.setdefault(match[1], []).append(f"{path} (removed)")

    majors: dict[str, int] = {}
    for path in sorted(tree.files()):
        if not (match := MANIFEST.match(path)):
            continue
        name = match[1]
        after, before = _yaml(tree, path), _yaml(base, path)
        if after is None:
            continue  # the schema check reports it
        new = parse_version(after.get("version"))
        if new is None:
            errors.append(f"{path}: version {after.get('version')!r} is not major.minor.patch")
            continue
        majors[name] = new[0]
        if before is None:
            continue
        old = parse_version(before.get("version")) or (1, 0, 0)
        edges_changed = any(sorted(before.get(k) or []) != sorted(after.get(k) or []) for k in ("may_call", "may_be_called_by"))
        why = []
        if edges_changed:
            why.append("an edge changed")
        if name in tools_bumped:
            why.append(f"a tool schema took a major bump ({', '.join(tools_bumped[name])})")
        if why and new[0] <= old[0]:
            errors.append(
                f"{path}: {' and '.join(why)}, which is a major bump of the manifest (R7); version "
                f"{'.'.join(map(str, old))} -> {'.'.join(map(str, new))} asserts less than {old[0] + 1}.0.0"
            )
        elif new < old:
            errors.append(f"{path}: version moved down, {'.'.join(map(str, old))} -> {'.'.join(map(str, new))}")

    for path in sorted(tree.files()):
        if not (match := MANIFEST.match(path)):
            continue
        manifest = _yaml(tree, path) or {}
        for key in ("may_call", "may_be_called_by"):
            for entry in manifest.get(key) or []:
                if isinstance(entry, str) and (edge := EDGE.match(entry)) and edge[1] in majors and int(edge[2]) != majors[edge[1]]:
                    errors.append(
                        f"{path}: {key} {entry} names major {edge[2]}, and agents/{edge[1]}/manifest.yaml is at major {majors[edge[1]]}"
                    )
    return errors


def check(tree: Path, base: str | Path | None = None) -> list[str]:
    if base is None:
        base = default_base(tree)
        if base is None:
            return ["agents/: no origin/main to compute versions against (fetch it)"]
    return compare(Tree(tree), Tree(base, repo=Path(tree)))
