---
adr: ADR-0005
title: The milestone video is recorded at the tag, not inside the close PR
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Product  # SPEC/00 §10.5, fourth bullet; §10.3's delivery sentence
amendments: 0
---

# ADR-0005 — The milestone video is recorded at the tag

## Context

SPEC/00 §10.5 says: "A milestone's close PR is not ruled ready without
its explainer page and video." §10.3 says the explainers are "delivered
at each milestone's close PR".

The M00 close PR carries the explainer page and not the video, and its
Watch line reads "pending, tag `m00`". The cold review of that PR found
the plain thing: a close that does not meet a SPEC line leaves the SPEC
line standing, and CLAUDE.md says SPEC/00 wins. Ruling the departure in
`milestones/M00/README.md` does not amend SPEC/00. This ADR does.

The rule as written cannot be met, for a reason that is not about
effort. §10.3 says the video "shows the plant going in, the gate firing,
and the ledger row being filled", and §10.2 says a recording is unedited
and carries "the commit and tag it was recorded at". The ledger row being
filled is a commit inside the close PR, and the tag is cut after the
close PR merges. A recording made before the merge cannot show the row on
`main` and cannot carry a tag that does not exist. Recording it, merging,
and re-recording to match is exactly the retake §10.2 forbids.

## Decision

1. **The explainer page is delivered in the close PR.** Unchanged. A
   close PR without its page is not ready.
2. **The video is recorded on `main`, after the merge and after
   `git tag mNN`,** and committed with the tag in its entry in
   `docs/video/README.md`. Until then the milestone's Watch line reads
   "pending, tag `mNN`".
3. **A milestone is not finished until the video is committed.** The
   ledger row and the tag come first, and the outstanding video is
   carried into the next milestone's `open.md` with Product's name on it
   and a date, like any other open item. It is not allowed to go quiet:
   an open video at the next milestone's close is a finding about this
   project.
4. SPEC/00 §10.5's fourth bullet is amended to say this.

## Consequences

- M00's video is item 27 of `milestones/M01/open.md`, Product, before
  M01 PR 1.
- The recording can now show what §10.3 asks for: the row filled on
  `main`, at the tag, in one unedited take.
- A RED milestone still gets its video, on the same terms. The finding on
  camera is the point (§10.2).
- This does not loosen §10.5's other three bullets. No document describes
  a control that has not fired on its seeded case; the quickstart is
  timed at M06 PR 3; recordings are evidence, not marketing.
