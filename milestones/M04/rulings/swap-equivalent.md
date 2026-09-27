---
# The equivalent swap PR (#26), the Threshold Owner's key. Drafted by the
# session at M04 PR 3; the human rules as Threshold Owner. This file is on
# main through PR 3 (#27), so the swap PR's own checks find it.
ruling: swap-equivalent
seat: Threshold Owner
authorises:
  # model only: id, version and profile, to pinned_roles.m04_equivalent_swap; region and deprecated_after unchanged
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - SPEC/04-model-swap.md#10-not-in-m04
  - milestones/M04/runs/f4_swaps.yaml
  - https://github.com/andaro74/agentkeel/pull/26
pr: 26
---

# Ruling: the equivalent swap, #26

Drafted by the session; the human rules as Threshold Owner.

## What the pull request is

refagent's pin moved to `pinned_roles.m04_equivalent_swap`, Sonnet 4.5: `id` `anthropic.claude-sonnet-4-5-20250929-v1:0`,
`version` `20250929-v1:0`, `profile` `us.anthropic.claude-sonnet-4-5-20250929-v1:0`. `region` stays
`us-west-2` and `deprecated_after` stays null. Nothing else in the diff
against `main`, once `main` is merged into the branch; the CI-written
envelopes under `evals/history/` are the bot's. Opened from M04 PR 2's
head (`10926b2`) on 2026-09-27. **Never merged** (SPEC/04 §10): it is
closed unmerged once PR 4's run has read it.

A model id change is not a relaxation (SPEC/04 §10, ruling 3): the gate
measuring the swap is its control, and this file is its key.

## `modelLifecycle`, read for this swap (SPEC/04 §8)

`aws bedrock get-foundation-model --model-identifier anthropic.claude-sonnet-4-5-20250929-v1:0`, us-west-2,
read by the session with the human's credentials at 2026-09-27T21:07Z:
`status: ACTIVE`, `startOfLifeTime` 2025-09-29T00:00:00Z, no `endOfLifeTime`. So
`deprecated_after: null` is a reading, not a gap. The same at
2026-09-27T21:23Z in us-east-1 and us-east-2, the profile's other two
regions (threshold-owner note on PR 3).

## Stated before its run (F4.2), in SPEC/04 §2 and §7 at PR 1

GREEN, with every required check green and A-vs-A zero diff (SPEC/04 §7). Named equivalent before any run; if its run regresses a golden, F4.2 fires and that is the finding, and the label is not moved (SPEC/04 §2).

## Its first run

Envelope `9ff21d5` (bot commit `131dc22`, run 36347490922): RED. Ordinary
8/9: `g-005` regressed the same way in both of its runs (available,
clause `EM-1`, no embargo; 01:30 UTC on 14 May is still 13 May in São
Paulo, before the embargo lifts). A-vs-A zero diff. **F4.2 fired on this
run, and it stands** (`rulings/pr3.md` §3); the label is not moved.
Its other red checks were the suite's, repaired at PR 3.
