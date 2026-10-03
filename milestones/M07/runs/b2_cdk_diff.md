# B2 and B3: what the three deploys by hand changed, and how each was read

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

`PYTHONUTF8=1` does not fix the sign: B3 below was deployed with it and
stored `?` too. Where the sign is lost between the app and the CLI on
this machine is not found, and is not looked for further: `Metadata`
only.

## B3, Grafana's stack, from `8f4bc7a` (2026-10-03T00:48:04Z)

`infra/grafana` is identical on `main` (`cba3aac`) and `m07-pr4`. The
first `deploy` with `2>&1 | tee` applied nothing: "Stack includes
security-sensitive updates, but terminal (TTY) is not attached so we are
unable to get a confirmation from the user". It printed the IAM changes,
which were read, and the deploy was run again with
`--require-approval never`. Its output:

```
Stack AgentkeelGrafana
IAM Statement Changes
┌───┬───────────────────────────────────────────────────────────────────────┬────────┬────────────────────────┬──────────────────────┬───────────┐
│   │ Resource                                                              │ Effect │ Action                 │ Principal            │ Condition │
├───┼───────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┼──────────────────────┼───────────┤
│ + │ arn:aws:dynamodb:us-west-2:581208540944:table/agentkeel-envelopes     │ Allow  │ dynamodb:DescribeTable │ AWS:${ConnectorRole} │           │
│   │                                                                       │        │ dynamodb:PartiQLSelect │                      │           │
│   │                                                                       │        │ dynamodb:Query         │                      │           │
│   │                                                                       │        │ dynamodb:Scan          │                      │           │
├───┼───────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┼──────────────────────┼───────────┤
│ + │ arn:aws:glue:us-west-2:581208540944:table/default/agentkeel-envelopes │ Allow  │ glue:GetTable          │ AWS:${ConnectorRole} │           │
└───┴───────────────────────────────────────────────────────────────────────┴────────┴──────────────────────────────────────────────┴──────────────────────┴───────────┘

AgentkeelGrafana | 0/5 | 5:48:06 PM | CREATE_IN_PROGRESS      | AWS::Glue::Table             | EnvelopesSchema
AgentkeelGrafana | 0/5 | 5:48:07 PM | UPDATE_IN_PROGRESS      | AWS::IAM::Policy             | ConnectorRole/DefaultPolicy (ConnectorRoleDefaultPolicyA5ABCAB4)
AgentkeelGrafana | 1/5 | 5:48:07 PM | CREATE_COMPLETE         | AWS::Glue::Table             | EnvelopesSchema
AgentkeelGrafana | 2/5 | 5:48:25 PM | UPDATE_COMPLETE         | AWS::IAM::Policy             | ConnectorRole/DefaultPolicy (ConnectorRoleDefaultPolicyA5ABCAB4)
AgentkeelGrafana | 4/5 | 5:48:28 PM | UPDATE_COMPLETE         | AWS::CloudFormation::Stack   | AgentkeelGrafana
✅  AgentkeelGrafana
```

Times are the machine's (UTC-7). The read: the stored template (YAML,
as the CLI uploads this stack) equals a synth of the tree at `8f4bc7a`,
with the 3 cdk-nag signs as `?` and CDK's path metadata set aside, as
for B2. Panel 2 is imported by the human from `infra/grafana/panel2.json`;
its table holds no row until the next push to `main`.
