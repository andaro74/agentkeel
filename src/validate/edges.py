"""`validate`: edges declared on both sides, no cycle, ceilings within bounds (SPEC/00 §5; SPEC/02 §6).

An edge is `may_call: [<callee>@v<major>]` on the caller and
`may_be_called_by: [<caller>@v<major>]` on the callee, each naming the
other (SPEC/02 §2). One side alone is refused, naming the side that is
missing; seed S3 is the caller's side alone. The call graph over
`may_call` has no cycle. A manifest's `ceilings` stay within the
`ceilings:` bounds in `thresholds.yaml` (Threshold Owner); a manifest with
an edge and no ceilings is refused, since the bounds would then bind
nothing.

`check(tree)` reads `agents/*/manifest.yaml` and `thresholds.yaml` under
`tree`, which is the repository root in `make validate` and a worktree with
a seed applied in `tests/test_m02_seeds.py`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

EDGE = re.compile(r"^([a-z][a-z0-9-]{2,30})@v([0-9]+)$")
CEILING_NAMES = ("concurrency", "rps_per_edge", "depth", "fan_out")


def manifests(tree: Path) -> dict[str, dict[str, Any]]:
    """Agent name -> manifest, for every agents/*/manifest.yaml that is a mapping."""
    out = {}
    for path in sorted((tree / "agents").glob("*/manifest.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict):
            out[path.parent.name] = doc
    return out


def _edges(manifest: dict[str, Any], key: str) -> list[tuple[str, str]]:
    """(agent, major) for each well-formed entry; malformed ones are the schema check's."""
    found = []
    for entry in manifest.get(key) or []:
        if isinstance(entry, str) and (match := EDGE.match(entry)):
            found.append((match[1], match[2]))
    return found


def two_sided(tree: Path) -> list[str]:
    errors = []
    all_manifests = manifests(tree)
    for name, manifest in all_manifests.items():
        rel = f"agents/{name}/manifest.yaml"
        for callee, major in _edges(manifest, "may_call"):
            edge = f"{callee}@v{major}"
            other = all_manifests.get(callee)
            if other is None:
                errors.append(f"{rel}: may_call {edge}, and no agents/{callee}/manifest.yaml exists to say may_be_called_by {name}: one-sided")
            elif name not in {a for a, _ in _edges(other, "may_be_called_by")}:
                errors.append(f"{rel}: may_call {edge}, and agents/{callee}/manifest.yaml may_be_called_by does not name {name}: one-sided")
            elif _major_of(other) != major:
                errors.append(f"{rel}: may_call {edge} names major {major}, and agents/{callee}/manifest.yaml is at major {_major_of(other)}: not the same major")
        for caller, major in _edges(manifest, "may_be_called_by"):
            edge = f"{caller}@v{major}"
            other = all_manifests.get(caller)
            if other is None:
                errors.append(f"{rel}: may_be_called_by {edge}, and no agents/{caller}/manifest.yaml exists to say may_call {name}: one-sided")
            elif name not in {a for a, _ in _edges(other, "may_call")}:
                errors.append(f"{rel}: may_be_called_by {edge}, and agents/{caller}/manifest.yaml may_call does not name {name}: one-sided")
            elif _major_of(other) != major:
                errors.append(f"{rel}: may_be_called_by {edge} names major {major}, and agents/{caller}/manifest.yaml is at major {_major_of(other)}: not the same major")
    return errors


def _major_of(manifest: dict[str, Any]) -> str:
    """The major of a manifest's `version`; `1` when it has none (tool-owner on PR 2: an edge is at the same major)."""
    match = re.match(r"^\s*v?(\d+)\.", str(manifest.get("version") or "1.0.0"))
    return match[1] if match else "?"


def cycles(tree: Path) -> list[str]:
    graph = {name: [callee for callee, _ in _edges(m, "may_call")] for name, m in manifests(tree).items()}
    errors = []
    state: dict[str, int] = {}  # 1 on the stack, 2 done

    def visit(node: str, path: list[str]) -> None:
        state[node] = 1
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                cycle = path[path.index(nxt):] + [nxt]
                errors.append(f"agents/{node}/manifest.yaml: may_call closes a cycle: {' -> '.join(cycle)}")
            elif state.get(nxt) is None:
                visit(nxt, path + [nxt])
        state[node] = 2

    for name in sorted(graph):
        if state.get(name) is None:
            visit(name, [name])
    return errors


def ceilings(tree: Path) -> list[str]:
    thresholds_path = tree / "thresholds.yaml"
    try:
        thresholds = yaml.safe_load(thresholds_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return [f"thresholds.yaml: unreadable: {exc}"]
    bounds = thresholds.get("ceilings") if isinstance(thresholds, dict) else None
    if not isinstance(bounds, dict) or set(bounds) != set(CEILING_NAMES):
        return [f"thresholds.yaml: ceilings must name exactly {list(CEILING_NAMES)} (Threshold Owner)"]
    errors = []
    for name, manifest in manifests(tree).items():
        rel = f"agents/{name}/manifest.yaml"
        asked = manifest.get("ceilings")
        has_edge = bool(manifest.get("may_call") or manifest.get("may_be_called_by"))
        if not isinstance(asked, dict):
            if has_edge:
                errors.append(f"{rel}: declares an edge and no ceilings; the bounds in thresholds.yaml would bind nothing")
            continue
        for key in CEILING_NAMES:
            value = asked.get(key)
            if value is None:
                errors.append(f"{rel}: ceilings.{key} missing")
            elif isinstance(value, (int, float)) and value > bounds[key]:
                errors.append(f"{rel}: ceilings.{key} {value} is over the bound {bounds[key]} in thresholds.yaml")
    return errors


def check(tree: Path) -> list[str]:
    """Edges two-sided, then no cycle, then ceilings within bounds; every error, not the first."""
    return two_sided(tree) + cycles(tree) + ceilings(tree)
