"""Look up claim 6's live records in GitHub, AWS and Grafana and write what each returned (P5, BLOCK 3).

    python scripts/observe_template.py --read github,grafana --out template.json
    python scripts/observe_template.py --read bucket --out template.json      # as agentkeel-audit-read
    python scripts/observe_template.py --read registry --out template.json    # as the eval role

An instrument, in the pattern of `scripts/observe_containment.py`. It reads
the two run files the human filled, `milestones/M06/runs/f6_2_standin.yaml`
(S2) and `f6_3_quickstart.yaml` (S3), for the repositories, pull request
numbers and the agent's name, and nothing else from them: every time and
every state it writes is GitHub's, AWS's or Grafana's. It writes raw lists
and decides nothing; `src/verdict/build.py` rules on them into the
envelope's `template` (`--template`, `src/verdict/template.py`), and the
ledger's row 6 reading reads that (SPEC/06 §4).

Each `--read` part needs its own credentials, so `evals.yml` calls this once
per set and each call merges its part into the same file:

- `github`: S2's pull request (merged or not, its head, every check run on
  its head with the App that posted it); S3's repository (`created_at`), its
  first pull request (merged, `merged_at`, the merged head) and, for each of
  its commits, the agent folder's seats and golden kinds as the commit holds
  them and the check runs on it; the deploy run that wrote the agent's first
  answer record (from that record, so `bucket` first when both are read). `GITHUB_TOKEN`; the repositories are public.
- `grafana`: panel 1's rows, `POST /api/ds/query` with panel 1's own target
  from `infra/grafana/panel1.json`, as the workspace answers. In CI the
  workflow posts the query in a step of its own and hands this the file
  (`AGENTKEEL_PANEL_FILE`), so the workspace's token is never in this
  process (security-reviewer F9 on M06 PR 2); locally,
  `AGENTKEEL_GRAFANA_URL` and `AGENTKEEL_GRAFANA_TOKEN`.
- `registry`: a scan of `agentkeel-registry` and S3's row in it.
- `bucket`: S3's first answer record, the earliest object under
  `envelopes/agents/<name>/` in the security account's bucket: its key,
  sha256, `LastModified` and the goldens it holds.

A part that cannot be read is written with its error, never left out: build
reads a missing record as unread, and row 6 reads unread as RED. Exit 0
whenever the file is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "milestones" / "M06" / "runs"
IDENTITY = ROOT / "infra" / "platform_identity.json"
PANEL = ROOT / "infra" / "grafana" / "panel1.json"
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
PLATFORM = "andaro74/agentkeel"
REGION = "us-west-2"
REGISTRY = "agentkeel-registry"
SECURITY_ACCOUNT = "897698239547"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
PARTS = ("github", "grafana", "registry", "bucket")


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_file(name: str) -> dict[str, Any]:
    return yaml.safe_load((RUNS / name).read_text(encoding="utf-8")) or {}


def first_observed(run: dict[str, Any]) -> dict[str, Any] | None:
    observed = run.get("observed")
    return observed[0] if isinstance(observed, list) and observed and isinstance(observed[0], dict) else None


# --- GitHub ---------------------------------------------------------------------


def gh(path: str, *, raw: bool = False) -> Any:
    request = urllib.request.Request(path if path.startswith("http") else f"{API}{path}")
    request.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    return body.decode("utf-8") if raw else json.loads(body)


def check_runs(repository: str, sha: str) -> list[dict[str, Any]]:
    runs = gh(f"/repos/{repository}/commits/{sha}/check-runs?per_page=100").get("check_runs") or []
    return [{"name": r.get("name"), "app_id": (r.get("app") or {}).get("id"), "app_slug": (r.get("app") or {}).get("slug"),
             "conclusion": r.get("conclusion"), "completed_at": r.get("completed_at")} for r in runs]  # fmt: skip


def required_checks(repository: str) -> list[dict[str, Any]] | None:
    """The live rulesets' required checks, each with the App it must come from; None when unread."""
    try:
        listed = gh(f"/repos/{repository}/rulesets?includes_parents=false&per_page=100") or []
        found = []
        for one in listed:
            ruleset = gh(f"/repos/{repository}/rulesets/{one['id']}")
            for rule in ruleset.get("rules") or []:
                if rule.get("type") == "required_status_checks":
                    found += [{"context": c.get("context"), "integration_id": c.get("integration_id")}
                              for c in (rule.get("parameters") or {}).get("required_status_checks") or []]  # fmt: skip
        return found
    except (urllib.error.URLError, KeyError, TimeoutError, OSError):
        return None


def folder_at(repository: str, sha: str) -> dict[str, Any]:
    """The agent folder's seats and golden kinds as the commit holds them (the repository's root).

    A file GitHub would not give is a read error, recorded, never read as a missing seat or golden
    (cold review F5 on M06 PR 2). A manifest that is not there is a 404, which is a fact about the commit."""
    read_error = None
    try:
        manifest = yaml.safe_load(gh(f"/repos/{repository}/contents/manifest.yaml?ref={sha}", raw=True))
        seats = manifest.get("seats") if isinstance(manifest, dict) else None
    except urllib.error.HTTPError as exc:
        seats = None
        if exc.code != 404:
            read_error = f"manifest.yaml: {exc.code}"
    except yaml.YAMLError:
        seats = None
    goldens = []
    try:
        listing = gh(f"/repos/{repository}/contents/goldens?ref={sha}")
    except urllib.error.HTTPError as exc:
        listing = []
        if exc.code != 404:
            read_error = read_error or f"goldens/: {exc.code}"
    for entry in listing if isinstance(listing, list) else []:
        if entry.get("type") != "file" or not str(entry.get("name", "")).endswith(".yaml"):
            continue
        try:
            golden = yaml.safe_load(gh(f"/repos/{repository}/contents/goldens/{entry['name']}?ref={sha}", raw=True))
        except urllib.error.HTTPError as exc:
            golden, read_error = None, read_error or f"goldens/{entry['name']}: {exc.code}"
        except yaml.YAMLError:
            golden = None
        golden = golden if isinstance(golden, dict) else {}
        goldens.append({"file": entry["name"], "kind": golden.get("kind"), "retired": golden.get("retired")})
    return {"seats": seats, "goldens": goldens, "read_error": read_error}


def read_s2() -> dict[str, Any] | None:
    seen = first_observed(run_file("f6_2_standin.yaml"))
    if seen is None:
        return None
    repository, number = seen.get("repository"), seen.get("pull_request")
    out: dict[str, Any] = {"repository": repository, "pull_request": number, "found": False, "error": None}
    try:
        pull = gh(f"/repos/{repository}/pulls/{number}")
        head = pull["head"]["sha"]
        out |= {"found": True, "merged": bool(pull.get("merged")), "head_sha": head,
                # GitHub's own reading of whether it could merge, and the check its ruleset requires, with the App.
                "mergeable_state": pull.get("mergeable_state"), "required_checks": required_checks(repository),
                "check_runs": check_runs(repository, head)}  # fmt: skip
    except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def read_s3_github(s3: dict[str, Any]) -> None:
    repository, number = s3["repository"], s3["pull_request"]
    repo = gh(f"/repos/{repository}")
    pull = gh(f"/repos/{repository}/pulls/{number}")
    commits = gh(f"/repos/{repository}/pulls/{number}/commits?per_page=100")
    s3["created_at"] = repo.get("created_at")
    s3["required_checks"] = required_checks(repository)
    s3["first_pr"] = {
        "merged": bool(pull.get("merged")), "merged_at": pull.get("merged_at"),
        "merge_head_sha": pull["head"]["sha"] if pull.get("merged") else None,
        "commits": [{"sha": c["sha"], **folder_at(repository, c["sha"]), "check_runs": check_runs(repository, c["sha"])}
                    for c in commits],
    }  # fmt: skip
    s3["found"] = True
    # The deploy run that wrote the first answer record, not the registry row's latest (threshold-owner N8).
    answer = s3.get("answer") or {}
    if run_id := answer.get("run_id"):
        run = gh(f"/repos/{PLATFORM}/actions/runs/{run_id}")
        s3["deploy"] = {"run_id": run_id, "conclusion": run.get("conclusion"), "completed_at": run.get("updated_at"),
                        "agent_commit": answer.get("commit")}  # fmt: skip


# --- AWS and Grafana --------------------------------------------------------------


def read_registry(s3: dict[str, Any] | None) -> dict[str, Any]:
    import boto3

    try:
        items = boto3.client("dynamodb", region_name=REGION).scan(TableName=REGISTRY).get("Items") or []
    except Exception as exc:  # noqa: BLE001 - an unread registry is an observation
        return {"read_at": now(), "error": f"{type(exc).__name__}: {exc}", "scan": None}
    if s3 is not None:
        mine = next((i for i in items if (i.get("name") or {}).get("S") == s3.get("agent_name")), None)
        s3["registry_row"] = None if mine is None else {k: next(iter(v.values())) for k, v in mine.items()}
    return {"read_at": now(), "error": None, "scan": {"Items": items}}


def read_bucket(s3: dict[str, Any]) -> None:
    """The agent's first answer record: the earliest object under its prefix, as the read role lists them.

    The earliest, not the registry row's commit: this part is read before the registry in evals.yml
    (the security account's credentials come first), and the timed run's record is its first deploy's."""
    import boto3

    prefix = f"envelopes/agents/{s3.get('agent_name')}/"
    try:
        client = boto3.client("s3", region_name=REGION)
        listed = [o for page in client.get_paginator("list_objects_v2").paginate(Bucket=AUDIT_BUCKET, Prefix=prefix)
                  for o in page.get("Contents") or []]  # fmt: skip
        if not listed:
            s3["answer"], s3["answer_error"] = None, f"no object under {prefix}"
            return
        first = min(listed, key=lambda o: o["LastModified"])
        got = client.get_object(Bucket=AUDIT_BUCKET, Key=first["Key"])
        body = got["Body"].read()
        record = json.loads(body)
        run_url = str(record.get("run_url") or "")
        s3["answer"] = {"key": first["Key"], "sha256": hashlib.sha256(body).hexdigest(),
                        "last_modified": got["LastModified"].isoformat().replace("+00:00", "Z"),
                        "goldens": record.get("goldens") or {}, "commit": record.get("commit"),
                        # The deploy run that wrote it, which F6.3 times by GitHub's own completion.
                        "run_id": run_url.rstrip("/").rsplit("/", 1)[-1] if "/actions/runs/" in run_url else None}  # fmt: skip
    except Exception as exc:  # noqa: BLE001 - an unread record is an observation
        s3["answer"], s3["answer_error"] = None, f"{prefix}: {type(exc).__name__}: {exc}"


def read_panel() -> dict[str, Any]:
    if path := os.environ.get("AGENTKEEL_PANEL_FILE"):
        try:
            return {"read_at": now(), "error": None, "frame": json.loads(Path(path).read_text(encoding="utf-8"))}
        except (OSError, ValueError) as exc:
            return {"read_at": now(), "frame": None,
                    "error": f"{path}: {type(exc).__name__}; the workflow step that reads panel 1 wrote nothing"}  # fmt: skip
    url, token = os.environ.get("AGENTKEEL_GRAFANA_URL"), os.environ.get("AGENTKEEL_GRAFANA_TOKEN")
    if not url or not token:
        return {"read_at": now(), "error": "no AGENTKEEL_GRAFANA_URL or AGENTKEEL_GRAFANA_TOKEN", "frame": None}
    dashboard = json.loads(PANEL.read_text(encoding="utf-8"))
    panel = next(p for p in dashboard["panels"] if p.get("id") == 1)
    body = json.dumps({"queries": panel["targets"], "from": "now-1h", "to": "now"}).encode("utf-8")
    request = urllib.request.Request(f"{url.rstrip('/')}/api/ds/query", data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return {"read_at": now(), "error": None, "frame": json.load(response)}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"read_at": now(), "error": f"{type(exc).__name__}: {exc}", "frame": None}


# --- the observation ----------------------------------------------------------------


def blank() -> dict[str, Any]:
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    seen = first_observed(run_file("f6_3_quickstart.yaml"))
    s3 = None
    if seen is not None:
        s3 = {"repository": seen.get("repository"), "pull_request": seen.get("pull_request"),
              "agent_name": run_file("f6_3_quickstart.yaml").get("agent_name"), "found": False, "error": None,
              "created_at": None, "first_pr": None, "deploy": None, "answer": None, "registry_row": None}  # fmt: skip
    return {"looked_up_at": now(), "platform_app_id": identity.get("platform_app_id"), "s2": None, "s3": s3,
            "panel": None, "registry": None, "parts": []}  # fmt: skip


def observe(parts: list[str], observation: dict[str, Any]) -> dict[str, Any]:
    s3 = observation.get("s3")
    if "registry" in parts:
        observation["registry"] = read_registry(s3)
    if "github" in parts:
        try:
            observation["s2"] = read_s2()
            if s3 is not None:
                read_s3_github(s3)
        except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
            if s3 is not None:
                s3["error"] = f"{type(exc).__name__}: {exc}"
    if "bucket" in parts and s3 is not None:
        read_bucket(s3)
    if "grafana" in parts:
        observation["panel"] = read_panel()
    observation["parts"] = sorted(set(observation.get("parts", [])) | set(parts))
    return observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--read", required=True, help=f"comma-separated, of {', '.join(PARTS)}")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    parts = [p.strip() for p in args.read.split(",") if p.strip()]
    if unknown := sorted(set(parts) - set(PARTS)):
        print(f"unknown parts {unknown}", file=sys.stderr)
        return 1
    observation = json.loads(args.out.read_text(encoding="utf-8")) if args.out.is_file() else blank()
    observation = observe(parts, observation)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(observation, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({', '.join(observation['parts'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
