"""Which deployed runtime, if any, runs this tree's refagent bundle (ADR-0007, P1: Option B).

    python scripts/runtime_for_tree.py [--github-output FILE] [--summary FILE]

A pull request's run measures refagent in the deployed runtime only when the
runtime runs the same bytes as this tree. Otherwise the envelope would say
`runtime` about bytes the tree does not hold. The match:

1. pack `agents/refagent` exactly as `deploy.yml` does. The archive's sha256
   is the bundle digest, and `deploy.yml` tags the image with it;
2. read the runtime's ARN from the `agentkeel-refagent` stack's outputs;
3. read the image digest that runtime runs (`GetAgentRuntime`);
4. read that image's tags (`ecr:DescribeImages`). A match means the bundle
   digest is among them;
5. from M03 PR 2 (seed S1's reader, SPEC/03 §6), read the rights table
   marker (`ssm:GetParameter`), which `scripts/load_rights_table.py` sets to
   the digest of the table it scanned back after a load. A match also means
   the marker **equals** the digest of this tree's `data/rights_table.json`.
   `unset`, `loading`, another digest, or a marker that cannot be read, is
   the runner (security-reviewer on e2839f2, FINDING 5): the runtime answers
   from its table, and a run on another table's answers is not this tree's.

On a match it writes `arn=<runtime ARN>`. On anything else — no stack, other
bytes, a refused call — it writes `arn=` and the reason. The run then
measures in the runner, and the envelope says `mode: runner`. **Every
lookup failure exits 0 with its reason, and it is never silent** (the
condition on P1): the reason goes to stdout and to the job summary, because
the envelope has no field for it. An import error is outside that promise:
it fails the step, which is loud, not silent.

**What a match proves, and what it does not.** It proves the runtime's image
was built from this tree's *bundle*. It does not prove the image is
reproducible: the Dockerfile's base image is pinned by tag and its packages by
range, and `agents/__init__.py` is copied in from outside the bundle. That is
recorded for M02 (PR 3 security-reviewer F3, cold review N3).

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

from src import rights_table  # noqa: E402
from src.bundle import pack  # noqa: E402

BUNDLE = ROOT / "agents" / "refagent"
STACK = "agentkeel-refagent"
REPOSITORY = "agentkeel-refagent"
REGION = "us-west-2"
MARKER = "/agentkeel/marker/refagent/rights-table-digest"


def bundle_digest(bundle: Path = BUNDLE) -> str:
    """The digest `deploy.yml` tags the image with: the sha256 of the packed archive."""
    with tempfile.TemporaryDirectory() as out:
        return pack.digest(pack.pack(bundle, Path(out) / pack.ARCHIVE_NAME))


def table_digest(root: Path = ROOT) -> str:
    """The digest the marker must equal: this tree's rights table, as the table would store it."""
    return rights_table.file_digest(root)


def marker(session: boto3.session.Session) -> str | None:
    """The table marker, or None when it cannot be read. None is the runner, never a match."""
    try:
        return session.client("ssm").get_parameter(Name=MARKER)["Parameter"]["Value"]
    except (BotoCoreError, ClientError, KeyError):
        return None


def deployed(session: boto3.session.Session | None = None) -> tuple[str, list[str], str | None]:
    """The runtime's ARN, the tags on the image it runs, and the table marker."""
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
    return arn, [tag for image in images for tag in image.get("imageTags", [])], marker(session)


def match(digest: str, table: str, lookup=deployed) -> tuple[str, str]:
    """(ARN or "", reason). Never raises: a failed lookup is a reason, not an error.

    The runtime only when it runs this tree's bundle and answers from this
    tree's rights table; the marker must equal `table`, whatever else it says.
    """
    try:
        arn, tags, held = lookup()
    except (BotoCoreError, ClientError, LookupError, KeyError, IndexError) as exc:
        return "", f"runner: the deployed runtime could not be read ({type(exc).__name__}: {exc})"
    if digest not in tags:
        return "", f"runner: the deployed runtime runs other bytes (tags {tags}), not this tree's {digest[:12]}"
    if held != table:
        said = "could not be read" if held is None else f"says {held[:12]!r}"
        return "", f"runner: the runtime's rights table marker {said}, not this tree's table {table[:12]}"
    return arn, f"runtime: {arn} runs this tree's bundle {digest[:12]} and its rights table {table[:12]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args(argv)

    try:
        digest, table = bundle_digest(), table_digest()
    except Exception as exc:  # noqa: BLE001 - never fails the job; the reason is the output
        arn, reason = "", f"runner: this tree's bundle or table could not be read ({type(exc).__name__}: {exc})"
    else:
        arn, reason = match(digest, table)
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
