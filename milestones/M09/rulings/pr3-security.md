---
# M09 PR 3 (#51), the run. Security's key over the one Security path this PR
# touches: the bootstrap stack and its cdk-nag report, repaired before the
# by-hand deploy on a reading of the Service Authorization Reference, not at
# the first deploy. Product's file is pr3.md (R8, the run file's observed
# block, this milestone's README), the Data Owner's pr3-data-owner.md (R9,
# R7, R11), Engineering's pr3-engineering.md (the tests, the run test's
# marker, the cold review).
ruling: pr3-security
seat: Security
authorises:
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/rulings/pr2-security.md
  - https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock.html
pr: 51
---

# Ruling: M09 PR 3, Security

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-11 from
the reading below; the by-hand bootstrap deploy (`milestones/M09/README.md`,
"By-hand steps", step 1) waits for this file to read "Ruled by" and is made
from this PR's branch, as M07 PR 3's second repair was.

## What this file rules

**R3-a, read before the deploy.** PR 2's Security ruling left Bedrock's
evaluation of the tag conditions on the guardrail actions to the first
deploy of the fixture agent (`pr2-security.md`, "Unsure, for this seat";
`#50` Unsure R3-a). The Service Authorization Reference for Amazon Bedrock
(`list_bedrock.html`; the `list_amazonbedrock.html` address redirects to
the index) was read on 2026-10-11, before any deploy, with CloudFormation's
own `describe-type` for the two resource types the fixture's stack adds.
It settles two things, leaves one to the first deploy, and names it.

1. **`CreateGuardrail` takes no `guardrail` resource type.** Its row's
   resource-types cell lists the optional `automated-reasoning-policy`,
   `automated-reasoning-policy-version` and `guardrail-profile` and no
   required type. The page's own rule: a statement naming a resource type
   the action does not take never applies. The execution role's
   `MakeAnAgentsGuardrailOnlyWithItsTag` was on `guardrail/*`, so it
   granted nothing, and the first deploy of an agent with `rules/` would
   have been refused on `CreateGuardrail`: the refusal `pr2-security.md`
   named as a PR 3 repair, read here from the page rather than from a
   failed run. Repaired (`2bc9067`): the statement is on `Resource *`, held
   by `Null aws:RequestTag/agentkeel:agent: false`, the shape
   `CreateAgentRuntime` has with its subnets (M07) and the shape the deploy
   boundary's deny already had.
2. **The `CreateGuardrail` operation authorises `bedrock:TagResource` too**
   when the request carries tags (the page's operations table lists the
   operation against `bedrock:CreateGuardrail` and `bedrock:TagResource`),
   and the create handler of `AWS::Bedrock::Guardrail` holds `TagResource`
   and `ListTagsForResource` in its permission list with `tagOnCreate:
   true` (`describe-type`, read 2026-10-11). At create the guardrail
   carries no tag, so the resource-tag statement cannot admit the call: the
   M07 lesson for `runtime/*` (deploy runs 37066321605 and 37074759767).
   Repaired (`2bc9067`): `TagAnAgentsGuardrailAtCreateOnly` grants
   `bedrock:TagResource` on `guardrail/*`, held to a request carrying the
   agent tag, and nothing else in that statement.
3. **`ListTagsForResource` on `guardrail*` carries `aws:ResourceTag`**
   (R3-d on `#50`), so the resource-tag condition on the read handler's
   call stays as PR 2 wrote it.
4. **Left to the first deploy, named** (`security-reviewer` F1 on this
   PR). The `CreateGuardrail` row's condition-keys cell, quoted:
   `aws:RequestTag/${TagKey}`, `aws:ResourceTag/${TagKey}`, `aws:TagKeys`
   beside `automated-reasoning-policy` and its version;
   `aws:RequestTag/${TagKey}`, `aws:TagKeys` beside `guardrail-profile`;
   no key on a row of its own. `CreateAgent` and `CreateKnowledgeBase` on
   the same page list `aws:RequestTag` on a row of their own. Whether
   Bedrock puts `aws:RequestTag/agentkeel:agent` in the context of a plain
   `CreateGuardrail` that names no policy and no profile is not settled by
   the page. If it does not, the grant in item 1 is dead the way the
   `guardrail/*` one was, **and so is the deploy boundary's deny on an
   untagged guardrail** (both keys null), which PR 2 wrote on the same
   assumption: the first fixture deploy is refused on `CreateGuardrail`
   either way, and that is the reading. Fallback, stated now: the create
   unconditioned on the execution role and exempted from the boundary's
   conditioned deny, the agent tag read on the handler's `TagResource`
   instead, whose `guardrail` row does list `aws:RequestTag`. A PR 3
   repair if read, not a finding of the claim (SPEC/09 §5.1).

**F3 on PR 2, reopened by item 2 and closed by name.** PR 2 kept
`TagResource` off the request-tag side because a request carrying the tag
could tag refagent's untagged guardrail and bring it under the execution
role's resource-tag grants (`security-reviewer` and cold review F3 on
`#50`). Item 2 puts `TagResource` back on that side, so the deploy
boundary now denies `bedrock:TagResource` and `bedrock:UntagResource` on
refagent's guardrail by its ARN, in both forms the Apply grant names
(`guardrail/<id>` and `guardrail/<id>:*`, `security-reviewer` F2 on this
PR), flat and unconditioned, stack-wide: no deploy-plane role tags or
untags refagent's guardrail whatever the request carries. The conditioned
deny on an untagged guardrail (`NeverTagAGuardrailThatIsNotATaggedAgentsOwn`)
stays for a request carrying no tag.

**What is not closed, counted** (`security-reviewer` F3 on this PR).
`aws bedrock list-guardrails` in the platform account, 2026-10-11: four
guardrails, all untagged: `agentkeel-refagent` (`1088aw3ujhyd`, the
bootstrap's, denied by ARN above) and three of other projects in this
shared account (`beaconpave-gateway`, `beaconpave-tool-output`,
`agentpave-gateway-dev`). Each of the three could be tagged
`agentkeel:agent` by the execution role on a request carrying the tag, and
would then be under its resource-tag grants (Update, Delete,
CreateGuardrailVersion). The only principal with that grant is the
CloudFormation execution role, and the only template it runs is the one
`GovernedAgent` renders from an agent repository the platform check
admitted; an agent repository authors no CloudFormation. This seat's call:
enough at M09 (proposed), or a deny by ARN list of the three, which names
other projects' ids in this stack. Recorded here and in the PR body under
Unsure.

**The cdk-nag suppression** (`security-reviewer` F4 on this PR): PR 2's
sentence said every action on an existing guardrail, tagging included, is
held to a resource tag and that the boundary denies tagging an untagged
guardrail; after item 2 neither is true of a tagged request. Rewritten:
tagging is the exception, refagent's is out of reach by ARN, another
untagged guardrail only by a tagged request from a template `GovernedAgent`
renders. The report regenerated; `validate` holds it.

## What the deploy changes

`npx aws-cdk@2 diff` from `infra/bootstrap/` on this branch, 2026-10-11,
against the stack deployed 2026-10-02 (before PR 2), read-only; the change
set could not be created from the laptop and the diff is template-based.
Four resources change and nothing else: the deploy boundary, the execution
role's policy, the eval role's policy, and `RefagentGuardrailVersion`
(**replace**: version 6, the baseline's digest; the old version is
retained). The IAM statement table, verbatim:

```
┌───┬─────────────────────────────────────────────────────────┬────────┬────────────────────────────────┬──────────────────────┬──────────────────────────────────────────────┐
│   │ Resource                                                │ Effect │ Action                         │ Principal            │ Condition                                    │
├───┼─────────────────────────────────────────────────────────┼────────┼────────────────────────────────┼──────────────────────┼──────────────────────────────────────────────┤
│ + │ *                                                       │ Allow  │ bedrock:CreateGuardrail        │ AWS:${ExecutionRole} │ "Null": {                                    │
│   │                                                         │        │                                │                      │   "aws:RequestTag/agentkeel:agent": "false"  │
│   │                                                         │        │                                │                      │ }                                            │
│ + │ *                                                       │ Deny   │ bedrock:Create*Guardrail*      │ AWS:${EvalRole}      │                                              │
│   │                                                         │        │ bedrock:Delete*Guardrail*      │                      │                                              │
│   │                                                         │        │ bedrock:ListGuardrails         │                      │                                              │
│   │                                                         │        │ bedrock:Put*Guardrail*         │                      │                                              │
│   │                                                         │        │ bedrock:Update*Guardrail*      │                      │                                              │
│   │                                                         │        │ iam:*                          │                      │                                              │
│   │                                                         │        │ logs:Delete*                   │                      │                                              │
│   │                                                         │        │ s3:PutBucketPolicy             │                      │                                              │
│   │                                                         │        │ sts:AssumeRole                 │                      │                                              │
│ + │ *                                                       │ Deny   │ bedrock:GetGuardrail           │ AWS:${EvalRole}      │ "Null": {                                    │
│   │                                                         │        │                                │                      │   "aws:ResourceTag/agentkeel:agent": "true"  │
│   │                                                         │        │                                │                      │ }                                            │
│ - │ *                                                       │ Deny   │ bedrock:Create*Guardrail*      │ AWS:${EvalRole}      │                                              │
│   │                                                         │        │ bedrock:Delete*Guardrail*      │                      │                                              │
│   │                                                         │        │ bedrock:GetGuardrail           │                      │                                              │
│   │                                                         │        │ bedrock:ListGuardrails         │                      │                                              │
│   │                                                         │        │ bedrock:Put*Guardrail*         │                      │                                              │
│   │                                                         │        │ bedrock:Update*Guardrail*      │                      │                                              │
│   │                                                         │        │ iam:*                          │                      │                                              │
│   │                                                         │        │ logs:Delete*                   │                      │                                              │
│   │                                                         │        │ s3:PutBucketPolicy             │                      │                                              │
│   │                                                         │        │ sts:AssumeRole                 │                      │                                              │
├───┼─────────────────────────────────────────────────────────┼────────┼────────────────────────────────┼──────────────────────┼──────────────────────────────────────────────┤
│ + │ arn:aws:bedrock:us-west-2:${AWS::AccountId}:guardrail/* │ Allow  │ bedrock:TagResource            │ AWS:${ExecutionRole} │ "Null": {                                    │
│   │                                                         │        │                                │                      │   "aws:RequestTag/agentkeel:agent": "false"  │
│   │                                                         │        │                                │                      │ }                                            │
│ + │ arn:aws:bedrock:us-west-2:${AWS::AccountId}:guardrail/* │ Allow  │ bedrock:CreateGuardrailVersion │ AWS:${ExecutionRole} │ "Null": {                                    │
│   │                                                         │        │ bedrock:DeleteGuardrail        │                      │   "aws:ResourceTag/agentkeel:agent": "false" │
│   │                                                         │        │ bedrock:GetGuardrail           │                      │ }                                            │
│   │                                                         │        │ bedrock:ListTagsForResource    │                      │                                              │
│   │                                                         │        │ bedrock:TagResource            │                      │                                              │
│   │                                                         │        │ bedrock:UntagResource          │                      │                                              │
│   │                                                         │        │ bedrock:UpdateGuardrail        │                      │                                              │
│ + │ arn:aws:bedrock:us-west-2:${AWS::AccountId}:guardrail/* │ Allow  │ bedrock:GetGuardrail           │ AWS:${EvalRole}      │ "Null": {                                    │
│   │                                                         │        │                                │                      │   "aws:ResourceTag/agentkeel:agent": "false" │
│   │                                                         │        │                                │                      │ }                                            │
└───┴─────────────────────────────────────────────────────────┴────────┴────────────────────────────────┴──────────────────────┴──────────────────────────────────────────────┘
```

The table is the roles' policies; the deploy boundary's three statements
(the guardrail deny conditioned on both tags, the tag deny on an untagged
guardrail, the tag deny on refagent's guardrail by ARN) are in the
`Resources` section of the same diff, which the `cdk diff` tool does not
tabulate. The stack's `GuardrailVersionForTheManifest` output after the
deploy is what the Rule Owner's version-6 pull request copies (step 2).

## What this PR does not do

- No grant is deployed by it. The deploy is this seat's, by hand, from
  this branch, after this file reads "Ruled by" and before the fixture
  repository's first merge (step 1). Until then `main` describes a boundary
  that is not deployed and nothing here has fired (`security-reviewer`
  NOTE 1).
- No change to the agent plane's boundary, the deploy role's trust, the
  eval role beyond PR 2's, `verify`'s identity, any bucket or key policy,
  any security group or VPC. `deploy.yml` and the construct are unchanged;
  `infra/workflows.sha256` is unchanged.
- cdk-nag: the bootstrap's report regenerated for the suppression's
  wording (the execution role's `Resource::*` already in `APPLIES_TO`); the
  construct's report unchanged. The deploy boundary's 6,144-character limit
  is not read at synth; the deploy reads it (`security-reviewer` NOTE 5).

## The `security-reviewer` read

On the diff `f5ecb25...a132c08` (5 files): **0 BLOCK, 4 FINDING, 5 NOTE**.
Every finding taken in the commit after it (F1 the cell quoted and the
reading named, item 4; F2 both ARN forms; F3 the account counted; F4 the
sentence rewritten). NOTE 2 taken (the table above); NOTE 4 taken ("calls"
to "holds in its permission list", item 2); NOTEs 1, 3 and 5 recorded
above. Pasted verbatim:

> Read: the diff f5ecb25...a132c08 (5 files)
>
> Security review, M09 PR 3 repair (infra/bootstrap/app.py, its NagReport.csv, tests/test_bootstrap.py, tests/test_m09_platform.py, milestones/M09/rulings/pr3-security.md). Patch: C:\Users\andar\AppData\Local\Temp\claude\c--Users-andar-code-agentkeel\df2c1915-48a6-4ef5-b1a2-a21d92877c43\scratchpad\m09-pr3.patch. Tree read only to resolve names the diff references (C:\Users\andar\code\agentkeel\infra\bootstrap\app.py lines 150, 285, 450-466, 805-809; C:\Users\andar\code\agentkeel\tests\test_m09_platform.py lines 28-69; C:\Users\andar\code\agentkeel\tests\test_bootstrap.py lines 49-67, 649-653). A report, not a ruling.
>
> **1. Workflows.** No file under `.github/workflows/**` is in the diff. Nothing to check; `infra/workflows.sha256` is not in the 5 files, consistent with ruling line 238.
>
> **2. Switched off from inside.** The boundary lives in `infra/bootstrap/app.py` (Security path; `ruling-cited` and CODEOWNERS). The deployed stack is changed only by Security's by-hand deploy (ruling lines 232-234). Nobody with write alone can change the deployed deny; they can change the text on `main` and the gates read the ruling. Plain answer: an edit needs a Security ruling file, and the deploy needs Security's hands. The text and the deployed stack diverge until step 1 runs (NOTE 1).
>
> **3. IAM.**
>
> - FINDING 1 — the `CreateGuardrail` condition key is not quoted. Patch lines 76-77: `resources=["*"], conditions={"Null": {f"aws:RequestTag/{AGENT_TAG}": "false"}}`. The ruling (lines 170-181) quotes the resource-types cell of the CreateGuardrail row and not its condition-keys cell. `Null ... false` matches only when the service puts `aws:RequestTag/agentkeel:agent` in the request context; if the CreateGuardrail row does not list `aws:RequestTag/${TagKey}`, this grant is dead in the same way the `guardrail/*` one was, and the first fixture deploy is refused on CreateGuardrail again. Same class of error as R3-a. Settles it: quote the condition-keys cell for CreateGuardrail in the ruling and in the app.py comment (lines 66-72). Security rules.
>
> - FINDING 2 — the flat deny names one ARN form; the Apply grant in the same method names two. Patch lines 105-110: `NeverTagRefagentsGuardrail ... resources=[guardrail.attr_guardrail_arn]`. Tree line 1213, two statements above it: `resources=[guardrail.attr_guardrail_arn, f"{guardrail.attr_guardrail_arn}:*"]`, so the bootstrap already treats `guardrail/<id>:<version>` as a form Bedrock accepts. A tagged request to `TagResource` on `guardrail/<id>:6` matches the allow at patch line 92 (`guardrail/*`), is not caught by the conditioned deny (request carries the tag), and is not caught by this deny (ARN differs). Whether Bedrock's TagResource accepts a versioned ARN is not read anywhere in the PR. The suppression's own rule applies: "a Deny must cover every resource" (patch line 123, `{CEILING}`). Settles it: add `f"{guardrail.attr_guardrail_arn}:*"` to the deny's resources, or cite the page that says TagResource rejects a versioned ARN. Security rules.
>
> - FINDING 3 — residual reach to any other untagged guardrail in the account, stated but unsettled. Patch lines 89-94: `TagAnAgentsGuardrailAtCreateOnly` grants `bedrock:TagResource` on `guardrail/*` held to the request tag alone. The boundary's conditioned deny (tree line 460-466) fires only when both request and resource are untagged, so a tagged request on any untagged guardrail is allowed and the guardrail then falls under `ReadUpdateVersionAndRemoveATaggedAgentsGuardrailOnly` (tree lines 805-809: Update, Delete, CreateVersion). The ruling says so (lines 208-218) and proposes "enough at M09". The claim that refagent's "is the only one the bootstrap builds" (line 209) is about the bootstrap, not the account; nothing in the PR reads the account. Settles it cheaply: an `aws bedrock list-guardrails` read on 2026-10-11 recorded in the ruling with the count, or a deny by ARN list. Security rules; the PR body's Unsure should carry it as the ruling says it will.
>
> - FINDING 4 — the cdk-nag suppression keeps a sentence the new grant falsifies. Patch lines 115-118 (kept from PR 2): "every action on an existing guardrail, tagging included, to one carrying that tag, so refagent's, untagged, and any other in this shared account are out of reach; the deploy boundary denies the same, and denies tagging an untagged guardrail." After patch line 92, TagResource on an existing untagged guardrail is allowed on a tagged request, and the boundary does not deny tagging an untagged guardrail when the request is tagged. The PR 3 sentence (lines 119-123) is added after it without retracting it. The same text is repeated in 19 `+` rows of the CSV (patch lines 25-45). Settles it: rewrite the PR 2 sentence to "...so refagent's is out of reach by ARN, and another untagged guardrail only by a tagged request from a template GovernedAgent renders". Security rules.
>
> - Boundary carried: tree line 285 `iam.PermissionsBoundary.of(self).apply(deploy_boundary)`; the execution role is in this stack, so the new deny applies to it. Confirmed.
> - R4: `kms:PutKeyPolicy` stays in the flat deny (tree line 439), unchanged by the diff. The deploy role's trust and the agent boundary are not in the diff.
> - Wildcard with a stated reason: `*` on CreateGuardrail, reason at patch lines 66-72 (no `guardrail` resource type). Accepted as a reason, subject to FINDING 1.
> - Widening beyond the create handler: none found. The two new grants are CreateGuardrail (request-tagged) and TagResource on `guardrail/*` (request-tagged), which the caller's SAR read names as the CreateGuardrail operation's dependent action. `UntagResource` on the execution role is on the resource-tag side only (tree line 807): an agent's own guardrail can be untagged and then is out of reach, a lock-out, not an escalation.
> - Deploy-plane reach to refagent's guardrail after this change: TagResource/UntagResource by the flat deny (subject to FINDING 2); Get/Update/Delete/CreateVersion/Put by `NeverTouchAGuardrailThatIsNotATaggedAgentsOwn` on an untagged resource (tree lines 450-456, unchanged); ApplyGuardrail deliberately open to the eval role. No other path found in the diff.
>
> **4. Network.** No security group, VPC, endpoint or egress rule is in the diff. Nothing to check.
>
> **5. Evidence.** No bucket, lock or retention change is in the diff. Nothing to check.
>
> **6. cdk-nag.** One suppression touched: `AwsSolutions-IAM5` on `ExecutionRole/DefaultPolicy/Resource`, patch lines 114-124, applied to `[Resource::*]` (already in the CSV before the diff, patch line 16) and `[Resource::...guardrail/*]` (one `-` row, one `+` row). The added sentence is specific (action, resource, condition, source, date). The kept sentence is now wrong (FINDING 4). The whole paragraph is one shared reason for every wildcard on the role; each wildcard's reason is inside it, which is the standing pattern here, not new in this PR.
>
> **Tests: do they read what they claim.**
>
> - `test_m09_platform.py` patch lines 290-322 read Sid, Action, Resource and Condition of the three allow statements and the two boundary denies from the synthesised template, including `"Condition" not in refagent` and `Resource == {"Fn::GetAtt": [guardrail_logical, "GuardrailArn"]}`. They read the diff. They do not read the versioned-ARN form (FINDING 2).
> - Patch lines 333-354, `GUARDRAIL_HANDLERS_NEED`, is hand-typed from describe-type and read by action name only; the docstring says so (line 332 "By action"). It cannot show the request tag is present on CloudFormation's CreateGuardrail call. That is the deploy's to show.
> - `test_bootstrap.py` patch lines 269-270 narrow the flat-deny set to `s["Resource"] == "*"`. From now on a flat deny on a named resource that collides with a construct resource is not read by this test. Today the only such deny names refagent's guardrail, which the construct does not render. NOTE 3.
>
> **Ruling draft vs the diff.**
>
> - Lines 247-248 ("88 passed", "twenty-one ok") and lines 220-228 (the `cdk diff` table, "Nothing else") are statements about runs, not in the diff. The deploy carries PR 2's and PR 3's IAM changes together against a stack from 2026-10-02; the ruling describes that diff from memory of a run. Settles it: paste the `cdk diff` IAM statement table into the PR body or the ruling. NOTE 2.
> - Line 185 says the create handler "calls TagResource and ListTagsForResource"; describe-type gives the handler's permission list, which is a superset of what it calls. The load-bearing reason is the SAR operations table (CreateGuardrail authorises TagResource), which the ruling has at line 182. Wording only. NOTE 4.
> - Everything else the ruling says the diff does, the diff does: Resource `*` (patch line 76), TagResource at create (89-94), the flat deny by ARN (105-110), the suppression wording (119-123), construct and workflows untouched (5 files).
>
> **NOTEs.**
>
> - NOTE 1 — until by-hand step 1 runs, `main` describes a boundary that is not deployed; the deployed stack (2026-10-02) still has PR 2's predecessor, the outright guardrail deny. Nothing in the diff fires until then; no control here has fired on its seeded case.
> - NOTE 2 — the `cdk diff` output the ruling relies on is not in the PR.
> - NOTE 3 — `test_bootstrap.py` lines 269-270: named-resource flat denies are no longer read for collisions.
> - NOTE 4 — ruling line 185 wording ("calls" for a permission list).
> - NOTE 5 — the deploy boundary is a managed policy with a 6,144-character limit that synth does not check; the new statement adds to it. The deploy is where this would surface.
>
> Checklist items 1, 4, 5: nothing in scope in this diff.
>
> BLOCK: 0 · FINDING: 4 · NOTE: 5

## What a reader can run

```
git log f5ecb25..HEAD --format='%h %s' -- infra/bootstrap   # the two Security commits and nothing else under infra/
git show 2bc9067 --stat; git show c7a8c36 --stat             # infra/bootstrap/app.py and its NagReport.csv in each
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py -q   # 88 passed: the three statements by Sid, the two tag denies with both ARN forms, the handlers' actions granted
make validate                                                # twenty-one ok; cdk-nag, every stack holds the regenerated report
cd infra/bootstrap && PYTHONPATH=../.. npx aws-cdk@2 diff          # the table above and four changed resources, read-only
curl -sL https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock.html | grep -o 'list_bedrock-action-CreateGuardrail".\{0,900\}' | sed 's/<[^>]*>/ /g'      # the row: no guardrail resource type, the keys on resource rows
curl -sL https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock.html | grep -o 'list_bedrock-operation-bedrock-CreateGuardrail".\{0,1200\}' | sed 's/<[^>]*>/ /g'   # the operation: CreateGuardrail and TagResource
aws cloudformation describe-type --type RESOURCE --type-name AWS::Bedrock::Guardrail --region us-west-2 --query Schema --output text | python -c "import sys,json; s=json.load(sys.stdin); print(s['handlers']['create']['permissions'], s['tagging']['tagOnCreate'])"
aws bedrock list-guardrails --region us-west-2 --query 'guardrails[].name'   # four, refagent's and three of other projects'
```

Any statement on `CreateGuardrail` scoped to `guardrail/*`, a `TagResource`
grant at create held to a resource tag, a boundary that lets a deploy-plane
role tag refagent's guardrail in either ARN form, or a first deploy refused
on `CreateGuardrail` with the request tag present, makes this ruling wrong.
