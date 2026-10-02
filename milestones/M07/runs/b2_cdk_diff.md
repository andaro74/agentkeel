# B2: what the two bootstrap deploys changed, and how it was read

The bootstrap stack was deployed by hand twice on 2026-10-02
(`runs/pr2_by_hand.md`, B2): from `7a9032d` at 22:49:50Z and from
`81508ab` at 23:16:52Z (`AgentkeelBootstrap` `LastUpdatedTime`, each read
after the deploy). This file keeps the `cdk diff --strict` output of each,
as far as it was kept, and one read that does not depend on a terminal:
the template CloudFormation stores against the tree.

## The outputs were not kept by the command given

The session's command was `npx aws-cdk@2 diff --strict | tee <file>`.
`cdk diff` writes the diff to stderr, so both files are empty. The
second diff was pasted from the terminal in full; of the first, the last
lines. That is the session's fault, not the human's; the command for B3
is below.

## Second deploy, from `81508ab` (pasted from the terminal)

The header said: "Could not create a change set, will base the diff on
template differences". So this is a template diff, not a change set.

```
Stack AgentkeelBootstrap
IAM Statement Changes
┌───┬─────────────────────────────────────────────────────────────────┬────────┬──────────────────────────────────────────────┬──────────────────────┬───────────┐
│   │ Resource                                                        │ Effect │ Action                                       │ Principal            │ Condition │
├───┼─────────────────────────────────────────────────────────────────┼────────┼──────────────────────────────────────────────┼──────────────────────┼───────────┤
│ + │ arn:aws:bedrock-agentcore:us-west-2:${AWS::AccountId}:runtime/* │ Allow  │ bedrock-agentcore:CreateAgentRuntimeEndpoint │ AWS:${ExecutionRole} │           │
│   │                                                                 │        │ bedrock-agentcore:TagResource                │                      │           │
│ - │ arn:aws:bedrock-agentcore:us-west-2:${AWS::AccountId}:runtime/* │ Allow  │ bedrock-agentcore:CreateAgentRuntimeEndpoint │ AWS:${ExecutionRole} │           │
└───┴─────────────────────────────────────────────────────────────────┴────────┴──────────────────────────────────────────────┴──────────────────────┴───────────┘

[~] AWS::IAM::Policy ExecutionRole/DefaultPolicy ExecutionRoleDefaultPolicyA5B92313
 ├─ [~] PolicyDocument
 │   └─ [~] .Statement:
 │       └─ @@ -473,7 +473,10 @@
 │          [ ]   "Sid": "CreateRuntimesInThePlatformSubnetsOnly"
 │          [ ] },
 │          [ ] {
 │          [-]   "Action": "bedrock-agentcore:CreateAgentRuntimeEndpoint",
 │          [+]   "Action": [
 │          [+]     "bedrock-agentcore:CreateAgentRuntimeEndpoint",
 │          [+]     "bedrock-agentcore:TagResource"
 │          [+]   ],
 │          [ ]   "Effect": "Allow",
 │          [ ]   "Resource": {
 │          [ ]     "Fn::Join": [
 │          @@ -487,7 +490,7 @@
 │          [ ]       ]
 │          [ ]     ]
 │          [ ]   },
 │          [-]   "Sid": "TheDefaultEndpointOfARuntimeBeingCreated"
 │          [+]   "Sid": "WhatCreateAgentRuntimeChecksOnTheRuntimeItHasNotNamedYet"
 │          [ ] },
```

That is the whole of the change to any resource property. The output
had ten more hunks, every one under `Metadata.cdk_nag.rules_to_suppress`
of a role policy, a security group or the boundary, and every one the
same change: a reason's `§` (as the tree writes it) against `?` (as the
stack stored it). CloudFormation reads nothing under `Metadata`. They are
not copied here; the read below covers them.

## First deploy, from `7a9032d` (the last lines, pasted)

```
Outputs
[+] Output ModelWatchRoleArn ModelWatchRoleArn: {"Value":{"Fn::GetAtt":["ModelWatchRole390BEA5D","Arn"]}}
[+] Output EnvelopeRowPutRoleArn EnvelopeRowPutRoleArn: {"Value":{"Fn::GetAtt":["EnvelopeRowPutRole5C9626D4","Arn"]}}

✨  Number of stacks with differences: 1
```

The rest of the first diff is not kept. The human read it against the
list `runs/pr2_by_hand.md` B2 gives (the three eval role reads, the two
roles, the envelopes table, refagent's key policy, the cfn-exec
statement, the two outputs) before deploying, and the pasted tail is
that list's last item. What the stack holds now is read below; the
second deploy changed one statement, so the rest of the difference
between the stored template and whatever the stack held before 22:49Z
is the first deploy's.

## The read that does not depend on a terminal

On 2026-10-02, after the second deploy, the stored template was read and
compared with a synth of the tree:

```sh
aws cloudformation get-template --stack-name AgentkeelBootstrap --region us-west-2 \
  --template-stage Original --query TemplateBody --output json > stored.json
CDK_OUTDIR=synth uv run python -m infra.bootstrap.app
```

and, in Python, both loaded, `§` replaced by `?` in the tree's, the
resource `CDKMetadata` and each resource's `aws:cdk:path` set aside (the
CLI adds those; a bare synth does not), `Parameters` and `Rules` set
aside (the CLI's bootstrap-version check): **the two are equal.** So the
stack holds the tree's template at `81508ab`, but for:

- `§` stored as `?` in the 20 cdk-nag reasons. Both deploys stored `?`.
  The diff showed `§` on the tree's side because the diff's synth ran
  under a pipe (`| tee`) and the deploy's synth ran on the console: the
  app's text reaches the CDK CLI through a Windows console code page
  that drops the sign. `Metadata` only; no property of any resource.
- CDK's path metadata.

`infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv` is
unaffected: `validate` compares it with a synth of the tree, and CI's
synth is on Linux.

## For B3, and any later deploy by hand

Keep the whole output, from stderr too, and synthesise under UTF-8:

```sh
PYTHONUTF8=1 npx aws-cdk@2 diff --strict 2>&1 | tee "$HOME/agentkeel-<stack>-diff.txt"
PYTHONUTF8=1 npx aws-cdk@2 deploy 2>&1 | tee "$HOME/agentkeel-<stack>-deploy.txt"
```

Whether `PYTHONUTF8=1` is what fixes the sign is not tested; the read
above, run again after the deploy, says whether it did.
