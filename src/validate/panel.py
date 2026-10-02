"""`validate`: Grafana panel 1 reads the registry and nothing else (SPEC/06 §6, finding 11, S4's query reader).

F6.4 fires when panel 1 shows an agent the registry does not. One way is a
second source in the panel's own query, which the seed S4 plants: a static
list beside the registry. This reads `infra/grafana/panel1.json` (Security)
and refuses, with that path:

- no panel with id 1, or one with no target;
- a target whose data source is not the registry's (uid `registry`);
- a target whose SQL reads any table but `agentkeel-registry` (every `FROM`
  and `JOIN`), or that carries no SQL at all.

The other half of F6.4, panel 1's rows against a registry scan, is
`build.panel_not_in_registry` (BLOCK 3): this reads the query, not the rows.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PANEL = "infra/grafana/panel1.json"
DATASOURCE_UID = "registry"
TABLE = "agentkeel-registry"
# FROM or JOIN, then a dotted name whose parts may be quoted: "a"."b"."c", a.b, `c`.
SOURCE = re.compile(r"\b(?:from|join)\s+((?:[\"`]?[\w-]+[\"`]?\s*\.\s*)*[\"`]?[\w-]+[\"`]?)", re.IGNORECASE)


# A second source that names no table after FROM or JOIN (cold review F4 on M06 PR 2): a UNION, a VALUES
# list, a subquery, or a comma join. Refused outright; panel 1 is one SELECT from one table.
SECOND_SOURCE = re.compile(r"\bunion\b|\bvalues\b|\(\s*select\b|\bfrom\s+[^,;]+?,", re.IGNORECASE)


def tables(sql: str) -> list[str]:
    """The last part of every name after FROM or JOIN, unquoted and lower case."""
    return [re.split(r"\s*\.\s*", m.group(1))[-1].strip("\"`").lower() for m in SOURCE.finditer(sql)]


# --- panel 2 (M07 PR 2; SPEC/07 section 2 "Panel 2", section 6; seed S4's query reader) ----------------
#
# F7.4 fires when panel 2 shows GREEN where the envelope says RED. One way is a query that computes its
# verdict column, which seed S4 plants: the constant 'GREEN'. Panel 2 is one row per envelope with the
# verdict as stored, so its query is one SELECT of bare columns from the envelopes' table and nothing
# else. The other half of F7.4, panel 2's rows against the envelopes, is `build.panel_verdict_mismatch`.

PANEL_2 = "infra/grafana/panel2.json"
TABLE_2 = "agentkeel-envelopes"  # one row per envelope on main: commit, verdict, mode, as stored
COLUMNS_2 = ("commit", "verdict", "mode")
SELECT_LIST = re.compile(r"^\s*select\s+(.*?)\s+from\s", re.IGNORECASE | re.DOTALL)
BARE = re.compile(r'^["`]?([A-Za-z_][A-Za-z0-9_]*)["`]?$')
VERDICT_LITERAL = re.compile(r"'\s*(GREEN|RED|UNMEASURED|REJECTED)\s*'", re.IGNORECASE)


def panel_2_sql_errors(sql: str, ref: str) -> list[str]:
    """Why a panel 2 query is refused; [] if nothing. Every reason is given, not the first."""
    where = f"{PANEL_2}: panel 2 target {ref}"
    errors = []
    if SECOND_SOURCE.search(sql):
        errors.append(f"{where} reads a second source (a UNION, VALUES, subquery or comma join), not {TABLE_2!r} alone")
    named = tables(sql)
    if not named:
        errors.append(f"{where} names no table, so what it reads is unread")
    errors += [f"{where} reads {table!r}, not {TABLE_2!r}" for table in named if table != TABLE_2]
    listed = SELECT_LIST.match(sql)
    items = [item.strip() for item in listed[1].split(",")] if listed else []
    if not items:
        errors.append(f"{where} is not one SELECT of columns from a table")
    columns = []
    for item in items:
        bare = BARE.match(item)
        if bare is None:
            what = "computes its verdict column" if re.search(r"\bverdict\b", item, re.IGNORECASE) else "computes a column"
            errors.append(f"{where} {what} ({item}); panel 2 selects each column as stored")
        else:
            columns.append(bare[1].lower())
    errors += [f"{where} selects {column!r}, which is not one of {', '.join(COLUMNS_2)}" for column in columns
               if column not in COLUMNS_2]  # fmt: skip
    errors += [f"{where} does not select {column!r} as stored" for column in ("commit", "verdict") if column not in columns
               and not any(re.search(rf"\b{column}\b", item, re.IGNORECASE) for item in items)]  # fmt: skip
    # The verdict is named once, as a selected column: a filter or a CASE over it would choose what is shown.
    if len(re.findall(r"\bverdict\b", sql, re.IGNORECASE)) > 1:
        errors.append(f"{where} names verdict outside its select list: a filter or an expression over the verdict")
    if VERDICT_LITERAL.search(sql):
        errors.append(f"{where} carries a verdict as a constant: the verdict shown would not be the envelope's")
    return errors


def check_panel_2(root: Path) -> list[str]:
    path = root / PANEL_2
    if not path.is_file():
        return [f"{PANEL_2}: missing; panel 2 has no query to read (SPEC/07 section 6)"]
    try:
        dashboard: Any = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{PANEL_2}: not JSON ({exc})"]
    panels = dashboard.get("panels") if isinstance(dashboard, dict) else None
    panel = next((p for p in panels or [] if isinstance(p, dict) and p.get("id") == 2), None)
    if panel is None:
        return [f"{PANEL_2}: no panel with id 2"]
    targets = panel.get("targets") or []
    if not targets:
        return [f"{PANEL_2}: panel 2 has no target"]
    errors: list[str] = []
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("datasource") or {}, dict):
            errors.append(f"{PANEL_2}: panel 2 has a target that is not a mapping with a datasource mapping")
            continue
        ref = target.get("refId", "?")
        source = target.get("datasource") or {}
        if source.get("uid") != DATASOURCE_UID:
            errors.append(f"{PANEL_2}: panel 2 target {ref} reads data source {source.get('uid')!r} "
                          f"({source.get('type')}), not the workspace's {DATASOURCE_UID!r}")  # fmt: skip
        errors += panel_2_sql_errors(str(target.get("rawSQL") or target.get("query") or ""), str(ref))
    return errors


def check(root: Path) -> list[str]:
    path = root / PANEL
    if not path.is_file():
        return [f"{PANEL}: missing; panel 1 has no query to read (SPEC/06 section 6)"]
    try:
        dashboard: Any = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{PANEL}: not JSON ({exc})"]
    panels = dashboard.get("panels") if isinstance(dashboard, dict) else None
    panel = next((p for p in panels or [] if isinstance(p, dict) and p.get("id") == 1), None)
    if panel is None:
        return [f"{PANEL}: no panel with id 1"]
    targets = panel.get("targets") or []
    if not targets:
        return [f"{PANEL}: panel 1 has no target"]
    errors: list[str] = []
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("datasource") or {}, dict):
            errors.append(f"{PANEL}: panel 1 has a target that is not a mapping with a datasource mapping")
            continue
        ref = target.get("refId", "?")
        source = target.get("datasource") or {}
        if source.get("uid") != DATASOURCE_UID:
            errors.append(f"{PANEL}: panel 1 target {ref} reads data source {source.get('uid')!r} "
                          f"({source.get('type')}), not the registry's {DATASOURCE_UID!r}")  # fmt: skip
            continue
        sql = str(target.get("rawSQL") or target.get("query") or "")
        if SECOND_SOURCE.search(sql):
            errors.append(f"{PANEL}: panel 1 target {ref} reads a second source (a UNION, VALUES, subquery or "
                          f"comma join), not {TABLE!r} alone")  # fmt: skip
            continue
        named = tables(sql)
        if not named:
            errors.append(f"{PANEL}: panel 1 target {ref} names no table, so what it reads is unread")
        for table in named:
            if table != TABLE:
                errors.append(f"{PANEL}: panel 1 target {ref} reads {table!r}, not {TABLE!r}")
    return errors
