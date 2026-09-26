"""refagent's stack: one `GovernedAgent`, and nothing else (Security seat).

This is the stack `deploy.yml` deploys from `main`, after the bundle is
packed, signed and verified. It is also the stack `make validate` runs
cdk-nag over, and the one the seeded cases S3, S5 and S8 are refusals
against: each seed is this stack with one thing added or taken away.

    cd infra/construct && npx cdk diff && npx cdk deploy

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


class RefagentStack(cdk.Stack):
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.agent = GovernedAgent(
            self, "Refagent",
            bundle="agents/refagent",
            image_digest=os.environ.get("AGENTKEEL_IMAGE_DIGEST"),
        )  # fmt: skip
        cdk.CfnOutput(self, "RuntimeArn", value=self.agent.runtime.attr_agent_runtime_arn)
        cdk.CfnOutput(self, "AgentRoleArn", value=self.agent.role.role_arn)


# A fixed output directory, so `make validate` reads the NagReport of the
# synth it just ran. The cdk CLI sets CDK_OUTDIR; a plain python run does not.
app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = RefagentStack(
    app, "AgentkeelRefagent",
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M01: refagent, as an instance of GovernedAgent. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
# One suppression per resource, each naming the seeded case or the SPEC/01 §6
# line it serves. A suppression that names neither is a finding, not a
# suppression (Security, M01 PR 2).
NagSuppressions.add_resource_suppressions_by_path(
    stack, "AgentkeelRefagent/Refagent/Role/DefaultPolicy/Resource",
    [{"id": "AwsSolutions-IAM5",
      "reason": "SPEC/01 §6, 'its own log group' and 'the agent's key'. The log streams are "
                "log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*, because AgentCore names the group "
                "and the stream at runtime. kms:Decrypt and kms:GenerateDataKey are on key/* conditioned on "
                "kms:ResourceAliases being this agent's alias, because the key's id is the bootstrap stack's "
                "and the construct does not read it (PR 3 security-reviewer F6: the earlier reason, 'reached "
                "through the grant', named a grant that does not exist). The boundary (S5) caps all of it, and "
                "the key policy denies this role its own key policy (S6). The profile and the rights table are "
                "named by ARN. B1 (M01 PR 3): "
                "ecr:GetAuthorizationToken and logs:DescribeLogGroups take no resource-level permission; "
                "the image pull is on this agent's repository and the log group under "
                "/aws/bedrock-agentcore/runtimes/*, whose suffix AgentCore assigns. M03 PR 2: ApplyGuardrail is "
                "on the guardrail the manifest pins and <arn>:*, its numbered versions, and every model invoke "
                "is conditioned on bedrock:GuardrailIdentifier at the pinned version."}],
)
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
