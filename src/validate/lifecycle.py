"""A pin within 30 days of its end of life, or past it, fails (M04 PR 2; SPEC/04 §5, seed S5).

`deprecated_after` is the manifest's date for the pinned model's end of
life (SPEC/00 §6; the Threshold Owner's by ADR-0010). At M04 it is set by
hand from Bedrock's `modelLifecycle.endOfLifeTime`, which Bedrock publishes
only once a model is `LEGACY`; setting it from Bedrock by code is
`model-watch`'s, cut to M07 (SPEC/04 §9, cut g). So this reads the date the
manifest carries and nothing in AWS. Null passes: it records "no date
announced", not a gap (SPEC/04 §2).

The window is counted from the day `validate` runs, so a pin that passes
today fails on the thirtieth day before its date without any change to the
tree. That is the point: a run that goes red on its own is the warning.
What it does not do: notice a date Bedrock has announced and the manifest
has not (M07), or read `pinned_roles`, which no run calls.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml

from src import manifest as manifest_module

WINDOW_DAYS = 30


def _as_date(value: object) -> datetime.date | None:
    """A YAML date, quoted or not; None for anything that is not one (the manifest schema refuses those)."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check(root: Path, today: datetime.date | None = None) -> list[str]:
    today = today or datetime.date.today()
    errors = []
    for path in manifest_module.paths(root):
        rel = path.relative_to(root).as_posix()
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("deprecated_after") is None:
            continue
        raw = manifest["deprecated_after"]
        after = _as_date(raw)
        if after is None:
            errors.append(f"{rel}: deprecated_after {raw!r} is not a date")
            continue
        model = (manifest.get("model") or {}).get("id")
        days = (after - today).days
        if days < 0:
            errors.append(f"{rel}: deprecated_after {after.isoformat()} is past ({-days} days ago, read {today.isoformat()}): "
                          f"the pinned model {model} is at or beyond its end of life")  # fmt: skip
        elif days <= WINDOW_DAYS:
            errors.append(f"{rel}: deprecated_after {after.isoformat()} is {days} days away (read {today.isoformat()}), "
                          f"within {WINDOW_DAYS}: swap the pinned model {model} before its end of life")  # fmt: skip
    return errors
