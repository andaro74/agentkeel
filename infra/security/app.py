"""The security account's stack, AgentkeelSecurity (Security seat; SPEC/05 §6, seed S6's reader).

Deployed by the human, by hand, in the security account (897698239547),
once, through the profile `agentkeel-security`; `OrganizationAccountAccessRole`
is deleted right after (milestones/M05/runs/security_account.md,
rulings/pr2-security.md). No workflow and no role in the agent account
deploys it.

    cd infra/security && npx aws-cdk@2 diff --profile agentkeel-security

What it makes, each named in SPEC/05 §6 before this file:

- **the audit bucket**: versioned, Object Lock COMPLIANCE for one day
  (R5 as amended at M05 PR 1: two keys, `rulings/pr1.md` and
  `pr1-security.md`), TLS only, public access blocked, S3-managed
  encryption, retained. Its policy:
  - CloudTrail puts under `AWSLogs/<account>/` for the two trails that
    deliver here (the agent account's, `infra/audit/`, and this account's),
    and flow-log delivery under `AWSLogs/<agent account>/` for the agent
    account's flow logs, each with the confused-deputy conditions AWS
    documents;
  - refagent's role puts under `agents/refagent/`, named by role ARN in
    `aws:PrincipalArn` (a principal named directly must exist when the
    policy is put). The stand-in's Allow under `agents/refagent/standin/`
    was removed at M06 PR 2 (`milestones/M06/open.md` row 2): the stand-in
    was deleted on 2026-09-30, and a role recreated with its name would have
    had the grant back. The two Denies that name it stay;
  - from M06 PR 2 (SPEC/06 section 6, item 8; `open.md` row 29), an agent
    from the template puts under `agents/<its agentkeel:agent tag>/` and
    nowhere else: one Allow and one Deny for every role under the agent
    path in the agent account, by the tag CloudFormation sets from the
    manifest's name on `main`. refagent's own grant stays by exact ARN;
  - an explicit Deny on either of them putting anywhere outside
    `agents/refagent/` (**seed S2's control**), and on the stand-in putting
    under `agents/refagent/events/`, where refagent's refusal events go;
  - the agent account granted, on `test/` only, a put and the two object
    actions seed S6 attempts (`s3:DeleteObjectVersion`,
    `s3:PutObjectRetention`), so that **the lock** is what refuses them;
  - an explicit Deny on `s3:PutBucketObjectLockConfiguration` (the IAM
    action for `PutObjectLockConfiguration`) to every principal outside
    this account. A bucket policy is only ever put by the bucket's own
    account (S3's rule), which is S6's fourth action's control;
- **this account's trail**: management events and the audit bucket's own
  object events under `agents/`, `test/` and `envelopes/`, delivered here.
  The bucket's owner receives the full record of a cross-account request,
  including one refused for the caller alone, which the caller's own trail
  may redact. The trail's own delivery prefix (`AWSLogs/`) is not among
  the prefixes it logs, so its writes are not events that make more writes
  (finding 17). Every region, with IAM's global events, so a change to a
  role in this account, the deletion of `OrganizationAccountAccessRole`
  included, will be recorded here once it is made;
- **GitHub's OIDC provider** in this account, and two roles CI assumes by
  it: `agentkeel-audit-read` (the observer; `evals.yml` on a pull request
  or `main`), which reads `AWSLogs/`, `agents/` and `test/` and nothing
  else, and `agentkeel-envelope-put` (`evals.yml` on `main` only), which
  puts under `envelopes/` and nothing else. The eval role in the agent
  account is denied `sts:AssumeRole`, so neither is reached through it;
- **the boundary** every role here carries, applied stack-wide.

From M07 PR 2 (SPEC/07 section 6; `milestones/M07/rulings/pr2-security.md`
items 9 and 11, ruled 2026-10-02), two more prefixes, each written once:

- **`bundles/`**: every deploy of an agent from the template puts its signed
  archive under `bundles/<name>/<commit>.tar`, with its signature beside it,
  as `agentkeel-answer-put` (deploy.yml on `main`), because the Actions
  artifact expires after 30 days and a retired agent's bundle must still be
  there. One statement in the bucket's policy refuses a put there without
  `If-None-Match`, as under `envelopes/`.
- **`observations/`**: what `observe.yml` read from GitHub as the platform's
  observer App, put as `agentkeel-observation-put`, a role that trusts that
  workflow on `refs/heads/main` and nothing else and may put there and
  nowhere else. The same put-once statement.

The read role lists and reads `observations/`, and lists `bundles/` (it does
not read a bundle's bytes: the observer asks only whether one is there). The
trail logs both prefixes' object events. A retirement's own record goes
under `envelopes/agents/<name>/retired.json`, which the answer-put role may
already write. No retention changes: the lock is still one day.

What it does not do: stop this account's own admin or root, who own the
bucket (the lock stops them on an object's day, not on the policy); stop
the organization's management account, which is the agent account, from
reaching this one through Organizations (centralized root access, removing
the account, an SCP; `milestones/M05/runs/security_account.md`); hold
anything seven years (M08); read the lock's retention in a gate (SPEC/05
§8).
"""

from __future__ import annotations

import os
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_cloudtrail as cloudtrail
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

REGION = "us-west-2"
SECURITY_ACCOUNT = "897698239547"  # milestones/M05/runs/security_account.md
AGENT_ACCOUNT = "581208540944"
AUDIT_BUCKET = f"agentkeel-audit-{SECURITY_ACCOUNT}"
LOCK_DAYS = 1  # R5 as amended at M05 PR 1: one day through M05, two keys; seven years is M08's
BOUNDARY_NAME = "agentkeel-security-boundary"
READ_ROLE = "agentkeel-audit-read"
PUT_ROLE = "agentkeel-envelope-put"
# M06 PR 2 (R7; security-reviewer F7): deploy.yml's own put role, under envelopes/agents/ and nothing else, so
# the deploy, which handles an agent repository's data, can never write evals.yml's envelope keys first.
ANSWER_PUT_ROLE = "agentkeel-answer-put"
# M07 PR 2 (rulings/pr2-security.md item 9): observe.yml's own put role, under observations/ and nothing else.
OBSERVATION_PUT_ROLE = "agentkeel-observation-put"
AGENT_TRAIL = f"arn:aws:cloudtrail:{REGION}:{AGENT_ACCOUNT}:trail/agentkeel-audit"  # infra/audit/
OWN_TRAIL_NAME = "agentkeel-audit-bucket"
OWN_TRAIL = f"arn:aws:cloudtrail:{REGION}:{SECURITY_ACCOUNT}:trail/{OWN_TRAIL_NAME}"
# The agent roles, by their whole ARN (security-reviewer and platform-architect on M05 PR 2: a pattern
# under `Principal: *` may read as public to S3, and would admit any role an admin names to match).
# refagent's name is the one CloudFormation gave it (the refagent stack's AgentRoleArn output, read
# 2026-09-28). A redeploy that replaces the role changes it: its puts are then refused and read as
# unrecorded, closed and not open, until this stack is redeployed with the new name.
AGENT_ROLES = f"arn:aws:iam::{AGENT_ACCOUNT}:role/agentkeel/agents/"
REFAGENT_ROLE = f"{AGENT_ROLES}agentkeel-refagent-RefagentRole5888DB41-i9IqTXU6NVSL"
STANDIN_ROLE = f"{AGENT_ROLES}agentkeel-refagent-standin"  # infra/audit/
# Repeated from infra/bootstrap/app.py, not imported: the two stacks are deployed by hand, in two accounts.
REPO = "andaro74/agentkeel"
SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"
GITHUB = "token.actions.githubusercontent.com"
EVAL_WORKFLOWS = [f"{REPO}/.github/workflows/evals.yml@refs/pull/*/merge",
                  f"{REPO}/.github/workflows/evals.yml@refs/heads/main"]
MAIN_EVALS = f"{REPO}/.github/workflows/evals.yml@refs/heads/main"
# M06 PR 2 (SPEC/06 section 6, R7): deploy.yml on main puts an agent from the template's answer record.
MAIN_DEPLOY = f"{REPO}/.github/workflows/deploy.yml@refs/heads/main"
# M07 PR 2 (SPEC/07 section 6): observe.yml on main stores what it read as the platform's observer App.
MAIN_OBSERVE = f"{REPO}/.github/workflows/observe.yml@refs/heads/main"
OBSERVER_ENVIRONMENT = "platform-observer"  # observe.yml's job environment; infra/platform_grant.yaml names it too
# The tag an agent role carries (infra/construct/governed_agent.py, AGENT_TAG), as a policy variable.
OWN_PREFIX = "agents/${aws:PrincipalTag/agentkeel:agent}/*"
# GitHub's two published intermediate thumbprints. IAM no longer checks them for GitHub, and
# CloudFormation still takes the list.
THUMBPRINTS = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c58a3a8518e8759bf075b76b750d4f2df264fcd"]
# What the observer reads (scripts/observe_containment.py), and nothing else.
# envelopes/agents/ from M06 PR 2 (item 4's records); observations/ from M07 PR 2 (the App-viewpoint observation).
READ_PREFIXES = ["AWSLogs/", "agents/", "test/", "envelopes/agents/", "observations/"]
# Listed, not read (M07 PR 2): whether a retired agent's signed bundle is there. Its bytes are not the observer's.
LIST_ONLY_PREFIXES = ["bundles/"]
# The object events this account's trail logs: the attempts and the evidence, not the delivery.
LOGGED_PREFIXES = ["agents/", "test/", "envelopes/", "bundles/", "observations/"]
# Written once (M07 PR 2): a put without If-None-Match is refused, as under envelopes/.
PUT_ONCE = {"bundles/": "ABundleIsWrittenOnce", "observations/": "AnObservationIsWrittenOnce"}
# Seed S6's two object actions, granted on test/ so that the lock is what refuses them.
S6_OBJECT_ACTIONS = ["s3:DeleteObjectVersion", "s3:PutObjectRetention"]


class SecurityStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        boundary = self._boundary()
        iam.PermissionsBoundary.of(self).apply(boundary)

        bucket = self._bucket()
        trail = self._trail(bucket)
        provider = iam.CfnOIDCProvider(
            self, "GitHubOidc", url=f"https://{GITHUB}", client_id_list=["sts.amazonaws.com"],
            thumbprint_list=THUMBPRINTS,
        )  # fmt: skip
        read_role = self._read_role(provider)
        put_role = self._put_role(provider)
        answer_role = self._answer_put_role(provider)
        observation_role = self._observation_put_role(provider)

        cdk.CfnOutput(self, "AuditBucket", value=bucket.bucket_name)
        cdk.CfnOutput(self, "AuditReadRoleArn", value=read_role.role_arn)
        cdk.CfnOutput(self, "EnvelopePutRoleArn", value=put_role.role_arn)
        cdk.CfnOutput(self, "AnswerPutRoleArn", value=answer_role.role_arn)
        cdk.CfnOutput(self, "ObservationPutRoleArn", value=observation_role.role_arn)
        cdk.CfnOutput(self, "TrailArn", value=trail.attr_arn)

    # --- the boundary ------------------------------------------------------

    def _boundary(self) -> iam.ManagedPolicy:
        """The ceiling on every role in this account's stack: read and put on the audit bucket, never more."""
        bucket_arn = f"arn:aws:s3:::{AUDIT_BUCKET}"
        return iam.ManagedPolicy(
            self, "Boundary", managed_policy_name=BOUNDARY_NAME,
            description="agentkeel: the ceiling on every role in the security account's stack (SPEC/05 section 6).",
            document=iam.PolicyDocument(statements=[
                iam.PolicyStatement(
                    sid="ReadTheAuditBucketAndPutNewObjects",
                    actions=["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention", "s3:ListBucket",
                             "s3:ListBucketVersions", "s3:PutObject"],
                    resources=[bucket_arn, f"{bucket_arn}/*"],
                ),
                iam.PolicyStatement(
                    sid="NeverEraseNeverUnlockNeverEscalate", effect=iam.Effect.DENY,
                    actions=["s3:DeleteObject", "s3:DeleteObjectVersion", "s3:PutObjectRetention",
                             "s3:PutObjectLegalHold", "s3:BypassGovernanceRetention", "s3:PutBucketPolicy",
                             "s3:DeleteBucketPolicy", "s3:PutBucketObjectLockConfiguration", "s3:PutBucketVersioning",
                             "s3:PutLifecycleConfiguration", "cloudtrail:StopLogging", "cloudtrail:DeleteTrail",
                             "cloudtrail:UpdateTrail", "cloudtrail:PutEventSelectors", "iam:*", "sts:AssumeRole"],
                    resources=["*"],
                ),
            ]),
        )  # fmt: skip

    # --- the audit bucket --------------------------------------------------

    def _bucket(self) -> s3.Bucket:
        bucket = s3.Bucket(
            self, "Audit", bucket_name=AUDIT_BUCKET, versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL, enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED, object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            object_lock_enabled=True,
            object_lock_default_retention=s3.ObjectLockRetention.compliance(cdk.Duration.days(LOCK_DAYS)),
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )  # fmt: skip
        objects = bucket.arn_for_objects
        trails = [AGENT_TRAIL, OWN_TRAIL]
        cloudtrail_ = iam.ServicePrincipal("cloudtrail.amazonaws.com")
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="CloudTrailChecksTheAcl", principals=[cloudtrail_], actions=["s3:GetBucketAcl"],
            resources=[bucket.bucket_arn], conditions={"StringEquals": {"aws:SourceArn": trails}},
        ))  # fmt: skip
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="TheTwoTrailsDeliverUnderTheirAccounts", principals=[cloudtrail_], actions=["s3:PutObject"],
            resources=[objects(f"AWSLogs/{AGENT_ACCOUNT}/*"), objects(f"AWSLogs/{SECURITY_ACCOUNT}/*")],
            conditions={"StringEquals": {"aws:SourceArn": trails, "s3:x-amz-acl": "bucket-owner-full-control"}},
        ))  # fmt: skip
        delivery = iam.ServicePrincipal("delivery.logs.amazonaws.com")
        from_the_agent_account = {"StringEquals": {"aws:SourceAccount": AGENT_ACCOUNT},
                                  "ArnLike": {"aws:SourceArn": f"arn:aws:logs:{REGION}:{AGENT_ACCOUNT}:*"}}
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="FlowLogsCheckTheAcl", principals=[delivery], actions=["s3:GetBucketAcl"],
            resources=[bucket.bucket_arn], conditions=from_the_agent_account,
        ))  # fmt: skip
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="FlowLogsDeliverUnderTheAgentAccount", principals=[delivery], actions=["s3:PutObject"],
            resources=[objects(f"AWSLogs/{AGENT_ACCOUNT}/*")],
            conditions={**from_the_agent_account, "StringEquals": {
                "aws:SourceAccount": AGENT_ACCOUNT, "s3:x-amz-acl": "bucket-owner-full-control"}},
        ))  # fmt: skip
        # Each agent role, and refagent's stand-in, on refagent's prefix only (finding 5, Security).
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="RefagentPutsUnderItsOwnPrefix", principals=[iam.AnyPrincipal()], actions=["s3:PutObject"],
            resources=[objects("agents/refagent/*")], conditions={"ArnEquals": {"aws:PrincipalArn": REFAGENT_ROLE}},
        ))  # fmt: skip
        # M06 PR 2 (SPEC/06 section 6, item 8): an agent from the template, under its own prefix, by its tag.
        # The account is named as a fixed value, so S3 does not read the policy as public; the path and the
        # tag are what the platform sets, from main, through the execution role (no agent role may tag).
        # refagent is left to its exact-ARN grant above.
        template_agents = {"StringEquals": {"aws:PrincipalAccount": AGENT_ACCOUNT},
                           "ArnLike": {"aws:PrincipalArn": f"{AGENT_ROLES}*"}}  # fmt: skip
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="AnAgentFromTheTemplatePutsUnderItsOwnPrefix", principals=[iam.AnyPrincipal()],
            actions=["s3:PutObject"], resources=[objects(OWN_PREFIX)],
            conditions={**template_agents, "StringNotEquals": {"aws:PrincipalTag/agentkeel:agent": "refagent"},
                        "Null": {"aws:PrincipalTag/agentkeel:agent": "false"}},
        ))  # fmt: skip
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="NoAgentFromTheTemplatePutsOutsideItsOwnPrefix", effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()], actions=["s3:PutObject"], not_resources=[objects(OWN_PREFIX)],
            # Tagged roles only: an untagged one has no Allow here either, and refagent's role carries no tag
            # until its next deploy, when its own exact-ARN Deny above still holds it.
            conditions={**template_agents, "Null": {"aws:PrincipalTag/agentkeel:agent": "false"}},
        ))  # fmt: skip
        # Seed S2's control: the refusal of another agent's prefix, explicit and named.
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="NoAgentPutsOutsideItsOwnPrefix", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=["s3:PutObject"], not_resources=[objects("agents/refagent/*")],
            conditions={"ArnEquals": {"aws:PrincipalArn": [REFAGENT_ROLE, STANDIN_ROLE]}},
        ))  # fmt: skip
        # The observer accepts S4's refusal event only from refagent's role; the stand-in cannot write one.
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="TheStandinNeverWritesARefusalEvent", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=["s3:PutObject"], resources=[objects("agents/refagent/events/*")],
            conditions={"ArnEquals": {"aws:PrincipalArn": STANDIN_ROLE}},
        ))  # fmt: skip
        # Seed S6: granted, on test/ only, so that Object Lock is what must refuse the two object actions.
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="SeedS6TheLockMustRefuseTheseOnTest", principals=[iam.AccountPrincipal(AGENT_ACCOUNT)],
            actions=["s3:PutObject", "s3:GetObjectRetention", *S6_OBJECT_ACTIONS], resources=[objects("test/*")],
        ))  # fmt: skip
        # An envelope is written once: a put under envelopes/ without If-None-Match is refused, so no
        # workflow on main can lay a second version over the first (security-reviewer on M05 PR 2).
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="AnEnvelopeIsWrittenOnce", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=["s3:PutObject"], resources=[objects("envelopes/*")],
            conditions={"Null": {"s3:if-none-match": "true"}},
        ))  # fmt: skip
        # M07 PR 2 (rulings/pr2-security.md items 9 and 11): a signed bundle and a stored observation are
        # each written once too. One statement per prefix, so each can be read for what it holds.
        for prefix, sid in PUT_ONCE.items():
            bucket.add_to_resource_policy(iam.PolicyStatement(
                sid=sid, effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
                actions=["s3:PutObject"], resources=[objects(f"{prefix}*")],
                conditions={"Null": {"s3:if-none-match": "true"}},
            ))  # fmt: skip
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="NobodyOutsideThisAccountTurnsTheLockOff", effect=iam.Effect.DENY, principals=[iam.AnyPrincipal()],
            actions=["s3:PutBucketObjectLockConfiguration"], resources=[bucket.bucket_arn],
            conditions={"StringNotEquals": {"aws:PrincipalAccount": SECURITY_ACCOUNT}},
        ))  # fmt: skip
        return bucket

    # --- this account's trail ---------------------------------------------

    def _trail(self, bucket: s3.Bucket) -> cloudtrail.CfnTrail:
        selector = cloudtrail.CfnTrail.AdvancedFieldSelectorProperty
        trail = cloudtrail.CfnTrail(
            self, "Trail", trail_name=OWN_TRAIL_NAME, s3_bucket_name=bucket.bucket_name, is_logging=True,
            # Every region and IAM's global events (security-reviewer and platform-architect on M05 PR 2):
            # the deletion of OrganizationAccountAccessRole, and any later change to a role here, is recorded.
            is_multi_region_trail=True, include_global_service_events=True, enable_log_file_validation=True,
            advanced_event_selectors=[
                cloudtrail.CfnTrail.AdvancedEventSelectorProperty(
                    name="Management events", field_selectors=[selector(field="eventCategory", equal_to=["Management"])]),
                cloudtrail.CfnTrail.AdvancedEventSelectorProperty(
                    name="The audit bucket's attempts and evidence, not its delivery", field_selectors=[
                        selector(field="eventCategory", equal_to=["Data"]),
                        selector(field="resources.type", equal_to=["AWS::S3::Object"]),
                        selector(field="resources.ARN",
                                 starts_with=[f"arn:aws:s3:::{AUDIT_BUCKET}/{p}" for p in LOGGED_PREFIXES]),
                    ]),
            ],
        )  # fmt: skip
        trail.node.add_dependency(bucket.policy)
        return trail

    # --- the two roles CI assumes -----------------------------------------

    def _github(self, provider: iam.CfnOIDCProvider, subjects: list[str], workflows: list[str] | str,
                *, exact: bool) -> iam.FederatedPrincipal:  # fmt: skip
        """GitHub OIDC: `aud` and `sub` exact; the workflow exact for the put role, by pattern for the read role."""
        equals: dict[str, object] = {f"{GITHUB}:aud": "sts.amazonaws.com", f"{GITHUB}:sub": subjects}
        conditions: dict[str, object] = {"StringEquals": equals}
        if exact:
            equals[f"{GITHUB}:job_workflow_ref"] = workflows
        else:
            conditions["StringLike"] = {f"{GITHUB}:job_workflow_ref": workflows}
        return iam.FederatedPrincipal(provider.attr_arn, conditions=conditions,
                                      assume_role_action="sts:AssumeRoleWithWebIdentity")

    def _read_role(self, provider: iam.CfnOIDCProvider) -> iam.Role:
        """The observer's: evals.yml on a pull request or on main. Reads what it needs, never writes."""
        role = iam.Role(
            self, "ReadRole", role_name=READ_ROLE, max_session_duration=cdk.Duration.hours(1),
            assumed_by=self._github(provider, [f"{SUBJECT}:pull_request", f"{SUBJECT}:ref:refs/heads/main"],
                                    EVAL_WORKFLOWS, exact=False),
            description="agentkeel: scripts/observe_containment.py reads the audit bucket as this (SPEC/05 section 4).",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ListTheObserversPrefixes", actions=["s3:ListBucket", "s3:ListBucketVersions"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}"],
            conditions={"StringLike": {"s3:prefix": [f"{p}*" for p in READ_PREFIXES + LIST_ONLY_PREFIXES]}},
        ))  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheObserversPrefixes", actions=["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/{p}*" for p in READ_PREFIXES],
        ))  # fmt: skip
        return role

    def _put_role(self, provider: iam.CfnOIDCProvider) -> iam.Role:
        """evals.yml on main, and only there: the envelope put under envelopes/ (SPEC/05 section 6, finding 2)."""
        role = iam.Role(
            self, "PutRole", role_name=PUT_ROLE, max_session_duration=cdk.Duration.hours(1),
            assumed_by=self._github(provider, [f"{SUBJECT}:ref:refs/heads/main"], MAIN_EVALS, exact=True),
            description="agentkeel: evals.yml on main puts each CI-written envelope under envelopes/ as this.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="PutEnvelopesOnly", actions=["s3:PutObject"], resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/envelopes/*"]))
        return role

    def _answer_put_role(self, provider: iam.CfnOIDCProvider) -> iam.Role:
        """deploy.yml on main, and only there: an agent from the template's answer record (SPEC/06 R7)."""
        role = iam.Role(
            self, "AnswerPutRole", role_name=ANSWER_PUT_ROLE, max_session_duration=cdk.Duration.hours(1),
            assumed_by=self._github(provider, [f"{SUBJECT}:ref:refs/heads/main"], MAIN_DEPLOY, exact=True),
            description="agentkeel: deploy.yml on main puts an agent's answer record under envelopes/agents/ as this.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="PutAnswerRecordsOnly", actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/envelopes/agents/*"]))
        # M07 PR 2 (item 11): the signed archive of what it just deployed, under bundles/<name>/, once.
        role.add_to_policy(iam.PolicyStatement(
            sid="PutSignedBundlesOnly", actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/bundles/*"]))
        return role

    def _observation_put_role(self, provider: iam.CfnOIDCProvider) -> iam.Role:
        """observe.yml on main, and only there: what it read as the observer App (SPEC/07 section 6, item 9).

        M07 PR 4 (runs 37094837939 to 37119509159, 2026-10-03): the job that puts is the job that holds the
        App's key, so it runs in the environment `platform-observer`, and GitHub's token for a job in an
        environment carries `sub` = `...:environment:<name>`, not `...:ref:refs/heads/main`. The role trusted the
        ref form, and every keyed run was refused at AssumeRoleWithWebIdentity. The subject is the environment's
        now. In IAM, main-only rests on `job_workflow_ref` alone, exact, `observe.yml@refs/heads/main`. The
        other half is no longer a token claim: it is the environment's branch policy (`main` alone, no admin
        bypass), a GitHub setting a repository admin can change, which the grant's reader reads back before
        this step. Not wider: the same job, named as GitHub names it. One run has assumed the role
        (37123531195); none from a branch or from another workflow has been refused at it, so "main only"
        here is read from the template and has not fired (security-reviewer N2, platform-architect F10 on
        M07 PR 4)."""
        role = iam.Role(
            self, "ObservationPutRole", role_name=OBSERVATION_PUT_ROLE, max_session_duration=cdk.Duration.hours(1),
            assumed_by=self._github(provider, [f"{SUBJECT}:environment:{OBSERVER_ENVIRONMENT}"], MAIN_OBSERVE,
                                    exact=True),
            description="agentkeel: observe.yml on main puts its App-viewpoint observation under observations/ as this.",
        )  # fmt: skip
        role.add_to_policy(iam.PolicyStatement(
            sid="PutObservationsOnly", actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{AUDIT_BUCKET}/observations/*"]))
        return role


app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = SecurityStack(
    app, "AgentkeelSecurity",
    env=cdk.Environment(account=SECURITY_ACCOUNT, region=REGION),
    description="agentkeel M05: the security account's audit bucket, trail and read and put roles. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # no CDK bootstrap in this account either
)
SUPPRESSIONS = {
    "Audit/Resource": (
        "AwsSolutions-S1",
        "SPEC/05 §6: the audit bucket is the log destination itself. Its object events under agents/, test/ "
        "and envelopes/ are this account's trail's data events, delivered to this bucket; server access logs "
        "would need a second bucket that nothing reads. The bucket is versioned and locked (COMPLIANCE, one day).",
    ),
    "Boundary/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6: 'so does every role infra/security/ makes'. Its Allow is the audit bucket and its "
        "objects (arn/*), because the keys are written by CloudTrail, flow-log delivery and the agents; the "
        "wildcard on * is in the Deny, which must cover every resource.",
    ),
    "ReadRole/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6: 'the read-only role reads the prefixes the observer needs and not *'. AWSLogs/*, agents/*, "
        "test/* and, from M06 PR 2, envelopes/agents/* (an agent from the template's answer records, SPEC/06 R7) "
        "are those prefixes; the keys under them are written by AWS, by the agents and by deploy.yml at run time. "
        "M07 PR 2 (SPEC/07 §6): observations/*, whose keys are observe.yml's run ids.",
    ),
    "ObservationPutRole/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6's 'envelopes to the audit bucket from main', as SPEC/07 §6 extends it to the observer's "
        "observation: observations/* because each key is an observe.yml run id, which exists only when that run "
        "writes it. Put only; the bucket refuses a put there without If-None-Match.",
    ),
    "AnswerPutRole/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6's envelopes to the audit bucket from main, for an agent from the template's answer record "
        "(SPEC/06 R7): envelopes/agents/* because each key is an agent repository's commit, which exists only "
        "when deploy.yml writes it. M07 PR 2 (SPEC/07 §6): bundles/* likewise, the signed archive of that commit.",
    ),
    "PutRole/DefaultPolicy/Resource": (
        "AwsSolutions-IAM5",
        "SPEC/05 §6: envelopes to the audit bucket from main (evals.yml, and from M06 PR 2 deploy.yml's answer "
        "records, SPEC/06 R7). envelopes/* because each key is a commit, which exists only when CI writes it.",
    ),
}
# Each IAM5 suppression names the findings it covers (open.md row 4; security-reviewer F10 on M06 PR 2).
_OBJECTS = f"Resource::arn:aws:s3:::{AUDIT_BUCKET}/"
APPLIES_TO = {
    "Boundary/Resource": [f"{_OBJECTS}*"],
    "ReadRole/DefaultPolicy/Resource": [f"{_OBJECTS}{p}*" for p in READ_PREFIXES],
    "PutRole/DefaultPolicy/Resource": [f"{_OBJECTS}envelopes/*"],
    "AnswerPutRole/DefaultPolicy/Resource": [f"{_OBJECTS}envelopes/agents/*", f"{_OBJECTS}bundles/*"],
    "ObservationPutRole/DefaultPolicy/Resource": [f"{_OBJECTS}observations/*"],
}
for path, (rule, reason) in SUPPRESSIONS.items():
    applies = {"appliesTo": APPLIES_TO[path]} if path in APPLIES_TO else {}
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelSecurity/{path}", [{"id": rule, "reason": reason, **applies}])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
