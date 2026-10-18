---
# M10 PR 3 (#56), the repair. Engineering's key over the Engineering paths
# this PR touches: the caller reader's epoch and the tests that read each
# deploy-path repair. infra/** is Security's (pr3-security.md) and
# milestones/M10/** is Product's (pr3.md).
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/verdict/caller.py
  - tests/test_bootstrap.py
  - tests/test_m10_platform.py
  - tests/test_m10_readers.py
  - tests/test_containment_stacks.py
evidence:
  - SPEC/00-overview.md#8-M10
  - milestones/M10/README.md
  - milestones/M10/rulings/pr2-engineering.md
pr: 56
---

# Ruling: M10 PR 3, Engineering

Ruled by andaro74 as Engineering, 2026-10-17, as written.

## What this covers

- **The reader** (`src/verdict/caller.py`): an access-log epoch is read in
  seconds or milliseconds by its size. festival-desk's first live lines
  carry an HTTP API's `$context.requestTimeEpoch` in seconds; read as
  milliseconds every call dated to 1970-01-21, which would have broken
  F10.4's within-N reading and the observer's search window for the bypass
  record. PR 2's Unsure G named this as a reader repair in PR 3.
- **The tests**: each repair has a test that fails on PR 2's tree for the
  reason it names (the cold read ran them against `917601d`: 8 failed, 138
  passed; at this branch they pass). IAM's three policy quotas on every role
  the bootstrap makes; the door's grants read by resource, not by action
  name; the deletion policies; the subscriber role's trust and the
  destination's principal; the live line's epoch; and that the doored stack
  writes no Logs resource policy.
- **Nothing here decides row 10.** The run is read by PR 4's (SPEC/10 §5.1;
  milestones/M10/README.md). The four calls were made on 2026-10-18; their
  request ids enter the run file's `observed` in PR 4.

## Dispositions

| # | Disposition |
|---|---|
| F1 | Answered by pr3-security.md and pr3.md in this PR; the by-hand deploys before them are named there |
| F2 | Security's: accepted by name in pr3-security.md, with a test that the construct writes no Logs resource policy |
| F3 | Repaired (99e6807): the README states the deploy run's goldens as its log, and says F10.2 is PR 4's |
| N1 | The local name repaired (99e6807); the field's name `time_epoch_ms` stays, since renaming it moves the construct and the fixture for no reading; the 1 s truncation is inside N's 600 s |
| N2 | Carried: the quota test's measure holds for this template; a grant written as an intrinsic ARN could pass it and be refused |
| N3 | DeleteLogDelivery carried (pr3.md Unsure); the suppression that matched nothing removed (99e6807) |
| N4 | Carried: no test reads the observer's window; the reader's fix repairs it |
| N5 | Carried: the action lists are the guide's; a deploy is the only reader of completeness |
| N6 | The destination's policy now limits who may subscribe (security F3, 99e6807) |

## Cold review (verbatim)

> ## Cold read: M10 PR 3 (`917601d..m10-pr3`, head `0733c2c`)
>
> I read the 7 commits, the diff of 10 files, ledger row 10 (`milestones/README.md:70`) and `milestones/M10/README.md`. I did not read the PR description.
>
> **How I checked**
> - **Tests at head:** I ran the four test files you named at `0733c2c`: **146 passed**.
> - **Tests against PR 2's code:** I ran PR 3's four test files against PR 2's tree (`git archive 917601d` extracted into the scratchpad). **8 failed, 138 passed.** Every new or changed test fails there, each on the defect it names:
>   - quotas: `{'ExecutionRole605A040B': 12071}`
>   - pool `Retain` against `RetainExceptOnCreate`, twice
>   - stage needs the vended-delivery actions
>   - `'"*"' in set()`
>   - the reader returns `'1970-01-21T17:51:17Z'`
>   - the subscriber trust test
> - **Policy sizes:** I synthesised the bootstrap stack into the scratchpad. The execution role's inline default policy is 9,134 characters; the DoorGrants managed policy is 3,458.
>
> No change decides row 10. The row says the live run is read by "PR 4's if the deploy path needs a repair" (milestones/README.md:70), and the README defers the run to PR 4 at :169-171.
>
> No new writer or reader of envelopes. caller.py is the reader that `build` already called at PR 2. scripts/observe_caller.py:280 (not in this diff) calls `reader.iso_of_epoch_ms` only to set its trail-search window. That is a reader helper used inside an observer; it writes no verdict.
>
> | Test | Fails on 917601d with |
> |---|---|
> | tests/test_bootstrap.py:236 `test_every_role_fits_iams_policy_quotas` | `{'ExecutionRole605A040B': 12071}`, the figure IAM refused (README:179-184) |
> | tests/test_m10_platform.py:109 (changed) and :338 | `'Retain' == 'RetainExceptOnCreate'` |
> | tests/test_m10_platform.py:364 (Stage needs, :306-308) | vended-delivery actions not granted |
> | tests/test_m10_platform.py:394 | `'"*"' in set()` for DescribeLogGroups |
> | tests/test_m10_platform.py:402 | no `agentkeel-cfn-exec-door` managed policy |
> | tests/test_m10_readers.py:430 | `'1970-01-21T17:51:17Z' == '2026-10-17T22:54:34Z'` |
> | tests/test_containment_stacks.py:271 | SourceAccount a single account |
>
> ### BLOCK
>
> None.
>
> ### FINDING
>
> **F1. infra/** is in this diff with no ruling file from its seat.** Paths: infra/bootstrap/app.py, infra/construct/governed_agent.py, infra/security/app.py and the nag report (Security), and milestones/M10/README.md (Product). `git diff --stat 917601d...m10-pr3` adds nothing under milestones/M10/rulings/. The Repair detail says both stacks were already deployed from this branch before any ruling (README:225-226, 198-201, 241). This is the same "deploy on unsigned draft ruling" carry as M09. Clears when pr3-security.md (with the security-reviewer report) and Product's pr3 ruling are in this PR and ruled. Engineering's key cannot cover infra/**.
>
> **F2. `logs:PutResourcePolicy` on `*` for the CloudFormation execution role.** This is the account-wide CloudWatch Logs resource policy. It decides which services may write into which log groups, any log group, not only the door's. The deploy boundary denies `logs:Delete*` but not `logs:PutResourcePolicy`, so any template the execution role runs can now rewrite that policy. The grant is justified only by the guide's list. tests/test_m10_platform.py:306-308 mirrors the same list by hand, so no test checks that the grant is the minimum the stage needs. Security's call: keep it on `*`, or condition it.
>
> **F3. The Repair detail states F10.2's reading in prose before the run that measures it.** milestones/M10/README.md:233-235: "the goldens went through it as `platform` (GREEN, g-030 blocked)". The row's F10.2 is "g-030 ... 1 of 1" on festival-desk's answer record through the door. Here it is written from deploy run 39076739413, not from an envelope. PR 4's cell must cite the envelope, not this line. Reword it as a deploy-run observation or cite the envelope.
>
> ### NOTE
>
> **N1. Epoch by size, src/verdict/caller.py:101-116.** The cut-over `10**11` is sound; the two units overlap only for millisecond stamps before 1973 or second stamps after 5138. `"-"`, None, a decimal string and microseconds return None. `"0"` reads 1970-01-01, harmless. `timespec="seconds"` truncates milliseconds, so F10.4's `delivered - time` can be overstated by up to 1 s against N = 600 s. The local name `seconds` shadows the module function `seconds()` inside this function only. The field name `time_epoch_ms` is now wrong for the HTTP API that writes it.
>
> **N2. The quota test's measure.** "Intrinsics render shorter than they are written" holds for this template; the synthesised measure, 12,071 at 917601d, matched IAM's refusal exactly. It is not true in general: a `Ref` to a managed policy, or a `Fn::GetAtt …Arn`, renders longer. Headroom is 1,106 characters. A future grant written as an intrinsic ARN could pass this test and still be refused by IAM.
>
> **N3.** DeleteLogDelivery is deliberately left ungranted. Deleting a stage, or changing where it logs, may be refused, and so may retiring an agent with a door through scripts/retire_agent.py. No test or step exercises it yet. Name it in PR 4's carry list. The new APPLIES_TO entry for the destination ARN suppresses nothing. Harmless.
>
> **N4. scripts/observe_caller.py:280-284 (not in this diff).** At 917601d the live seconds-epoch lines would have dated to 1970, and the window would have walked roughly 20,000 days of trail prefixes. PR 3's reader fix repairs this as a side effect, but no test reads the observer's window.
>
> **N5. Hand-mirrored action lists.** tests/test_m10_platform.py copies the guide's action list. They prove the grant matches the list, not that the list is complete, which is how PR 2's gap passed. A deploy remains the only reader of completeness.
>
> **N6. The subscriber trust** now trusts Logs on behalf of both accounts, following the Logs guide's cross-account form. The destination's own access policy, not this trust, limits who may subscribe. This diff does not change it.
>
> BLOCK: 0 · FINDING: 3 · NOTE: 6
