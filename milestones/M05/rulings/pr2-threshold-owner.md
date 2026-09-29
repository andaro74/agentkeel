---
# M05 PR 2, the Threshold Owner's key: N added to thresholds.yaml before
# its reader (SPEC/05 §2, §6; finding 11 on M05 PR 1; open.md row 10).
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md#2-words-used-here
  - milestones/M05/feasibility.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
pr: 31
---

# Ruling: M05 PR 2, Threshold Owner

Drafted by the session; the human rules as Threshold Owner before the merge.

## N

`detection.max_seconds: 600`, `relaxes: up`, in `thresholds.yaml`, in its
own commit before any code reads it. R10's figure, as SPEC/05 §2 states
it. Adding a bar is not a relaxation (ADR-0009): one key. Moving it up
later is two.

Who reads it: `verdict.build` writes each attempt's latency and
`alarm_latency_s` (the largest), and the ledger's row 5 reading of
`containment` (`gate.containment_misses`) reads N **at the envelope's
commit**, as the cap and the relative bars are read. An attempt whose
record is later than N makes row 5's cell RED; it gates no pull request
(SPEC/05 §4).

## Unsure C, answered by the run, not here

Whether 600 s holds for flow logs is this PR's reading, not a ruling.
CloudTrail delivers to S3 in about five minutes on average, with no
guarantee; flow logs publish about every five minutes even at a one-minute
aggregation. If S1's record lands later than 600 s after the flow record's
`start`, that is the finding, recorded in row 5, and the bar is not moved
to meet it (SPEC/05 §2, note 3).

## The report, and what came of it

`threshold-owner` read the diff `5a5720e...27f2678`: 0 BLOCK, 2 FINDING,
10 NOTE, verbatim in the PR body. No diff to `thresholds.yaml` proposed.
Note 12 checked by git: `a4e8922` holds `thresholds.yaml` and this file
alone, and is an ancestor of `2663fa2`, the first commit that reads N.
F7 (N read at the commit, untested) and F8 (build's N never compared
with the commit's) are Engineering's, repaired at `ec6747b`
(`rulings/pr2-engineering.md`).
