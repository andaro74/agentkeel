"""`validate`: every agent brings its own goldens, at or over the minimum (SPEC/06 §2, S1b's reader).

For each `agents/<name>/` that is not an exemption below: `goldens/g-NNN.yaml`
in SPEC/00 §6's shape, of the four kinds, and **at least one live ordinary
and one live trap** (a retired golden does not count). An ordinary or trap
golden cites a row of the agent's own `data/table.json` (rows keyed by
`table_row`) and a clause of its own `data/clauses.json` (ruled by the Data
Owner at M06 PR 2, `milestones/M06/feasibility.md` §8, R5). Fewer, or a
citation that is not in the agent's data, is refused with the agent's path.
From M09 PR 2 (SPEC/09 §2, §6) a guardrail or red-team golden is a plant:
`expected` BLOCKED (or MASKED for a guardrail golden), no citation, and its
control file in the agent's `rules/` names it in `plants` with a `blocks`
entry, or it is refused (F9.4).

Two exemptions, each named, and neither available to an agent repository
(`src/validate/agent.py` refuses both names):

- `refagent`: its goldens are `evals/goldens/v1/`, which the base checks read.
- `ratings-helper`: a manifest-only stub until its code lands at M07
  (SPEC/00 §8 M07); nothing deploys it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from src.gates import canonical_seat

EXEMPT = {
    "refagent": "its goldens are evals/goldens/v1/",
    "ratings-helper": "a manifest-only stub until M07; nothing deploys it",
}
FIELDS = {"id", "kind", "question", "expected", "seat", "added", "retired"}
# M09 PR 2 (SPEC/09 §2, §6; seed S1): the four kinds. A guardrail or red-team golden is a plant: `expected`
# is BLOCKED (or MASKED for a guardrail golden), it cites no row, and its control file in rules/ must name
# it in `plants` with a `blocks` entry (the other direction, a plant with no golden, is agent_rules').
KINDS = ("ordinary", "trap", "guardrail", "redteam")
CITING = ("ordinary", "trap")
PLANT_EXPECTED = {"guardrail": ("BLOCKED", "MASKED"), "redteam": ("BLOCKED",)}
PLANT_CONTROL = {"guardrail": "rules/guardrail.yaml", "redteam": "rules/redteam.yaml"}
GOLDEN_ID = re.compile(r"^g-\d{3}$")
MILESTONE_ID = re.compile(r"^M\d{2}$")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def agent_dirs(root: Path) -> list[Path]:
    return sorted(p.parent for p in (root / "agents").glob("*/manifest.yaml"))


def _plants_of(control: Path) -> set[str] | None:
    """The ids a control file names in `plants` with a `blocks` entry; None when there is no such file."""
    if not control.is_file():
        return None
    try:
        doc = yaml.safe_load(control.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return set()
    if not isinstance(doc, dict) or not isinstance(doc.get("plants"), list):
        return set()
    blocks = doc.get("blocks") if isinstance(doc.get("blocks"), dict) else {}
    return {g for g in doc["plants"] if isinstance(g, str) and isinstance(blocks.get(g), str) and blocks[g]}


def check_agent(agent: Path, rel: str) -> list[str]:
    """Errors for one agent folder, each starting with `rel` (its path as the reader names it)."""
    errors: list[str] = []
    table = _load_json(agent / "data" / "table.json")
    clauses = _load_json(agent / "data" / "clauses.json")
    rows: set[str] | None = None
    if not isinstance(table, list):
        errors.append(f"{rel}data/table.json: missing or not a list of rows keyed by table_row")
    else:
        keys = [r.get("table_row") if isinstance(r, dict) else None for r in table]
        bad = [i for i, key in enumerate(keys) if not isinstance(key, str) or not key]
        twice = sorted({key for key in keys if isinstance(key, str) and keys.count(key) > 1})
        if bad:
            errors.append(f"{rel}data/table.json: rows {bad[:5]} have no table_row string; every row is keyed by one")
        if twice:
            errors.append(f"{rel}data/table.json: table_row {twice[:5]} appear more than once; a key is one row")
        rows = {key for key in keys if isinstance(key, str) and key}
    if not isinstance(clauses, dict):
        errors.append(f"{rel}data/clauses.json: missing or not a mapping of clause ids")
        clauses = None

    planted = {kind: _plants_of(agent / control) for kind, control in PLANT_CONTROL.items()}
    live: dict[str, int] = {kind: 0 for kind in KINDS}
    for path in sorted((agent / "goldens").glob("*.yaml")):
        where = f"{rel}goldens/{path.name}"
        try:
            golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            errors.append(f"{where}: not YAML")
            continue
        if not isinstance(golden, dict):
            errors.append(f"{where}: not a mapping")
            continue
        if set(golden) != FIELDS:
            errors.append(f"{where}: fields {sorted(golden)}, SPEC/00 section 6 asks {sorted(FIELDS)}")
            continue
        if not GOLDEN_ID.match(str(golden["id"])) or f"{golden['id']}.yaml" != path.name:
            errors.append(f"{where}: id {golden['id']!r} is not g-NNN or not the file's name")
        if golden["kind"] not in KINDS:
            errors.append(f"{where}: kind {golden['kind']!r}; an agent's goldens are ordinary, trap, guardrail or redteam")
            continue
        if not isinstance(golden["question"], str) or not golden["question"].strip():
            errors.append(f"{where}: no question")
        if canonical_seat(golden["seat"]) != "Data Owner":
            errors.append(f"{where}: seat {golden['seat']!r}, not the Data Owner")
        if not MILESTONE_ID.match(str(golden["added"])):
            errors.append(f"{where}: added {golden['added']!r} is not a milestone id")
        if golden["retired"] is not None and not MILESTONE_ID.match(str(golden["retired"])):
            errors.append(f"{where}: retired {golden['retired']!r} is neither null nor a milestone id")
        expected = golden["expected"]
        if golden["kind"] not in CITING:
            # A plant (M09 PR 2): expected shaped for its kind, named by its control with a blocks entry.
            kind, shapes = golden["kind"], PLANT_EXPECTED[golden["kind"]]
            if expected not in shapes:
                errors.append(f"{where}: expected {expected!r}; a {kind} golden expects {' or '.join(shapes)}")
            named = planted[kind]
            if named is None:
                errors.append(f"{where}: a {kind} golden with no {rel}{PLANT_CONTROL[kind]} to plant it (F9.4)")
            elif golden["id"] not in named:
                errors.append(f"{where}: a {kind} golden {rel}{PLANT_CONTROL[kind]} does not name in plants with a "
                              f"blocks entry; a plant with no named rule is one nobody could see fire (F9.4)")  # fmt: skip
            if golden["retired"] is None:
                live[kind] += 1
            continue
        if not isinstance(expected, dict) or set(expected) != {"table_row", "clause_id", "answer_fields"}:
            errors.append(f"{where}: expected must carry table_row, clause_id and answer_fields")
            continue
        if not isinstance(expected["answer_fields"], dict) or not expected["answer_fields"]:
            errors.append(f"{where}: answer_fields is empty")
        if not all(isinstance(expected[k], str) and expected[k] for k in ("table_row", "clause_id")):
            errors.append(f"{where}: table_row and clause_id are each one id, a string")
            continue
        if rows is not None and expected["table_row"] not in rows:
            errors.append(f"{where}: table_row {expected['table_row']!r} is not a row of {rel}data/table.json")
        if clauses is not None and expected["clause_id"] not in clauses:
            errors.append(f"{where}: clause_id {expected['clause_id']!r} is not in {rel}data/clauses.json")
        if golden["retired"] is None:
            live[golden["kind"]] += 1

    short = [f"{live[kind]} {kind}" for kind in CITING if live[kind] < 1]
    if short:
        errors.append(f"{rel}goldens/: {', '.join(short)}: under the minimum of one ordinary and one trap "
                      f"(SPEC/06 section 2)")  # fmt: skip
    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for agent in agent_dirs(root):
        if agent.name in EXEMPT:
            continue
        errors += check_agent(agent, f"{agent.relative_to(root).as_posix()}/")
    return errors
