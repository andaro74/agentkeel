# infra/audit

Delivery from the agent account to the security account, `AgentkeelAudit`
(Security). SPEC/05 §6 names each part; `app.py` builds them. Deployed by
the human with admin in the agent account (581208540944), **after**
`infra/security/` is deployed in the security account.

- the trail `agentkeel-audit`: management events, the audit bucket's object
  events under `agents/`, `test/` and `envelopes/`, the production corpus
  bucket's object events, and AgentCore runtime invocations, to the audit
  bucket;
- the platform VPC's flow log to the audit bucket, one-minute aggregation;
- refagent's stand-in for seeds S2 and S3 (until both are read);
- the quarantine policy for seed S7, attached to nothing.

## Deploy, at M05 PR 2

```sh
aws sts get-caller-identity                     # Account 581208540944, as the admin
cd infra/audit && npx aws-cdk@2 diff
npx aws-cdk@2 deploy
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelAudit \
  --query "Stacks[0].Outputs" --output table
```

`cdk diff` should show only new resources: one trail, one flow log, one
managed policy (the quarantine), one role and its policy, and one SSM
parameter read (the VPC id). Anything touching another stack is a stop.

## The quarantine (seed S7, after M05 PR 2's merge deploy)

The one command that quarantines refagent, and the one that lifts it. The
role name is the refagent stack's `AgentRoleArn` output, without its path:

```sh
ROLE=$(aws cloudformation describe-stacks --region us-west-2 --stack-name agentkeel-refagent \
  --query "Stacks[0].Outputs[?OutputKey=='AgentRoleArn'].OutputValue" --output text | sed 's#.*/##')
aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::581208540944:policy/agentkeel-quarantine
aws iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::581208540944:policy/agentkeel-quarantine
```

A redeploy of refagent's stack does not detach it: a policy attached by
hand is not the stack's. The observer reads the last attach or detach on
that role from the trail before it reads anything else (SPEC/05 §6).

## Removing the stand-in

Once seeds S2 and S3 are read, `STANDIN = False` in `app.py` (M05 PR 3), and
the human redeploys this stack: the role is deleted. `cdk diff` must show
only these, all removed, and nothing else:

- `[-] AWS::IAM::Role` Standin and `[-] AWS::IAM::Policy` StandinDefaultPolicy;
- in the IAM statement changes: the trust (`hector.acevedo` with
  `aws:MultiFactorAuthPresent`), the Deny `RefagentsExplicitDenies`, the
  Allows `SeedS2PutAnywhereInTheAuditBucket` and `SeedS3DeleteARuntimeLogStream`;
- `[-]` the output `StandinRoleArn`.

A change to the trail, the flow log, the quarantine or any other stack is a
stop. After the deploy, `aws iam get-role --role-name agentkeel-refagent-standin`
answers `NoSuchEntity`, recorded in `milestones/M05/runs/`.
