"""Seed S8 (SPEC/01 §5, F1.1): an AgentCore runtime made directly, with no GovernedAgent.

"An agent exists on this platform only as an instance of the construct"
(SPEC/01 §2). A check over the whole synthesised stack must refuse this.
It imports `infra.construct` only for that check, which does not exist
until M01 PR 2; that failure is the seed standing. The resource is the
raw CloudFormation type, so no construct API can change what it is.
"""

import aws_cdk as cdk

from infra.construct import refuse_outside_construct

app = cdk.App()
stack = cdk.Stack(app, "SeedS8OutsideConstruct", env=cdk.Environment(region="us-west-2"))
cdk.CfnResource(
    stack,
    "BareRuntime",
    type="AWS::BedrockAgentCore::Runtime",
    properties={
        "AgentRuntimeName": "refagent_bare",
        "NetworkConfiguration": {"NetworkMode": "PUBLIC"},
    },
)
refuse_outside_construct(stack)
app.synth()
