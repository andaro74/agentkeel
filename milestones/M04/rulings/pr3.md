---
# M04 PR 3 (#27), the repair and the read's machinery. Product's key. One
# seat per file: pr3-threshold-owner.md (the two swap rulings), pr3-security.md
# (evals.yml), pr3-engineering.md (the code, with the cold review).
ruling: pr3
seat: Product
authorises:
  - SPEC/04-model-swap.md
  - milestones/README.md
  - milestones/M04/README.md
  - milestones/M04/runs/f4_swaps.yaml
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#4-falsifiers
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - milestones/M04/rulings/pr2.md
  - https://github.com/andaro74/agentkeel/pull/25
  - https://github.com/andaro74/agentkeel/pull/26
pr: 27
---

# Ruling: M04 PR 3, Product

Drafted by the session; the human rules as Product before the merge.

## 1. Why PR 3 is not the read

SPEC/04 §5.1 had PR 3's run read the swap PRs after their rulings were on
`main`, carried there by PR 2. PR 2 (#24) merged at 2026-09-27T20:18Z,
before the swap PRs ran (#25 and #26, opened 20:17Z, bot envelopes about
20:23Z), so neither their rulings nor `f4_swaps.yaml` joined it. A ruling
can reach `main` now only through PR 3, and PR 3's own run happens before
its merge. So **PR 3 is the repair and the read's machinery, and PR 4's
run is the read**, ruled by the human on 2026-09-27. The machinery is not
built in the last PR: it lands and runs here, where it reads the swaps as
they stand. This is the named P3 exception, moved one PR; the row's
expected results for the swaps are unchanged.

## 2. Recorded, not gated

Ruled by the human on 2026-09-27. As first written, `build` wrote `F4_1`
and `F4_2` as pass only when the seed test and the swap PR both passed.
The equivalent swap's first run regressed `g-005`, so `F4_2` would fail
on every envelope that read it: the reading PR could not merge, and left
on, every later PR would be RED for a result that is already the
finding. So the swap PRs are recorded in the envelope's `swaps`, the
Measured cell prints them, and nothing gates them. `F4_1` and `F4_2` stay
test-only witnesses, as the row already says. SPEC/04 §4, §5.1, §6 and
§7, and row 4, are amended to say so.

What this gives up: a later swap PR is not held to M04's two by any
check. It is held by its own envelope, as every pull request is:
a golden that passed and now fails is RED under any model (P7).

## 3. `g-005`: the first run decides F4.2

SPEC/04 §2 named Sonnet 4.5 equivalent before any run, and said that if
its run regressed a golden, F4.2 fires and is recorded as the finding,
with the label not moved. Its first run (#26, `9ff21d5`) regressed
`g-005` in both of its runs. **F4.2 fired there, and that stands**
(threshold-owner FINDING and cold review F2 on PR 3; drafted for the
human's ruling as Product). Nothing since touches the model, `g-005`, the
rights table or the candidate list, so a GREEN at PR 4's read would be a
difference between jobs, not a fix: it is recorded beside the first run,
and row 4 closes RED on F4.2 either way.

## 4. How PR 4's run is made to read

A run reuses an earlier envelope when nothing but prose changed
(`evals.yml`, "Is this tree already measured?"), and a close is mostly
prose (security-reviewer F3). PR 4 records the swaps' re-run envelopes
in `milestones/M04/runs/f4_swaps.yaml`, which is not prose, so its run
measures, and that run is the read.

## 5. What the cold review of PR 2 missed

The suite failed on any tree whose pin moved (nine tests on #25, ten on
#26), so both swap PRs' `checks` were red for a reason of their own:
F4.2's own wording. The swap PRs found it; the cold review of PR 2 and
the seat reports did not. Repaired first in this PR.
