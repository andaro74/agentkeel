"""Look up M05's attempts in the security account's audit bucket and write what AWS recorded (P5).

    python scripts/observe_containment.py milestones/M05/runs/f5_*.yaml --out containment.json

An instrument, in the pattern of `scripts/observe_attempt.py` and
`observe_ingest.py`. It reads each run file the human filled after making an
attempt, and reads the audit bucket in the security account as
`agentkeel-audit-read` (`infra/security/`): the two trails' records, the
flow log's records, refagent's refusal events and seed S6's object. It
writes raw records and decides nothing: `src/verdict/build.py` reads the
observation into the envelope's `containment` and `alarm_latency_s`
(`--containment`), and the ledger's row 5 reading is what turns them into a
measurement (SPEC/05 §4).

**The attempt's time is AWS's, never the human's** (SPEC/05 §2, finding 8).
The `at` a human wrote only opens the window searched. What is written for
each attempt is the record's own time (CloudTrail's `eventTime`, the flow
record's `start`) and the time the record's object reached the bucket (its
`LastModified`). An attempt whose record is not found is written as not
found; build reads that as unrecorded, and row 5 reads it as absent.

What each seed's entry records (SPEC/05 §5):

- S1: the flow records for the ENI and 1.1.1.1 the human named, each with
  its `start`, `action` and the object it came in;
- S2, S3, S6: the trail's record of each request id, from both accounts'
  trails, with `errorCode`, `errorMessage` and the principal it names
  (M03 open.md row 11, item a: the refusing principal is read, not only
  the code); for S2 whether an object is at the key, and for S6 the test
  object's versions and each one's retain-until date as they stand now;
- S4: the trail's record of the `InvokeAgentRuntime` call (by the session
  id the human passed, which CloudTrail records only in the response of a
  call that returned; a refused call is the one invocation by the caller
  within two minutes of the run file's `at`), refagent's refusal event for that session and the
  trail's record of who put it, and every model call refagent's role made
  in the minutes around it (SPEC/05 §2, self-reported);
- S7: the attach, the invocation, the model calls refagent's role made
  between the attach and the detach, and the detach. Before any of that,
  the last attach or detach of the quarantine on refagent's role, from the
  trail: a quarantine still attached is written first (SPEC/05 §6).

Exit 0 when the observation is written, whatever it says; 1 only when it
could not be written at all. No credentials, or a bucket this role cannot
read, is an observation too (`readable: false`).
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

REGION = "us-west-2"
AGENT_ACCOUNT = "581208540944"
SECURITY_ACCOUNT = "897698239547"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
# The trails' regions: refagent's calls in us-west-2; IAM's (S7's attach and detach) are global, recorded in us-east-1.
TRAIL_REGIONS = ("us-west-2", "us-east-1")
BEFORE = timedelta(minutes=30)  # either side of the human's `at` for the event itself
DELIVERY = timedelta(hours=3)  # how long after it an object is still looked for: a late record is late, not absent
MODEL_EVENTS = ("Converse", "ConverseStream", "InvokeModel", "InvokeModelWithResponseStream")
REFAGENT_ROLE = ":role/agentkeel/agents/agentkeel-refagent-RefagentRole5888DB41-i9IqTXU6NVSL"
QUARANTINE = f"arn:aws:iam::{AGENT_ACCOUNT}:policy/agentkeel-quarantine"
EVENTS_PREFIX = "agents/refagent/events/"
RUNTIME = f"arn:aws:bedrock-agentcore:{REGION}:{AGENT_ACCOUNT}:runtime/refagent-Du2VJx6xWc"
# Who makes S4's and S7's invocations: the human's admin user (infra/audit's ADMIN), as the run files say.
CALLER = f"arn:aws:iam::{AGENT_ACCOUNT}:user/hector.acevedo"
# How far from the run file's `at` a failed invocation is looked for, when its record carries no session id.
NEAR = timedelta(minutes=2)


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


class Bucket:
    """The audit bucket as the read role sees it: objects listed by prefix and time, each read at most once."""

    def __init__(self, s3: Any, name: str = AUDIT_BUCKET) -> None:
        self.s3, self.name = s3, name
        self._bodies: dict[str, bytes] = {}

    def objects(self, prefix: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Objects under `prefix` whose LastModified is in [start, end]."""
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


class Trails:
    """Both trails' records delivered in a window, parsed once: (record, the object's key, its LastModified)."""

    def __init__(self, bucket: Bucket, start: datetime, end: datetime) -> None:
        self.records: list[tuple[dict[str, Any], str, datetime]] = []
        for account in (AGENT_ACCOUNT, SECURITY_ACCOUNT):
            for region in TRAIL_REGIONS:
                for day in days(start, end):
                    prefix = f"AWSLogs/{account}/CloudTrail/{region}/{day:%Y/%m/%d}/"
                    for obj in bucket.objects(prefix, start, end):
                        for record in json.loads(bucket.body(obj["key"])).get("Records", []):
                            self.records.append((record, obj["key"], obj["last_modified"]))

    def matching(self, **wanted: Any) -> list[dict[str, Any]]:
        """Every record with these fields, earliest delivery first. `session` matches runtimeSessionId.

        CloudTrail records InvokeAgentRuntime's session id in `responseElements`, not in `requestParameters`
        (null), and only when the call returned: a call the runtime answered with an error has neither (M05 PR
        3, read in the audit bucket: S7's 200 carries it, S4's RuntimeClientError does not)."""
        out = []
        for record, key, modified in self.records:
            params = {**(record.get("responseElements") or {}), **(record.get("requestParameters") or {})}
            if "request_id" in wanted and record.get("requestID") != wanted["request_id"]:
                continue
            if "event_name" in wanted and record.get("eventName") != wanted["event_name"]:
                continue
            if "session" in wanted and params.get("runtimeSessionId") != wanted["session"]:
                continue
            out.append(shaped(record, key, modified))
        return sorted(out, key=lambda r: r["last_modified"])

    def invocations_near(self, caller: str, at: datetime) -> list[dict[str, Any]]:
        """refagent's runtime invoked by `caller` within NEAR of `at`, one record per event."""
        out = {}
        for record, key, modified in self.records:
            if (record.get("eventName") == "InvokeAgentRuntime" and principal(record) == caller
                    and any(r.get("ARN") == RUNTIME for r in record.get("resources") or [])
                    and abs(parse_time(record["eventTime"]) - at) <= NEAR):  # fmt: skip
                out.setdefault(record.get("eventID"), shaped(record, key, modified))
        return sorted(out.values(), key=lambda r: r["event_time"])

    def by_role(self, role_fragment: str, event_names: Iterable[str], start: datetime, end: datetime) -> list[dict]:
        names = set(event_names)
        out = [shaped(record, key, modified) for record, key, modified in self.records
               if record.get("eventName") in names and role_fragment in principal(record)
               and start <= parse_time(record["eventTime"]) <= end]  # fmt: skip
        # One record per event: both trails can carry the same call.
        unique = {r["event_id"] or (r["request_id"], r["event_time"]): r for r in sorted(out, key=lambda r: r["last_modified"], reverse=True)}
        return sorted(unique.values(), key=lambda r: r["event_time"])


def principal(record: dict[str, Any]) -> str:
    """Who the record says made the call: the role's own ARN (with its path) for an assumed role (item a)."""
    identity = record.get("userIdentity") or {}
    issuer = ((identity.get("sessionContext") or {}).get("sessionIssuer") or {}).get("arn")
    return issuer or identity.get("arn") or identity.get("principalId") or ""


def shaped(record: dict[str, Any], key: str, modified: datetime) -> dict[str, Any]:
    params = record.get("requestParameters") or {}
    return {
        "found": True, "key": key, "last_modified": iso(modified), "event_time": record.get("eventTime"),
        "event_id": record.get("eventID"), "event_name": record.get("eventName"),
        "event_source": record.get("eventSource"), "request_id": record.get("requestID"),
        "recipient_account": record.get("recipientAccountId"), "error_code": record.get("errorCode"),
        "error_message": record.get("errorMessage"), "principal": principal(record),
        "object_key": params.get("key"), "policy_arn": params.get("policyArn"), "role_name": params.get("roleName"),
    }  # fmt: skip


NOT_FOUND = {"found": False}


# --- each kind of attempt --------------------------------------------------------------


def api_attempt(attempt: dict[str, Any], entry: dict[str, Any], trails: Trails) -> dict[str, Any]:
    request_id = entry.get("request_id")
    # By the request id alone, which is the call's own: CloudTrail's event name need not be the API's. It logged
    # S6's lock-off, the API PutObjectLockConfiguration, as PutBucketObjectLockConfiguration, and matching the
    # run file's name read a recorded refusal as unrecorded (#31's first run). Each record keeps the name it has.
    records = trails.matching(request_id=request_id) if request_id else []
    return {"what": attempt["what"], "event_name": attempt.get("event_name"), "request_id": entry.get("request_id"),
            "records": records, "human_said": {"result": entry.get("result"), "message": entry.get("message")}}  # fmt: skip


def flow_attempt(attempt: dict[str, Any], entry: dict[str, Any], bucket: Bucket, at: datetime) -> dict[str, Any]:
    eni, destination = entry.get("eni"), entry.get("destination")
    start, end = at - BEFORE, at + DELIVERY
    records = []
    for day in days(start, end):
        prefix = f"AWSLogs/{AGENT_ACCOUNT}/vpcflowlogs/{REGION}/{day:%Y/%m/%d}/"
        for obj in bucket.objects(prefix, start, end):
            for line in bucket.body(obj["key"]).decode("utf-8").splitlines():
                fields = line.split()
                # version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
                if len(fields) < 14 or fields[2] != eni or fields[4] != destination:
                    continue
                records.append({"found": True, "key": obj["key"], "last_modified": iso(obj["last_modified"]),
                                "start": iso(datetime.fromtimestamp(int(fields[10]), UTC)), "action": fields[12],
                                "dstport": fields[6], "srcaddr": fields[3]})  # fmt: skip
    return {"what": attempt["what"], "eni": eni, "destination": destination, "records": records,
            "human_said": {"connected": entry.get("connected"), "result": entry.get("result")}}  # fmt: skip


def session_attempt(attempt: dict[str, Any], entry: dict[str, Any], trails: Trails, bucket: Bucket,
                    *, until: datetime | None = None) -> dict[str, Any]:  # fmt: skip
    """An InvokeAgentRuntime call, by its session id, and the model calls refagent's role made around it."""
    session = entry.get("session_id")
    invoke = trails.matching(session=session, event_name="InvokeAgentRuntime") if session else []
    matched_by = "session id" if invoke else None
    if not invoke and entry.get("at"):
        # A call the runtime answered with an error carries no session id in its record (S4's 403): found as the
        # one invocation of refagent's runtime by the caller near the run file's `at`. The time read is still the
        # record's own; two such calls are not told apart, and none is unrecorded.
        near = trails.invocations_near(CALLER, parse_time(entry["at"]))
        if len(near) > 1:
            return {"what": attempt["what"], "mismatch": f"{len(near)} invocations by {CALLER} within {NEAR} of "
                                                         f"{entry['at']} and none names session {session}"}
        invoke, matched_by = near, ("the one invocation by the caller near `at`" if near else None)
    around = parse_time(invoke[0]["event_time"]) if invoke else parse_time(entry["at"])
    models = trails.by_role(REFAGENT_ROLE, MODEL_EVENTS, around - timedelta(minutes=1),
                            until or around + timedelta(minutes=2))  # fmt: skip
    return {"what": attempt["what"], "event_name": "InvokeAgentRuntime", "session_id": session, "records": invoke,
            "matched_by": matched_by,
            "model_calls": models, "human_said": {"result": entry.get("result")}}  # fmt: skip


def refusal_event(session: str | None, bucket: Bucket, trails: Trails, start: datetime, end: datetime) -> dict:
    """refagent's own record of refusing that session, and the trail's record of who put it (Security)."""
    if not session:
        return dict(NOT_FOUND)
    for obj in bucket.objects(EVENTS_PREFIX, start, end):
        if obj["key"].endswith(f"-{session}.json"):
            writes = [r for r in trails.matching(event_name="PutObject") if r["object_key"] == obj["key"]]
            return {"found": True, "key": obj["key"], "last_modified": iso(obj["last_modified"]),
                    "event": json.loads(bucket.body(obj["key"])), "writers": sorted({w["principal"] for w in writes})}
    return dict(NOT_FOUND)


def object_state(s3: Any, key: str) -> dict[str, Any]:
    """Seed S6's object as it stands: every version, and each one's retain-until date."""
    versions = []
    for page in s3.get_paginator("list_object_versions").paginate(Bucket=AUDIT_BUCKET, Prefix=key):
        for version in page.get("Versions", []):
            if version["Key"] != key:
                continue
            try:
                retention = s3.get_object_retention(Bucket=AUDIT_BUCKET, Key=key, VersionId=version["VersionId"])
                until = iso(parse_time(retention["Retention"]["RetainUntilDate"]))
            except Exception as exc:  # noqa: BLE001 - what it could not read is written as such
                until = f"unread: {type(exc).__name__}"
            versions.append({"version_id": version["VersionId"], "retain_until": until})
    return {"key": key, "versions": versions}


def object_at(s3: Any, key: str) -> bool:
    page = s3.list_objects_v2(Bucket=AUDIT_BUCKET, Prefix=key)
    return any(obj["Key"] == key for obj in page.get("Contents", []))


def quarantine_state(trails: Trails) -> dict[str, Any]:
    """The last attach or detach of the quarantine on refagent's role, in the window read (SPEC/05 §6)."""
    moves = [r for r in trails.matching() if r["event_name"] in ("AttachRolePolicy", "DetachRolePolicy")
             and r["policy_arn"] == QUARANTINE and not r["error_code"]]  # fmt: skip
    moves.sort(key=lambda r: r["event_time"])
    last = moves[-1] if moves else None
    return {"last": last["event_name"] if last else None, "at": last["event_time"] if last else None,
            "attached": bool(last and last["event_name"] == "AttachRolePolicy")}


# --- the run files --------------------------------------------------------------------


def observe(runs: list[dict[str, Any]], s3: Any) -> dict[str, Any]:
    bucket = Bucket(s3)
    made = [(run, entry) for run in runs for entry in run.get("observed") or []]
    times = [parse_time(entry["at"]) for _, entry in made if entry.get("at")]
    trails = Trails(bucket, min(times) - BEFORE, max(times) + DELIVERY) if times else None
    out: dict[str, Any] = {"quarantine": quarantine_state(trails) if trails else None, "seeds": []}
    for run in runs:
        seed = {"seed": run["seed"], "falsifiers": run.get("falsifiers"), "made": bool(run.get("observed")),
                "attempts": []}  # fmt: skip
        observed = run.get("observed") or []
        if not observed:
            seed["note"] = "the attempt has not been made: `observed` is empty in the run file"
        elif len(observed) != len(run["attempts"]):
            seed["made"], seed["note"] = False, f"{len(observed)} entries for {len(run['attempts'])} attempts"
        else:
            seed["attempts"] = [one(run, attempt, entry, trails, bucket, s3) for attempt, entry in zip(run["attempts"], observed)]
            if run["seed"] == "S6" and run.get("object"):
                seed["object"] = object_state(s3, str(run["object"]).split(",")[0].split()[0])
        out["seeds"].append(seed)
    return out


def one(run: dict[str, Any], attempt: dict[str, Any], entry: dict[str, Any], trails: Trails, bucket: Bucket,
        s3: Any) -> dict[str, Any]:  # fmt: skip
    at = parse_time(entry["at"]) if entry.get("at") else None
    if entry.get("event_name") != attempt.get("event_name"):
        return {"what": attempt["what"], "mismatch": f"entry {entry.get('event_name')!r} for {attempt.get('event_name')!r}"}
    if run["seed"] == "S1":
        return flow_attempt(attempt, entry, bucket, at)
    if attempt.get("event_name") == "InvokeAgentRuntime":
        # S7: the model calls up to the detach as the trail recorded it, never past it: a call after the
        # quarantine is lifted is refagent working again, not the quarantine (cold review F1 on M05 PR 2).
        detach = next((e for e in run["observed"] if e.get("event_name") == "DetachRolePolicy"), None)
        until = None
        if run["seed"] == "S7" and detach:
            found = trails.matching(request_id=detach.get("request_id"), event_name="DetachRolePolicy") \
                if detach.get("request_id") else []
            until = parse_time(found[0]["event_time"]) if found else None
            if until is None:
                return {"what": attempt["what"], "mismatch": "the detach is not in the trail: the window the "
                                                             "quarantine held cannot be read"}
        found = session_attempt(attempt, entry, trails, bucket, until=until)
        if run["seed"] == "S4":
            found["refusal_event"] = refusal_event(entry.get("session_id"), bucket, trails, at - BEFORE, at + DELIVERY)
        return found
    found = api_attempt(attempt, entry, trails)
    if run["seed"] == "S2":
        found["object_at_key"] = object_at(s3, "agents/ratings-helper/seed-s2.txt")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    runs = [yaml.safe_load(path.read_text(encoding="utf-8")) | {"path": path.as_posix()} for path in args.runs]
    result: dict[str, Any] = {
        "what": "the audit bucket's record of M05's attempts; not an envelope; rules nothing",
        "looked_up_at": iso(datetime.now(UTC)), "bucket": AUDIT_BUCKET, "readable": True,
        "runs": [run["path"] for run in runs],
    }  # fmt: skip
    try:
        import boto3

        result |= observe(runs, boto3.client("s3", region_name=REGION))
    except Exception as exc:  # noqa: BLE001 - no credentials, a denied read: an observation, not a crash
        result |= {"readable": False, "error": f"{type(exc).__name__}: {exc}", "quarantine": None,
                   "seeds": [{"seed": run["seed"], "falsifiers": run.get("falsifiers"), "made": bool(run.get("observed")),
                              "attempts": [], "note": "the audit bucket could not be read"} for run in runs]}  # fmt: skip
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8",
                        newline="\n")  # fmt: skip
    made = sum(seed["made"] for seed in result["seeds"])
    print(f"wrote {args.out}: {made} of {len(result['seeds'])} seeds made; readable {result['readable']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
