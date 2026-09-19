"""Look up one seed's attempts in CloudTrail and write what AWS recorded (P5).

    python scripts/observe_attempt.py milestones/M01/runs/f1_1_laptop.yaml --out f1_1.json

This is an instrument, in the pattern of `scripts/observe_pr_check.py`. It
reads the run file the human filled in after making the attempt, asks
CloudTrail for the event with each request id, and writes a raw
observation. It decides nothing: `src/verdict/build.py` reads the
observation into `checks` (`--check-attempt`), and only `verdict.gate`
rules.

Why the lookup exists at all (ruling i, ruling 4 before PR #7 merged). The
human makes the attempt, so the file is human-written, and a human-written
file feeds no check by itself (SPEC/01 §4). What feeds the check is this:
AWS's own record that the request id the human wrote was refused. A person
who wanted to fake the refusal would have to fake a CloudTrail event.

CloudTrail has no lookup attribute for a request id, so this looks up by
event name over a window around the attempt and matches `requestID` in the
event itself. An attempt that is not found is a fail, not an absence: a
refusal nobody can find is not a refusal.

Exit 0 when the observation is written, whatever it says. Exit 1 only when
it could not be written at all.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.exceptions import BotoCoreError, ClientError

WINDOW = timedelta(minutes=30)  # either side of the timestamp the human wrote
REGION = "us-west-2"


def parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def lookup(client: Any, event_name: str, at: datetime, request_id: str) -> dict[str, Any]:
    """The CloudTrail event with this request id, or a record that it was not found."""
    pages = client.get_paginator("lookup_events").paginate(
        LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": event_name}],
        StartTime=at - WINDOW,
        EndTime=at + WINDOW,
    )
    for page in pages:
        for event in page["Events"]:
            record = json.loads(event["CloudTrailEvent"])
            if record.get("requestID") != request_id:
                continue
            return {
                "found": True,
                "event_id": event["EventId"],
                "event_name": record.get("eventName"),
                "event_time": record.get("eventTime"),
                "error_code": record.get("errorCode"),
                "error_message": record.get("errorMessage"),
                "principal": (record.get("userIdentity") or {}).get("arn"),
            }
    return {"found": False, "event_name": event_name, "error_code": None,
            "error_message": f"no {event_name} event with request id {request_id} within "
                             f"{WINDOW} of {at.isoformat()}"}  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--region", default=REGION)
    args = parser.parse_args(argv)

    run = yaml.safe_load(args.run.read_text(encoding="utf-8"))
    observed = run.get("observed")
    result: dict[str, Any] = {
        "what": f"CloudTrail's record of seed {run['seed']}'s attempts; not an envelope; rules nothing",
        "looked_up_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "run": args.run.as_posix(),
        "seed": run["seed"],
        "falsifier": run["falsifier"],
        "attempts": [],
    }
    if not observed:
        # The attempt has not been made. The check fails; it does not error.
        result["note"] = "the attempt has not been made: `observed` is empty in the run file"
    else:
        client = boto3.client("cloudtrail", region_name=args.region)
        for attempt in observed:
            entry = {"request_id": attempt["request_id"], "what": attempt.get("what")}
            try:
                entry |= lookup(client, attempt["event_name"], parse_time(attempt["at"]), attempt["request_id"])
            except (BotoCoreError, ClientError) as exc:  # a failed lookup is an observation too
                entry |= {"found": False, "error_code": None, "error_message": f"{type(exc).__name__}: {exc}"}
            # What the human wrote, beside what CloudTrail says. They must agree.
            entry["human_said"] = {"result": attempt.get("result"), "message": attempt.get("message")}
            result["attempts"].append(entry)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    found = sum(1 for a in result["attempts"] if a.get("error_code") == "AccessDenied")
    print(f"wrote {args.out} ({found} of {len(result['attempts'])} attempts recorded as AccessDenied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
