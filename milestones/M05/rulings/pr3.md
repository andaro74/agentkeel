---
# M05 PR 3, the repair and the read (SPEC/05 §5.1). Product's key. Engineering's is
# pr3-engineering.md (with the cold review); Security's pr3-security.md once the stand-in
# is removed.
ruling: pr3
seat: Product
authorises:
  - milestones/README.md
  - milestones/M05/**
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/M05/rulings/pr2.md
  - evals/history/388dbcf159813a4675f7afa4a40fa07828465624.json
pr: 32
---

# Ruling: M05 PR 3, Product

Drafted by the session, 2026-09-30. Not ruled.

## What this PR is

PR 3 of M05: 3 / 4. The read of S3, S4 and S7, attempted after PR 2's merge
deploy (the named P3 exception, ruled at PR 1), and the repair of what that
read finds. It changes nothing under `agents/refagent/**`, so its run
measures in the runtime that deploy made.

## Rulings

1. **S7 is attempted as written, and its expected reading is stated first**
   (ruled by the human as Product, with Security, 2026-09-30, option A;
   `e1a6bb2`). Under the deny-all, `server.py`'s table read is refused
   before any model call, so no model call can be recorded. F5.4 as
   restated reads a model call; no other call stands in for it, and the
   trail is not widened to record the table read. S7 reads unrecorded and
   not shown refused: a second finding for row 5, beside S1's.
2. **The run files record what the caller was answered, verbatim.** S3's
   is the Logs API's `AccessDeniedException`; the trail's record of it is
   `AccessDenied`. S7's model-call fields are empty; the answer is in
   `caller_answer`, which feeds no reading.

## The run that decides this ruling

Pending: the head and run that read S3, S4 and S7, written here before the
ruling line.
