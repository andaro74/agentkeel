---
# M08 PR 4, the close — Product. Copies the Measured cell from the
# CI-written envelope of this PR's evals run, fills the explainer's "What
# happened", writes the attestations, records every finding's and Unsure
# item's home (there is no M09 — M08 is the last milestone, so items that
# would carry forward are named as standing findings here), commits the
# game-day recording under LFS (the ADR-0005 amendment 2 for the last
# milestone), and tags m08 after the merge.
#
# This PR also carries a repair discovered at the close: PR 3's observed
# blocks named the drill's lookup keys in a shape observe_drill does not
# read (run 3 had no top-level answer_key, so the observer listed the whole
# bucket and the audit-read role denied it — readable:false, every run
# "not made"). The three observed blocks are corrected to the schema here;
# this PR's evals run re-observes and the envelope's drill field then carries
# the real readings. No infra, no control, no change to what was measured.
ruling: pr4
seat: Product
authorises:
  - milestones/M08/runs/drill_run1.yaml
  - milestones/M08/runs/drill_run2.yaml
  - milestones/M08/runs/drill_run3.yaml
  - milestones/README.md
  - milestones/M08/README.md
  - docs/milestones/M08.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M08.mp4
  - milestones/M08/attestations.md
  - milestones/M08/rulings/pr4.md
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md#5-the-seeded-cases
  - milestones/M08/rulings/pr3.md
  - milestones/M08/rulings/pr3-engineering.md
  - milestones/M08/rulings/pr3-security.md
  # The envelope and run URL of this PR's evals run are filled once it lands.
pr: 48
---

# Ruling: M08 PR 4, the close — DRAFT

To be ruled by andaro74 as Product.

## What this closes

Row 8 closes **RED**, as expected at open (SPEC/08 §7). The Measured cell is
copied from this PR's CI envelope's `drill` field (filled below once the run
lands), not retyped.

## The observed-block repair (discovered at the close)

PR 3's `observed:` blocks recorded the readings for humans but named the
lookup keys in a shape `observe_drill` does not read: run 3 had no top-level
`answer_key`, so the observer called `bucket.objects("")` — a whole-bucket
list — which the `agentkeel-audit-read` role denies (it allows `s3:ListBucket`
only on `READ_PREFIXES`). That `AccessDenied` threw and set the whole
observation `readable:false`, so the merged envelope `b48e279` read every run
"not made". The three blocks are corrected to the schema `observe_drill`
reads (top-level `answer_key`/`eni`/`destination`/`request_id`; `request_id`
singular for a5), keeping every human-readable finding. Nothing about what
was measured changes — the records already existed; the observer can now read
them. This PR's evals run re-observes and the envelope carries the readings.

## Findings — each with a home (no M09; M08 is the last milestone)

Filled in the close detail of `milestones/M08/README.md` and summarised here
once the envelope lands. Every M08 finding (feasibility, the three rulings,
the cold review) is named there with the seat and the standing it has after
the project stops building.

## Unsure — ruled here or named standing

Every Unsure item from the M08 PR bodies is ruled here (there is no
`milestones/M09/open.md` to move it to). Listed in the close detail.

## What a reader can run

```
make ledger              # row 8 RED, Measured from this PR's envelope
make validate            # ok
make ledger-plain        # rewrites docs/milestones/README.md
git show m08             # the tag, after the merge
git lfs ls-files | grep M08.mp4
```
