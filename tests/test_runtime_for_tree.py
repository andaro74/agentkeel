"""scripts/runtime_for_tree.py: runtime mode only when the deployed bytes are this tree's (ADR-0007, P1).

No AWS here: the lookup is passed in. What these hold is the decision and the
condition on P1 — a match sets the ARN, anything else sets none and says why,
and nothing fails the job.
"""

from __future__ import annotations

import subprocess
import sys

import pytest
from botocore.exceptions import ClientError

from scripts import runtime_for_tree as rt
from src.verdict import ROOT

ARN = "arn:aws:bedrock-agentcore:us-west-2:111122223333:runtime/refagent-abc"


def test_the_digest_is_the_one_deploy_yml_tags_the_image_with(tmp_path):
    """deploy.yml tags the image with the first field `python -m src.bundle.pack` prints."""
    printed = subprocess.run(
        [sys.executable, "-m", "src.bundle.pack", "agents/refagent", "--out", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()[0]  # fmt: skip
    assert rt.bundle_digest() == printed


def test_a_match_measures_the_runtime():
    arn, reason = rt.match("d" * 64, lambda: (ARN, ["other", "d" * 64]))
    assert arn == ARN and reason.startswith("runtime:")


def test_other_bytes_stay_in_the_runner_and_say_so():
    arn, reason = rt.match("d" * 64, lambda: (ARN, ["e" * 64]))
    assert arn == "" and reason.startswith("runner:") and "other bytes" in reason


@pytest.mark.parametrize("failure", [
    ClientError({"Error": {"Code": "AccessDenied", "Message": "no"}}, "GetAgentRuntime"),
    ClientError({"Error": {"Code": "ValidationError", "Message": "Stack does not exist"}}, "DescribeStacks"),
    LookupError("stack agentkeel-refagent has no RuntimeArn output"),
])  # fmt: skip
def test_a_failed_lookup_is_a_reason_not_an_error(failure):
    """The condition on P1: never silent, never a failed job."""

    def lookup():
        raise failure

    arn, reason = rt.match("d" * 64, lookup)
    assert arn == "" and reason.startswith("runner: the deployed runtime could not be read")


def test_it_writes_the_output_and_the_summary_and_exits_0(tmp_path, monkeypatch):
    monkeypatch.setattr(rt, "match", lambda digest: ("", "runner: test reason"))
    out, summary = tmp_path / "out", tmp_path / "summary"
    assert rt.main(["--github-output", str(out), "--summary", str(summary)]) == 0
    assert out.read_text(encoding="utf-8") == "arn=\n"
    assert "runner: test reason" in summary.read_text(encoding="utf-8")
