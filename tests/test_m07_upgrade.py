"""build's readings of claim 7 (`src/verdict/upgrade.py`; SPEC/07 §4), on observations made for the test.

The seed tests hold each fixture reader to its planted refusal. These hold what a fixture does not
reach: the unread arms (an attempt not made is unread, never held), each way a live reading can miss,
and the envelope's `upgrade` as PR 2's run writes it, with every live reading unread. Nothing here
calls AWS, a model, GitHub or Grafana.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.verdict import ROOT, plants, replay_history, upgrade
from src.verdict.template import Unreadable

FIXTURES = Path(__file__).parent / "fixtures" / "m07"
HISTORY = ROOT / "evals" / "history"
RUNS = ROOT / "milestones" / "M07" / "runs"
APP = 5144253
OPENER = {"id": 5200001, "slug": "agentkeel-upgrades"}
BOT = {"login": "agentkeel-upgrades[bot]", "type": "Bot", "app_id": 5200001}
PERSON = {"login": "andaro74", "type": "User", "app_id": None}
BARS = {"arrive_max_seconds": 4500.0, "deploy_max_seconds": 3600.0, "retire_max_seconds": 3600.0}
THRESHOLDS = {"upgrade": {"arrive_max_seconds": 4500, "deploy_max_seconds": 3600, "retire_max_seconds": 3600}}
NOW = "2026-10-06T12:00:00Z"


def fixture(path: str) -> Any:
    return json.loads((FIXTURES / path).read_text(encoding="utf-8"))


# --- F7.2 ------------------------------------------------------------------------------


@pytest.mark.parametrize("change, said", [
    (None, "no retirement observed"),
    ({"error": "AccessDenied on the bucket"}, "AccessDenied on the bucket"),
    ({"pull_request": {"merged": False, "merged_at": None}}, "has not merged"),
    ({"get_runtime": None}, "GetAgentRuntime not looked up"),
    ({"invocation": None}, "invocation not looked up"),
    ({"bundle": None}, "the bundle not looked up"),
    # Refused for access says nothing about whether the runtime is gone.
    ({"get_runtime": {"found": False, "error": "AccessDeniedException", "read_at": "2026-10-05T12:00:00Z"}}, "does not say"),
    # Still there, inside the limit: not yet a miss.
    ({"get_runtime": {"found": True, "status": "READY", "read_at": "2026-10-05T10:20:00Z"}}, "has not passed"),
])  # fmt: skip
def test_a_retirement_that_is_not_all_looked_up_is_unread_never_held(change, said):
    observation = None if change is None else {**fixture("s2-retired-agent/observation_held.json"), **change}
    entry = upgrade.f7_2(observation, 3600.0)
    assert entry["read"] is False and entry["held"] is None and said in entry["reasons"][0], entry


@pytest.mark.parametrize("change, said", [
    ({"delete_event": None}, "no DeleteAgentRuntime"),
    ({"delete_event": {"eventName": "UpdateAgentRuntime", "eventTime": "2026-10-05T10:00:00Z"}}, "no DeleteAgentRuntime"),
    ({"delete_event": {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T11:00:00Z"}}, "4200 s after the merge"),
    ({"delete_event": {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T09:00:00Z"}}, "earlier than the merge"),
    ({"invocation": {"answered": False, "error": "ResourceNotFoundException", "at": "2026-10-05T09:59:00Z"}}, "before the deletion"),
    ({"registry_row": {"name": "premiere-desk"}}, "no retired_at"),
])  # fmt: skip
def test_each_way_a_retirement_can_miss_is_named(change, said):
    entry = upgrade.f7_2({**fixture("s2-retired-agent/observation_held.json"), **change}, 3600.0)
    assert entry["read"] is True and entry["held"] is False and any(said in r for r in entry["reasons"]), entry


def test_a_held_retirement_carries_its_elapsed_time():
    entry = upgrade.f7_2(fixture("s2-retired-agent/observation_held.json"), 3600.0)
    assert entry == {"read": True, "held": True, "reasons": [], "elapsed_s": 600.0}
    assert upgrade.f7_2(fixture("s2-retired-agent/observation_held.json"), 599.0)["held"] is False  # the bar is read


# --- F7.3 ------------------------------------------------------------------------------


@pytest.mark.parametrize("change, said", [
    (None, "no rollback observed"),
    ({"revert": {"merged": False}}, "has not merged"),
    ({"revert_deploy": {"conclusion": None, "completed_at": None}}, "has not concluded"),
    ({"runtime": {"image_tags": None, "error": "AccessDeniedException"}}, "AccessDeniedException"),
    ({"tree_digest_at_revert": None}, "not read"),
    ({"runtime": {"image_tags": ["a" * 64], "read_at": "2026-10-06T09:59:00Z"}}, "before the revert's deploy completed"),
])  # fmt: skip
def test_a_rollback_that_is_not_all_read_is_unread(change, said):
    observation = None if change is None else {**fixture("s3-rollback/observation_held.json"), **change}
    entry = upgrade.f7_3(observation)
    assert entry["read"] is False and entry["held"] is None and said in entry["reasons"][0], entry


@pytest.mark.parametrize("change, said", [
    ({"revert_deploy": {"conclusion": "failure", "completed_at": "2026-10-06T10:00:00Z"}}, "concluded 'failure'"),
    ({"upgrade_digest": "a" * 64}, "nothing was rolled back"),
    ({"runtime": {"image_tags": ["a" * 64, "b" * 64], "read_at": "2026-10-06T10:05:00Z"}}, "still carries the upgrade's digest"),
    ({"runtime": {"image_tags": [], "read_at": "2026-10-06T10:05:00Z"}}, "does not carry the digest the tree gives"),
])  # fmt: skip
def test_each_way_a_rollback_can_miss_is_named(change, said):
    entry = upgrade.f7_3({**fixture("s3-rollback/observation_held.json"), **change})
    assert entry["read"] is True and entry["held"] is False and any(said in r for r in entry["reasons"]), entry


# --- F7.4 ------------------------------------------------------------------------------


def frame(rows: dict[str, str]) -> dict[str, Any]:
    return {"results": {"A": {"frames": [{"schema": {"fields": [{"name": "commit"}, {"name": "verdict"}]},
                                          "data": {"values": [list(rows), list(rows.values())]}}]}}}  # fmt: skip


def test_the_stored_verdicts_are_read_through_replay_history_and_a_bad_file_stops_the_read(tmp_path):
    stored = replay_history.verdicts(HISTORY)
    assert stored["6f3d1618f42acbb217f7bcd62ecf2fc000ac4a9f"] == "RED"
    assert stored["245eb9baf796cd9ceed652abe3805825208358c9"] == "GREEN"
    assert set(stored.values()) <= {"GREEN", "RED", "UNMEASURED"}
    (tmp_path / ("a" * 40 + ".json")).write_text(json.dumps({"commit": "b" * 40, "verdict": "GREEN"}), encoding="utf-8")
    with pytest.raises(ValueError, match="not the file name"):
        replay_history.verdicts(tmp_path)
    (tmp_path / ("a" * 40 + ".json")).write_text(json.dumps({"commit": "a" * 40, "verdict": "PASSED"}), encoding="utf-8")
    with pytest.raises(ValueError, match="not one build writes"):
        replay_history.verdicts(tmp_path)
    assert replay_history.verdicts(tmp_path / "absent") == {}


def test_panel_2_is_compared_by_commit_and_only_a_green_row_can_miss(tmp_path):
    for commit, verdict in (("a" * 40, "RED"), ("b" * 40, "UNMEASURED"), ("c" * 40, "GREEN")):
        (tmp_path / f"{commit}.json").write_text(json.dumps({"commit": commit, "verdict": verdict}), encoding="utf-8")
    shown = frame({"a" * 40: "GREEN", "b" * 40: "GREEN", "c" * 40: "GREEN", "d" * 40: "GREEN"})
    # d has no envelope in this tree: not compared (a pull request may be behind main).
    assert upgrade.panel_verdict_mismatch(shown, tmp_path) == ["a" * 40, "b" * 40]
    # A panel that shows RED for a GREEN envelope is wrong, and is not F7.4: the falsifier is GREEN over RED.
    assert upgrade.panel_verdict_mismatch(frame({"c" * 40: "RED", "a" * 40: "RED"}), tmp_path) == []
    entry = upgrade.f7_4({"error": None, "frame": shown}, tmp_path)
    assert entry["read"] is True and entry["held"] is False and entry["rows"] == 4 and entry["mismatched"] == ["a" * 40, "b" * 40]
    assert upgrade.f7_4({"error": None, "frame": frame({"c" * 40: "GREEN"})}, tmp_path)["held"] is True


@pytest.mark.parametrize("panel, said", [
    (None, "panel 2 was not read"),
    ({"error": "HTTPError 401", "frame": None}, "HTTPError 401"),
    ({"error": None, "frame": {"results": {}}}, "no results.A.frames"),
    ({"error": None, "frame": {"results": {"A": {"frames": [{"schema": {"fields": [{"name": "commit"}]}}]}}}}, "no `commit` and `verdict`"),
])  # fmt: skip
def test_a_panel_2_that_was_not_read_is_unread(tmp_path, panel, said):
    entry = upgrade.f7_4(panel, tmp_path)
    assert entry["read"] is False and entry["held"] is None and said in entry["reasons"][0], entry


def test_a_panel_that_shows_nothing_this_tree_holds_is_unread_not_held(tmp_path):
    entry = upgrade.f7_4({"error": None, "frame": frame({"d" * 40: "GREEN"})}, tmp_path)
    assert entry["read"] is False and "no commit this tree holds an envelope for" in entry["reasons"][0]
    with pytest.raises(Unreadable, match="twice"):
        upgrade.panel_rows({"results": {"A": {"frames": [frame({"a" * 40: "GREEN"})["results"]["A"]["frames"][0],
                                                         frame({"a" * 40: "RED"})["results"]["A"]["frames"][0]]}}})  # fmt: skip


# --- F7.5 ------------------------------------------------------------------------------


def junit(tmp_path: Path, cases: dict[str, str]) -> Path:
    body = "".join(f'<testcase classname="tests.t" name="{name}">{inner}</testcase>' for name, inner in cases.items())
    path = tmp_path / "junit.xml"
    path.write_text(f"<testsuites><testsuite>{body}</testsuite></testsuites>", encoding="utf-8")
    return path


def test_a_surface_plant_fired_only_when_every_test_that_reads_it_ran_and_passed(tmp_path):
    every = {name: "" for tests in plants.SURFACE_PLANTS.values() for name in tests}
    assert upgrade.surface_results(junit(tmp_path, every)) == {plant: True for plant in plants.SURFACE_PLANTS}
    panel2 = "tests/fixtures/m07/s4-panel2/"
    for inner in ("<failure/>", "<error/>", "<skipped/>"):
        results = upgrade.surface_results(junit(tmp_path, {**every, plants.SURFACE_PLANTS[panel2][0]: inner}))
        assert results[panel2] is False and results["tests/fixtures/m06/s4-panel1/"] is True
    missing = {k: v for k, v in every.items() if k != plants.SURFACE_PLANTS[panel2][1]}
    results = upgrade.surface_results(junit(tmp_path, missing))  # a test that did not run did not refuse anything
    counted = upgrade.surface_plants(results)
    assert counted == {"plants_expected": 2, "plants_fired": 1, "silent": [panel2]}
    assert upgrade.surface_plants(None)["plants_fired"] == 0 and upgrade.surface_plants({panel2: "yes"})["plants_fired"] == 0


def test_the_surfaces_tests_are_tests_that_exist():
    """A plant named for a test that is not there could never fire, and nobody would see why."""
    import tests.test_m06_seeds as m06
    import tests.test_m07_seeds as m07

    for names in plants.SURFACE_PLANTS.values():
        assert all(hasattr(m06, name) or hasattr(m07, name) for name in names), names


# --- F7.1: one upgrade's pull request -------------------------------------------------


def pull(**more: Any) -> dict[str, Any]:
    base = {
        "repository": "agentkeel-studio/owner-check", "pull_request": 3, "found": True, "error": None,
        "trigger": {"at": "2026-10-06T09:00:00Z", "what": "the template's push"},
        "author": BOT, "created_at": "2026-10-06T09:20:00Z", "merged": True, "merged_at": "2026-10-06T10:00:00Z",
        "files": ["manifest.yaml", "server.py"],
        "commits": [{"sha": "1" * 40, "author": BOT, "files": ["manifest.yaml", "server.py"]}],
        "required_on_head": {"platform-check": "success"}, "default_branch_commits_between": [],
        "workflows_sha256_changed": False,
    }  # fmt: skip
    return {**base, **more}


def test_an_upgrade_the_platform_opened_in_time_with_no_edit_is_held():
    reading = upgrade.pull_reading("platform", pull(), OPENER, BARS, NOW)
    assert reading["read"] is True and reading["held"] is True and reading["reasons"] == []
    assert reading["arrived_s"] == 1200.0 and reading["merged"] is True


@pytest.mark.parametrize("change, said", [
    ({"author": PERSON}, "opened by 'andaro74'"),
    ({"created_at": "2026-10-06T10:20:00Z"}, "arrived 4800 s after the trigger"),
    ({"created_at": "2026-10-06T08:00:00Z"}, "earlier than its trigger"),
    ({"files": ["manifest.yaml", ".github/workflows/own.yml"]}, "touches a workflow"),
    ({"files": ["manifest.yaml", "agent.py"]}, "changes agent.py, which a platform upgrade does not"),
    ({"commits": [{"sha": "1" * 40, "author": BOT, "files": ["manifest.yaml"]},
                  {"sha": "2" * 40, "author": PERSON, "files": ["server.py"]}]}, "a person's edit: 222222222222"),
    ({"workflows_sha256_changed": True}, "infra/workflows.sha256 changed"),
    ({"default_branch_commits_between": [{"sha": "3" * 40, "author": PERSON, "files": ["server.py", "agent.py"]}]},
     "a person's commit on the default branch"),
    ({"required_on_head": {"platform-check": "failure"}}, "merged with platform-check not green"),
    ({"required_on_head": {}}, "no required check read"),
])  # fmt: skip
def test_each_way_an_upgrade_needs_a_manual_edit_is_named(change, said):
    reading = upgrade.pull_reading("platform", pull(**change), OPENER, BARS, NOW)
    assert reading["read"] is True and reading["held"] is False and any(said in r for r in reading["reasons"]), reading


def test_a_ruling_file_is_not_a_persons_edit_and_only_where_a_seat_must_rule():
    """BLOCK 2: a model upgrade in agentkeel cannot merge without a seat ruling it."""
    ruled = pull(repository="andaro74/agentkeel", files=["agents/refagent/manifest.yaml", "milestones/M07/rulings/model-swap.md"],
                 commits=[{"sha": "1" * 40, "author": BOT, "files": ["agents/refagent/manifest.yaml"]},
                          {"sha": "2" * 40, "author": BOT, "files": ["milestones/M07/rulings/model-swap.md"]},
                          {"sha": "3" * 40, "author": PERSON, "files": ["milestones/M07/rulings/model-swap.md"]}],
                 required_on_head={"evals": "success", "checks": "success"})  # fmt: skip
    assert upgrade.pull_reading("model", ruled, OPENER, BARS, NOW, expects_ruling=True)["held"] is True
    # The same commit in an agent repository, which asks for no ruling, is an edit.
    reading = upgrade.pull_reading("model", ruled, OPENER, BARS, NOW)
    assert reading["held"] is False and any("a person's edit" in r for r in reading["reasons"])
    # A person's commit that touches the pin as well as the ruling is an edit either way.
    ruled["commits"][2]["files"].append("agents/refagent/manifest.yaml")
    assert upgrade.pull_reading("model", ruled, OPENER, BARS, NOW, expects_ruling=True)["held"] is False
    assert upgrade.is_ruling("milestones/M07/rulings/x.md") and not upgrade.is_ruling("milestones/M07/runs/x.md")
    assert not upgrade.is_ruling("docs/rulings/x.md") and not upgrade.is_ruling("milestones/M07/rulings/x.yaml")


def test_the_app_is_told_by_its_id_and_by_its_bot_login():
    assert upgrade.by_the_app(BOT, OPENER) and not upgrade.by_the_app(PERSON, OPENER)
    assert not upgrade.by_the_app({**BOT, "app_id": APP}, OPENER)  # the checking App is not the App that opens
    assert upgrade.by_the_app({"login": "agentkeel-upgrades[bot]", "type": "Bot"}, {"id": None, "slug": "agentkeel-upgrades"})
    assert not upgrade.by_the_app({"login": "agentkeel-upgrades", "type": "User"}, {"id": None, "slug": "agentkeel-upgrades"})


def test_no_pull_request_is_unread_inside_the_limit_and_a_miss_after_it():
    waiting = {"repository": "agentkeel-studio/owner-check", "pull_request": None, "found": False, "error": None,
               "trigger": {"at": "2026-10-06T11:30:00Z"}}  # fmt: skip
    assert upgrade.pull_reading("platform", waiting, OPENER, BARS, NOW)["read"] is False
    late = {**waiting, "trigger": {"at": "2026-10-06T10:00:00Z"}}
    reading = upgrade.pull_reading("platform", late, OPENER, BARS, NOW)
    assert reading["read"] is True and reading["held"] is False and "no pull request from the platform 7200 s" in reading["reasons"][0]
    assert upgrade.pull_reading("platform", None, OPENER, BARS, NOW)["reasons"] == ["unread: the attempt has not been made"]
    for unread in ({"files": None}, {"commits": []}, {"trigger": {}}, {"default_branch_commits_between": None},
                   {"commits": [{"sha": "2" * 40, "author": PERSON, "files": None}]}):  # fmt: skip
        assert upgrade.pull_reading("platform", pull(**unread), OPENER, BARS, NOW)["read"] is False, unread


def live(**more: Any) -> dict[str, Any]:
    return {"deploy": {"conclusion": "success", "completed_at": "2026-10-06T10:30:00Z"}, "tree_digest": "a" * 64,
            "runtime": {"image_tags": ["a" * 64], "read_at": "2026-10-06T10:40:00Z"}, **more}  # fmt: skip


def test_live_is_the_deploy_in_time_and_the_runtime_on_the_trees_bytes():
    merged_at = "2026-10-06T10:00:00Z"
    assert upgrade.live_reading(live(), merged_at, BARS) == {"read": True, "held": True, "reasons": [], "elapsed_s": 1800.0}
    for change, said in (({"deploy": {"conclusion": "failure", "completed_at": "2026-10-06T10:30:00Z"}}, "concluded 'failure'"),
                         ({"deploy": {"conclusion": "success", "completed_at": "2026-10-06T11:30:00Z"}}, "5400 s after the merge"),
                         ({"runtime": {"image_tags": ["b" * 64]}}, "no image of the agent carries the merged tree's digest")):  # fmt: skip
        reading = upgrade.live_reading(live(**change), merged_at, BARS)
        assert reading["held"] is False and any(said in r for r in reading["reasons"]), reading
    for unread in (None, {"error": "AccessDenied"}, live(deploy={}), live(runtime={"error": "AccessDeniedException"}), live(tree_digest=None)):
        assert upgrade.live_reading(unread, merged_at, BARS)["read"] is False, unread


# --- F7.0 ------------------------------------------------------------------------------

SEATS = {s: "andaro74" for s in ("product", "rule-owner", "data-owner", "tool-owner", "threshold-owner", "security", "engineering")}
GOLDENS = [{"file": "g-001.yaml", "kind": "ordinary", "retired": None}, {"file": "g-002.yaml", "kind": "trap", "retired": None}]


def app_check(conclusion: str, refused: list[str] | None = None) -> dict[str, Any]:
    return {"name": "platform-check", "app_id": APP, "conclusion": conclusion, "refused": refused or []}


def owner(**more: Any) -> dict[str, Any]:
    refused = [upgrade.SEAT_CHECK, upgrade.GOLDENS_CHECK]
    base = {
        "repository": "agentkeel-studio/owner-check", "pull_request": 1, "agent_name": "owner-check", "found": True,
        "error": None, "merged": True, "merged_at": "2026-10-06T10:00:00Z", "merge_head_sha": "3" * 40,
        "commits": [
            # M06's head, refused then on the hidden bypass_actors too: not the last faulty head.
            {"sha": "1" * 40, "seats": {s: None for s in SEATS}, "goldens": [], "read_error": None,
             "check_runs": [app_check("failure", [*refused, upgrade.RULESET_CHECK])]},
            {"sha": "2" * 40, "seats": {s: None for s in SEATS}, "goldens": [], "read_error": None,
             "check_runs": [app_check("failure", refused)]},
            {"sha": "3" * 40, "seats": SEATS, "goldens": GOLDENS, "read_error": None, "check_runs": [app_check("success")]},
        ],
        "merge_commit": {"sha": "4" * 40, "check_runs": [app_check("success")]},
        "deploy": {"run_id": "9", "conclusion": "success", "completed_at": "2026-10-06T10:40:00Z"},
        "answer": {"key": "envelopes/agents/owner-check/4.json", "goldens": {"g-001": {"pass": True}}},
        "registry_row": {"name": "owner-check", "repository": "agentkeel-studio/owner-check"}, "on_panel": True,
    }  # fmt: skip
    return {**base, **more}


def test_the_owners_test_is_held_on_the_last_head_with_the_templates_content():
    assert upgrade.owner_test(owner(), APP, BARS, NOW) == {"read": True, "held": True, "reasons": []}


def with_last_faulty(**check: Any) -> dict[str, Any]:
    test = owner()
    test["commits"][1]["check_runs"] = [{**test["commits"][1]["check_runs"][0], **check}] if check else []
    return test


@pytest.mark.parametrize("test, said", [
    (with_last_faulty(refused=[upgrade.SEAT_CHECK, upgrade.GOLDENS_CHECK, upgrade.RULESET_CHECK]), "and nothing else"),
    (with_last_faulty(refused=[upgrade.SEAT_CHECK]), "and nothing else"),
    (with_last_faulty(conclusion="success"), "was not refused"),
    (owner(merged=False), "is not merged"),
    (owner(merge_head_sha="2" * 40), "merged at a head with no success"),
    (owner(merge_commit={"sha": "4" * 40, "check_runs": []}), "the merge commit has no success"),
    (owner(deploy={"run_id": "9", "conclusion": "success", "completed_at": "2026-10-06T11:30:00Z"}), "deployed 5400 s"),
    (owner(deploy={"run_id": "9", "conclusion": "failure", "completed_at": "2026-10-06T10:40:00Z"}), "concluded 'failure'"),
    (owner(answer=None, deploy=None), "no deploy and answer record 7200 s after the merge"),
    (owner(answer={"goldens": {"g-001": {"pass": False}}}), "passed none of its own goldens"),
    (owner(registry_row=None), "no row for the agent"),
    (owner(on_panel=False), "panel 1 does not list"),
    (owner(commits=[owner()["commits"][2]]), "nothing was refused"),
])  # fmt: skip
def test_each_way_the_owners_test_can_miss_is_named(test, said):
    reading = upgrade.owner_test(test, APP, BARS, NOW)
    assert reading["read"] is True and reading["held"] is False and any(said in r for r in reading["reasons"]), reading


@pytest.mark.parametrize("test, said", [
    (None, "was not made"),
    (owner(found=False, error="HTTPError 404"), "HTTPError 404"),
    (owner(commits=[]), "commits were not read"),
    (with_last_faulty(), "has not checked the new head 222222222222"),
    (with_last_faulty(refused=None), "reasons on 222222222222 were not read"),
    (owner(on_panel=None), "panel 1 was not read"),
    (owner(answer=None, deploy=None, merged_at="2026-10-06T11:30:00Z"), "not deployed yet"),
])  # fmt: skip
def test_an_owners_test_that_is_not_all_read_is_unread(test, said):
    reading = upgrade.owner_test(test, APP, BARS, NOW)
    assert reading["read"] is False and said in reading["reasons"][0], reading
    assert upgrade.owner_test(owner(), None, BARS, NOW)["read"] is False  # no App id: whose check is not known


def recorded_dispatch() -> dict[str, Any]:
    """S0's second attempt as GitHub recorded it on 2026-10-02 (runs/f7_0_dispatch_from_branch.json),
    in the observer's shape: each job's steps counted, not listed."""
    raw = json.loads((RUNS / "f7_0_dispatch_from_branch.json").read_text(encoding="utf-8"))
    return {"repository": "andaro74/agentkeel", "run": raw["run"], "found": True, "error": None,
            "event": "workflow_dispatch", "head_branch": "m07-pr1", "path": ".github/workflows/platform-check.yml",
            "jobs": [{"name": j["name"], "conclusion": j["conclusion"], "steps": len(j["steps"]),
                      "runner_name": j["runner_name"],
                      "annotations": list(REFUSED_BY_THE_ENVIRONMENT) if j["conclusion"] == "failure" else []}
                     for j in raw["jobs"]]}  # fmt: skip


# GitHub's annotations on the refused `post` job of run 36963543726 (check run 110702392789), read 2026-10-02.
REFUSED_BY_THE_ENVIRONMENT = ["Branch \"m07-pr1\" is not allowed to deploy to platform-app due to environment protection rules.",
               "The deployment was rejected or didn't satisfy other protection rules."]


@pytest.mark.parametrize("change, said", [
    ({"annotations": []}, "does not say the environment refused the ref"),  # a failure that never started, for another reason
    ({"annotations": None}, "were not read"),
    ({"steps": None}, "were not read"),  # cold review F3: a job with no `steps` key read as "no step"
    ({"runner_name": None}, "were not read"),
])  # fmt: skip
def test_a_post_job_that_never_started_is_a_refusal_only_on_githubs_own_word(change, said):
    """Cold review F12 and F3 on M07 PR 2: the refusal was inferred from failure, no steps and no runner."""
    run = recorded_dispatch()
    run["jobs"][-1] |= change
    reading = upgrade.dispatch_from_a_branch(run)
    assert reading["read"] is False and reading["held"] is None and said in reading["reasons"][0]


def test_a_run_of_another_workflow_is_not_the_dispatch():
    run = recorded_dispatch() | {"path": ".github/workflows/anything.yml"}
    reading = upgrade.dispatch_from_a_branch(run)
    assert reading["read"] is False and "not /platform-check.yml" in reading["reasons"][0]


def test_the_dispatch_recorded_on_2026_10_02_reads_as_refused():
    assert upgrade.dispatch_from_a_branch(recorded_dispatch()) == {"read": True, "held": True, "reasons": []}


def test_a_post_job_that_ran_from_a_branch_reached_the_key():
    run = recorded_dispatch()
    run["jobs"][-1] |= {"conclusion": "success", "steps": 7, "runner_name": "GitHub Actions 3"}
    reading = upgrade.dispatch_from_a_branch(run)
    assert reading["held"] is False and "the App's key was reached from a branch" in reading["reasons"][0]
    run["jobs"][-1] |= {"conclusion": "failure"}  # it started, and failed later: the key was still read
    assert upgrade.dispatch_from_a_branch(run)["held"] is False


@pytest.mark.parametrize("change", [
    {"found": False}, {"event": "schedule"}, {"head_branch": "main"},
    {"jobs": [{"name": "find", "conclusion": "success", "steps": 8, "runner_name": "r"}]},  # find listed no head
    {"jobs": [{"name": "evaluate (x)", "conclusion": "success", "steps": 9, "runner_name": "r"},
              {"name": "post", "conclusion": "skipped", "steps": 0, "runner_name": ""}]},
])  # fmt: skip
def test_a_skip_or_a_run_that_never_asked_for_the_key_is_not_a_refusal(change):
    reading = upgrade.dispatch_from_a_branch({**recorded_dispatch(), **change})
    assert reading["read"] is False and reading["held"] is None


def relaxed(**more: Any) -> dict[str, Any]:
    base = {"repository": "agentkeel-studio/owner-check", "run": 5, "found": True, "error": None, "answer": {"status": 200},
            "new_head": {"sha": "5" * 40, "check_runs": [app_check("failure", [upgrade.RULESET_CHECK])]},
            "merges_between": [], "passed_after_restore": True}  # fmt: skip
    return {**base, **more}


def test_a_relaxation_is_refused_or_detected_and_says_which():
    assert upgrade.relaxation(relaxed(answer={"status": 403}), APP)["outcome"] == "refused"
    detected = upgrade.relaxation(relaxed(), APP)
    assert detected["held"] is True and detected["outcome"] == "detected"
    for change, said in (({"new_head": {"check_runs": [app_check("success")]}}, "did not fail the new head"),
                         ({"new_head": {"check_runs": [app_check("failure", [upgrade.SEAT_CHECK])]}}, "did not fail the new head"),
                         ({"merges_between": [4]}, "merged while the ruleset differed: 4"),
                         ({"passed_after_restore": False}, "passed no head")):  # fmt: skip
        reading = upgrade.relaxation(relaxed(**change), APP)
        assert reading["held"] is False and reading["outcome"] == "undetected" and said in reading["reasons"][0], reading
    for unread in (None, relaxed(found=False), relaxed(answer=None), relaxed(merges_between=None),
                   relaxed(new_head={"check_runs": []}), relaxed(passed_after_restore=None)):  # fmt: skip
        assert upgrade.relaxation(unread, APP)["read"] is False, unread


def test_the_timed_runs_agent_exists_whether_or_not_it_was_under_its_bar():
    assert upgrade.timed_run({"F6_3": {"read": True, "held": False, "listed": True}})["held"] is True
    assert upgrade.timed_run({"F6_3": {"read": False, "held": None, "listed": False}})["read"] is False
    assert upgrade.timed_run(None)["read"] is False


# --- the envelope's `upgrade` ----------------------------------------------------------


def observation(**more: Any) -> dict[str, Any]:
    return {"looked_up_at": NOW, "parts": [], "viewpoint": "anonymous",
            "apps": {"platform": APP, "upgrades": 5200001, "observer": 5200002},
            "s0": {"owner_test": None, "dispatch": None, "relaxation": None}, "s1": None, "s2": None, "s3": None,
            "panel2": None, "surfaces": {"results": {plant: True for plant in plants.SURFACE_PLANTS}}, **more}  # fmt: skip


def test_before_any_attempt_every_live_reading_is_unread_and_none_is_taken():
    """PR 2's own run, as SPEC/07 section 7 states it: every live reading unread, the surfaces 2 of 2, taken 0 of 3."""
    reading = upgrade.record(observation(), THRESHOLDS, HISTORY)
    for name in ("F7_0", "F7_1", "F7_2", "F7_3", "F7_4"):
        assert reading[name]["read"] is False and reading[name]["held"] is None, name
        assert all(reason.split(": ")[-2].endswith("unread") or "unread:" in reason for reason in reading[name]["reasons"]), reading[name]
    assert reading["F7_5"]["read"] is True and reading["F7_5"]["held"] is True
    assert reading["surfaces"] == {"plants_expected": 2, "plants_fired": 2, "silent": []}
    assert reading["taken"] == {"n": 0, "of": 3, "platform": None, "model": None, "retirement": None}
    assert reading["bars"] == BARS and reading["app_observation"] is None
    assert [u["kind"] for u in reading["F7_1"]["upgrades"]] == ["platform", "model", "retirement"]
    assert reading["F7_0"]["parts"] == {name: {"read": False, "held": None} for name in ("owner_test", "dispatch", "relaxation", "timed_run")}


def test_the_dispatch_already_made_is_read_and_the_rest_of_f7_0_is_still_unread():
    reading = upgrade.record(observation(s0={"owner_test": None, "dispatch": recorded_dispatch(), "relaxation": None}),
                             THRESHOLDS, HISTORY)  # fmt: skip
    assert reading["F7_0"]["parts"]["dispatch"] == {"read": True, "held": True}
    assert reading["F7_0"]["read"] is False and reading["F7_0"]["held"] is None and reading["F7_0"]["viewpoint"] == "anonymous"


def full() -> dict[str, Any]:
    """Every attempt made and held: what PR 4's run would hand build if nothing missed."""
    retirement = fixture("s2-retired-agent/observation_held.json")
    rollback = fixture("s3-rollback/observation_held.json")
    swap = pull(repository="andaro74/agentkeel", pull_request=41, files=["agents/refagent/manifest.yaml"],
                commits=[{"sha": "6" * 40, "author": BOT, "files": ["agents/refagent/manifest.yaml"]}],
                required_on_head={"evals": "success"})  # fmt: skip
    retire = pull(pull_request=5, files=["manifest.yaml"], commits=[{"sha": "7" * 40, "author": BOT, "files": ["manifest.yaml"]}],
                  merged_at="2026-10-05T09:50:00Z", created_at="2026-10-05T09:20:00Z", trigger={"at": "2026-10-05T09:00:00Z"})  # fmt: skip
    return observation(
        s0={"owner_test": owner(), "dispatch": recorded_dispatch(), "relaxation": relaxed(answer={"status": 403})},
        s1={"pulls": [pull()], "lives": {"agentkeel-studio/owner-check": live()}},
        s2={"pull": retire, "retirement": retirement},
        s3={"swap": swap, "swap_live": live(), "rollback": rollback},
        panel2={"error": None, "frame": fixture("s4-panel2/frame.json") | {"results": {"A": {"frames": [
            frame({"245eb9baf796cd9ceed652abe3805825208358c9": "GREEN"})["results"]["A"]["frames"][0]]}}}},
    )  # fmt: skip


TEMPLATE = {"F6_3": {"read": True, "held": True, "listed": True}}


def test_three_of_three_only_when_every_upgrade_arrived_merged_and_went_live():
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    assert all(reading[name]["read"] and reading[name]["held"] for name in ("F7_0", "F7_1", "F7_2", "F7_3", "F7_4", "F7_5")), reading
    assert reading["taken"] == {"n": 3, "of": 3, "platform": True, "model": True, "retirement": True}
    assert reading["F7_0"]["relaxation"] == "refused" and reading["F7_3"]["on"] == "refagent"


@pytest.mark.parametrize("path, value, kind", [
    (("s1", "pulls", 0, "author"), PERSON, "platform"),  # a person opened it
    (("s1", "pulls", 0, "merged"), False, "platform"),  # arrived, never merged
    (("s1", "lives", "agentkeel-studio/owner-check", "runtime"), {"image_tags": ["b" * 64]}, "platform"),  # merged, not live
    (("s3", "swap", "commits", 0, "author"), PERSON, "model"),
    (("s3", "swap_live", "deploy"), {"conclusion": "failure", "completed_at": "2026-10-06T10:30:00Z"}, "model"),
    (("s2", "retirement", "invocation"), {"answered": True, "error": None, "at": "2026-10-05T10:01:00Z"}, "retirement"),
])  # fmt: skip
def test_an_upgrade_that_missed_is_not_taken(path, value, kind):
    seen: Any = full()
    target = seen
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    reading = upgrade.record(seen, THRESHOLDS, HISTORY, template=TEMPLATE)
    # Not taken: False where a miss was read, None where the pull request has not merged (unread).
    assert reading["taken"][kind] is (None if path[-1] == "merged" else False) and reading["taken"]["n"] == 2, reading["taken"]


def test_the_apps_stored_reading_is_ruled_on_where_it_found_the_record_and_says_so():
    """The run's own token has no rights in the organisation; main's observer read as the App (SPEC/07 §4)."""
    own = full()
    stored = {"run_id": "777", "read_at": "2026-10-06T11:45:00Z", "key": "observations/777.json",
              "upgrade": {"s0": {"owner_test": {k: v for k, v in owner().items() if k not in ("answer", "deploy", "registry_row", "on_panel")}}}}  # fmt: skip
    # The App saw the last faulty head refused on the ruleset too; the anonymous reading did not say so.
    stored["upgrade"]["s0"]["owner_test"]["commits"] = copy.deepcopy(own["s0"]["owner_test"]["commits"])
    stored["upgrade"]["s0"]["owner_test"]["commits"][1]["check_runs"][0]["refused"].append(upgrade.RULESET_CHECK)
    reading = upgrade.record(own, THRESHOLDS, HISTORY, template=TEMPLATE, app=stored)
    assert reading["F7_0"]["viewpoint"] == "anonymous and app" and reading["F7_0"]["held"] is False
    assert reading["app_observation"] == {"run_id": "777", "read_at": "2026-10-06T11:45:00Z", "key": "observations/777.json"}
    assert reading["F7_1"]["viewpoint"] == "anonymous"  # nothing of F7.1's was in the stored observation
    # AWS's records stay the run's own: the App's record carries no answer, and the deploy is still read.
    assert reading["F7_0"]["reasons"] == ["owner_test: the new head 222222222222 was not refused on the seats and the goldens "
                                          f"and nothing else: {upgrade.RULESET_CHECK}"]  # fmt: skip
    # A stored record the App did not find is not preferred.
    stored["upgrade"]["s0"]["owner_test"]["found"] = False
    assert upgrade.record(own, THRESHOLDS, HISTORY, template=TEMPLATE, app=stored)["F7_0"]["viewpoint"] == "anonymous"


@pytest.mark.parametrize("thresholds", [{}, {"upgrade": {"arrive_max_seconds": 4500}},
                                        {"upgrade": {"arrive_max_seconds": 4500, "deploy_max_seconds": True, "retire_max_seconds": 0}}])  # fmt: skip
def test_a_missing_bar_is_refused_not_read_as_no_bar(thresholds):
    with pytest.raises(Unreadable, match="thresholds.yaml upgrade must give"):
        upgrade.record(observation(), thresholds, HISTORY)
    with pytest.raises(Unreadable, match="no looked_up_at"):
        upgrade.record({}, THRESHOLDS, HISTORY)


# --- after the cold review of M07 PR 2: readings that came out held with a record missing ----------


@pytest.mark.parametrize("status, read, outcome", [
    (403, True, "refused"),
    (404, False, None),  # a ruleset GitHub could not find
    (422, False, None),  # a body GitHub would not parse
    (500, False, None),  # an error of GitHub's own
])  # fmt: skip
def test_only_githubs_refusal_of_the_token_reads_as_refused(status, read, outcome):
    """Cold review F2: any status of 400 or more read `held True, outcome refused`."""
    reading = upgrade.relaxation({"found": True, "answer": {"status": status}}, 5144253)
    assert (reading["read"], reading["outcome"]) == (read, outcome) and reading["held"] is (True if read else None)


def test_a_retirement_with_no_listing_of_answer_records_or_no_time_on_its_invocation_is_unread():
    """Cold review F3: both read as nothing after the deletion, and the retirement came out held."""
    held = json.loads((ROOT / "tests/fixtures/m07/s2-retired-agent/observation_held.json").read_text(encoding="utf-8"))
    assert upgrade.f7_2(held, 3600.0)["held"] is True
    for change in ({"answer_records": None}, {"invocation": {**held["invocation"], "at": None}}):
        reading = upgrade.f7_2({**held, **change}, 3600.0)
        assert reading["read"] is False and reading["held"] is None, reading


def test_a_pull_request_that_has_not_merged_is_unread_unless_a_miss_is_already_there():
    """Cold review F3: an open pull request with nothing wrong so far read `held True` for "needed to merge it"."""
    seen = full()
    pull = seen["s1"]["pulls"][0] | {"merged": False}
    opener = {"id": seen["apps"]["upgrades"], "slug": "agentkeel-upgrades"}
    bars = upgrade.bars_of(THRESHOLDS)
    reading = upgrade.pull_reading("platform", pull, opener, bars, seen["looked_up_at"])
    assert (reading["read"], reading["held"], reading["merged"]) == (False, None, False)
    assert reading["arrived_s"] is not None  # what was read stays read
    edited = pull | {"files": [*pull["files"], ".github/workflows/own.yml"]}
    reading = upgrade.pull_reading("platform", edited, opener, bars, seen["looked_up_at"])
    assert (reading["read"], reading["held"]) == (True, False) and "touches a workflow" in reading["reasons"][0]


def test_an_owner_test_whose_deploy_run_completed_before_the_merge_matched_the_wrong_run():
    seen = full()
    test = seen["s0"]["owner_test"]
    test["deploy"] = {**test["deploy"], "completed_at": "2020-01-01T00:00:00Z"}
    reading = upgrade.owner_test(test, seen["apps"]["platform"], upgrade.bars_of(THRESHOLDS), seen["looked_up_at"])
    assert reading["held"] is False and any("the wrong run was matched" in r for r in reading["reasons"])


def test_the_apps_stored_reading_is_not_laid_over_a_record_the_run_read_later():
    """Cold review F4: a person's commit pushed after the observer's last run was hidden by a reading that said `app`."""
    own = {"found": True, "commits": [{"sha": "1"}, {"sha": "2"}], "merged": True}
    stale = {"found": True, "commits": [{"sha": "1"}], "merged": False}
    assert upgrade._prefer(own, stale) == (own, "anonymous")
    current = {"found": True, "commits": [{"sha": "1"}, {"sha": "2"}], "merged": True, "seen_only_by_the_app": 1}
    found, viewpoint = upgrade._prefer(own, current)
    assert viewpoint == "app" and found["seen_only_by_the_app"] == 1


def test_cis_own_envelope_commit_reads_as_a_persons_edit_as_the_spec_defines_one():
    """Cold review F1 on M07 PR 2, stated and not repaired: SPEC/07 section 2 calls any commit on an upgrade
    pull request that is not the App's, and touches anything but a ruling file, a person's edit. CI pushes
    `evals/history/<commit>.json` to every agentkeel pull request as `github-actions[bot]`. So the model
    upgrade cannot read as held, and `taken` is at most 2 of 3, until Product amends the definition. This
    test holds the reader to the definition as written; it changes when the definition does."""
    seen = full()
    swap = seen["s3"]["swap"]
    envelope = f"evals/history/{'a' * 40}.json"
    swap["files"] = [*swap["files"], envelope]
    swap["commits"] = [*swap["commits"], {"sha": "3" * 40, "author": {"login": "github-actions[bot]", "type": "Bot",
                                                                    "app_id": None, "app_slug": None}, "files": [envelope]}]  # fmt: skip
    reading = upgrade.record(seen, THRESHOLDS, HISTORY, template=TEMPLATE)
    said = " ".join(reading["F7_1"]["reasons"])
    assert reading["taken"]["model"] is False and reading["taken"]["n"] == 2
    assert "which a model upgrade does not" in said and "a person's edit" in said and "github-actions[bot]" in said


def test_each_upgrades_deploy_seconds_are_kept_beside_it():
    """threshold-owner F6: the deploy's seconds were worked out and only `taken` was kept."""
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    kept = {u["kind"]: u["deployed_s"] for u in reading["F7_1"]["upgrades"]}
    assert kept["retirement"] is None and kept["platform"] is not None and kept["model"] is not None
