---
# M06 PR 4 (#37), Engineering's key and the cold review, one file. Drafted
# from engineering-cold-reviewer's read of the diff. Product's file is
# pr4.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m06_seeds.py
evidence:
  - SPEC/00-overview.md#8-M06
  - milestones/README.md
  - milestones/M06/README.md
  - evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json
pr: 37
---

# Ruling: M06 PR 4, Engineering, with the cold review

DRAFT for andaro74 as Engineering. Not ruled until this line reads "Ruled by".

## What this authorises

- **`tests/test_m06_seeds.py`**: S2's strict `xfail` marker removed, in the
  commit that filled S2's run file (`245eb9b`). With `observed` filled the
  test passes, and a strict marker would fail it as XPASS. The test reads
  that the attempt was recorded, not F6.2: F6.2 is `build`'s, from the
  observer's lookup (`pr1-engineering.md` NOTE 1). S3's marker stays: S3
  was not attempted.

## The cold review

COLD_REVIEW
