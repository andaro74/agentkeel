"""`scripts/observe_upgrade.py`: what it reads and how it lays the records side by side (SPEC/07 §4).

The observer writes raw records and decides nothing; these tests hand it a stand-in GitHub, a stand-in
bucket and stand-in AWS answers, and then let `build`'s own reader rule on what it wrote, so the two
are held to one shape. Nothing here calls AWS, GitHub or Grafana.
"""

from __future__ import annotations

import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from scripts import observe_upgrade as observer
from src.verdict import ROOT, plants, upgrade

from .test_m07_upgrade import BARS, GOLDENS, HISTORY, SEATS, THRESHOLDS

APP, OPENER, WATCHER = 5144253, 5200001, 5200002
ORG = "agentkeel-studio"
REPO = f"{ORG}/owner-check"
BOT = {"login": "agentkeel-upgrades[bot]", "type": "Bot"}
OWNER = {"login": "andaro74", "type": "User"}
SUMMARY = f"- **{upgrade.SEAT_CHECK}**: manifest.yaml: seat product is null\n- **{upgrade.GOLDENS_CHECK}**: goldens/: none"


class FakeGitHub(observer.GitHub):
    """Answers from `pages`, keyed by repository and path; every request is recorded with who asked."""

    def __init__(self, pages: dict[tuple[str, str], Any], viewpoint: str = "anonymous") -> None:
        self.viewpoint, self.organisation = viewpoint, ORG
        self.tokens, self.unminted, self.job_token = {}, {}, "the-jobs-own-token"
        self.pages, self.asked = pages, []

    def token(self, repository: str) -> str | None:
        return f"app-token-for-{repository}" if self.viewpoint == "app" and repository.startswith(f"{ORG}/") else self.job_token

    def __call__(self, repository: str, path: str, *, raw: bool = False) -> Any:
        self.asked.append((repository, path, self.token(repository)))
        base = path.split("&per_page")[0].split("?per_page")[0]
        if (repository, base) not in self.pages:
            raise urllib.error.HTTPError(f"{repository}{path}", 404, "Not Found", {}, None)
        return self.pages[(repository, base)]


def check(conclusion: str, app: int = APP, summary: str | None = None) -> dict[str, Any]:
    return {"name": "platform-check", "app": {"id": app, "slug": "agentkeel-platform"}, "conclusion": conclusion,
            "completed_at": "2026-10-06T09:30:00Z", "output": {"title": "t", "summary": summary}}  # fmt: skip


def pull_pages(number: int = 3, *, repository: str = REPO, author: dict[str, Any] = BOT, files: list[str] | None = None,
               merged: bool = True, body: str = "") -> dict[tuple[str, str], Any]:  # fmt: skip
    files = files or ["manifest.yaml", "server.py"]
    return {
        (repository, f"/pulls/{number}"): {
            "user": author, "created_at": "2026-10-06T09:20:00Z", "draft": False, "state": "closed", "merged": merged,
            "merged_at": "2026-10-06T10:00:00Z" if merged else None, "merge_commit_sha": "4" * 40,
            "head": {"sha": "1" * 40}, "base": {"sha": "0" * 40, "ref": "main"}, "mergeable_state": "unknown", "body": body},
        (repository, f"/issues/{number}"): {"performed_via_github_app": {"id": OPENER, "slug": "agentkeel-upgrades"}
                                            if author is BOT else None},
        # As GitHub returns an App's API commit: its bot as author, GitHub's signer as committer, verified.
        (repository, f"/pulls/{number}/commits"): [{"sha": "1" * 40, "author": author, **(
            {"committer": {"login": "web-flow", "type": "User"}, "commit": {"verification": {"verified": True}}}
            if author is BOT else {})}],
        (repository, f"/pulls/{number}/files"): [{"filename": f} for f in files],
        (repository, f"/commits/{'1' * 40}"): {"files": [{"filename": f} for f in files]},
        (repository, f"/commits/{'1' * 40}/check-runs"): {"check_runs": [check("success")]},
        (repository, "/commits?sha=main&since=2026-10-06T09:20:00Z&until=2026-10-06T10:00:00Z"): [
            {"sha": "4" * 40, "author": OWNER}, {"sha": "5" * 40, "author": OWNER, "committer": OWNER,
                                                 "commit": {"verification": {"verified": False}}}],
        (repository, f"/commits/{'5' * 40}"): {"files": [{"filename": "agent.py"}]},
    }  # fmt: skip


# --- one pull request, as GitHub records it ------------------------------------------------


def test_a_pull_request_is_written_with_who_opened_it_its_files_its_commits_and_its_checks():
    gh = FakeGitHub(pull_pages())
    pull = observer.pull_record(gh, REPO, 3, APP)
    assert pull["found"] is True and pull["error"] is None
    assert pull["author"] == {"login": "agentkeel-upgrades[bot]", "type": "Bot", "app_id": OPENER, "app_slug": "agentkeel-upgrades"}
    assert pull["files"] == ["manifest.yaml", "server.py"] and pull["merged"] is True and pull["merge_commit_sha"] == "4" * 40
    signer = {"login": "web-flow", "type": "User", "app_id": None, "app_slug": None}
    # The committer and GitHub's verification are written raw beside the author (cold review F5 on M07 PR 2:
    # "no person's edit" rested on the author's login). build rules on them from M07 PR 3.
    assert pull["commits"] == [{"sha": "1" * 40, "author": {"login": "agentkeel-upgrades[bot]", "type": "Bot", "app_id": None,
                                                           "app_slug": None}, "committer": signer, "verified": True,
                                "files": ["manifest.yaml", "server.py"]}]  # fmt: skip
    assert pull["required_on_head"] == {"platform-check": "success"}
    # The merge commit itself is the pull request's own. Another commit on the branch meanwhile is written
    # with its committer and verification too, so build can hold it to the same rule.
    owner = {"login": "andaro74", "type": "User", "app_id": None, "app_slug": None}
    assert pull["default_branch_commits_between"] == [
        {"sha": "5" * 40, "author": owner, "committer": owner, "verified": False, "files": ["agent.py"]}]
    # build rules on it as written: held, once it carries its trigger.
    observer.with_trigger(pull, {"at": "2026-10-06T09:00:00Z"})
    pull["workflows_sha256_changed"] = False
    reading = upgrade.pull_reading("platform", pull, {"id": OPENER, "slug": "agentkeel-upgrades"}, BARS, "2026-10-06T12:00:00Z")
    assert reading["held"] is True and reading["arrived_s"] == 1200.0


def test_a_pull_request_that_cannot_be_read_is_written_with_its_error_and_build_reads_it_unread():
    pull = observer.pull_record(FakeGitHub({}), REPO, 3, APP)
    assert pull["found"] is False and "HTTPError" in pull["error"]
    assert observer.pull_record(FakeGitHub({}), REPO, None, APP)["found"] is False  # an entry the human left unfilled
    assert upgrade.pull_reading("platform", pull, {"id": OPENER, "slug": "agentkeel-upgrades"}, BARS, "t")["read"] is False


def test_in_agentkeel_the_checks_read_are_the_ones_the_exported_ruleset_requires():
    pages = pull_pages(41, repository=observer.PLATFORM, files=["agents/refagent/manifest.yaml"])
    pages[(observer.PLATFORM, f"/commits/{'1' * 40}/check-runs")] = {"check_runs": [
        {"name": "evals", "app": {"id": 15368}, "conclusion": "success"},
        {"name": "checks", "app": {"id": 15368}, "conclusion": "failure"}]}  # fmt: skip
    pull = observer.pull_record(FakeGitHub(pages), observer.PLATFORM, 41, APP)
    assert pull["required_on_head"] == {"checks": "failure", "cold-review-ruling": None, "evals": "success",
                                        "ruling-cited": None, "two-key": None}  # fmt: skip


def test_the_trigger_of_a_platform_upgrade_is_githubs_push_record_not_the_commits_date():
    template = f"{ORG}/agent-template"
    pages = {
        (template, "/activity?activity_type=push"): [
            {"before": "b" * 40, "after": "c" * 40, "timestamp": "2026-10-06T09:05:00Z"},  # a later push, same version
            {"before": "a" * 40, "after": "b" * 40, "timestamp": "2026-10-06T09:00:00Z"},
        ],
        (template, f"/contents/manifest.yaml?ref={'a' * 40}"): "platform_version: m06\n",
        (template, f"/contents/manifest.yaml?ref={'b' * 40}"): "platform_version: m07\n",
        (template, f"/contents/manifest.yaml?ref={'c' * 40}"): "platform_version: m07\n",
    }  # fmt: skip
    trigger = observer.template_push(FakeGitHub(pages), ORG, "m07")
    assert trigger["at"] == "2026-10-06T09:00:00Z" and trigger["after"] == "b" * 40 and trigger["error"] is None
    assert observer.template_push(FakeGitHub(pages), ORG, "m08")["at"] is None  # no push moved it there: unread
    assert "HTTPError" in observer.template_push(FakeGitHub({}), ORG, "m07")["error"]


def test_a_run_is_a_trigger_only_when_it_is_that_workflow_on_main():
    pages = {(observer.PLATFORM, "/actions/runs/9"): {"id": 9, "created_at": "2026-10-06T09:00:00Z", "event": "schedule",
                                                      "head_branch": "main", "path": ".github/workflows/model-watch.yml"}}  # fmt: skip
    assert observer.workflow_run(FakeGitHub(pages), "9", "model-watch.yml")["at"] == "2026-10-06T09:00:00Z"
    wrong = observer.workflow_run(FakeGitHub(pages), "9", "deploy.yml")
    assert wrong["at"] is None and "is not deploy.yml on main" in wrong["error"]
    pages[(observer.PLATFORM, "/actions/runs/9")]["head_branch"] = "m07-pr2"
    assert observer.workflow_run(FakeGitHub(pages), "9", "model-watch.yml")["at"] is None
    assert observer.workflow_run(FakeGitHub(pages), None, "model-watch.yml")["at"] is None


# --- the viewpoint ---------------------------------------------------------------------------


def test_as_the_app_each_repository_of_the_organisations_is_read_under_its_own_token():
    """And `agentkeel` itself, where the observer App is not installed, under the job's own."""
    gh = FakeGitHub({**pull_pages(), (observer.PLATFORM, "/actions/runs/9"): {"id": 9, "path": "x", "head_branch": "main"}}, "app")
    observer.pull_record(gh, REPO, 3, APP)
    observer.workflow_run(gh, 9, "deploy.yml")
    assert {token for repository, _path, token in gh.asked if repository == REPO} == {f"app-token-for-{REPO}"}
    assert {token for repository, _path, token in gh.asked if repository == observer.PLATFORM} == {"the-jobs-own-token"}


def test_the_real_reader_mints_first_for_the_repositories_named_and_does_not_keep_the_key(monkeypatch):
    """security-reviewer 12 on M07 PR 2: the one keyed job with no keyless job before it. Every token is
    minted before anything is read, read-only, one per repository named; the key is not kept."""
    minted: list[tuple[Any, ...]] = []
    from scripts import platform_check

    def mint(*args: Any) -> str:
        if args[3].endswith("/gone"):
            raise urllib.error.HTTPError("x", 404, "Not Found", {}, None)
        minted.append(args)
        return f"observer-token-for-{args[3]}"

    monkeypatch.setattr(platform_check, "identity", lambda: (ORG, APP))
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: {"agentkeel-observer": {"app_id": WATCHER}})
    monkeypatch.setattr(platform_check, "app_token", mint)
    seen: list[str | None] = []
    monkeypatch.setattr(platform_check, "gh", lambda path, raw=False: seen.append(__import__("os").environ.get("GITHUB_TOKEN")) or {})
    monkeypatch.setenv("GITHUB_TOKEN", "the-jobs-own-token")
    gh = observer.GitHub("app", "the-key", [REPO, f"{ORG}/gone", "someone-else/their-repo", observer.PLATFORM])
    # Once per organisation repository, the read-only set, before any read; nobody else's account is asked.
    assert minted == [(WATCHER, ORG, "the-key", REPO, "observe")] and seen == []
    assert "the-key" not in repr(vars(gh)) and not hasattr(gh, "key")
    gh(REPO, "/pulls/1")
    gh(REPO, "/pulls/2")
    gh(observer.PLATFORM, "/actions/runs/9")
    assert len(minted) == 1  # nothing is minted later
    assert seen == [f"observer-token-for-{REPO}", f"observer-token-for-{REPO}", "the-jobs-own-token"]
    assert __import__("os").environ["GITHUB_TOKEN"] == "the-jobs-own-token"
    # A repository no token was minted for is unread, with the reason: never read under another token.
    for name, said in ((f"{ORG}/gone", "HTTPError"), (f"{ORG}/never-named", "no run file on main names it")):
        with pytest.raises(KeyError, match=said):
            gh(name, "/pulls/1")
    assert observer.pull_record(gh, f"{ORG}/never-named", 1, APP)["found"] is False
    anonymous = observer.GitHub("anonymous")
    anonymous(REPO, "/pulls/1")
    assert seen[-1] == "the-jobs-own-token" and len(minted) == 1
    # security-reviewer 14 on M07 PR 3: the tokens are revoked when the observation is done, not left an hour.
    revoked: list[str] = []
    monkeypatch.setattr(platform_check, "revoke", revoked.append)
    gh.close()
    assert revoked == [f"observer-token-for-{REPO}"] and gh.tokens == {}
    with pytest.raises(KeyError):
        gh(REPO, "/pulls/1")  # and nothing is read under a revoked token
    anonymous.close()
    assert len(revoked) == 1  # the job's own token is not this script's to revoke


def test_the_repositories_minted_for_are_the_ones_the_run_files_name_and_the_template():
    named = observer.named_repositories()
    assert f"{ORG}/agent-template" in named and REPO in named and observer.PLATFORM in named
    assert all(name.count("/") == 1 for name in named)


def test_as_the_app_no_agent_repositorys_tree_is_fetched_or_packed(monkeypatch):
    """The digests are the pull request's run's, under no key; build never takes them from the stored record."""
    def refuse(*args: Any) -> None:
        raise AssertionError("packed beside the App's tokens")

    monkeypatch.setattr(observer, "agent_digest", refuse)
    monkeypatch.setattr(observer, "refagent_digest", refuse)
    monkeypatch.setattr(observer, "observed", lambda name: [{"repository": REPO, "pull_request": 3}]
                        if name == "f7_1_platform_upgrade.yaml" else [])  # fmt: skip
    monkeypatch.setattr(observer, "template_push", lambda gh, org, version: {"at": "2026-10-06T09:00:00Z"})
    pages = {**pull_pages(), (REPO, f"/contents/manifest.yaml?ref={'1' * 40}"): "name: owner-check\nplatform_version: m07\n",
             (REPO, f"/contents/manifest.yaml?ref={'4' * 40}"): "name: owner-check\nplatform_version: m07\n"}  # fmt: skip
    observation = observer.blank("app")
    observer.read_github(FakeGitHub(pages, "app"), observation)
    live = observation["s1"]["lives"][REPO]
    assert live["tree_digest"] is None and live["error"] == observer.NOT_PACKED and live["agent"] == "owner-check"


class Redirecting:
    """An opener that answers the first request with GitHub's redirect and the second with the bytes."""

    def __init__(self, location: str | None) -> None:
        self.location, self.requests = location, []

    def open(self, request: Any, timeout: int = 0) -> Any:
        self.requests.append((request.full_url, dict(request.header_items())))
        if len(self.requests) == 1 and self.location:
            raise urllib.error.HTTPError(request.full_url, 302, "Found", {"Location": self.location}, None)
        return __import__("io").BytesIO(b"the bytes")


def test_an_artifact_is_fetched_from_the_storage_host_with_no_credential():
    """security-reviewer 12 on M07 PR 2: urllib carried the job's token to the host GitHub redirects to."""
    opener = Redirecting("https://storage.example/artifact.zip?sig=x")
    assert observer.download("https://api.github.com/repos/o/r/actions/artifacts/1/zip", "the-token", opener) == b"the bytes"
    (first, sent), (second, bare) = opener.requests
    assert first.startswith("https://api.github.com/") and sent == {"Authorization": "Bearer the-token"}
    assert second.startswith("https://storage.example/") and bare == {}
    # No redirect: the bytes come from the host that was asked, in one request.
    direct = Redirecting(None)
    assert observer.download("https://api.github.com/x", "the-token", direct) == b"the bytes" and len(direct.requests) == 1
    with pytest.raises(ValueError, match="not to an https address"):
        observer.download("https://api.github.com/x", "the-token", Redirecting("http://storage.example/a.zip"))
    # security-reviewer 15 on M07 PR 3: the first address is GitHub's API host or nothing is sent.
    for elsewhere in ("https://storage.example/a.zip", "https://api.github.com.example/x", "http://api.github.com/x"):
        nowhere = Redirecting(None)
        with pytest.raises(ValueError, match="not on GitHub's API host"):
            observer.download(elsewhere, "the-token", nowhere)
        assert nowhere.requests == []
    # The real opener never follows one by itself.
    assert observer._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://elsewhere.example/") is None


# --- the owner's test and the dispatch ---------------------------------------------------------


def test_the_owners_test_is_written_commit_by_commit_with_the_apps_own_reasons(monkeypatch):
    null_seats = "name: owner-check\nseats: {" + ", ".join(f"{s}: null" for s in SEATS) + "}\n"
    full_seats = "name: owner-check\nseats: {" + ", ".join(f"{s}: andaro74" for s in SEATS) + "}\n"
    contents = {
        f"/repos/{REPO}/contents/manifest.yaml?ref={'2' * 40}": null_seats,
        f"/repos/{REPO}/contents/goldens?ref={'2' * 40}": [],
        f"/repos/{REPO}/contents/manifest.yaml?ref={'3' * 40}": full_seats,
        f"/repos/{REPO}/contents/goldens?ref={'3' * 40}": [{"type": "file", "name": g["file"]} for g in GOLDENS],
        f"/repos/{REPO}/contents/goldens/g-001.yaml?ref={'3' * 40}": "kind: ordinary\nretired: null\n",
        f"/repos/{REPO}/contents/goldens/g-002.yaml?ref={'3' * 40}": "kind: trap\nretired: null\n",
    }  # fmt: skip
    monkeypatch.setattr(observer.observe_template, "gh", lambda path, raw=False: contents[path])
    pages = {
        (REPO, "/pulls/1"): {"merged": True, "merged_at": "2026-10-06T10:00:00Z", "merge_commit_sha": "4" * 40,
                             "head": {"sha": "3" * 40}, "mergeable_state": "unknown"},
        (REPO, "/pulls/1/commits"): [{"sha": "2" * 40}, {"sha": "3" * 40}],
        (REPO, f"/commits/{'2' * 40}/check-runs"): {"check_runs": [check("failure", summary=SUMMARY)]},
        (REPO, f"/commits/{'3' * 40}/check-runs"): {"check_runs": [check("success")]},
        (REPO, f"/commits/{'4' * 40}/check-runs"): {"check_runs": [check("success")]},
        (REPO, f"/contents/manifest.yaml?ref={'4' * 40}"): full_seats,
    }  # fmt: skip
    test = observer.read_owner_test(FakeGitHub(pages), {"repository": REPO, "pull_request": 1}, APP)
    assert test["found"] is True and test["agent_name"] == "owner-check" and test["merge_head_sha"] == "3" * 40
    assert test["commits"][0]["check_runs"][0]["refused"] == [upgrade.SEAT_CHECK, upgrade.GOLDENS_CHECK]
    assert test["commits"][1]["seats"]["security"] == "andaro74" and [g["kind"] for g in test["commits"][1]["goldens"]] == ["ordinary", "trap"]
    # GitHub's half alone leaves the deploy unread; with AWS's records laid beside it, build holds it.
    observation = {**observer.blank("anonymous"), "s0": {"owner_test": test, "dispatch": None, "relaxation": None}}
    observation["bucket"] = {"agents": {"owner-check": {"answers": [
        {"key": f"envelopes/agents/owner-check/{'4' * 40}.json", "commit": "4" * 40, "last_modified": "2026-10-06T10:41:00Z",
         "run_id": "9", "passed": True, "goldens": {"g-001": {"pass": True}}}], "retired": None, "bundles": []}}}  # fmt: skip
    observation["aws"] = {"registry": {"owner-check": {"name": "owner-check", "repository": REPO}}, "runtimes": {}, "images": {}}
    observation["panel1"] = {"frame": {"results": {"A": {"frames": [{"schema": {"fields": [{"name": "name"}]},
                                                                      "data": {"values": [["owner-check", "refagent"]]}}]}}}}  # fmt: skip
    runs = FakeGitHub({(observer.PLATFORM, "/actions/runs/9"): {"id": 9, "conclusion": "success", "updated_at": "2026-10-06T10:40:00Z"}})
    observer.compose(observation, runs)
    reading = upgrade.owner_test(observation["s0"]["owner_test"], APP, BARS, "2026-10-06T12:00:00Z")
    assert reading == {"read": True, "held": True, "reasons": []}


def test_the_dispatch_already_recorded_is_read_from_githubs_jobs_as_refused():
    raw = json.loads((ROOT / "milestones/M07/runs/f7_0_dispatch_from_branch.json").read_text(encoding="utf-8"))
    pages = {
        (observer.PLATFORM, f"/actions/runs/{raw['run']}"): {"event": "workflow_dispatch", "head_branch": "m07-pr1",
                                                              "path": ".github/workflows/platform-check.yml",
                                                              "created_at": "2026-10-02T04:12:44Z"},
        (observer.PLATFORM, f"/actions/runs/{raw['run']}/jobs"): {"jobs": [
            {"id": 100 + n, "name": j["name"], "conclusion": j["conclusion"], "runner_name": j["runner_name"],
             "steps": [{"name": s} for s in j["steps"]]} for n, j in enumerate(raw["jobs"])]},
        # GitHub's own annotations on the refused job (check run 110702392789, read 2026-10-02).
        (observer.PLATFORM, "/check-runs/102/annotations"): [
            {"message": 'Branch "m07-pr1" is not allowed to deploy to platform-app due to environment protection rules.'},
            {"message": "The deployment was rejected or didn't satisfy other protection rules."}],
    }  # fmt: skip
    seen = observer.read_dispatch(FakeGitHub(pages), {"run": raw["run"]})
    assert [(j["name"].split()[0], j["steps"]) for j in seen["jobs"]] == [("find", 8), ("evaluate", 11), ("post", 0)]
    assert seen["jobs"][0]["annotations"] == [] and len(seen["jobs"][2]["annotations"]) == 2  # asked for the failed job only
    assert upgrade.dispatch_from_a_branch(seen) == {"read": True, "held": True, "reasons": []}
    # Annotations that could not be read are unread, not "none": the refusal is GitHub's word, never inferred.
    del pages[(observer.PLATFORM, "/check-runs/102/annotations")]
    unread = observer.read_dispatch(FakeGitHub(pages), {"run": raw["run"]})
    assert unread["jobs"][2]["annotations"] is None and upgrade.dispatch_from_a_branch(unread)["read"] is False


def test_the_relaxation_is_written_as_records_and_build_compares_their_times(monkeypatch):
    """Cold review F6 on M07 PR 2: the observer said which pass was "after the restore" and what merged
    meanwhile. It now writes each record with GitHub's own time and no comparison; build makes them."""
    export = json.loads((ROOT / "infra" / "ruleset" / "agent.json").read_text(encoding="utf-8"))
    refused = f"- **{upgrade.RULESET_CHECK}**: rules differs from live ruleset 24310403"
    passed = {**check("success"), "completed_at": "2026-10-06T10:40:00Z"}
    pages = {
        (observer.PLATFORM, "/actions/runs/5"): {"id": 5, "path": ".github/workflows/platform-check.yml", "head_branch": "main",
                                                 "event": "workflow_dispatch", "created_at": "2026-10-06T10:00:00Z"},
        (REPO, "/pulls/7"): {"head": {"sha": "5" * 40}},
        (REPO, f"/commits/{'5' * 40}/check-runs"): {"check_runs": [check("failure", summary=refused)]},
        (REPO, "/pulls?state=all&sort=updated&direction=desc"): [
            {"number": 7, "head": {"sha": "5" * 40}, "merged_at": None},
            {"number": 1, "head": {"sha": "3" * 40}, "merged_at": "2026-10-02T14:39:32Z"}],
        (REPO, ""): {"default_branch": "main"},
        (REPO, "/branches/main"): {"commit": {"sha": "4" * 40}},
        (REPO, f"/commits/{'3' * 40}/check-runs"): {"check_runs": [check("success")]},
        (REPO, f"/commits/{'4' * 40}/check-runs"): {"check_runs": [passed, check("success", app=15368)]},
        # As GitHub returns it to a caller that cannot administer it: no bypass_actors.
        (REPO, "/rulesets/24310403"): {"id": 24310403, **{k: v for k, v in export.items() if k != "bypass_actors"},
                                       "updated_at": "2026-10-06T10:30:00Z", "created_at": "2026-10-01T13:06:00Z"},
    }  # fmt: skip
    answer = {"status": 200, "ruleset": 24310403, "at": "2026-10-06T10:00:20Z", "repository": REPO}
    monkeypatch.setattr(observer, "artifact_json", lambda gh, run, name: answer if (run, name) == (5, "relax-seed") else None)
    seen = observer.read_relaxation(FakeGitHub(pages), {"repository": REPO, "run": 5, "pull_request": 7}, APP)
    assert seen["error"] is None and seen["asked"]["at"] == "2026-10-06T10:00:00Z"
    # Raw: every App success on a head, before the call or after; every merge, whenever it was.
    assert seen["app_passes"] == [{"sha": "3" * 40, "completed_at": "2026-10-06T09:30:00Z"},
                                  {"sha": "4" * 40, "completed_at": "2026-10-06T10:40:00Z"}]  # fmt: skip
    assert seen["merges"] == [{"number": 1, "merged_at": "2026-10-02T14:39:32Z"}]
    assert seen["ruleset"]["updated_at"] == "2026-10-06T10:30:00Z" and seen["ruleset"]["bypass_actors"] is None
    assert not {"passed_after_restore", "merges_between"} & set(seen)  # the comparisons it no longer makes
    reading = upgrade.relaxation(seen, APP, "2026-10-06T12:00:00Z")
    assert reading["held"] is True and reading["outcome"] == "detected" and reading["restored_at"] == "2026-10-06T10:30:00Z"
    # A run that is not platform-check.yml on main gives the call no time, and build reads that as unread.
    pages[(observer.PLATFORM, "/actions/runs/5")]["head_branch"] = "m07-pr3"
    other = observer.read_relaxation(FakeGitHub(pages), {"repository": REPO, "run": 5, "pull_request": 7}, APP)
    assert other["asked"]["at"] is None and upgrade.relaxation(other, APP, "2026-10-06T12:00:00Z")["read"] is False
    # A ruleset that cannot be read is written with its error; a refusal is read from the answer alone.
    del pages[(REPO, "/rulesets/24310403")]
    unread = observer.read_relaxation(FakeGitHub(pages), {"repository": REPO, "run": 5, "pull_request": 7}, APP)
    assert "HTTPError" in unread["ruleset"]["error"]
    answer["status"] = 403
    refused_by_github = observer.read_relaxation(FakeGitHub({}), {"repository": REPO, "run": 5, "pull_request": 7}, APP)
    assert refused_by_github["asked"] is None and upgrade.relaxation(refused_by_github, APP, None)["outcome"] == "refused"


def test_the_run_files_as_they_stand_name_every_attempt_and_each_is_looked_up(monkeypatch):
    """At M07's close the run files name every attempt: S0's three, S1's two pull requests, the retirement,
    the swap and the rollback on the fallback. Each is looked up, and nothing else is. (At PR 3 this test held
    that two were named; it failed on the close's first run, 37147871497, because the entries had been
    written and the test had not: the suite had not been read to its end before the push.)"""
    asked: list[str] = []
    monkeypatch.setattr(observer, "read_dispatch", lambda gh, entry: asked.append(str(entry["run"])) or {"found": True})
    monkeypatch.setattr(observer, "read_owner_test", lambda gh, entry, app: asked.append(
        f"{entry['repository']}#{entry['pull_request']}") or {"found": True})  # fmt: skip
    monkeypatch.setattr(observer, "read_relaxation", lambda gh, entry, app: asked.append(
        f"relaxation {entry['run']} on {entry['repository']}#{entry['pull_request']}") or {"found": True})  # fmt: skip
    observation = observer.blank("anonymous")
    observer.read_github(FakeGitHub({}), observation)
    assert asked == ["36963543726", "agentkeel-studio/owner-check#1",
                     "relaxation 37123843294 on agentkeel-studio/owner-check#4"]  # fmt: skip
    assert observation["s0"]["owner_test"] == {"found": True} and observation["s0"]["relaxation"] == {"found": True}
    # The fake holds no pull request, so each is recorded as asked for and not found: the names are the run files'.
    assert [p["repository"] for p in observation["s1"]["pulls"]] == ["agentkeel-studio/owner-check",
                                                                    "agentkeel-studio/window-check"]  # fmt: skip
    assert observation["s2"]["pull"]["repository"] == "agentkeel-studio/owner-check"
    assert observation["s2"]["pull"]["pull_request"] == 6 and observation["s2"]["pull"]["trigger"]["run"] == 37128759405
    swap, back = observation["s3"]["swap"], observation["s3"]["rollback"]
    assert (swap["repository"], swap["pull_request"]) == ("andaro74/agentkeel", 43)
    assert (back["repository"], back["pull_request"], back["fallback"]) == ("agentkeel-studio/window-check", 3, True)


# --- the bucket, AWS and the composition ---------------------------------------------------------


class Bucket:
    def __init__(self, objects: dict[str, tuple[str, Any]], refuse_prefix: str | None = None) -> None:
        self.objects, self.refuse_prefix = objects, refuse_prefix

    def get_paginator(self, _name: str) -> Any:
        bucket = self

        class Pages:
            def paginate(self, Bucket, Prefix):  # noqa: N803 - boto3's names
                if bucket.refuse_prefix and Prefix.startswith(bucket.refuse_prefix):
                    raise RuntimeError("AccessDenied")
                return [{"Contents": [{"Key": key, "LastModified": datetime.fromisoformat(when).replace(tzinfo=UTC)}
                                      for key, (when, _body) in sorted(bucket.objects.items()) if key.startswith(Prefix)]}]

        return Pages()

    def get_object(self, Bucket, Key):  # noqa: N803
        body = json.dumps(self.objects[Key][1]).encode()
        return {"Body": type("B", (), {"read": lambda self: body})()}


RUN_URL = "https://github.com/andaro74/agentkeel/actions/runs/9"
GONE = {"answered": False, "error": "ResourceNotFoundException", "at": "2026-10-05T10:01:00Z"}
OBJECTS = {
    f"envelopes/agents/premiere-desk/{'c' * 40}.json": ("2026-10-04T08:00:00", {"run_url": RUN_URL, "goldens": {"g-001": {"pass": True}}}),
    "envelopes/agents/premiere-desk/retired.json": ("2026-10-05T10:02:00", {"runtime_arn": "arn:x/agentkeel_premiere_desk-1",
                                                                            "commit": "d" * 40, "invocation": GONE}),
    f"bundles/premiere-desk/{'c' * 40}.tar": ("2026-10-04T07:59:00", {}),
    f"bundles/premiere-desk/{'c' * 40}.cosign.json": ("2026-10-04T07:59:00", {}),
}  # fmt: skip


def test_the_bucket_is_listed_agent_by_agent_and_a_retirement_record_is_not_an_answer_record():
    seen = observer.read_bucket(Bucket(OBJECTS))
    mine = seen["agents"]["premiere-desk"]
    assert [a["commit"] for a in mine["answers"]] == ["c" * 40] and mine["answers"][0]["run_id"] == "9"
    assert mine["retired"]["invocation"] == GONE  # written after the deletion, and never counted as the agent answering
    assert [b["key"] for b in mine["bundles"]] == [f"bundles/premiere-desk/{'c' * 40}.tar"]
    # Until the security account's stack carries bundles/, the prefix is refused: unread, and said so.
    refused = observer.read_bucket(Bucket(OBJECTS, refuse_prefix="bundles/"))
    assert refused["agents"]["premiere-desk"]["bundles_error"] and refused["error"] is None
    assert "AccessDenied" in observer.read_bucket(Bucket(OBJECTS, refuse_prefix="envelopes/"))["error"]


def retirement_observation(**bucket_kwargs: Any) -> dict[str, Any]:
    observation = observer.blank("anonymous")
    observation["s2"] = {"pull": None, "retirement": {
        "agent": "premiere-desk", "pull_request": {"merged": True, "merged_at": "2026-10-05T09:50:00Z"},
        "delete_event": None, "get_runtime": None, "invocation": None, "answer_records": None, "bundle": None,
        "registry_row": None}}  # fmt: skip
    observation["bucket"] = observer.read_bucket(Bucket(OBJECTS, **bucket_kwargs))
    observation["aws"] = {
        "registry": {"premiere-desk": {"name": "premiere-desk", "retired_at": "2026-10-05T10:00:30Z",
                                       "retiring_arn": "arn:x/agentkeel_premiere_desk-1"}},
        "runtimes": {}, "images": {},
        "retiring": {"arn": "arn:x/agentkeel_premiere_desk-1", "found": False, "error": "ResourceNotFoundException",
                     "read_at": "2026-10-05T12:00:00Z"},
        "deletes": [{"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-01T10:00:00Z", "runtime": "agentkeel_premiere_desk-1", "errorCode": None},
                    {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T10:00:00Z", "runtime": "agentkeel_other-9", "errorCode": None},
                    {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T09:55:00Z", "runtime": "agentkeel_premiere_desk-1", "errorCode": "AccessDenied"},
                    {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T10:00:00Z", "runtime": "agentkeel_premiere_desk-1", "errorCode": None}],
    }  # fmt: skip
    observer.compose(observation)
    return observation


def test_a_retirements_records_are_laid_side_by_side_in_the_shape_build_reads():
    """The observer writes S2's observation in the fixture's shape (feasibility.md section 4)."""
    retirement = retirement_observation()["s2"]["retirement"]
    fixture = json.loads((ROOT / "tests/fixtures/m07/s2-retired-agent/observation_held.json").read_text(encoding="utf-8"))
    assert set(fixture) <= set(retirement)
    # The deletion matched is this runtime's, after the merge, and not a refused attempt at one.
    assert retirement["delete_event"] == {"eventName": "DeleteAgentRuntime", "eventTime": "2026-10-05T10:00:00Z"}
    assert retirement["bundle"] == {"found": True, "key": f"bundles/premiere-desk/{'c' * 40}.tar"}
    assert upgrade.f7_2(retirement, 3600.0) == {"read": True, "held": True, "reasons": [], "elapsed_s": 600.0}


def test_a_bundles_prefix_that_cannot_be_listed_leaves_the_retirement_unread_not_missed():
    retirement = retirement_observation(refuse_prefix="bundles/")["s2"]["retirement"]
    assert retirement["bundle"] is None
    reading = upgrade.f7_2(retirement, 3600.0)
    assert reading["read"] is False and "the bundle not looked up" in reading["reasons"][0]


def test_the_latest_stored_observation_is_fetched_and_one_not_made_as_the_app_is_refused():
    stored = {"viewpoint": "app", "run_id": "777", "read_at": "2026-10-06T11:45:00Z", "upgrade": {}, "template": {}}
    objects = {"observations/700.json": ("2026-10-06T10:00:00", {**stored, "run_id": "700"}),
               "observations/777.json": ("2026-10-06T11:46:00", stored)}  # fmt: skip
    got = observer.read_stored(Bucket(objects))
    assert got["run_id"] == "777" and got["key"] == "observations/777.json" and got["error"] is None
    assert "stored nothing yet" in observer.read_stored(Bucket({}))["error"]
    assert "not an observation made as the App" in observer.read_stored(Bucket({"observations/1.json": ("2026-10-06T10:00:00", {"viewpoint": "anonymous"})}))["error"]
    assert "AccessDenied" in observer.read_stored(Bucket(objects, refuse_prefix="observations/"))["error"]


def test_an_observation_with_nothing_made_is_the_one_build_reads_as_all_unread(tmp_path, monkeypatch):
    """The observer's blank, through build's own reader: PR 2's stated reading."""
    monkeypatch.delenv("AGENTKEEL_PANEL2_FILE", raising=False)
    observation = observer.observe(["grafana"], observer.blank("anonymous"), FakeGitHub({}))
    assert "the workflow step that reads the panel did not run" in observation["panel2"]["error"]
    observation["surfaces"] = {"results": {plant: True for plant in plants.SURFACE_PLANTS}}
    reading = upgrade.record(observation, THRESHOLDS, HISTORY)
    assert [reading[name]["read"] for name in ("F7_0", "F7_1", "F7_2", "F7_3", "F7_4", "F7_5")] == [False] * 5 + [True]
    assert reading["taken"]["n"] == 0 and observation["apps"]["platform"] == APP


def test_the_observer_never_fails_the_job_on_a_part_it_cannot_read(monkeypatch):
    def broken(gh, observation):
        raise RuntimeError("GitHub is down")

    monkeypatch.setattr(observer, "read_github", broken)
    observation = observer.observe(["github"], observer.blank("anonymous"), FakeGitHub({}))
    assert observation["github_error"] == "RuntimeError: GitHub is down" and observation["parts"] == ["github"]


@pytest.mark.parametrize("flags, said", [
    (["--read", "nonsense", "--out", "x.json"], "unknown parts"),
    (["--read", "stored", "--out", "x.json"], "--read stored needs --stored"),
    (["--read", "github", "--viewpoint", "app", "--out", "x.json"], "platform-observer environment only"),
])  # fmt: skip
def test_the_command_refuses_a_part_it_does_not_know_and_the_apps_viewpoint_without_its_key(flags, said, capsys, monkeypatch, tmp_path):
    monkeypatch.delenv("AGENTKEEL_APP_PRIVATE_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    assert observer.main(flags) == 1
    captured = capsys.readouterr()
    assert said in captured.out + captured.err and not Path("x.json").exists()
