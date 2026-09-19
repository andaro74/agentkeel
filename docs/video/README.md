# Recordings

Two kinds, both unedited screen capture with narration, both committed
once and never re-recorded to match later prose. If the platform changes,
a new recording is added and the old one is marked superseded here
(SPEC/00 §10.2).

Every entry carries the commit and the tag it was recorded at. A failure
on camera is kept and explained in its entry; a retake of a failed step
is not a recording, it is an advertisement.

## Milestone videos (`docs/video/milestones/MNN.mp4`, ≤ 5 minutes)

The screen shows the plant going in, the gate firing, and the ledger row
being filled (SPEC/00 §10.3).

| M | Recorded at | Shows | State |
|---|---|---|---|
| M00 | tag `m00` | the three traps and the baseline prompt; `make evals-local` losing; `verdict.gate` on `tests/fixtures/hand_written_envelope_no_baseline_card_ref.json` exiting 2, REJECTED; the CI-written envelope for `9407615`; `make ledger` printing row 0 GREEN and exiting 0 | **pending, tag `m00`** |

M00's video is recorded after the close PR merges and the tag is cut, not
inside the close PR. SPEC/00 §10.5 says a close is not ruled ready
without the page and the video; the page is in the close PR and this
departure is ruled by Product at the M00 close
(`milestones/M00/README.md`, close detail) and carried as item 27 of
`milestones/M01/open.md`.

## Acts (`docs/video/actN-*.mp4`, ≤ 8 minutes)

None recorded. The six acts are scheduled at M06 to M08 (SPEC/00 §10.2);
each gets its row here when it is recorded, with its commit and tag.
