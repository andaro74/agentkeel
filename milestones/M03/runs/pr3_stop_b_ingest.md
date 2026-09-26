# Stop B, the ingest stack redeployed with guardrail version 5 (M03 PR 3)

Run by the human as admin, 2026-09-26, from a clean checkout of `70e7d53`
(`before.md` and `after.md` untracked in the tree, read by nothing that
synthesises), after `rule-owner` and `security-reviewer` read `47ee02d`.
Pasted by the human, transcribed by the session; the session's reading
first, then the outputs whole.

- **Why.** `infra/ingest/app.py` reads the manifest's guardrail pin at
  synth into the promoter's environment. After the pin moved from 4 to 5
  (`47ee02d`) the deployed promoter no longer matched the tree (Product,
  `rulings/pr3.md` C: redeploy rather than record the drift).
- **Expected before the diff.** The session synthesised the stack from
  `0ee873e` (PR 2's stop B) and from the branch and compared the
  templates: one difference, `Promoter` `GUARDRAIL_VERSION` `4 -> 5`. Of
  the stack's inputs, only `agents/refagent/manifest.yaml` changed since
  `0ee873e` (`src/verdict/__init__.py`, `pyproject.toml`, `uv.lock`,
  `data/corpus/` unchanged; `infra/ingest/README.md` is not synthesised).
- **The diff** (a read-only change set, nothing omitted): that one change,
  in place.
- **After.** The stack `UPDATE_COMPLETE`, one resource updated. The
  promoter's configuration: `1088aw3ujhyd`, `5`, admitted fingerprint
  `e12988c5…`, the same as the stack output and as seed S5's record. Version
  4 still `READY` with `rules sha256 9cbefa08…`, retained as designed: PR 2's
  envelope and S5's scan name it.
- **What it does not show.** That the promoter scans with version 5: it
  has not run since. The record keeps no guardrail version (a later
  promoter change, Security). Nothing mechanical compares the deployed
  promoter's pin with the manifest; the eval role has no
  `lambda:GetFunctionConfiguration` (M05).

```
$ git log -1 --format='%H'
70e7d53cad774b6bba827f631955324cf465f9a0
$ cd infra/ingest && npx aws-cdk@2 diff --strict AgentkeelIngest; cd ../..
Hold on while we create a read-only change set to get a diff with accurate replacement information (use --method=template to use a less accurate but faster template-only diff)

Stack AgentkeelIngest
Resources
[~] AWS::Lambda::Function Promoter Promoter771ABA6D
 └─ [~] Environment
     └─ [~] .Variables:
         └─ [~] .GUARDRAIL_VERSION:
             ├─ [-] 4
             └─ [+] 5



✨  Number of stacks with differences: 1

$ cd infra/ingest && npx aws-cdk@2 deploy AgentkeelIngest; cd ../..

✨  Synthesis time: 4.43s

AgentkeelIngest: creating CloudFormation changeset...
AgentkeelIngest: deploying... [1/1]
AgentkeelIngest | 0/3 | 1:12:29 PM | UPDATE_IN_PROGRESS      | AWS::CloudFormation::Stack | AgentkeelIngest User Initiated
AgentkeelIngest | 0/3 | 1:12:33 PM | UPDATE_IN_PROGRESS      | AWS::Lambda::Function      | Promoter (Promoter771ABA6D) 
AgentkeelIngest | 0/3 | 1:12:41 PM | UPDATE_IN_PROGRESS      | AWS::Lambda::Function      | Promoter (Promoter771ABA6D) Eventual consistency check initiated
AgentkeelIngest | 1/3 | 1:12:42 PM | UPDATE_COMPLETE         | AWS::Lambda::Function      | Promoter (Promoter771ABA6D) 
AgentkeelIngest | 2/3 | 1:13:40 PM | UPDATE_COMPLETE_CLEANUP | AWS::CloudFormation::Stack | AgentkeelIngest 
AgentkeelIngest | 3/3 | 1:13:41 PM | UPDATE_COMPLETE         | AWS::CloudFormation::Stack | AgentkeelIngest 

✅  AgentkeelIngest

✨  Deployment time: 73.37s

Outputs:
AgentkeelIngest.AdmittedFingerprint = e12988c54befa69c2f67437ab3f0c2a225a1845a5a43e553132003faa2e6431c
AgentkeelIngest.ProductionBucket = agentkeel-refagent-corpus-581208540944
AgentkeelIngest.QuarantineBucket = agentkeel-refagent-quarantine-581208540944
AgentkeelIngest.RecordTable = agentkeel-refagent-ingest-record
Stack ARN:
arn:aws:cloudformation:us-west-2:581208540944:stack/AgentkeelIngest/afb620e0-b95a-11f1-adeb-0afeb8aa52cf

✨  Total time: 90.56s

$ aws lambda get-function-configuration --function-name agentkeel-refagent-promoter --region us-west-2 \
  --query 'Environment.Variables.[GUARDRAIL_ID,GUARDRAIL_VERSION,ADMITTED_FINGERPRINT]'
[
    "1088aw3ujhyd",
    "5",
    "e12988c54befa69c2f67437ab3f0c2a225a1845a5a43e553132003faa2e6431c"
]
$ aws cloudformation describe-stacks --stack-name AgentkeelIngest --region us-west-2 \
  --query "Stacks[0].[StackStatus,LastUpdatedTime,Outputs[?OutputKey=='AdmittedFingerprint'].OutputValue]"
[
    "UPDATE_COMPLETE",
    "2026-09-26T20:12:29.398000+00:00",
    [
        "e12988c54befa69c2f67437ab3f0c2a225a1845a5a43e553132003faa2e6431c"
    ]
]
$ aws bedrock get-guardrail --guardrail-identifier 1088aw3ujhyd --guardrail-version 4 --region us-west-2 \
  --query '{version:version,status:status,description:description}'
{
    "version": "4",
    "status": "READY",
    "description": "rules sha256 9cbefa08166fa869a80a0a533431366458b5671f4fa501297bf6b61af0e4413f"
}
```
