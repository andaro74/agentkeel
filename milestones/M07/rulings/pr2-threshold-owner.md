---
# M07 PR 2 (to open as #39), the Threshold Owner's key. Drafted before PR
# 2's first code commit, from milestones/M07/runs/pr2_reads.md and the two
# runs of M07 PR 1. It moves no existing bar.
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/runs/pr2_reads.md
  - milestones/M07/runs/model_lifecycle_2026-10-02.json
  - milestones/M07/runs/pr1_second_run.yaml
  - milestones/M07/runs/f7_3_rollback.yaml
  - evals/history/9f2ce07c5499e245f34f7117cb928317164af437.json
  - evals/history/0f4b72ae8028b92d82b191391fb517f362c91c48.json
pr: 39
---

# Ruling: M07 PR 2, Threshold Owner

DRAFT for andaro74 as Threshold Owner. Not ruled until this line reads "Ruled by".

Each item is a recommendation with its alternative.

## Made on 2026-10-02, before any PR 2 code

andaro74, as Threshold Owner, ruled every item of this file as its
recommended option on 2026-10-02 ("as proposed"), before PR 2's first
code commit (`16d9f84` is the last commit before it). Recorded here by
the session. The line above stays a draft until the seat changes it at
the end of the PR, as in PR 1. No alternative was taken.

| Item | As ruled, 2026-10-02 |
|---|---|
| 1 | Three new bars under `upgrade:`: `arrive_max_seconds` 4,500, `deploy_max_seconds` 3,600, `retire_max_seconds` 3,600, each `relaxes: up` |
| 2 | The p95 bar stays at 2.0. One stated second run is allowed only when the diff touches nothing the agent runs. A swap never gets one, but for a revert RED on `F4_4` alone |
| 3 | The swap candidate is Haiku 4.5. If its revert is RED on a regressed golden, or RED twice, refagent stays on Haiku 4.5 until a pin change passes, and F7.3 is read on the fallback |
| 4 | `model-watch` writes `deprecated_after` from Bedrock and opens nothing to set a null to null; a date moved later or cleared with the model unchanged is two keys |

## 1. Three new bars under `upgrade:` (Unsure I)

Added before any attempt; adding a bar is not a relaxation (ADR-0009).
Each `relaxes: up`.

| Bar | Value | What it times |
|---|---|---|
| `upgrade.arrive_max_seconds` | 4,500 | the platform's pull request's `created_at` after the trigger: one 15-minute schedule period plus an hour |
| `upgrade.deploy_max_seconds` | 3,600 | the deploy run completed after a merge |
| `upgrade.retire_max_seconds` | 3,600 | `DeleteAgentRuntime` in CloudTrail after the retirement pull request's merge |

Read by `build` into `upgrade` and by row 7's reading; they gate no pull
request. GitHub may delay a scheduled run; a miss is the finding, not a
bar to move. A two-key test covers these three and
`quickstart.max_seconds` (`open.md` row 23).

## 2. The p95 bar (Unsure Q)

M07 PR 1 went RED on `F4_4` at 14,281 ms (2.06 times the incumbent's
median, 6,946 ms) and GREEN 30 minutes later at 5,830 ms, on a diff that
changes nothing refagent runs. With about nineteen answers in a run, p95
is close to the slowest single call.

- **Recommended: the bar stays at 2.0 and the reading stays as it is.
  What changes is the rule for a miss**, written into SPEC/04 §2 by
  Product: when `F4_4` alone fails on a pull request whose diff touches
  nothing the agent runs (`agents/`, `src/agent/`, `infra/construct/`,
  the pin, the guardrail, `rules/`, `data/`), one second run may be made,
  stated before in a run file and pushed first. Both envelopes stay; the
  second rules. A swap pull request never gets a second run: its p95 is
  the thing under test.
- **Alternative (a): read p95 over both A-vs-A runs** where A-vs-A runs,
  about twice the answers. Changes what the number means, so every past
  envelope's median is on a different basis; a new bar, not this one
  moved.
- **Alternative (b): raise `p95_ratio_max`.** A relaxation: two keys. Not
  recommended; the miss was one slow call, and a higher bar would also
  pass a slow model.

## 3. The swap candidate, and the path back (R6; Unsure G)

Read 2026-10-02: Haiku 4.5 is ACTIVE with no end-of-life date, its
profile ACTIVE, and the eval role may already invoke it. refagent's pin
is ACTIVE with no end-of-life date.

- **The candidate stays `pinned_roles.m04_cheaper_swap`, Haiku 4.5.** Its
  verdict is not stated: it has never been run against the goldens.
- **If the swap's envelope is GREEN it is merged, then reverted.** The
  revert's pull request is a pin move the M04 gate rules against the
  incumbent at its merge-base, which is then Haiku 4.5. **Stated before:**
  the revert returns to Sonnet 4.6, whose envelopes are the long history;
  `F4_4`'s median for it is read over Sonnet 4.6's envelopes in that
  mode, so the revert is expected GREEN.
- **If the revert's envelope is RED** (recommended, to be named in
  `runs/f7_3_rollback.yaml` before the swap is merged). A RED revert
  cannot merge: `evals` is required and nobody can bypass it. So:
  - RED on `F4_4` alone: one second run of the revert is allowed, stated
    before and pushed first. The revert restores the incumbent of record,
    and its p95 is not what the swap tested. This is the one exception to
    item 2's "a swap never gets a second run".
  - RED on a regressed golden, or RED twice: refagent stays on Haiku 4.5,
    which the gate passed, until a pin pull request is GREEN. That is the
    finding. F7.3 is then read on the fallback, owner-check's platform
    upgrade reverted, and `upgrade.taken` stays under 3.
  No pin is moved by hand, and no re-point of the runtime is made.
- **Row 58** (`open.md`): the first `main` envelope after the merged swap
  is recorded as read, whatever `F4_4` says.
- **Alternative: skip the merge.** The swap is opened and ruled, never
  merged; the model upgrade is not taken (`upgrade.taken` under 3) and
  F7.3 is read on owner-check's platform upgrade alone. Less risk to
  refagent; row 7 RED on `taken` by choice.

## 4. `deprecated_after` from Bedrock (`open.md` row 65)

`model-watch` writes it from `modelLifecycle.endOfLifeTime`. Today it has
nothing to write for refagent. It opens no pull request to set a null to
null. Moving the date later, or clearing it, with the model unchanged is
two keys (ADR-0009 amendment 1), whoever opens the pull request.

## 5. The threshold-owner review, and what was done

Read on the diff `a2c5a61...1b376a3`, before the pull request was
opened: BLOCK 0, FINDING 6, NOTE 13. The report is in the pull request's
body, verbatim.

| # | Finding | Status |
|---|---|---|
| F1 | `two-key` does not read `deprecated_after`, and ADR-0009 amendment 1 says it does from M04 PR 2 | **Open, the seat's.** Confirmed: `grep -rn deprecated src/gates` finds nothing. Item 4's "is two keys" is then true by rule and read by no gate. `scripts/model_watch.py` now says so, and its own refusal is what holds the platform. Recommended: the reader and a seeded case in PR 3 (Engineering builds), before model-watch first runs |
| F2 | Item 3's "the revert is expected GREEN" names the wrong median | **The expectation is withdrawn** in `runs/f7_3_rollback.yaml`, from the code: the revert's Sonnet 4.6 p95 is held to 2.0 times the median of Haiku 4.5's one or two envelopes in that mode. The revert's verdict is not stated; the number is written once the swap's envelope exists and before the revert opens. **Item 3's own sentence above is left as ruled and is wrong on this point; the seat's to restate.** What follows a RED revert is as ruled |
| F3 | This file reads DRAFT | The seat's line, at the end of the PR |
| F4 | The "never later" guard was skipped for a date that is not a string | **Repaired** (`b3196d6`): refused in `plan` and in the keyed job, with a test on an unquoted date |
| F5 | A swap leaves the old model's `deprecated_after` in place | **Open, the seat's.** Moot today: refagent's is null. Recommended: a swap also writes null, ruled before any pin carries a date |
| F6 | The gate did not hold `deploy_max_seconds` again | **Repaired** (`ccb2be8`): each upgrade's `deployed_s` is kept in the envelope and the gate holds it to the bar at the envelope's commit |
| N1 to N13 | Notes | N12: the comment in `thresholds.yaml` is corrected (15 minutes for the platform upgrade, 10 for the retire job, daily for model-watch); no value moves. N4: `runs/pr2_expected.md` now says which envelope rules if the head moves. N5 (the rule's list omits the workflows and build) and N9 (the manifest's stale judge comment) are the seat's, not changed here. N13: model-watch's `CANDIDATE_FILE` and `RULINGS` are fixed to M07; after tag `m07` its daily run would draft into a closed milestone; to M08's open list |

## What a reader can run

```
grep -rn deprecated src/gates                                                                    # nothing
uv run pytest -q tests/test_m07_platform.py -k "quoted or keyed_jobs_own"
uv run pytest -q tests/test_m07_envelope.py -k "counts_each_kind"
python -c "import json;[print(m['modelId'],m['modelLifecycle']) for m in json.load(open('milestones/M07/runs/model_lifecycle_2026-10-02.json'))]"
python -c "import json;print(json.load(open('evals/history/9f2ce07c5499e245f34f7117cb928317164af437.json'))['p95_ms'])"   # 14281
python -c "import json;print(json.load(open('evals/history/0f4b72ae8028b92d82b191391fb517f362c91c48.json'))['p95_ms'])"   # 5830
grep -n "anthropic.claude-haiku-4-5" infra/bootstrap/app.py
```
