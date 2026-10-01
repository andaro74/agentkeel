"""refagent's stack: one `GovernedAgent`, and nothing else (Security seat).

This is the stack `deploy.yml` deploys from `main`, after the bundle is
packed, signed and verified. It is also the stack `make validate` runs
cdk-nag over, and the one the seeded cases S3, S5 and S8 are refusals
against: each seed is this stack with one thing added or taken away.

    cd infra/construct && npx cdk diff && npx cdk deploy

From M06 PR 2 (SPEC/06 section 6, R3) the same file synthesises an agent from
the template: `AGENTKEEL_BUNDLE=agents/<name>` (deploy.yml places the agent
repository's folder there) gives the stack `AgentkeelAgent`, deployed as
`agentkeel-<name>`. Unset, it is refagent's, exactly as before.

The image digest comes from the deploy, not from here:
`AGENTKEEL_IMAGE_DIGEST` is the digest of the image `deploy.yml` pushed in
the same run. Without it the stack synthesises against a digest that
cannot be pulled, which is what a synth is for and what a deploy must not
have.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import aws_cdk as cdk
from cdk_nag import AwsSolutionsChecks, NagSuppressions

# The cdk CLI runs this file from `infra/construct/`, so the repository root
# is not on the path and `infra.construct` would not import. `make validate`
# runs it with PYTHONPATH set; both end up here.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from infra.construct.governed_agent import GovernedAgent  # noqa: E402

REGION = "us-west-2"
BUNDLE = os.environ.get("AGENTKEEL_BUNDLE", "agents/refagent").rstrip("/")
REFAGENT = BUNDLE == "agents/refagent"
# refagent's ids are the ones it was deployed under, so its resources are not replaced.
STACK_ID, AGENT_ID = ("AgentkeelRefagent", "Refagent") if REFAGENT else ("AgentkeelAgent", "Agent")


class RefagentStack(cdk.Stack):
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.agent = GovernedAgent(
            self, AGENT_ID,
            bundle=BUNDLE,
            image_digest=os.environ.get("AGENTKEEL_IMAGE_DIGEST"),
        )  # fmt: skip
        cdk.CfnOutput(self, "RuntimeArn", value=self.agent.runtime.attr_agent_runtime_arn)
        cdk.CfnOutput(self, "AgentRoleArn", value=self.agent.role.role_arn)


# A fixed output directory, so `make validate` reads the NagReport of the
# synth it just ran. The cdk CLI sets CDK_OUTDIR; a plain python run does not.
app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = RefagentStack(
    app, STACK_ID,
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M01: refagent, as an instance of GovernedAgent. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
# One suppression per wildcard, each with its own reason naming the seeded
# case or the SPEC/01 section 6 line it serves. A suppression that names neither
# is a finding, not a suppression (Security, M01 PR 2). One reason per finding
# from M05 PR 2 (M03 open.md row 11, item k): the rows had shared one reason,
# which said less about each than each needed.
ACCOUNT = "<AWS::AccountId>"  # how cdk-nag names the account in a finding: it comes from the deployer
RUNTIMES = f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:/aws/bedrock-agentcore/runtimes/*"
GUARDRAIL = stack.agent.manifest["guardrail"]["id"]
WILDCARDS = {
    "Resource::*": (
        "SPEC/01 §6, B1 (M01 PR 3): ecr:GetAuthorizationToken and logs:DescribeLogGroups take no resource-level "
        "permission. The image pull itself is on this agent's repository, by name, and the boundary (seed S5) "
        "caps the rest."
    ),
    f"Resource::{RUNTIMES}": (
        "SPEC/01 §6, 'its own log group': under /aws/bedrock-agentcore/runtimes/*, whose suffix AgentCore "
        "assigns when it makes the runtime; CreateLogGroup and DescribeLogStreams only."
    ),
    f"Resource::{RUNTIMES}:log-stream:*": (
        "SPEC/01 §6, 'its own log group': the runtime's own streams, which AgentCore names at run time; "
        "CreateLogStream and PutLogEvents only. The role and the boundary deny logs:Delete* (seed S5's boundary)."
    ),
    f"Resource::arn:aws:kms:{REGION}:{ACCOUNT}:key/*": (
        "SPEC/01 §6, 'the agent's key': Decrypt and GenerateDataKey on key/* conditioned on kms:ResourceAliases "
        "being this agent's alias, because the key's id is the bootstrap stack's and the construct does not read "
        "it (PR 3 security-reviewer F6). The key policy denies this role its own key policy (seed S6)."
    ),
    f"Resource::arn:aws:bedrock:{REGION}:{ACCOUNT}:guardrail/{GUARDRAIL}:*": (
        "SPEC/01 §6 as built on at M03 PR 2: ApplyGuardrail on the guardrail the manifest pins and <arn>:*, its "
        "numbered versions, and every model invoke is conditioned on bedrock:GuardrailIdentifier at the pinned "
        "version. The boundary (seed S5) caps it."
    ),
    f"Resource::arn:aws:s3:::agentkeel-audit-897698239547/agents/{stack.agent.agent_name}/*": (
        "SPEC/01 §6's boundary (seed S5) as widened at M05 PR 2: PutObject under this agent's own prefix in the "
        "security account's audit bucket, whose keys the agent writes at run time (SPEC/05 §6). The bucket's "
        "policy refuses any other prefix."
    ),
}
NagSuppressions.add_resource_suppressions_by_path(
    stack, f"{STACK_ID}/{AGENT_ID}/Role/DefaultPolicy/Resource",
    [{"id": "AwsSolutions-IAM5", "reason": reason, "appliesTo": [finding]} for finding, reason in WILDCARDS.items()],
)
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
