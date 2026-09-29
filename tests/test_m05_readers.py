"""M05 PR 2's readers, beside the seeds they read (SPEC/05 §6). The seeds' own tests are tests/test_m05_seeds.py.

Nothing here calls AWS or a model: the S3 client and the model are stand-ins that record what they are asked.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agents.refagent import server

from .test_m05_seeds import FIXTURES, invoke


class S3ThatRecords:
    def __init__(self, fail: bool = False) -> None:
        self.puts: list[dict[str, Any]] = []
        self.fail = fail

    def put_object(self, **request: Any) -> dict[str, Any]:
        if self.fail:
            raise RuntimeError("AccessDenied")
        self.puts.append(request)
        return {}


# --- S4's reader: the chain check in server.py --------------------------------


def test_a_chain_within_the_ceiling_reaches_the_model(monkeypatch):
    status, _, model = invoke({"question": "Can we?", "chain": ["distribution-desk"]}, monkeypatch)
    assert status == 200 and len(model.calls) == 1


def test_no_chain_is_depth_one_and_reaches_the_model(monkeypatch):
    """What the runner and every golden send: the question alone."""
    status, _, model = invoke({"question": "Can we?"}, monkeypatch)
    assert status == 200 and len(model.calls) == 1


@pytest.mark.parametrize("ceiling", [None, "", "two"])
def test_a_runtime_with_no_ceiling_refuses_rather_than_hold_a_chain_to_nothing(monkeypatch, ceiling):
    if ceiling is None:
        monkeypatch.delenv("AGENTKEEL_CEILING_DEPTH", raising=False)
    else:
        monkeypatch.setenv("AGENTKEEL_CEILING_DEPTH", ceiling)
    refusal = server.chain_refusal({"question": "Can we?"}, None)
    assert refusal is not None and "no depth ceiling" in refusal["refused"] and refusal["depth"] == 1


@pytest.mark.parametrize("chain", ["ratings-helper", [""], [1, 2], {"a": 1}])
def test_a_chain_that_is_not_a_list_of_names_is_refused(monkeypatch, chain):
    status, answer, model = invoke({"question": "Can we?", "chain": chain}, monkeypatch)
    assert status == 403 and model.calls == [] and "list of the agents" in answer["refused"]


def test_the_refusal_event_is_written_under_the_agents_own_prefix_with_the_session(monkeypatch):
    monkeypatch.setenv("AGENTKEEL_CEILING_DEPTH", "2")
    monkeypatch.setenv("AGENTKEEL_AUDIT_BUCKET", "agentkeel-audit-897698239547")
    monkeypatch.setenv("AGENTKEEL_AUDIT_PREFIX", "agents/refagent/events/")
    payload = json.loads((FIXTURES / "s4-depth3-request.json").read_text(encoding="utf-8"))
    session = "s4-" + "0" * 40
    refusal = server.chain_refusal(payload, session)
    s3 = S3ThatRecords()
    recorded = server.record_refusal(refusal, s3)
    (put,) = s3.puts
    assert put["Bucket"] == "agentkeel-audit-897698239547"
    assert put["Key"].startswith("agents/refagent/events/") and put["Key"].endswith(f"-{session}.json")
    assert put["ChecksumAlgorithm"] == "SHA256"  # Object Lock refuses a put with no checksum
    event = json.loads(put["Body"])
    assert event["event"] == "chain_refused" and event["depth"] == 3 and event["ceiling"] == 2
    assert event["session_id"] == session and event["chain"] == payload["chain"]
    assert recorded == {"recorded": f"s3://agentkeel-audit-897698239547/{put['Key']}"}


def test_a_refusal_whose_record_fails_is_still_a_refusal_and_says_so(monkeypatch):
    monkeypatch.setenv("AGENTKEEL_AUDIT_BUCKET", "b")
    monkeypatch.setenv("AGENTKEEL_AUDIT_PREFIX", "agents/refagent/events/")
    recorded = server.record_refusal({"refused": "deep", "depth": 3, "ceiling": 2}, S3ThatRecords(fail=True))
    assert recorded["recorded"] is None and "AccessDenied" in recorded["record_error"]

