"""Run refagent over the goldens and write raw observations (P5, ruling l).

    python -m src.agent.run --out evals/local/<commit>.agent-raw.json

This is a runner. It reads each golden's id, kind and question, never its
`expected`. It scores nothing and writes no envelope; only
`src/verdict/build.py` does that, and only `src/verdict/gate.py` rules.

Two modes, and the raw file says which one ran (`where`):

- **in the runner.** refagent's code runs here, against the pinned
  inference profile. This is a pull request's mode whenever the deployed
  runtime does not run the tree's bundle.
- **the deployed runtime.** `AGENTKEEL_RUNTIME_ARN` names it, and the runner
  calls `InvokeAgentRuntime` (ruling f). `evals.yml` sets it only when
  `scripts/runtime_for_tree.py` finds the tree's bundle digest among the
  runtime image's tags (ADR-0007, P1).

The first line this prints is `mode: runner (AGENTKEEL_RUNTIME_ARN unset)`
or `mode: runtime <arn>`, because the fallback used to be silent and the
envelope could not tell the two apart. From ADR-0007 it can: this raw file
carries `mode`, `runtime_arn` and `bundle`, and `verdict.build` copies them
into the envelope. Construct tenancy is read at M01 PR 4's run (ledger row 1).

The model id, the profile and the region come from
`agents/refagent/manifest.yaml`, not from here: the Threshold Owner owns
them and a runner that carried its own copy could measure a model the
manifest does not name.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.exceptions import BotoCoreError, ClientError

from agents.refagent import agent
from src import manifest as manifest_module

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = "agents/refagent"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def dirty() -> bool:
    """Is the tree other than what this commit names?

    `evals/` is excluded, and it has to be: the control runs first and its
    card is written into `evals/history/` before this runner starts, so
    without the exclusion every CI run would see a dirty tree and `build`
    would refuse the envelope. What this run writes is not what it ran.
    `src/baseline/run.py` has no such line because nothing writes there
    before it, and it is frozen at tag m00 either way.
    """
    return bool(git("status", "--porcelain", "--", ".", ":(exclude)evals"))


def invoke_deployed(client: Any, runtime_arn: str, question: str) -> dict[str, Any]:
    """The deployed runtime answers. The payload is the observation refagent's code would have written."""
    response = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        payload=json.dumps({"question": question}).encode("utf-8"),
    )
    body = response["response"].read() if hasattr(response["response"], "read") else response["response"]
    return json.loads(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--goldens", type=Path, default=ROOT / "evals" / "goldens" / "v1")
    args = parser.parse_args(argv)

    manifest = manifest_module.load(ROOT / BUNDLE / "manifest.yaml")
    model_id, region = manifest["model"]["profile"], manifest["model"]["region"]
    runtime_arn = os.environ.get("AGENTKEEL_RUNTIME_ARN")
    table = os.environ.get("AGENTKEEL_RIGHTS_TABLE")

    # The mode, before anything else it prints. The fallback used to be
    # silent, and a silent fallback is how "refagent in the runner" and
    # "refagent in the construct" became the same envelope.
    print(f"mode: runtime {runtime_arn}" if runtime_arn else "mode: runner (AGENTKEEL_RUNTIME_ARN unset)")

    if runtime_arn:
        client: Any = boto3.client("bedrock-agentcore", region_name=region)
        rows, source = [], "the deployed runtime reads its own table"
    else:
        client = boto3.client("bedrock-runtime", region_name=region)
        rows, source = agent.rights_rows(table, boto3.client("dynamodb", region_name=region) if table else None)

    observations, errors = [], 0
    for path in sorted(args.goldens.glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        if golden.get("retired") is not None:
            # M02 PR 2 (Door 2): a retired golden is not asked. The frozen
            # control still asks it (ADR-0002); build drops that answer.
            print(f"{golden['id']} {golden['kind']:<9} retired at {golden['retired']}; not asked")
            continue
        entry = {"id": golden["id"], "kind": golden["kind"], "question": golden["question"]}
        try:
            if runtime_arn:
                entry.update(invoke_deployed(client, runtime_arn, golden["question"]))
            else:
                entry.update(agent.answer(client, golden["question"], model_id, rows, source))
        except (BotoCoreError, ClientError, ValueError, KeyError) as exc:  # a failed call is an observation too
            entry["error"] = f"{type(exc).__name__}: {exc}"
        observations.append(entry)
        # `agent.answer` returns its own failures rather than raising, so that a
        # golden which spent and then failed still reports what it spent. Count
        # and print those too: a runner that said "0 errors" while every call
        # failed is a runner that cannot be read (M01 PR 2, run 35477627103).
        if failure := entry.get("error"):
            errors += 1
            print(f"{entry['id']} {entry['kind']:<9} ERROR        {failure[:160]}")
        else:
            print(f"{entry['id']} {entry['kind']:<9} {entry.get('stop_reason', ''):<12} {entry.get('parsed')}")

    result = {
        "what": "raw observations from refagent; not an envelope; scores nothing",
        "started_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": dirty(),
        "model_id": model_id,
        "region": region,  # the request region, the profile ARN's (item 23)
        "inference_config": agent.INFERENCE_CONFIG,
        "prompt_sha256": hashlib.sha256(agent.PROMPT.encode("utf-8")).hexdigest(),
        "tools": [agent.CONTRACT["name"] + "@" + agent.CONTRACT["version"]],
        "guardrail": None,  # M03
        "retrieval": None,  # the knowledge base is cut to M03 (SPEC/01 §10, cut 3)
        "where": "the deployed runtime" if runtime_arn else "refagent's code, in the runner",
        # ADR-0007: what verdict.build copies into the envelope, which the gate
        # then checks for pairing and against the bundle's manifest pin.
        "mode": "runtime" if runtime_arn else "runner",
        "runtime_arn": runtime_arn or None,
        "bundle": BUNDLE,
        "rights_table": source,
        "observations": observations,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.out} ({len(observations)} observations, {errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
