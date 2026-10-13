---
# M09 PR 4 (#53), the close. Security's key, in words, over the Unsure
# items this seat carried into the close (#52's table): R3-a' (settled by
# the deploy), F3' (the residual tag reach), the platform App's installation
# on "selected repositories", the unsigned-draft deploy's record, the failed
# deploy runs and the schedules, and what stands in AWS after the close.
# This seat owns no path in this diff: nothing under infra/, .github/ or
# scripts/platform_check.py changed in PR 4. The one path listed is this
# file, which Product's pr4.md carries for the gate; the key is given here.
ruling: pr4-security
seat: Security
authorises:
  - milestones/M09/rulings/pr4-security.md
evidence:
  - SPEC/09-per-agent-rules.md#11-read-before-PR-2
  - milestones/M09/rulings/pr2-security.md
  - milestones/M09/rulings/pr3-security.md
  - evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json
  - https://github.com/andaro74/agentkeel/actions/runs/38342463397
pr: 53
---

# Ruling: M09 PR 4, Security

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-13.

## R3-a′, settled by the deploy

`pr3-security.md` item 4 left one reading to the first deploy that reached
the stack: whether Bedrock puts `aws:RequestTag/agentkeel:agent` in the
context of a plain `CreateGuardrail`. Deploy run 38342463397 created
`at8e36cosq1r` in stack `agentkeel-festival-desk` (`CREATE_COMPLETE`
2026-10-13 03:38Z) under the execution role, whose only create grant is
`MakeAnAgentsGuardrailOnlyWithItsTag` on `Resource *` held to that request
tag, and tagged it at create under `TagAnAgentsGuardrailAtCreateOnly`. The
key is in the context; the grant is live; the deploy boundary's
conditioned deny on an untagged guardrail did not fire. The fallback in
item 4 (the create unconditioned, the tag read on `TagResource`) is not
needed and is not built. The create handler's `ListTagsForResource` read
succeeded under the resource-tag condition (R3-d, read on the page at
PR 3). The eval role's `GetGuardrail` on the tagged guardrail succeeded
(R4): the envelope reads `source: read_back`.

## F3′, the residual tag reach: enough at M09 (proposed)

Three other projects' untagged guardrails in the shared account
(`beaconpave-gateway`, `beaconpave-tool-output`, `agentpave-gateway-dev`,
read 2026-10-11) can be tagged `agentkeel:agent` by the execution role on
a request carrying the tag, and would then fall under its resource-tag
grants (Update, Delete, CreateGuardrailVersion). The only principal with
that grant is the CloudFormation execution role, the only template it runs
is the one `GovernedAgent` renders from an agent repository the platform
check admitted, and an agent repository authors no CloudFormation
(`deploy.yml`, Security-hashed). Proposed ruling: enough at M09; recorded
as finding 9 of the close, standing with this seat. The alternative, a
flat deny by ARN naming the three, writes other projects' ids into this
stack and is not taken. If a fourth untagged guardrail appears in the
account, nothing here reads it; that is the standing gap.

## The platform App on "selected repositories" (proposed: stays)

`agentkeel-platform` (5144253) is installed on the organisation with
`repository_selection: selected`; `agentkeel-upgrades` and
`agentkeel-observer` are on all repositories. SPEC/06 §6 and
`pr2-security.md`'s grant reading describe "all". A new agent repository
has to be added to the platform App's installation by the owner before
`infra/ruleset/agent.post.json` can name its check ("Invalid integration
ids" until then; read at festival-desk's creation, 2026-10-12).
`infra/platform_grant.yaml` does not pin the selection, and
`scripts/platform_check.py grant` prints it without refusing. Proposed
ruling: the installation stays "selected". Narrower is safer: the App's
token reaches only repositories the owner named, which is the shape M07's
grant reading wanted for the other two Apps and this one has by accident.
The cost is one owner step per new repository, which the quickstart's
first step should name (Product, finding 3); SPEC/06 §6's "all" is
corrected to "selected, each new repository added by the owner" at the
next Product PR. No change to `infra/platform_grant.yaml` is made here;
whether it should pin the selection is a standing item with this seat.

## The deploy made on a draft ruling

Recorded at PR 3 as it happened (`pr3-security.md`, top; `pr3.md` item 5;
cold review F2 on `#52`): the bootstrap was deployed from `m09-pr3` at
`c7a8c36` on 2026-10-12 01:19Z on a draft Security had read and not
signed; the live policies were read back and pasted; the deploy stands on
the "Ruled by" that file carries since 2026-10-12. Finding 4 of the close,
a standing lesson for this seat: no by-hand deploy before the ruling file
reads "Ruled by" on the branch it is deployed from.

## The failed deploy runs and the schedules

50 scheduled `deploy.yml` runs failed at the held-pin check between
2026-10-12 13:58Z and 2026-10-13 03:09Z (finding 6): the workflow finds the
same admitted head every ten minutes until the registry holds it, and a
head the check refuses is retried, not parked. Harmless: nothing in AWS was
touched by any of them (each returned before the stack), and each left a
failed run with its artifacts. The latency finding 7 names (30 and 19
minutes) is the two `*/10` schedules in series. Neither is changed here: a
workflow edit is a Security PR with its hash, and nothing in claim 9 reads
it.

## What stands in AWS after the close

Nothing is deleted without a ruling from this seat, and none is given
here: festival-desk's stack (`agentkeel-festival-desk`), its guardrail
`at8e36cosq1r` (version 1), its key, its runtime and its image stand; the
50 failed runs' artifacts stand; refagent's guardrail keeps versions 1 to
6. The envelope row 9 cites read them as they are. A retirement of
festival-desk, if ever, goes through M07's path (`rollout: retired` in a
pull request by its seats, the registry row kept with `retired_at`), not
by hand (finding 18).

## What a reader can run

```
gh run view 38342463397 --json conclusion -q .conclusion                                   # success
aws bedrock get-guardrail --guardrail-identifier at8e36cosq1r --guardrail-version 1 --region us-west-2 --query '[description,topicPolicy.topics[].name,sensitiveInformationPolicy.piiEntities[].[type,action]]'   # the digest, one topic, PHONE and EMAIL ANONYMIZE (platform account)
aws bedrock list-tags-for-resource --resource-arn arn:aws:bedrock:us-west-2:581208540944:guardrail/at8e36cosq1r --region us-west-2   # agentkeel:agent=festival-desk
aws bedrock list-guardrails --region us-west-2 --query 'guardrails[].name'                   # refagent's, festival-desk's, and three of other projects'
gh api orgs/agentkeel-studio/installations --jq '.installations[] | [.app_id, .repository_selection]'   # 5144253 selected; the other two all
gh run list --workflow deploy.yml --limit 200 --json createdAt,conclusion --jq '[.[] | select(.createdAt > "2026-10-12T13:50:00Z" and .createdAt < "2026-10-13T03:35:00Z")] | group_by(.conclusion) | map({(.[0].conclusion): length})'   # failure 50
```

A guardrail create refused under the request-tag grant, a read-back
refused under R4's grant, a deletion in AWS made at this close, or a
change under `infra/` or `.github/` in this PR, makes this ruling wrong.
