"""GovernedAgent, beyond the seeded cases (SPEC/01 §6, ruling SCOPE).

S3, S5 and S8 are in `tests/test_m01_seeds.py`. These are the rules the
construct has that no seed covers: Gateway and Identity declared and not
wired, an imported role refused, and the stack that refagent deploys as
synthesising with nothing refused.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from infra.construct import synth_refusal

ROOT = Path(__file__).resolve().parents[1]
APPS = Path(__file__).parent / "fixtures" / "construct"
REFAGENT_APP = ROOT / "infra" / "construct" / "app.py"


@pytest.fixture(scope="module")
def template(tmp_path_factory) -> dict:
    """refagent's template, synthesised here rather than read from `cdk.out`.

    `cdk.out/` is gitignored and is written by `make validate`. Reading it
    would let these tests pass on a template from an earlier synth, or fail
    on a fresh clone for the wrong reason.
    """
    out = tmp_path_factory.mktemp("synth")
    done = subprocess.run(
        [sys.executable, str(REFAGENT_APP)], cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(out)},
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    return json.loads((out / "AgentkeelRefagent.template.json").read_text(encoding="utf-8"))


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


def test_the_runtime_is_in_the_vpc_and_the_egress_is_the_manifests(template):
    """Read from the rendered template, not from the construct's own claim."""
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


def test_every_role_in_the_stack_carries_a_boundary(template):
    roles = [r for r in template["Resources"].values() if r["Type"] == "AWS::IAM::Role"]
    assert roles and all(r["Properties"].get("PermissionsBoundary") for r in roles)
    assert all(r["Properties"].get("Path") == "/agentkeel/agents/" for r in roles)


def test_the_same_egress_rule_written_raw_is_refused_too(tmp_path):
    """platform-architect BLOCK 3: matched by CloudFormation type, not by Python class."""
    refusal = synth_refusal(app(tmp_path, (
        'a = GovernedAgent(stack, "R", bundle="agents/refagent")\n'
        'cdk.CfnResource(stack, "Raw", type="AWS::EC2::SecurityGroupEgress", properties={\n'
        '    "GroupId": a.security_group.security_group_id, "IpProtocol": "tcp",\n'
        '    "FromPort": 443, "ToPort": 443, "CidrIp": "0.0.0.0/0"})'
    )))
    assert refusal is not None and "egress to 0.0.0.0/0" in refusal
    assert "added outside the construct" in refusal


def test_a_second_runtime_inside_the_construct_is_not_the_constructs_own(tmp_path):
    """platform-architect finding 4: the check is identity, not a place in the tree."""
    refusal = synth_refusal(app(tmp_path, (
        'from aws_cdk import aws_bedrockagentcore as ac\n'
        'a = GovernedAgent(stack, "R", bundle="agents/refagent")\n'
        'ac.CfnRuntime(a, "Extra", agent_runtime_name="extra", role_arn="arn:aws:iam::1:role/x",\n'
        '    agent_runtime_artifact=ac.CfnRuntime.AgentRuntimeArtifactProperty(\n'
        '        container_configuration=ac.CfnRuntime.ContainerConfigurationProperty(container_uri="x")),\n'
        '    network_configuration=ac.CfnRuntime.NetworkConfigurationProperty(network_mode="PUBLIC"))'
    )))
    assert refusal is not None and "not a GovernedAgent's own runtime" in refusal


def test_a_rule_to_an_approved_endpoint_on_a_wider_port_range_is_refused():
    """platform-architect note 1: tcp 1-443 to an approved endpoint reaches more than 443.

    Read directly: through a synth the destination check fires first, because
    an approved destination is an SSM token no fixture can name.
    """
    from infra.construct.governed_agent import _egress_refusal

    approved = {"Ref": "SsmParameterValue"}
    exact = {"destinationSecurityGroupId": approved, "ipProtocol": "tcp", "fromPort": 443, "toPort": 443}
    assert _egress_refusal(exact, [approved]) is None
    assert "tcp 1-443" in _egress_refusal({**exact, "fromPort": 1}, [approved])
    assert "udp 443-443" in _egress_refusal({**exact, "ipProtocol": "udp"}, [approved])
    # an absent destination is 0.0.0.0/0 (SPEC/01 §6)
    assert "no destination" in _egress_refusal({"ipProtocol": "tcp", "toPort": 443}, [approved])
