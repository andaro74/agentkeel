---
# M05 PR 3, Engineering's key and the cold review of the repair and the read. Drafted by
# engineering-cold-reviewer from the diff 59f06c0...335f276 and row 5 only; repaired and
# completed by the session. Product's file is rulings/pr3.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - tests/test_m05_seeds.py
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/README.md
  - milestones/M05/README.md
  - milestones/M05/runs/f5_3_logs.yaml
  - milestones/M05/runs/f5_4_chain.yaml
  - milestones/M05/runs/f5_7_quarantine.yaml
pr: 32
---

# Ruling: M05 PR 3, Engineering, with the cold review

Drafted by the session, 2026-09-30. Not ruled.

## What changed

`tests/test_m05_seeds.py`: S3's test takes `AccessDeniedException`, the
answer CloudWatch Logs (a JSON-protocol API) gives for the refusal S3 and
IAM call `AccessDenied`; no other seed's test does. S3's marker is off.
S7's stays, with the finding as its reason (`rulings/pr3.md` ruling 1).
`containment.py`, which reads the trail, is unchanged.

## What was read

`engineering-cold-reviewer` read the diff `59f06c0...335f276` (8 files,
7 commits) and row 5 only, and ran `test_m05_seeds.py` (5 passed, 2
xfailed; S7 with `--runxfail` fails on the empty `denied_principal`). It
also ran the observer and `containment.record` offline on the six run
files against an empty stub bucket. S3, S4 and S7 each read as made, with
no event-name mismatch, inside the observer's window (13:24Z on 09-29 to
05:16Z on 09-30). 0 BLOCK, 3 FINDING, 6 NOTE, verbatim in the PR body.

## What holds

- The shape is PR 3's: three run files filled, one marker off, one
  reworded, the ledger's 3 / 4, draft rulings. Nothing under `agents/`,
  `src/`, `infra/`, `.github/`, `rules/`, `data/` or `thresholds.yaml`,
  so this PR's run measures the runtime PR 2's merge deploy made.
- P5: no new writer or reader of envelopes.
- S7's marker, its run file and `containment.py`'s reading agree: no
  model call by refagent's role, so S7 reads unrecorded.

## Dispositions

| # | Finding | Status |
|---|---|---|
| F1 | S3's trail code asserted as `AccessDenied` with no record in the diff; the reader matches it exactly | **Worded** (Product): the run file and `rulings/pr3.md` say the event history showed `AccessDenied` for that request, and the audit bucket's copy is this PR's run's reading. **Read by this PR's run**: if the record says otherwise, the repair is in this PR |
| F2 | The widened code let S2 and S6 accept `AccessDeniedException` | **Repaired**: `denied()` takes the codes per seed; only S3 passes it. Falsified: an S2 entry with `AccessDeniedException` now fails |
| F3 | The README wrote the agent account's readings as facts before the run, and gave a cause for the silent log | **Worded** (Product): marked as the human's and the session's reading in the agent account; the cause is "likely, not read" |
| N1 | Nothing under `agents/refagent/**` changed | Recorded |
| N2 | S3's "stream still there" rests on the human; the reader does not look | Recorded; PR 2's reader. M06 |
| N3 | "Stated before the attempt" rests on a local commit time, 91 s before the attach | Recorded. The trail dates the attach; nothing outside this machine dates `e1a6bb2` before its push |
| N4 | S7's caller answer is the only sign the quarantine held on the right role, and feeds no reading | Recorded for the close |
| N5 | This file had no cold review | Repaired: this file |
| N6 | S4's key and S7's window are PR 2's reader's | Recorded; the run reads them (Unsure F) |

## The run that decides this ruling

Pending: the head and the `evals` run on it that read S3, S4 and S7 from
the audit bucket, with S3's `error_code` quoted from its `containment`
(F1).

## What a reader can run

```
uv run pytest -q tests/test_m05_seeds.py                     # 5 passed, 2 xfailed (S1, S7)
uv run pytest -q tests/test_m05_seeds.py -k s7 --runxfail    # fails on denied_principal: no model call
git diff --name-only 59f06c0...HEAD                          # nothing under agents/
```
