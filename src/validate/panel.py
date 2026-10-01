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
