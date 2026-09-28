---
# M04's sign-off (#29): not a milestone PR. Product's key. It carries the
# human's ruling lines and signatures that #28 was merged without.
ruling: signoff
seat: Product
authorises:
  - milestones/README.md
  - milestones/M04/attestations.md
  - milestones/M04/rulings/pr4.md
  - milestones/M04/rulings/pr4-engineering.md
  - milestones/M04/rulings/signoff.md
evidence:
  - SPEC/00-overview.md#8-M04
  - milestones/M04/rulings/pr4.md
  - https://github.com/andaro74/agentkeel/pull/28
pr: 29
---

# Ruling: M04 sign-off, Product

Ruled by andaro74 as Product, 2026-09-27, before this file was written:
a sign-off PR, not counted against M04's cap.

## What happened

M04 PR 4 (#28) merged as `c3d25ec` at head `feff1f6`, with `pr4.md` and
`pr4-engineering.md` still reading "Drafted by the session" and the five
lines of `attestations.md` unsigned. The human had ruled both files as
written and signed the five lines on 2026-09-27, but the commit carrying
that was never made; it was found when `git checkout main` refused to
overwrite the three edited files. `m04` was not tagged, as
`attestations.md` requires: an unsigned line is a milestone that is not
tagged.

## What this PR is

The three files as the human edited them, and nothing else of M04:

- `pr4.md`: "Drafted by the session; the human rules as Product before
  the merge." becomes "Ruled by andaro74 as Product, 2026-09-27, as
  written."
- `pr4-engineering.md`: the same line, as Engineering.
- `attestations.md`: the five signature lines, `andaro74`, 2026-09-27.

No ruling's content, no number, no path it authorises and no cell
changes. `main` takes a change only through a pull request, and
`attestations.md` allows signing "on `main` before the tag", so this is
that pull request.

## Why it is not counted

It adds nothing to M04's claim, its measurement or its prose: row 4's
Measured cell, State and PRs cell are as #28 merged them, RED, 4 / 4.
It is uncounted as the adoption PR (#1) is, and the ledger says so
beside that line. It is not a precedent for any later milestone: from
M05 the close PR's attestations are signed, and its rulings ruled, in a
commit on the close branch before the merge, and a close that merges
unsigned is a finding.

## Finding

The close merged before its rulings were ruled. Nothing mechanical
stopped it: `cold-review-ruling` and `ruling-cited` read that a ruling
file with the PR's number exists, not that it says "Ruled". Carried to
`milestones/M05/open.md` when M05 opens (Engineering, Product: a gate,
or a `/close-milestone` step, that refuses a draft ruling at merge).
