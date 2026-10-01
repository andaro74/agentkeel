"""M06 PR 2's readers beyond the seed tests (SPEC/06 §4, §6).

The seed tests (`test_m06_seeds.py`) say each planted fault is refused for its
planted reason. These say what the readers do with what was not planted: the
seat lookup's answers, and build's rulings on the observer's raw lists for
claim 6's live falsifiers, with row 6's reading of them (P5: the gate holds
the elapsed time again to the bar at the envelope's commit).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.validate import seats
from src.verdict import build, gate, schema_errors
from src.verdict import template as shipped

APP = 1234567  # the platform App's id, as the observer reads it from the configuration
FIXTURES = Path(__file__).parent / "fixtures" / "m06"

# --- the seat lookup -----------------------------------------------------------


@pytest.fixture
def api(monkeypatch):
    """A stand-in for GitHub's API: path -> (status, body). Clears the lookup's cache around each test."""
    answers: dict[str, tuple[int, Any]] = {}
    monkeypatch.setattr(seats, "_get", lambda path: (*answers.get(path, (404, None)), "a test token"))
    monkeypatch.setenv("AGENTKEEL_SEAT_REPOSITORY", "org/agent")
    seats.login_has_access.cache_clear()
    yield answers
    seats.login_has_access.cache_clear()


def test_the_repositorys_owner_has_access(api):
    api["/repos/org/agent"] = (200, {"owner": {"login": "Org"}})
    assert seats.login_has_access("org") == (True, "owner of org/agent")


def test_a_collaborator_has_access_and_a_stranger_does_not(api):
    api["/repos/org/agent"] = (200, {"owner": {"login": "org"}})
    api["/repos/org/agent/collaborators/andaro74"] = (204, None)
    assert seats.login_has_access("andaro74")[0] is True
    real, status = seats.login_has_access("someone-else")
    assert real is False and "not a collaborator" in status


def test_access_that_cannot_be_read_is_not_access(api):
    """A 403 on the collaborators endpoint (a token without push) refuses the seat; it is not a skip."""
    api["/repos/org/agent"] = (200, {"owner": {"login": "org"}})
    api["/repos/org/agent/collaborators/andaro74"] = (403, None)
    real, status = seats.login_has_access("andaro74")
    assert real is False and "access is unread" in status


def test_an_assigned_seat_the_lookup_refuses_names_the_seat(tmp_path):
    agent = tmp_path / "agents" / "premiere-desk"
    agent.mkdir(parents=True)
    manifest = (FIXTURES / "s1b-no-goldens" / "manifest.yaml").read_text(encoding="utf-8")
    (agent / "manifest.yaml").write_text(manifest, encoding="utf-8")
    errors = seats.check(tmp_path, lookup=lambda login: (False, "404"))
    assert len(errors) == 7 and all("not a login with access (404)" in e for e in errors)


# --- claim 6's live readings ---------------------------------------------------

SEATED = {slug: "andaro74" for slug in shipped.SEAT_SLUGS}
TWO = [{"file": "g-001.yaml", "kind": "ordinary", "retired": None}, {"file": "g-002.yaml", "kind": "trap", "retired": None}]


def runs(conclusion: str | None, stand_in: bool = False) -> list[dict[str, Any]]:
    out = [] if conclusion is None else [{"name": shipped.PLATFORM_CHECK, "app_id": APP, "app_slug": "agentkeel-platform",
                                           "conclusion": conclusion}]  # fmt: skip
    if stand_in:
        out.append({"name": shipped.PLATFORM_CHECK, "app_id": 15368, "app_slug": "github-actions", "conclusion": "success"})
    return out


def observation() -> dict[str, Any]:
    """Every record read and every control held: S2 refused, S3 inside the bar, panel 1 equal to the registry."""
    return {
        "looked_up_at": "2026-10-02T12:00:00Z",
        "platform_app_id": APP,
        "s2": {"repository": "org/premiere-desk", "pull_request": 3, "found": True, "error": None, "merged": False,
               "head_sha": "c" * 40, "check_runs": runs("failure", stand_in=True)},  # fmt: skip
        "s3": {
            "repository": "org/premiere-desk", "pull_request": 1, "agent_name": "premiere-desk",
            "found": True, "error": None, "created_at": "2026-10-01T09:00:00Z",
            "first_pr": {
                "merged": True, "merged_at": "2026-10-01T11:00:00Z", "merge_head_sha": "b" * 40,
                "commits": [
                    {"sha": "a" * 40, "seats": {s: None for s in shipped.SEAT_SLUGS}, "goldens": [], "check_runs": runs("failure")},
                    {"sha": "b" * 40, "seats": SEATED, "goldens": TWO, "check_runs": runs("success")},
                ],
            },
            "deploy": {"run_id": 1, "conclusion": "success", "completed_at": "2026-10-01T11:30:00Z", "agent_commit": "d" * 40},
            "answer": {"key": "envelopes/agents/premiere-desk/" + "d" * 40 + ".json", "sha256": "e" * 64,
                       "last_modified": "2026-10-01T11:31:00Z", "goldens": {"g-001": {"kind": "ordinary", "pass": True}}},
            "registry_row": {"name": "premiere-desk", "repository": "org/premiere-desk", "commit_sha": "d" * 40,
                             "deployed_at": "2026-10-01T11:29:00Z"},
        },  # fmt: skip
        "panel": {"read_at": "2026-10-02T12:00:00Z", "error": None, "frame": {"results": {"A": {"frames": [
            {"schema": {"fields": [{"name": "name"}, {"name": "repository"}]},
             "data": {"values": [["premiere-desk", "refagent"], ["org/premiere-desk", "andaro74/agentkeel"]]}}]}}}},
        "registry": {"read_at": "2026-10-02T12:00:00Z", "error": None,
                     "scan": {"Items": [{"name": {"S": "refagent"}}, {"name": {"S": "premiere-desk"}}]}},
    }  # fmt: skip


def ruled(obs: dict[str, Any], bar: float = 28800.0) -> dict[str, Any]:
    return {"template": shipped.record(obs, bar)}


def test_every_record_read_and_every_control_held_is_no_miss():
    envelope = ruled(observation())
    assert gate.template_misses(envelope, 28800.0, "here") == []
    assert envelope["template"]["F6_3"]["elapsed_s"] == 9060.0  # 11:31 less 09:00: the answer is the last record


def mutated(change) -> dict[str, Any]:
    obs = copy.deepcopy(observation())
    change(obs)
    return obs


@pytest.mark.parametrize(("name", "change", "miss"), [
    ("F6_1", lambda o: o["s3"]["first_pr"]["commits"][0].update(check_runs=runs("success")),
     "passed the platform check with seats unassigned"),
    ("F6_1", lambda o: o["s3"]["first_pr"]["commits"].pop(0), "never carried a planted fault"),
    ("F6_1", lambda o: o["s3"]["first_pr"].update(merged=False), "was not merged"),
    ("F6_2", lambda o: o["s2"].update(merged=True), "S2's pull request merged"),
    ("F6_2", lambda o: o["s2"].update(check_runs=runs("success", stand_in=True)), "passed S2's head"),
    ("F6_2", lambda o: o["s2"].update(check_runs=runs("failure")), "not made as planted"),
    ("F6_3", lambda o: o["s3"]["answer"].update(last_modified="2026-10-01T17:01:00Z"), "over quickstart.max_seconds"),
    ("F6_3", lambda o: o["s3"]["registry_row"].update(repository="org/other"), "unread: registered_at"),
    ("F6_3", lambda o: o["s3"]["answer"]["goldens"]["g-001"].update(**{"pass": False}), "unread: answered_at"),
    ("F6_3", lambda o: o["s3"]["deploy"].update(conclusion="failure"), "unread: deployed_at"),
    ("F6_4", lambda o: o["registry"]["scan"]["Items"].pop(), "panel 1 shows premiere-desk"),
    ("F6_4", lambda o: o["panel"].update(error="401 Unauthorized"), "unread: 401 Unauthorized"),
    ("F6_2", lambda o: o.update(s2=None), "unread"),
])  # fmt: skip
def test_row_6_names_each_falsifier_that_is_unread_or_not_held(name, change, miss):
    misses = gate.template_misses(ruled(mutated(change)), 28800.0, "here")
    assert any(m.startswith(name) and miss in m for m in misses), misses


def test_no_platform_app_id_leaves_f6_1_and_f6_2_unread():
    misses = gate.template_misses(ruled(mutated(lambda o: o.update(platform_app_id=None))), 28800.0, "here")
    assert [m.split()[0] for m in misses] == ["F6_1", "F6_2"]


def test_an_envelope_with_no_template_reads_red_for_row_6():
    assert gate.template_misses({}, 28800.0, "here") == ["template not read: the envelope records no live attempt"]


def test_the_bar_is_read_at_the_envelopes_commit_and_build_and_the_gate_can_disagree():
    """P5: build held 9,060 s against the bar it was given; a commit whose bar is lower reads it again."""
    envelope = ruled(observation())
    misses = gate.template_misses(envelope, 3600.0, "at a later commit")
    assert "template was read against 28800.0 s, the commit's bar is 3600 s (at a later commit)" in misses
    assert "F6_3: build held 9060 s, over the commit's bar 3600 s" in misses


def test_build_refuses_a_template_run_with_no_bar(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps(observation()))
    with pytest.raises(build.Refused, match="quickstart.max_seconds"):
        build.template_record(path, {"cost_cap": {"tokens_per_run": 1}})


def test_build_refuses_an_observation_not_in_the_observers_shape(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps({"s3": None}))
    with pytest.raises(build.Refused, match="looked_up_at"):
        build.template_record(path, {"quickstart": {"max_seconds": 28800}})


def test_an_envelope_carrying_template_validates():
    envelope = json.loads((build.ROOT / "evals" / "history" / "827ee8bc014b28f588e9b8f3e1d4a947be885f26.json")
                          .read_text(encoding="utf-8"))  # fmt: skip
    assert schema_errors({**envelope, **ruled(observation())}) == []
    unread = ruled(mutated(lambda o: o.update(s3=None, s2=None, panel=None)))
    assert schema_errors({**envelope, **unread}) == []


def test_row_6s_cell_names_each_falsifier():
    parts = gate.template_reading(ruled(mutated(lambda o: o.update(s2=None))))
    assert parts == ["F6_1 held", "F6_2 unread", "F6_3 held 9060 s", "F6_4 held"]
