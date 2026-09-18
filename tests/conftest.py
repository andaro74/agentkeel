"""Shared test helpers. Nothing here calls a model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.verdict import ROOT, build

GOLDENS_DIR = ROOT / "evals" / "goldens" / "v1"
COMMIT = "a" * 40
URL = "https://github.com/andaro74/agentkeel/actions/runs/1"


@pytest.fixture(scope="session")
def goldens() -> dict[str, dict[str, Any]]:
    return build.load_goldens(GOLDENS_DIR)


def make_raw(goldens: dict[str, dict[str, Any]], right: set[str] = frozenset(), **top: Any) -> dict[str, Any]:
    """Raw observations as a runner would write them. Goldens in `right` get the expected answer."""
    observations = []
    for golden_id, golden in goldens.items():
        if golden["kind"] in build.CITING_KINDS:
            fields = golden["expected"]["answer_fields"]
            parsed = dict(fields) if golden_id in right else {"available": None}
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

    By default the run is the baseline itself, as at M00: one raw file, scored into
    the card and into the envelope, so every result is scope `control`.
    With agent=True the card comes from a baseline that gets everything wrong and the
    envelope from a second runner, the agent under test, so every result is scope `agent`.
    """

    def run(right: set[str] = frozenset(), history_dir: Path | None = None, agent: bool = False, **top: Any):
        raw_path = tmp_path / f"{COMMIT}.baseline-raw.json"
        card_path = tmp_path / f"{COMMIT}.baseline-card.json"
        envelope_path = tmp_path / f"{COMMIT}.json"
        raw_path.write_text(json.dumps(make_raw(goldens, () if agent else right, **top)), encoding="utf-8")
        assert build.main(["card", "--raw", str(raw_path), "--out", str(card_path)]) == 0
        if agent:
            raw_path = tmp_path / f"{COMMIT}.agent-raw.json"
            raw_path.write_text(json.dumps(make_raw(goldens, right, model_id="agent-under-test", **top)), encoding="utf-8")
        history = ["--history-dir", str(history_dir or tmp_path / "no-history")]
        assert build.main(["envelope", "--raw", str(raw_path), "--baseline-card", str(card_path),
                           "--out", str(envelope_path), *history]) == 0  # fmt: skip
        return envelope_path, card_path, raw_path

    return run


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
