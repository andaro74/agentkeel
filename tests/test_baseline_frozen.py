"""ADR-0002: `src/baseline/` is closed from tag `m00`.

Fails on any diff to `src/baseline/` or to the prompt hash. Four ways:

1. the file set and each file's content hash;
2. the model id, region and inference parameters the Threshold Owner
   confirmed before the tag;
3. ADR-0002's table against the same constants, so the ADR and this file
   cannot drift apart;
4. `git diff m00 HEAD -- src/baseline`, where tag `m00` is in the checkout.

1 to 3 run anywhere. 4 is the one that reads the tag; it skips, loudly,
where the tag was not fetched. `evals` checks out with `fetch-depth: 0`.

Hashes are of the file's text read as text, so a CRLF checkout hashes the
same as CI (the rule `canonical_sha256` follows for documents).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from src.baseline import agent
from src.verdict import ROOT

BASELINE = ROOT / "src" / "baseline"
ADR = ROOT / "docs" / "adr" / "ADR-0002-baseline-frozen.md"

# ADR-0002 §2. The prompt's hash is the `prompt_sha256` of every baseline card
# in evals/history/, including the card row 0 rests on.
FROZEN = {
    "__init__.py": "cbb26eec2d2181a42954125f22b4f7b5d0f9ba6ffc847ce2b34e3d974d0b9147",
    "agent.py": "70d9fc4561dfa423027cc51e241dcc8b8f977c98406bd7550874da943cb3dfd3",
    "prompt.txt": "2c3d9b754f8c285e95c3590cea61cafb1f59e5c5af64a1ea7b776c6c383684ab",
    "run.py": "625183fd3ca5f7b3014218d7b043e3a5268b3f8b3f3d56a74992f1a2db549e22",
}

# ADR-0002 §3. Threshold Owner, confirmed before tag m00.
FROZEN_MODEL_ID = "us.amazon.nova-micro-v1:0"
FROZEN_REGION = "us-west-2"
FROZEN_INFERENCE_CONFIG = {"temperature": 0, "maxTokens": 512}

ADR_ROW = re.compile(r"^\s*\| `src/baseline/([^`]+)` \| `([0-9a-f]{64})` \|$", re.MULTILINE)


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def test_the_folder_holds_the_frozen_files_and_nothing_else():
    present = {p.name for p in BASELINE.iterdir() if p.is_file()}
    assert present == set(FROZEN), "a file was added to or removed from the control"


@pytest.mark.parametrize("name", sorted(FROZEN))
def test_each_file_is_the_frozen_one(name):
    assert text_sha256(BASELINE / name) == FROZEN[name], (
        f"src/baseline/{name} differs from ADR-0002. The control is not edited; it is retired."
    )


def test_the_parameters_are_the_ones_confirmed_before_the_tag():
    assert agent.MODEL_ID == FROZEN_MODEL_ID
    assert agent.REGION == FROZEN_REGION
    assert agent.INFERENCE_CONFIG == FROZEN_INFERENCE_CONFIG


def test_the_prompt_the_measurement_used_is_the_prompt_that_is_frozen():
    """Every baseline card in evals/history/ names the frozen prompt."""
    cards = sorted((ROOT / "evals" / "history").glob("*.baseline-card.json"))
    assert cards, "no baseline card in evals/history/"
    for card in cards:
        assert FROZEN["prompt.txt"] in card.read_text(encoding="utf-8"), (
            f"{card.name} was measured on a prompt that is not the frozen one"
        )


def test_the_adr_records_the_same_hashes():
    """The ADR is prose; this file is the guard. They say the same thing or neither is true."""
    recorded = dict(ADR_ROW.findall(ADR.read_text(encoding="utf-8")))
    assert recorded == FROZEN, "ADR-0002's table and this test disagree"


def test_the_control_has_not_changed_since_tag_m00():
    tag = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", "refs/tags/m00"],
        cwd=ROOT, capture_output=True, text=True,
    )  # fmt: skip
    if tag.returncode != 0:
        pytest.skip("tag m00 is not in this checkout; the hashes above are the freeze until it is")
    diff = subprocess.run(
        ["git", "diff", "--stat", "m00", "HEAD", "--", "src/baseline"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )  # fmt: skip
    assert not diff.stdout.strip(), f"src/baseline/ has changed since tag m00:\n{diff.stdout}"
