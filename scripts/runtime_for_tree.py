"""Which deployed runtime, if any, runs this tree's refagent bytes (ADR-0007, P1: Option B).

    python scripts/runtime_for_tree.py [--github-output FILE] [--summary FILE]

A pull request's run measures refagent in the deployed runtime only when the
runtime runs the same bytes as this tree. Otherwise the envelope would say
`runtime` about bytes the tree does not hold. The match:

1. pack `agents/refagent` exactly as `deploy.yml` does. The archive's sha256
   is the bundle digest, and `deploy.yml` tags the image with it;
2. read the runtime's ARN from the `agentkeel-refagent` stack's outputs;
3. read the image digest that runtime runs (`GetAgentRuntime`);
4. read that image's tags (`ecr:DescribeImages`). A match means the bundle
   digest is among them.

On a match it writes `arn=<runtime ARN>`. On anything else — no stack, other
bytes, a refused call — it writes `arn=` and the reason. The run then
measures in the runner, and the envelope says `mode: runner`. **It never
fails the job, and it is never silent** (the condition on P1): the reason
goes to stdout and to the job summary, because the envelope has no field
for it.

What it does not do: prove the runtime answered. That is the run itself,
whose envelope says `runtime` only if this found a match and the calls were
made.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bundle import pack  # noqa: E402

BUNDLE = ROOT / "agents" / "refagent"
STACK = "agentkeel-refagent"
REPOSITORY = "agentkeel-refagent"
REGION = "us-west-2"


def bundle_digest(bundle: Path = BUNDLE) -> str:
    """The digest `deploy.yml` tags the image with: the sha256 of the packed archive."""
    with tempfile.TemporaryDirectory() as out:
        return pack.digest(pack.pack(bundle, Path(out) / pack.ARCHIVE_NAME))


def deployed(session: boto3.session.Session | None = None) -> tuple[str, list[str]]:
    """The runtime's ARN, and the tags on the image it runs."""
    session = session or boto3.session.Session(region_name=REGION)
    outputs = session.client("cloudformation").describe_stacks(StackName=STACK)["Stacks"][0].get("Outputs", [])
    arn = next((o["OutputValue"] for o in outputs if o["OutputKey"] == "RuntimeArn"), None)
    if not arn:
        raise LookupError(f"stack {STACK} has no RuntimeArn output")
    runtime = session.client("bedrock-agentcore-control").get_agent_runtime(agentRuntimeId=arn.rsplit("/", 1)[-1])
    uri = runtime["agentRuntimeArtifact"]["containerConfiguration"]["containerUri"]
    if "@" not in uri:
        raise LookupError(f"the runtime's image is not pinned by digest: {uri}")
    images = session.client("ecr").describe_images(
        repositoryName=REPOSITORY, imageIds=[{"imageDigest": uri.split("@", 1)[1]}]
    )["imageDetails"]
    return arn, [tag for image in images for tag in image.get("imageTags", [])]


def match(digest: str, lookup=deployed) -> tuple[str, str]:
    """(ARN or "", reason). Never raises: a failed lookup is a reason, not an error."""
    try:
        arn, tags = lookup()
    except (BotoCoreError, ClientError, LookupError, KeyError, IndexError) as exc:
        return "", f"runner: the deployed runtime could not be read ({type(exc).__name__}: {exc})"
    if digest in tags:
        return arn, f"runtime: {arn} runs this tree's bundle {digest[:12]}"
    return "", f"runner: the deployed runtime runs other bytes (tags {tags}), not this tree's {digest[:12]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args(argv)

    try:
        digest = bundle_digest()
    except Exception as exc:  # noqa: BLE001 - never fails the job; the reason is the output
        arn, reason = "", f"runner: this tree's bundle could not be packed ({type(exc).__name__}: {exc})"
    else:
        arn, reason = match(digest)
    print(reason)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as out:
            out.write(f"arn={arn}\n")
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as out:
            out.write(f"### Which refagent this run measures\n{reason}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
