---
# M04 PR 3 (#27), the Threshold Owner's key: the two swap rulings, which
# land on main here because PR 2 merged before they joined it. Product's
# file is rulings/pr3.md.
ruling: pr3-threshold-owner
seat: Threshold Owner
authorises:
  - milestones/M04/rulings/swap-breaking.md
  - milestones/M04/rulings/swap-equivalent.md
evidence:
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - SPEC/04-model-swap.md#8-controls-with-no-seeded-case-at-m04
  - milestones/M04/runs/f4_swaps.yaml
pr: 27
---

# Ruling: M04 PR 3, Threshold Owner

Drafted by the session; the human rules as Threshold Owner before the
merge.

The two swap rulings, `swap-breaking.md` (`pr: 25`) and
`swap-equivalent.md` (`pr: 26`), each authorise the swap PR's change to
`model` and record the `modelLifecycle` read for its model (SPEC/04 §8):
both ACTIVE, no `endOfLifeTime`, so each keeps `deprecated_after: null`.
Neither swap merges. Nothing in this PR moves a bar, the cap,
`pinned_roles` or refagent's own pin.
