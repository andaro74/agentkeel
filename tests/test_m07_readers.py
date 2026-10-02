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


def live_pages(github, installation: dict[str, Any], registered: dict[str, str], environment: dict[str, Any]) -> None:
    name = environment["name"]
    github["pages"].update({
        "/app": {"slug": installation["app_slug"], "id": installation["app_id"], "permissions": registered},
        "/app/installations?per_page=100": [{k: v for k, v in installation.items() if k != "repositories"}],
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
