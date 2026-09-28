"""M05's seeded cases S1-S7 (SPEC/05 §5), committed before the code that reads them.

Two kinds. **Attempt seeds** (S1, S2, S3, S6, S7) are run files under
`milestones/M05/runs/`, each the attempt to make with `observed: null`, M01
S4's and S6's pattern: the test reads the file as the human filled it and
asserts every attempt was made and refused. It fails until the attempt is
made, after its control is deployed (SPEC/05 §5.1: S1, S2 and S6 during PR 2,
S3 and S7 after PR 2's merge deploy). What records an attempt is
`scripts/observe_containment.py`'s lookup in the audit bucket, not this test
(SPEC/05 §4): these tests are the test-only witnesses `F5_*` is built from.
**Code seeds** (S4, S5) are fixtures under `tests/fixtures/m05/`; each test
asks the reader to refuse its fixture and asserts the planted reason.

Each is marked `xfail(strict=True, raises=...)` with the one exception class
its planted reason raises, so an exception of any other class (a moved
fixture, a run file that no longer parses) is a failure, not an expected
one. Preconditions raise `SeedBroken`. Each was run once with `--runxfail`
and its message read, and the marker comes off in the commit that lands the
reader (or records the attempt). Nothing here calls AWS or a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT

RUNS = ROOT / "milestones" / "M05" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m05"


class SeedBroken(Exception):
    """A seed's own precondition failed. Not AssertionError, which the strict markers expect of the
    planted failure: a broken seed must fail the run, not pass as an expected one (M04's rule)."""


def holds(condition: bool, message: str) -> None:
    if not condition:
        raise SeedBroken(message)


def run_file(name: str, seed: str) -> dict[str, Any]:
    run = yaml.safe_load((RUNS / name).read_text(encoding="utf-8"))
    holds(isinstance(run, dict) and run.get("seed") == seed, f"{name} is seed {seed}'s run file")
    holds(isinstance(run.get("attempts"), list) and run["attempts"], f"{name} names the attempts to make")
    holds(all(a.get("what") and a.get("refused_when") for a in run["attempts"]),
          f"{name}: every attempt says what it is and when it counts as refused")  # fmt: skip
    return run


def made(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The observed entries, one per attempt: the planted failure is that there are none yet."""
    observed = run["observed"]
    assert observed is not None, f"seed {run['seed']}: the attempt has not been made"
    assert len(observed) == len(run["attempts"]), f"seed {run['seed']}: every attempt is made, not some"
    return observed


# --- S1: curl to the internet -------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S1 is attempted during M05 PR 2 (SPEC/05 §5.1)")
def test_s1_curl_to_the_internet_was_refused():
    """From the platform VPC with refagent's security group, `curl https://example.com`. Held today
    (no internet gateway, no NAT, egress to the listed endpoints only); what is missing is its
    record in the security account (SPEC/05 §3.1, §3.6). Refused when curl cannot connect and the
    flow record reads REJECT."""
    run = run_file("f5_1_curl.yaml", "S1")
    observed = made(run)
    assert all(o.get("eni") and o.get("destination") and o.get("result") for o in observed), observed


# --- S2: a write to another agent's prefix ------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S2 is attempted during M05 PR 2 (SPEC/05 §5.1)")
def test_s2_a_write_to_another_agents_prefix_was_refused():
    """As refagent's stand-in, `s3:PutObject` under `agents/ratings-helper/` in the audit bucket.
    The stand-in's own policy grants the write, so the refusal can only be the audit bucket's
    policy, which scopes each agent role to its own prefix (SPEC/05 §2, §5). Today there is no
    audit bucket and no prefix, own or another's (SPEC/05 §3.7)."""
    run = run_file("f5_2_prefix.yaml", "S2")
    observed = made(run)
    assert all(o.get("result") == "AccessDenied" and o.get("request_id") for o in observed), observed


# --- S3: logs:DeleteLogStream --------------------------------------------------


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="S3 is attempted after M05 PR 2's merge deploy, read at PR 3 (SPEC/05 §5.1)")  # fmt: skip
def test_s3_deleting_its_own_log_stream_was_refused():
    """As refagent's stand-in, `logs:DeleteLogStream` on the runtime's own log stream. The boundary
    denies `logs:Delete*` today and PR 2 adds the role's own deny; both are explicit, so this reads
    "refused and recorded", and the record in the security account is what is new (SPEC/05 §3.8)."""
    run = run_file("f5_3_logs.yaml", "S3")
    observed = made(run)
    assert all(o.get("result") == "AccessDenied" and o.get("request_id") and "explicit deny" in (o.get("message") or "")
               for o in observed), observed  # fmt: skip


# --- S4: a call chain at depth 3 ----------------------------------------------


class ModelThatRecords:
    """A Bedrock client whose only call records itself and answers as a model would, with no tool."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def converse(self, **request: Any) -> dict[str, Any]:
        self.calls.append(request)
        return {"usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2}, "stopReason": "end_turn",
                "output": {"message": {"role": "assistant", "content": [{"text": "{}"}]}}}  # fmt: skip


def invoke(payload: dict[str, Any], monkeypatch) -> tuple[int, dict[str, Any], ModelThatRecords]:
    """POST `payload` to refagent's own handler, served in-process with a model that records its calls.

    The runtime's environment as GovernedAgent sets it, but for the model and the table, which are
    stand-ins: nothing here reaches AWS."""
    import json
    import threading
    import urllib.request
    from http.server import HTTPServer

    from agents.refagent import agent, server

    manifest = yaml.safe_load((ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
    monkeypatch.setattr(server, "MODEL_ID", "the agent's profile")
    monkeypatch.setattr(server, "TABLE", "the rights table")
    monkeypatch.setattr(server.boto3, "client", lambda *args, **kwargs: None)
    monkeypatch.setattr(agent, "rights_rows", lambda table, client=None: ([], "the rights table"))
    # What the construct passes from PR 2 (SPEC/05 section 6): the image has no YAML reader.
    monkeypatch.setenv("AGENTKEEL_CEILING_DEPTH", str(manifest["ceilings"]["depth"]))
    model = ModelThatRecords()
    httpd = HTTPServer(("127.0.0.1", 0), server.Handler)
    httpd._bedrock = model
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        request = urllib.request.Request(f"http://127.0.0.1:{httpd.server_port}/invocations",
                                         data=json.dumps(payload).encode("utf-8"), method="POST")  # fmt: skip
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - loopback only
            return response.status, json.loads(response.read()), model
    except urllib.error.HTTPError as refused:
        return refused.code, json.loads(refused.read() or b"{}"), model
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="S4's reader, the chain check in server.py, is M05 PR 2's")
def test_s4_a_chain_at_depth_3_is_refused_before_the_model(monkeypatch):
    """An invocation whose payload's `chain` names two agents before refagent: refagent is the third,
    and its manifest's `ceilings.depth` is 2. Today `server.py` reads the question and nothing about
    who called, and the model is called (SPEC/05 §3.2). From PR 2 the chain is refused before any
    model call, and the refusal names the depth (SPEC/05 §5, S4)."""
    import json

    payload = json.loads((FIXTURES / "s4-depth3-request.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
    holds(manifest["ceilings"]["depth"] == 2, "refagent's ceiling is the one the seed was planted against")
    holds(len(payload["chain"]) + 1 == 3 and payload["question"], "the seed is a question at depth 3")

    status, answer, model = invoke(payload, monkeypatch)
    holds(status in (200, 400, 403, 429), f"the handler answered: {status} {answer}")
    assert model.calls == [], f"a chain at depth 3 reached the model ({len(model.calls)} call): {answer}"
    assert "depth" in json.dumps(answer), answer
