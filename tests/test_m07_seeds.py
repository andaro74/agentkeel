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
from tests.test_m06_seeds import (  # noqa: F401  (worktree: a fixture)
    NOT_RUN,
    SeedBroken,
    holds,
    stand_in_lookup,
    worktree,
)

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
def test_s0_app_token_refuses_a_call_with_no_repository(monkeypatch):
    """`app_token()` with no repository mints the installation's token with `scope = {}`: every
    permission the App holds, on every repository it reaches (open.md row 2). After the grant that
    token could relax any agent repository's ruleset. Called with None, it must refuse and send no
    request for a token: a signature with no default would not be a refusal (cold review F1,
    security-reviewer 20 on M07 PR 1). GitHub is a stub here; the key is made for the test."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    from scripts import platform_check

    holds("repository" in inspect.signature(platform_check.app_token).parameters,
          "app_token() still takes the repository it mints for")  # fmt: skip
    pem = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()  # fmt: skip
    sent: list[tuple[str, str, Any]] = []

    def stub(path: str, *, method: str = "GET", body: Any = None, raw: bool = False) -> Any:
        sent.append((method, path, body))
        return {"id": 1, "token": "not-a-token"}

    monkeypatch.setattr(platform_check, "gh", stub)
    try:
        platform_check.app_token(1, "an-organisation", pem, None)
        refused = False
    except (TypeError, ValueError):
        refused = True
    minted = [body for method, _path, body in sent if method == "POST"]
    assert refused and not minted, (
        "seed S0: app_token() can be called with no repository, and then mints every permission on every "
        f"repository (it asked for a token with scope {minted})")


@expected_failure
def test_s0_the_installations_grant_is_read_back():
    """An installation as GitHub returns it to its App, for each of the three Apps Security ruled on
    2026-10-02 (milestones/M07/rulings/pr2-security.md, item 2): as `grant.json` names it, and with a
    permission, a level, a repository, a selection or an account that no ruling covers. A reader must
    pass the first and refuse each of the others, naming what is not covered. Today nothing reads an
    installation.

    **The shape changed at M07 PR 2's first commit, before the reader** (feasibility.md section 4): the
    grant was one flat permission set and is now one entry per App, in the ruling's `grant:` block's
    shape. `grant_errors(installation, environment, grant)` keeps its three arguments and finds the
    App by the installation's `app_slug`. Every planted reason of PR 1 is still asked for (`members`,
    `scratch-repo`, `contents`, `repository_selection`), each on the App where the ruling makes it one."""
    from scripts import platform_check

    grant = fixture("s0-app-token/grant.json")
    holds(sorted(a for a in grant if a != "environments") == ["agentkeel-observer", "agentkeel-platform", "agentkeel-upgrades"],
          "the grant names three Apps")  # fmt: skip
    platform, upgrades = grant["agentkeel-platform"], grant["agentkeel-upgrades"]
    ruled, uncovered = fixture("s0-app-token/installation_as_ruled.json"), fixture("s0-app-token/installation_uncovered.json")
    environment = fixture("s0-app-token/environment_as_ruled.json")
    holds(ruled["permissions"] == platform["permissions"] and ruled["app_id"] == platform["app_id"],
          "the first installation is the grant's, for the App that posts the check")  # fmt: skip
    holds("members" in uncovered["permissions"] and "members" not in platform["permissions"],
          "the second installation holds a permission the grant does not name")  # fmt: skip
    check = reader(platform_check, "grant_errors", "S0", "nothing reads the installation's grant back")
    assert check(ruled, environment, grant) == []
    errors = check(uncovered, environment, grant)
    assert any("members" in e for e in errors), errors
    # The same keys and the same names, one level raised (security-reviewer 19): a reader that compares
    # key sets and ignores values would pass it.
    raised = fixture("s0-app-token/installation_raised.json")
    holds(set(raised["permissions"]) == set(platform["permissions"]) and raised["repositories"] == ruled["repositories"],
          "the third installation holds no new permission name and no new repository")  # fmt: skip
    holds(raised["permissions"]["contents"] == "write", "the third installation raises contents to write")
    errors = check(raised, environment, grant)
    assert any("contents" in e for e in errors), errors
    # 5144253 is never installed on the personal account, where main's required checks are names any App
    # with checks: write could answer to (item 2; security-reviewer 2).
    personal = fixture("s0-app-token/installation_on_personal_account.json")
    holds(personal["app_id"] == 5144253 and personal["account"]["login"] == "andaro74",
          "the fourth installation is the checking App on the personal account")  # fmt: skip
    errors = check(personal, environment, grant)
    assert any("andaro74" in e for e in errors), errors

    # The App that opens pull requests: on the personal account it reaches one repository, by name.
    upgrades_environment = fixture("s0-app-token/environment_upgrades_as_ruled.json")
    opens = fixture("s0-app-token/upgrades_as_ruled.json")
    holds(opens["permissions"] == upgrades["permissions"] and opens["repositories"] == upgrades["repository_selection"]["andaro74"],
          "the upgrades App on the personal account is the grant's")  # fmt: skip
    holds("checks" not in upgrades["permissions"] and "administration" not in upgrades["permissions"],
          "the App that opens a pull request can neither post the check nor administer")  # fmt: skip
    assert check(opens, upgrades_environment, grant) == []
    assert check(fixture("s0-app-token/upgrades_org_as_ruled.json"), upgrades_environment, grant) == []
    errors = check(fixture("s0-app-token/upgrades_uncovered.json"), upgrades_environment, grant)
    assert any("scratch-repo" in e for e in errors) and any("checks" in e for e in errors), errors
    widened = fixture("s0-app-token/upgrades_widened.json")
    holds(widened["repository_selection"] == "all" and widened["repositories"] == opens["repositories"],
          "the widened installation names no new repository and reaches all of them")  # fmt: skip
    errors = check(widened, upgrades_environment, grant)
    assert any("repository_selection" in e for e in errors), errors

    # The App that reads: a write level on it is not covered.
    observer_environment = fixture("s0-app-token/environment_observer_as_ruled.json")
    assert check(fixture("s0-app-token/observer_as_ruled.json"), observer_environment, grant) == []
    errors = check(fixture("s0-app-token/observer_writes.json"), observer_environment, grant)
    assert any("pull_requests" in e for e in errors), errors

    # An App the grant does not name, an id that is not the named App's, a grant with no id yet (the
    # ruling's own block until the App exists), and an App's key read in another App's environment.
    errors = check(fixture("s0-app-token/unnamed_app.json"), environment, grant)
    assert any("agentkeel-other" in e for e in errors), errors
    errors = check(fixture("s0-app-token/another_apps_id.json"), observer_environment, grant)
    assert any("5200009" in e for e in errors), errors
    no_id = {**grant, "agentkeel-observer": {**grant["agentkeel-observer"], "app_id": None}}
    errors = check(fixture("s0-app-token/observer_as_ruled.json"), observer_environment, no_id)
    assert any("app_id" in e for e in errors), errors
    errors = check(ruled, upgrades_environment, grant)
    assert any("platform-upgrades" in e for e in errors), errors


@expected_failure
def test_s0_the_key_environment_is_read_back():
    """The `platform-app` environment as GitHub returns it, twice: one branch policy, `main`, with no
    admin bypass, as `grant.json` names it; and with a second branch policy and `can_admins_bypass`
    true. A reader must pass the first and refuse the second for both. Today nothing reads it
    (open.md row 20). The live value of `can_admins_bypass` was true at M07 PR 1
    (runs/platform_app_environment.json) and was switched off by Security on 2026-10-02
    (runs/platform_app_environment_after.json). From M07 PR 2's first commit the grant names the
    environments' rules once, under `environments`, for all three Apps' environments."""
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
    # One policy still named main, but a tag policy, not a branch (security-reviewer 19).
    tag = fixture("s0-app-token/environment_tag.json")
    holds([(p["name"], p["type"]) for p in tag["branch_policies"]] == [("main", "tag")], "the third environment's one policy is a tag")
    errors = check(installation, tag, grant)
    assert any("tag" in e for e in errors), errors
    # The key is one secret of its environment and not a secret of the repository, where any workflow
    # on any branch could read it (item 6; security-reviewer 11).
    holds(grant["environments"]["branch_policies"] == [{"name": "main", "type": "branch"}]
          and grant["environments"]["can_admins_bypass"] is False, "the grant names main only, with no admin bypass")  # fmt: skip
    errors = check(installation, fixture("s0-app-token/environment_key_in_the_repository.json"), grant)
    assert any("A_SECOND_SECRET" in e for e in errors) and any("repository secret" in e for e in errors), errors


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
    # The platform side carries a workflow and an agent.py too: a reader that copies whatever is there
    # brings them, and that is the arm of F7.1 the fixture must be able to fire (cold review F2).
    holds((platform / ".github" / "workflows" / "platform.yml").is_file() and (platform / "agent.py").is_file(),
          "the platform side carries a workflow and an agent.py, neither platform-owned")  # fmt: skip
    upgrade = module("scripts.platform_upgrade", "S1", "nothing computes an agent's platform upgrade")
    changed: dict[str, str] = upgrade.diff(agent, platform)
    outside = sorted(set(changed) - PLATFORM_OWNED)
    assert not outside, f"the upgrade touches paths the platform does not own: {outside}"
    assert set(changed) == {"manifest.yaml", "server.py"}, sorted(changed)
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
    # The reader must also hold a retirement that held, and refuse one for the bundle alone and one whose
    # invocation was refused for access, not for the deletion (cold review F3; legal-compliance 7;
    # security-reviewer 15).
    held = read(fixture("s2-retired-agent/observation_held.json"), 3600.0)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held
    no_bundle = read(fixture("s2-retired-agent/observation_no_bundle.json"), 3600.0)
    assert no_bundle["held"] is False and len(no_bundle["reasons"]) == 1 and "bundle" in no_bundle["reasons"][0], no_bundle
    denied = read(fixture("s2-retired-agent/observation_access_denied.json"), 3600.0)
    assert denied["held"] is False and len(denied["reasons"]) == 1 and "invocation" in denied["reasons"][0], denied


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
    held = read(fixture("s3-rollback/observation_held.json"))  # the tree's digest live: held (cold review F3)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held


@expected_failure
def test_s3_the_rollback_was_made():
    """model-watch's draft swap pull request on refagent, merged if its envelope is GREEN, then
    reverted; or the fallback the run file names before any run (SPEC/07 §5, item 16)."""
    run = run_file("f7_3_rollback.yaml", "S3", 2)
    observed = made(run)
    assert all(o.get("repository") and o.get("pull_request") for o in observed), observed


# --- S4: panel 2 forced to show GREEN on a RED envelope -----------------------

PANEL_2 = "infra/grafana/panel2.json"  # the dashboard's path from PR 2 (Security's)
RED_ENVELOPE = "6f3d1618f42acbb217f7bcd62ecf2fc000ac4a9f"  # on main since M01 PR 2, RED
GREEN_ENVELOPE = "245eb9baf796cd9ceed652abe3805825208358c9"  # row 6's: its stored verdict is GREEN


def validate_over(tree: Path) -> dict[str, list[str]]:
    """Each `validate` check's errors over `tree`, by check name, but those in NOT_RUN (M06's helper,
    against this file's base)."""
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


@expected_failure
def test_s4_a_panel_2_query_that_computes_the_verdict_is_refused(worktree):  # noqa: F811
    """Panel 2 of S4's dashboard selects the constant 'GREEN' as its verdict column. `validate` must
    refuse a panel 2 query that does anything but select the verdict as stored (F7.4). Today nothing
    reads panel 2: placed at infra/grafana/panel2.json, `validate` over the tree is green."""
    dashboard = fixture("s4-panel2/dashboard.json")
    panel = next((p for p in dashboard.get("panels", []) if p.get("id") == 2), None)
    holds(panel is not None, "S4's dashboard has a panel 2")
    holds("'GREEN' AS verdict" in panel["targets"][0]["rawSQL"], "S4's panel 2 computes its verdict")
    tree = worktree()
    (tree / PANEL_2).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURES / "s4-panel2" / "dashboard.json", tree / PANEL_2)
    errors = validate_over(tree)
    refusing = {name for name, errs in errors.items() if any(PANEL_2 in e.replace("\\", "/") for e in errs)}
    holds(not refusing & BASE_CHECKS, f"no check at the base refuses the fixture ({sorted(refusing & BASE_CHECKS)})")
    refused = sorted(name for name in refusing - BASE_CHECKS if "panel 2" in name)
    assert refused, "seed S4: no check that reads panel 2's query refused a computed verdict"


@expected_failure
def test_s4_a_green_row_for_a_red_envelope_is_found_by_build():
    """Panel 2's rows as Grafana's /api/ds/query returns them say GREEN for 6f3d161; the envelope on
    main says RED. `build.panel_verdict_mismatch(frame, history_dir)` must return that commit. Today
    nothing compares a panel's verdict with an envelope."""
    from src.verdict import build

    frame = fixture("s4-panel2/frame.json")
    fields = [f["name"] for f in frame["results"]["A"]["frames"][0]["schema"]["fields"]]
    values = frame["results"]["A"]["frames"][0]["data"]["values"]
    rows = dict(zip(values[fields.index("commit")], values[fields.index("verdict")], strict=True))
    holds(rows.get(RED_ENVELOPE) == "GREEN", "S4's panel rows say GREEN for the envelope")
    envelope = json.loads((HISTORY / f"{RED_ENVELOPE}.json").read_text(encoding="utf-8"))
    holds(envelope["verdict"] == "RED", "the envelope on main says RED")
    # A second row, GREEN for an envelope that stores GREEN: the comparison must not name it (cold review F3).
    holds(rows.get(GREEN_ENVELOPE) == "GREEN", "S4's panel rows say GREEN for a second envelope")
    holds(json.loads((HISTORY / f"{GREEN_ENVELOPE}.json").read_text(encoding="utf-8"))["verdict"] == "GREEN",
          "the second envelope on main stores GREEN")  # fmt: skip
    compare = reader(build, "panel_verdict_mismatch", "S4", "nothing compares panel 2's verdicts with the envelopes")
    assert compare(frame, HISTORY) == [RED_ENVELOPE]


# --- S5: a surface plant goes silent ------------------------------------------


@expected_failure
def test_s5_a_silent_surface_plant_is_counted():
    """A run's results for the surfaces' plants with one reader's result missing: panel 1's plant
    fired, panel 2's did not report. `plants.SURFACE_PLANTS` must name the two, and
    `build.surface_plants(results)` must give plants_expected 2, plants_fired 1 and name the silent
    one (F7.5). Today no control names a surface's plants and nothing counts them."""
    from src.verdict import build, plants

    results = fixture("s5-silent-surface-plant/results.json")
    holds(list(results) == ["tests/fixtures/m06/s4-panel1/"] and results["tests/fixtures/m06/s4-panel1/"] is True,
          "the run reports panel 1's plant as fired and says nothing of panel 2's")  # fmt: skip
    named = reader(plants, "SURFACE_PLANTS", "S5", "no control names a surface's plants")
    assert sorted(named) == ["tests/fixtures/m06/s4-panel1/", "tests/fixtures/m07/s4-panel2/"], named
    count = reader(build, "surface_plants", "S5", "nothing counts a surface's plants")
    counted = count(results)
    assert counted["plants_expected"] == 2 and counted["plants_fired"] == 1, counted
    assert counted["silent"] == ["tests/fixtures/m07/s4-panel2/"], counted
    full = count({plant: True for plant in named})  # both fired: nothing silent (cold review F3)
    assert full["plants_expected"] == 2 and full["plants_fired"] == 2 and full["silent"] == [], full
