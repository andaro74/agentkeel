---
# M08 PR 2, Product's key over the Product path this PR touches:
# docs/developer/incident.md, the incident runbook, committed from
# incident-responder's draft on #45 (SPEC/08 §6; §10 amendment 2, which moved
# it from PR 4 to PR 2 because run 1's attach follows it). It is a document,
# not a reading, and gates nothing. Engineering's file (with the cold review)
# is rulings/pr2-engineering.md; Security's is rulings/pr2-security.md.
ruling: pr2
seat: Product
authorises:
  - docs/developer/incident.md
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md
  - milestones/M08/feasibility.md
pr: 46
---

# Ruling: M08 PR 2, Product

Ruled by andaro74 as Product, 2026-10-04, as written.

## What this covers

**`docs/developer/incident.md`** — the on-call runbook, four steps: detect,
quarantine, forensics, restore. Committed by Product from `incident-responder`'s
draft on #45 (feasibility.md §2.5; SPEC/00 §5.1 "owns incident.md" read as
"drafts", the specialist drafts and the seat commits). It carries the three
findings `incident-responder` applied to SPEC/08:

- the quarantine lookup names the **drill-agent** stack, not refagent (F1);
- the **M05 S7 hazard** caveat: under the deny-all the runtime may not start,
  so no refused call reaches the trail and F8.5 reads unread (F2);
- run 1's **evidence** (F8.4) is read at PR 3's run, after the detach, not at
  PR 2's (F3).

It describes no control as working that has not fired, and names the one-day
lock's lapse (SPEC/08 §8): an expired lock is not called a protection.

## What it does not do

It builds no control (ADR-0013) and is read by no check (`make validate`'s
twenty checks do not read it). It is followed by hand at run 1; PR 4 fills its
evidence paths with what the runs left.

## Unsure

- None. The runbook is incident-responder's draft committed as agreed; its
  commands are the ones already in `infra/audit/README.md` with the drill-agent
  stack substituted (SPEC/08 §2).
