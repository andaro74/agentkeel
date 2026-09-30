"""M06's seeded cases (SPEC/06 §5), committed before the code that reads them.

Two kinds. **Code seeds** (S1a, S1b, S4) are fixtures under
`tests/fixtures/m06/`: each test puts its fixture where the reader will look,
in a detached worktree of HEAD, and asks the readers in the tree to refuse it.
Today none does, and that is the planted failure. **Attempt seeds** (S2, S3)
are run files under `milestones/M06/runs/`, each the attempt to make with
`observed: null`, M05's pattern: the test reads the file as the human filled
it. What records an attempt is `scripts/observe_template.py` reading GitHub,
Grafana and AWS, and `build` ruling on what it wrote, not this test (SPEC/06
§4): the code seeds' tests are the test-only witnesses `F6_1` and `F6_4` are
built from, and the attempt tests write no check.

Each is marked `xfail(strict=True, raises=...)` with the one exception class
its planted reason raises, so an exception of any other class (a moved
fixture, a run file that no longer parses) is a failure, not an expected one.
Preconditions raise `SeedBroken`. Each was run once with `--runxfail` and its
message read, and the marker comes off in the commit that lands the reader
(or records the attempt). Nothing here calls AWS, a model, or GitHub.
"""

from __future__ import annotations

import inspect
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT

RUNS = ROOT / "milestones" / "M06" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m06"
AGENT = "premiere-desk"  # the fixtures' agent: fictional, as the slate is

# `validate`'s checks a seed test does not run: the cdk-nag synth takes minutes
# and reads no manifest, and the live ruleset check reads the GitHub API. A
# check that takes a `lookup` (M02's CODEOWNERS logins) is given LOGINS below
# instead of the API, so no test here reaches GitHub.
NOT_RUN = {"cdk-nag, every stack", "live main ruleset equals its export, bypass_actors []"}
LOGINS = {"andaro74"}  # the one login a stand-in lookup answers for (R1: every seat is the author)


class SeedBroken(Exception):
    """A seed's own precondition failed. Not AssertionError, which the strict markers expect of the
    planted failure: a broken seed must fail the run, not pass as an expected one (M04's rule)."""


def holds(condition: bool, message: str) -> None:
    if not condition:
        raise SeedBroken(message)


def stand_in_lookup(login: str) -> tuple[bool, str]:
    return (login in LOGINS, "stand-in lookup (tests/test_m06_seeds.py)")


@pytest.fixture
def worktree():
    """A detached worktree of HEAD; removed after the test."""
    trees: list[Path] = []

    def make() -> Path:
        tree = Path(tempfile.mkdtemp()) / "tree"
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), "HEAD"],
                       cwd=ROOT, check=True, capture_output=True)  # fmt: skip
        trees.append(tree)
        return tree

    yield make
    for tree in trees:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False,
                       capture_output=True)  # fmt: skip


def validate_over(tree: Path) -> list[str]:
    """Every error the tree's own `validate` checks return over `tree`, but those in NOT_RUN."""
    from src.validate import checks

    errors: list[str] = []
    for name, check in checks.CHECKS.items():
        if name in NOT_RUN:
            continue
        if "lookup" in inspect.signature(check).parameters:
            errors += check(tree, lookup=stand_in_lookup)
        else:
            errors += check(tree)
    return errors


def with_agent(tree: Path, fixture: str) -> Path:
    """Put a fixture agent folder at agents/premiere-desk/ in `tree`, as a first PR would."""
    from src import manifest

    source = FIXTURES / fixture
    holds((source / "manifest.yaml").is_file(), f"{fixture} carries a manifest")
    target = tree / "agents" / AGENT
    shutil.copytree(source, target)
    doc = yaml.safe_load((target / "manifest.yaml").read_text(encoding="utf-8"))
    holds(doc.get("name") == AGENT, f"{fixture}'s manifest is {AGENT}'s")
    holds(not manifest.schema_errors(doc), f"{fixture}'s manifest validates, so the schema is not what refuses it")
    return target


def about_the_agent(errors: list[str]) -> list[str]:
    return [e for e in errors if f"agents/{AGENT}/" in e.replace("\\", "/")]


# --- S1a: an unassigned seat -------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S1a's reader is M06 PR 2's (SPEC/06 §6)")
def test_s1a_an_unassigned_seat_is_refused(worktree):
    """The template's manifest with all seven seats null, beside one ordinary and one trap golden:
    a first PR adding it must not be mergeable (F6.1). Today `validate` over the tree with it is
    green: no check reads a seat's value, though SPEC/00 R1 listed one from M01 (SPEC/06 §3.3)."""
    tree = worktree()
    agent = with_agent(tree, "s1a-unassigned-seat")
    seats = yaml.safe_load((agent / "manifest.yaml").read_text(encoding="utf-8"))["seats"]
    holds(len(seats) == 7 and all(v is None for v in seats.values()), "S1a's seven seats are null")
    goldens = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((agent / "goldens").glob("g-*.yaml"))]
    holds(sorted(g["kind"] for g in goldens) == ["ordinary", "trap"], "S1a's goldens are at the minimum")
    refused = about_the_agent(validate_over(tree))
    assert any("seat" in e for e in refused), f"seed S1a: no check refused the unassigned seats ({refused})"


# --- S1b: goldens under the minimum --------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S1b's reader is M06 PR 2's (SPEC/06 §6)")
def test_s1b_goldens_under_the_minimum_are_refused(worktree):
    """The same agent folder with every seat assigned and an empty goldens folder: a first PR adding
    it must not be mergeable (F6.1). Today `validate` over the tree with it is green: goldens are
    one folder, evals/goldens/v1/, and nothing asks an agent to bring any (SPEC/06 §3.4)."""
    tree = worktree()
    agent = with_agent(tree, "s1b-no-goldens")
    seats = yaml.safe_load((agent / "manifest.yaml").read_text(encoding="utf-8"))["seats"]
    holds(len(seats) == 7 and set(seats.values()) <= LOGINS, "S1b's seven seats are assigned")
    holds((agent / "goldens").is_dir() and not list((agent / "goldens").glob("g-*.yaml")), "S1b has no goldens")
    refused = about_the_agent(validate_over(tree))
    assert any("golden" in e for e in refused), f"seed S1b: no check refused an agent with no goldens ({refused})"


# --- The attempt seeds' run files (S2, S3) -----------------------------------


def run_file(name: str, seed: str) -> dict[str, Any]:
    run = yaml.safe_load((RUNS / name).read_text(encoding="utf-8"))
    holds(isinstance(run, dict) and run.get("seed") == seed, f"{name} is seed {seed}'s run file")
    holds(isinstance(run.get("attempts"), list) and run["attempts"], f"{name} names the attempts to make")
    holds(all(a.get("what") and a.get("refused_when") for a in run["attempts"]),
          f"{name}: every attempt says what it is and when it counts as refused")  # fmt: skip
    return run


def made(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The observed entries, one per attempt: the planted failure is that there are none yet."""
    observed = run["observed"]
    assert observed is not None, f"seed {run['seed']}: the attempt has not been made"
    assert len(observed) == len(run["attempts"]), f"seed {run['seed']}: every attempt is made, not some"
    return observed


# --- S2: a stand-in for the platform check -------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S2 is attempted after M06 PR 2 merges (SPEC/06 §5.1)")
def test_s2_a_stand_in_for_the_platform_check_was_refused():
    """In an agent repository, a pull request whose own workflow answers to the platform check's name
    and never asks agentkeel for it. Refused when it is not mergeable and no check run on its head
    came from the platform's App (F6.2, BLOCK 2). Read by PR 3's run, not by this test."""
    run = run_file("f6_2_standin.yaml", "S2")
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed


# --- S3: the timed quickstart ----------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S3 is timed after M06 PR 2 merges (SPEC/06 §5.1)")
def test_s3_the_timed_quickstart_was_made():
    """The second developer runs the quickstart once, from the repository's created_at to the last of
    its four records (F6.3), with the first pull request refused on its planted reasons (F6.1's live
    half). Read by PR 3's run from GitHub, AWS and Grafana, and ruled on by build, not by this test."""
    run = run_file("f6_3_quickstart.yaml", "S3")
    holds("336113686" in str(run.get("principal")), "S3 names the second developer's account by id")
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed
    assert run.get("agent_name"), "seed S3: the agent's name was not stated before the run"
