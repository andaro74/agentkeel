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

# `validate`'s sixteen checks at M06 PR 1's base (0b96da4). A seed is read only
# by a check added after these, whose name says what it reads (cold review F1
# on PR 1): a refusal by one of these, or by a new check about something else,
# is not the planted reason, and must not take a strict marker off.
BASE_CHECKS = frozenset({
    "golden front matter", "golden citations exist in data/", "ruling front matter", "workflow-hash",
    "manifest schema", "cdk-nag, every stack", "CODEOWNERS complete, single-owner, logins real",
    "relaxes: on every bar", "edges two-sided, no cycle, ceilings within bounds",
    "golden ids against origin/main", "computed semver",
    "live main ruleset equals its export, bypass_actors []",
    "plant controls name live goldens of their kind",
    "golden/corpus overlap (12 words), no row id in the corpus",
    "admitted.yaml is the corpus, byte for byte, under a Data Owner ruling",
    "deprecated_after more than 30 days away, or null",
})


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


def validate_over(tree: Path) -> dict[str, list[str]]:
    """Each `validate` check's errors over `tree`, by check name, but those in NOT_RUN.

    The checks are this checkout's (src/validate/ as imported here), run against `tree`; the two
    are the same code in a clean checkout, which is where the seed tests are read."""
    from src.validate import checks

    holds(BASE_CHECKS <= set(checks.CHECKS), "every check at the base is still in validate")
    errors: dict[str, list[str]] = {}
    for name, check in checks.CHECKS.items():
        if name in NOT_RUN:
            continue
        if "lookup" in inspect.signature(check).parameters:
            errors[name] = check(tree, lookup=stand_in_lookup)
        else:
            errors[name] = check(tree)
    return errors


def refused_by(errors: dict[str, list[str]], about: str, reads: str) -> list[str]:
    """The checks added since the base whose name says they read `reads` and that refused `about`.

    A base check refusing the fixture means the fixture carries a second fault, and is SeedBroken."""
    refusing = {name for name, errs in errors.items() if any(about in e.replace("\\", "/") for e in errs)}
    holds(not refusing & BASE_CHECKS, f"no check at the base refuses the fixture ({sorted(refusing & BASE_CHECKS)})")
    return sorted(name for name in refusing - BASE_CHECKS if reads in name)


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


# --- S1a: an unassigned seat -------------------------------------------------


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
    refused = refused_by(validate_over(tree), f"agents/{AGENT}/", "seat")
    assert refused, "seed S1a: no check that reads seats refused the unassigned seats"


def test_s1a_reader_does_not_refuse_s1b(worktree):
    """Cold review F4 on PR 1: a seat check that refused every new agent folder would pass S1a. S1b's
    seats are assigned, so S1a's reader must not refuse it."""
    tree = worktree()
    with_agent(tree, "s1b-no-goldens")
    errors = validate_over(tree)
    seat_checks = [name for name in errors if name not in BASE_CHECKS and "seat" in name]
    holds(bool(seat_checks), "S1a's reader is in validate")
    refusing = [n for n in seat_checks if any(f"agents/{AGENT}/" in e.replace("\\", "/") for e in errors[n])]
    assert not refusing, f"S1a's reader refused S1b, whose seats are assigned: {refusing}"


# --- S1b: goldens under the minimum --------------------------------------------


def test_s1b_goldens_under_the_minimum_are_refused(worktree):
    """The same agent folder with every seat assigned and an empty goldens folder: a first PR adding
    it must not be mergeable (F6.1). Today `validate` over the tree with it is green: goldens are
    one folder, evals/goldens/v1/, and nothing asks an agent to bring any (SPEC/06 §3.4)."""
    tree = worktree()
    agent = with_agent(tree, "s1b-no-goldens")
    seats = yaml.safe_load((agent / "manifest.yaml").read_text(encoding="utf-8"))["seats"]
    holds(len(seats) == 7 and set(seats.values()) <= LOGINS, "S1b's seven seats are assigned")
    holds((agent / "goldens").is_dir() and not list((agent / "goldens").glob("g-*.yaml")), "S1b has no goldens")
    refused = refused_by(validate_over(tree), f"agents/{AGENT}/", "golden")
    assert refused, "seed S1b: no check that reads an agent's goldens refused an agent with none"


def test_s1b_reader_does_not_refuse_s1a(worktree):
    """Cold review F4 on PR 1, the other half: S1a's goldens are at the minimum and cite its own data,
    so S1b's reader must not refuse it. Each seed is refused by its own reader alone."""
    tree = worktree()
    with_agent(tree, "s1a-unassigned-seat")
    errors = validate_over(tree)
    golden_checks = [name for name in errors if name not in BASE_CHECKS and "golden" in name]
    holds(bool(golden_checks), "S1b's reader is in validate")
    refusing = [n for n in golden_checks if any(f"agents/{AGENT}/" in e.replace("\\", "/") for e in errors[n])]
    assert not refusing, f"S1b's reader refused S1a, whose goldens are at the minimum: {refusing}"


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


def test_s2_a_stand_in_for_the_platform_check_was_refused():
    """In an agent repository, a pull request whose own workflow answers to the platform check's name
    and never asks agentkeel for it. Refused when it is not mergeable and no check run on its head
    came from the platform's App (F6.2, BLOCK 2). Read by PR 4's run, not by this test."""
    run = run_file("f6_2_standin.yaml", "S2")
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed


# --- S3: the timed quickstart ----------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S3 is timed after M06 PR 2 merges (SPEC/06 §5.1)")
def test_s3_the_timed_quickstart_was_made():
    """The second developer runs the quickstart once, from the repository's created_at to the last of
    its four records (F6.3), with the first pull request refused on its planted reasons (F6.1's live
    half). Read by PR 4's run from GitHub, AWS and Grafana, and ruled on by build, not by this test."""
    run = run_file("f6_3_quickstart.yaml", "S3")
    holds("336113686" in str(run.get("principal")), "S3 names the second developer's account by id")
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed
    assert run.get("agent_name"), "seed S3: the agent's name was not stated before the run"


# --- S4: panel 1 shows an agent the registry does not ----------------------------

PANEL = "infra/grafana/panel1.json"  # the dashboard's path from PR 2 (finding 16: Security's)


def test_s4_a_panel_1_query_with_a_second_source_is_refused(worktree):
    """Panel 1 of S4's dashboard reads the registry and a static list naming ghost-agent. `validate`
    must refuse a panel 1 query that names anything but the registry (finding 11). Today nothing
    reads a dashboard: placed at infra/grafana/panel1.json, `validate` over the tree is green."""
    import json

    dashboard = json.loads((FIXTURES / "s4-panel1" / "dashboard.json").read_text(encoding="utf-8"))
    panel = next((p for p in dashboard.get("panels", []) if p.get("id") == 1), None)
    holds(panel is not None, "S4's dashboard has a panel 1")
    sources = {t["datasource"]["uid"] for t in panel["targets"]}
    holds(sources == {"registry", "static"}, "S4's panel 1 reads the registry and one other source")
    tree = worktree()
    (tree / PANEL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURES / "s4-panel1" / "dashboard.json", tree / PANEL)
    refused = refused_by(validate_over(tree), PANEL, "panel")
    assert refused, "seed S4: no check that reads panel 1's query refused a second source"


def test_s4_a_panel_row_with_no_registry_row_is_found_by_build():
    """Panel 1's rows as Grafana's /api/ds/query returns them name ghost-agent; the registry scan does
    not. The observer writes both lists raw, and `build` compares them by agent name (BLOCK 3):
    `build.panel_not_in_registry(frame, registry)` must return ["ghost-agent"]. Today build has no
    such comparison, and nothing else in the tree compares a panel with the registry."""
    import json

    from src.verdict import build

    frame = json.loads((FIXTURES / "s4-panel1" / "frame.json").read_text(encoding="utf-8"))
    registry = json.loads((FIXTURES / "s4-panel1" / "registry.json").read_text(encoding="utf-8"))
    rows = frame["results"]["A"]["frames"][0]["data"]["values"][0]
    holds("ghost-agent" in rows and "refagent" in rows, "S4's panel rows name refagent and ghost-agent")
    holds([i["name"]["S"] for i in registry["Items"]] == ["refagent"], "S4's registry names refagent only")
    compare = getattr(build, "panel_not_in_registry", None)
    assert compare is not None, "seed S4: nothing compares panel 1's rows with the registry"
    assert compare(frame, registry) == ["ghost-agent"]
