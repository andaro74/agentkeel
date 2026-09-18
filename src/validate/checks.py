"""The M00 PR 1 checks (SPEC/00 §5 `validate`, ADR-0001 amendment 1 item 22).

Golden front matter, ruling front matter, and that every ordinary and trap
golden cites a rights-table row and a clause that exist. Each check returns
a list of error strings; empty means it passed.
"""

from __future__ import annotations

import glob
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

GOLDEN_FIELDS = {"id", "kind", "question", "expected", "seat", "added", "retired"}
GOLDEN_ID = re.compile(r"^g-\d{3}$")
KINDS = {"ordinary", "trap", "guardrail", "redteam"}
CITING_KINDS = {"ordinary", "trap"}
CITING_EXPECTED = {"table_row", "clause_id", "answer_fields"}
BLOCK_EXPECTED = {"guardrail": {"BLOCKED", "MASKED"}, "redteam": {"BLOCKED"}}
RULING_FIELDS = {"ruling", "seat", "authorises", "evidence", "pr"}


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_goldens(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Goldens by file name, plus errors for files that are not a YAML mapping."""
    goldens: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted((root / "evals" / "goldens").glob("v*/*")):
        rel = path.relative_to(root).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: not YAML: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{rel}: not a mapping")
            continue
        goldens[rel] = doc
    return goldens, errors


def check_goldens(root: Path) -> list[str]:
    goldens, errors = load_goldens(root)
    if not goldens and not errors:
        return ["evals/goldens/: no goldens found"]
    seen: dict[str, str] = {}
    for rel, g in goldens.items():
        stem = Path(rel).stem
        if Path(rel).suffix != ".yaml" or not GOLDEN_ID.match(stem):
            errors.append(f"{rel}: file name is not g-NNN.yaml")
        if set(g) != GOLDEN_FIELDS:
            missing, extra = (
                sorted(GOLDEN_FIELDS - set(g)),
                sorted(set(g) - GOLDEN_FIELDS),
            )
            errors.append(
                f"{rel}: fields differ from SPEC/00 section 6 (missing {missing}, extra {extra})"
            )
            continue
        if g["id"] != stem:
            errors.append(f"{rel}: id {g['id']!r} does not equal the file name")
        if g["id"] in seen:
            errors.append(f"{rel}: id {g['id']!r} already used by {seen[g['id']]}")
        seen[g["id"]] = rel
        if g["kind"] not in KINDS:
            errors.append(f"{rel}: kind {g['kind']!r} not in {sorted(KINDS)}")
            continue
        expected = g["expected"]
        if g["kind"] in CITING_KINDS:
            if not isinstance(expected, dict) or set(expected) != CITING_EXPECTED:
                errors.append(
                    f"{rel}: expected must have exactly {sorted(CITING_EXPECTED)}"
                )
            elif (
                not isinstance(expected["answer_fields"], dict)
                or not expected["answer_fields"]
            ):
                errors.append(
                    f"{rel}: expected.answer_fields must be a non-empty mapping"
                )
        elif expected not in BLOCK_EXPECTED[g["kind"]]:
            errors.append(
                f"{rel}: expected must be one of {sorted(BLOCK_EXPECTED[g['kind']])}"
            )
        for field in ("question", "seat"):
            if not isinstance(g[field], str) or not g[field].strip():
                errors.append(f"{rel}: {field} must be a non-empty string")
        if not _is_iso_date(g["added"]):
            errors.append(f"{rel}: added must be a quoted ISO date")
        if g["retired"] is not None and not _is_iso_date(g["retired"]):
            errors.append(f"{rel}: retired must be null or a quoted ISO date")
    return errors


def check_golden_citations(root: Path) -> list[str]:
    rows = {
        r["table_row"]
        for r in json.loads(
            (root / "data" / "rights_table.json").read_text(encoding="utf-8")
        )
    }
    clauses = set(
        json.loads((root / "data" / "clause_index.json").read_text(encoding="utf-8"))
    )
    goldens, _ = load_goldens(root)
    errors = []
    for rel, g in goldens.items():
        expected = g.get("expected")
        if g.get("kind") not in CITING_KINDS or not isinstance(expected, dict):
            continue
        if expected.get("table_row") not in rows:
            errors.append(
                f"{rel}: table_row {expected.get('table_row')!r} is not in data/rights_table.json"
            )
        if expected.get("clause_id") not in clauses:
            errors.append(
                f"{rel}: clause_id {expected.get('clause_id')!r} is not in data/clause_index.json"
            )
    return errors


def front_matter(text: str) -> dict[str, Any] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    doc = yaml.safe_load("\n".join(lines[1:end]))
    return doc if isinstance(doc, dict) else None


def check_rulings(root: Path) -> list[str]:
    paths = sorted((root / "milestones").glob("*/rulings/*.md"))
    if not paths:
        return ["milestones/*/rulings/: no ruling files found"]
    errors = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        fm = front_matter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rel}: no front matter")
            continue
        missing = sorted(f for f in RULING_FIELDS if fm.get(f) in (None, "", []))
        if missing:
            errors.append(f"{rel}: front matter missing or empty: {missing}")
        for field in ("authorises", "evidence"):
            if fm.get(field) and not isinstance(fm[field], list):
                errors.append(f"{rel}: {field} must be a list")
        if isinstance(fm.get("authorises"), list):
            for pattern in fm["authorises"]:
                if not glob.glob(str(pattern), root_dir=root, recursive=True):
                    errors.append(
                        f"{rel}: authorises path {pattern!r} matches nothing in the tree"
                    )
    return errors


CHECKS = {
    "golden front matter": check_goldens,
    "golden citations exist in data/": check_golden_citations,
    "ruling front matter": check_rulings,
}
