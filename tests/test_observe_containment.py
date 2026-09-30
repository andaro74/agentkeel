"""scripts/observe_containment.py against a stand-in audit bucket (M05 PR 2; SPEC/05 §4). Nothing reaches AWS."""

from __future__ import annotations

import gzip
import importlib.util
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("observe_containment", ROOT / "scripts" / "observe_containment.py")
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)

AT = datetime(2026, 9, 29, 18, 0, 0, tzinfo=UTC)
AGENT, SECURITY = observer.AGENT_ACCOUNT, observer.SECURITY_ACCOUNT
STANDIN = f"arn:aws:iam::{AGENT}:role/agentkeel/agents/agentkeel-refagent-standin"
REFAGENT = f"arn:aws:iam::{AGENT}:role/agentkeel/agents/agentkeel-refagent-RefagentRole5888DB41-i9IqTXU6NVSL"


class Body:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def read(self) -> bytes:
        return self.data


class Pages:
    def __init__(self, pages: list[dict[str, Any]]) -> None:
        self.pages = pages

    def paginate(self, **_: Any) -> list[dict[str, Any]]:
        return self.pages


class FakeS3:
    """Objects by key, each with its bytes and LastModified; versions and retention for S6's object."""

    def __init__(self) -> None:
        self.objects: dict[str, tuple[bytes, datetime]] = {}
        self.versions: dict[str, list[tuple[str, datetime]]] = {}

    def put(self, key: str, data: bytes, modified: datetime) -> None:
        self.objects[key] = (data, modified)

    def _list(self, prefix: str) -> dict[str, Any]:
        return {"Contents": [{"Key": k, "LastModified": m} for k, (_, m) in sorted(self.objects.items()) if k.startswith(prefix)]}

    def get_paginator(self, name: str) -> Pages:
        if name == "list_objects_v2":
            return _Prefixed(self)
        return _Versions(self)

    def list_objects_v2(self, Bucket: str, Prefix: str) -> dict[str, Any]:  # noqa: N803
        return self._list(Prefix)

    def get_object(self, Bucket: str, Key: str) -> dict[str, Any]:  # noqa: N803
        return {"Body": Body(self.objects[Key][0])}

    def get_object_retention(self, Bucket: str, Key: str, VersionId: str) -> dict[str, Any]:  # noqa: N803
        until = dict(self.versions[Key])[VersionId]
        return {"Retention": {"Mode": "COMPLIANCE", "RetainUntilDate": until}}


class _Prefixed:
    def __init__(self, s3: FakeS3) -> None:
        self.s3 = s3

    def paginate(self, Bucket: str, Prefix: str) -> list[dict[str, Any]]:  # noqa: N803
        return [self.s3._list(Prefix)]


class _Versions:
    def __init__(self, s3: FakeS3) -> None:
        self.s3 = s3

    def paginate(self, Bucket: str, Prefix: str) -> list[dict[str, Any]]:  # noqa: N803
        return [{"Versions": [{"Key": k, "VersionId": v} for k, vs in self.s3.versions.items() if k.startswith(Prefix)
                              for v, _ in vs]}]  # fmt: skip


def trail_file(s3: FakeS3, account: str, region: str, records: list[dict[str, Any]], delivered: datetime, n: int) -> None:
    key = f"AWSLogs/{account}/CloudTrail/{region}/{delivered:%Y/%m/%d}/{account}_CloudTrail_{region}_{n}.json.gz"
    s3.put(key, gzip.compress(json.dumps({"Records": records}).encode()), delivered)


def record(name: str, request_id: str, when: datetime, who: str, error: str | None = None, message: str | None = None,
           **params: Any) -> dict[str, Any]:  # fmt: skip
    identity = ({"type": "AssumedRole", "arn": f"arn:aws:sts::{AGENT}:assumed-role/x/y",
                 "sessionContext": {"sessionIssuer": {"arn": who}}} if ":role/" in who else {"type": "IAMUser", "arn": who})
    return {"eventName": name, "requestID": request_id, "eventID": f"id-{request_id}", "eventTime": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "eventSource": "s3.amazonaws.com", "recipientAccountId": AGENT, "userIdentity": identity,
            "errorCode": error, "errorMessage": message, "requestParameters": params}  # fmt: skip


def test_s2_is_read_from_both_trails_with_the_principal_and_the_message():
    s3 = FakeS3()
    denied = record("PutObject", "REQ-S2", AT, STANDIN, "AccessDenied",
                    "User is not authorized to perform: s3:PutObject with an explicit deny in a resource-based policy",
                    key="agents/ratings-helper/seed-s2.txt")  # fmt: skip
    trail_file(s3, SECURITY, "us-west-2", [denied], AT + timedelta(minutes=4), 1)
    trail_file(s3, AGENT, "us-west-2", [denied], AT + timedelta(minutes=6), 2)
    run = {"seed": "S2", "falsifiers": ["F5.1", "F5.2"],
           "attempts": [{"what": "put", "event_name": "PutObject"}],
           "observed": [{"event_name": "PutObject", "request_id": "REQ-S2", "at": AT.isoformat(),
                         "result": "AccessDenied", "message": "whatever the human saw"}]}  # fmt: skip
    (seed,) = observer.observe([run], s3)["seeds"]
    (attempt,) = seed["attempts"]
    assert seed["made"] and [r["last_modified"] for r in attempt["records"]] == ["2026-09-29T18:04:00Z", "2026-09-29T18:06:00Z"]
    assert attempt["records"][0]["principal"] == STANDIN and "resource-based policy" in attempt["records"][0]["error_message"]
    assert attempt["records"][0]["event_time"] == "2026-09-29T18:00:00Z"
    assert attempt["object_at_key"] is False
    assert attempt["human_said"]["message"] == "whatever the human saw"  # beside the record, never instead of it


def test_an_attempt_not_made_and_an_id_nobody_recorded_are_written_as_such():
    s3 = FakeS3()
    not_made = {"seed": "S3", "attempts": [{"what": "delete", "event_name": "DeleteLogStream"}], "observed": None}
    unrecorded = {"seed": "S2", "attempts": [{"what": "put", "event_name": "PutObject"}],
                  "observed": [{"event_name": "PutObject", "request_id": "NOBODY", "at": AT.isoformat()}]}  # fmt: skip
    seeds = {s["seed"]: s for s in observer.observe([not_made, unrecorded], s3)["seeds"]}
    assert seeds["S3"]["made"] is False and "not been made" in seeds["S3"]["note"]
    assert seeds["S2"]["made"] is True and seeds["S2"]["attempts"][0]["records"] == []


def test_s1_is_read_from_the_flow_record_for_that_eni_and_address():
    s3 = FakeS3()
    start = int(AT.timestamp())
    lines = [f"2 {AGENT} eni-0abc 10.20.0.254 1.1.1.1 51000 443 6 3 180 {start} {start + 60} REJECT OK",
             f"2 {AGENT} eni-0other 10.20.0.9 1.1.1.1 51000 443 6 3 180 {start} {start + 60} ACCEPT OK",
             f"2 {AGENT} eni-0abc 10.20.0.254 10.20.0.5 51000 443 6 3 180 {start} {start + 60} ACCEPT OK"]
    s3.put(f"AWSLogs/{AGENT}/vpcflowlogs/us-west-2/2026/09/29/{AGENT}_vpcflowlogs_us-west-2_fl-1_20260929T1805Z.log.gz",
           gzip.compress(("version account-id ...\n" + "\n".join(lines)).encode()), AT + timedelta(minutes=7))  # fmt: skip
    run = {"seed": "S1", "attempts": [{"what": "curl"}],
           "observed": [{"eni": "eni-0abc", "destination": "1.1.1.1", "at": AT.isoformat(), "connected": False}]}
    (record_,) = observer.observe([run], s3)["seeds"][0]["attempts"][0]["records"]
    assert record_["action"] == "REJECT" and record_["start"] == "2026-09-29T18:00:00Z"
    assert record_["last_modified"] == "2026-09-29T18:07:00Z"


def test_s4_reads_the_call_the_refusal_event_its_writer_and_the_model_calls():
    s3 = FakeS3()
    session = "s4-" + "a" * 40
    invoke = record("InvokeAgentRuntime", "REQ-S4", AT, f"arn:aws:iam::{AGENT}:user/admin", runtimeSessionId=session)
    event_key = f"agents/refagent/events/20260929T180001Z-{session}.json"
    put = record("PutObject", "REQ-EV", AT + timedelta(seconds=1), REFAGENT, key=event_key)
    trail_file(s3, AGENT, "us-west-2", [invoke, put], AT + timedelta(minutes=5), 1)
    s3.put(event_key, json.dumps({"event": "chain_refused", "depth": 3}).encode(), AT + timedelta(seconds=2))
    run = {"seed": "S4", "attempts": [{"what": "invoke", "event_name": "InvokeAgentRuntime"}],
           "observed": [{"event_name": "InvokeAgentRuntime", "session_id": session, "at": AT.isoformat()}]}
    (attempt,) = observer.observe([run], s3)["seeds"][0]["attempts"]
    assert attempt["records"][0]["request_id"] == "REQ-S4" and attempt["model_calls"] == []
    assert attempt["refusal_event"]["found"] and attempt["refusal_event"]["writers"] == [REFAGENT]
    assert attempt["refusal_event"]["event"]["depth"] == 3


def test_s7_reads_the_model_calls_between_the_attach_and_the_detach_and_the_quarantine_state():
    s3 = FakeS3()
    session = "s7-" + "b" * 40
    admin = f"arn:aws:iam::{AGENT}:user/admin"
    attach = record("AttachRolePolicy", "REQ-A", AT, admin, policyArn=observer.QUARANTINE, roleName="r")
    invoke = record("InvokeAgentRuntime", "REQ-I", AT + timedelta(minutes=2), admin, runtimeSessionId=session)
    model = record("Converse", "REQ-M", AT + timedelta(minutes=2, seconds=3), REFAGENT, "AccessDenied",
                   "with an explicit deny in an identity-based policy")  # fmt: skip
    detach = record("DetachRolePolicy", "REQ-D", AT + timedelta(minutes=5), admin, policyArn=observer.QUARANTINE, roleName="r")
    # refagent answering again one minute after the detach: not the quarantine's, and not read (cold review F1)
    after = record("Converse", "REQ-AFTER", AT + timedelta(minutes=6), REFAGENT)
    trail_file(s3, AGENT, "us-east-1", [attach, detach], AT + timedelta(minutes=9), 1)
    trail_file(s3, AGENT, "us-west-2", [invoke, model, after], AT + timedelta(minutes=8), 2)
    entries = [{"event_name": "AttachRolePolicy", "request_id": "REQ-A", "at": AT.isoformat()},
               {"event_name": "InvokeAgentRuntime", "session_id": session, "at": (AT + timedelta(minutes=2)).isoformat()},
               {"event_name": "DetachRolePolicy", "request_id": "REQ-D", "at": (AT + timedelta(minutes=25)).isoformat()}]  # written late: the trail's time is read
    run = {"seed": "S7", "attempts": [{"what": w, "event_name": e["event_name"]} for w, e in zip("aid", entries)],
           "observed": entries}
    out = observer.observe([run], s3)
    attach_, invoke_, detach_ = out["seeds"][0]["attempts"]
    assert attach_["records"][0]["policy_arn"] == observer.QUARANTINE
    (call,) = invoke_["model_calls"]
    assert call["principal"] == REFAGENT and call["error_code"] == "AccessDenied"
    assert detach_["records"][0]["event_name"] == "DetachRolePolicy"
    assert out["quarantine"] == {"last": "DetachRolePolicy", "at": "2026-09-29T18:05:00Z", "attached": False}


def test_s6_reads_the_objects_versions_and_retention_as_they_stand():
    s3 = FakeS3()
    until = AT + timedelta(days=1)
    s3.versions["test/seed-s6.txt"] = [("v1", until)]
    run = {"seed": "S6", "object": "test/seed-s6.txt, put within the day",
           "attempts": [{"what": "delete", "event_name": "DeleteObject"}],
           "observed": [{"event_name": "DeleteObject", "request_id": "REQ-6", "at": AT.isoformat()}]}
    seed = observer.observe([run], s3)["seeds"][0]
    assert seed["object"] == {"key": "test/seed-s6.txt", "versions": [{"version_id": "v1", "retain_until": "2026-09-30T18:00:00Z"}]}


def test_a_bucket_it_cannot_read_is_an_observation_not_a_crash(tmp_path, monkeypatch):
    run = tmp_path / "f5_2.yaml"
    run.write_text("seed: S2\nattempts: [{what: put, event_name: PutObject}]\n"
                   "observed: [{event_name: PutObject, request_id: R, at: '2026-09-29T18:00:00Z'}]\n")  # fmt: skip
    import boto3

    monkeypatch.setattr(boto3, "client", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("NoCredentialsError")))
    out = tmp_path / "o.json"
    assert observer.main([str(run), "--out", str(out)]) == 0
    written = json.loads(out.read_text())
    assert written["readable"] is False and written["seeds"][0]["made"] is True and written["seeds"][0]["attempts"] == []


@pytest.mark.parametrize("name", sorted(p.name for p in (ROOT / "milestones" / "M05" / "runs").glob("f5_*.yaml")))
def test_every_run_file_as_committed_is_one_the_observer_reads(name):
    import yaml

    run = yaml.safe_load((ROOT / "milestones" / "M05" / "runs" / name).read_text(encoding="utf-8"))
    out = observer.observe([run], FakeS3())
    assert out["seeds"][0]["seed"] == run["seed"]


def test_s7_with_no_detach_in_the_trail_cannot_bound_the_window():
    s3 = FakeS3()
    entries = [{"event_name": "AttachRolePolicy", "request_id": "REQ-A", "at": AT.isoformat()},
               {"event_name": "InvokeAgentRuntime", "session_id": "s7-" + "c" * 40, "at": AT.isoformat()},
               {"event_name": "DetachRolePolicy", "request_id": "NOT-IN-THE-TRAIL", "at": AT.isoformat()}]
    run = {"seed": "S7", "attempts": [{"what": w, "event_name": e["event_name"]} for w, e in zip("aid", entries)],
           "observed": entries}
    invoke = observer.observe([run], s3)["seeds"][0]["attempts"][1]
    assert "the detach is not in the trail" in invoke["mismatch"]


def test_an_attempt_is_found_by_its_request_id_whatever_cloudtrail_names_it():
    """#31's first run: CloudTrail logged S6's lock-off, the API PutObjectLockConfiguration, as
    PutBucketObjectLockConfiguration; matching the run file's name read a recorded refusal as unrecorded."""
    s3 = FakeS3()
    denied = record("PutBucketObjectLockConfiguration", "DSHB2N47998KBX7K", AT, f"arn:aws:iam::{AGENT}:user/admin",
                    "AccessDenied", "with an explicit deny in a resource-based policy")  # fmt: skip
    trail_file(s3, AGENT, "us-west-2", [denied], AT + timedelta(minutes=5), 1)
    run = {"seed": "S6", "attempts": [{"what": "unlock", "event_name": "PutObjectLockConfiguration"}],
           "observed": [{"event_name": "PutObjectLockConfiguration", "request_id": "DSHB2N47998KBX7K", "at": AT.isoformat()}]}
    (attempt,) = observer.observe([run], s3)["seeds"][0]["attempts"]
    assert attempt["records"][0]["event_name"] == "PutBucketObjectLockConfiguration"
