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


# --- S2: a red-team plant goes silent with its control in the tree -------

M02_ENVELOPE = ROOT / "evals" / "history" / "8033c2a7a0588e557df577464c190e64a435e88a.json"


def recorded() -> dict:
    """Row 2's envelope, GREEN, as CI wrote it. Every seed that needs an envelope starts here, in memory."""
    return json.loads(M02_ENVELOPE.read_text(encoding="utf-8"))


def judged(envelope: dict, plant_ids) -> tuple[str, list[str]]:
    """`gate.judge` as `gate.rule` calls it, with the plant ids passed in."""
    from src.verdict import gate, replay_history

    history = replay_history.load(gate.HISTORY, exclude_commit=envelope["commit"])
    kinds = {g: r["kind"] for g, r in envelope["goldens"].items()}
    cap, _ = gate.cap_at(envelope["commit"])
    return gate.judge(envelope, kinds, history, list(plant_ids), cap, gate.required_checks(envelope["commit"]))


def commit_in(tree: Path, message: str) -> str:
    """Commit everything in a throwaway worktree, detached, and return the sha."""
    subprocess.run(["git", "add", "-A"], cwd=tree, check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.name=seed", "-c", "user.email=seed@invalid", "commit", "-q", "--no-verify",
                    "-m", message], cwd=tree, check=True, capture_output=True)  # fmt: skip
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=tree, check=True, capture_output=True,
                          text=True).stdout.strip()  # fmt: skip


@pytest.mark.xfail(strict=True, reason="S2: CONTROLS is empty until M03 PR 2 (SPEC/03 §6)")
def test_s2_a_silent_red_team_plant_is_red(seeded):
    """g-016's attack got through. With the red-team control in the tree, g-016 is a plant, and a
    plant that does not fire is a silent plant: RED, for that reason."""
    from src.verdict import plants

    envelope = recorded()
    envelope["goldens"]["g-016"] = json.loads((FIXTURES / "s2-g-016-result.json").read_text(encoding="utf-8"))
    envelope["never_passed"] = sorted(envelope["never_passed"] + ["g-016"])
    kinds = {g: r["kind"] for g, r in envelope["goldens"].items()}

    tree = seeded()
    control = tree / "agents" / "refagent" / "rules" / "redteam.yaml"
    control.parent.mkdir(parents=True)
    control.write_text("# S2: the red-team control is in the tree (SPEC/03 §2)\n", encoding="utf-8")
    at = commit_in(tree, "S2: the red-team control")  # the control is in the tree and at this commit

    plant_ids = plants.plant_ids(kinds, tree)  # PR 2 passes `at`: the plant rule reads the control at a commit (S6)
    assert "g-016" in plant_ids, f"the plant rule gives {plant_ids} with {control.relative_to(tree)} at {at[:7]}"
    verdict, reasons = judged(envelope, plant_ids)
    assert verdict == "RED" and any(reason.startswith("silent plant") for reason in reasons), reasons


# --- S3: a golden that overlaps the corpus --------------------------------


@pytest.mark.xfail(strict=True, reason="S3: validate has no golden/corpus overlap check until M03 PR 2 (SPEC/03 §6)")
def test_s3_a_golden_that_overlaps_the_corpus_is_refused(seeded):
    """The holdback schedule holds g-010's whole question with its answer: 38 words, over the
    12-word bound (SPEC/03 §2). Today's golden, citation and ruling checks pass on it."""
    from src.validate import checks

    tree = seeded("s3-overlap.patch")
    assert checks.check_goldens(tree) == [] and checks.check_golden_citations(tree) == []
    assert checks.check_rulings(tree) == [], "the seed's ruling is well formed; only the overlap can refuse it"

    from src.validate import overlap

    errors = overlap.check(tree)
    assert any("g-010" in e and "data/corpus/holdback-schedule.md" in e for e in errors), errors
