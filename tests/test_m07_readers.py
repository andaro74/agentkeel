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
