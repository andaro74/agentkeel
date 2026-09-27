---
# The breaking swap PR (#25), the Threshold Owner's key. Drafted by the
# session at M04 PR 3; the human rules as Threshold Owner. This file is on
# main through PR 3 (#27), so the swap PR's own checks find it.
ruling: swap-breaking
seat: Threshold Owner
authorises:
  # model only: id, version and profile, to pinned_roles.m04_breaking_swap; region and deprecated_after unchanged
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - SPEC/04-model-swap.md#10-not-in-m04
  - milestones/M04/runs/f4_swaps.yaml
  - https://github.com/andaro74/agentkeel/pull/25
pr: 25
---

# Ruling: the breaking swap, #25

Drafted by the session; the human rules as Threshold Owner.

## What the pull request is

refagent's pin moved to `pinned_roles.m04_breaking_swap`, Llama 3.1 8B: `id` `meta.llama3-1-8b-instruct-v1:0`,
`version` `v1:0`, `profile` `us.meta.llama3-1-8b-instruct-v1:0`. `region` stays
`us-west-2` and `deprecated_after` stays null. Nothing else in the diff
against `main`, once `main` is merged into the branch; the CI-written
envelopes under `evals/history/` are the bot's. Opened from M04 PR 2's
head (`10926b2`) on 2026-09-27. **Never merged** (SPEC/04 §10): it is
closed unmerged once PR 4's run has read it.

A model id change is not a relaxation (SPEC/04 §10, ruling 3): the gate
measuring the swap is its control, and this file is its key.

## `modelLifecycle`, read for this swap (SPEC/04 §8)

`aws bedrock get-foundation-model --model-identifier meta.llama3-1-8b-instruct-v1:0`, us-west-2,
read by the session with the human's credentials at 2026-09-27T21:07Z:
`status: ACTIVE`, `startOfLifeTime` 2024-07-23T08:00:00Z, no `endOfLifeTime`. So
`deprecated_after: null` is a reading, not a gap.

## Stated before its run (F4.1)

RED, with at least one citing golden regressed, ungrounded or with wrong fields, and none of REJECTED, an access error or the cost cap (SPEC/04 §7).
