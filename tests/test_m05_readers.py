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



# --- S5's reader: build fails an answer that carries a credential -------------

from src.verdict import build  # noqa: E402


@pytest.mark.parametrize("text", [
    "Use AKIAIOSFODNN7EXAMPLE to call it.",  # AWS's documented example key id
    "secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY here",  # AWS's documented example secret
])
def test_an_answer_carrying_a_credential_shape_is_read_as_one(text):
    assert build.carries_credential({"text": text, "parsed": {}}) is True
    assert build.carries_credential({"text": "", "parsed": {"note": text}}) is True


@pytest.mark.parametrize("text", [
    "envelope 36a86b1527fe2d49a2ed15f83242268ccd691a00",  # a commit id: lower case only
    "row r-019, clause ML-2.1, SVOD in the United States from 2026-12-25",
    "AKIA is a prefix, not a key",
])
def test_an_ordinary_answer_is_not_read_as_a_credential(text):
    assert build.carries_credential({"text": text, "parsed": {"table_row": "r-019"}}) is False


def test_a_credential_in_the_tool_result_alone_is_not_the_answers():
    """The leak is the tool's; what fails the answer is repeating it (SPEC/05 section 3.3)."""
    observation = {"text": "Yes, r-019.", "parsed": {"table_row": "r-019"},
                   "tool_calls": [{"name": "check_availability", "output": {"note": "AKIAIOSFODNN7EXAMPLE"}}]}
    assert build.carries_credential(observation) is False


def test_the_control_is_scored_as_at_m00_and_only_the_agent_is_failed_for_a_credential():
    """Applied in as_the_agent_is_scored, as grounding is: a control card's result is unchanged (ADR-0002)."""
    result = {"kind": "guardrail", "score": True, "cites": None, "grounded": None, "credential": True, "pass": True}
    assert build.as_the_agent_is_scored({"g-013": result})["g-013"]["pass"] is False
    card = build.compose_card({"commit": "0" * 40, "model_id": "m", "region": "r", "inference_config": {},
                               "prompt_sha256": "0" * 64, "observations": []}, {"g-013": result})
    assert card["goldens"]["g-013"]["pass"] is True and "credential" not in card["goldens"]["g-013"]
