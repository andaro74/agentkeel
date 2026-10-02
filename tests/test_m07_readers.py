"""M07 PR 2's readers, beyond what the seed tests ask of them (SPEC/07 §6).

The seed tests (`tests/test_m07_seeds.py`) hand each fixture to its reader and ask for the planted
refusal. These hold the rest: the arms a fixture does not reach, the unread cases, and the shapes the
observer writes. Nothing here calls AWS, a model or GitHub.
"""

from __future__ import annotations

import json
import os
import urllib.error
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts import platform_check

APP = 5144253


@pytest.fixture
def key() -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    return rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()  # fmt: skip


@pytest.fixture
def github(monkeypatch):
    """A stand-in GitHub: every request is recorded with the token it carried; GETs answer from `pages`."""
    state: dict[str, Any] = {"pages": {}, "sent": [], "fail": {}}

    def gh(path, *, method="GET", body=None, raw=False):
        state["sent"].append((method, path, body, os.environ.get("GITHUB_TOKEN")))
        if (method, path) in state["fail"]:
            raise urllib.error.HTTPError(path, state["fail"][(method, path)], "x", {}, None)
        if method == "POST" and path.endswith("/access_tokens"):
            return {"token": f"token-for-{'+'.join(sorted(body['permissions']))}"}
        if method != "GET":
            return {}
        return state["pages"][path]

    monkeypatch.setattr(platform_check, "gh", gh)
    return state


# --- the token (S0; rulings/pr2-security.md item 5) ----------------------------


def test_a_token_is_minted_for_one_repository_and_one_named_set(github, key):
    github["pages"]["/repos/org/a/installation"] = {"id": 77}
    assert platform_check.app_token(APP, "org", key, "org/a", "check") == "token-for-checks+contents+metadata+pull_requests"
    (method, path, body, _token), = [s for s in github["sent"] if s[0] == "POST"]
    assert path == "/app/installations/77/access_tokens"
    assert body == {"repositories": ["a"], "permissions": platform_check.PERMISSION_SETS["check"]}


@pytest.mark.parametrize("repository, named, said", [
    (None, "check", "one repository"),
    ("", "check", "one repository"),
    ("a", "check", "one repository"),  # a name with no owner
    ("org/a/b", "check", "one repository"),
    ("other/a", "check", "not org's"),  # another account's repository
    ("org/a", None, "named permission set"),
    ("org/a", "everything", "named permission set"),
    ("org/a", {"administration": "write"}, "named permission set"),  # a set by value is not a named set
])  # fmt: skip
def test_no_token_is_asked_for_without_a_repository_and_a_named_set(github, key, repository, named, said):
    with pytest.raises((ValueError, TypeError), match=said):
        platform_check.app_token(APP, "org", key, repository, named)
    assert github["sent"] == []  # refused before any request, the JWT's included


def test_no_named_set_can_both_open_a_pull_request_and_post_the_check():
    """Item 2: the key that can post the check cannot push or open a pull request, and the other way."""
    sets = platform_check.PERMISSION_SETS
    assert sorted(sets) == ["check", "observe", "open", "rulesets"]
    writes = {name: {p for p, level in perms.items() if level == "write"} for name, perms in sets.items()}
    assert writes == {"check": {"checks"}, "rulesets": {"administration"}, "open": {"contents", "pull_requests"},
                      "observe": set()}  # fmt: skip


def result_file(tmp_path, **more: Any) -> None:
    (tmp_path / "1").mkdir(exist_ok=True)
    result = {"repository": "org/a", "head": "2" * 40, "errors": {"manifest schema": []}, "seat_logins": [], **more}
    (tmp_path / "1" / "result.json").write_text(json.dumps(result), encoding="utf-8")


def test_post_reads_the_ruleset_under_one_token_revokes_it_and_posts_under_another(github, tmp_path):
    from src.validate import agent as platform
    from src.verdict import ROOT

    export = json.loads((ROOT / platform.EXPORT).read_text(encoding="utf-8"))
    github["pages"].update({"/repos/org/a": {"private": False},
                            "/repos/org/a/rulesets?includes_parents=false&per_page=100": [{"id": 9}],
                            "/repos/org/a/rulesets/9": {**export, "id": 9}})  # fmt: skip
    result_file(tmp_path)
    minted: list[tuple[str, str]] = []

    def mint(repository: str, named: str) -> str:
        minted.append((repository, named))
        return f"token-{named}"

    assert platform_check.post(tmp_path, APP, mint=mint) == 1
    assert minted == [("org/a", "rulesets"), ("org/a", "check")]
    by_path = {(method, path.split("?")[0]): token for method, path, _body, token in github["sent"]}
    assert by_path[("GET", "/repos/org/a/rulesets")] == "token-rulesets"
    assert by_path[("GET", "/repos/org/a/rulesets/9")] == "token-rulesets"
    assert by_path[("DELETE", "/installation/token")] == "token-rulesets"  # revoked once the ruleset is read
    assert by_path[("GET", "/repos/org/a")] == "token-check"
    assert by_path[("POST", "/repos/org/a/check-runs")] == "token-check"
    order = [(method, path.split("?")[0]) for method, path, _body, _token in github["sent"]]
    assert order.index(("DELETE", "/installation/token")) < order.index(("POST", "/repos/org/a/check-runs"))
    (body,) = [b for method, path, b, _t in github["sent"] if method == "POST" and path.endswith("/check-runs")]
    assert body["conclusion"] == "success"


def test_before_the_grant_the_head_is_refused_and_the_check_still_posted(github, tmp_path):
    """Until Administration: write is granted, GitHub answers 422 to the `rulesets` mint. The head is
    refused for a ruleset that could not be read, and the refusal is posted: closed, not silent."""
    github["pages"]["/repos/org/a"] = {"private": False}
    result_file(tmp_path)

    def mint(repository: str, named: str) -> str:
        if named == "rulesets":
            raise urllib.error.HTTPError("/app/installations/77/access_tokens", 422, "x", {}, None)
        return f"token-{named}"

    assert platform_check.post(tmp_path, APP, mint=mint) == 1
    (body,) = [b for method, path, b, _t in github["sent"] if method == "POST" and path.endswith("/check-runs")]
    assert body["conclusion"] == "failure" and "could not be read (422)" in body["output"]["summary"]
    assert not any(method == "DELETE" for method, *_ in github["sent"])  # no token was minted to revoke


# --- the reader of the grant (S0; rulings/pr2-security.md item 6) --------------

FIXTURES = Path(__file__).parent / "fixtures" / "m07" / "s0-app-token"


def s0(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def ruling(tmp_path, body: str, name: str = "pr2-security.md") -> None:
    folder = tmp_path / "milestones" / "M07" / "rulings"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(body, encoding="utf-8")


GRANT_BLOCK = "```yaml\ngrant:\n  agentkeel-observer:\n    app_id: 7\n    environment: platform-observer\n```\n"


def test_a_draft_is_not_a_grant_and_two_blocks_are_refused(tmp_path):
    ruling(tmp_path, f"DRAFT for a seat.\n\n{GRANT_BLOCK}")
    with pytest.raises(platform_check.NoGrant, match="a draft"):
        platform_check.load_grant(tmp_path)
    assert platform_check.load_grant(tmp_path, ruled_only=False)["agentkeel-observer"]["app_id"] == 7
    ruling(tmp_path, f"Ruled by andaro74 as Security, 2026-10-02.\n\n{GRANT_BLOCK}")
    assert sorted(platform_check.load_grant(tmp_path)) == ["agentkeel-observer"]
    # "Ruled by" inside a sentence is not the line the gate reads.
    ruling(tmp_path, f"Not ruled until this line reads \"Ruled by\".\n\n{GRANT_BLOCK}")
    with pytest.raises(platform_check.NoGrant, match="a draft"):
        platform_check.load_grant(tmp_path)
    ruling(tmp_path, f"Ruled by andaro74 as Security.\n\n{GRANT_BLOCK}")
    ruling(tmp_path, f"Ruled by andaro74 as Security.\n\n{GRANT_BLOCK}", name="pr3-security.md")
    with pytest.raises(platform_check.NoGrant, match="found 2"):
        platform_check.load_grant(tmp_path)


def test_no_ruling_with_a_block_is_no_grant(tmp_path):
    ruling(tmp_path, "Ruled by andaro74 as Security.\n\nNo block here.\n")
    with pytest.raises(platform_check.NoGrant, match="found 0"):
        platform_check.load_grant(tmp_path)


def test_the_rulings_own_block_is_the_fixtures_grant_but_for_the_ids_not_yet_made():
    """The fixture is the shape of the ruling's block: if either moves, this says so. The two new Apps'
    ids are null in the ruling until each App exists, and the reader refuses a null id."""
    live = platform_check.load_grant(ruled_only=False)
    fixture = s0("grant.json")
    assert sorted(live) == sorted(fixture)
    for slug in ("agentkeel-platform", "agentkeel-upgrades", "agentkeel-observer"):
        assert {k: v for k, v in live[slug].items() if k != "app_id"} == {k: v for k, v in fixture[slug].items() if k != "app_id"}
    assert live["agentkeel-platform"]["app_id"] == fixture["agentkeel-platform"]["app_id"] == APP
    assert live["environments"] == fixture["environments"]


def test_a_grant_not_yet_made_reads_as_narrower_and_not_as_an_error():
    """Before the grant, 5144253 holds Administration: read. That is inside the ruled grant: nothing
    is beyond it, so the reader passes, and the keyed job then finds it cannot mint `rulesets`."""
    held = {**s0("installation_as_ruled.json"), "permissions": {"administration": "read", "checks": "write",
                                                               "contents": "read", "metadata": "read",
                                                               "pull_requests": "read"}}  # fmt: skip
    assert platform_check.grant_errors(held, s0("environment_as_ruled.json"), s0("grant.json")) == []
    selected = {**s0("upgrades_org_as_ruled.json"), "repository_selection": "selected", "repositories": ["owner-check"]}
    assert platform_check.grant_errors(selected, s0("environment_upgrades_as_ruled.json"), s0("grant.json")) == []


@pytest.mark.parametrize("change, said", [
    ({"branch_policies": []}, "no deployment policy main (branch)"),  # no policy: any branch may deploy
    ({"branch_policies": None}, "were not read"),
    ({"branch_policies": [{"name": "(every protected branch)", "type": "protected"}]}, "protected"),
    ({"can_admins_bypass": None}, "can_admins_bypass is None"),
    ({"secrets": []}, "holds 0 secrets"),
])  # fmt: skip
def test_an_environment_that_does_not_limit_the_key_to_main_is_refused(change, said):
    environment = {**s0("environment_as_ruled.json"), **change}
    errors = platform_check.grant_errors(s0("installation_as_ruled.json"), environment, s0("grant.json"))
    assert any(said in e for e in errors), errors


def test_an_unknown_level_and_an_unread_list_are_refused_not_passed():
    grant = s0("grant.json")
    odd = {**s0("installation_as_ruled.json"), "permissions": {"metadata": "admin"}}
    assert any("metadata is admin" in e for e in platform_check.grant_errors(odd, s0("environment_as_ruled.json"), grant))
    unread = {**s0("upgrades_as_ruled.json"), "repositories": None}
    errors = platform_check.grant_errors(unread, s0("environment_upgrades_as_ruled.json"), grant)
    assert any("were not read" in e for e in errors), errors
    assert platform_check.grant_errors({"app_slug": "environments"}, {}, grant)[0].startswith("the grant names no App")


def live_pages(github, installation: dict[str, Any], registered: dict[str, str], environment: dict[str, Any],
               others: tuple[dict[str, Any], ...] = ()) -> None:  # fmt: skip
    name = environment["name"]
    github["pages"].update({
        "/app": {"slug": installation["app_slug"], "id": installation["app_id"], "permissions": registered},
        "/app/installations?per_page=100&page=1": [{k: v for k, v in one.items() if k != "repositories"}
                                                   for one in (installation, *others)],
        "/installation/repositories?per_page=100&page=1": {
            "total_count": len(installation["repositories"]),
            "repositories": [{"name": n} for n in installation["repositories"]]},
        f"/repos/andaro74/agentkeel/environments/{name}": {
            "can_admins_bypass": environment["can_admins_bypass"],
            "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}},
        f"/repos/andaro74/agentkeel/environments/{name}/deployment-branch-policies?per_page=100": {
            "branch_policies": environment["branch_policies"]},
    })  # fmt: skip


def test_the_grant_is_read_back_with_the_apps_jwt_and_a_metadata_only_token(github, key, tmp_path, monkeypatch):
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    monkeypatch.setenv("GITHUB_TOKEN", "the-jobs-own-token")
    installation = s0("observer_as_ruled.json")
    live_pages(github, installation, installation["permissions"], s0("environment_observer_as_ruled.json"))
    read, errors = platform_check.check_grant("agentkeel-observer", key)
    assert errors == [] and read["narrower"] == []
    assert read["installations"][0]["repositories"] == ["agent-template", "owner-check"]
    assert read["environment"]["secrets"] is None  # not read by a job; said in the artifact, not guessed
    minted = [body for method, path, body, _t in github["sent"] if method == "POST"]
    assert minted == [{"permissions": {"metadata": "read"}}]  # the only token the reader mints
    revoked = [t for method, path, _b, t in github["sent"] if method == "DELETE"]
    assert revoked == ["token-for-metadata"]
    environment_reads = [t for method, path, _b, t in github["sent"] if "/environments/" in path]
    assert set(environment_reads) == {"the-jobs-own-token"}  # the environment is not read as the App
    assert os.environ["GITHUB_TOKEN"] == "the-jobs-own-token"


def test_a_permission_registered_and_not_yet_accepted_is_beyond_the_grant(github, key, monkeypatch):
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    installation = s0("observer_as_ruled.json")
    live_pages(github, installation, {**installation["permissions"], "contents": "write"},
               s0("environment_observer_as_ruled.json"))  # fmt: skip
    _read, errors = platform_check.check_grant("agentkeel-observer", key)
    assert errors == ["agentkeel-observer as registered: permission contents is write, the grant names read"]


def test_a_key_that_is_another_apps_and_an_unreadable_github_are_refused(github, key, monkeypatch):
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    installation = s0("observer_as_ruled.json")
    live_pages(github, installation, installation["permissions"], s0("environment_observer_as_ruled.json"))
    github["pages"]["/app"] = {"slug": "agentkeel-platform", "id": APP, "permissions": installation["permissions"]}
    _read, errors = platform_check.check_grant("agentkeel-observer", key)
    assert any("the key is App agentkeel-platform" in e for e in errors), errors
    github["fail"][("GET", "/app")] = 401
    read, errors = platform_check.check_grant("agentkeel-observer", key)
    assert read["installations"] == [] and any("could not be read as the App" in e for e in errors), errors


def test_the_grant_command_stops_on_a_draft_a_missing_key_and_a_missing_id(tmp_path, monkeypatch, capsys):
    out = tmp_path / "read.json"
    monkeypatch.delenv("AGENTKEEL_APP_PRIVATE_KEY", raising=False)
    assert platform_check.main(["grant", "--app", "agentkeel-platform", "--out", str(out)]) == 1
    assert "read in its key's environment only" in capsys.readouterr().out
    monkeypatch.setenv("AGENTKEEL_APP_PRIVATE_KEY", "not a key")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: {"agentkeel-upgrades": {"app_id": None}})
    assert platform_check.main(["grant", "--app", "agentkeel-upgrades", "--out", str(out)]) == 1
    assert "holds no app_id" in capsys.readouterr().out
    assert "AGENTKEEL_APP_PRIVATE_KEY" not in os.environ and not out.exists()  # the key is taken out of the environment


# --- the platform upgrade (S1; SPEC/07 section 6) -------------------------------

from scripts import platform_pr, platform_upgrade  # noqa: E402

S1 = Path(__file__).parent / "fixtures" / "m07" / "s1-platform-upgrade"
MANIFEST = """# the team's own comment
name: premiere-desk
guardrail:
  id: 1088aw3ujhyd  # the platform's
  version: "5"
seats:
  product: andaro74
rollout: all-at-once
platform_version: m06  # written by the template
"""


def test_the_manifest_edit_moves_two_fields_and_keeps_every_other_byte():
    edited = platform_upgrade.set_fields(MANIFEST, {"platform_version": "m07", "guardrail": {"id": "1088aw3ujhyd", "version": "6"}})
    assert edited == MANIFEST.replace('version: "5"', 'version: "6"').replace("platform_version: m06", "platform_version: m07")
    assert platform_upgrade.set_fields(MANIFEST, {"platform_version": "m06"}) == MANIFEST  # nothing to move
    # A version that is a commit is a string of digits and letters; all digits must stay a string.
    assert 'platform_version: "1234567"  # written' in platform_upgrade.set_fields(MANIFEST, {"platform_version": "1234567"})
    # A field that changes shape, or is not there, is written whole.
    nulled = MANIFEST.replace('guardrail:\n  id: 1088aw3ujhyd  # the platform\'s\n  version: "5"', "guardrail: null")
    whole = platform_upgrade.set_fields(nulled, {"guardrail": {"id": "1088aw3ujhyd", "version": "6"}})
    assert yaml.safe_load(whole)["guardrail"] == {"id": "1088aw3ujhyd", "version": "6"} and "seats:" in whole
    added = platform_upgrade.set_fields(MANIFEST.replace("rollout: all-at-once\n", ""), {"rollout": "retired"})
    assert yaml.safe_load(added)["rollout"] == "retired"
    with pytest.raises(platform_upgrade.Refused, match="not a mapping"):
        platform_upgrade.set_fields("- a list\n", {"platform_version": "m07"})


def test_the_upgrade_reads_the_templates_own_manifest_when_no_platform_json_is_given(tmp_path):
    """Live, the platform side is the template repository's checkout: its manifest carries both fields."""
    template = tmp_path / "template"
    template.mkdir()
    (template / "manifest.yaml").write_text(MANIFEST.replace("m06", "m07").replace('"5"', '"6"'), encoding="utf-8")
    (template / "server.py").write_text("NEW = True\n", encoding="utf-8")
    (template / "agent.py").write_text("NOT_THE_PLATFORMS = True\n", encoding="utf-8")
    changed = platform_upgrade.diff(S1 / "agent", template)
    assert sorted(changed) == ["manifest.yaml", "server.py"]
    assert yaml.safe_load(changed["manifest.yaml"])["platform_version"] == "m07"
    (template / "manifest.yaml").write_text("name: x\n", encoding="utf-8")
    with pytest.raises(platform_upgrade.Refused, match="names no platform_version"):
        platform_upgrade.diff(S1 / "agent", template)


def test_behind_is_ancestry_in_agentkeel_not_a_comparison_of_names():
    assert platform_upgrade.behind("m05", "m06")[0] is True
    assert platform_upgrade.behind("m06", "m06") == (False, "at m06")
    assert platform_upgrade.behind("m06", "m05")[0] is False  # ahead is not behind
    assert platform_upgrade.behind("m99", "m06")[0] is False  # a tag that is not there is not read as behind
    assert platform_upgrade.behind("not-a-version", "m06")[0] is False
    head = platform_upgrade.commit_of("m06")
    assert head and platform_upgrade.behind("m05", head[:12])[0] is True  # a short commit is a version too


def plan_entry(tmp_path, **more: Any) -> dict[str, Any]:
    def fetch(repository: str, commit: str, into: Path) -> Path:
        return S1 / "agent"

    entry = platform_upgrade.plan_one({"repository": "agentkeel-studio/premiere-desk", "commit": "c" * 40,
                                       "name": "premiere-desk"}, more.pop("template", S1 / "platform"), tmp_path, fetch)  # fmt: skip
    return {**entry, **more}


@pytest.fixture
def versions(monkeypatch):
    """The fixture's versions, m06 and m07: m07 is no tag yet, so ancestry is given here, not read."""
    order = {"m06": "6" * 40, "m07": "7" * 40}
    monkeypatch.setattr(platform_upgrade, "commit_of", lambda version, root=None: order.get(version))
    monkeypatch.setattr(platform_upgrade, "behind", lambda mine, theirs, root=None: (
        (mine, theirs) == ("m06", "m07"), f"{mine} is behind {theirs}" if (mine, theirs) == ("m06", "m07") else f"at {theirs}"))


def test_the_plan_names_the_branch_the_kind_and_the_files_and_reads_the_agent_as_data(tmp_path, versions):
    entry = plan_entry(tmp_path)
    assert entry["open"] is True and entry["branch"] == "platform-upgrade/m07" and (entry["from"], entry["to"]) == ("m06", "m07")
    assert sorted(entry["files"]) == ["manifest.yaml", "server.py"]
    # The fixture's agent has no goldens, no prompt and no tool: the check at main refuses its head as it stands.
    assert entry["kind"] == "major" and "the files the platform's image copies" in entry["refused"]
    assert "**Kind: major.**" in entry["body"] and "`manifest.yaml`, `server.py`" in entry["body"]


def test_an_agent_that_is_not_behind_or_is_retired_gets_no_pull_request(tmp_path, versions, monkeypatch):
    template = tmp_path / "at-m06"
    template.mkdir()
    (template / "platform.json").write_text(json.dumps({"platform_version": "m06", "guardrail": {"id": "1088aw3ujhyd", "version": "5"}}), encoding="utf-8")
    entry = plan_entry(tmp_path, template=template)
    assert entry["open"] is False and entry["why"] == "at m06" and "files" not in entry

    retired = tmp_path / "retired"
    retired.mkdir()
    (retired / "manifest.yaml").write_text((S1 / "agent" / "manifest.yaml").read_text(encoding="utf-8").replace(
        "rollout: all-at-once", "rollout: retired"), encoding="utf-8")  # fmt: skip
    entry = platform_upgrade.plan_one({"repository": "agentkeel-studio/gone", "commit": "c" * 40, "name": "gone"},
                                      S1 / "platform", tmp_path, lambda *a: retired)  # fmt: skip
    assert entry["open"] is False and "retired" in entry["why"]

    def unreadable(*_a):
        raise platform_upgrade.Refused("could not be read as data: not found")

    entry = platform_upgrade.plan_one({"repository": "agentkeel-studio/gone", "commit": "c" * 40, "name": "gone"},
                                      S1 / "platform", tmp_path, unreadable)  # fmt: skip
    assert entry["open"] is False and "could not be read" in entry["why"]


@pytest.mark.parametrize("change, said", [
    ({"repository": "someone-else/premiere-desk"}, "not an agent repository"),
    ({"repository": "agentkeel-studio/agent-template"}, "not an agent repository"),
    ({"files": {".github/workflows/own.yml": "on: push"}}, "does not own"),
    ({"files": {"agent.py": "x = 1"}}, "does not own"),
    ({"base": "main"}, "not a commit"),
    ({"to": "m99", "branch": "platform-upgrade/m99"}, "not a commit of main's history"),
    ({"branch": "main"}, "is not platform-upgrade/"),
    ({"kind": "tiny"}, "neither major nor minor"),
    ({"name": "refagent/../x"}, "not a name"),
    # security-reviewer 4 on M07 PR 2: what the body will say is held to check names, and to the kind.
    ({"refused": ["[click](https://example.invalid)"]}, "not a list of check names"),
    ({"refused": "the files"}, "not a list of check names"),
    ({"refused": []}, "does not agree with 0 refusing checks"),
])  # fmt: skip
def test_the_keyed_job_checks_the_artifact_again_before_it_mints(tmp_path, versions, monkeypatch, change, said):
    """The plan is data from a job that read an agent repository. Each bound is held again on main's code."""
    monkeypatch.setattr(platform_upgrade.subprocess, "run", lambda *a, **k: type("Done", (), {"returncode": 0})())
    monkeypatch.setattr(platform_upgrade, "commit_of", lambda version, root=None: {"m06": "6" * 40, "m07": "7" * 40}.get(version))
    entry = plan_entry(tmp_path)
    current = (S1 / "agent" / "manifest.yaml").read_text(encoding="utf-8")
    assert platform_upgrade.entry_errors(entry, "agentkeel-studio", current) == []
    errors = platform_upgrade.entry_errors({**entry, **change}, "agentkeel-studio", current)
    assert any(said in e for e in errors), errors


def test_a_proposed_manifest_that_moves_another_field_is_refused_by_the_keyed_job(tmp_path, versions, monkeypatch):
    monkeypatch.setattr(platform_upgrade.subprocess, "run", lambda *a, **k: type("Done", (), {"returncode": 0})())
    monkeypatch.setattr(platform_upgrade, "commit_of", lambda version, root=None: {"m06": "6" * 40, "m07": "7" * 40}.get(version))
    entry = plan_entry(tmp_path)
    current = (S1 / "agent" / "manifest.yaml").read_text(encoding="utf-8")
    entry["files"]["manifest.yaml"] = entry["files"]["manifest.yaml"].replace("security: andaro74", "security: someone-else")
    errors = platform_upgrade.entry_errors(entry, "agentkeel-studio", current)
    assert errors == ["manifest.yaml: the proposal moves seats"]


# --- the one place a draft pull request is opened (scripts/platform_pr.py) ------


@pytest.fixture
def repo(github):
    github["pages"].update({
        "/repos/org/a/git/ref/heads/main": {"object": {"sha": "b" * 40}},
        f"/repos/org/a/git/commits/{'b' * 40}": {"tree": {"sha": "t" * 40}},
        "/repos/org/a/pulls?state=all&head=org:platform-upgrade/m07&per_page=100": [],
    })  # fmt: skip
    github["fail"][("GET", "/repos/org/a/git/ref/heads/platform-upgrade/m07")] = 404
    real = platform_check.gh

    def gh(path, *, method="GET", body=None, raw=False):
        if method == "POST":
            github["sent"].append((method, path, body, os.environ.get("GITHUB_TOKEN")))
            return {"sha": "n" * 40, "number": 7, "html_url": "https://github.com/org/a/pull/7"}
        return real(path, method=method, body=body, raw=raw)

    platform_check.gh = gh  # the fixture's monkeypatch restores it
    return github


def test_a_draft_is_one_commit_on_a_new_branch_and_one_pull_request(repo):
    opened = platform_pr.open_draft("org/a", "main", "b" * 40, "platform-upgrade/m07", {"manifest.yaml": "x: 1\n"},
                                    title="t", body="b", message="m")  # fmt: skip
    posts = [(path, body) for method, path, body, _t in repo["sent"] if method == "POST"]
    assert [path.rsplit("/", 1)[-1] for path, _b in posts] == ["trees", "commits", "refs", "pulls"]
    assert posts[1][1]["parents"] == ["b" * 40] and posts[2][1]["ref"] == "refs/heads/platform-upgrade/m07"
    assert posts[3][1]["draft"] is True and posts[3][1]["base"] == "main"
    assert opened["number"] == 7 and opened["files"] == ["manifest.yaml"]


@pytest.mark.parametrize("branch, files, said", [
    ("platform-upgrade/m07", {".github/workflows/x.yml": "on: push"}, "never writes this path"),
    ("platform-upgrade/m07", {"../outside": "x"}, "never writes this path"),
    ("platform-upgrade/m07", {}, "empty diff"),
    ("main", {"manifest.yaml": "x"}, "not a branch the platform opens"),
    ("feature/anything", {"manifest.yaml": "x"}, "not a branch the platform opens"),
])  # fmt: skip
def test_no_workflow_path_no_empty_change_and_no_other_branch(repo, branch, files, said):
    with pytest.raises(platform_pr.Refused, match=said):
        platform_pr.open_draft("org/a", "main", "b" * 40, branch, files, title="t", body="b", message="m")
    assert not any(method == "POST" for method, *_ in repo["sent"])


def test_nothing_is_opened_twice_and_nothing_against_a_base_that_moved(repo):
    with pytest.raises(platform_pr.Refused, match="computed at"):
        platform_pr.open_draft("org/a", "main", "c" * 40, "platform-upgrade/m07", {"manifest.yaml": "x"},
                               title="t", body="b", message="m")  # fmt: skip
    repo["pages"]["/repos/org/a/pulls?state=all&head=org:platform-upgrade/m07&per_page=100"] = [{"number": 3, "state": "closed"}]
    with pytest.raises(platform_pr.Refused, match="#3 was opened from platform-upgrade/m07 .closed."):
        platform_pr.open_draft("org/a", "main", "b" * 40, "platform-upgrade/m07", {"manifest.yaml": "x"},
                               title="t", body="b", message="m")  # fmt: skip
    del repo["fail"][("GET", "/repos/org/a/git/ref/heads/platform-upgrade/m07")]
    repo["pages"]["/repos/org/a/git/ref/heads/platform-upgrade/m07"] = {"object": {"sha": "d" * 40}}
    assert platform_pr.already("org/a", "platform-upgrade/m07") == "the branch platform-upgrade/m07 exists"
    assert not any(method == "POST" for method, *_ in repo["sent"])


# --- panel 2's query (S4's query reader; src/validate/panel.py) -----------------

from src.validate import panel  # noqa: E402
from src.verdict import ROOT  # noqa: E402

GOOD_SQL = 'SELECT commit, verdict, mode FROM "agentkeel_registry"."default"."agentkeel-envelopes" ORDER BY commit'


def place_panel_2(tmp_path, **target: Any) -> Path:
    dashboard = json.loads((ROOT / panel.PANEL_2).read_text(encoding="utf-8"))
    dashboard["panels"][0]["targets"][0] |= target
    (tmp_path / "infra" / "grafana").mkdir(parents=True, exist_ok=True)
    (tmp_path / panel.PANEL_2).write_text(json.dumps(dashboard), encoding="utf-8")
    return tmp_path


def test_panel_2_as_committed_passes_and_its_query_is_the_one_held_here(tmp_path):
    assert panel.check_panel_2(ROOT) == []
    dashboard = json.loads((ROOT / panel.PANEL_2).read_text(encoding="utf-8"))
    assert dashboard["panels"][0]["targets"][0]["rawSQL"] == GOOD_SQL
    assert panel.check_panel_2(tmp_path) == [f"{panel.PANEL_2}: missing; panel 2 has no query to read (SPEC/07 section 6)"]


def test_s4s_fixture_is_refused_for_its_computed_verdict_whatever_its_source():
    """The fixture's source names were placeholders (SPEC/07 section 11, R8). With the source put right,
    the planted reason alone still refuses it."""
    fixture_sql = json.loads((ROOT / "tests/fixtures/m07/s4-panel2/dashboard.json").read_text(encoding="utf-8"))[
        "panels"][0]["targets"][0]["rawSQL"]  # fmt: skip
    errors = panel.panel_2_sql_errors(fixture_sql, "A")
    assert any("computes its verdict column ('GREEN' AS verdict)" in e for e in errors), errors
    right_source = fixture_sql.replace('"agentkeel_envelopes"."default"."envelopes"', '"agentkeel_registry"."default"."agentkeel-envelopes"')
    errors = panel.panel_2_sql_errors(right_source, "A")
    assert errors and all("verdict" in e for e in errors) and not any("reads" in e for e in errors), errors


@pytest.mark.parametrize("sql, said", [
    (GOOD_SQL.replace("verdict,", "upper(verdict),"), "computes its verdict column"),
    (GOOD_SQL.replace("verdict,", "CASE WHEN verdict = 'RED' THEN 'GREEN' ELSE verdict END AS verdict,"), "computes its verdict column"),
    (GOOD_SQL.replace("verdict,", "verdict AS v,"), "computes its verdict column"),
    (GOOD_SQL.replace("mode ", "length(mode) "), "computes a column"),
    (GOOD_SQL.replace(" ORDER BY", " WHERE verdict = 'GREEN' ORDER BY"), "names verdict outside its select list"),
    (GOOD_SQL.replace(" ORDER BY", " WHERE mode <> 'GREEN' ORDER BY"), "carries a verdict as a constant"),
    (GOOD_SQL.replace("commit, verdict, mode", "commit, mode"), "does not select 'verdict' as stored"),
    (GOOD_SQL.replace("commit, verdict, mode", "*"), "computes a column"),
    (GOOD_SQL.replace("commit, verdict, mode", "commit, verdict, tag"), "selects 'tag'"),
    (GOOD_SQL.replace("agentkeel-envelopes", "agentkeel-registry"), "reads 'agentkeel-registry'"),
    (GOOD_SQL + " UNION SELECT 'x', 'y', 'z'", "reads a second source"),
    ("", "names no table"),
])  # fmt: skip
def test_a_panel_2_query_that_is_not_the_stored_columns_from_the_one_table_is_refused(tmp_path, sql, said):
    errors = panel.check_panel_2(place_panel_2(tmp_path, rawSQL=sql))
    assert any(said in e for e in errors), errors
    assert all(e.startswith(panel.PANEL_2) for e in errors)


def test_a_panel_2_on_another_data_source_or_with_no_panel_is_refused(tmp_path):
    errors = panel.check_panel_2(place_panel_2(tmp_path, datasource={"type": "grafana-athena-datasource", "uid": "other"}))
    assert any("reads data source 'other'" in e for e in errors), errors
    (tmp_path / panel.PANEL_2).write_text(json.dumps({"panels": [{"id": 1}]}), encoding="utf-8")
    assert panel.check_panel_2(tmp_path) == [f"{panel.PANEL_2}: no panel with id 2"]
    (tmp_path / panel.PANEL_2).write_text("{", encoding="utf-8")
    assert "not JSON" in panel.check_panel_2(tmp_path)[0]


def test_panel_1s_check_does_not_read_panel_2_and_the_other_way(tmp_path):
    """Two checks, each with its own file: a panel 2 fault must be named by the panel 2 check alone."""
    place_panel_2(tmp_path, rawSQL="SELECT commit, 'GREEN' AS verdict FROM x")
    assert all(panel.PANEL_2 not in e for e in panel.check(tmp_path))
    from src.validate import checks

    names = [name for name in checks.CHECKS if "panel 2" in name]
    assert names == ["panel 2 selects the verdict as stored, from the envelopes' table and nothing else"]
    assert checks.CHECKS[names[0]] is panel.check_panel_2 and len(checks.CHECKS) == 20


# --- inherited from PR 1's review: claim 6's readers (src/verdict/template.py) ----

import copy  # noqa: E402

from src.verdict import template as shipped  # noqa: E402
from tests import test_m06_readers as m06  # noqa: E402


def test_a_merged_s2_is_a_miss_even_when_github_says_its_state_is_unknown():
    """Re-read of 69f8383, A: GitHub gives a merged pull request the state "unknown", and the unread
    return came first, so a merged S2 read as unread. `merged` is read before it now."""
    seen = copy.deepcopy(m06.observation())
    seen["s2"] |= {"merged": True, "mergeable_state": "unknown"}
    reading = shipped.record(seen, 28800.0)["F6_2"]
    assert reading["read"] is True and reading["held"] is False and reading["reasons"] == ["S2's pull request merged"]
    seen["s2"] |= {"merged": None}
    reading = shipped.record(seen, 28800.0)["F6_2"]
    assert reading["read"] is False and "whether S2's pull request merged was not read" in reading["reasons"][0]
    # Not merged and still unknown is GitHub still computing: unread, as before.
    seen["s2"] |= {"merged": False}
    assert shipped.record(seen, 28800.0)["F6_2"]["read"] is False


def test_refused_first_means_refused_for_the_planted_fault():
    """Re-read of 69f8383, B: any failure from the App counted as "refused first". At M06 every head failed
    on the hidden bypass_actors, so a head would have read as refused for seats it was never checked on."""
    seen = copy.deepcopy(m06.observation())
    first = seen["s3"]["first_pr"]["commits"][0]
    first["check_runs"][0]["refused"] = ["the repository's ruleset is the export"]
    reading = shipped.record(seen, 28800.0)["F6_1"]
    assert reading["held"] is False and "not for its planted fault" in reading["reasons"][0]
    assert shipped.SEAT_CHECK in reading["reasons"][0] and shipped.GOLDENS_CHECK in reading["reasons"][0]
    # Refused for the planted faults and for something else as well is still refused for them.
    first["check_runs"][0]["refused"] = [shipped.SEAT_CHECK, shipped.GOLDENS_CHECK, "the repository's ruleset is the export"]
    assert shipped.record(seen, 28800.0)["F6_1"]["held"] is True
    # The App's reasons not read is unread, not held.
    first["check_runs"][0]["refused"] = None
    reading = shipped.record(seen, 28800.0)["F6_1"]
    assert reading["read"] is False and "reasons for refusing the first commit were not read" in reading["reasons"][0]
    # Only the fault that is there is asked for: goldens present, seats null.
    first["goldens"] = m06.TWO
    first["check_runs"][0]["refused"] = [shipped.SEAT_CHECK]
    assert shipped.record(seen, 28800.0)["F6_1"]["held"] is True


def test_the_observer_reads_the_apps_reasons_from_its_check_runs_own_summary():
    from scripts import observe_template

    summary = f"- **{shipped.SEAT_CHECK}**: manifest.yaml: seat product is null; seat security is null\n- **{shipped.GOLDENS_CHECK}**: none"
    run = {"conclusion": "failure", "output": {"title": "2 refused", "summary": summary}}
    assert observe_template.refused_checks(run) == [shipped.SEAT_CHECK, shipped.GOLDENS_CHECK]
    assert observe_template.refused_checks({"conclusion": "success", "output": {"summary": "Every check passed."}}) == []
    assert observe_template.refused_checks({"conclusion": "failure", "output": {"summary": None}}) is None
    assert observe_template.refused_checks({"conclusion": "failure"}) is None


def test_each_github_reading_of_claim_6_says_which_viewpoint_it_was_ruled_on():
    """open.md row 3: the owner read `blocked` on S2 where CI's own token read `unstable`. The envelope now
    keeps the raw state and who asked, and rules on the App's reading where main's observer stored one."""
    own = copy.deepcopy(m06.observation())
    own["s2"]["mergeable_state"] = "unstable"  # as a pull request's own run, with no rights there, reads it
    alone = shipped.record(own, 28800.0)
    assert alone["F6_2"]["held"] is False and alone["F6_2"]["viewpoint"] == "anonymous"
    assert alone["F6_2"]["mergeable_state"] == "unstable" and alone["app_observation"] is None
    stored = {"run_id": "777", "read_at": "2026-10-06T11:45:00Z", "key": "observations/777.json",
              "template": {"s2": {**own["s2"], "mergeable_state": "blocked"}}}  # fmt: skip
    both = shipped.record(own, 28800.0, stored)
    assert both["F6_2"] == {"read": True, "held": True, "reasons": [], "viewpoint": "app", "mergeable_state": "blocked"}
    assert both["F6_1"]["viewpoint"] == both["F6_3"]["viewpoint"] == "anonymous"  # the App stored no S3
    assert both["app_observation"]["run_id"] == "777" and "viewpoint" not in both["F6_4"]
    # A record the App did not find is not preferred, and row 6's reading of it is unchanged.
    stored["template"]["s2"]["found"] = False
    assert shipped.record(own, 28800.0, stored)["F6_2"]["viewpoint"] == "anonymous"
    from src.verdict import gate, schema_errors

    recorded = json.loads((ROOT / "evals" / "history" / "827ee8bc014b28f588e9b8f3e1d4a947be885f26.json").read_text(encoding="utf-8"))
    assert schema_errors({**recorded, "template": both}) == []
    assert gate.template_reading({"template": both})[1] == "F6_2 held"


# --- the seeded relaxation (S0's third attempt; rulings/pr2-security.md item 8) ---

EXPORT_RULESET = json.loads((ROOT / "infra" / "ruleset" / "agent.json").read_text(encoding="utf-8"))


@pytest.fixture
def owner_check(github, monkeypatch):
    github["pages"].update({
        "/repos/agentkeel-studio/owner-check/installation": {"id": 77},
        "/repos/agentkeel-studio/owner-check/rulesets?includes_parents=false&per_page=100": [{"id": 24310403}],
        "/repos/agentkeel-studio/owner-check/rulesets/24310403": {**EXPORT_RULESET, "id": 24310403},
    })  # fmt: skip
    real = platform_check.gh

    def gh(path, *, method="GET", body=None, raw=False):
        if method == "PUT":
            github["sent"].append((method, path, body, os.environ.get("GITHUB_TOKEN")))
            if github.get("refuse"):
                raise urllib.error.HTTPError(path, github["refuse"], "Forbidden", {}, None)
            return {}
        return real(path, method=method, body=body, raw=raw)

    platform_check.gh = gh
    return github


def test_the_seeded_relaxation_asks_for_the_required_check_to_go_and_keeps_githubs_answer(owner_check, key):
    record = platform_check.relax_seed("owner-check", "agentkeel-studio", APP, key)
    assert record["status"] == 200 and record["ruleset"] == 24310403 and record["repository"] == "agentkeel-studio/owner-check"
    (path, body, token), = [(p, b, t) for method, p, b, t in owner_check["sent"] if method == "PUT"]
    assert path == "/repos/agentkeel-studio/owner-check/rulesets/24310403" and token == "token-for-administration+metadata"
    assert [rule["type"] for rule in body["rules"]] == ["deletion", "non_fast_forward", "pull_request"]  # the check is gone, nothing else
    assert "bypass_actors" not in body  # it asks for one thing
    minted = [b for method, p, b, _t in owner_check["sent"] if method == "POST" and p.endswith("/access_tokens")]
    assert minted == [{"repositories": ["owner-check"], "permissions": platform_check.PERMISSION_SETS["rulesets"]}]
    assert [method for method, *_ in owner_check["sent"]][-1] == "DELETE"  # the token is revoked after the one call


def test_a_refusal_by_github_is_recorded_as_githubs_not_raised(owner_check, key):
    owner_check["refuse"] = 403
    record = platform_check.relax_seed("owner-check", "agentkeel-studio", APP, key)
    assert record["status"] == 403 and record["ruleset"] == 24310403


@pytest.mark.parametrize("name, org, said", [
    ("premiere-desk", "agentkeel-studio", "on no other repository"),
    ("owner-check", "another-organisation", "on no other repository"),
    ("agent-template", "agentkeel-studio", "on no other repository"),
    ("../owner-check", "agentkeel-studio", "not an agent's name"),
    ("", "agentkeel-studio", "not an agent's name"),
])  # fmt: skip
def test_the_seeded_relaxation_cannot_be_pointed_at_another_repository(github, key, name, org, said):
    with pytest.raises(ValueError, match=said):
        platform_check.relax_seed(name, org, APP, key)
    assert github["sent"] == []  # refused before any token is asked for


def test_a_repository_whose_ruleset_does_not_bind_the_check_gets_no_call(owner_check, key):
    unbound = {**EXPORT_RULESET, "id": 24310403, "rules": [r for r in EXPORT_RULESET["rules"] if r["type"] != "required_status_checks"]}
    owner_check["pages"]["/repos/agentkeel-studio/owner-check/rulesets/24310403"] = unbound
    record = platform_check.relax_seed("owner-check", "agentkeel-studio", APP, key)
    assert record["status"] is None and "nothing to ask" in record["message"]
    assert not any(method == "PUT" for method, *_ in owner_check["sent"])


# --- a public App, installed by a stranger (rulings/pr2-security.md item 13a) -----


def test_a_strangers_installation_of_the_public_app_is_recorded_and_stops_nothing():
    """`agentkeel-upgrades` is installed on two accounts, so GitHub requires it to be public, and anybody
    may install it on an account of their own. That must not stop every keyed job."""
    grant, environment = s0("grant.json"), s0("environment_upgrades_as_ruled.json")
    assert grant["agentkeel-upgrades"]["public"] is True
    assert platform_check.grant_errors(s0("upgrades_on_a_strangers_account.json"), environment, grant) == []
    # And only for the App the grant calls public: the checking App on an unnamed account is still refused.
    assert "public" not in grant["agentkeel-platform"]
    errors = platform_check.grant_errors(s0("installation_on_personal_account.json"), s0("environment_as_ruled.json"), grant)
    assert any("andaro74" in e for e in errors)
    # A stranger's installation that holds more than the App's own permissions is still said.
    more = {**s0("upgrades_on_a_strangers_account.json"), "permissions": {"contents": "write", "administration": "write"}}
    assert platform_check.grant_errors(more, environment, grant) == []  # their account, their grant: not this platform's to refuse


@pytest.mark.parametrize("suspended_at", [None, "2026-10-02T00:00:00Z"])
def test_the_reader_of_the_grant_mints_nothing_on_a_strangers_installation(github, key, monkeypatch, suspended_at):
    """security-reviewer BLOCK 1 on M07 PR 2: `read_grant` minted a metadata token on every installation,
    a stranger's included, and listed their repositories into an artifact; and a stranger who suspended
    their installation stopped every keyed job. Through `check_grant`, with the stranger's beside ours."""
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    monkeypatch.setenv("GITHUB_TOKEN", "the-jobs-own-token")
    ours = s0("upgrades_org_as_ruled.json")
    theirs = {**s0("upgrades_on_a_strangers_account.json"), "suspended_at": suspended_at}
    live_pages(github, ours, ours["permissions"], s0("environment_upgrades_as_ruled.json"), others=(theirs,))
    read, errors = platform_check.check_grant("agentkeel-upgrades", key)
    assert errors == []
    assert read["not_ours"] == ["a-stranger"]
    mine, stranger = read["installations"]
    assert mine["repositories"] == sorted(ours["repositories"])
    assert stranger["account"]["login"] == "a-stranger" and stranger["repositories"] is None  # not read: no token
    minted = [path for method, path, _b, _t in github["sent"] if method == "POST"]
    assert minted == [f"/app/installations/{ours['id']}/access_tokens"]  # one token, on the account the grant names


def test_the_environment_is_compared_when_only_unnamed_accounts_hold_the_app(github, key, monkeypatch):
    """security-reviewer 3 on M07 PR 2: inside an installation's pass alone, a public App read with only
    a stranger's installation never had its key's environment compared."""
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    monkeypatch.setenv("GITHUB_TOKEN", "the-jobs-own-token")
    theirs = s0("upgrades_on_a_strangers_account.json")
    environment = {**s0("environment_upgrades_as_ruled.json"), "can_admins_bypass": True}
    live_pages(github, theirs, theirs["permissions"], environment)
    _read, errors = platform_check.check_grant("agentkeel-upgrades", key)
    assert any("can_admins_bypass" in e for e in errors)
    assert not [1 for method, *_ in github["sent"] if method == "POST"]


def test_every_page_of_the_apps_installations_is_read(github, key, monkeypatch):
    """security-reviewer 2 on M07 PR 2: one page of a public App's list can leave ours unread."""
    fixture = s0("grant.json")
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: fixture)
    monkeypatch.setenv("GITHUB_TOKEN", "the-jobs-own-token")
    ours = {**s0("upgrades_org_as_ruled.json"), "permissions": {"contents": "write", "administration": "write", "metadata": "read"}}
    theirs = s0("upgrades_on_a_strangers_account.json")
    live_pages(github, theirs, s0("upgrades_org_as_ruled.json")["permissions"], s0("environment_upgrades_as_ruled.json"),
               others=tuple({**theirs, "id": 1000 + n, "account": {"login": f"stranger-{n}"}} for n in range(99)))  # fmt: skip
    github["pages"]["/app/installations?per_page=100&page=2"] = [{k: v for k, v in ours.items() if k != "repositories"}]
    github["pages"]["/installation/repositories?per_page=100&page=1"] = {
        "total_count": len(ours["repositories"]), "repositories": [{"name": n} for n in ours["repositories"]]}  # fmt: skip
    _read, errors = platform_check.check_grant("agentkeel-upgrades", key)
    assert any("administration" in e for e in errors)  # ours, widened, on the second page: found and refused


def test_the_seeded_relaxation_is_made_once(owner_check, key, tmp_path):
    """security-reviewer 6 on M07 PR 2: once the run file on main records the attempt, it is refused."""
    import yaml as _yaml

    seed = _yaml.safe_load((platform_check.ROOT / platform_check.SEED_RUN_FILE).read_text(encoding="utf-8"))
    seed["observed"] = [*(seed.get("observed") or []),
                        {"what": "the App's token asked to relax owner-check's ruleset", "repository": seed["repository"], "run": 1}]  # fmt: skip
    (tmp_path / platform_check.SEED_RUN_FILE).parent.mkdir(parents=True)
    (tmp_path / platform_check.SEED_RUN_FILE).write_text(_yaml.safe_dump(seed), encoding="utf-8")
    with pytest.raises(ValueError, match="made once"):
        platform_check.relax_seed("owner-check", "agentkeel-studio", APP, key, root=tmp_path)
    assert owner_check["sent"] == []


def test_no_token_is_minted_for_an_account_the_caller_does_not_name(github, key):
    with pytest.raises(ValueError, match="not agentkeel-studio's"):
        platform_check.app_token(5200001, "agentkeel-studio", key, "a-stranger/their-own-repository", "open")
    assert github["sent"] == []
