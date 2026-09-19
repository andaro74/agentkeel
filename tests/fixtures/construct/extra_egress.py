"""Seed S3 (SPEC/01 §5, F1.1): refagent's GovernedAgent, plus one egress rule the manifest does not list.

The construct must refuse this at synth. `infra/construct/` does not exist
until M01 PR 2, so importing it fails today; that failure is the seed
standing. The construct's API is PR 2's: if its names differ, PR 2 changes
the call, never what is added (one egress rule, anywhere, port 443).
"""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2

from infra.construct import GovernedAgent

app = cdk.App()
stack = cdk.Stack(app, "SeedS3ExtraEgress", env=cdk.Environment(region="us-west-2"))
agent = GovernedAgent(stack, "Refagent", bundle="agents/refagent")
agent.security_group.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "seed S3: not in the manifest")
app.synth()
