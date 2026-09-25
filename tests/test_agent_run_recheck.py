"""src/agent/run.py: a runtime run reads the match again after its last call (M03 PR 2; security on 606bece, F1)."""

from __future__ import annotations

import json

import pytest

from src.agent import run

ARN = "arn:aws:bedrock-agentcore:us-west-2:111122223333:runtime/refagent-abc"


@pytest.fixture
def runtime(monkeypatch):
    monkeypatch.setenv("AGENTKEEL_RUNTIME_ARN", ARN)
    monkeypatch.setattr(run.boto3, "client", lambda *a, **k: object())
    monkeypatch.setattr(run, "invoke_deployed", lambda client, arn, question: {
        "text": "{}", "parsed": {}, "stop_reason": "end_turn", "usage": {"inputTokens": 1, "outputTokens": 1}})


def ran(tmp_path, *flags) -> tuple[int, list[dict]]:
    out = tmp_path / "raw.json"
    code = run.main(["--out", str(out), *flags])
    return code, json.loads(out.read_text(encoding="utf-8"))["observations"]


def test_a_runtime_that_moved_during_the_run_makes_every_answer_a_failed_call(tmp_path, runtime, monkeypatch):
    monkeypatch.setattr(run, "runtime_moved", lambda arn: "runner: the runtime's rights table marker says 'loading'")
    code, observations = ran(tmp_path, "--recheck-runtime")
    assert code == 1 and observations
    assert all(o["error"].startswith("the runtime moved during the run: runner: the runtime's rights table marker")
               for o in observations)  # fmt: skip


def test_a_runtime_that_did_not_move_leaves_the_answers(tmp_path, runtime, monkeypatch):
    monkeypatch.setattr(run, "runtime_moved", lambda arn: None)
    code, observations = ran(tmp_path, "--recheck-runtime")
    assert code == 0 and not any("error" in o for o in observations)


def test_without_the_flag_it_is_not_read_again(tmp_path, runtime, monkeypatch):
    """deploy.yml's check at load: the deploy role may not read the image or the marker."""
    monkeypatch.setattr(run, "runtime_moved", lambda arn: pytest.fail("read again without --recheck-runtime"))
    assert ran(tmp_path)[0] == 0


def test_the_match_that_cannot_be_read_again_is_a_move(monkeypatch):
    from scripts import runtime_for_tree

    monkeypatch.setattr(runtime_for_tree, "bundle_digest", lambda: (_ for _ in ()).throw(OSError("no")))
    assert run.runtime_moved(ARN).startswith("the match could not be read again (OSError")


def test_make_evals_passes_the_flag():
    from src.verdict import ROOT

    assert "src.agent.run --out $(1)/$(2).agent-raw.json --recheck-runtime" in (ROOT / "Makefile").read_text(encoding="utf-8")
