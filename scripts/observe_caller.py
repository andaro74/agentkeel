"""Look up M10's live run and write what the audit bucket, the trail and GitHub returned, raw (P5).

    python scripts/observe_caller.py --read bucket --out caller.json    # as agentkeel-audit-read
    python scripts/observe_caller.py --read github --out caller.json    # as the eval role, GITHUB_TOKEN

An instrument, in the pattern of `scripts/observe_rules.py`. It reads the run
file the owner fills after making the four calls,
`milestones/M10/runs/f10_x_caller_run.yaml`, for the repository, the agent's
name, the callers pull request number, the answer record's key, each call's
request id and the bypass call's principal, and nothing else from it: every
state it writes is AWS's, GitHub's or the record's. It writes raw records and
decides nothing; `src/verdict/caller.py` rules on them into the envelope's
`caller` (`build --caller`), and the ledger's row 10 reading reads that
(SPEC/10 §4, §6).

The `observed` block the owner fills (SPEC/10 §5.1), keys only, never a result:

    observed:
      callers: {pull_request: 4}
      deploy:  {run_id: 123456789, answer_key: envelopes/agents/festival-desk/<merge commit>.json}
      admitted: {request_id: ...}
      none:     {request_id: ...}
      stranger: {request_id: ...}
      bypass:   {request_id: ..., principal: arn:aws:sts::<account>:assumed-role/<role>/<session>}

What `stated` is: the caller each step names in the run file (`steps[].caller`:
`issuer: self` is the agent's pool user, `other` a stranger, `null` no token)
and, for the bypass, the principal the owner wrote under `observed`; derived
here so it has one seat-owned source (cold review F3 on M10 PR 1). The outcome
and reason each step must read are fixed by its id (SPEC/10 §2): admitted;
refused for no identity; refused, not admitted; refused, not the door.

Each `--read` part needs its own credentials, so `evals.yml` calls this once
per set and each call merges its part into the same file:

- `bucket`: every object under `calls/agents/<name>/` (the door's access-log
  lines, one object per delivery, each line wrapped with the object's key
  and `LastModified`), stepped by the request id the owner wrote; the
  bypass call's `InvokeAgentRuntime` data event, found by its request id in
  the platform account's trail objects for the days the access-log lines
  span (the trail has carried the runtime data-event selector since M05
  PR 2); and the answer record of the deploy that put the door on, by
  `answer_key`. **A raw record that carries a credential is not copied**:
  its key and the refusal are written in its place (SPEC/10 §2, R5).
- `github`: the callers pull request (merged, merge commit, the platform's
  check runs on its head) and the agent's `manifest.yaml` at that merge
  commit, read through the API by the commit, never from a working tree,
  for its `callers` list.

A part that cannot be read is written with its error, never left out: build
reads a missing record as unread, and row 10 reads unread as RED. A run file
whose `observed` is null is written `made: false`, every part null, which is
PR 2's own envelope. Exit 0 whenever the file is written.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.verdict import caller as reader  # noqa: E402  (refuse_credential: the observer refuses what build refuses)

RUN = ROOT / "milestones" / "M10" / "runs" / "f10_x_caller_run.yaml"
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
REGION = "us-west-2"
AGENT_ACCOUNT = "581208540944"
SECURITY_ACCOUNT = "897698239547"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
CALLS_PREFIX = "calls/agents/{agent}/"
TRAIL_PREFIX = f"AWSLogs/{AGENT_ACCOUNT}/CloudTrail/{REGION}/"
PARTS = ("bucket", "github")
STEPS = ("admitted", "none", "stranger", "bypass")
# What each step's record must read, by its id (SPEC/10 §2, §5): the run file's prose feeds no reading.
OUTCOMES = {"admitted": ("admitted", None), "none": ("refused", "no identity"),
            "stranger": ("refused", "not admitted"), "bypass": ("refused", "not the door")}  # fmt: skip
PLATFORM_CHECK = "platform-check"
REFUSED = re.compile(r"^- \*\*(.+?)\*\*: ", re.MULTILINE)
SUMMARY_MAX = 8000
WINDOW_BEFORE, WINDOW_AFTER = timedelta(hours=1), timedelta(hours=2)


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value: Any) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(UTC)


def run_file(path: Path = RUN) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def stated_from(run: dict[str, Any]) -> dict[str, Any]:
    """`{step: {subject, outcome, reason}}` from `steps[].caller` and `observed.bypass.principal`."""
    observed = run.get("observed") if isinstance(run.get("observed"), dict) else {}
    out: dict[str, Any] = {}
    for step in run.get("steps") or []:
        if not isinstance(step, dict) or step.get("id") not in OUTCOMES:
            continue
        outcome, reason = OUTCOMES[step["id"]]
        named = step.get("caller")
        if step["id"] == "bypass":
            subject = (observed.get("bypass") or {}).get("principal")
        elif isinstance(named, dict) and named.get("issuer") in ("self", "other"):
            subject = named.get("subject")
        else:
            subject = None
        out[step["id"]] = {"subject": subject, "outcome": outcome, "reason": reason}
    return out


# --- GitHub ---------------------------------------------------------------------


def gh(path: str) -> Any:
    request = urllib.request.Request(path if path.startswith("http") else f"{API}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token := os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def check_runs(repository: str, sha: str) -> list[dict[str, Any]]:
    runs = gh(f"/repos/{repository}/commits/{sha}/check-runs?per_page=100").get("check_runs") or []
    out = []
    for run in runs:
        summary = (run.get("output") or {}).get("summary")
        refused = REFUSED.findall(summary) if isinstance(summary, str) else None
        out.append({"name": run.get("name"), "app_id": (run.get("app") or {}).get("id"), "conclusion": run.get("conclusion"),
                    "completed_at": run.get("completed_at"), "refused": [] if run.get("conclusion") == "success" else refused,
                    "summary": summary[:SUMMARY_MAX] if isinstance(summary, str) else None})  # fmt: skip
    return out


def file_at(repository: str, sha: str, path: str) -> bytes | None:
    try:
        got = gh(f"/repos/{repository}/contents/{path}?ref={sha}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    if not isinstance(got, dict) or got.get("encoding") != "base64":
        raise ValueError(f"{path}@{sha[:12]}: not a file GitHub would give whole")
    return base64.b64decode(got["content"])


def read_github(observation: dict[str, Any]) -> None:
    repository, observed = observation["repository"], observation["observed"]
    number = (observed.get("callers") or {}).get("pull_request")
    pull: dict[str, Any] = {"pull_request": number, "found": False, "error": None}
    observation["pull"], observation["callers"], observation["manifest_error"] = pull, None, None
    if not isinstance(number, int):
        pull["error"] = "no pull request number in the run file"
        return
    try:
        got = gh(f"/repos/{repository}/pulls/{number}")
        head = got["head"]["sha"]
        pull |= {"found": True, "merged": bool(got.get("merged")), "merged_at": got.get("merged_at"), "head_sha": head,
                 "merge_commit": got.get("merge_commit_sha") if got.get("merged") else None, "check_runs": check_runs(repository, head)}  # fmt: skip
    except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
        pull["error"] = f"{type(exc).__name__}: {exc}"
        return
    if not pull["merge_commit"]:
        observation["manifest_error"] = "the callers pull request is not merged: no manifest is read"
        return
    try:
        raw = file_at(repository, pull["merge_commit"], "manifest.yaml")
        manifest = yaml.safe_load(raw) if raw is not None else None
        callers = manifest.get("callers") if isinstance(manifest, dict) else None
        observation["callers"] = callers if isinstance(callers, list) else None
        if observation["callers"] is None:
            observation["manifest_error"] = f"manifest.yaml@{pull['merge_commit'][:12]}: no callers list"
    except (urllib.error.URLError, ValueError, yaml.YAMLError, TimeoutError, OSError) as exc:
        observation["manifest_error"] = f"{type(exc).__name__}: {exc}"


# --- AWS ------------------------------------------------------------------------------


def objects(s3: Any, prefix: str) -> list[dict[str, Any]]:
    found = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=AUDIT_BUCKET, Prefix=prefix):
        for obj in page.get("Contents") or []:
            found.append({"key": obj["Key"], "last_modified": iso(parse_time(obj["LastModified"]))})
    return sorted(found, key=lambda o: o["last_modified"])


def body(s3: Any, key: str) -> bytes:
    raw = s3.get_object(Bucket=AUDIT_BUCKET, Key=key)["Body"].read()
    return gzip.decompress(raw) if key.endswith(".gz") or raw[:2] == b"\x1f\x8b" else raw


def lines_of(data: bytes) -> list[dict[str, Any]]:
    """Each JSON object in a delivered object: one per line (the door's access log through Firehose), or the
    messages of a CloudWatch Logs batch where the delivery left that envelope on."""
    text = data.decode("utf-8", errors="replace")
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            doc = json.loads(line)
        except ValueError:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("logEvents"), list):
            for event in doc["logEvents"]:
                try:
                    inner = json.loads(event.get("message", ""))
                except (ValueError, AttributeError):
                    continue
                if isinstance(inner, dict):
                    out.append(inner)
        elif isinstance(doc, dict):
            out.append(doc)
    return out


def wrap(source: str, key: str, last_modified: str, raw: dict[str, Any], step: str | None) -> dict[str, Any]:
    """The observer's wrapper; a raw record that carries a credential is not copied (R5)."""
    try:
        reader.refuse_credential(raw)
    except reader.Credential as exc:
        return {"source": source, "key": key, "last_modified": last_modified, "step": step, "raw": None, "dropped": [],
                "error": str(exc)}  # fmt: skip
    # The caller's address, user agent, key id and the rest of DROPPED_KEYS never leave the bucket (R5): what is
    # copied is what AWS delivered less the named keys, and the names are written beside it.
    kept, dropped = reader.redact(raw)
    return {"source": source, "key": key, "last_modified": last_modified, "step": step, "raw": kept, "dropped": dropped,
            "error": None}  # fmt: skip


def read_bucket(observation: dict[str, Any]) -> None:
    import boto3

    s3 = boto3.client("s3", region_name=REGION)
    observed, agent = observation["observed"], observation["agent"]
    by_request = {(observed.get(step) or {}).get("request_id"): step for step in STEPS}
    by_request.pop(None, None)
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    # The door's access-log objects, every line.
    prefix = CALLS_PREFIX.format(agent=agent)
    try:
        for obj in objects(s3, prefix):
            for line in lines_of(body(s3, obj["key"])):
                step = by_request.get(line.get("request_id"))
                if line.get("agent") != agent:
                    # Under this agent's prefix and naming another: not copied, named (security-reviewer F1 on PR 2).
                    records.append({"source": "access-log", "key": obj["key"], "last_modified": obj["last_modified"],
                                    "step": step, "raw": None, "dropped": [],
                                    "error": f"the line names agent {line.get('agent')!r} under {prefix}"})  # fmt: skip
                    continue
                records.append(wrap("access-log", obj["key"], obj["last_modified"], line, step))
    except Exception as exc:  # noqa: BLE001 - an unread prefix is an observation
        errors.append(f"{prefix}: {type(exc).__name__}: {exc}")
    # The bypass call's data event, by its request id, in the trail's objects for the days the lines span.
    bypass_id = (observed.get("bypass") or {}).get("request_id")
    times = [reader.iso_of_epoch_ms(r["raw"].get("time_epoch_ms")) for r in records if r.get("raw") and r.get("step")]
    times = [parse_time(t) for t in times if t]
    if bypass_id:
        start = (min(times) - WINDOW_BEFORE) if times else datetime.now(UTC) - timedelta(days=1)
        end = (max(times) + WINDOW_AFTER) if times else datetime.now(UTC)
        try:
            day = start.date()
            while day <= end.date():
                for obj in objects(s3, f"{TRAIL_PREFIX}{day:%Y/%m/%d}/"):
                    if not (start - timedelta(minutes=1) <= parse_time(obj["last_modified"]) <= end + timedelta(hours=1)):
                        continue
                    for record in json.loads(body(s3, obj["key"])).get("Records") or []:
                        if record.get("eventName") == "InvokeAgentRuntime" and record.get("requestID") == bypass_id:
                            records.append(wrap("data-event", obj["key"], obj["last_modified"], record, "bypass"))
                day += timedelta(days=1)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{TRAIL_PREFIX}: {type(exc).__name__}: {exc}")
        if not any(r.get("step") == "bypass" for r in records):
            errors.append(f"no InvokeAgentRuntime data event with request id {bypass_id} in the trail's objects "
                          f"between {iso(start)} and {iso(end)}")  # fmt: skip
    observation["records"], observation["records_errors"] = records, errors
    # The answer record of the deploy that put the door on, whole.
    key = (observed.get("deploy") or {}).get("answer_key")
    if not key:
        observation["answer"], observation["answer_error"] = None, "no answer_key in the run file"
        return
    try:
        got = s3.get_object(Bucket=AUDIT_BUCKET, Key=key)
        observation["answer"] = {**json.loads(got["Body"].read()), "key": key,
                                 "last_modified": iso(parse_time(got["LastModified"]))}  # fmt: skip
        observation["answer_error"] = None
    except Exception as exc:  # noqa: BLE001
        observation["answer"], observation["answer_error"] = None, f"{key}: {type(exc).__name__}: {exc}"


# --- the file --------------------------------------------------------------------------


def blank(run: dict[str, Any]) -> dict[str, Any]:
    observed = run.get("observed")
    return {"what": "AWS's, GitHub's and the records' record of M10's live run; not an envelope; rules nothing",
            "looked_up_at": now(), "made": isinstance(observed, dict), "repository": run.get("repository"),
            "agent": run.get("agent"), "observed": observed if isinstance(observed, dict) else {},
            "stated": stated_from(run), "records": None, "records_errors": None, "answer": None, "answer_error": None,
            "pull": None, "callers": None, "manifest_error": None, "parts": []}  # fmt: skip


def observe(parts: list[str], observation: dict[str, Any]) -> dict[str, Any]:
    if observation["made"]:
        if "bucket" in parts:
            read_bucket(observation)
        if "github" in parts:
            try:
                read_github(observation)
            except (urllib.error.URLError, KeyError, TimeoutError, OSError) as exc:
                observation["manifest_error"] = f"{type(exc).__name__}: {exc}"
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
