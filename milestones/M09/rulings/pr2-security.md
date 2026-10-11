---
# M09 PR 2 (#50), Security's key over the Security paths this PR touches:
# the construct and its app, the bootstrap stack and its regenerated
# NagReport, the construct's regenerated NagReport, deploy.yml, evals.yml
# and infra/workflows.sha256. The two rulings SPEC/09 §11 puts to this seat
# before PR 2: R3 (which role builds a guardrail for a new agent) and R4
# (the observer's read-back). Product's file is rulings/pr2.md; the Rule
# Owner's is pr2-rule-owner.md; Engineering's (with the cold review) is
# pr2-engineering.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - infra/bootstrap/app.py
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/governed_agent.py
  - infra/construct/app.py
  - infra/construct/AwsSolutions--AgentkeelRefagent-NagReport.csv
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/README.md
  - milestones/M09/feasibility.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
pr: 50
---

# Ruling: M09 PR 2, Security

Ruled by: pending

## R3. The construct builds an agent's guardrail in the agent's own stack

For an agent whose repository carries `rules/guardrail.yaml`,
`infra/construct/governed_agent.py` builds one Bedrock Guardrail,
`agentkeel-<name>`, from the agent's rules merged onto
`rules/baseline.yaml` at synth (the platform check's own merge,
`src/validate/agent_rules.py`; a file it would refuse is refused at synth),
tagged `agentkeel:agent=<name>`, with a numbered version whose description
carries the digest of the baseline and the agent's files, retained. The
role's invoke and the runtime's converse are conditioned on **the stack's
own resource** (`bedrock:GuardrailIdentifier` is the built ARN at the built
version; `AGENTKEEL_GUARDRAIL_ARN` is the built ARN), and the manifest's
pin is read only to refuse null and refagent's. The bootstrap keeps
refagent's guardrail, untagged. An agent without `rules/` is as at M06.

**The deploy plane's deny, narrowed** (`infra/bootstrap/app.py`,
`agentkeel-deploy-boundary`): every guardrail action but Apply and List
was denied outright since M03 PR 2. It is now denied on a guardrail that
is not tagged as an agent's own, read as both `aws:RequestTag/agentkeel:agent`
and `aws:ResourceTag/agentkeel:agent` null: a create with the tag in the
request passes, every action on a guardrail carrying the tag passes, and
refagent's and any other guardrail in the shared account stay out of
reach. `ListGuardrails` stays denied outright. The verbs stay patterns.
The execution role gains two statements: `CreateGuardrail` held to a
tagged request (CloudFormation passes the tags in the create); Get,
Update, Delete, CreateGuardrailVersion, the tags and `ListTagsForResource`
held to a tagged resource. `TagResource` was in the first statement too
and could have tagged refagent's untagged guardrail, bringing it under the
second (`security-reviewer` finding and cold review finding 3 on this PR):
repaired, and the boundary now denies `TagResource` and `UntagResource` on
an untagged guardrail, with a test. The built guardrail and its version
are both retained. The agent plane's deny is unchanged: no agent role may touch any
guardrail but Apply.

**The deploy writes the registry row** (`deploy.yml` `deploy-agent`): the
stack's `GuardrailId`, `GuardrailVersion` and `GuardrailDigest` outputs go
to `build answer` (`--guardrail`, so the answer record names the guardrail
the call carried) and to `scripts/registry.py write`. Before the stack is
touched, the platform check runs once more with the pin the row holds
(`--held-guardrail`), so a head whose manifest pins anything but the built
guardrail is refused and a placeholder is admitted only while the row holds
none (the placeholder's life, with R10). The check's own job
(`platform-check.yml`) holds no AWS credential and cannot read the row:
that refusal fires at the deploy, after a merge, not at the check. Stated
under Unsure.

**Nothing new runs.** The deploy role's trust, the eval role's and
`verify`'s identity are unchanged; no agent repository can assume or sign
anything. The first deploy of an agent with `rules/` is PR 3's run.

## R4. The observer's role may read a built guardrail back

The eval role gains `bedrock:GetGuardrail` on a guardrail tagged as an
agent's own (`Null aws:ResourceTag/agentkeel:agent: false`), read only;
its deny on `GetGuardrail` is kept for an untagged one (refagent's), and
its other guardrail denies are unchanged. `scripts/observe_rules.py` reads
the version's description, the topic names and the PII entities as the
eval role, in `evals.yml`'s eval-role block. Until the stack is deployed
the read is refused and written as such, and F9.1 reads the registry row's
digest instead (SPEC/09 §9 cut 3), named `source: registry` on the
envelope; F9.2's guardrail half (every baseline rule in the built
guardrail) is then **unread**, `baseline_in_guardrail: null`, not a miss,
and the cell says so (cold review finding 1 on this PR). The grant deployed
before PR 3's run is what makes both halves read.

## What this PR does not do

- **No grant is deployed by it.** The bootstrap stack is deployed by hand
  (this seat, `infra/bootstrap/README.md`), a by-hand step before PR 3's
  run (`milestones/M09/README.md`). Until then: the execution role is
  refused on `CreateGuardrail` at the first deploy of an agent with
  `rules/` (a PR 3 repair, not a finding of the claim), and the read-back
  is refused.
- No bucket policy, key policy, security group, VPC or trust policy
  changes. `agentkeel-audit-read` already reads `envelopes/agents/*`.
- `evals.yml` gains two steps and one Makefile variable; a refused read,
  a run file that does not parse or an earlier part's file that does not
  parse is written as an observation with its error, never a failed job. `infra/workflows.sha256` recomputed for
  `evals.yml` and `deploy.yml`.
- cdk-nag: both committed reports regenerated and held by `validate`; the
  new rows are the execution role's and the eval role's `guardrail/*`,
  each with its reason naming SPEC/01 §6 and the tag that holds it.

## Unsure, for this seat

- Whether Bedrock evaluates `aws:RequestTag` on `CreateGuardrail` and
  `aws:ResourceTag` on the other guardrail actions as the IAM reference
  lists them. The build follows the reference; the first deploy of the
  fixture agent (PR 3's run) is the reading. If the create is refused on
  the condition, the fallback is the deny narrowed by resource ARN after
  the create, or the bootstrap alternative R3 named.
- The placeholder's refusal fires at the deploy, not at the check (above).
- Whether `bedrock:ListTagsForResource` carries `aws:ResourceTag`; if not,
  the execution role's read handler is refused on it and the statement
  loses its condition for that one action (`security-reviewer` on this
  PR). Read on the Service Authorization Reference page before the by-hand
  deploy.
- The construct's suppression key for an agent with `rules/` (by logical
  id) is first exercised by `validate` at no synth in this PR; the fixture's
  synth in `tests/test_m09_platform.py` exercises it.

## The `security-reviewer` read

On the diff `460990b...d3897ab` (40 files): **0 BLOCK, 1 FINDING, 22
NOTE**. The finding (the execution role could tag refagent's untagged
guardrail and then reach it; the cold review's finding 3 names the same)
is **repaired** in the commit after `d3897ab`: `TagResource` out of the
request-tag statement, the boundary's new conditioned deny on
`TagResource` and `UntagResource` for an untagged guardrail, the cdk-nag
reason and this file's R3 amended, a test in `tests/test_m09_platform.py`.
Of the notes: the observer's two unguarded reads **repaired**
(Engineering) and the sentence here corrected; the built guardrail now
**retained** with its version; `ListTagsForResource`'s condition key and
the construct's suppression key for an agent with `rules/` recorded under
Unsure above; the rest settled as read. The report, verbatim:

> Read: the diff 460990b...d3897ab (40 files)
>
> Security review, M09 PR 2 (#50). A report, never a ruling. Lines cited are the tree at d3897ab unless marked `patch:`.
>
> **1. Workflows**
>
> - NOTE. `permissions:` is set and minimal and unchanged. `deploy.yml:150` `permissions: {}`; `deploy-agent` at :485-487 `contents: read`, `id-token: write`. `evals.yml:186` `permissions: {}`; the eval job at :257-262 `contents: read`, `id-token: write`, `checks: read`, `actions: read`, `pull-requests: read`. The new steps add no permission. Settled. Security.
> - NOTE. No new `uses:`. Every third-party action in both files is pinned to a SHA (deploy.yml :499, :503, :510, :522, :527, :536, :567; evals.yml :269, :403, :466). Settled. Security.
> - NOTE. No `${{ }}` in a new `run:` line. The held-pin step (deploy.yml :559-565) uses `$NAME`, `$REPOSITORY`, `$COMMIT`, which are job env from the matrix (:493-497), as at M06; the stack-output step (:615-635) reads only `aws cloudformation describe-stacks` output, which the platform's construct wrote. evals.yml :529-532 passes `github.token` through `env:`, not into the line. Settled. Security.
> - NOTE. No `pull_request_target`. The evals job still runs only on push or a same-repo PR (evals.yml :254), so a fork never reaches OIDC or `github.token`. The agent repository is checked out at `matrix.commit` with `persist-credentials: false` (deploy.yml :503-508) and copied without `.git`/`.github` (:515-520), as before. Settled. Security.
> - NOTE. Does deploy.yml put the deploy role near agent code it did not before? No. The one new thing read while the deploy role's credentials are live is the held-pin check (:559-565), which runs `src.validate.agent evaluate` on the folder as data (`yaml.safe_load`, `src/validate/agent.py:169`; `agent_rules.load` is `yaml.safe_load`, `src/validate/agent_rules.py:70`). Synth now also parses `rules/*.yaml` from the agent folder (`infra/construct/governed_agent.py:834-844`) through the same loader. Nothing of the agent's executes. Settled. Security.
> - NOTE. `--held-guardrail` ordering: deploy.yml :559 sits after the registry claim (:543-552) and before ECR login (:567), the image push (:571) and `Deploy agentkeel-<name>` (:592). It is before anything touches the stack, and before the push. It is after `registry.py claim`, which writes the row's repository claim; that is the name claim, not the stack. `evaluate` returns 1 on any error (agent.py :289) and the step has `set -euo pipefail`, so a refused pin fails the job. `registry.py guardrail` prints an empty line when the row holds none (`scripts/registry.py:114`), and `--held-guardrail ""` becomes `held=None` (agent.py :271-274), so a placeholder is admitted only then (agent.py :151-153). Held as claimed, not yet fired: no agent with `rules/` has deployed. Security.
> - NOTE. The evals.yml observer steps are in the right blocks. `--read bucket` at :448-452 sits inside the `AWS_AUDIT_READ_ROLE_ARN` block (configured :403-407) and before the eval role is assumed (:466-469); `--read github,registry,guardrail` at :526-532 sits after it. Both carry `if: steps.current.outputs.measured_at == ''` like their neighbours. Settled. Security.
> - NOTE. "Both observer steps never fail the job" (`patch:1362-1363`, rulings/pr2-security.md) is true for a refused read: every AWS and GitHub read is caught and written (`scripts/observe_rules.py:217, :229, :254, :276-279`) and `main` returns 0 once the file is written (:289-304). It is not true for a malformed `milestones/M09/runs/f9_3_plant_run.yaml` or a corrupt `$RUNNER_TEMP/rules.json`: `run_file` (:86) and the `json.loads` at :299 are outside any try, there is no `continue-on-error`, so a YAML error in a Product-owned file fails the evals job. Settle: wrap those two reads, or change the sentence in the ruling to "a refused read never fails the job". Engineering (the script); Security (the sentence).
> - NOTE. The observer computes the baseline digest from `origin/main` via `git show` (observe_rules.py :150-156); evals.yml checks out with `fetch-depth: 0` (:272), so `origin/main` exists and the fallback to `HEAD` (the PR's own tree) is not taken in CI. `read_from` is written either way. Settled. Security.
> - NOTE. `infra/workflows.sha256` (`patch:899-907`) carries new hashes for deploy.yml and evals.yml. I cannot run a hash here; `make validate` holds it. Unverified by me. Engineering runs it; Security owns the file.
>
> **2. Can it be switched off from inside?**
>
> - NOTE. The held-pin refusal lives in deploy.yml only (`patch:34-45`); `platform-check.yml` cannot read the registry, so a head with a wrong pin passes the check and is refused at the deploy, after its merge. The ruling says so (`patch:1329-1334`). Anyone with write can edit deploy.yml or the bootstrap; what stops them is `ruling-cited` plus CODEOWNERS on `.github/workflows/**` and `infra/**` (Security), and `validate`'s hash of the workflows, whose file is itself a Security path in the same PR. The IAM narrowing takes a by-hand bootstrap deploy by Security (`patch:1354-1359`); no workflow can deploy it. So: anyone with write and a cited ruling, and nothing stops them but that gate. Stated plainly; nothing new in this PR changes it. Security.
>
> **3. IAM**
>
> - FINDING. The execution role can reach refagent's untagged guardrail in two calls, which the ruling says it cannot (`patch:1316-1317`: "refagent's and any other guardrail in the shared account stay out of reach"; `patch:1321`; the cdk-nag reason at `patch:636-638`). `infra/bootstrap/app.py:764-770` `MakeAnAgentsGuardrailOnlyWithItsTag` allows `bedrock:CreateGuardrail` **and `bedrock:TagResource`** on `guardrail/*` with only `Null aws:RequestTag/agentkeel:agent: false`. A `TagResource` call on refagent's guardrail (untagged, `tests/test_m09_platform.py:175`) with `agentkeel:agent=<anything>` in the request satisfies that condition. The deploy boundary does not deny it: `GUARDRAIL_ADMIN` (`app.py:140-146`) is `Create*Guardrail*`, `Update*Guardrail*`, `Delete*Guardrail*`, `Put*Guardrail*`, `GetGuardrail`, and `bedrock:TagResource` matches none; the flat deny at :436-443 names only `ListGuardrails`; the role's own deny at :778-785 names no bedrock action. Once the tag is on, `aws:ResourceTag` is non-null, the boundary's conditional deny (:449-455) no longer matches, and `ReadUpdateVersionAndRemoveATaggedAgentsGuardrailOnly` (:771-777) allows `UpdateGuardrail`, `DeleteGuardrail`, `CreateGuardrailVersion` on it. Who can drive it: only the execution role, which is a CloudFormation template in a stack the deploy role may deploy, so it takes a change to `infra/construct/**` or `deploy.yml` (Security paths) or a custom resource; it is not reachable from an agent repository, and no seeded case reads it. The test at `test_m09_platform.py:190-199` checks the two statements' conditions and does not read this. Settle: drop `bedrock:TagResource` from the RequestTag statement (CloudFormation passes tags in the CreateGuardrail request itself; the ResourceTag statement already carries `TagResource` for a tagged one), and add `bedrock:TagResource` and `bedrock:UntagResource` to the boundary's conditional deny, with a test that a `TagResource` on an untagged guardrail is denied. Note the shape was copied from `MakeAnAgentsKeyOnlyWithItsTag` (:735-738); refagent's key is held by its key policy (`NoPlatformRoleChangesThisKey`, :1263), a guardrail has no resource policy, so the copy is weaker here. Security.
> - NOTE. Does any grant widen beyond a guardrail tagged `agentkeel:agent`? Apart from the finding above, no. The boundary's conditional deny (:449-455) needs both `aws:RequestTag` and `aws:ResourceTag` null to fire, so `CreateGuardrail` with the tag in the request passes and every action on a tagged guardrail passes; both null (refagent's, or a create without the tag) is denied. The eval role's allow (:1044-1048) and its split deny (:1050-1056) match the ruling word for word. The agent boundary (:375-386) still carries `*GUARDRAIL_DENIED` unchanged, so no agent role touches any guardrail but Apply. `ListGuardrails` stays denied flat (:439). Held in the template (tests :178-210); not fired on a seeded case. Security.
> - NOTE. The deploy boundary's key-policy denies (`kms:PutKeyPolicy`, `kms:CreateGrant`, `kms:ScheduleKeyDeletion`, `kms:DisableKey`, :438) are unchanged; R4 holds as before. `iam:*`, `sts:AssumeRole`, `logs:Delete*`, `s3:PutBucketPolicy` stay in `DENY` (:151) for every role that uses it; only the eval role drops `bedrock:GetGuardrail` from the flat list and re-denies it conditionally (:1051-1056). The model-watch and envelope-row-put roles still take `DENY` whole (:1085, :1131). Settled. Security.
> - NOTE. Bedrock condition keys, as I recall the Service Authorization Reference for Amazon Bedrock: `CreateGuardrail` and `TagResource` take `aws:RequestTag/${TagKey}` and `aws:TagKeys`; `GetGuardrail`, `UpdateGuardrail`, `DeleteGuardrail`, `CreateGuardrailVersion`, `ApplyGuardrail`, `TagResource`, `UntagResource` take `aws:ResourceTag/${TagKey}`. I am not certain `ListTagsForResource` lists `aws:ResourceTag`; if it does not, the key is absent, `Null ... false` is unmet, and the execution role's `ListTagsForResource` (:773-774) is refused, which CloudFormation's read handler may need. The ruling's own Unsure (`patch:1371-1376`) names the first deploy as the reading; check that page before the by-hand bootstrap deploy. `Put*Guardrail*` (:140) matches no Bedrock action; harmless. Security.
> - NOTE. The placeholder pin is never on an IAM condition or a call. For an agent with `rules/`, `guardrail_arn`/`guardrail_version` are the built resource's tokens (`governed_agent.py:777-779`), the invoke condition and ApplyGuardrail use them (:795, :806), the runtime env uses them (:885-887), and `build answer --guardrail "$PIN"` takes the stack output (deploy.yml :619-647). The manifest pin is read only to refuse null and refagent's (:750-761). The `elif self.guardrail` branch (:780-783) would put the manifest pin on the condition if `_agent_guardrail` refused and synth went on; it does not, because `rules.refuse` feeds `IValidation.validate` (:592-604) and synth fails. Settled. Security.
> - NOTE. `CfnGuardrailVersion` is RETAIN (`governed_agent.py:875`); `CfnGuardrail` is not. On a stack delete the execution role may `DeleteGuardrail` a tagged guardrail (:771-777) and the retained version goes with it. Old envelopes name the pin, and the envelope, not the guardrail, is the evidence, so R5 is not touched; but "the one the record names, and old envelopes name, outlives it" (:874) is true of a rules change, not a stack delete. Settle: say so in the comment, or RETAIN the guardrail too. Security.
>
> **4. Network.** NOTE. No security group, VPC, endpoint or trust-policy change in the diff. Default-deny egress and the manifest allowlist are untouched. Settled. Security.
>
> **5. Evidence.** NOTE. No bucket policy, Object Lock, retention or key policy change. The answer record gains a `guardrail` field from the stack output; `agentkeel-audit-read` already reads `envelopes/agents/*`. Settled. Security.
>
> **6. cdk-nag**
>
> - NOTE. Bootstrap, `ExecutionRole/DefaultPolicy` gains one `applies_to`, `guardrail/*` (`patch:402`; `app.py:1579-1581`), reason at `app.py:1519-1524`: names CreateGuardrail/TagResource on `aws:RequestTag`, every other action on `aws:ResourceTag`, and the boundary. Specific, but its sentence "any other in this shared account are out of reach" is the sentence the FINDING above contradicts; amend it with the repair. Security.
> - NOTE. Bootstrap, `EvalRole/DefaultPolicy` gains `guardrail/*` (`patch:423`; `app.py:1598`), reason at :1547-1550: GetGuardrail, read only, tagged, refagent's denied. Specific. Security.
> - NOTE. Construct, `infra/construct/app.py:710-712`: the suppression key for an agent with `rules/` is `Resource::<Guardrail.GuardrailArn>:*` by logical id. The committed NagReport (`patch:682`) still shows refagent's id, because refagent has no `rules/`; the own-rules branch of that key has no committed report and `validate` has not exercised it. It will first be exercised at PR 3's synth of the fixture agent. Not fired. Security.
> - NOTE. No other suppression is added or removed; the reworded ones (`patch:634-638`, `patch:647-650`, `patch:725-728`) keep their SPEC/01 §6 citation. Security.
>
> **Unsure.** Whether `bedrock:ListTagsForResource` carries `aws:ResourceTag` (above). Security, by reading the SAR page before the by-hand deploy.
>
> BLOCK: 0 · FINDING: 1 · NOTE: 22

## The KMS keys from M08

`ce2d6f46` and `fcd9e973` (`milestones/M08/open.md` row 6, tagged
owner-check, scheduled for deletion 2026-10-09) read as gone by andaro74
in the KMS console, agent account, us-west-2, on 2026-10-11. Noted here;
no file in the repository reads it.

## What a reader can run

```
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py tests/test_construct.py -q   # the builder, the grants, the denies
make validate                                                                                   # cdk-nag, every stack: ok, reports equal
git diff 460990b...HEAD --stat -- .github/workflows infra                                       # this key's paths and nothing else under them
```
