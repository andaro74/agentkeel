"""The rights table's digest, the same from the file and from the DynamoDB copy (M03 PR 2, seed S1).

`data/rights_table.json` is the truth (SPEC/00 §9); refagent's runtime
answers from the DynamoDB copy `scripts/load_rights_table.py` makes. A run
is in the runtime only when that copy is this tree's file
(`scripts/runtime_for_tree.py`), and the only thing both sides can compare
is a digest. So the digest is of the rows as the table holds them: each
value as `load_rights_table.attribute` writes it (a bool, None, or its
string), rows ordered by `table_row`. A row read back from DynamoDB
digests the same as the row in the file it was written from.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.verdict import canonical_sha256

KEY = "table_row"


def as_stored(value: Any) -> Any:
    """What DynamoDB holds for a file value: None, a bool, or its string (load_rights_table.attribute)."""
    return value if value is None or isinstance(value, bool) else str(value)


def from_item(item: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """One DynamoDB item, back to a row of stored values. Only the three types the loader writes."""
    row = {}
    for name, value in item.items():
        (kind, raw), = value.items()
        if kind not in ("S", "BOOL", "NULL"):
            raise ValueError(f"{name}: {kind} is not a type load_rights_table writes")
        row[name] = None if kind == "NULL" else raw
    return row


def digest(rows: list[dict[str, Any]]) -> str:
    """sha256 of the rows as stored, ordered by table_row. The marker's value."""
    stored = [{k: as_stored(v) for k, v in row.items()} for row in rows]
    return canonical_sha256(sorted(stored, key=lambda row: row[KEY]))


def file_digest(root: Path) -> str:
    """The digest of `data/rights_table.json` in the tree at `root`."""
    return digest(json.loads((root / "data" / "rights_table.json").read_text(encoding="utf-8")))
