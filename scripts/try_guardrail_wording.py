"""Try the rule files' wording on a temporary guardrail before a deploy (M03 PR 2).

    python scripts/try_guardrail_wording.py      # admin credentials, agent account, us-west-2

Builds a guardrail named `agentkeel-wording-trial-<time>` from the working
tree's `agents/refagent/rules/` exactly as the bootstrap stack would
(`guardrail_spec`), runs `probe_guardrail`'s check on every live golden
against its DRAFT, prints the table, and deletes the guardrail whatever
happened. Exit 1 on any mismatch.

Why it exists: the first two deployed versions blocked g-006, an
ordinary golden, and each rewording otherwise costs a bootstrap deploy.
A trial is not evidence of the deployed guardrail; `probe_guardrail.py`
on the deployed version is, and it is still run after the deploy.

Only an admin can run it: every platform role is denied Create and
Delete on a guardrail (infra/bootstrap/app.py, GUARDRAIL_DENIED).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import time
from pathlib import Path

import boto3
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import probe_guardrail as probe


def bootstrap_spec() -> dict:
    """guardrail_spec from infra/bootstrap/app.py; importing it synthesises once, into a temporary folder."""
    os.environ.setdefault("CDK_OUTDIR", tempfile.mkdtemp())
    spec = importlib.util.spec_from_file_location("bootstrap_app", ROOT / "infra" / "bootstrap" / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.guardrail_spec()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    spec = bootstrap_spec()
    bedrock = boto3.client("bedrock", region_name="us-west-2")
    runtime = boto3.client("bedrock-runtime", region_name="us-west-2")
    created = bedrock.create_guardrail(
        name=f"agentkeel-wording-trial-{int(time.time())}",
        description=f"temporary: rules sha256 {spec['digest']} (scripts/try_guardrail_wording.py)",
        topicPolicyConfig={"topicsConfig": [
            {"name": t["name"], "definition": t["definition"], "examples": t.get("examples", []), "type": "DENY"}
            for t in spec["topics"]]},
        sensitiveInformationPolicyConfig={"piiEntitiesConfig": [
            {"type": e["entity"], "action": e["action"]} for e in spec["pii"]]},
        blockedInputMessaging=spec["messages"]["blocked_input"],
        blockedOutputsMessaging=spec["messages"]["blocked_output"],
    )  # fmt: skip
    guardrail_id = created["guardrailId"]
    try:
        for _ in range(30):
            if bedrock.get_guardrail(guardrailIdentifier=guardrail_id)["status"] == "READY":
                break
            time.sleep(2)
        rules = ROOT / "agents" / "refagent" / "rules"
        guardrail = yaml.safe_load((rules / "guardrail.yaml").read_text(encoding="utf-8"))
        redteam = yaml.safe_load((rules / "redteam.yaml").read_text(encoding="utf-8"))
        plants, blocks = set(guardrail["plants"]) | set(redteam["plants"]), redteam["blocks"]
        bad = 0
        print(f"trial guardrail {guardrail_id} DRAFT, rules sha256 {spec['digest']}\n")
        print("| Golden | Kind | Expected | Action | Topics matched | |")
        print("|---|---|---|---|---|---|")
        for path in sorted((ROOT / "evals" / "goldens" / "v1").glob("g-*.yaml")):
            golden = yaml.safe_load(path.read_text(encoding="utf-8"))
            if golden.get("retired") is not None:
                continue
            response = runtime.apply_guardrail(guardrailIdentifier=guardrail_id, guardrailVersion="DRAFT",
                                               source="INPUT", content=[{"text": {"text": golden["question"]}}])  # fmt: skip
            action, topics = response["action"], probe.matched_topics(response.get("assessments", []))
            expect = probe.expectation(golden, plants, blocks)
            ok = probe.judge(expect, action, topics)
            bad += not ok
            wanted = expect[0] + (f" by {expect[1]}" if expect[1] else "")
            print(f"| {golden['id']} | {golden['kind']} | {wanted} | {action} | {', '.join(topics) or '—'} |"
                  f"{'' if ok else ' **MISMATCH**'} |")  # fmt: skip
        print(f"\nmismatches: {bad}")
        return 1 if bad else 0
    finally:
        bedrock.delete_guardrail(guardrailIdentifier=guardrail_id)
        print(f"deleted {guardrail_id}")


if __name__ == "__main__":
    sys.exit(main())
