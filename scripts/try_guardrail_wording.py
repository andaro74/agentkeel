"""Try the rule files' wording on a temporary guardrail before a deploy (M03 PR 2).

    python scripts/try_guardrail_wording.py                      # the rule files as one guardrail
    python scripts/try_guardrail_wording.py --candidates FILE    # each candidate topic alone

Admin credentials, agent account, us-west-2.

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


GOLDENS = ROOT / "evals" / "goldens" / "v1"


def live_goldens() -> list[dict]:
    goldens = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(GOLDENS.glob("g-*.yaml"))]
    return [g for g in goldens if g.get("retired") is None]


def create(bedrock, topics: list[dict], spec: dict, pii: bool) -> str:
    """A temporary guardrail with these topics, READY. The caller deletes it."""
    config = {
        "name": f"agentkeel-wording-trial-{time.time_ns()}",
        "description": "temporary (scripts/try_guardrail_wording.py)",
        "topicPolicyConfig": {"topicsConfig": [
            {"name": t["name"], "definition": t["definition"], "examples": t.get("examples", []), "type": "DENY"}
            for t in topics]},
        "blockedInputMessaging": spec["messages"]["blocked_input"],
        "blockedOutputsMessaging": spec["messages"]["blocked_output"],
    }  # fmt: skip
    if pii:
        config["sensitiveInformationPolicyConfig"] = {"piiEntitiesConfig": [
            {"type": e["entity"], "action": e["action"]} for e in spec["pii"]]}  # fmt: skip
    guardrail_id = bedrock.create_guardrail(**config)["guardrailId"]
    for _ in range(30):
        if bedrock.get_guardrail(guardrailIdentifier=guardrail_id)["status"] == "READY":
            break
        time.sleep(2)
    return guardrail_id


def ask(runtime, guardrail_id: str, question: str) -> tuple[str, list[str]]:
    response = runtime.apply_guardrail(guardrailIdentifier=guardrail_id, guardrailVersion="DRAFT",
                                       source="INPUT", content=[{"text": {"text": question}}])  # fmt: skip
    return response["action"], probe.matched_topics(response.get("assessments", []))


def whole(bedrock, runtime, spec: dict) -> int:
    """The working tree's rule files as one guardrail: probe_guardrail's table."""
    rules = ROOT / "agents" / "refagent" / "rules"
    guardrail = yaml.safe_load((rules / "guardrail.yaml").read_text(encoding="utf-8"))
    redteam = yaml.safe_load((rules / "redteam.yaml").read_text(encoding="utf-8"))
    plants, blocks = set(guardrail["plants"]) | set(redteam["plants"]), redteam["blocks"]
    guardrail_id = create(bedrock, spec["topics"], spec, pii=True)
    try:
        bad = 0
        print(f"trial guardrail {guardrail_id} DRAFT, rules sha256 {spec['digest']}\n")
        print("| Golden | Kind | Expected | Action | Topics matched | |")
        print("|---|---|---|---|---|---|")
        for golden in live_goldens():
            action, topics = ask(runtime, guardrail_id, golden["question"])
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


def candidates(bedrock, runtime, spec: dict, path: Path) -> int:
    """Each candidate topic alone in its own guardrail, against every live golden.

    `path` is a YAML file: `must_block` (ids), and `candidates`, each a topic
    as guardrail.yaml writes one. A candidate is good when it blocks every id
    in `must_block` and no ordinary or trap golden. One row per candidate.
    """
    wanted = yaml.safe_load(path.read_text(encoding="utf-8"))
    goldens = live_goldens()
    innocent = [g["id"] for g in goldens if g["kind"] in ("ordinary", "trap")]
    good = 0
    print("| Candidate | Blocks of must_block | Ordinary or trap blocked | Other blocked | |")
    print("|---|---|---|---|---|")
    for topic in wanted["candidates"]:
        guardrail_id = create(bedrock, [topic], spec, pii=False)
        try:
            blocked = [g["id"] for g in goldens if ask(runtime, guardrail_id, g["question"])[0] == "GUARDRAIL_INTERVENED"]
        finally:
            bedrock.delete_guardrail(guardrailIdentifier=guardrail_id)
        hit = [i for i in wanted["must_block"] if i in blocked]
        wrong = [i for i in blocked if i in innocent]
        other = [i for i in blocked if i not in innocent and i not in wanted["must_block"]]
        ok = len(hit) == len(wanted["must_block"]) and not wrong
        good += ok
        print(f"| {topic['name']} | {', '.join(hit) or '—'} | {', '.join(wrong) or '—'} | {', '.join(other) or '—'} |"
              f" {'GOOD' if ok else ''} |")  # fmt: skip
    print(f"\ngood candidates: {good} of {len(wanted['candidates'])} (each guardrail deleted after its row)")
    return 0 if good else 1


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--candidates", type=Path, help="try each topic in this file alone, instead of the rule files")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    spec = bootstrap_spec()
    bedrock = boto3.client("bedrock", region_name="us-west-2")
    runtime = boto3.client("bedrock-runtime", region_name="us-west-2")
    return candidates(bedrock, runtime, spec, args.candidates) if args.candidates else whole(bedrock, runtime, spec)


if __name__ == "__main__":
    sys.exit(main())
