"""`validate` reads `deprecated_after` (M04 PR 2; SPEC/04 §5, seed S5's reader): the window's edges."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from src.validate import lifecycle

from .conftest import ROOT

TODAY = datetime.date(2026, 9, 27)


def tree_with(tmp_path: Path, deprecated_after: str) -> Path:
    bundle = tmp_path / "agents" / "refagent"
    bundle.mkdir(parents=True)
    (bundle / "manifest.yaml").write_text(
        f"name: refagent\nmodel:\n  id: anthropic.claude-sonnet-4-20250514-v1:0\ndeprecated_after: {deprecated_after}\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.parametrize(("value", "fails"), [
    ("null", False),              # no date announced (SPEC/04 §2)
    ("2026-10-28", False),        # 31 days away
    ("2026-10-27", True),         # 30 days away: within the window
    ("'2026-10-14'", True),       # S5's date, quoted as in its patch
    ("2026-09-27", True),         # today
    ("2026-09-26", True),         # past
    ("'next spring'", True),      # not a date: the schema refuses it too
])  # fmt: skip
def test_the_window(tmp_path, value, fails):
    errors = lifecycle.check(tree_with(tmp_path, value), today=TODAY)
    assert bool(errors) is fails, errors
    assert all("deprecated_after" in e for e in errors)


def test_refagents_own_pin_passes_today():
    """refagent's is null, a reading of Bedrock on 2026-09-26 (no date announced), not a gap."""
    assert lifecycle.check(ROOT) == []
