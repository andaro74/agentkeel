"""verdict.template: build's readings of claim 6's live observations (SPEC/06 §4; P5).

`scripts/observe_template.py` writes raw lists only (BLOCK 3). Everything
that compares one record with another is here, and only `build` calls it.
The gate rules nothing on `template`; row 6's Measured cell reads it.
"""

from __future__ import annotations

from typing import Any


class Unreadable(Exception):
    """An observation that is not in the observer's shape: build refuses it."""


def panel_names(frame: dict[str, Any]) -> list[str]:
    """The `name` column of panel 1's rows, as Grafana's `/api/ds/query` returns them (every frame of A)."""
    try:
        frames = frame["results"]["A"]["frames"]
    except (KeyError, TypeError) as exc:
        raise Unreadable(f"panel 1's frame has no results.A.frames ({exc!r})") from exc
    names: list[str] = []
    for one in frames:
        fields = [f.get("name") for f in (one.get("schema") or {}).get("fields") or []]
        if "name" not in fields:
            raise Unreadable(f"a panel 1 frame has no `name` field (fields {fields})")
        names += [str(v) for v in (one.get("data") or {}).get("values", [])[fields.index("name")]]
    return names


def registry_names(registry: dict[str, Any]) -> list[str]:
    """The `name` of every item in a DynamoDB scan of the registry, as the API returns it."""
    items = registry.get("Items") if isinstance(registry, dict) else None
    if not isinstance(items, list):
        raise Unreadable("the registry scan has no Items list")
    try:
        return [item["name"]["S"] for item in items]
    except (KeyError, TypeError) as exc:
        raise Unreadable(f"a registry item has no name ({exc!r})") from exc


def panel_not_in_registry(frame: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    """F6.4: the agents panel 1 shows that the registry does not hold, by name, sorted (BLOCK 3)."""
    held = set(registry_names(registry))
    return sorted({name for name in panel_names(frame) if name not in held})
