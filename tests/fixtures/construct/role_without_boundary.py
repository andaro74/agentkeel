"""Seed S5 (SPEC/01 §5, F1.2): GovernedAgent handed an agent role with no permission boundary.

The construct must refuse this at synth. `infra/construct/` does not exist
until M01 PR 2, so importing it fails today; that failure is the seed
standing. The construct's API is PR 2's: if its names differ, PR 2 changes
the call, never what is handed in (a role with no boundary).
"""

import aws_cdk as cdk
from aws_cdk import aws_iam as iam

from infra.construct import GovernedAgent

app = cdk.App()
stack = cdk.Stack(app, "SeedS5RoleWithoutBoundary", env=cdk.Environment(region="us-west-2"))
role = iam.Role(stack, "NoBoundary", assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"))
GovernedAgent(stack, "Refagent", bundle="agents/refagent", role=role)
app.synth()
