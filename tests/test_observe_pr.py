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
        {"door": 2, "found": True, "merged": True, "two_key": {"conclusion": "success"}, "distinct_seats": ["Data Owner", "Threshold Owner"]},
        {"door": 3, "found": True, "merged": False, "bypass": bypass()},
    ]}  # fmt: skip


def test_doors_pass_only_when_all_three_are_in_the_record(tmp_path):
    assert build.check_from_doors(write(tmp_path, doors()), URL)["status"] == "pass"
    broken = doors()
    broken["doors"][1]["distinct_seats"] = ["Data Owner"]
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
