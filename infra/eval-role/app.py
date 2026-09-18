"""The M00 eval role (Security seat; ruling on report 2.3, M00 PR 2).

One IAM role that GitHub Actions in andaro74/agentkeel assumes over OIDC to
run `make evals`. It may invoke the models the current milestone calls,
through their inference profiles, and nothing else. At M00 that is one: the
baseline. It has no S3, no IAM, no logs.

Finding S-1 (Security, M00 PR 2): the first version allowed all six pinned
models to any workflow on any PR branch. Each milestone's PR 1 now adds the
ARNs that milestone calls, and only `.github/workflows/evals.yml` may assume
the role.

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
# This repo issues GitHub's immutable OIDC subject (`use_immutable_subject`,
# read from `gh api repos/andaro74/agentkeel/actions/oidc/customization/sub`
# on 2026-09-18): the owner id and the repo id ride in the claim, so a renamed
# or re-created `andaro74/agentkeel` does not match. The classic form,
# `repo:andaro74/agentkeel:...`, is never issued here and is not trusted.
SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"
REGION = "us-west-2"
ROLE_NAME = "agentkeel-m00-evals"

# Only what the current milestone calls, without the `us.` profile prefix
# (Finding S-1). The ids are the Threshold Owner's, pinned in
# milestones/M00/README.md. Each milestone's PR 1 adds its own here, with a
# Security ruling: M01 adds refagent's, M04 the swap candidates'.
MODELS = [
    "amazon.nova-micro-v1:0",  # baseline (M00)
]
# Where the `us.` profile routes, from `aws bedrock get-inference-profile`
# in us-west-2 on 2026-09-18. A profile call is authorised on the profile and
# on the foundation model in whichever of these serves it.
PROFILE_REGIONS = ["us-east-1", "us-east-2", "us-west-2"]

# The one workflow the trust policy names (Finding S-1), at the two refs it
# runs from: a PR's merge ref, and main. The ref is spelled out so that a file
# called `evals.yml@x.yml`, or a reusable call to another branch's evals.yml,
# does not match; `*` stands only for the PR number. This is aimed at a second
# workflow file reusing the role. It does not stop a PR that edits evals.yml:
# on `pull_request` the workflow is the PR's own copy, and nothing gates that
# edit until M02. Not observed yet: see the README.
WORKFLOWS = [
    f"{REPO}/.github/workflows/evals.yml@refs/pull/*/merge",
    f"{REPO}/.github/workflows/evals.yml@refs/heads/main",
]

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
            # 3600 is IAM's floor. The ruling on S-1 asked for 900; IAM and CDK
            # refuse anything under one hour. evals.yml asks for 900 seconds,
            # but a step that mints its own token can ask for the full hour.
            max_session_duration=cdk.Duration.hours(1),
            assumed_by=iam.FederatedPrincipal(
                provider.open_id_connect_provider_arn,
                conditions={
                    # No wildcard: any branch on pull_request, main only on push.
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": [
                            f"{SUBJECT}:pull_request",
                            f"{SUBJECT}:ref:refs/heads/main",
                        ],
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:job_workflow_ref": WORKFLOWS,
                    },
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
