# infra/ingest

The corpus ingest stack, `AgentkeelIngest` (Security). SPEC/03 §6 names
each part; `app.py` builds them; `promoter.py` is the Lambda, inlined.

What it is for, in one line: a document reaches the production bucket, the
only one refagent will read from (M04), when and only when
`data/corpus/admitted.yaml` names its sha256. Seed S5, the unsigned
Amendment No. 2, is named by no ruling, so it stays in quarantine.

It is deployed by the human with admin and by nothing else. A change to
`admitted.yaml` reaches the promoter only through such a deploy.

## Stop B (M03 PR 2)

As the admin, in the agent account, us-west-2:

```sh
aws sts get-caller-identity
cd infra/ingest && npx aws-cdk@2 diff          # read it before anything touches AWS
npx aws-cdk@2 deploy
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelIngest \
  --query "Stacks[0].Outputs" --output table
```

Then the six admitted documents, which the promoter should promote, and seed
S5, which it should not:

```sh
cd ../..
for f in data/corpus/*.md; do aws s3 cp "$f" "s3://agentkeel-quarantine-<account>/$(basename "$f")"; done
aws s3api put-object --bucket agentkeel-quarantine-<account> --key amendment-2.md \
  --body tests/fixtures/m03/s5-unsigned-amendment.md      # prints the VersionId
```

Fill `milestones/M03/runs/f3_5_amendment.yaml`'s `observed` from what AWS
returned (the key, the version id, the time) and the record table's item for
that version (`aws dynamodb get-item --table-name agentkeel-ingest-record
--key '{"key":{"S":"amendment-2.md"},"version_id":{"S":"<VersionId>"}}'`).
PR 2's CI run looks it up itself (`scripts/observe_ingest.py`); what the
human writes feeds no check by itself.

## The lock

Production has Object Lock in COMPLIANCE mode for 1 day (the human as
Security, 2026-09-25, a demo setting). For a day after a document is
promoted, nobody, root included, can change or delete it, and the bucket
cannot be deleted while it holds a locked object. After that day the stack
can be torn down. Lowering the period, or GOVERNANCE mode, is a relaxation.
