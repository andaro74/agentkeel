---
# M05 PR 3, Engineering's key and the cold review. Product's file is rulings/pr3.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_m05_seeds.py
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/README.md
  - milestones/M05/README.md
pr: 32
---

# Ruling: M05 PR 3, Engineering, with the cold review

Drafted by the session, 2026-09-30. Not ruled; the cold review is pending.

## What changed

- `tests/test_m05_seeds.py`: `denied()` reads `AccessDeniedException`, the
  answer the JSON-protocol APIs give (CloudWatch Logs, S3's attempt), as
  the refusal S3 and IAM call `AccessDenied`. It reads the human's file;
  `containment.py`, which reads the trail, is unchanged. S3's marker is off.
  S7's stays, with the finding as its reason (`rulings/pr3.md` ruling 1).

## The run that decides this ruling

Pending.
