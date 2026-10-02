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
    seats.login_holds_seat.cache_clear()
    yield answers
    seats.login_holds_seat.cache_clear()


def test_a_person_who_owns_the_repository_holds_a_seat_and_an_organisation_does_not(api):
    """cold review F1 on PR 2: an agent repository is the organisation's, and the write developer could have
    named the organisation in every seat."""
    api["/repos/org/agent"] = (200, {"owner": {"login": "Org", "type": "Organization"}})
    real, status = seats.login_holds_seat("org")
    assert real is False and "is the organisation that owns org/agent, not a person" in status
    seats.login_holds_seat.cache_clear()
    api["/repos/org/agent"] = (200, {"owner": {"login": "andaro74", "type": "User"}})
    assert seats.login_holds_seat("andaro74") == (True, "owner of org/agent")


def test_an_admin_holds_a_seat_and_a_write_developer_or_a_stranger_does_not(api):
    """security-reviewer F11 on PR 2: the developer has write, so a seat held by write would let them fill
    every seat themselves (R1: the second developer's login holds none)."""
    api["/repos/org/agent"] = (200, {"owner": {"login": "org"}})
    api["/repos/org/agent/collaborators/andaro74/permission"] = (200, {"permission": "admin"})
    api["/repos/org/agent/collaborators/floresinnovations/permission"] = (200, {"permission": "write"})
    assert seats.login_holds_seat("andaro74")[0] is True
    real, status = seats.login_holds_seat("floresinnovations")
    assert real is False and "write on org/agent, not admin" in status
    real, status = seats.login_holds_seat("someone-else")
    assert real is False and "not a collaborator" in status


def test_a_seat_that_cannot_be_read_is_not_held(api):
    """A 403 (a token that may not ask) refuses the seat; it is not a skip."""
    api["/repos/org/agent"] = (200, {"owner": {"login": "org"}})
    api["/repos/org/agent/collaborators/andaro74/permission"] = (403, None)
    real, status = seats.login_holds_seat("andaro74")
    assert real is False and "it is unread" in status


@pytest.mark.parametrize("login", ["a/../x", "name?per_page=1", "-lead", "x" * 40, ""])
def test_a_string_that_is_not_a_login_never_reaches_a_url(api, login):
    real, status = seats.login_holds_seat(login)
    assert real is False and "is not a GitHub login" in status


def test_an_assigned_seat_the_lookup_refuses_names_the_seat(tmp_path):
    agent = tmp_path / "agents" / "premiere-desk"
    agent.mkdir(parents=True)
    manifest = (FIXTURES / "s1b-no-goldens" / "manifest.yaml").read_text(encoding="utf-8")
    (agent / "manifest.yaml").write_text(manifest, encoding="utf-8")
    errors = seats.check(tmp_path, lookup=lambda login: (False, "404"))
    assert len(errors) == 7 and all("not a login that administers the repository (404)" in e for e in errors)


# --- claim 6's live readings ---------------------------------------------------

SEATED = {slug: "andaro74" for slug in shipped.SEAT_SLUGS}
TWO = [{"file": "g-001.yaml", "kind": "ordinary", "retired": None}, {"file": "g-002.yaml", "kind": "trap", "retired": None}]


BOUND = [{"context": "platform-check", "integration_id": APP}]  # the agent repository's live ruleset: platform-check, from the App


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
               "mergeable_state": "blocked", "required_checks": BOUND,
               "head_sha": "c" * 40, "check_runs": runs("failure", stand_in=True)},  # fmt: skip
        "s3": {
            "repository": "org/premiere-desk", "pull_request": 1, "agent_name": "premiere-desk",
            "found": True, "error": None, "created_at": "2026-10-01T09:00:00Z", "required_checks": BOUND,
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
                             "deployed_at": "2026-10-03T08:00:00Z"},  # a later redeploy's: not timed (N8)
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
    ("F6_1", lambda o: o["s3"]["first_pr"]["commits"].pop(0), "first commit carried no planted fault"),
    ("F6_1", lambda o: o["s3"]["first_pr"]["commits"][0].update(check_runs=[]), "it was never refused"),
    ("F6_1", lambda o: o["s3"]["first_pr"].update(merged=False), "was not merged"),
    ("F6_2", lambda o: o["s2"].update(merged=True), "S2's pull request merged"),
    ("F6_2", lambda o: o["s2"].update(check_runs=runs("success", stand_in=True)), "passed S2's head"),
    ("F6_2", lambda o: o["s2"].update(check_runs=runs("failure")), "not made as planted"),
    ("F6_3", lambda o: o["s3"]["answer"].update(last_modified="2026-10-01T17:01:00Z"), "over quickstart.max_seconds"),
    ("F6_3", lambda o: o["s3"]["registry_row"].update(repository="org/other"), "unread: registry row"),
    ("F6_3", lambda o: o["s3"]["answer"]["goldens"]["g-001"].update(**{"pass": False}), "unread: answered_at"),
    ("F6_3", lambda o: o["s3"]["deploy"].update(conclusion="failure"), "unread: deployed_at"),
    ("F6_4", lambda o: o["registry"]["scan"]["Items"].pop(), "panel 1 shows premiere-desk"),
    ("F6_4", lambda o: o["panel"].update(error="401 Unauthorized"), "unread: 401 Unauthorized"),
    # cold review F2: panel 1 not listing S3's agent is an unread record, not a held one
    ("F6_3", lambda o: o["panel"]["frame"]["results"]["A"]["frames"][0]["data"].update(
        values=[["refagent"], ["andaro74/agentkeel"]]), "unread: panel 1's row"),
    # cold review F3: mergeable is not refused, and a refusal by an unbound check is not this control's
    ("F6_2", lambda o: o["s2"].update(mergeable_state="clean"), "mergeable_state is 'clean'"),
    ("F6_2", lambda o: o["s2"].update(mergeable_state="unstable"), "mergeable_state is 'unstable'"),
    ("F6_2", lambda o: o["s2"].update(mergeable_state="unknown"), "unread: S2's mergeable_state is 'unknown'"),
    ("F6_2", lambda o: o["s2"].update(required_checks=[{"context": "platform-check", "integration_id": None}]),
     "does not require platform-check from the platform's App"),
    ("F6_1", lambda o: o["s3"].update(required_checks=None), "does not require platform-check"),
    # cold review F5: a commit that could not be read is unread, not a planted fault
    ("F6_1", lambda o: o["s3"]["first_pr"]["commits"][0].update(read_error="manifest.yaml: 403"), "unread: commits"),
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
    assert parts == ["F6_1 held", "F6_2 unread", "F6_3 held 9060 s", "F6_4 held"], parts


# --- the platform check over an agent repository (src/validate/agent.py) -------

import shutil  # noqa: E402

import yaml  # noqa: E402

from src.validate import agent as platform  # noqa: E402


CODE = ("__init__.py", "agent.py", "server.py", "prompt.txt")


def agent_repo(tmp_path: Path, fixture: str, **manifest: Any) -> Path:
    """An agent repository's root, from a seed fixture with the example agent's code beside it, the platform's
    guardrail, and any change given. The fixtures carry no code: the seeds plant manifests and goldens."""
    root = tmp_path / "repo"
    shutil.copytree(FIXTURES / fixture, root)
    for name in CODE:
        shutil.copyfile(build.ROOT / "agents" / "refagent" / name, root / name)
    shutil.copytree(build.ROOT / "agents" / "refagent" / "tools", root / "tools")
    doc = yaml.safe_load((root / "manifest.yaml").read_text(encoding="utf-8"))
    platform_pin = yaml.safe_load((build.ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
    doc |= {"guardrail": platform_pin["guardrail"], **manifest}
    (root / "manifest.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return root


def owner(login: str) -> tuple[bool, str]:
    return login == "andaro74", "stand-in"


def refused(errors: dict[str, list[str]]) -> list[str]:
    return sorted(name for name, errs in errors.items() if errs)


def test_an_agent_with_seats_assigned_and_goldens_at_the_minimum_passes(tmp_path):
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats={s: "andaro74" for s in shipped.SEAT_SLUGS})
    assert refused(platform.evaluate(repo, "org/premiere-desk", lookup=owner)) == []


def test_s1a_and_s1b_are_refused_in_an_agent_repository_for_their_planted_reasons(tmp_path):
    s1a = platform.evaluate(agent_repo(tmp_path / "a", "s1a-unassigned-seat"), "org/premiere-desk", lookup=owner)
    s1b = platform.evaluate(agent_repo(tmp_path / "b", "s1b-no-goldens"), "org/premiere-desk", lookup=owner)
    assert refused(s1a) == ["seats assigned, each a login that administers the repository"]
    assert refused(s1b) == ["an agent's goldens: one ordinary and one trap at least, citing its own data"]


@pytest.mark.parametrize("name", ["refagent", "ratings-helper", "Premiere", "x"])
def test_a_name_agentkeel_holds_or_that_is_not_a_name_is_refused_before_anything_else(tmp_path, name):
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", name=name)
    assert refused(platform.evaluate(repo, "org/x", lookup=owner)) == ["the agent's name"]


def test_a_guardrail_that_is_not_the_platforms_is_refused(tmp_path):
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats={s: "andaro74" for s in shipped.SEAT_SLUGS},
                      guardrail={"id": "0000aaaa1111", "version": "1"})  # fmt: skip
    assert refused(platform.evaluate(repo, "org/premiere-desk", lookup=owner)) == ["the platform's guardrail"]


def test_a_null_guardrail_is_refused_even_where_the_platform_pins_none(tmp_path, monkeypatch):
    """rule-owner on PR 2: equality alone would copy a null on refagent's pin to every agent at once."""
    seated = {s: "andaro74" for s in shipped.SEAT_SLUGS}
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats=seated, guardrail=None)
    assert refused(platform.evaluate(repo, "org/premiere-desk", lookup=owner)) == ["the platform's guardrail"]


def test_a_folder_the_platforms_image_cannot_be_built_from_is_refused(tmp_path):
    """security-reviewer F3 on PR 2: a merged repository without server.py would stop every agent's deploy."""
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats={s: "andaro74" for s in shipped.SEAT_SLUGS})
    (repo / "server.py").unlink()
    errors = platform.evaluate(repo, "org/premiere-desk", lookup=owner)
    assert refused(errors) == ["the files the platform's image copies"]
    assert errors["the files the platform's image copies"] == [
        "server.py: missing; the platform's image copies it (infra/construct/agent.Dockerfile)"]


@pytest.mark.parametrize(("where", "value"), [("table_row", ["pd-001"]), ("clause_id", {"PD-1.1": 1})])
def test_an_id_that_is_not_a_string_is_refused_not_a_crash(tmp_path, where, value):
    """data-owner F4 on PR 2: a list or a mapping as an id raised, and the head got no check at all."""
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats={s: "andaro74" for s in shipped.SEAT_SLUGS})
    golden = yaml.safe_load((repo / "goldens" / "g-001.yaml").read_text(encoding="utf-8"))
    golden["expected"][where] = value
    (repo / "goldens" / "g-001.yaml").write_text(yaml.safe_dump(golden), encoding="utf-8")
    errors = platform.evaluate(repo, "org/premiere-desk", lookup=owner)
    goldens = errors["an agent's goldens: one ordinary and one trap at least, citing its own data"]
    assert any("each one id, a string" in e for e in goldens)


def test_a_row_without_a_key_or_a_key_twice_is_refused(tmp_path):
    """data-owner N2 on PR 2: R5 says rows are keyed by table_row; a missing key let `table_row: null` cite it."""
    repo = agent_repo(tmp_path, "s1a-unassigned-seat", seats={s: "andaro74" for s in shipped.SEAT_SLUGS})
    rows = json.loads((repo / "data" / "table.json").read_text(encoding="utf-8"))
    rows += [{"title": "no key"}, dict(rows[0])]
    (repo / "data" / "table.json").write_text(json.dumps(rows), encoding="utf-8")
    goldens = platform.evaluate(repo, "org/premiere-desk", lookup=owner)[
        "an agent's goldens: one ordinary and one trap at least, citing its own data"]
    assert any("have no table_row string" in e for e in goldens) and any("appear more than once" in e for e in goldens)


def test_a_symbolic_link_is_refused_before_anything_is_read(tmp_path):
    repo = agent_repo(tmp_path, "s1a-unassigned-seat")
    try:
        (repo / "data" / "secret.json").symlink_to(build.ROOT / "infra" / "platform_identity.json")
    except OSError:
        pytest.skip("this machine cannot make a symbolic link")
    assert refused(platform.evaluate(repo, "org/premiere-desk", lookup=owner)) == ["no symbolic links"]


def test_the_repositorys_ruleset_must_be_the_export_with_no_bypass():
    export = json.loads((build.ROOT / platform.EXPORT).read_text(encoding="utf-8"))
    live = {**export, "id": 1}
    assert platform.ruleset_errors([live]) == []
    assert platform.ruleset_errors([]) and "no ruleset" in platform.ruleset_errors([])[0]
    loose = {**live, "bypass_actors": [{"actor_type": "OrganizationAdmin", "bypass_mode": "always"}]}
    assert platform.ruleset_errors([loose]) == [f"{platform.EXPORT}: bypass_actors differs from live ruleset 1"]
    hidden = {**live, "bypass_actors": None}
    assert "not shown" in platform.ruleset_errors([hidden])[0]


# agentkeel-studio/owner-check's ruleset 24310403, GitHub's response as `gh api` saved it, 2026-10-01 (M06 PR 3).
LIVE_ORGANISATION_RULESET = json.loads(
    (build.ROOT / "milestones" / "M06" / "runs" / "owner_check_ruleset_24310403.json").read_text(encoding="utf-8"))
GITHUBS_OWN = {"dismissal_restriction": {"enabled": False, "allowed_actors": []},
               "require_extra_approval_for_unattributed_changes": True}


def _with_pull_request(ruleset: dict, change) -> dict:
    out = copy.deepcopy(ruleset)
    rule = next(r for r in out["rules"] if r["type"] == "pull_request")
    rule["parameters"] = change(dict(rule["parameters"]))
    return out


def test_the_export_is_the_form_github_returns_for_an_organisation_repository():
    """GitHub adds `dismissal_restriction` and `require_extra_approval_for_unattributed_changes` to an
    organisation repository's pull request rule. An export without them read as different from every live
    ruleset, so the App would have refused every head of every agent repository (M06 PR 3, before S2 and S3)."""
    assert platform.ruleset_errors([LIVE_ORGANISATION_RULESET]) == []
    without = _with_pull_request(LIVE_ORGANISATION_RULESET, lambda p: {k: v for k, v in p.items()
                                                                       if k != "dismissal_restriction"})
    assert platform.ruleset_errors([without]) == [
        f"{platform.EXPORT}: rules differs from live ruleset 24310403 (pull_request: dismissal_restriction)"]
    # The weaker live ruleset an admin could make is refused too (security-reviewer F2 on PR 3).
    weaker = _with_pull_request(LIVE_ORGANISATION_RULESET,
                                lambda p: {**p, "require_extra_approval_for_unattributed_changes": False})
    assert platform.ruleset_errors([weaker]) == [f"{platform.EXPORT}: rules differs from live ruleset 24310403 "
                                                 "(pull_request: require_extra_approval_for_unattributed_changes)"]


def test_the_post_body_is_the_export_without_githubs_own_fields():
    """`agent.post.json` is what the owner POSTs: the form GitHub accepted for ruleset 24310403, to which it
    added the two fields itself. With them added it is the export, field for field."""
    body = json.loads((build.ROOT / "infra" / "ruleset" / "agent.post.json").read_text(encoding="utf-8"))
    export = json.loads((build.ROOT / platform.EXPORT).read_text(encoding="utf-8"))
    assert _with_pull_request(body, lambda p: {**p, **GITHUBS_OWN}) == export
    assert not set(GITHUBS_OWN) & set(next(r for r in body["rules"] if r["type"] == "pull_request")["parameters"])


def test_the_rulesets_app_is_the_platforms_app():
    """agent.json's integration_id and platform_identity.json's platform_app_id are one number (5144253 from 2026-09-30)."""
    export = json.loads((build.ROOT / platform.EXPORT).read_text(encoding="utf-8"))
    identity = json.loads((build.ROOT / "infra" / "platform_identity.json").read_text(encoding="utf-8"))
    checks = [r for r in export["rules"] if r["type"] == "required_status_checks"]
    (required,) = checks[0]["parameters"]["required_status_checks"]
    assert required["context"] == shipped.PLATFORM_CHECK
    assert required["integration_id"] == identity["platform_app_id"]
    assert export["bypass_actors"] == []


# --- item 4's record: build answer (R7) -----------------------------------------


def answered(golden_id: str, row: str, clause: str, available: bool) -> dict[str, Any]:
    """An observation as refagent's runtime returns one, grounded by its tool call."""
    parsed = {"table_row": row, "clause_id": clause, "available": available}
    call = {"name": "check_availability", "status": "success",
            "output": {"found": True, "row": {"table_row": row}, "clause_candidates": [clause]}}  # fmt: skip
    return {"id": golden_id, "kind": "ordinary", "parsed": parsed, "tool_calls": [call], "stop_reason": "end_turn",
            "usage": {"inputTokens": 100, "outputTokens": 20}}  # fmt: skip


def raw_answers(*observations: dict[str, Any], **override: Any) -> dict[str, Any]:
    return {"commit": "d" * 40, "dirty": False, "model_id": "us.anthropic.claude-sonnet-4-6", "region": "us-west-2",
            "mode": "runtime", "runtime_arn": "arn:aws:bedrock-agentcore:us-west-2:1:runtime/agentkeel_premiere_desk-x",
            "bundle": "agents/premiere-desk", "observations": list(observations), **override}  # fmt: skip


def test_an_agent_that_answers_one_of_its_own_goldens_is_green_against_its_own_data():
    agent = FIXTURES / "s1a-unassigned-seat"
    raw = raw_answers(answered("g-001", "pd-001", "PD-1.1", True), {**answered("g-002", "pd-002", "PD-1.2", True), "kind": "trap"})
    document = build.compose_answer(raw, agent, "org/premiere-desk", "f" * 40, "https://run")
    assert build.answer_errors(document) == []
    assert document["verdict"] == "GREEN" and document["goldens"]["g-001"]["pass"] is True
    assert document["goldens"]["g-002"]["pass"] is False  # available: true where the table says false


def test_an_answer_citing_a_row_its_own_data_lacks_does_not_pass():
    agent = FIXTURES / "s1a-unassigned-seat"
    raw = raw_answers(answered("g-001", "r-019", "ML-2.1", True), {**answered("g-002", "pd-002", "PD-1.2", True), "kind": "trap"})
    assert build.compose_answer(raw, agent, "org/premiere-desk", "f" * 40, "https://run")["verdict"] == "RED"


def test_an_answer_record_is_read_in_the_runtime_only():
    agent = FIXTURES / "s1a-unassigned-seat"
    with pytest.raises(build.Refused, match="deployed runtime only"):
        build.compose_answer(raw_answers(mode="runner"), agent, "org/x", "f" * 40, "https://run")


# --- the observer writes raw lists (scripts/observe_template.py) ----------------

from scripts import observe_template as observer  # noqa: E402


def test_the_observer_writes_what_github_returned_and_build_rules_on_it(monkeypatch):
    """S3's first pull request through a stand-in GitHub: the observer copies seats, golden kinds and check
    runs per commit; it decides nothing, and build's F6_1 is held on that alone (BLOCK 3)."""
    runs_by_name = {
        "f6_2_standin.yaml": {"observed": None},
        "f6_3_quickstart.yaml": {"agent_name": "premiere-desk",
                                 "observed": [{"repository": "org/premiere-desk", "pull_request": 1}]},
    }  # fmt: skip
    monkeypatch.setattr(observer, "run_file", lambda name: runs_by_name[name])
    null_seats = yaml.safe_dump({"seats": {s: None for s in shipped.SEAT_SLUGS}})
    full_seats = yaml.safe_dump({"seats": {s: "andaro74" for s in shipped.SEAT_SLUGS}})
    pages = {
        "/repos/org/premiere-desk": {"created_at": "2026-10-01T09:00:00Z"},
        "/repos/org/premiere-desk/pulls/1": {"merged": True, "merged_at": "2026-10-01T11:00:00Z", "head": {"sha": "b" * 40}},
        "/repos/org/premiere-desk/pulls/1/commits?per_page=100": [{"sha": "a" * 40}, {"sha": "b" * 40}],
        f"/repos/org/premiere-desk/contents/manifest.yaml?ref={'a' * 40}": null_seats,
        f"/repos/org/premiere-desk/contents/manifest.yaml?ref={'b' * 40}": full_seats,
        f"/repos/org/premiere-desk/contents/goldens?ref={'a' * 40}": [],
        f"/repos/org/premiere-desk/contents/goldens?ref={'b' * 40}": [{"type": "file", "name": "g-001.yaml"},
                                                                      {"type": "file", "name": "g-002.yaml"}],
        f"/repos/org/premiere-desk/contents/goldens/g-001.yaml?ref={'b' * 40}": "kind: ordinary\nretired: null\n",
        f"/repos/org/premiere-desk/contents/goldens/g-002.yaml?ref={'b' * 40}": "kind: trap\nretired: null\n",
        f"/repos/org/premiere-desk/commits/{'a' * 40}/check-runs?per_page=100":
            {"check_runs": [{"name": "platform-check", "app": {"id": APP, "slug": "p"}, "conclusion": "failure"}]},
        "/repos/org/premiere-desk/rulesets?includes_parents=false&per_page=100": [{"id": 5}],
        "/repos/org/premiere-desk/rulesets/5": {"rules": [{"type": "required_status_checks", "parameters": {
            "required_status_checks": [{"context": "platform-check", "integration_id": APP}]}}]},
        f"/repos/org/premiere-desk/commits/{'b' * 40}/check-runs?per_page=100":
            {"check_runs": [{"name": "platform-check", "app": {"id": APP, "slug": "p"}, "conclusion": "success"}]},
    }  # fmt: skip
    monkeypatch.setattr(observer, "gh", lambda path, raw=False: pages[path])
    observation = observer.observe(["github"], {**observer.blank(), "platform_app_id": APP})
    commits = observation["s3"]["first_pr"]["commits"]
    assert [c["seats"]["product"] for c in commits] == [None, "andaro74"]
    assert [g["kind"] for g in commits[1]["goldens"]] == ["ordinary", "trap"]
    reading = shipped.record(observation, 28800.0)
    assert reading["F6_1"] == {"read": True, "held": True, "reasons": [], "faulty_commits": 1}
    assert reading["F6_3"]["read"] is False  # no deploy, answer or registry row read in this part


# --- the template, as scripts/make_template.py writes it --------------------------

from scripts import make_template  # noqa: E402


def test_the_template_as_shipped_is_refused_for_its_seats_and_its_goldens_and_nothing_else(tmp_path):
    """SPEC/06 section 2: every seat null, an empty goldens folder, the platform's guardrail, no workflow.
    The first pull request of the timed run is refused on exactly the two planted reasons (F6.1)."""
    repo = tmp_path / "template"
    make_template.write(repo, "example-agent")
    assert not (repo / ".github").exists()
    assert "from . import agent" in (repo / "server.py").read_text(encoding="utf-8")
    assert refused(platform.evaluate(repo, "org/example-agent", lookup=owner)) == [
        "an agent's goldens: one ordinary and one trap at least, citing its own data",
        "seats assigned, each a login that administers the repository"]


def test_the_template_with_seats_and_two_goldens_passes_the_platform_check(tmp_path):
    repo = tmp_path / "template"
    make_template.write(repo, "example-agent")
    doc = yaml.safe_load((repo / "manifest.yaml").read_text(encoding="utf-8"))
    doc["seats"] = {s: "andaro74" for s in shipped.SEAT_SLUGS}
    (repo / "manifest.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    # As refagent's g-001 and g-010 (data-owner N8 on PR 2: the trap is one the row makes, not a guess of "no").
    for golden_id, kind, row, clause, available in (("g-001", "ordinary", "r-019", "ML-2.1", True),
                                                    ("g-002", "trap", "r-009", "HS-4", False)):  # fmt: skip
        (repo / "goldens" / f"{golden_id}.yaml").write_text(yaml.safe_dump({
            "id": golden_id, "kind": kind, "question": "Can we publish it on 2027-01-20?",
            "expected": {"table_row": row, "clause_id": clause, "answer_fields": {"available": available}},
            "seat": "Data Owner", "added": "M06", "retired": None}), encoding="utf-8")  # fmt: skip
    assert refused(platform.evaluate(repo, "org/example-agent", lookup=owner)) == []


# --- the platform check's two halves (scripts/platform_check.py) ------------------

from scripts import platform_check  # noqa: E402


@pytest.fixture
def github(monkeypatch):
    """A stand-in GitHub: GET answers from `pages`, POSTs are recorded."""
    state: dict[str, Any] = {"pages": {}, "posted": []}

    def gh(path, *, method="GET", body=None, raw=False):
        if method == "POST":
            state["posted"].append((path, body))
            return {}
        return state["pages"][path]

    monkeypatch.setattr(platform_check, "gh", gh)
    return state


def test_find_lists_open_heads_the_app_has_not_checked(github):
    github["pages"].update({
        "/orgs/org/repos?per_page=100&type=all": [{"full_name": "org/a", "archived": False, "is_template": False,
                                                    "default_branch": "main"},
                                                   {"full_name": "org/template", "archived": False, "is_template": True}],
        "/repos/org/a/pulls?state=open&per_page=100": [{"number": 1, "head": {"sha": "1" * 40}},
                                                       {"number": 2, "head": {"sha": "2" * 40}}],
        "/repos/org/a/branches/main": {"commit": {"sha": "0" * 40}},
        f"/repos/org/a/commits/{'0' * 40}/check-runs?check_name=platform-check&app_id={APP}&per_page=100":
            {"check_runs": []},
        f"/repos/org/a/commits/{'1' * 40}/check-runs?check_name=platform-check&app_id={APP}&per_page=100":
            {"check_runs": [{"app": {"id": APP}, "conclusion": "failure"}]},
        f"/repos/org/a/commits/{'2' * 40}/check-runs?check_name=platform-check&app_id={APP}&per_page=100":
            {"check_runs": [{"app": {"id": 15368}, "conclusion": "success"}]},  # the stand-in's, not the App's
    })  # fmt: skip
    # The default-branch head too: a merge makes a commit no pull request's head is (security-reviewer F1).
    assert platform_check.find("org", APP) == [{"repository": "org/a", "number": 0, "head": "0" * 40},
                                               {"repository": "org/a", "number": 2, "head": "2" * 40}]


def test_post_checks_seats_and_the_ruleset_then_posts_one_check_on_the_head(github, tmp_path, monkeypatch):
    export = json.loads((build.ROOT / platform.EXPORT).read_text(encoding="utf-8"))
    github["pages"].update({"/repos/org/a": {"private": False},
                            "/repos/org/a/rulesets?includes_parents=false&per_page=100": [{"id": 9}],
                            "/repos/org/a/rulesets/9": {**export, "id": 9}})  # fmt: skip
    monkeypatch.setattr(seats, "login_holds_seat", type("L", (), {
        "__call__": staticmethod(lambda login: (login == "andaro74", "stand-in")),
        "cache_clear": staticmethod(lambda: None)})())  # fmt: skip
    (tmp_path / "1").mkdir()
    result = {"repository": "org/a", "head": "2" * 40, "errors": {"manifest schema": []}, "seat_logins": ["andaro74"]}
    (tmp_path / "1" / "result.json").write_text(json.dumps(result), encoding="utf-8")
    assert platform_check.post(tmp_path, APP) == 1
    (path, body), = github["posted"]
    assert path == "/repos/org/a/check-runs" and body["head_sha"] == "2" * 40
    assert body["name"] == "platform-check" and body["conclusion"] == "success"

    github["posted"].clear()
    result["seat_logins"] = ["floresinnovations"]
    (tmp_path / "1" / "result.json").write_text(json.dumps(result), encoding="utf-8")
    platform_check.post(tmp_path, APP)
    assert github["posted"][0][1]["conclusion"] == "failure"
    assert "floresinnovations is not a holder" in github["posted"][0][1]["output"]["summary"]

    # A private repository's ruleset is not enforced on GitHub Free: refused, whatever else passes.
    github["posted"].clear()
    result["seat_logins"] = ["andaro74"]
    (tmp_path / "1" / "result.json").write_text(json.dumps(result), encoding="utf-8")
    github["pages"]["/repos/org/a"] = {"private": True}
    platform_check.post(tmp_path, APP)
    assert github["posted"][0][1]["conclusion"] == "failure"
    assert "org/a is private" in github["posted"][0][1]["output"]["summary"]


def test_a_private_repository_is_not_deployed(github, monkeypatch):
    monkeypatch.setattr(platform_check, "repositories", lambda org: [
        {"full_name": "org/a", "id": 1, "private": True, "default_branch": "main"}])
    assert platform_check.deployable("org", APP) == []


@pytest.mark.parametrize("named", [(None, None), ("agentkeel-studio", None), (None, 5144253)])
def test_nothing_is_read_or_posted_while_the_organisation_or_the_app_is_unnamed(tmp_path, github, monkeypatch, named):
    monkeypatch.setattr(platform_check, "identity", lambda: named)
    out = tmp_path / "heads.json"
    assert platform_check.main(["find", "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == [] and github["posted"] == []


# --- the registry's writer (scripts/registry.py) ----------------------------------

from scripts import registry  # noqa: E402


class FakeTable:
    """DynamoDB's get_item and conditional put_item on one key, as the registry uses them."""

    def __init__(self) -> None:
        self.items: dict[str, dict[str, Any]] = {}

    def get_item(self, TableName, Key, ConsistentRead):  # noqa: N803 - boto3's names
        item = self.items.get(Key["name"]["S"])
        return {"Item": item} if item else {}

    def put_item(self, TableName, Item, ConditionExpression, ExpressionAttributeNames,  # noqa: N803
                 ExpressionAttributeValues=None):  # noqa: N803
        from botocore.exceptions import ClientError

        held = self.items.get(Item["name"]["S"])
        same = ExpressionAttributeValues is not None and held and held["repository_id"] == ExpressionAttributeValues[":id"]
        if held and not same:
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "PutItem")
        self.items[Item["name"]["S"]] = Item


def test_a_name_belongs_to_the_first_repository_deployed_under_it():
    table = FakeTable()
    assert registry.claim(table, "premiere-desk", "org/a", "111")[0] == 0
    # The claim is written before the stack is touched: a deploy that fails after it keeps the name (F2).
    assert table.items["premiere-desk"]["repository_id"]["S"] == "111"
    code, said = registry.claim(table, "premiere-desk", "org/b", "222")
    assert code == 3 and "held by repository 111" in said
    assert registry.write(table, "premiere-desk", "org/a", "111", "a" * 40, "7")[0] == 0
    assert registry.claim(table, "premiere-desk", "org/a", "111")[0] == 0  # the same repository redeploys
    assert table.items["premiere-desk"]["commit_sha"]["S"] == "a" * 40  # and its claim does not undo the row
    assert registry.deployed(table, "premiere-desk", "a" * 40)[0] == 0
    assert registry.write(table, "premiere-desk", "org/b", "222", "b" * 40, "8")[0] == 3
    assert table.items["premiere-desk"]["repository"]["S"] == "org/a"


def test_the_app_token_is_minted_from_a_jwt_the_apps_key_signs(monkeypatch):
    import base64

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()  # fmt: skip
    seen: list[str] = []

    def gh(path, *, method="GET", body=None, raw=False):
        seen.append(os.environ["GITHUB_TOKEN"])
        return {"id": 77} if path == "/repos/org/a/installation" else {"token": "ghs_installation"}

    import os

    monkeypatch.setattr(platform_check, "gh", gh)
    monkeypatch.setenv("GITHUB_TOKEN", "before")
    # From M07 PR 2 a token is minted for one repository and one named permission set (seed S0's reader).
    assert platform_check.app_token(APP, "org", pem, "org/a", "check") == "ghs_installation"
    assert os.environ["GITHUB_TOKEN"] == "before"  # the JWT never outlives the call
    head, body, signature = seen[0].split(".")
    pad = lambda s: s + "=" * (-len(s) % 4)  # noqa: E731
    assert json.loads(base64.urlsafe_b64decode(pad(body)))["iss"] == str(APP)
    key.public_key().verify(base64.urlsafe_b64decode(pad(signature)), f"{head}.{body}".encode(),
                            padding.PKCS1v15(), hashes.SHA256())  # fmt: skip


@pytest.mark.parametrize("sql", [
    'SELECT name FROM "agentkeel-registry" UNION SELECT \'ghost-agent\'',
    'SELECT name FROM "agentkeel-registry" r, other_table o',
    'SELECT name FROM (SELECT \'ghost-agent\' AS name)',
    "SELECT * FROM (VALUES ('ghost-agent'))",
])
def test_a_second_source_with_no_from_or_join_of_its_own_is_refused(tmp_path, sql):
    """cold review F4 on PR 2: tables() named only the registry for each of these, and they passed."""
    from src.validate import panel

    dashboard = json.loads((build.ROOT / panel.PANEL).read_text(encoding="utf-8"))
    dashboard["panels"][0]["targets"][0]["rawSQL"] = sql
    (tmp_path / "infra" / "grafana").mkdir(parents=True)
    (tmp_path / panel.PANEL).write_text(json.dumps(dashboard), encoding="utf-8")
    assert any("reads a second source" in e for e in panel.check(tmp_path))


def test_a_malformed_panel_target_is_refused_not_a_crash(tmp_path):
    from src.validate import panel

    dashboard = json.loads((build.ROOT / panel.PANEL).read_text(encoding="utf-8"))
    dashboard["panels"][0]["targets"] = ["not a mapping", {"refId": "B", "datasource": "registry"}]
    (tmp_path / "infra" / "grafana").mkdir(parents=True)
    (tmp_path / panel.PANEL).write_text(json.dumps(dashboard), encoding="utf-8")
    assert len(panel.check(tmp_path)) == 2


def test_the_observer_reads_a_missing_file_as_a_fact_and_a_refused_read_as_an_error(monkeypatch):
    """F5's split (second cold read, N4): a 404 is the commit's; a 403 is the read's, and is recorded."""
    import urllib.error

    def gh(path, *, raw=False):
        code = 404 if "manifest.yaml" in path else 403
        raise urllib.error.HTTPError(path, code, "x", {}, None)

    monkeypatch.setattr(observer, "gh", gh)
    folder = observer.folder_at("org/a", "a" * 40)
    assert folder["seats"] is None and folder["read_error"] == "goldens/: 403"
