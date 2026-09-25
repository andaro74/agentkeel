"""M03's seeded cases S1-S6 (SPEC/03 §5), committed before the code that reads them.

Each test asks the reader to refuse its seed, and asserts the planted
reason, not only the verdict. Until the reader is in the tree the test
fails, and it is marked `xfail(strict=True)`: an expected failure now, and
a failure the first time it passes, so the marker has to come off in the
commit that lands the reader.

The readers, none of which exist at M03 PR 1 (SPEC/03 §6): the runtime
match covering the rights table (S1); `plants.CONTROLS` (S2); `validate`'s
golden/corpus overlap (S3); the gate's own reading of the corpus
fingerprint (S4); the ingest pipeline and `scripts/observe_ingest.py`
(S5); the plant rule reading each control at the envelope's commit (S6).
The API names below are what PR 2 must provide; if they land under other
names, PR 2 changes the call and never what the seed adds.

The two guards at the end carry no marker. What they hold is already
true (SPEC/03 §5.2); a commit that turns one red has broken a part of
claim 3 that was whole.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from src.verdict import ROOT

FIXTURES = Path(__file__).parent / "fixtures" / "m03"


@pytest.fixture
def seeded():
    """A detached worktree of HEAD with one seed's patch applied. Removed after the test."""
    trees: list[Path] = []

    def apply(patch: str | None = None) -> Path:
        tree = Path(tempfile.mkdtemp()) / "tree"
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), "HEAD"],
                       cwd=ROOT, check=True, capture_output=True)  # fmt: skip
        trees.append(tree)  # before apply, so a patch that no longer applies is still cleaned up
        if patch is not None:
            subprocess.run(["git", "apply", str(FIXTURES / patch)], cwd=tree, check=True, capture_output=True)
        return tree

    yield apply
    for tree in trees:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False,
                       capture_output=True)  # fmt: skip


# --- S1: a regression through the rights table ---------------------------


@pytest.mark.xfail(strict=True, reason="S1: the runtime match reads the bundle alone until M03 PR 2 (SPEC/03 §6)")
def test_s1_a_table_change_is_not_measured_against_mains_table(seeded):
    """`r-003` says exclusive; `g-011` expects non-exclusive. In `mode: runtime` the run answers
    from the table the last deploy loaded, so the tree's table must be part of what the runtime
    is matched on, or the run is not in the runtime."""
    from scripts import runtime_for_tree

    tree = seeded("s1-table-regresses.patch")
    rows = {row["table_row"]: row for row in json.loads((tree / "data" / "rights_table.json").read_text("utf-8"))}
    assert rows["r-003"]["exclusive"] is True, "the seed is what it says"

    here = runtime_for_tree.bundle_digest(ROOT / "agents" / "refagent")
    there = runtime_for_tree.bundle_digest(tree / "agents" / "refagent")
    assert there != here, "the runtime deployed from main would answer this tree, from main's table"
