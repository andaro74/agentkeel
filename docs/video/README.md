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
| M00 | tag `m00`, commit `cfbd8ba`, 2026-09-19 | trap `g-012` and its answer; `make evals-local` losing, live; the seed commit `f9f1342` with no `src/verdict/`; `verdict.gate` on `tests/fixtures/hand_written_envelope_no_baseline_card_ref.json` exiting 2, REJECTED; row 0 before and after the close; `make ledger` exiting 0; `tests/test_baseline_frozen.py`, 9 passed | recorded, 4:16 |

M00's video was recorded on `main` at tag `m00`, after the close PR
merged, and committed in M00 PR 4 (ADR-0005). The live `make evals-local`
in it is a laptop run and is not evidence; its counts may differ from the
recorded envelope's, which is Finding F0.4.

From M01, a milestone's video is committed in the **next** milestone's
PR 1, never in a PR of its own milestone (ADR-0005 amendment 1). M00 PR 4
was the one exception, and it spent M00's cap.

## Storage and size

M00.mp4 is a plain blob (84.4 MiB); recordings from M01 are LFS objects
under .gitattributes. It is not migrated: a migration would rewrite
`cfbd8ba` and `8252763` and move tag `m00`, and envelopes are keyed to
commits (ADR-0004). CI checks out with `lfs: false` and reads no video
bytes; `make ledger-plain` links a recording when its path exists, which a
pointer file satisfies.

Ceilings, per recording (Product): **40 MiB per milestone video, 64 MiB
per act.** At M00's bitrate the fifteen recordings would come to about
1.6 GB, over GitHub's 1 GiB of free LFS storage. Recording settings are
chosen to fit; they are not edits.

## Acts (`docs/video/actN-*.mp4`, ≤ 8 minutes)

None recorded. The six acts are scheduled at M06 to M08 (SPEC/00 §10.2);
each gets its row here when it is recorded, with its commit and tag.
