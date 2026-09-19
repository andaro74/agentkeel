"""GovernedAgent, beyond the seeded cases (SPEC/01 §6, ruling SCOPE).

S3, S5 and S8 are in `tests/test_m01_seeds.py`. These are the rules the
construct has that no seed covers: Gateway and Identity declared and not
wired, an imported role refused, and the stack that refagent deploys as
synthesising with nothing refused.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from infra.construct import synth_refusal

ROOT = Path(__file__).resolve().parents[1]
APPS = Path(__file__).parent / "fixtures" / "construct"
TEMPLATE = ROOT / "infra" / "construct" / "cdk.out" / "AgentkeelRefagent.template.json"


def app(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "app.py"
    path.write_text(
        "import aws_cdk as cdk\n"
        "from aws_cdk import aws_iam as iam\n"
        "from infra.construct import GovernedAgent\n"
        'app = cdk.App()\n'
        'stack = cdk.Stack(app, "T", env=cdk.Environment(region="us-west-2"))\n'
        f"{body}\n"
        "app.synth()\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize("prop", ["gateway", "identity"])
def test_gateway_and_identity_are_declared_and_not_wired(tmp_path, prop):
    """Ruling SCOPE, finding 17: the construct declares both props and wires neither."""
    refusal = synth_refusal(app(tmp_path, f'GovernedAgent(stack, "R", bundle="agents/refagent", {prop}=object())'))
    assert refusal is not None
    assert f"{prop.title()} is a declared prop and is not wired at M01" in refusal


def test_an_imported_role_is_refused(tmp_path):
    """CDK cannot see whether an imported role has the boundary, and a check that cannot see is not a check."""
    refusal = synth_refusal(app(tmp_path, (
        'role = iam.Role.from_role_arn(stack, "Imported", "arn:aws:iam::111122223333:role/agentkeel/agents/x")\n'
        'GovernedAgent(stack, "R", bundle="agents/refagent", role=role)'
    )))
    assert refusal is not None and "an imported role" in refusal


def test_refagents_own_stack_synthesises():
    """The stack the seeds are a copy of, with one thing added, must itself pass."""
    assert synth_refusal(ROOT / "infra" / "construct" / "app.py") is None


def test_the_runtime_is_in_the_vpc_and_the_egress_is_the_manifests():
    """Read from the template `make validate` just wrote, not from the construct's own claim."""
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    resources = template["Resources"].values()
    runtimes = [r for r in resources if r["Type"] == "AWS::BedrockAgentCore::Runtime"]
    assert len(runtimes) == 1
    network = runtimes[0]["Properties"]["NetworkConfiguration"]
    assert network["NetworkMode"] == "VPC"
    assert len(network["NetworkModeConfig"]["SecurityGroups"]) == 1

    groups = [r for r in resources if r["Type"] == "AWS::EC2::SecurityGroup"]
    assert len(groups) == 1
    # Five endpoints in the manifest, five rules. CDK renders a prefix-list
    # rule as its own resource and a security-group one inline, so the count
    # is over both forms: s3 and dynamodb are gateway endpoints (ADR-0006).
    inline = groups[0]["Properties"]["SecurityGroupEgress"]
    apart = [r["Properties"] for r in resources if r["Type"] == "AWS::EC2::SecurityGroupEgress"]
    egress = inline + apart
    assert (len(inline), len(apart)) == (3, 2)
    assert all(rule["ToPort"] == 443 and rule["IpProtocol"] == "tcp" for rule in egress)
    assert not any("CidrIp" in rule or "CidrIpv6" in rule for rule in egress)
    assert all("DestinationPrefixListId" in rule for rule in apart)


def test_every_role_in_the_stack_carries_a_boundary():
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    roles = [r for r in template["Resources"].values() if r["Type"] == "AWS::IAM::Role"]
    assert roles and all(r["Properties"].get("PermissionsBoundary") for r in roles)
    assert all(r["Properties"].get("Path") == "/agentkeel/agents/" for r in roles)
