# infra/ingest

refagent's corpus ingest stack, `AgentkeelIngest` (Security). SPEC/03 §6
names each part; `app.py` builds them; `promoter.py` is the Lambda, inlined.

What it is for, in one line: a document reaches the production bucket, the
only one refagent will read from (M04), when and only when
`data/corpus/admitted.yaml` names its sha256. Seed S5, the unsigned
Amendment No. 2, is named by no ruling, so it should stay in quarantine.
At stop B (M03 PR 2, 2026-09-25/26) the six admitted documents were
promoted and S5 was recorded not promoted (`milestones/M03/runs/f3_5_amendment.yaml`);
PR 2's CI run is what reads it as evidence. The stack's own refusals (a
put by anyone but the promoter, a delete, a re-lock) have not been
attempted (SPEC/03 §8).

It is deployed by the human with admin and by nothing else, **from a clean
checkout**: the admitted list is read from the tree at synth. Each record the
promoter writes carries the fingerprint of the list it was built with, and
the stack's `AdmittedFingerprint` output says the same, so the list the
deployed promoter holds can be compared with `admitted.yaml` at a commit.

## Stop B (M03 PR 2)

As the admin, in the agent account, us-west-2, after stop A (the stack's
policies name `agentkeel-evals` and its roles the deploy boundary, both the
bootstrap stack's):

```sh
aws sts get-caller-identity
git status --short                              # empty: the list is read from this tree
cd infra/ingest && npx aws-cdk@2 diff           # read it before anything touches AWS
npx aws-cdk@2 deploy
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelIngest \
  --query "Stacks[0].Outputs" --output table
```

`cdk diff` should show only new resources: two buckets and their policies,
the record table, the promoter's role, policy, log group, function and
permission, four outputs. An asset parameter, a custom resource or a second
function is a stop.

Then the six admitted documents, which the promoter should promote, and seed
S5, which it should not:

```sh
cd ../..
for f in data/corpus/*.md; do aws s3 cp "$f" "s3://agentkeel-refagent-quarantine-<account>/$(basename "$f")"; done
aws s3api put-object --bucket agentkeel-refagent-quarantine-<account> --key amendment-2.md \
  --body tests/fixtures/m03/s5-unsigned-amendment.md      # prints the VersionId
aws dynamodb get-item --table-name agentkeel-refagent-ingest-record \
  --key '{"key":{"S":"amendment-2.md"},"version_id":{"S":"<VersionId>"}}'
```

Fill `milestones/M03/runs/f3_5_amendment.yaml`'s `observed` from what AWS
returned. PR 2's CI run looks it up itself (`scripts/observe_ingest.py`);
what the human writes feeds no check by itself.

## The lock, and taking the stack down

Production has Object Lock in COMPLIANCE mode for 1 day (the human as
Security, 2026-09-25, a demo setting): once promoted, an object version
cannot be changed or deleted by anyone, root included, for a day. Its policy
also denies every principal a delete, a replication into it, a legal hold, a
new retention date and a new lock configuration. None of that has been
attempted yet (SPEC/03 §8), and the admin can still remove the policy.

A stack delete removes only the promoter's role and function: both buckets,
the record table (deletion protection on) and the log group are retained,
with fixed names, so a redeploy fails on them until they are gone. To take
it all down, as the admin, at least a day after the last promotion:

1. `aws s3api delete-bucket-policy --bucket agentkeel-refagent-corpus-<account>`
   (the policy denies every delete, the admin's included);
2. delete every object version and delete marker in both buckets, then the
   buckets (a version still locked is refused: wait for its day);
3. turn off the table's deletion protection, then delete the table;
4. delete the log group `/agentkeel/refagent/ingest/promoter`;
5. `npx aws-cdk@2 destroy` in `infra/ingest`.

Each re-upload of an admitted document makes a new version, locked for
another day.
