"""The M00 eval role (Security seat; ruling on report 2.3, M00 PR 2).

One IAM role that GitHub Actions in andaro74/agentkeel assumes over OIDC to
run `make evals`. It may invoke the six pinned models through their
inference profiles and nothing else. It has no S3, no IAM, no logs.

The GitHub OIDC provider already exists in the account; this stack imports
it and does not create it. Security deploys this once with admin. M01's
bootstrap stack absorbs the role; delete this stack then.

    cd infra/eval-role && npx cdk deploy
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from cdk_nag import AwsSolutionsChecks
from constructs import Construct

REPO = "andaro74/agentkeel"
REGION = "us-west-2"
ROLE_NAME = "agentkeel-m00-evals"

# The six ids pinned by the Threshold Owner in milestones/M00/README.md,
# without the `us.` profile prefix. The judge candidates are not pinned
# until M03 and are not here.
MODELS = [
    "amazon.nova-micro-v1:0",  # baseline
    "anthropic.claude-sonnet-5",  # refagent (M01)
    "anthropic.claude-sonnet-4-6",  # M04 equivalent swap
    "anthropic.claude-haiku-4-5-20251001-v1:0",  # M04 cheaper swap
    "anthropic.claude-sonnet-4-20250514-v1:0",  # M04 deprecation plant
    "meta.llama3-1-8b-instruct-v1:0",  # M04 known-breaking swap
]
# Where each `us.` profile routes, from `aws bedrock get-inference-profile`
# in us-west-2 on 2026-09-18. The same three regions for all six.
PROFILE_REGIONS = ["us-east-1", "us-east-2", "us-west-2"]

INVOKE = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]


class EvalRoleStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self,
            "GitHubOidc",
            f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com",
        )

        role = iam.Role(
            self,
            "EvalRole",
            role_name=ROLE_NAME,
            description="agentkeel M00: GitHub Actions runs make evals. Absorbed by the M01 bootstrap stack.",
            max_session_duration=cdk.Duration.hours(1),
            assumed_by=iam.FederatedPrincipal(
                provider.open_id_connect_provider_arn,
                conditions={
                    # No wildcard: any branch on pull_request, main only on push.
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": [
                            f"repo:{REPO}:pull_request",
                            f"repo:{REPO}:ref:refs/heads/main",
                        ],
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )

        profiles = [
            f"arn:aws:bedrock:{REGION}:{self.account}:inference-profile/us.{model}"
            for model in MODELS
        ]
        role.add_to_policy(
            iam.PolicyStatement(
                sid="InvokePinnedProfiles", actions=INVOKE, resources=profiles
            )
        )
        # A profile call is authorised on the profile and on the model it
        # routes to. The condition stops a direct call to the model.
        role.add_to_policy(
            iam.PolicyStatement(
                sid="InvokePinnedModelsThroughProfilesOnly",
                actions=INVOKE,
                resources=[
                    f"arn:aws:bedrock:{region}::foundation-model/{model}"
                    for model in MODELS
                    for region in PROFILE_REGIONS
                ],
                conditions={"StringEquals": {"bedrock:InferenceProfileArn": profiles}},
            )
        )

        cdk.CfnOutput(self, "EvalRoleArn", value=role.role_arn)


app = cdk.App()
EvalRoleStack(
    app,
    "AgentkeelM00EvalRole",
    env=cdk.Environment(region=REGION),  # account comes from the deployer's credentials
    description="agentkeel M00 eval role for GitHub Actions (OIDC). Security seat.",
    # No assets, and the account is not CDK-bootstrapped in us-west-2 (that is
    # M01). This synthesizer deploys with the caller's credentials and needs
    # no bootstrap stack.
    synthesizer=cdk.LegacyStackSynthesizer(),
)
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
