"""Run the baseline over the goldens and write raw observations (P5).

This is a runner. It reads each golden's id, kind and question, never its
`expected`. It scores nothing and writes no envelope; from M00 PR 2 only
src/verdict/build.py does that.

    python -m src.baseline.run --out evals/local/<name>.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import boto3
import yaml
from botocore.exceptions import BotoCoreError, ClientError

from src.baseline import agent

ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--goldens", type=Path, default=ROOT / "evals" / "goldens" / "v1"
    )
    args = parser.parse_args()

    client = boto3.client("bedrock-runtime", region_name=agent.REGION)
    observations = []
    errors = 0
    for path in sorted(args.goldens.glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        entry = {
            "id": golden["id"],
            "kind": golden["kind"],
            "question": golden["question"],
        }
        try:
            entry.update(agent.answer(client, golden["question"]))
        # a failed call is an observation too
        except (BotoCoreError, ClientError) as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            errors += 1
        observations.append(entry)
        print(
            f"{entry['id']} {entry['kind']:<9} {entry.get('stop_reason', 'ERROR'):<10} {entry.get('parsed')}"
        )

    result = {
        "what": "raw observations from the naive baseline; not an envelope; scores nothing",
        "started_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "model_id": agent.MODEL_ID,
        "region": agent.REGION,
        "inference_config": agent.INFERENCE_CONFIG,
        "prompt_sha256": hashlib.sha256(agent.PROMPT.encode("utf-8")).hexdigest(),
        "tools": None,
        "guardrail": None,
        "retrieval": None,
        "observations": observations,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {args.out} ({len(observations)} observations, {errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
