---
# The ids pull request (#42), Product: the fourth pull request of M07,
# so that the close is a fifth and M07 closes RED by the cap's rule.
ruling: grant-ids
seat: Product
authorises:
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/rulings/grant-ids.md
  - milestones/M07/rulings/grant-ids-security.md
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/runs/pr2_by_hand.md
  - milestones/M07/runs/pr4_expected.md
pr: 42
---

# Ruling: the ids pull request, Product

Ruled by andaro74 as Product, 2026-10-03, as written.

Dates in this file are UTC.

## What this pull request is

Two ids in the grant file (Security's ruling, `grant-ids-security.md`),
the ledger's "PRs used / cap" cell for row 7 moved from 3 / 4 to 4 / 4
with the note that the close is a fifth, and the M07 README's section
saying why. Nothing measured changes under `milestones/`: no `.yaml` or `.json`
there, no reader, no seed. The grant file is the input every keyed
job's reader compares GitHub against (cold review N4): this changes
the measurement's input, not its reader, and the first keyed run after
the merge is the first live comparison with a non-null id.

## Why a fifth pull request, and why that is RED

CLAUDE.md: "A milestone may close in three PRs; never in five. A fifth
PR is a RED close with the finding as the result. Do not propose a cap
raise; write the finding." The finding: the ids were to reach `main` in
PR 3 (`runs/pr2_by_hand.md` A4), the Apps were made after PR 3 merged,
and every attempt left (S1, the swap, the retirement, and the relaxation
behind S1) needs an App whose id is on `main`. The branch for PR 4 is
the close and cannot merge before the attempts it records. Product chose
on 2026-10-03 to spend the cap on the ids and make the attempts in M07,
over carrying them to M08 with F7.1 to F7.5 unread. Both are RED; this
one measures more. No cap raise is proposed.

## What stands

- Row 7 was already expected to close RED on F7.0 (`rulings/pr3.md`).
  The close's ruling names both reasons.
- The close, PR 4 by name and the fifth by count, is opened from
  `m07-pr4` after the attempts; `/close-milestone` writes the measured
  cell from that run's envelope, and the cap cell reads `5 / 4`.
- `make validate` (20 checks) and `make ledger` (exit 0) pass on the
  cap cell's new form (cold review N2).

## To falsify

M07's pull requests inside the cap are #38 (PR 1), #39 (PR 2), #40
(PR 3) and this one, #42 (#41 is the same content, closed unmerged for its author); `model-watch`'s swap and revert, when they
come, are outside it by row 7's own text. `gh pr view <n> --repo
andaro74/agentkeel --json title,mergedAt` on each: if one of the four
is not merged with `M07` in its title, or a fifth inside the cap merged
before the close, the count here is wrong.
