"""Look up M09's plant run and write what the answer record, the built guardrail, the registry and GitHub returned (P5).

    python scripts/observe_rules.py --read bucket --out rules.json                   # as agentkeel-audit-read
    python scripts/observe_rules.py --read github,registry,guardrail --out rules.json  # as the eval role, GITHUB_TOKEN

An instrument, in the pattern of `scripts/observe_template.py`. It reads the
run file the owner fills after making the run,
`milestones/M09/runs/f9_3_plant_run.yaml`, for the repository, the agent's
name, the three pull request numbers and the answer record's key, and nothing
else from it: every state it writes is GitHub's, AWS's or the record's. It
writes raw records and decides nothing; `src/verdict/agent_rules.py` rules on
them into the envelope's `agent_rules` (`build --rules`), and the ledger's
row 9 reading reads that (SPEC/09 §4, §6).

The `observed` block the owner fills (SPEC/09 §5.1), keys only, never a result:

    observed:
      first:  {pull_request: 1}        # S1's folder with the placeholder pin; merged
      deploy: {run_id: 123, answer_key: envelopes/agents/festival-desk/<merge commit>.json}
      second: {pull_request: 2}        # the pin from the registry row and S2's weakened.yaml; refused
      third:  {pull_request: 3}        # the pin alone; merged

Each `--read` part needs its own credentials, so `evals.yml` calls this once
per set and each call merges its part into the same file:

- `bucket`: the answer record the deploy put, by `answer_key`, or the latest
  object under `envelopes/agents/<name>/` when no key is named: the record
  whole (its goldens, observations and the guardrail the stack built).
- `github`: each of the three pull requests (merged, head, merge commit) and
  every check run on its head with the names the platform's check refused
  under and its summary; the agent's `rules/guardrail.yaml` and
  `rules/redteam.yaml` **at the first pull request's merge commit**, read
  through the API by that commit, never from a working tree; and the digest
  the observer computes itself over `rules/baseline.yaml` as `git show`
  reads it on `origin/main` and those files (F9.1, SPEC/09 §4, note 9).
- `registry`: the agent's row (`guardrail_id`, `guardrail_version`,
  `rules_digest`, the deployed commit).
- `guardrail`: `GetGuardrail` on the pin the record names (or the row's), as
  the eval role (SPEC/09 §11 R4): the version description, the topic names
  and the PII entities. A refused read is written as such; build then reads
  the registry row's digest instead (SPEC/09 §9 cut 3).

A part that cannot be read is written with its error, never left out: build
reads a missing record as unread, and row 9 reads unread as RED. A run file
whose `observed` is null is written `made: false`, every part null, which is
PR 2's own envelope. Exit 0 whenever the file is written.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "milestones" / "M09" / "runs" / "f9_3_plant_run.yaml"
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
REGION = "us-west-2"
REGISTRY = "agentkeel-registry"
SECURITY_ACCOUNT = "897698239547"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
PARTS = ("bucket", "github", "registry", "guardrail")
STEPS = ("first", "second", "third")
PLATFORM_CHECK = "platform-check"
REFUSED = re.compile(r"^- \*\*(.+?)\*\*: ", re.MULTILINE)
SUMMARY_MAX = 8000


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_file(path: Path = RUN) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def digest(baseline: bytes, *agent_files: bytes) -> str:
    """The construct's recipe, computed here from bytes this script fetched itself: baseline first, LF endings."""
    return hashlib.sha256(b"".join(part.replace(b"\r\n", b"\n") for part in (baseline, *agent_files))).hexdigest()


# --- GitHub ---------------------------------------------------------------------


def gh(path: str, *, raw: bool = False) -> Any:
    request = urllib.request.Request(path if path.startswith("http") else f"{API}{path}")
    request.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    return body if raw else json.loads(body)


def check_runs(repository: str, sha: str) -> list[dict[str, Any]]:
    """Every check run on a head: its conclusion, the names its summary says it refused under, the summary itself."""
    runs = gh(f"/repos/{repository}/commits/{sha}/check-runs?per_page=100").get("check_runs") or []
    out = []
    for run in runs:
        summary = (run.get("output") or {}).get("summary")
        refused = REFUSED.findall(summary) if isinstance(summary, str) else None
        out.append({"name": run.get("name"), "app_id": (run.get("app") or {}).get("id"), "conclusion": run.get("conclusion"),
                    "completed_at": run.get("completed_at"), "refused": [] if run.get("conclusion") == "success" else refused,
                    "summary": summary[:SUMMARY_MAX] if isinstance(summary, str) else None})  # fmt: skip
    return out


def pull(repository: str, number: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"pull_request": number, "found": False, "error": None}
    if not isinstance(number, int):
        out["error"] = "no pull request number in the run file"
        return out
    try:
        got = gh(f"/repos/{repository}/pulls/{number}")
        head = got["head"]["sha"]
        out |= {"found": True, "merged": bool(got.get("merged")), "merged_at": got.get("merged_at"), "head_sha": head,
                "merge_commit": got.get("merge_commit_sha") if got.get("merged") else None,
                "check_runs": check_runs(repository, head)}  # fmt: skip
    except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def file_at(repository: str, sha: str, path: str) -> bytes | None:
    """A file's bytes at `sha`, through the API, as `git show <sha>:<path>` would give them; None at a 404."""
    try:
        got = gh(f"/repos/{repository}/contents/{path}?ref={sha}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    if not isinstance(got, dict) or got.get("encoding") != "base64":
        raise ValueError(f"{path}@{sha[:12]}: not a file GitHub would give whole")
    return base64.b64decode(got["content"])


def baseline_on_main() -> tuple[bytes | None, str]:
    """`rules/baseline.yaml` as `git show` reads it on main, never the working tree (cold review N7 on PR 1)."""
    for ref in ("origin/main", "main", "HEAD"):
        shown = subprocess.run(["git", "show", f"{ref}:rules/baseline.yaml"], cwd=ROOT, capture_output=True, check=False)
        if shown.returncode == 0:
            return shown.stdout, ref
    return None, "not found on origin/main, main or HEAD"


def read_github(observation: dict[str, Any]) -> None:
    repository, observed = observation["repository"], observation["observed"]
    pulls = {step: pull(repository, (observed.get(step) or {}).get("pull_request")) for step in STEPS}
    observation["pulls"] = pulls
    merge_commit = pulls["first"].get("merge_commit")
    rules: dict[str, Any] = {"read_from": None, "guardrail": None, "redteam": None, "error": None}
    baseline_bytes, where = baseline_on_main()
    observation["baseline"] = {"read_from": where, "pii": None, "sha256": None}
    if baseline_bytes is not None:
        try:
            loaded = yaml.safe_load(baseline_bytes)
            observation["baseline"] |= {"pii": loaded.get("pii") if isinstance(loaded, dict) else None,
                                        "sha256": hashlib.sha256(baseline_bytes.replace(b"\r\n", b"\n")).hexdigest()}  # fmt: skip
        except yaml.YAMLError as exc:
            observation["baseline"]["error"] = f"{type(exc).__name__}: {exc}"
    if not merge_commit:
        rules["error"] = "the first pull request's merge commit is not known: no rules file is read"
        observation["rules"], observation["tree_digest"] = rules, None
        return
    try:
        guardrail_bytes = file_at(repository, merge_commit, "rules/guardrail.yaml")
        redteam_bytes = file_at(repository, merge_commit, "rules/redteam.yaml")
        rules["read_from"] = f"{repository}@{merge_commit}"
        rules["guardrail"] = yaml.safe_load(guardrail_bytes) if guardrail_bytes is not None else None
        rules["redteam"] = yaml.safe_load(redteam_bytes) if redteam_bytes is not None else None
        files = [b for b in (guardrail_bytes, redteam_bytes) if b is not None]
        observation["tree_digest"] = digest(baseline_bytes, *files) if baseline_bytes is not None and guardrail_bytes is not None else None
    except (urllib.error.URLError, ValueError, yaml.YAMLError, TimeoutError, OSError) as exc:
        rules["error"] = f"{type(exc).__name__}: {exc}"
        observation["tree_digest"] = None
    observation["rules"] = rules


# --- AWS ------------------------------------------------------------------------------


def read_bucket(observation: dict[str, Any]) -> None:
    """The answer record the deploy put, whole: its observations and the guardrail the stack built."""
    import boto3

    agent = observation["agent"]
    key = ((observation["observed"].get("deploy") or {}).get("answer_key"))
    prefix = f"envelopes/agents/{agent}/"
    try:
        client = boto3.client("s3", region_name=REGION)
        if not key:
            listed = [o for page in client.get_paginator("list_objects_v2").paginate(Bucket=AUDIT_BUCKET, Prefix=prefix)
                      for o in page.get("Contents") or [] if o["Key"].endswith(".json") and "retired" not in o["Key"]]  # fmt: skip
            if not listed:
                observation["answer"], observation["answer_error"] = None, f"no object under {prefix}"
                return
            key = max(listed, key=lambda o: o["LastModified"])["Key"]
        got = client.get_object(Bucket=AUDIT_BUCKET, Key=key)
        body = got["Body"].read()
        record = json.loads(body)
        observation["answer"] = {**record, "key": key, "sha256": hashlib.sha256(body).hexdigest(),
                                 "last_modified": got["LastModified"].isoformat().replace("+00:00", "Z")}  # fmt: skip
        observation["answer_error"] = None
    except Exception as exc:  # noqa: BLE001 - an unread record is an observation
        observation["answer"], observation["answer_error"] = None, f"{key or prefix}: {type(exc).__name__}: {exc}"


def read_registry(observation: dict[str, Any]) -> None:
    import boto3

    try:
        item = boto3.client("dynamodb", region_name=REGION).get_item(
            TableName=REGISTRY, Key={"name": {"S": observation["agent"]}}, ConsistentRead=True).get("Item")
        observation["registry"] = None if item is None else {k: next(iter(v.values())) for k, v in item.items()}
        observation["registry_error"] = None if item is not None else "no row for the agent"
    except Exception as exc:  # noqa: BLE001
        observation["registry"], observation["registry_error"] = None, f"{type(exc).__name__}: {exc}"


def read_guardrail(observation: dict[str, Any]) -> None:
    """GetGuardrail on the pin the answer record names, or the registry row's: the version's description and rules."""
    import boto3

    pin = (observation.get("answer") or {}).get("guardrail") or {}
    row = observation.get("registry") or {}
    pin_id = pin.get("id") or row.get("guardrail_id")
    pin_version = pin.get("version") or row.get("guardrail_version")
    if not pin_id or not pin_version:
        observation["read_back"], observation["read_back_error"] = None, "no pin to read back: neither the record nor the row names one"
        return
    try:
        got = boto3.client("bedrock", region_name=REGION).get_guardrail(guardrailIdentifier=pin_id, guardrailVersion=str(pin_version))
        observation["read_back"] = {
            "source": "read_back", "id": got.get("guardrailId"), "version": got.get("version"), "name": got.get("name"),
            "description": got.get("description"), "status": got.get("status"), "read_at": now(),
            "topics": [t.get("name") for t in (got.get("topicPolicy") or {}).get("topics") or []],
            "pii": [{"entity": e.get("type"), "action": e.get("action")}
                    for e in (got.get("sensitiveInformationPolicy") or {}).get("piiEntities") or []],
        }  # fmt: skip
        observation["read_back_error"] = None
    except Exception as exc:  # noqa: BLE001 - a refused read is an observation (R4: the grant may not be deployed)
        observation["read_back"], observation["read_back_error"] = None, f"{pin_id}:{pin_version}: {type(exc).__name__}: {exc}"


# --- the file --------------------------------------------------------------------------


def blank(run: dict[str, Any]) -> dict[str, Any]:
    observed = run.get("observed")
    return {"what": "GitHub's, AWS's and the answer record's record of M09's plant run; not an envelope; rules nothing",
            "looked_up_at": now(), "made": isinstance(observed, dict), "repository": run.get("repository"),
            "agent": run.get("agent"), "observed": observed if isinstance(observed, dict) else {},
            "answer": None, "answer_error": None, "registry": None, "registry_error": None,
            "read_back": None, "read_back_error": None, "pulls": None, "rules": None, "baseline": None,
            "tree_digest": None, "parts": []}  # fmt: skip


def observe(parts: list[str], observation: dict[str, Any]) -> dict[str, Any]:
    if observation["made"]:
        if "bucket" in parts:
            read_bucket(observation)
        if "github" in parts:
            try:
                read_github(observation)
            except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
                observation["rules"] = {"read_from": None, "guardrail": None, "redteam": None, "error": f"{type(exc).__name__}: {exc}"}
        if "registry" in parts:
            read_registry(observation)
        if "guardrail" in parts:
            read_guardrail(observation)
    observation["looked_up_at"] = now()
    observation["parts"] = sorted(set(observation.get("parts", [])) | set(parts))
    return observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--read", required=True, help=f"comma-separated, of {', '.join(PARTS)}")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--run", type=Path, default=RUN)
    args = parser.parse_args(argv)
    parts = [p.strip() for p in args.read.split(",") if p.strip()]
    if unknown := sorted(set(parts) - set(PARTS)):
        print(f"unknown parts {unknown}", file=sys.stderr)
        return 1
    # A run file or an earlier part's file that does not parse is an observation too (security-reviewer on
    # PR 2): written with its error, every part null, never a failed job.
    try:
        observation = json.loads(args.out.read_text(encoding="utf-8")) if args.out.is_file() else blank(run_file(args.run))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        observation = {**blank({}), "error": f"{type(exc).__name__}: {exc}"}
    try:
        observation = observe(parts, observation)
    except Exception as exc:  # noqa: BLE001 - a part that cannot be read is written as such, never a failed job
        observation["error"] = f"{type(exc).__name__}: {exc}"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(observation, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.out} ({', '.join(observation['parts'])}; made {observation['made']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
