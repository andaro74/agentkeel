"""M02's seeded cases S1-S5 (SPEC/02 §5), committed before the code that reads them.

Each seed is a diff to a seat-owned path with too few rulings, or a bypass
attempt, under tests/fixtures/m02/. Each test applies its seed to a copy
of the tree at HEAD and asks the reader to refuse it, naming the seed's
path and the planted reason. Until the reader is in the tree the test
fails, and it is marked `xfail(strict=True)`: an expected failure now, and
a failure the first time it passes, so the marker has to come off in the
commit that lands the reader. A seed cannot start passing without
somebody saying so.

The readers, none of which exist at M02 PR 1: `src/gates/two_key.py` (S1),
`src/gates/ruling_cited.py` (S2, S3, S5), `validate`'s edge and golden-id
checks (S3, S5), and for S4 the human's attempts against the `main`
ruleset, recorded in milestones/M02/runs/f2_1_bypass.yaml and looked up by
`scripts/observe_pr.py` at PR 3. The API names below are what PR 2 must
provide; if they land under other names, PR 2 changes the call and never
what the seed adds or removes.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

from src.verdict import ROOT

FIXTURES = Path(__file__).parent / "fixtures" / "m02"
RUNS = ROOT / "milestones" / "M02" / "runs"


@pytest.fixture
def seeded(request):
    """A detached worktree of HEAD with one seed's patch applied. Removed after the test."""
    trees: list[Path] = []

    def apply(patch: str) -> Path:
        tree = Path(tempfile.mkdtemp()) / "tree"
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), "HEAD"],
                       cwd=ROOT, check=True, capture_output=True)  # fmt: skip
        subprocess.run(["git", "apply", str(FIXTURES / patch)], cwd=tree, check=True, capture_output=True)
        trees.append(tree)
        return tree

    yield apply
    for tree in trees:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False,
                       capture_output=True)  # fmt: skip


# --- S1: a relaxation with one key, and with two files from one seat -----


@pytest.mark.xfail(strict=True, reason="src/gates/two_key.py lands at M02 PR 2")
def test_s1_one_key_on_a_relaxation_is_refused(seeded):
    """ruling-cited is satisfied by the Threshold Owner's file; only two-key can refuse this."""
    from src.gates import ruling_cited, two_key

    tree = seeded("s1-one-key.patch")
    assert ruling_cited.refusal(tree, base=ROOT, pr=0) is None, "the one key covers the path; that gate must pass"
    refusal = two_key.refusal(tree, base=ROOT, pr=0)
    assert refusal is not None and "thresholds.yaml" in refusal and "cost_cap.tokens_per_run" in refusal
    assert "1 seat" in refusal or "one seat" in refusal


@pytest.mark.xfail(strict=True, reason="src/gates/two_key.py lands at M02 PR 2")
def test_s1_two_files_from_one_seat_are_one_key(seeded):
    """Two ruling files, both Threshold Owner: the gate counts seats, not files."""
    from src.gates import two_key

    tree = seeded("s1-two-files-one-seat.patch")
    refusal = two_key.refusal(tree, base=ROOT, pr=0)
    assert refusal is not None and "thresholds.yaml" in refusal
    assert "Threshold Owner" in refusal and ("same seat" in refusal or "distinct" in refusal)


# --- S2: a golden edited so the trap rewards what it was written to catch --


@pytest.mark.xfail(strict=True, reason="src/gates/ruling_cited.py and two_key.py land at M02 PR 2")
def test_s2_a_golden_edited_to_green_a_build_is_refused(seeded):
    """No ruling at all, so ruling-cited refuses it; and `expected` moved on an id with a pass in
    history, so two-key refuses it too. Both must name the golden."""
    from src.gates import ruling_cited, two_key

    tree = seeded("s2-golden-greened.patch")
    cited = ruling_cited.refusal(tree, base=ROOT, pr=0)
    assert cited is not None and "evals/goldens/v1/g-010.yaml" in cited and "Data Owner" in cited
    keys = two_key.refusal(tree, base=ROOT, pr=0)
    assert keys is not None and "g-010" in keys and "expected" in keys


# --- S3: an edge declared on one side only ------------------------------


@pytest.mark.xfail(strict=True, reason="validate's edge check lands at M02 PR 2")
def test_s3_a_one_sided_edge_is_refused(seeded):
    """refagent says it may call ratings-helper@v1; no manifest says ratings-helper may be called."""
    from src.validate import checks

    tree = seeded("s3-one-sided-edge.patch")
    errors = checks.check_edges(tree)
    assert any("ratings-helper@v1" in e and "may_be_called_by" in e for e in errors), errors


# --- S4: the owner tries to bypass a red check ----------------------------


@pytest.mark.xfail(strict=True, reason="the attempts are made by the human after M02 PR 2 merges")
def test_s4_the_owner_was_refused():
    """Two attempts against GitHub, recorded by the human and looked up by CI at PR 3.
    Door 3 is two gates: the ruleset refuses the merge, and validate refuses the ruleset
    that would have allowed it."""
    run = yaml.safe_load((RUNS / "f2_1_bypass.yaml").read_text(encoding="utf-8"))
    observed = run["observed"]
    assert observed is not None, "the attempts have not been made"
    assert len(observed) == len(run["attempts"]), "every attempt is made, not some"
    merge, ruleset = observed
    assert merge["result"] == "refused" and merge["message_must_contain"] in merge["message"]
    assert ruleset["validate_result"] == "RED" and ruleset["bypass_actors_after"] == []
    export = json.loads((ROOT / "infra" / "ruleset" / "main.json").read_text(encoding="utf-8"))
    assert export["bypass_actors"] == [], "the export on main must say nobody bypasses"
