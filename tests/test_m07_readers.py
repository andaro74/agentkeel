"""M07 PR 2's readers, beyond what the seed tests ask of them (SPEC/07 §6).

The seed tests (`tests/test_m07_seeds.py`) hand each fixture to its reader and ask for the planted
refusal. These hold the rest: the arms a fixture does not reach, the unread cases, and the shapes the
observer writes. Nothing here calls AWS, a model or GitHub.
"""

from __future__ import annotations

import json
import os
import urllib.error
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
