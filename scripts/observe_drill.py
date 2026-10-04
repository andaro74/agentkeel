"""Look up the game-day drill's three runs in the security account's audit bucket and write what AWS recorded (P5).

    python scripts/observe_drill.py milestones/M08/runs/drill_run1.yaml \
        milestones/M08/runs/drill_run2.yaml milestones/M08/runs/drill_run3.yaml --out drill.json

An instrument, in the pattern of `scripts/observe_containment.py`. It reads
each run file the owner filled after making the run, and reads the audit
bucket in the security account as `agentkeel-audit-read` (`infra/security/`):
the trail's records, the flow records, the answer record, the bucket's
listing with each object's versions and retention, and (for run 3) the
registry row and panel 1 through Grafana. It writes raw records and decides
nothing: `src/verdict/drill.py` reads the observation into the envelope's
`drill` field (`build --drill`), and the ledger's row 8 reading is what turns
it into a measurement (SPEC/08 §4, §6). M08 builds no control (ADR-0013).

**The attempt's time is AWS's, never a person's** (SPEC/08 §2). The run file's
`observed` block names only the lookup keys — a request id, an ENI and a
destination, an object key, a session id, a window — never a result. What is
written for each record is its own time (CloudTrail's `eventTime`, the flow
record's `start`) and the time its object reached the bucket (`LastModified`).
A record not found is written as not found; `build` reads that as unrecorded
and row 8 reads it as absent. **A run file names the attempts, not the
records** (SPEC/08 finding 9): the records row 8 rests on are what this finds.

The `observed` each run carries, filled by the owner before its reading
(SPEC/08 §5.1):

- run 1: `window` (opened, closed=the detach), `attempts` — one entry per
  attempt a1 to a6, each `{id, kind}` plus the key its kind needs: a trail
  attempt (a4, a5, a6) a `request_id`; the flow attempt (a1) an `eni` and a
  `destination`; the answer attempt (a3) an `object_key`; the unread attempt
  (a2) `kind: none`. And `quarantine`: `role`, `attached_at`, `detached_at`.
- run 2: `window`, `attempt` a1 with `eni`, `destination` and `request_id`.
- run 3: `window`, `answer_key`, `role`.
- run 1's evidence is read at PR 3's run, after the detach closes run 1
  (SPEC/08 §5.1): `evidence` names the `records` (key, kind) the runs rest on.

Exit 0 when the observation is written, whatever it says; 1 only when it
could not be written at all. No credentials, or a bucket this role cannot
read, is an observation too (`readable: false`, every run null).
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

REGION = "us-west-2"
AGENT_ACCOUNT = "581208540944"
SECURITY_ACCOUNT = "897698239547"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
TRAIL_REGIONS = ("us-west-2", "us-east-1")
BEFORE = timedelta(minutes=30)
DELIVERY = timedelta(hours=3)
# The drill-agent role, by its path. A redeploy that replaces the role changes the name, and then its
# events read as another writer: closed, not open (as refagent's did at M05).
DRILL_ROLE_FRAGMENT = ":role/agentkeel/agents/agentkeel-drill-agent"


def parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z") if value else None


def days(start: datetime, end: datetime) -> list[datetime]:
    out, day = [], start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= end:
        out.append(day)
        day += timedelta(days=1)
    return out


def principal(record: dict[str, Any]) -> str:
    identity = record.get("userIdentity") or {}
    issuer = ((identity.get("sessionContext") or {}).get("sessionIssuer") or {}).get("arn")
    return issuer or identity.get("arn") or identity.get("principalId") or ""


class Bucket:
    """The audit bucket as the read role sees it: objects by prefix and time, each body read at most once."""

    def __init__(self, s3: Any, name: str = AUDIT_BUCKET) -> None:
        self.s3, self.name = s3, name
        self._bodies: dict[str, bytes] = {}

    def objects(self, prefix: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        found = []
        for page in self.s3.get_paginator("list_objects_v2").paginate(Bucket=self.name, Prefix=prefix):
            for obj in page.get("Contents", []):
                modified = parse_time(obj["LastModified"])
                if start <= modified <= end:
                    found.append({"key": obj["Key"], "last_modified": modified})
        return found

    def body(self, key: str) -> bytes:
        if key not in self._bodies:
            raw = self.s3.get_object(Bucket=self.name, Key=key)["Body"].read()
            self._bodies[key] = gzip.decompress(raw) if key.endswith(".gz") else raw
        return self._bodies[key]

    def versions_and_retention(self, key: str) -> dict[str, Any]:
        """Every version of `key`, and each one's retain-until date as it stands now (F8.4)."""
        versions = []
        for page in self.s3.get_paginator("list_object_versions").paginate(Bucket=self.name, Prefix=key):
            for version in page.get("Versions", []):
                if version["Key"] != key:
                    continue
                try:
                    got = self.s3.get_object_retention(Bucket=self.name, Key=key, VersionId=version["VersionId"])
                    retention = {"mode": got["Retention"]["Mode"], "until": iso(parse_time(got["Retention"]["RetainUntilDate"]))}
                except Exception as exc:  # noqa: BLE001 - what it could not read is written as such
                    retention = {"mode": None, "until": f"unread: {type(exc).__name__}"}
                versions.append({"version_id": version["VersionId"], "last_modified": iso(parse_time(version["LastModified"])),
                                 "retention": retention})  # fmt: skip
        return {"versions": versions, "found": bool(versions)}


class Trails:
    """Both trails' records delivered in a window, parsed once: (record, key, last_modified)."""

    def __init__(self, bucket: Bucket, start: datetime, end: datetime) -> None:
        self.records: list[tuple[dict[str, Any], str, datetime]] = []
        for account in (AGENT_ACCOUNT, SECURITY_ACCOUNT):
            for region in TRAIL_REGIONS:
                for day in days(start, end):
                    prefix = f"AWSLogs/{account}/CloudTrail/{region}/{day:%Y/%m/%d}/"
                    for obj in bucket.objects(prefix, start, end):
                        for record in json.loads(bucket.body(obj["key"])).get("Records", []):
                            self.records.append((record, obj["key"], obj["last_modified"]))

    def by_request(self, request_id: str) -> dict[str, Any]:
        for record, key, modified in sorted(self.records, key=lambda item: item[2]):
            if record.get("requestID") == request_id:
                params = record.get("requestParameters") or {}
                return {"found": True, "kind": "trail", "key": key, "last_modified": iso(modified),
                        "event_name": record.get("eventName"), "error_code": record.get("errorCode"),
                        "error_message": record.get("errorMessage"), "request_id": request_id,
                        "object_key": params.get("key"), "principal": principal(record),
                        "event_time": record.get("eventTime")}  # fmt: skip
        return {"found": False}

    def refusals_by_role(self, role_fragment: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Every refused call (an errorCode) by the role in the window, one per event, earliest first."""
        seen: dict[Any, dict[str, Any]] = {}
        for record, key, modified in sorted(self.records, key=lambda item: item[2]):
            if (record.get("errorCode") and role_fragment in principal(record)
                    and start <= parse_time(record["eventTime"]) <= end):  # fmt: skip
                ident = record.get("eventID") or (record.get("requestID"), record.get("eventTime"))
                seen.setdefault(ident, {"role": principal(record), "event_name": record.get("eventName"),
                                        "error_code": record.get("errorCode"), "event_time": record.get("eventTime"),
                                        "last_modified": iso(modified), "key": key})  # fmt: skip
        return sorted(seen.values(), key=lambda r: r["event_time"])

    def calls_by_role(self, role_fragment: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Every call by the role in the window, answered or refused: for the quarantine reading (F8.5)."""
        out = []
        for record, _key, modified in sorted(self.records, key=lambda item: item[2]):
            if role_fragment in principal(record) and start <= parse_time(record["eventTime"]) <= end:
                out.append({"event_name": record.get("eventName"), "answered": not record.get("errorCode"),
                            "error_code": record.get("errorCode"), "event_time": record.get("eventTime")})  # fmt: skip
        return out


def flow_record(bucket: Bucket, eni: str, destination: str, start: datetime, end: datetime) -> dict[str, Any]:
    """The flow record for `eni` to `destination` on 443, earliest delivery; not found is not found (a1)."""
    for day in days(start, end):
        prefix = f"AWSLogs/{AGENT_ACCOUNT}/vpcflowlogs/{REGION}/{day:%Y/%m/%d}/"
        for obj in sorted(bucket.objects(prefix, start, end), key=lambda o: o["last_modified"]):
            for line in bucket.body(obj["key"]).decode("utf-8").splitlines():
                fields = line.split()
                # version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action status
                if len(fields) < 14 or fields[2] != eni or fields[4] != destination:
                    continue
                return {"found": True, "kind": "flow", "key": obj["key"], "last_modified": iso(obj["last_modified"]),
                        "flow_action": fields[12], "event_time": iso(datetime.fromtimestamp(int(fields[10]), UTC)),
                        "eni": eni, "destination": destination}  # fmt: skip
    return {"found": False}


def window_of(run: dict[str, Any], observed: dict[str, Any]) -> tuple[datetime, datetime]:
    w = observed.get("window") or run.get("window") or {}
    opened = parse_time(w["opened"]) if w.get("opened") else datetime.now(UTC) - BEFORE
    closed = parse_time(w["closed"]) if w.get("closed") else datetime.now(UTC)
    return opened, closed


# --- each run ------------------------------------------------------------------


def read_run1(run: dict[str, Any], bucket: Bucket) -> dict[str, Any]:
    observed = run.get("observed") or {}
    opened, closed = window_of(run, observed)
    trails = Trails(bucket, opened - BEFORE, closed + DELIVERY)
    attempts = []
    for entry in observed.get("attempts") or []:
        aid, kind = entry.get("id"), entry.get("kind")
        if kind == "flow":
            record = flow_record(bucket, entry.get("eni"), entry.get("destination"), opened - BEFORE, closed + DELIVERY)
            refused = (record.get("flow_action") == "REJECT") if record.get("found") else None
        elif kind == "answer":
            found = bucket.objects(entry.get("object_key", ""), opened - BEFORE, closed + DELIVERY)
            record = {"found": bool(found), "kind": "answer", "key": entry.get("object_key"),
                      "last_modified": iso(found[0]["last_modified"]) if found else None}  # fmt: skip
            refused = False  # a3 is recorded, not refused
        elif kind == "none":
            record, refused = {"found": False}, None  # a2 is unread on both halves
        else:
            record = trails.by_request(entry.get("request_id", ""))
            refused = (record.get("error_code") is not None) if record.get("found") else None
        attempts.append({"id": aid, "refused": refused, "record": record})
    return {"window": {"opened": iso(opened), "closed": iso(closed)}, "attempts": attempts}


def read_run1_quarantine(run: dict[str, Any], bucket: Bucket) -> dict[str, Any] | None:
    q = (run.get("observed") or {}).get("quarantine")
    if not q:
        return None
    attached, detached = parse_time(q["attached_at"]), parse_time(q["detached_at"])
    trails = Trails(bucket, attached - BEFORE, detached + DELIVERY)
    role = q["role"]
    return {"run": "run1-quarantine", "role": role, "attached_at": iso(attached), "detached_at": iso(detached),
            "calls_after_attach": trails.calls_by_role(role, attached, detached),
            "refused_calls_in_window": trails.refusals_by_role(role, attached, detached)}  # fmt: skip


def read_run2(run: dict[str, Any], bucket: Bucket) -> dict[str, Any]:
    observed = run.get("observed") or {}
    opened, closed = window_of(run, observed)
    trails = Trails(bucket, opened - BEFORE, closed + DELIVERY)
    flow = flow_record(bucket, observed.get("eni"), observed.get("destination"), opened - BEFORE, closed + DELIVERY)
    iam = trails.by_request(observed.get("request_id", ""))
    return {"run": "run2", "attempt": "a1", "window": {"opened": iso(opened), "closed": iso(closed)},
            "flow": flow, "iam": iam if iam.get("found") else {"found": False}}  # fmt: skip


def read_run3(run: dict[str, Any], bucket: Bucket, panel1: dict[str, Any] | None) -> dict[str, Any]:
    observed = run.get("observed") or {}
    opened, closed = window_of(run, observed)
    trails = Trails(bucket, opened - BEFORE, closed + DELIVERY)
    role = observed.get("role", DRILL_ROLE_FRAGMENT)
    answer_record: dict[str, Any] = {"verdict": None, "goldens": {}}
    found = bucket.objects(observed.get("answer_key", ""), opened - BEFORE, closed + DELIVERY)
    if found:
        body = json.loads(bucket.body(found[0]["key"]))
        answer_record = {"verdict": body.get("verdict"),
                         "goldens": {g: {"pass": v.get("pass")} for g, v in (body.get("goldens") or {}).items()}}  # fmt: skip
    return {"run": "run3", "window": {"opened": iso(opened), "closed": iso(closed)},
            "answer_record": answer_record,
            "refusals": trails.refusals_by_role(role, opened, closed),
            "rejected_flows": observed.get("rejected_flows") or [],
            "registry_row_in_panel1": registry_in_panel1(panel1, observed.get("registry_row"))}  # fmt: skip


def read_evidence(run: dict[str, Any], bucket: Bucket) -> dict[str, Any]:
    observed = run.get("observed") or {}
    evidence = observed.get("evidence")
    if not evidence:
        return {}
    opened, closed = window_of(run, observed)
    trails = Trails(bucket, opened - BEFORE, closed + DELIVERY)
    role = observed.get("role", DRILL_ROLE_FRAGMENT)
    records = []
    for named in evidence.get("records") or []:
        state = bucket.versions_and_retention(named["key"])
        latest = max(state["versions"], key=lambda v: v["last_modified"]) if state["found"] else None
        records.append({"key": named["key"], "kind": named.get("kind", "delivered"), "found": state["found"],
                        "versions": len(state["versions"]),
                        "last_modified": latest["last_modified"] if latest else None,
                        "retention": latest["retention"] if latest else None})  # fmt: skip
    named_keys = {r["key"] for r in evidence.get("records") or []}
    unnamed = [r for r in trails.refusals_by_role(role, opened, closed) if r["key"] not in named_keys]
    return {"run": "run1", "window": {"opened": iso(opened), "closed": iso(closed)},
            "records": records, "unnamed_refusals": unnamed}  # fmt: skip


def registry_in_panel1(panel1: dict[str, Any] | None, row: str | None) -> bool:
    """Whether panel 1's frame carries the drill agent's registry row (F8.3's third arm). False when unread."""
    if not panel1 or not row:
        return False
    return row in json.dumps(panel1)


def read_panel1() -> dict[str, Any] | None:
    path = os.environ.get("AGENTKEEL_PANEL_FILE")
    if path and Path(path).is_file():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
    return None


def observe(runs: dict[str, dict[str, Any]], s3: Any) -> dict[str, Any]:
    bucket = Bucket(s3)
    panel1 = read_panel1()
    run1, run2, run3 = runs.get("run1"), runs.get("run2"), runs.get("run3")
    made = lambda run: bool(run and run.get("observed"))  # noqa: E731
    return {
        "run1": read_run1(run1, bucket) if made(run1) else None,
        "quarantine": read_run1_quarantine(run1, bucket) if made(run1) else None,
        "run2": read_run2(run2, bucket) if made(run2) else None,
        "run3": read_run3(run3, bucket, panel1) if made(run3) else None,
        "evidence": read_evidence(run1, bucket) or None if made(run1) else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    runs = {}
    for path in args.runs:
        run = yaml.safe_load(path.read_text(encoding="utf-8"))
        runs[run["seed"]] = run | {"path": path.as_posix()}

    result: dict[str, Any] = {
        "what": "the audit bucket's record of M08's game-day drill; not an envelope; rules nothing",
        "looked_up_at": iso(datetime.now(UTC)), "bucket": AUDIT_BUCKET, "readable": True,
        "runs": [run["path"] for run in runs.values()],
    }  # fmt: skip
    try:
        import boto3

        result |= observe(runs, boto3.client("s3", region_name=REGION))
    except Exception as exc:  # noqa: BLE001 - no credentials, a denied read: an observation, not a crash
        result |= {"readable": False, "error": f"{type(exc).__name__}: {exc}",
                   "run1": None, "quarantine": None, "run2": None, "run3": None, "evidence": None}  # fmt: skip

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8",
                        newline="\n")  # fmt: skip
    made = sum(result.get(name) is not None for name in ("run1", "run2", "run3"))
    print(f"wrote {args.out}: {made} of 3 runs made; readable {result['readable']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
