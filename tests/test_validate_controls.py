"""validate: the plant controls name live goldens of their own kind (M03 PR 2; rule-owner on 06ed59b)."""

from __future__ import annotations

import shutil

import pytest

from src.validate import controls
from src.verdict import ROOT, plants


def test_the_controls_in_the_tree_pass():
    assert controls.check(ROOT) == []


@pytest.fixture
def tree(tmp_path):
    """The goldens and the two rule files, copied, so a test can break one."""
    shutil.copytree(ROOT / "evals" / "goldens", tmp_path / "evals" / "goldens")
    shutil.copytree(ROOT / "agents" / "refagent" / "rules", tmp_path / "agents" / "refagent" / "rules")
    return tmp_path


def rewrite(tree, name: str, old: str, new: str) -> None:
    path = tree / "agents" / "refagent" / "rules" / name
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


@pytest.mark.parametrize(("name", "old", "new", "said"), [
    ("redteam.yaml", "plants: [g-016,", "plants: [g-099, g-016,", "not a live golden"),
    ("redteam.yaml", "plants: [g-016,", "plants: [g-001, g-016,", "a ordinary golden"),
    ("guardrail.yaml", "plants: [g-013, g-015]", "plants: [g-013, g-015, g-016]", "a redteam golden"),
    ("redteam.yaml", "plants: [g-016,", "plants: [g-016, g-016,", "an id twice"),
    ("redteam.yaml", "  g-020: user-supplied-contract-terms", "", "they must be one set"),
    ("guardrail.yaml", "plants: [g-013, g-015]", "", "under `plants`"),
])  # fmt: skip
def test_a_control_that_would_drop_a_plant_without_a_word_is_refused(tree, name, old, new, said):
    """plants.py drops an id that is no live golden of the control's kind; validate says so instead."""
    rewrite(tree, name, old, new)
    assert any(said in error for error in controls.check(tree)), controls.check(tree)


def test_a_control_named_in_controls_must_be_in_the_tree(tree):
    (tree / plants.CONTROLS["redteam"]).unlink()
    assert any("not in the tree" in error for error in controls.check(tree))
