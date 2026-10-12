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
was read instead on 2026-10-11, before any deploy, and it settles three
things.

1. **`CreateGuardrail` takes no `guardrail` resource type.** Its row lists
   the optional `automated-reasoning-policy`, `automated-reasoning-policy-version`
   and `guardrail-profile` types and no required one. The page's own
   rule: a statement naming a resource type the action does not take never
   applies. The execution role's `MakeAnAgentsGuardrailOnlyWithItsTag` was
   on `guardrail/*`, so it granted nothing, and the first deploy of an agent
   with `rules/` would have been refused on `CreateGuardrail`: the refusal
   `pr2-security.md` named as a PR 3 repair, read here from the page rather
   than from a failed run. Repaired: the statement is on `Resource *`, held
   by `Null aws:RequestTag/agentkeel:agent: false`, the same shape as
   `CreateAgentRuntime` held by its subnets (M07) and as the deploy
   boundary's deny already read it.
2. **The `CreateGuardrail` operation authorises `bedrock:TagResource` too**
   when the request carries tags (the page's operations table), and
   CloudFormation's create handler for `AWS::Bedrock::Guardrail` calls
   `TagResource` and `ListTagsForResource` on the new guardrail
   (`describe-type`, `tagOnCreate: true`, read 2026-10-11). At create the
   guardrail carries no tag, so the resource-tag statement cannot admit the
   call: the M07 lesson for `runtime/*` (deploy runs 37066321605 and
   37074759767). Repaired: `TagAnAgentsGuardrailAtCreateOnly` grants
   `bedrock:TagResource` on `guardrail/*`, held to a request carrying the
   agent tag, and nothing else in that statement.
3. **`ListTagsForResource` on `guardrail*` carries `aws:ResourceTag`**
   (R3-d on `#50`), so the resource-tag condition on the read handler's
   call stays as PR 2 wrote it.

**F3 on PR 2, reopened by item 2 and closed by name.** PR 2 kept
`TagResource` off the request-tag side because a request carrying the tag
could tag refagent's untagged guardrail and bring it under the execution
role's resource-tag grants (`security-reviewer` and cold review F3 on
`#50`). Item 2 puts `TagResource` back on that side, so the deploy
boundary now denies `bedrock:TagResource` and `bedrock:UntagResource` on
refagent's guardrail by its ARN (`NeverTagRefagentsGuardrail`), flat and
unconditioned, stack-wide: no deploy-plane role tags or untags refagent's
guardrail whatever the request carries. The conditioned deny on an
untagged guardrail (`NeverTagAGuardrailThatIsNotATaggedAgentsOwn`) stays
for a request carrying no tag.

**What is not closed, stated.** Any *other* untagged guardrail in this
shared account (none is the platform's; refagent's is the only one the
bootstrap builds) could be tagged `agentkeel:agent` by the execution role
on a request carrying the tag, and would then be under its resource-tag
grants. The only principal with that grant is the CloudFormation execution
role, and the only template it runs is the one `GovernedAgent` renders from
an agent repository the platform check admitted; an agent repository
authors no CloudFormation. This seat's call whether that is enough at M09
or whether the boundary should deny `TagResource` on every guardrail not
built by an agent stack, which needs a list the bootstrap does not hold.
Proposed: enough at M09, recorded here and in the PR body under Unsure.

**What the deploy changes** (`npx aws-cdk@2 diff` from `infra/bootstrap/`
on this branch, 2026-10-11, against the stack deployed 2026-10-02): PR 2's
narrowing (the boundary's guardrail deny conditioned on the tags, the
execution role's two guardrail statements, the eval role's `GetGuardrail`
on a tagged guardrail, refagent's guardrail version 6 with the baseline's
digest) and this PR's three changes (the create on `*`, the tag-at-create
grant, the deny on refagent's guardrail by ARN). Nothing else. The stack's
`GuardrailVersionForTheManifest` output after the deploy is what the Rule
Owner's version-6 pull request copies (step 2).

## What this PR does not do

- No grant is deployed by it. The deploy is this seat's, by hand, from
  this branch, after this file reads "Ruled by" and before the fixture
  repository's first merge (step 1).
- No change to the agent plane's boundary, the deploy role's trust, the
  eval role, `verify`'s identity, any bucket or key policy, any security
  group or VPC. `deploy.yml` and the construct are unchanged;
  `infra/workflows.sha256` is unchanged.
- cdk-nag: the bootstrap's report regenerated for the suppression's
  wording (the execution role's `Resource::*` already in `APPLIES_TO`); the
  construct's report unchanged.

## What a reader can run

```
git show 2bc9067 --stat                                                       # infra/bootstrap/app.py and its NagReport.csv, nothing else
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py -q   # 88 passed: the three statements by Sid, the two tag denies, the handlers' actions granted
make validate                                          # twenty-one ok; cdk-nag, every stack holds the regenerated report
cd infra/bootstrap && PYTHONPATH=../.. npx aws-cdk@2 diff   # the IAM statement table above, read-only
curl -sL https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock.html | grep -o 'list_bedrock-action-CreateGuardrail".\{0,900\}' | sed 's/<[^>]*>/ /g'   # the CreateGuardrail row: no guardrail resource type
aws cloudformation describe-type --type RESOURCE --type-name AWS::Bedrock::Guardrail --region us-west-2 --query Schema --output text | python -c "import sys,json; s=json.load(sys.stdin); print(s['handlers']['create']['permissions'], s['tagging']['tagOnCreate'])"
```

Any statement on `CreateGuardrail` scoped to `guardrail/*`, a `TagResource`
grant at create held to a resource tag, or a boundary that lets a
deploy-plane role tag refagent's guardrail, makes this ruling wrong.
