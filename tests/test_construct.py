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
    # Seven endpoints in the manifest, seven rules. CDK renders a prefix-list
    # rule as its own resource and a security-group one inline, so the count
    # is over both forms: s3 and dynamodb are gateway endpoints (ADR-0006).
    inline = groups[0]["Properties"]["SecurityGroupEgress"]
    apart = [r["Properties"] for r in resources if r["Type"] == "AWS::EC2::SecurityGroupEgress"]
    egress = inline + apart
    assert (len(inline), len(apart)) == (5, 2)  # ecr.api and ecr.dkr since M01 PR 3 (ruling d, amended)
    assert all(rule["ToPort"] == 443 and rule["IpProtocol"] == "tcp" for rule in egress)
    assert not any("CidrIp" in rule or "CidrIpv6" in rule for rule in egress)
    assert all("DestinationPrefixListId" in rule for rule in apart)


def test_every_role_in_the_stack_carries_the_agent_boundary(template):
    """Ruling s: an agent-path role carries the agent plane's allow-list, and no other.

    The ARN is a Security-owned SSM parameter, so what the template can say
    is which parameter it reads. That is the point: the construct cannot
    name a boundary of its own.
    """
    boundary_param = [
        logical for logical, parameter in template.get("Parameters", {}).items()
        if parameter.get("Default") == "/agentkeel/security/boundary-arn"
    ]  # fmt: skip
    assert len(boundary_param) == 1
    roles = [r for r in template["Resources"].values() if r["Type"] == "AWS::IAM::Role"]
    assert roles
    for role in roles:
        assert role["Properties"].get("PermissionsBoundary") == {"Ref": boundary_param[0]}
        assert role["Properties"].get("Path") == "/agentkeel/agents/"


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


# --- B2 (M01 PR 3): the agent can call the model it is given ---------------
#
# The role named `application-inference-profile/agentkeel-refagent`, which
# is no ARN AWS assigns, and the runtime was handed the system profile,
# which the role was never granted. The stack would have deployed and every
# call would have been refused. These read the rendered template.


def agent_statements(template: dict) -> list[dict]:
    policy = next(r for r in template["Resources"].values() if r["Type"] == "AWS::IAM::Policy")
    return policy["Properties"]["PolicyDocument"]["Statement"]


def profile_arn(template: dict) -> dict:
    logical = next(k for k, r in template["Resources"].items()
                   if r["Type"] == "AWS::Bedrock::ApplicationInferenceProfile")  # fmt: skip
    return {"Fn::GetAtt": [logical, "InferenceProfileArn"]}


def test_the_role_may_call_the_profile_aws_actually_made(template):
    invoke = [s for s in agent_statements(template) if "bedrock:InvokeModel" in s["Action"] and "Condition" not in s]
    assert len(invoke) == 1
    assert invoke[0]["Resource"] == profile_arn(template), "a profile ARN built from its name names nothing"


def test_the_runtime_is_given_the_profile_its_role_may_call(template):
    runtime = next(r for r in template["Resources"].values() if r["Type"] == "AWS::BedrockAgentCore::Runtime")
    assert runtime["Properties"]["EnvironmentVariables"]["AGENTKEEL_MODEL_PROFILE"] == profile_arn(template)


def test_the_model_is_reachable_only_through_the_agents_own_profile(template):
    direct = [s for s in agent_statements(template)
              if "bedrock:InvokeModel" in s["Action"] and "foundation-model" in json.dumps(s["Resource"])]  # fmt: skip
    assert len(direct) == 1
    assert direct[0]["Condition"] == {"StringEquals": {"bedrock:InferenceProfileArn": profile_arn(template)}}
    assert all(arn.endswith("::foundation-model/anthropic.claude-sonnet-4-6") for arn in direct[0]["Resource"])


# --- B1 (M01 PR 3): the runtime can pull its own image -----------------------


def test_a_manifest_without_the_image_pull_endpoints_is_refused_at_synth(tmp_path):
    """Ruling d, amended. refagent's own manifest, less the two lines: the manifest
    an agent written before the amendment would have. It is still schema-valid."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = (ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8")
    trimmed = "\n".join(line for line in manifest.splitlines() if line not in ("  - ecr.api", "  - ecr.dkr"))
    assert trimmed != manifest
    (bundle / "manifest.yaml").write_text(trimmed, encoding="utf-8")
    refusal = synth_refusal(app(tmp_path, f'GovernedAgent(stack, "R", bundle={str(bundle)!r})'))
    assert refusal is not None
    assert "endpoint_allowlist lacks ecr.api, ecr.dkr" in refusal


def test_the_role_pulls_its_own_image_read_only(template):
    pulls = [s for s in agent_statements(template) if "ecr:BatchGetImage" in s["Action"]]
    assert len(pulls) == 1
    assert set(pulls[0]["Action"]) == {"ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"}
    assert json.dumps(pulls[0]["Resource"]).endswith(':repository/agentkeel-refagent"]]}')
    named = {a for s in agent_statements(template) for a in (s["Action"] if isinstance(s["Action"], list) else [s["Action"]])}
    assert not {a for a in named if a.startswith("ecr:")} - {"ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer",
                                                              "ecr:GetAuthorizationToken"}  # fmt: skip


def test_the_role_makes_its_log_group_under_agentcores_prefix_only(template):
    groups = [s for s in agent_statements(template) if "logs:CreateLogGroup" in s["Action"]]
    assert len(groups) == 1
    assert ":log-group:/aws/bedrock-agentcore/runtimes/*" in json.dumps(groups[0]["Resource"])


def test_no_action_the_role_names_is_one_iam_does_not_have(template):
    """`bedrock:Converse` is not an IAM action; Converse is authorised as InvokeModel."""
    named = {a for s in agent_statements(template) for a in (s["Action"] if isinstance(s["Action"], list) else [s["Action"]])}
    assert "bedrock:Converse" not in named
