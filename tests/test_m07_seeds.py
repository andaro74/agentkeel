"""M07's seeded cases (SPEC/07 §5), committed before the code that reads them.

Two kinds. **Code seeds** are fixtures under `tests/fixtures/m07/`: each test
hands its fixture to the reader PR 2 must build, by the name fixed here, and
asks it to refuse the fixture for its planted reason. Today no such reader
exists, and that is the planted failure. **Attempt seeds** are run files under
`milestones/M07/runs/`, each the attempt to make with `observed: null`, M05's
and M06's pattern: the test reads the file as the human filled it. What records
an attempt is `scripts/observe_upgrade.py` reading GitHub, AWS and Grafana, and
`build` ruling on what it wrote, not this test (SPEC/07 §4): the fixture tests
are the test-only witnesses `F7_0` to `F7_5` are built from at PR 2, and the
run-file tests write no check.

Each is marked `xfail(strict=True, raises=AssertionError)`, so an exception of
any other class (a moved fixture, a run file that no longer parses) is a
failure, not an expected one. Preconditions raise `SeedBroken`. Each was run
once with `--runxfail` and its message read, and a marker comes off in the
commit that lands the reader (fixtures, PR 2) or records the attempt (run
files). Nothing here calls AWS, a model, or GitHub.

SPEC/06's S3, the timed quickstart, is received at M07 and not re-planted: its
run file and its test stay in `milestones/M06/runs/` and `tests/test_m06_seeds.py`.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT
from tests.test_m06_seeds import NOT_RUN, SeedBroken, holds, stand_in_lookup, worktree  # noqa: F401  (worktree: a fixture)

RUNS = ROOT / "milestones" / "M07" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m07"
HISTORY = ROOT / "evals" / "history"

# `validate`'s nineteen checks at M07 PR 1's base (57b9bf6, tag m06). A seed is read only by a check
# added after these, whose name says what it reads (M06's rule, cold review F1 on M06 PR 1): a refusal
# by one of these is not the planted reason, and must not take a strict marker off.
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
    "seats assigned, each a login that administers the repository",
    "an agent's goldens: one ordinary and one trap at least, citing its own data",
    "panel 1 queries the registry and nothing else",
})  # fmt: skip

expected_failure = pytest.mark.xfail(strict=True, raises=AssertionError, reason="planted at M07 PR 1 (SPEC/07 §5)")


def fixture(path: str) -> Any:
    file = FIXTURES / path
    holds(file.is_file(), f"{path} is in tests/fixtures/m07/")
    return json.loads(file.read_text(encoding="utf-8"))


def module(name: str, seed: str, what: str) -> Any:
    """A module PR 2 adds, by the name fixed here; the planted failure is that it is not there."""
    assert importlib.util.find_spec(name) is not None, f"seed {seed}: {what}"
    return importlib.import_module(name)


def reader(owner: Any, name: str, seed: str, what: str) -> Any:
    """A function PR 2 adds to a module that exists; the planted failure is that it is not there."""
    found = getattr(owner, name, None)
    assert found is not None, f"seed {seed}: {what}"
    return found


def run_file(name: str, seed: str, attempts: int) -> dict[str, Any]:
    run = yaml.safe_load((RUNS / name).read_text(encoding="utf-8"))
    holds(isinstance(run, dict) and run.get("seed") == seed, f"{name} is seed {seed}'s run file")
    holds(isinstance(run.get("attempts"), list) and len(run["attempts"]) == attempts, f"{name} names {attempts} attempts")
    holds(all(a.get("what") and a.get("refused_when") and a.get("recorded_when") for a in run["attempts"]),
          f"{name}: every attempt says what it is, when it counts and what records it")  # fmt: skip
    return run


def made(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The observed entries, one per attempt: the planted failure is that there are none yet."""
    observed = run["observed"]
    assert observed is not None, f"seed {run['seed']}: the attempt has not been made"
    assert len(observed) == len(run["attempts"]), f"seed {run['seed']}: every attempt is made, not some"
    return observed


# --- S0: the template's repair, read by CI ------------------------------------


@expected_failure
def test_s0_app_token_refuses_a_call_with_no_repository():
    """`app_token()` with no repository mints the installation's token with `scope = {}`: every
    permission the App holds, on every repository it reaches (open.md row 2). After the grant that
    token could relax any agent repository's ruleset. It must not be callable that way."""
    from scripts import platform_check

    parameters = inspect.signature(platform_check.app_token).parameters
    holds("repository" in parameters, "app_token() still takes the repository it mints for")
    assert parameters["repository"].default is inspect.Parameter.empty, (
        "seed S0: app_token() can be called with no repository, and then mints every permission on every repository")


@expected_failure
def test_s0_the_installations_grant_is_read_back():
    """The installation as GitHub returns it to the App, twice: as `grant.json` names it, and with
    `members: write` and a third repository that no ruling covers. A reader must pass the first and
    refuse the second, naming what is not covered. Today nothing reads an installation."""
    from scripts import platform_check

    grant = fixture("s0-app-token/grant.json")
    ruled, uncovered = fixture("s0-app-token/installation_as_ruled.json"), fixture("s0-app-token/installation_uncovered.json")
    environment = fixture("s0-app-token/environment_as_ruled.json")
    holds(ruled["permissions"] == grant["installation"]["permissions"], "the first installation is the grant's")
    holds("members" in uncovered["permissions"] and "members" not in grant["installation"]["permissions"],
          "the second installation holds a permission the grant does not name")  # fmt: skip
    check = reader(platform_check, "grant_errors", "S0", "nothing reads the installation's grant back")
    assert check(ruled, environment, grant) == []
    errors = check(uncovered, environment, grant)
    assert any("members" in e for e in errors) and any("scratch-repo" in e for e in errors), errors


@expected_failure
def test_s0_the_key_environment_is_read_back():
    """The `platform-app` environment as GitHub returns it, twice: one branch policy, `main`, with no
    admin bypass, as `grant.json` names it; and with a second branch policy and `can_admins_bypass`
    true. A reader must pass the first and refuse the second for both. Today nothing reads it
    (open.md row 20); the live value of `can_admins_bypass` is true (runs/platform_app_environment.json)."""
    from scripts import platform_check

    grant = fixture("s0-app-token/grant.json")
    installation = fixture("s0-app-token/installation_as_ruled.json")
    ruled, uncovered = fixture("s0-app-token/environment_as_ruled.json"), fixture("s0-app-token/environment_uncovered.json")
    holds([p["name"] for p in ruled["branch_policies"]] == ["main"] and ruled["can_admins_bypass"] is False,
          "the first environment is main only, with no admin bypass")  # fmt: skip
    holds(len(uncovered["branch_policies"]) == 2 and uncovered["can_admins_bypass"] is True,
          "the second environment has a second branch and an admin bypass")  # fmt: skip
    check = reader(platform_check, "grant_errors", "S0", "nothing reads the key's environment back")
    assert check(installation, ruled, grant) == []
    errors = check(installation, uncovered, grant)
    assert any("m07-*" in e for e in errors) and any("can_admins_bypass" in e for e in errors), errors


@expected_failure
def test_s0_the_owners_test_was_read():
    """The owner's test of the template, steps 2 to 4 again, on owner-check pull request 1; the
    platform check dispatched from a branch; the App's token asked to relax a ruleset. Each is made
    after M07 PR 2 merges and the grant (SPEC/07 §5.1), and read by the observer, not by this test."""
    run = run_file("f7_0_owner_test.yaml", "S0", 3)
    observed = made(run)
    assert all(o.get("what") and o.get("repository") for o in observed), observed


# --- S1: a platform bump opens a draft pull request ---------------------------

PLATFORM_OWNED = {"manifest.yaml", "server.py", "__init__.py"}


@expected_failure
def test_s1_a_platform_upgrade_changes_platform_owned_files_only():
    """An agent folder at `platform_version: m06` that carries a workflow of its own and an edited
    `agent.py`, beside the platform-owned files at a later version. The upgrade's diff must move
    `platform_version` and the guardrail pin, bring `server.py`, and leave the workflow, `agent.py`
    and the manifest's other fields alone (F7.1). Today nothing computes an upgrade: a person edits."""
    agent, platform = FIXTURES / "s1-platform-upgrade" / "agent", FIXTURES / "s1-platform-upgrade" / "platform"
    before = yaml.safe_load((agent / "manifest.yaml").read_text(encoding="utf-8"))
    target = json.loads((platform / "platform.json").read_text(encoding="utf-8"))
    holds(before["platform_version"] == "m06" and target["platform_version"] == "m07", "the fixture is one version behind")
    holds(before["guardrail"] != target["guardrail"], "the platform's guardrail pin moved")
    holds((agent / ".github" / "workflows" / "own.yml").is_file(), "the agent folder carries a workflow of its own")
    holds((agent / "server.py").read_text(encoding="utf-8") != (platform / "server.py").read_text(encoding="utf-8"),
          "the platform's server.py differs from the agent's")  # fmt: skip
    upgrade = module("scripts.platform_upgrade", "S1", "nothing computes an agent's platform upgrade")
    changed: dict[str, str] = upgrade.diff(agent, platform)
    assert set(changed) == {"manifest.yaml", "server.py"}, sorted(changed)
    assert not any(path.startswith(".github/") for path in changed), "the upgrade touches a workflow"
    after = yaml.safe_load(changed["manifest.yaml"])
    assert after["platform_version"] == "m07" and after["guardrail"] == target["guardrail"]
    assert {k: v for k, v in after.items() if k not in ("platform_version", "guardrail")} == {
        k: v for k, v in before.items() if k not in ("platform_version", "guardrail")}, "another manifest field moved"
    assert changed["server.py"] == (platform / "server.py").read_text(encoding="utf-8")


@expected_failure
def test_s1_the_platform_upgrade_was_made():
    """The template re-made from M07 PR 2's merge, and the draft pull request the platform must open
    in owner-check. Made after the owner's test and the timed run (SPEC/07 §5.1), read by the observer."""
    run = run_file("f7_1_platform_upgrade.yaml", "S1", 1)
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed


# --- S2: a retired agent's target is gone -------------------------------------


@expected_failure
def test_s2_a_retired_agent_that_still_answers_is_found_by_build():
    """The records of a retirement that did not hold: CloudTrail's DeleteAgentRuntime, a GetAgentRuntime
    that still finds the runtime after the limit, the retire job's invocation answered, and an answer
    record dated after the deletion. `build.f7_2(observation, max_seconds)` must read it as not held and
    name each (F7.2). Today nothing reads a retirement."""
    from src.verdict import build

    observation = fixture("s2-retired-agent/observation.json")
    holds(observation["delete_event"]["eventName"] == "DeleteAgentRuntime", "the fixture carries the deletion's record")
    holds(observation["get_runtime"]["found"] is True and observation["invocation"]["answered"] is True,
          "the runtime is still found and still answers")  # fmt: skip
    holds(observation["answer_records"][0]["last_modified"] > observation["delete_event"]["eventTime"],
          "an answer record is dated after the deletion")  # fmt: skip
    read = reader(build, "f7_2", "S2", "nothing reads a retired agent's records against each other")
    entry = read(observation, 3600.0)
    assert entry["read"] is True and entry["held"] is False, entry
    reasons = " ".join(entry["reasons"])
    assert "invocation" in reasons and "still exists" in reasons and "answer record" in reasons, entry["reasons"]


@expected_failure
def test_s2_the_retirement_was_made():
    """The retire workflow dispatched for owner-check, its draft pull request, the merge. Made last,
    after owner-check has deployed, answered, been listed and taken S1 (SPEC/07 §5.1)."""
    run = run_file("f7_2_retire.yaml", "S2", 1)
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed


# --- S3: a model-watch pull request is merged and rolled back -----------------


@expected_failure
def test_s3_a_rollback_that_leaves_the_new_digest_live_is_found_by_build():
    """After a revert's deploy completed, the runtime's image tags hold the upgrade's digest and not
    the digest the tree gives at the revert. `build.f7_3(observation)` must read it as not held and
    name the digest still live (F7.3). Today nothing compares the two after a merge to main."""
    from src.verdict import build

    observation = fixture("s3-rollback/observation.json")
    tags = observation["runtime"]["image_tags"]
    holds(observation["upgrade_digest"] in tags and observation["tree_digest_at_revert"] not in tags,
          "the runtime runs the upgrade's digest, not the revert's")  # fmt: skip
    holds(observation["revert_deploy"]["conclusion"] == "success", "the revert's deploy completed")
    read = reader(build, "f7_3", "S3", "nothing compares the runtime's digest with the tree's after a revert")
    entry = read(observation)
    assert entry["read"] is True and entry["held"] is False, entry
    assert any(observation["upgrade_digest"][:12] in reason for reason in entry["reasons"]), entry["reasons"]


@expected_failure
def test_s3_the_rollback_was_made():
    """model-watch's draft swap pull request on refagent, merged if its envelope is GREEN, then
    reverted; or the fallback the run file names before any run (SPEC/07 §5, item 16)."""
    run = run_file("f7_3_rollback.yaml", "S3", 2)
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed
