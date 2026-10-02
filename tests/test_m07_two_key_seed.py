"""The seeded case for `two-key`'s reading of `deprecated_after` (ADR-0009 amendment 1, entry 6).

ADR-0009 amendment 1 (M04 PR 1) made a pin's `deprecated_after` moved later, set from a date to null, or
removed, with `model.id` unchanged, a relaxation, and said `src/gates/two_key.py` reads it from M04 PR 2.
Nothing did (threshold-owner F1 on M07 PR 2): `grep -rn deprecated src/gates` found nothing, and
SPEC/00 section 5, CLAUDE.md and `scripts/model_watch.py` each said two keys were needed. `validate` fails a
pin 30 days from its date, so a one-key commit that moved the date switched that check off.

Planted at M07 PR 3 in its own commit, before the reader: `tests/fixtures/m07/two-key-deprecated-after/
cases.json` names a dated base and each change to it. Each test puts refagent's manifest, as this tree
holds it, with that date, in a repository as the base ref, makes the one change with the Threshold
Owner's ruling alone, and asks `two-key` to refuse it. Until the reader is in the tree the gate passes
every case, and the marker says so; it comes off in the commit that lands the reader.

It is not one of row 7's seeds (S0 to S5, `plants.SEEDS_M07`): it reads no falsifier of claim 7. It is
the false state of a rule M04 wrote and M07's `model-watch` leans on.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.verdict import ROOT
from tests.test_gates import Repo, git, ruling

CASES = json.loads((Path(__file__).parent / "fixtures" / "m07" / "two-key-deprecated-after" / "cases.json").read_text(encoding="utf-8"))
MANIFEST = "agents/refagent/manifest.yaml"
LINE = "deprecated_after: null\n"


def manifest(value: object) -> str:
    """refagent's manifest as the tree holds it, with `deprecated_after` as the case gives it."""
    text = (ROOT / MANIFEST).read_text(encoding="utf-8").replace("\r\n", "\n")
    assert text.count(LINE) == 1, "refagent's manifest no longer says deprecated_after: null on one line"
    if value == "<the line deleted>":
        return text.replace(LINE, "")
    if isinstance(value, str) and value.startswith("<unquoted "):
        return text.replace(LINE, f"deprecated_after: {value[len('<unquoted '):-1]}\n")
    return text.replace(LINE, "deprecated_after: null\n" if value is None else f"deprecated_after: '{value}'\n")


@pytest.fixture
def dated(tmp_path: Path):
    """A repository whose base ref holds refagent's manifest with the fixture's date, and this tree's CODEOWNERS."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    repo = Repo(root)
    repo.write(".github/CODEOWNERS", (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8"))
    repo.write(MANIFEST, manifest(CASES["base"]))
    (root / "evals" / "history").mkdir(parents=True)
    (root / "evals" / "history" / ".keep").write_text("", encoding="utf-8")
    repo.commit_base()
    yield repo
    git(root, "worktree", "remove", "--force", str(repo.base))


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="planted at M07 PR 3: two-key does not read deprecated_after")
@pytest.mark.parametrize("case", sorted(CASES["relaxed_with_one_key"]))
def test_a_pins_date_relaxed_with_one_key_is_refused(dated, case):
    dated.write(MANIFEST, manifest(CASES["relaxed_with_one_key"][case]))
    dated.write("milestones/M07/rulings/a.md", ruling("Threshold Owner", [MANIFEST]))
    refused = dated.keys() or ""
    assert f"{MANIFEST}: deprecated_after" in refused and "one seat holds a key" in refused, f"{case}: two-key passed it"
    assert "ADR-0009 amendment 1, entry 6" in refused
    # The planted reason is the second key, not the change: with it the same diff passes.
    dated.write("milestones/M07/rulings/b.md", ruling("Product", ["milestones/**"], keys=[MANIFEST]))
    assert dated.keys() is None


@pytest.mark.parametrize("case", sorted(CASES["not_a_relaxation"]))
def test_a_date_moved_earlier_or_left_alone_needs_no_second_key(dated, case):
    """A guard, not a seed: it passes before the reader and must still pass after it."""
    dated.write(MANIFEST, manifest(CASES["not_a_relaxation"][case]))
    dated.write("milestones/M07/rulings/a.md", ruling("Threshold Owner", [MANIFEST]))
    assert dated.keys() is None


def test_a_swap_is_not_read_as_a_relaxed_date_and_null_to_a_date_is_not_one(dated):
    """Entry 6: "with `model.id` unchanged". A swap's date describes another model; the two are not compared.
    A guard, as above."""
    text = manifest(None)
    assert text.count("  id: anthropic.claude-sonnet-4-6\n") == 1
    dated.write(MANIFEST, text.replace("  id: anthropic.claude-sonnet-4-6\n", "  id: anthropic.claude-haiku-4-5-20251001-v1:0\n"))
    assert dated.keys() is None
    # Null on the base, a date on the tree: writing the date Bedrock gives is not a relaxation.
    dated.write(MANIFEST, manifest(None))
    dated.commit_as("t", "the base says null")
    git(dated.root, "worktree", "remove", "--force", str(dated.base))
    git(dated.root, "worktree", "add", "-q", "--detach", str(dated.base), "HEAD")
    dated.write(MANIFEST, manifest("2027-06-30"))
    assert dated.keys() is None
