"""Seed S3, second form (SPEC/01 §5, F1.1): the egress rule added as its own resource, outside the construct.

A check inside `GovernedAgent` sees only its own children; this rule is not
one of them. The refusal must read the whole synthesised stack. The
construct's API is PR 2's: if its names differ, PR 2 changes the call,
never what is added (one egress rule to 0.0.0.0/0:443, as a separate
resource naming the agent's security group).
"""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2

from infra.construct import GovernedAgent

app = cdk.App()
stack = cdk.Stack(app, "SeedS3ExtraEgressStandalone", env=cdk.Environment(region="us-west-2"))
agent = GovernedAgent(stack, "Refagent", bundle="agents/refagent")
ec2.CfnSecurityGroupEgress(
    stack,
    "NotInTheManifest",
    group_id=agent.security_group.security_group_id,
    ip_protocol="tcp",
    from_port=443,
    to_port=443,
    cidr_ip="0.0.0.0/0",
    description="seed S3: not in the manifest, added from outside the construct",
)
app.synth()
