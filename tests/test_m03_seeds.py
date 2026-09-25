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


# --- S4: an envelope with no corpus fingerprint ----------------------------


@pytest.mark.xfail(strict=True, reason="S4: the gate does not read the corpus fingerprint until M03 PR 2 (SPEC/03 §6)")
def test_s4_no_fingerprint_where_a_corpus_is_admitted_is_red(seeded):
    """Nothing new is planted: row 2's envelope says `corpus_fingerprint: null`, like every
    envelope in history. Beside a tree that admits a corpus, the gate's own reading is not null,
    and an envelope that disagrees with it is RED for that reason (SPEC/03 §2, ruling on F3)."""
    import hashlib

    import yaml

    from src.verdict import gate, replay_history

    envelope = recorded()
    assert envelope["corpus_fingerprint"] is None, "the false state is already in evals/history/"

    tree = seeded("s3-overlap.patch")  # S3's document is the corpus; admitted.yaml admits it here only
    doc = tree / "data" / "corpus" / "holdback-schedule.md"
    (tree / "data" / "corpus" / "admitted.yaml").write_text(yaml.safe_dump([{
        "key": "holdback-schedule.md",
        "sha256": hashlib.sha256(doc.read_bytes()).hexdigest(),
        "ruling": "milestones/M03/rulings/seed-s3-data-owner.md",
    }]), encoding="utf-8")  # fmt: skip

    reading = gate.corpus_fingerprint(tree)  # the gate's own reading; `rule` takes it at the envelope's commit
    assert reading is not None
    history = replay_history.load(gate.HISTORY, exclude_commit=envelope["commit"])
    kinds = {g: r["kind"] for g, r in envelope["goldens"].items()}
    cap, _ = gate.cap_at(envelope["commit"])
    verdict, reasons = gate.judge(envelope, kinds, history, [], cap, gate.required_checks(envelope["commit"]),
                                  corpus=reading)  # fmt: skip
    assert verdict == "RED" and any("corpus_fingerprint" in reason for reason in reasons), reasons


# --- S5: the unsigned amendment dropped into the corpus bucket ------------

RUNS = ROOT / "milestones" / "M03" / "runs"


@pytest.mark.xfail(strict=True, reason="S5: the ingest pipeline and the attempt are M03 PR 2's (SPEC/03 §5.1)")
def test_s5_the_unsigned_amendment_stays_in_quarantine():
    """An attempt against AWS, recorded by the human and looked up by CI (`scripts/observe_ingest.py`).
    This test reads what the human typed; it is the weaker witness, and checks.F3_5 passes only if
    the lookup agrees. The expected refusal is no admission (SPEC/03 §2)."""
    import hashlib

    import yaml

    run = yaml.safe_load((RUNS / "f3_5_amendment.yaml").read_text(encoding="utf-8"))
    observed = run["observed"]
    assert observed is not None, "the attempt has not been made"
    document = (ROOT / run["document"]).read_bytes()
    assert observed["sha256"] == hashlib.sha256(document).hexdigest(), "the object uploaded is the seed"
    assert observed["in_production"] is False and observed["named_in_admitted"] is False


# --- S6: a control added today makes old envelopes RED ---------------------


@pytest.mark.xfail(strict=True, reason="S6: the plant rule reads the working tree until M03 PR 2 (SPEC/03 §6)")
def test_s6_a_control_added_later_does_not_re_rule_an_old_envelope(seeded, monkeypatch):
    """Row 2's envelope was written before any guardrail. Put a guardrail control in a worktree
    of HEAD and name it in CONTROLS, as PR 2 will: g-013 to g-015, which have never passed,
    must not become plants of that envelope. Today they do, and the gate says "silent plant"."""
    import shutil

    from src.verdict import gate, plants

    tree = seeded()
    control = tree / "agents" / "refagent" / "rules" / "guardrail.yaml"
    control.parent.mkdir(parents=True)
    shutil.copyfile(FIXTURES / "s6-guardrail.yaml", control)
    monkeypatch.setattr(plants, "CONTROLS", {"guardrail": "agents/refagent/rules/guardrail.yaml"})
    monkeypatch.setattr(gate, "ROOT", tree)  # rule() reads the tree here: the goldens at the commit, and the plant rule
    monkeypatch.setattr(gate, "GOLDENS", tree / "evals" / "goldens" / "v1")

    verdict, reasons = gate.rule(M02_ENVELOPE)
    assert not any(reason.startswith("silent plant") for reason in reasons), reasons
    assert verdict == "GREEN", reasons
