---
# M08 PR 1 (#45), the plant. Product's key. One seat per file:
# Engineering's is pr1-engineering.md (the seeds, plants.py, the tests);
# Security's is pr1-security.md (the CODEOWNERS line, incident-responder's
# prompt, and R5's second key). ADR-0013 and the SPEC/00 amendments are on
# Product paths.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/08-game-day-drill.md
  - docs/adr/ADR-0013-m08-builds-no-control.md
  - docs/milestones/M08.md
  - docs/milestones/M07.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M07.mp4
  - docs/video/readbacks/M07-timed-run.mp4
  - milestones/README.md
  - milestones/M08/**
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md
  - milestones/M08/feasibility.md
  - milestones/M08/open.md
  - milestones/M08/runs/security_stack_hash.md
  - docs/adr/ADR-0013-m08-builds-no-control.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 45
---

# Ruling: M08 PR 1, Product

Ruled by andaro74 as Product, 2026-10-04, as written.

## What this PR is

PR 1 of M08, the plant: 1 / 4. M07 is closed (RED, tag `m07` on
`ddfa684`). SPEC/08 first (`142cd53`), reviewed by
`product-spec-reviewer` (2 BLOCK, 12 FINDING, 2 NOTE; `feasibility.md`
§1), the BLOCKs and four findings ruled as a diff, SPEC/08 revised
(`fa144cf`), SPEC/00 amended (`3daefb0`, `27655ad`), ADR-0013 and
`incident-responder` (`2a3a636`), the seeds (`e5266cc`). M07's two
recordings (`de2417f`) and the security account's hash (`ac16d0e`). It
builds no reader, no control, no workflow, no stack, no bar, no golden,
no rule and no manifest field, and makes no grant and no attempt.

## Rulings

The decisions this PR rests on are recorded in `feasibility.md` §2 (the
`product-spec-reviewer` report's dispositions, each with its seat and
what would undo it) and §2.5 (the `incident-responder` report). This
file carries Product's key over the Product paths above; the two BLOCKs
and the four findings that touch row 8 or SPEC/00 were put to the human
as a diff and answered "go ahead with your recommendations"; the rest
were taken on the session's recommendation under the M08 decision rule
(`milestones/M08/open.md` lines 12–19) and recorded, not made, here.

1. **No new control** (ADR-0013). M08 builds the adversary and the
   instrument; every control the drill tests was built at M01–M07. A
   defect found in one of them is that milestone's finding, repaired on
   M08 PR 3 only when a run cannot be made without it.
2. **The two known misses stay in the count.** Refused 4 of 6, recorded
   5 of 6 are the stated expected readings (SPEC/08 §7); row 8 is
   expected to close RED. Naming a2 or a3 as a gap outside the count
   would make GREEN reachable, which is the bend.
3. **The plain sentence is not reworded** (§10.3 row 08), and the
   explainer carries the expected miss beside it (SPEC/00 §10.5 is not
   broken: the sentence is the claim at open, and the draft says which
   parts are expected not to hold).
4. **R5: seven years is not set in this project** (two keys; the second
   is `pr1-security.md`). The lock stays COMPLIANCE, one day. A longer
   lock on a shared bucket cannot be undone by anyone, and nothing M08
   measures needs it.
5. **M08's own video** is ruled at M08's close under a second amendment
   to ADR-0005, since M08 has no next milestone's PR 1 to carry it.

## Unsure, each with its seat and when

| # | Item | Seat | By |
|---|---|---|---|
| A | The hostile copy's deploy may fail or answer oddly for the missing `kms` endpoint; NOTE 2 rests on no resource using the agent key. If it does, a1 is restated with another endpoint before run 1 is counted | Product; Security | before run 1 |
| B | F8.5's hazard: the deny-all may refuse the agent before any call reaches the trail (M05's S7), so F8.5 may read unread; the measurement decides | Security; Product | at run 1 |
| C | Whether a1's flow record arrives within N: no `REJECT` has ever been seen in this VPC and flow-log delivery was never measured (`open.md` row 55) | Threshold Owner | at run 1 |
| D | The drill's records' prefix: ride `agents/drill-agent/` and `envelopes/agents/drill-agent/`, or a prefix of their own (proposed: as any agent's) | Security | before PR 2 |
| E | The cap. PR 2 carries the reader, the runbook and run 1; PR 3 carries runs 2 and 3, a merge-and-deploy through `main`, and the cold review's repairs. The second P3 exception (run 3 read by PR 4's run) is named at open so it is not found at PR 3 | Product | PR 3 |
| F | The one-day lock lapses before PR 4 reads the records; F8.4 reads "a retention was set", and the explainer says the lock has lapsed (a consequence of R5, not a reason to reopen it) | Product; Security | at the close |

## What a reader can run

See `milestones/M08/README.md`, "What a reader can run".
