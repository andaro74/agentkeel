"""scripts/observe_pr.py's pure parts and build's three M02 readers (SPEC/02 §4).

Nothing here calls GitHub. The instrument's API calls are rehearsed once
against a known record at M02 PR 2 (`milestones/M02/runs/rehearsal_*.json`,
open.md row 17); what is held here is what it makes of a log, what it
reads from a merge commit with git, and what `build` makes of each
observation shape.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts import observe_pr
from src.verdict import build

URL = "https://github.com/andaro74/agentkeel/actions/runs/1"

LOG = """\
2026-09-22T20:00:00.0000000Z ruling-cited: 2 uncovered path(s) in the diff (CODEOWNERS read from the base 1234abcd):
2026-09-22T20:00:00.0000000Z   uncovered evals/goldens/v1/g-010.yaml: owned by Data Owner; no ruling file with pr: 13 and seat: Data Owner authorises it
2026-09-22T20:00:00.0000000Z   uncovered evals/goldens/v1/g-099.yaml: owned by Data Owner; no ruling file with pr: 13 and seat: Data Owner authorises it
2026-09-22T20:00:01.0000000Z FAIL golden ids against origin/main
2026-09-22T20:00:01.0000000Z      evals/goldens/v1/g-005.yaml: g-005 is on origin/main and not in this tree, and its retired is null: an id is retired (retired: MNN), never renamed or deleted (R11)
"""


def test_lines_naming_the_seeds_path_are_found_and_others_are_not():
    assert len(observe_pr.lines_naming(LOG, "evals/goldens/v1/g-010.yaml", "ruling-cited")) == 1
    assert observe_pr.lines_naming(LOG, "evals/goldens/v1/g-011.yaml", "ruling-cited") == []
    assert observe_pr.lines_naming(LOG, "evals/goldens/v1/g-010.yaml", "checks") == []  # validate's FAIL lines only
    found = observe_pr.lines_naming(LOG, "evals/goldens/v1/g-005.yaml", "checks")
    assert len(found) == 1 and "retired is null" in found[0]


def test_rulings_in_a_merge_commit_are_read_with_git():
    """M02 PR 1 (#11) merged as c77e872 with three ruling files carrying pr: 11 and three seats."""
    found = observe_pr.rulings_in("c77e87270e6152ab0a8536b86642406449ebd78e", 11)
    assert {r["path"] for r in found} >= {"milestones/M02/rulings/pr1.md", "milestones/M02/rulings/pr1-security.md",
                                          "milestones/M02/rulings/pr1-engineering.md"}  # fmt: skip
    assert {r["seat"] for r in found} >= {"Product", "Security", "Engineering"}
    assert observe_pr.rulings_in("c77e87270e6152ab0a8536b86642406449ebd78e", 999) == []


# --- build's readers ----------------------------------------------------------------


def seed(**over) -> dict:
    return {"seed": "S1 one key", "pr": 13, "found": True, "merged": False, "state": "open",
            "check_run": {"conclusion": "failure"}, "required_on_base": True, "path_named_in_log": True} | over  # fmt: skip


def write(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "obs.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def test_seed_prs_pass_only_when_every_seed_was_refused_naming_its_path(tmp_path):
    assert build.check_from_seed_prs(write(tmp_path, {"seeds": [seed(), seed(seed="S2")]}), URL)["status"] == "pass"
    for over in ({"merged": True}, {"check_run": {"conclusion": "success"}}, {"check_run": None}, {"required_on_base": False},
                 {"path_named_in_log": False}, {"found": False}):  # fmt: skip
        assert build.check_from_seed_prs(write(tmp_path, {"seeds": [seed(), seed(**over)]}), URL)["status"] == "fail", over
    assert build.check_from_seed_prs(write(tmp_path, {"seeds": [], "note": "not opened"}), URL)["status"] == "fail"


def bypass(**over) -> dict:
    doc = {
        "attempt_1": {"found": True, "merged": False, "rule_suite_fail_found": False, "human_message_contains": True},
        "attempt_2": {"human_said": {"validate_result": "RED"}, "live_now": {"bypass_actors": []}},
    }
    for key, value in over.items():
        doc[key] = value
    return doc


def test_bypass_passes_on_the_api_record_or_the_humans_output_and_fails_without_either(tmp_path):
    assert build.check_from_bypass(write(tmp_path, bypass()), URL)["status"] == "pass"
    api = bypass(attempt_1={"found": True, "merged": False, "rule_suite_fail_found": True, "human_message_contains": False})
    assert build.check_from_bypass(write(tmp_path, api), URL)["status"] == "pass"
    neither = bypass(attempt_1={"found": True, "merged": False, "rule_suite_fail_found": False, "human_message_contains": False})
    assert build.check_from_bypass(write(tmp_path, neither), URL)["status"] == "fail"
    merged = bypass(attempt_1={"found": True, "merged": True, "rule_suite_fail_found": True, "human_message_contains": True})
    assert build.check_from_bypass(write(tmp_path, merged), URL)["status"] == "fail"
    listed = bypass(attempt_2={"human_said": {"validate_result": "RED"}, "live_now": {"bypass_actors": [{"actor_id": 1}]}})
    assert build.check_from_bypass(write(tmp_path, listed), URL)["status"] == "fail"
    green = bypass(attempt_2={"human_said": {"validate_result": "GREEN"}, "live_now": {"bypass_actors": []}})
    assert build.check_from_bypass(write(tmp_path, green), URL)["status"] == "fail"
    assert build.check_from_bypass(write(tmp_path, {"note": "not made"}), URL)["status"] == "fail"


def doors() -> dict:
    return {"doors": [
        {"door": 1, "found": True, "merged": False, "two_key": {"conclusion": "failure"}, "path_named_in_log": True},
        {"door": 2, "found": True, "merged": True, "two_key": {"conclusion": "success"}, "distinct_seats": ["Data Owner", "Threshold Owner"], "relaxation_keyed": True},
        {"door": 3, "found": True, "merged": False, "bypass": bypass()},
    ]}  # fmt: skip


def test_doors_pass_only_when_all_three_are_in_the_record(tmp_path):
    assert build.check_from_doors(write(tmp_path, doors()), URL)["status"] == "pass"
    broken = doors()
    broken["doors"][1]["distinct_seats"] = ["Data Owner"]
    assert build.check_from_doors(write(tmp_path, broken), URL)["status"] == "fail"
    broken = doors()
    broken["doors"][1]["relaxation_keyed"] = False  # two files, nothing relaxed: not Door 2 (cold review, F2)
    assert build.check_from_doors(write(tmp_path, broken), URL)["status"] == "fail"
    broken = doors()
    broken["doors"][0]["two_key"] = {"conclusion": "success"}
    assert build.check_from_doors(write(tmp_path, broken), URL)["status"] == "fail"
    broken = doors()
    broken["doors"][2]["merged"] = True
    assert build.check_from_doors(write(tmp_path, broken), URL)["status"] == "fail"
    assert build.check_from_doors(write(tmp_path, {"doors": [], "note": "not filled"}), URL)["status"] == "fail"


def test_every_reader_needs_the_run_url(tmp_path):
    for reader in (build.check_from_seed_prs, build.check_from_bypass, build.check_from_doors):
        with pytest.raises(build.Refused):
            reader(write(tmp_path, {}), None)


def test_the_second_source_joins_the_first_through_both(tmp_path):
    first = {"F2_1": {"status": "pass", "url": URL}}
    joined = build.both(first, "F2_1", build.check_from_seed_prs(write(tmp_path, {"seeds": []}), URL))
    assert joined["F2_1"]["status"] == "fail"


def test_the_login_is_read_from_the_seeds_own_principal_line():
    """The committed f2_1_bypass.yaml line; the first draft raised IndexError on it (cold review of PR 2, F1)."""
    assert observe_pr.login_in("the repository owner, andaro74, with admin on andaro74/agentkeel") == "andaro74"
    assert observe_pr.login_in("") == ""


def test_observe_bypass_on_the_seed_before_the_attempts_writes_a_note_and_calls_nothing(tmp_path, monkeypatch):
    """The seed as planted (`observed: null`), on a copy: the committed file was filled by the human on
    2026-09-23, and a test that read it asserted the state it had at PR 2 (the branch's run 35874322479)."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "andaro74/agentkeel")
    monkeypatch.setenv("GITHUB_API_URL", "http://127.0.0.1:9")  # a call would fail loudly, not silently pass
    seed = yaml.safe_load((observe_pr.ROOT / "milestones" / "M02" / "runs" / "f2_1_bypass.yaml").read_text(encoding="utf-8"))
    planted = tmp_path / "f2_1_bypass.yaml"
    planted.write_text(yaml.safe_dump({**seed, "observed": None}), encoding="utf-8")
    out = tmp_path / "bypass.json"
    assert observe_pr.main([str(planted), "--out", str(out)]) == 0
    seen = json.loads(out.read_text(encoding="utf-8"))
    assert seen["kind"] == "bypass" and seen["attempt_1"] is None and "not been made" in seen["note"]


# --- the files evals.yml fetches with RULESET_TOKEN (M02 PR 3) ---------------------------


SUITE = {"id": 4192991324, "actor_name": "andaro74", "before_sha": "97d3c76", "after_sha": "1995389", "ref": "refs/heads/main",
         "pushed_at": "2026-09-23T06:34:13-07:00", "result": "fail",
         "rule_evaluations": [{"rule_type": "required_status_checks", "result": "fail"}, {"rule_type": "pull_request", "result": "pass"}]}  # fmt: skip


def suites_dir(tmp_path: Path, listed: list, by_id: dict | None) -> Path:
    folder = tmp_path / "rule-suites"
    folder.mkdir(parents=True)
    (folder / "list.json").write_text(json.dumps(listed), encoding="utf-8")
    if by_id is not None:
        (folder / f"{by_id['id']}.json").write_text(json.dumps(by_id), encoding="utf-8")
    return folder


def test_rule_suites_are_read_from_the_directory_the_workflow_filled_and_not_the_api(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(suites_dir(tmp_path, [SUITE], SUITE)))
    at = observe_pr.parse_time("2026-09-23T13:34:13Z")
    seen = observe_pr.rule_suites("andaro74/agentkeel", "andaro74", at, None, recorded_id=4192991324)
    assert seen["source"] == "file" and seen["readable"] is True
    assert [s["id"] for s in seen["failed_evaluations"]] == [4192991324]
    assert seen["recorded"]["is_the_actors_refusal"] is True
    assert seen["recorded"]["refusing_rules"] == ["required_status_checks"]
    # the recorded suite must be within WINDOW of the attempt: another failed push by the owner is not this refusal (F3)
    early = {**SUITE, "pushed_at": "2025-09-23T06:34:13-07:00"}
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(suites_dir(tmp_path / "early", [], early)))
    seen = observe_pr.rule_suites("andaro74/agentkeel", "andaro74", at, None, recorded_id=4192991324)
    assert seen["recorded"]["within_window_of_attempt"] is False and seen["recorded"]["is_the_actors_refusal"] is False
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(suites_dir(tmp_path / "again", [SUITE], SUITE)))
    # another actor's suite, or the recorded one for another actor, is not this actor's refusal
    seen = observe_pr.rule_suites("andaro74/agentkeel", "someone-else", at, None, recorded_id=4192991324)
    assert seen["failed_evaluations"] == [] and seen["recorded"]["is_the_actors_refusal"] is False
    # the list aged out but the recorded id is still there: the by-id read carries it
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(suites_dir(tmp_path / "later", [], SUITE)))
    seen = observe_pr.rule_suites("andaro74/agentkeel", "andaro74", at, None, recorded_id=4192991324)
    assert seen["failed_evaluations"] == [] and seen["recorded"]["is_the_actors_refusal"] is True
    # a directory that is set and empty is unreadable, never the API
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(tmp_path / "missing"))
    seen = observe_pr.rule_suites("andaro74/agentkeel", "andaro74", at, None, recorded_id=4192991324)
    assert seen["readable"] is False and seen["failed_evaluations"] == [] and seen["recorded"]["readable"] is False


def test_the_live_ruleset_is_read_from_the_file_validate_reads(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "http://127.0.0.1:9")
    live = tmp_path / "live-ruleset.json"
    live.write_text(json.dumps({"id": 23685206, "bypass_actors": [], "updated_at": "2026-09-23T06:45:29.044-07:00"}), encoding="utf-8")
    monkeypatch.setenv("AGENTKEEL_LIVE_RULESET", str(live))
    seen = observe_pr.live_ruleset("andaro74/agentkeel", 23685206, None)
    assert seen == {"source": "file", "status": 200, "readable": True, "bypass_actors": [],
                    "updated_at": "2026-09-23T06:45:29.044-07:00", "shown_bypass_actors": True}  # fmt: skip
    # the file must be the export's ruleset, and an absent list is not an empty one
    live.write_text(json.dumps({"id": 1, "bypass_actors": []}), encoding="utf-8")
    assert observe_pr.live_ruleset("andaro74/agentkeel", 23685206, None)["readable"] is False
    live.write_text(json.dumps({"id": 23685206}), encoding="utf-8")
    seen = observe_pr.live_ruleset("andaro74/agentkeel", 23685206, None)
    assert seen["readable"] is True and seen["bypass_actors"] is None and seen["shown_bypass_actors"] is False
    monkeypatch.setenv("AGENTKEEL_LIVE_RULESET", str(tmp_path / "missing.json"))
    assert observe_pr.live_ruleset("andaro74/agentkeel", 23685206, None)["readable"] is False


def test_attempt_1_is_witnessed_by_the_recorded_suite_when_the_list_is_empty(tmp_path, monkeypatch):
    """`rule_suite_fail_found` reads the by-id record too; build then names the API as the witness."""
    monkeypatch.setenv("GITHUB_API_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("AGENTKEEL_RULE_SUITES", str(suites_dir(tmp_path, [], SUITE)))
    monkeypatch.setattr(observe_pr, "pull", lambda repo, number, token: {"pr": number, "found": True, "merged": False})
    run = {"principal": "the repository owner, andaro74, with admin on andaro74/agentkeel",
           "attempts": [{"message_must_contain": "required status check"}],
           "observed": [{"pr": 14, "at": "2026-09-23T13:34:13Z", "rule_suite": 4192991324, "message": "3 of 5 required status checks are failing."}]}  # fmt: skip
    seen = observe_pr.observe_bypass("andaro74/agentkeel", run, None, None)
    assert seen["attempt_1"]["rule_suite_fail_found"] is True and seen["attempt_1"]["witness"] == "the rule-suites API"
    run["observed"][0]["at"] = "2026-10-30T13:34:13Z"  # the same suite, a month after the attempt: not its witness
    seen = observe_pr.observe_bypass("andaro74/agentkeel", run, None, None)
    assert seen["attempt_1"]["rule_suite_fail_found"] is False
