"""Look up claim 7's live records in GitHub, AWS and Grafana and write what each returned (SPEC/07 §4; P5).

    python scripts/observe_upgrade.py --read bucket --out upgrade.json                 # as agentkeel-audit-read
    python scripts/observe_upgrade.py --read stored --out upgrade.json --stored app.json   # the same role
    python scripts/observe_upgrade.py --read github,aws,grafana --out upgrade.json      # as the eval role, with GITHUB_TOKEN
    python scripts/observe_upgrade.py --read github --viewpoint app --out observed.json   # observe.yml on main, as the observer App

An instrument, in the pattern of `scripts/observe_template.py`. It reads the
four run files under `milestones/M07/runs/` for the repositories, pull
request numbers and run ids the human filled in, and nothing else from
them: every time and every state it writes is GitHub's, AWS's or Grafana's.
A name it cannot find is unread. It writes raw records and decides nothing:
`src/verdict/build.py` rules on them into the envelope's `upgrade`
(`--upgrade`, `src/verdict/upgrade.py`), and the ledger's row 7 reading
reads that.

**The viewpoint** (SPEC/07 §2; `milestones/M07/open.md` row 3). A pull
request's own run asks GitHub with a token that has no rights in the
organisation: `--viewpoint anonymous`, the default. `observe.yml`, on
`main`, asks as the platform's observer App, with a token minted for each
repository and the `observe` permission set: `--viewpoint app`. Its
observation is stored in the audit bucket, and `--read stored` fetches the
latest one for build to rule on. The App's key is never in a job that
checks out a pull request's code.

Each `--read` part needs its own credentials, so `evals.yml` calls this once
per set and each call merges its part into the same file:

- `bucket` (the security account's read role): for every agent under
  `envelopes/agents/`, its answer records (key, commit, `LastModified`, the
  deploy run that wrote each, whether a golden passed), its retirement
  record if one was put, and its signed bundles under `bundles/`.
- `stored` (the same role): the latest object under `observations/`.
- `github`: each attempt's pull request (who opened it, when, its files, each
  commit's author and files, the checks on its head, its merge, what landed
  on the default branch meanwhile), its trigger (the template's push, the
  run that opened it), the owner's test's commits with the App's own
  reasons, the dispatched runs' jobs, and the tree's bundle digest at each
  merge.
- `aws` (the eval role): the registry, each agent's runtime and the tags of
  the image it runs, the image a tree's digest names, CloudTrail's
  `DeleteAgentRuntime` records.
- `grafana`: panel 2's rows, from the file the workflow's own step wrote
  (`AGENTKEEL_PANEL2_FILE`), so the workspace's token is never in this
  process; and panel 1's, the same way, for whether it lists an agent.

A part that cannot be read is written with its error, never left out. Exit
0 whenever the file is written.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import observe_template, platform_check, platform_upgrade  # noqa: E402

RUNS = ROOT / "milestones" / "M07" / "runs"
PLATFORM = "andaro74/agentkeel"
TEMPLATE = "agent-template"
REGION = "us-west-2"
REGISTRY = "agentkeel-registry"
AUDIT_BUCKET = "agentkeel-audit-897698239547"
ANSWER_KEY = re.compile(r"^envelopes/agents/([a-z][a-z0-9-]{2,30})/([0-9a-f]{40})\.json$")
RUN_URL = re.compile(r"/actions/runs/([0-9]+)")
PARTS = ("bucket", "stored", "github", "aws", "grafana")
REQUIRED_ON_MAIN = ROOT / "infra" / "ruleset" / "main.json"
LOOK_BACK = timedelta(days=30)


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def iso(value: Any) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if hasattr(value, "isoformat") else (value if isinstance(value, str) else None)


def run_file(name: str) -> dict[str, Any]:
    path = RUNS / name
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}


def observed(name: str) -> list[dict[str, Any]]:
    entries = run_file(name).get("observed")
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def failed(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:300]


GITHUB_ERRORS = (urllib.error.URLError, KeyError, TypeError, TimeoutError, OSError, ValueError)


# --- GitHub, from one viewpoint ---------------------------------------------------------


class GitHub:
    """Who is asking. Anonymous: the job's own token, which has no rights in the organisation. App: for a
    repository of the organisation's, a token minted for that repository and the `observe` set; for
    `agentkeel` itself, where the observer App is not installed, the job's own token."""

    def __init__(self, viewpoint: str, key: str | None = None) -> None:
        self.viewpoint = viewpoint
        self.key = key
        self.organisation, _platform = platform_check.identity()
        self.tokens: dict[str, str] = {}
        self.job_token = os.environ.get("GITHUB_TOKEN")

    def token(self, repository: str) -> str | None:
        if self.viewpoint != "app" or repository.split("/")[0] != self.organisation:
            return self.job_token
        if repository not in self.tokens:
            app_id = platform_check.load_grant()["agentkeel-observer"]["app_id"]
            self.tokens[repository] = platform_check.app_token(app_id, str(self.organisation), str(self.key), repository, "observe")
        return self.tokens[repository]

    def __call__(self, repository: str, path: str, *, raw: bool = False) -> Any:
        token = self.token(repository)
        saved = os.environ.get("GITHUB_TOKEN")
        try:
            if token is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = token
            return platform_check.gh(f"/repos/{repository}{path}", raw=raw)
        finally:
            if saved is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = saved

    def paged(self, repository: str, path: str, limit: int = 300) -> list[Any]:
        """Every page, not the first hundred (milestones/M07/open.md row 22: the M06 observer read one)."""
        out: list[Any] = []
        page = 1
        while len(out) < limit:
            got = self(repository, f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            out += got
            if len(got) < 100:
                break
            page += 1
        return out


def actor(user: Any, app: Any = None) -> dict[str, Any]:
    user = user if isinstance(user, dict) else {}
    app = app if isinstance(app, dict) else {}
    return {"login": user.get("login"), "type": user.get("type"), "app_id": app.get("id"), "app_slug": app.get("slug")}


def check_runs(gh: GitHub, repository: str, sha: str) -> list[dict[str, Any]]:
    runs = gh(repository, f"/commits/{sha}/check-runs?per_page=100").get("check_runs") or []
    return [{"name": r.get("name"), "app_id": (r.get("app") or {}).get("id"), "app_slug": (r.get("app") or {}).get("slug"),
             "conclusion": r.get("conclusion"), "completed_at": r.get("completed_at"),
             "title": (r.get("output") or {}).get("title"), "refused": observe_template.refused_checks(r)} for r in runs]  # fmt: skip


def commit_files(gh: GitHub, repository: str, sha: str) -> list[str] | None:
    try:
        return [f["filename"] for f in gh(repository, f"/commits/{sha}").get("files") or []]
    except GITHUB_ERRORS:
        return None


def required_on_head(gh: GitHub, repository: str, sha: str, platform_app: int | None) -> dict[str, str | None]:
    """The checks that gate a merge there, each with its conclusion on `sha`: in `agentkeel`, the contexts
    the exported main ruleset requires; in an agent repository, the platform check from the platform's App."""
    runs = check_runs(gh, repository, sha)
    if repository == PLATFORM:
        export = json.loads(REQUIRED_ON_MAIN.read_text(encoding="utf-8"))
        wanted = [c["context"] for rule in export["rules"] if rule["type"] == "required_status_checks"
                  for c in rule["parameters"]["required_status_checks"]]  # fmt: skip
        return {name: next((r["conclusion"] for r in runs if r["name"] == name), None) for name in wanted}
    mine = [r for r in runs if r["name"] == platform_check.CHECK and r["app_id"] == platform_app]
    return {platform_check.CHECK: mine[0]["conclusion"] if mine else None}


def workflow_run(gh: GitHub, run_id: Any, workflow: str) -> dict[str, Any]:
    """A run of `workflow` on `agentkeel`'s main: its `created_at` is a trigger's time (SPEC/07 §2). A run
    of another workflow, or from another branch, is not the trigger and is written as that."""
    try:
        run = gh(PLATFORM, f"/actions/runs/{int(run_id)}")
    except GITHUB_ERRORS as exc:
        return {"run": run_id, "at": None, "error": failed(exc)}
    right = str(run.get("path", "")).endswith(f"/{workflow}") and run.get("head_branch") == "main"
    return {"run": run.get("id"), "at": run.get("created_at") if right else None, "what": f"{workflow} run",
            "event": run.get("event"), "head_branch": run.get("head_branch"), "path": run.get("path"),
            "error": None if right else f"run {run_id} is not {workflow} on main"}  # fmt: skip


def template_push(gh: GitHub, organisation: str, version: Any) -> dict[str, Any]:
    """GitHub's push record of the template repository's commit that moved `platform_version` to `version`:
    the push event's time, not the commit's own date (SPEC/07 §2)."""
    repository = f"{organisation}/{TEMPLATE}"

    def version_at(ref: str) -> Any:
        try:
            return (yaml.safe_load(gh(repository, f"/contents/manifest.yaml?ref={ref}", raw=True)) or {}).get("platform_version")
        except GITHUB_ERRORS:
            return None

    try:
        for push in gh(repository, "/activity?activity_type=push&per_page=100"):
            if version_at(push["after"]) == version and version_at(push["before"]) != version:
                return {"what": "the template's push", "repository": repository, "at": push.get("timestamp"),
                        "after": push["after"], "platform_version": version, "error": None}  # fmt: skip
    except GITHUB_ERRORS as exc:
        return {"what": "the template's push", "repository": repository, "at": None, "error": failed(exc)}
    return {"what": "the template's push", "repository": repository, "at": None,
            "error": f"no push of {repository} moved platform_version to {version!r}"}  # fmt: skip


def sha256_file_changed(since: Any, until: Any) -> bool | None:
    """Did `infra/workflows.sha256` change on `agentkeel`'s main between two times? None when git cannot say."""
    if not since or not until:
        return None
    for ref in ("origin/main", "main", "HEAD"):
        done = subprocess.run(["git", "log", "--format=%H", f"--since={since}", f"--until={until}", ref, "--",
                               "infra/workflows.sha256"], cwd=ROOT, capture_output=True, text=True, check=False)  # fmt: skip
        if done.returncode == 0:
            return bool(done.stdout.strip())
    return None


def pull_record(gh: GitHub, repository: str, number: Any, platform_app: int | None) -> dict[str, Any]:
    """One pull request as GitHub records it: who opened it and when, its files, each commit's author and
    files, the checks on its head, its merge, and what landed on its base branch meanwhile."""
    out: dict[str, Any] = {"repository": repository, "pull_request": number, "found": False, "error": None, "trigger": None}
    try:
        pull = gh(repository, f"/pulls/{int(number)}")
        issue = gh(repository, f"/issues/{int(number)}")
        commits = gh.paged(repository, f"/pulls/{int(number)}/commits")
        files = gh.paged(repository, f"/pulls/{int(number)}/files")
        head = pull["head"]["sha"]
        opened = RUN_URL.search(pull.get("body") or "")
        out |= {
            "found": True, "author": actor(pull.get("user"), issue.get("performed_via_github_app")),
            "created_at": pull.get("created_at"), "draft": pull.get("draft"), "state": pull.get("state"),
            "merged": bool(pull.get("merged")), "merged_at": pull.get("merged_at"),
            "merge_commit_sha": pull.get("merge_commit_sha") if pull.get("merged") else None,
            "head_sha": head, "base_sha": pull["base"]["sha"], "base_ref": pull["base"]["ref"],
            "mergeable_state": pull.get("mergeable_state"), "opened_by_run": opened[1] if opened else None,
            "files": [f["filename"] for f in files],
            "commits": [{"sha": c["sha"], "author": actor(c.get("author")), "committer": actor(c.get("committer")),
                         "verified": ((c.get("commit") or {}).get("verification") or {}).get("verified"),
                         "files": commit_files(gh, repository, c["sha"])}
                        for c in commits],
            "required_on_head": required_on_head(gh, repository, head, platform_app),
            "default_branch_commits_between": None, "workflows_sha256_changed": None,
        }  # fmt: skip
        if out["merged"]:
            own = {c["sha"] for c in commits} | {out["merge_commit_sha"]}
            between = gh.paged(repository, f"/commits?sha={out['base_ref']}&since={out['created_at']}&until={out['merged_at']}")
            out["default_branch_commits_between"] = [
                {"sha": c["sha"], "author": actor(c.get("author")), "committer": actor(c.get("committer")),
                 "verified": ((c.get("commit") or {}).get("verification") or {}).get("verified"),
                 "files": commit_files(gh, repository, c["sha"])}
                for c in between if c["sha"] not in own]  # fmt: skip
    except GITHUB_ERRORS as exc:
        out["error"] = failed(exc)
    return out


def with_trigger(pull: dict[str, Any], trigger: dict[str, Any]) -> dict[str, Any]:
    pull["trigger"] = trigger
    if pull.get("merged"):
        pull["workflows_sha256_changed"] = sha256_file_changed(trigger.get("at"), pull.get("merged_at"))
    return pull


def manifest_at(gh: GitHub, repository: str, ref: str) -> dict[str, Any]:
    try:
        doc = yaml.safe_load(gh(repository, f"/contents/manifest.yaml?ref={ref}", raw=True))
        return doc if isinstance(doc, dict) else {}
    except (*GITHUB_ERRORS, yaml.YAMLError):
        return {}


# --- the bundle digest a tree gives ------------------------------------------------------


def digest_of(folder: Path) -> str:
    """The digest `deploy.yml` tags an agent's image with: the folder packed without its git or workflow files."""
    from scripts import runtime_for_tree

    with tempfile.TemporaryDirectory(prefix="agentkeel-digest-") as scratch:
        copy = Path(scratch) / "agent"
        shutil.copytree(folder, copy, ignore=shutil.ignore_patterns(".git", ".github"))
        return runtime_for_tree.bundle_digest(copy)


def agent_digest(repository: str, commit: str | None) -> tuple[str | None, str | None]:
    """An agent repository's bundle digest at `commit`, read as data; (digest, error)."""
    if not commit:
        return None, "no commit to pack"
    try:
        with tempfile.TemporaryDirectory(prefix="agentkeel-observe-") as scratch:
            return digest_of(platform_upgrade.fetch_as_data(repository, commit, Path(scratch))), None
    except (platform_upgrade.Refused, OSError, ValueError) as exc:
        return None, failed(exc)


def refagent_digest(commit: str | None) -> tuple[str | None, str | None]:
    """refagent's bundle digest as `agentkeel`'s tree gives it at `commit`; (digest, error)."""
    if not commit:
        return None, "no commit to pack"
    scratch = Path(tempfile.mkdtemp(prefix="agentkeel-tree-"))
    tree = scratch / "tree"
    try:
        done = subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(tree), commit], cwd=ROOT,
                              capture_output=True, text=True, check=False)  # fmt: skip
        if done.returncode != 0:
            return None, f"git cannot place {commit[:12]}: {done.stderr.strip()[-160:]}"
        return digest_of(tree / "agents" / "refagent"), None
    except (OSError, ValueError) as exc:
        return None, failed(exc)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, capture_output=True, check=False)
        shutil.rmtree(scratch, ignore_errors=True)


# --- each seed's GitHub part -----------------------------------------------------------------


def read_owner_test(gh: GitHub, entry: dict[str, Any], platform_app: int | None) -> dict[str, Any]:
    repository, number = str(entry.get("repository")), entry.get("pull_request")
    out: dict[str, Any] = {"repository": repository, "pull_request": number, "found": False, "error": None}
    try:
        pull = gh(repository, f"/pulls/{int(number)}")  # type: ignore[arg-type]
        commits = gh.paged(repository, f"/pulls/{int(number)}/commits")  # type: ignore[arg-type]
        merged = bool(pull.get("merged"))
        saved = os.environ.get("GITHUB_TOKEN")
        token = gh.token(repository)
        try:
            if token:
                os.environ["GITHUB_TOKEN"] = token
            folders = {c["sha"]: observe_template.folder_at(repository, c["sha"]) for c in commits}
        finally:
            if saved is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = saved
        merge_commit = pull.get("merge_commit_sha") if merged else None
        out |= {
            "found": True, "merged": merged, "merged_at": pull.get("merged_at"), "mergeable_state": pull.get("mergeable_state"),
            "merge_head_sha": pull["head"]["sha"] if merged else None,
            "commits": [{"sha": c["sha"], **folders[c["sha"]], "check_runs": check_runs(gh, repository, c["sha"])} for c in commits],
            "merge_commit": {"sha": merge_commit, "check_runs": check_runs(gh, repository, merge_commit) if merge_commit else []},
            "agent_name": manifest_at(gh, repository, merge_commit or pull["head"]["sha"]).get("name"),
        }  # fmt: skip
    except GITHUB_ERRORS as exc:
        out["error"] = failed(exc)
    return out


def job_annotations(gh: GitHub, job: dict[str, Any]) -> list[str] | None:
    """GitHub's own annotations on a job (its check run): where it says why a job never started, as
    'Branch "x" is not allowed to deploy to platform-app due to environment protection rules.' None if unread."""
    try:
        return [str(a.get("message")) for a in gh(PLATFORM, f"/check-runs/{int(job['id'])}/annotations?per_page=100")]
    except (*GITHUB_ERRORS, KeyError, TypeError, ValueError):
        return None


def read_dispatch(gh: GitHub, entry: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"repository": PLATFORM, "run": entry.get("run"), "found": False, "error": None}
    try:
        run = gh(PLATFORM, f"/actions/runs/{int(entry['run'])}")
        jobs = gh(PLATFORM, f"/actions/runs/{int(entry['run'])}/jobs?per_page=100").get("jobs") or []
        out |= {"found": True, "event": run.get("event"), "head_branch": run.get("head_branch"), "path": run.get("path"),
                "created_at": run.get("created_at"),
                "jobs": [{"name": j.get("name"), "conclusion": j.get("conclusion"),
                          "steps": len(j["steps"]) if isinstance(j.get("steps"), list) else None,
                          "runner_name": j.get("runner_name"),
                          "annotations": job_annotations(gh, j) if j.get("conclusion") == "failure" else []} for j in jobs]}  # fmt: skip
    except GITHUB_ERRORS as exc:
        out["error"] = failed(exc)
    return out


def artifact_json(gh: GitHub, run_id: Any, name: str) -> dict[str, Any] | None:
    """A JSON artifact a run of `agentkeel`'s kept, by name: GitHub's copy of what the job wrote. None if absent."""
    listed = gh(PLATFORM, f"/actions/runs/{int(run_id)}/artifacts?per_page=100").get("artifacts") or []
    found = next((a for a in listed if a.get("name") == name and not a.get("expired")), None)
    if found is None:
        return None
    request = urllib.request.Request(found["archive_download_url"])
    if token := gh.token(PLATFORM):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    return json.loads(archive.read(archive.namelist()[0]))


def read_ruleset(gh: GitHub, repository: str, ruleset_id: Any) -> dict[str, Any]:
    """One ruleset as GitHub returns it to this caller, with GitHub's own time of its last change. A field
    GitHub does not show the caller (`bypass_actors`, to anyone who cannot administer it) is written None."""
    out: dict[str, Any] = {"id": ruleset_id, "read_at": now(), "error": None}
    try:
        live = gh(repository, f"/rulesets/{int(ruleset_id)}")
        out |= {key: live.get(key) for key in ("name", "target", "enforcement", "conditions", "rules", "bypass_actors",
                                               "updated_at")}  # fmt: skip
    except GITHUB_ERRORS as exc:
        out["error"] = failed(exc)
    return out


def read_relaxation(gh: GitHub, entry: dict[str, Any], platform_app: int | None) -> dict[str, Any]:
    """The seeded relaxation, as records and nothing else: GitHub's answer to the App's call, as the `post`
    job kept it; GitHub's time of the run that made it; the new head's checks; the ruleset as it stands;
    every pull request's merge time; every time the platform's App passed a head.

    Which of them fall after the call, between it and the restore, or after the restore is build's to
    say (`upgrade.relaxation`; cold review F6 on M07 PR 2: until M07 PR 3 this compared the times itself)."""
    repository = str(entry.get("repository"))
    out: dict[str, Any] = {"repository": repository, "run": entry.get("run"), "pull_request": entry.get("pull_request"),
                           "found": False, "error": None, "answer": None, "asked": None, "new_head": None,
                           "ruleset": None, "merges": None, "app_passes": None}  # fmt: skip
    try:
        answer = artifact_json(gh, entry["run"], "relax-seed")
        out |= {"found": answer is not None, "answer": answer}
        if answer is None or not isinstance(answer.get("status"), int) or answer["status"] >= 400:
            return out
        out["asked"] = workflow_run(gh, entry["run"], "platform-check.yml")
        head = gh(repository, f"/pulls/{int(entry['pull_request'])}")["head"]["sha"]
        out["new_head"] = {"sha": head, "check_runs": check_runs(gh, repository, head)}
        pulls = gh.paged(repository, "/pulls?state=all&sort=updated&direction=desc")
        default = gh(repository, "")["default_branch"]
        heads = {p["head"]["sha"] for p in pulls} | {gh(repository, f"/branches/{default}")["commit"]["sha"]}
        out["app_passes"] = sorted(({"sha": sha, "completed_at": run["completed_at"]}
                                    for sha in heads for run in check_runs(gh, repository, sha)
                                    if run["app_id"] == platform_app and run["name"] == platform_check.CHECK
                                    and run["conclusion"] == "success"), key=lambda p: (str(p["completed_at"]), p["sha"]))  # fmt: skip
        out["merges"] = sorted(({"number": p["number"], "merged_at": p["merged_at"]} for p in pulls if p.get("merged_at")),
                               key=lambda m: m["number"])  # fmt: skip
        out["ruleset"] = read_ruleset(gh, repository, answer.get("ruleset"))
    except GITHUB_ERRORS as exc:
        out["error"] = failed(exc)
    return out


def read_github(gh: GitHub, observation: dict[str, Any]) -> None:
    organisation, platform_app = platform_check.identity()
    platform_app = platform_app if isinstance(platform_app, int) else None
    s0 = {"owner_test": None, "dispatch": None, "relaxation": None}
    for entry in observed("f7_0_owner_test.yaml"):
        what = str(entry.get("what", ""))
        if "dispatched from a branch" in what:
            s0["dispatch"] = read_dispatch(gh, entry)
        elif "relax" in what:
            s0["relaxation"] = read_relaxation(gh, entry, platform_app)
        elif "owner's test" in what:
            s0["owner_test"] = read_owner_test(gh, entry, platform_app)
    observation["s0"] = s0

    pulls, lives = [], {}
    for entry in observed("f7_1_platform_upgrade.yaml"):
        repository = str(entry.get("repository"))
        pull = pull_record(gh, repository, entry.get("pull_request"), platform_app)
        version = manifest_at(gh, repository, pull["head_sha"]).get("platform_version") if pull.get("found") else None
        pulls.append(with_trigger(pull, template_push(gh, str(organisation), version)))
        if pull.get("merged"):
            digest, error = agent_digest(repository, pull.get("merge_commit_sha"))
            lives[repository] = {"agent": manifest_at(gh, repository, pull["merge_commit_sha"]).get("name"),
                                 "merge_commit_sha": pull.get("merge_commit_sha"), "tree_digest": digest, "error": error,
                                 "deploy": None, "runtime": None}  # fmt: skip
    observation["s1"] = {"pulls": pulls, "lives": lives} if pulls else None

    observation["s2"] = None
    for entry in observed("f7_2_retire.yaml"):
        repository = str(entry.get("repository"))
        pull = pull_record(gh, repository, entry.get("pull_request"), platform_app)
        trigger = workflow_run(gh, entry.get("run") or pull.get("opened_by_run"), "deploy.yml")
        base = pull.get("base_sha") if pull.get("found") else None
        observation["s2"] = {
            "pull": with_trigger(pull, trigger),
            "retirement": {"agent": manifest_at(gh, repository, base).get("name") if base else None,
                           "pull_request": {"merged": pull.get("merged"), "merged_at": pull.get("merged_at")},
                           "delete_event": None, "get_runtime": None, "invocation": None, "answer_records": None,
                           "bundle": None, "registry_row": None},
        }  # fmt: skip

    made = observed("f7_3_rollback.yaml")
    observation["s3"] = None
    if made:
        swap_entry = next((e for e in made if "swap" in str(e.get("what", ""))), None)
        back_entry = next((e for e in made if "rollback" in str(e.get("what", ""))), None)
        s3: dict[str, Any] = {"swap": None, "swap_live": None, "rollback": None}
        if swap_entry:
            swap = pull_record(gh, PLATFORM, swap_entry.get("pull_request"), platform_app)
            s3["swap"] = with_trigger(swap, workflow_run(gh, swap.get("opened_by_run"), "model-watch.yml"))
            if swap.get("merged"):
                digest, error = refagent_digest(swap.get("merge_commit_sha"))
                s3["swap_live"] = {"agent": "refagent", "merge_commit_sha": swap["merge_commit_sha"], "tree_digest": digest,
                                   "error": error, "deploy": deploy_run(gh, swap["merge_commit_sha"]), "runtime": None}  # fmt: skip
        if back_entry:
            repository = str(back_entry.get("repository"))
            revert = pull_record(gh, repository, back_entry.get("pull_request"), platform_app)
            on_refagent = repository == PLATFORM
            merge = revert.get("merge_commit_sha")
            # What the revert reverts: the swap's merge on agentkeel, or the platform upgrade's merge in the agent's repository.
            upgraded = (s3["swap"] or {}).get("merge_commit_sha") if on_refagent else next(
                (p.get("merge_commit_sha") for p in pulls if p.get("repository") == repository), None)  # fmt: skip
            pack = refagent_digest if on_refagent else (lambda commit: agent_digest(repository, commit))
            tree, tree_error = pack(merge)
            upgrade, upgrade_error = pack(upgraded)
            s3["rollback"] = {
                "agent": "refagent" if on_refagent else manifest_at(gh, repository, merge or revert.get("head_sha") or "HEAD").get("name"),
                "repository": repository, "pull_request": back_entry.get("pull_request"), "fallback": not on_refagent,
                "revert": {"merged": revert.get("merged"), "merge_commit_sha": merge, "merged_at": revert.get("merged_at")},
                "revert_deploy": deploy_run(gh, merge) if on_refagent and merge else None,
                "tree_digest_at_revert": tree, "upgrade_digest": upgrade, "runtime": None,
                "error": revert.get("error") or tree_error or upgrade_error,
            }  # fmt: skip
        observation["s3"] = s3


def deploy_run(gh: GitHub, commit: str | None) -> dict[str, Any]:
    """`deploy.yml`'s run for a push of `commit` to main: GitHub's record of whether and when it completed."""
    if not commit:
        return {"run_id": None, "conclusion": None, "completed_at": None}
    try:
        runs = gh(PLATFORM, f"/actions/workflows/deploy.yml/runs?head_sha={commit}&event=push&per_page=20").get("workflow_runs") or []
    except GITHUB_ERRORS as exc:
        return {"run_id": None, "conclusion": None, "completed_at": None, "error": failed(exc)}
    done = [r for r in runs if r.get("status") == "completed"]
    if not done:
        return {"run_id": runs[0].get("id") if runs else None, "conclusion": None, "completed_at": None}
    last = max(done, key=lambda r: r.get("updated_at") or "")
    return {"run_id": last.get("id"), "conclusion": last.get("conclusion"), "completed_at": last.get("updated_at")}


def run_completed(gh: GitHub, run_id: Any) -> dict[str, Any]:
    """One run of `agentkeel`'s, by id: the deploy run an answer record names."""
    try:
        run = gh(PLATFORM, f"/actions/runs/{int(run_id)}")
        return {"run_id": run.get("id"), "conclusion": run.get("conclusion"), "completed_at": run.get("updated_at")}
    except GITHUB_ERRORS as exc:
        return {"run_id": run_id, "conclusion": None, "completed_at": None, "error": failed(exc)}


# --- the audit bucket ---------------------------------------------------------------------------


def read_bucket(s3: Any = None) -> dict[str, Any]:
    """Every agent's answer records, retirement record and bundles, as the read role lists them."""
    out: dict[str, Any] = {"read_at": now(), "error": None, "agents": {}}
    try:
        if s3 is None:
            import boto3

            s3 = boto3.client("s3", region_name=REGION)
        pages = s3.get_paginator("list_objects_v2")

        def agent(name: str) -> dict[str, Any]:
            return out["agents"].setdefault(name, {"answers": [], "retired": None, "bundles": [], "bundles_error": None})

        for page in pages.paginate(Bucket=AUDIT_BUCKET, Prefix="envelopes/agents/"):
            for item in page.get("Contents") or []:
                key = item["Key"]
                if match := ANSWER_KEY.match(key):
                    record = json.loads(s3.get_object(Bucket=AUDIT_BUCKET, Key=key)["Body"].read())
                    run = RUN_URL.search(str(record.get("run_url") or ""))
                    agent(match[1])["answers"].append({
                        "key": key, "commit": match[2], "last_modified": iso(item["LastModified"]),
                        "run_id": run[1] if run else None,
                        "passed": any(g.get("pass") is True for g in (record.get("goldens") or {}).values()),
                        "goldens": {g: {"pass": r.get("pass")} for g, r in (record.get("goldens") or {}).items()}})  # fmt: skip
                elif key.endswith("/retired.json"):
                    name = key.split("/")[2]
                    record = json.loads(s3.get_object(Bucket=AUDIT_BUCKET, Key=key)["Body"].read())
                    agent(name)["retired"] = {"key": key, "last_modified": iso(item["LastModified"]),
                                              "runtime_arn": record.get("runtime_arn"), "commit": record.get("commit"),
                                              "invocation": record.get("invocation")}  # fmt: skip
        # A prefix of its own, and a grant of its own: unreadable until the security account's stack carries it.
        try:
            for page in pages.paginate(Bucket=AUDIT_BUCKET, Prefix="bundles/"):
                for item in page.get("Contents") or []:
                    parts = item["Key"].split("/")
                    if len(parts) == 3 and parts[2].endswith(".tar"):
                        agent(parts[1])["bundles"].append({"key": item["Key"], "last_modified": iso(item["LastModified"])})
        except Exception as exc:  # noqa: BLE001 - an unread prefix is an observation
            for one in out["agents"].values():
                one["bundles_error"] = failed(exc)
            out["bundles_error"] = failed(exc)
    except Exception as exc:  # noqa: BLE001 - an unread bucket is an observation
        out["error"] = failed(exc)
    return out


def read_stored(s3: Any = None) -> dict[str, Any]:
    """The latest observation `observe.yml` stored under `observations/`, with its key and when it was put."""
    try:
        if s3 is None:
            import boto3

            s3 = boto3.client("s3", region_name=REGION)
        listed = [o for page in s3.get_paginator("list_objects_v2").paginate(Bucket=AUDIT_BUCKET, Prefix="observations/")
                  for o in page.get("Contents") or [] if o["Key"].endswith(".json")]  # fmt: skip
        if not listed:
            return {"error": "no object under observations/: main's observer has stored nothing yet", "run_id": None}
        latest = max(listed, key=lambda o: o["LastModified"])
        stored = json.loads(s3.get_object(Bucket=AUDIT_BUCKET, Key=latest["Key"])["Body"].read())
        if not isinstance(stored, dict) or stored.get("viewpoint") != "app":
            return {"error": f"{latest['Key']} is not an observation made as the App", "run_id": None}
        return {**stored, "key": latest["Key"], "stored_at": iso(latest["LastModified"]), "error": None}
    except Exception as exc:  # noqa: BLE001 - an unread prefix is an observation
        return {"error": failed(exc), "run_id": None}


# --- AWS, as the eval role ------------------------------------------------------------------------


def read_aws(observation: dict[str, Any], session: Any = None) -> None:
    """The registry, the runtimes and images the GitHub part named, and CloudTrail's deletions."""
    from scripts import runtime_for_tree

    out: dict[str, Any] = {"read_at": now(), "error": None, "registry": None, "runtimes": {}, "images": {}, "deletes": None}
    observation["aws"] = out
    try:
        if session is None:
            import boto3

            session = boto3.session.Session(region_name=REGION)
        items = session.client("dynamodb").scan(TableName=REGISTRY).get("Items") or []
        out["registry"] = {(i.get("name") or {}).get("S"): {k: next(iter(v.values())) for k, v in i.items()} for i in items}
    except Exception as exc:  # noqa: BLE001 - an unread registry is an observation
        out["error"] = failed(exc)
        return
    rows = out["registry"]
    wanted: dict[str, list[str]] = {}  # agent -> the tree digests whose image is looked for
    s1, s3 = observation.get("s1") or {}, observation.get("s3") or {}
    for live in [*(s1.get("lives") or {}).values(), s3.get("swap_live")]:
        if isinstance(live, dict) and live.get("agent"):
            wanted.setdefault(live["agent"], []).append(live.get("tree_digest"))
    rollback = s3.get("rollback") if isinstance(s3.get("rollback"), dict) else None
    if rollback and rollback.get("agent"):
        wanted.setdefault(rollback["agent"], [])
    ecr = session.client("ecr")
    for name, digests in wanted.items():
        try:
            arn, digest, tags = runtime_for_tree.runtime_image(session, name)
            out["runtimes"][name] = {"arn": arn, "image_digest": digest, "image_tags": tags, "read_at": now(), "error": None}
        except Exception as exc:  # noqa: BLE001
            out["runtimes"][name] = {"image_tags": None, "read_at": now(), "error": failed(exc)}
        for digest in [d for d in digests if d]:
            try:
                found = ecr.describe_images(repositoryName=runtime_for_tree.names(name)[1], imageIds=[{"imageTag": digest}])
                out["images"][digest] = {"image_tags": [t for i in found["imageDetails"] for t in i.get("imageTags", [])],
                                         "read_at": now(), "error": None}  # fmt: skip
            except Exception as exc:  # noqa: BLE001
                missing = "ImageNotFound" in type(exc).__name__ or "ImageNotFound" in str(exc)
                out["images"][digest] = {"image_tags": [] if missing else None, "read_at": now(),
                                         "error": None if missing else failed(exc)}  # fmt: skip
    # A retiring agent: is its runtime gone, and when did CloudTrail see it deleted?
    retirement = (observation.get("s2") or {}).get("retirement") or {}
    name = retirement.get("agent")
    arn = (rows.get(name) or {}).get("retiring_arn") if name else None
    if arn:
        try:
            runtime = session.client("bedrock-agentcore-control").get_agent_runtime(agentRuntimeId=arn.rsplit("/", 1)[-1])
            out["retiring"] = {"arn": arn, "found": True, "status": runtime.get("status"), "read_at": now(), "error": None}
        except Exception as exc:  # noqa: BLE001
            code = getattr(exc, "response", {}).get("Error", {}).get("Code") if hasattr(exc, "response") else type(exc).__name__
            out["retiring"] = {"arn": arn, "found": False, "error": code, "read_at": now()}
        try:
            pages = session.client("cloudtrail").get_paginator("lookup_events").paginate(
                LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "DeleteAgentRuntime"}],
                StartTime=datetime.now(UTC) - LOOK_BACK, EndTime=datetime.now(UTC))  # fmt: skip
            out["deletes"] = []
            for page in pages:
                for event in page.get("Events") or []:
                    detail = json.loads(event.get("CloudTrailEvent") or "{}")
                    out["deletes"].append({"eventName": "DeleteAgentRuntime", "eventTime": detail.get("eventTime"),
                                           "runtime": (detail.get("requestParameters") or {}).get("agentRuntimeId"),
                                           "errorCode": detail.get("errorCode")})  # fmt: skip
        except Exception as exc:  # noqa: BLE001
            out["deletes_error"] = failed(exc)


# --- one observation from the parts -------------------------------------------------------------


def panel(env: str) -> dict[str, Any]:
    path = os.environ.get(env)
    if not path:
        return {"read_at": now(), "error": f"no {env}: the workflow step that reads the panel did not run", "frame": None}
    try:
        return {"read_at": now(), "error": None, "frame": json.loads(Path(path).read_text(encoding="utf-8"))}
    except (OSError, ValueError) as exc:
        return {"read_at": now(), "frame": None, "error": f"{path}: {type(exc).__name__}; the step that reads the panel wrote nothing"}


def compose(observation: dict[str, Any], gh: GitHub | None = None) -> None:
    """Lay AWS's and the bucket's records beside the GitHub records they belong to, in `upgrade.record`'s shape.

    Matching only: which answer record is the merge commit's, which CloudTrail record is the runtime's.
    Nothing here says held or not."""
    bucket = (observation.get("bucket") or {}).get("agents") or {}
    aws = observation.get("aws") or {}
    rows, runtimes, images = aws.get("registry") or {}, aws.get("runtimes") or {}, aws.get("images") or {}

    def answer_for(name: Any, commit: Any) -> dict[str, Any] | None:
        return next((a for a in (bucket.get(name) or {}).get("answers") or [] if a["commit"] == commit), None)

    def deploy_of(answer: dict[str, Any] | None) -> dict[str, Any] | None:
        if not answer or not answer.get("run_id") or gh is None:
            return None
        return run_completed(gh, answer["run_id"])

    test = (observation.get("s0") or {}).get("owner_test")
    if isinstance(test, dict) and test.get("found"):
        name = test.get("agent_name")
        answer = answer_for(name, (test.get("merge_commit") or {}).get("sha"))
        if answer is not None or "answer" not in test:
            test["answer"] = answer
            test["deploy"] = deploy_of(answer) or test.get("deploy")
        row = rows.get(name) if name else None
        if row is not None or "registry_row" not in test:
            test["registry_row"] = row
        frame = (observation.get("panel1") or {}).get("frame")
        if frame is not None:
            try:
                from src.verdict import template

                test["on_panel"] = name in template.panel_names(frame)
            except Exception:  # noqa: BLE001 - a frame that does not parse is panel 1 unread
                test["on_panel"] = None
        else:
            test.setdefault("on_panel", None)

    for live in ((observation.get("s1") or {}).get("lives") or {}).values():
        answer = answer_for(live.get("agent"), live.get("merge_commit_sha"))
        live["deploy"] = deploy_of(answer) or live.get("deploy")
        live["runtime"] = images.get(live.get("tree_digest")) or live.get("runtime")
    s3 = observation.get("s3") or {}
    if isinstance(s3.get("swap_live"), dict):
        s3["swap_live"]["runtime"] = images.get(s3["swap_live"].get("tree_digest")) or s3["swap_live"].get("runtime")
    back = s3.get("rollback")
    if isinstance(back, dict):
        back["runtime"] = runtimes.get(back.get("agent")) or back.get("runtime")
        if back.get("fallback"):
            answer = answer_for(back.get("agent"), (back.get("revert") or {}).get("merge_commit_sha"))
            back["revert_deploy"] = deploy_of(answer) or back.get("revert_deploy")

    retirement = (observation.get("s2") or {}).get("retirement")
    if isinstance(retirement, dict) and retirement.get("agent"):
        name = retirement["agent"]
        mine = bucket.get(name)
        if mine is not None:
            retirement["answer_records"] = [{"key": a["key"], "last_modified": a["last_modified"]} for a in mine["answers"]]
            retirement["invocation"] = (mine.get("retired") or {}).get("invocation")
            if mine.get("bundles_error") is None:
                tars = mine.get("bundles") or []
                retirement["bundle"] = {"found": bool(tars), "key": tars[-1]["key"] if tars else None}
        if "retiring" in aws:
            retirement["get_runtime"] = {k: aws["retiring"].get(k) for k in ("found", "status", "error", "read_at") if k in aws["retiring"]}
            runtime_id = str(aws["retiring"].get("arn", "")).rsplit("/", 1)[-1]
            merged_at = (retirement.get("pull_request") or {}).get("merged_at") or ""
            # Matching, by the runtime's id, no error and a time at or after the merge. Build's own "earlier
            # than the merge" is then a guard on a record from any other source (cold review F6 on M07 PR 2).
            after = sorted((d for d in aws.get("deletes") or [] if d.get("runtime") == runtime_id and not d.get("errorCode")
                            and str(d.get("eventTime")) >= merged_at), key=lambda d: str(d.get("eventTime")))  # fmt: skip
            retirement["delete_event"] = {"eventName": after[0]["eventName"], "eventTime": after[0]["eventTime"]} if after else None
        if name in rows:
            retirement["registry_row"] = {"name": name, "retired_at": rows[name].get("retired_at")}


def blank(viewpoint: str) -> dict[str, Any]:
    _organisation, platform_app = platform_check.identity()
    try:
        grant = platform_check.load_grant(ruled_only=False)
    except platform_check.NoGrant:
        grant = {}
    return {"looked_up_at": now(), "viewpoint": viewpoint, "parts": [],
            "apps": {"platform": platform_app, "upgrades": (grant.get("agentkeel-upgrades") or {}).get("app_id"),
                     "observer": (grant.get("agentkeel-observer") or {}).get("app_id")},
            "s0": {"owner_test": None, "dispatch": None, "relaxation": None}, "s1": None, "s2": None, "s3": None,
            "panel2": None}  # fmt: skip


def observe(parts: list[str], observation: dict[str, Any], gh: GitHub) -> dict[str, Any]:
    if "bucket" in parts:
        observation["bucket"] = read_bucket()
    if "github" in parts:
        try:
            read_github(gh, observation)
            observation["github_error"] = None
        except Exception as exc:  # noqa: BLE001 - the observer never fails the job; an unread part is recorded
            observation["github_error"] = failed(exc)
    if "aws" in parts:
        try:
            read_aws(observation)
        except Exception as exc:  # noqa: BLE001 - as above: recorded, never raised
            observation.setdefault("aws", {})["error"] = failed(exc)
    if "grafana" in parts:
        observation["panel2"] = panel("AGENTKEEL_PANEL2_FILE")
        observation["panel1"] = panel("AGENTKEEL_PANEL_FILE")
    try:
        compose(observation, gh if "github" in parts else None)
    except Exception as exc:  # noqa: BLE001
        observation["compose_error"] = failed(exc)
    observation["parts"] = sorted(set(observation.get("parts", [])) | set(parts))
    observation["looked_up_at"] = now()
    return observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--read", required=True, help=f"comma-separated, of {', '.join(PARTS)}")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--stored", type=Path, help="where --read stored writes the observation main's observer stored")
    parser.add_argument("--viewpoint", choices=("anonymous", "app"), default="anonymous")
    parser.add_argument("--run-id", help="with --viewpoint app: the observe.yml run that made this observation")
    args = parser.parse_args(argv)
    parts = [p.strip() for p in args.read.split(",") if p.strip()]
    if unknown := sorted(set(parts) - set(PARTS)):
        print(f"unknown parts {unknown}", file=sys.stderr)
        return 1
    key = os.environ.pop("AGENTKEEL_APP_PRIVATE_KEY", None)
    if args.viewpoint == "app" and not key:
        print("no AGENTKEEL_APP_PRIVATE_KEY: the App's viewpoint is read in the platform-observer environment only")
        return 1
    if "stored" in parts:
        if not args.stored:
            print("--read stored needs --stored FILE", file=sys.stderr)
            return 1
        stored = read_stored()
        args.stored.write_text(json.dumps(stored, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"wrote {args.stored}: {stored.get('key') or stored.get('error')}")
        parts = [p for p in parts if p != "stored"]
    observation = json.loads(args.out.read_text(encoding="utf-8")) if args.out.is_file() else blank(args.viewpoint)
    observation = observe(parts, observation, GitHub(args.viewpoint, key))
    if args.viewpoint == "app":
        # What is stored: the App's reading, with the run that made it, in the shape build takes as `app`.
        observation = {"viewpoint": "app", "run_id": args.run_id, "read_at": observation["looked_up_at"],
                       "upgrade": {k: observation.get(k) for k in ("s0", "s1", "s2", "s3")},
                       "template": observe_template_as(GitHub(args.viewpoint, key)),
                       "github_error": observation.get("github_error")}  # fmt: skip
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(observation, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({', '.join(parts) or 'nothing more'}; viewpoint {args.viewpoint})")
    return 0


def observe_template_as(gh: GitHub) -> dict[str, Any]:
    """Claim 6's two GitHub readings, S2 and S3, read as the App: `scripts/observe_template.py`'s own
    readers, each under the token minted for the repository its run file names."""
    out: dict[str, Any] = {"s2": None, "s3": None}
    for name, key in (("f6_2_standin.yaml", "s2"), ("f6_3_quickstart.yaml", "s3")):
        seen = observe_template.first_observed(observe_template.run_file(name))
        if seen is None:
            continue
        saved = os.environ.get("GITHUB_TOKEN")
        try:
            if token := gh.token(str(seen.get("repository"))):
                os.environ["GITHUB_TOKEN"] = token
            if key == "s2":
                out["s2"] = observe_template.read_s2()
            else:
                s3 = {"repository": seen.get("repository"), "pull_request": seen.get("pull_request"), "found": False,
                      "error": None, "answer": None}  # fmt: skip
                observe_template.read_s3_github(s3)
                out["s3"] = s3
        except GITHUB_ERRORS as exc:
            out[key] = {"found": False, "error": failed(exc)}
        finally:
            if saved is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = saved
    return out


if __name__ == "__main__":
    sys.exit(main())
