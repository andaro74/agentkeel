"""Shared test helpers. Nothing here calls a model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT, build

GOLDENS_DIR = ROOT / "evals" / "goldens" / "v1"
COMMIT = "a" * 40
URL = "https://github.com/andaro74/agentkeel/actions/runs/1"
REFAGENT_PIN = yaml.safe_load((ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))["model"]
# What an agent's raw file says about where it ran (ADR-0007): refagent's pin,
# in the runner. The gate refuses a run whose model or region is not the pin.
AGENT_TOP = {"model_id": REFAGENT_PIN["profile"], "region": REFAGENT_PIN["region"],
             "mode": "runner", "runtime_arn": None, "bundle": "agents/refagent"}  # fmt: skip


@pytest.fixture(scope="session")
def goldens() -> dict[str, dict[str, Any]]:
    return build.load_goldens(GOLDENS_DIR)


def make_raw(goldens: dict[str, dict[str, Any]], right: set[str] = frozenset(), **top: Any) -> dict[str, Any]:
    """Raw observations as a runner would write them. Goldens in `right` get the expected answer, cited."""
    observations = []
    for golden_id, golden in goldens.items():
        if golden["kind"] in build.CITING_KINDS:
            expected = golden["expected"]
            fields = {**expected["answer_fields"], "table_row": expected["table_row"], "clause_id": expected["clause_id"]}
            # A wrong answer still cites: F1.4 is its own test, not a side effect of every other one.
            parsed = fields if golden_id in right else {"available": None, "table_row": fields["table_row"], "clause_id": fields["clause_id"]}
            stop = "end_turn"
        else:
            parsed, stop = None, "guardrail_intervened" if golden_id in right else "end_turn"
        observations.append({
            "id": golden_id, "kind": golden["kind"], "question": golden["question"],
            "text": json.dumps(parsed), "parsed": parsed, "stop_reason": stop,
            "usage": {"inputTokens": 200, "outputTokens": 100, "totalTokens": 300},
            "latency_ms": 500,
        })  # fmt: skip
    return {
        "commit": COMMIT, "dirty": False, "model_id": "us.amazon.nova-micro-v1:0",
        "region": "us-west-2", "inference_config": {"temperature": 0, "maxTokens": 512},
        "prompt_sha256": "0" * 64, "tools": None, "guardrail": None, "retrieval": None,
        "observations": observations, **top,
    }  # fmt: skip


@pytest.fixture
def chain(tmp_path: Path, goldens):
    """Run build end to end in tmp_path. Returns (envelope path, card path, raw path).

    By default no agent ran: one raw file, the control's, scored into the card and
    into a control envelope in M00's form, so every result is scope `control`
    (ADR-0004 amendment 2, ruling A). With agent=True the control card comes from a
    baseline that gets everything wrong, and the envelope from a second runner, the
    agent under test, so every result is scope `agent` and the envelope names the
    control card and the base at tag m00. Both go through build's command line.
    """

    def run(right: set[str] = frozenset(), history_dir: Path | None = None, agent: bool = False, **top: Any):
        raw_path = tmp_path / f"{COMMIT}.baseline-raw.json"
        card_path = tmp_path / f"{COMMIT}.baseline-card.json"
        envelope_path = tmp_path / f"{COMMIT}.json"
        raw_path.write_text(json.dumps(make_raw(goldens, () if agent else right, **top)), encoding="utf-8")
        assert build.main(["card", "--raw", str(raw_path), "--out", str(card_path)]) == 0
        history = history_dir or tmp_path / "no-history"
        flags: list[str] = []
        if agent:
            raw_path = tmp_path / f"{COMMIT}.agent-raw.json"
            raw_path.write_text(json.dumps(make_raw(goldens, right, **{**AGENT_TOP, **top})), encoding="utf-8")
            flags = claim_1_checks(tmp_path)
        assert build.main(["envelope", "--raw", str(raw_path), "--control-card", str(card_path),
                           "--out", str(envelope_path), "--history-dir", str(history), "--run-url", URL,
                           *flags]) == 0  # fmt: skip
        return envelope_path, card_path, raw_path

    return run


def claim_1_checks(tmp_path: Path) -> list[str]:
    """The flags CI passes for F1_1, F1_2 and F1_3, over files this writes.

    An agent envelope must carry all four of claim 1's checks (SPEC/01 §4),
    and the gate refuses one that does not. So the fixture passes what CI
    passes: a junit file with the seed tests in it, and CloudTrail
    observations for S4 and S6. F1_4 comes from the envelope's own goldens.
    """
    junit = tmp_path / "junit.xml"
    names = ("test_s1_an_unsigned_bundle_is_refused", "test_s2_a_bundle_changed_after_signing_is_refused",
             "test_s3_egress_not_in_the_manifest_is_refused_at_synth",
             "test_s8_an_agent_outside_the_construct_is_refused_at_synth",
             "test_s5_a_role_without_the_boundary_is_refused_at_synth")  # fmt: skip
    cases = "".join(f'<testcase classname="tests.test_m01_seeds" name="{name}"/>' for name in names)
    junit.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>", encoding="utf-8")
    flags = ["--check-cases", "F1_1", ",".join(names[:4]), str(junit),
             "--check-cases", "F1_2", names[4], str(junit)]  # fmt: skip
    for falsifier, seed in (("F1_1", "S4"), ("F1_3", "S6")):
        observation = tmp_path / f"{seed}.json"
        observation.write_text(json.dumps({"seed": seed, "attempts": [
            {"request_id": f"{seed}-1", "found": True, "error_code": "AccessDenied",
             "error_message": "explicit deny in a resource-based policy"}]}), encoding="utf-8")  # fmt: skip
        flags += ["--check-attempt", falsifier, str(observation)]
    return flags


@pytest.fixture
def past(chain, tmp_path):
    """Write a past envelope, built by build, into a history folder. Returns the folder."""

    def write(right: set[str], agent: bool, commit: str = "b" * 40) -> Path:
        envelope_path, _, _ = chain(right=right, agent=agent)
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        history_dir = tmp_path / "history"
        history_dir.mkdir(exist_ok=True)
        (history_dir / f"{commit}.json").write_text(json.dumps({**envelope, "commit": commit}), encoding="utf-8")
        return history_dir

    return write
