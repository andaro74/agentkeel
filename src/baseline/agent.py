"""The naive baseline (SPEC/00 §8 M00).

Converse on the pinned baseline model. One prompt, no tools, no guardrail,
no retrieval. Reads nothing under data/. It is meant to lose.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# Pinned by the Threshold Owner at the top of milestones/M00/README.md.
MODEL_ID = "us.amazon.nova-micro-v1:0"
REGION = "us-west-2"
INFERENCE_CONFIG = {"temperature": 0, "maxTokens": 512}

PROMPT = (Path(__file__).parent / "prompt.txt").read_text(encoding="utf-8")


def parse_json(text: str) -> dict[str, Any] | None:
    """The outermost JSON object in the reply, or None. No repair."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def answer(client: Any, question: str) -> dict[str, Any]:
    """One Converse call. Returns the raw observation; judges nothing."""
    started = time.perf_counter()
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": PROMPT}],
        messages=[{"role": "user", "content": [{"text": question}]}],
        inferenceConfig=INFERENCE_CONFIG,
    )
    latency_ms = round((time.perf_counter() - started) * 1000)
    text = "".join(
        block.get("text", "") for block in response["output"]["message"]["content"]
    )
    return {
        "text": text,
        "parsed": parse_json(text),
        "stop_reason": response["stopReason"],
        "usage": response["usage"],
        "latency_ms": latency_ms,
    }
