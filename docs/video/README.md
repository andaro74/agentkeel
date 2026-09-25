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
| M01 | tag `m01`, recorded on `main` after the close PR merged; committed in M02 PR 1 as an LFS object (`f6d1e73`, ADR-0005 amendment 1) | S1 and S2 refused by `verify`, each with its planted reason; S3, S5 and S8 refused at synth; the S4 and S6 refusals in CloudTrail; the uncited answers turning the result RED; row 1 reading UNMEASURED on the runner envelope, and `make ledger` refusing GREEN beside it; the failed first deploy, `kms:CreateGrant` refused by the deploy boundary | recorded, 6:09, 9.5 MB. **Over the five-minute ceiling above by 69 seconds**; this row said "not recorded" from the file's landing until M02's close, and Product rules at M03 PR 1 whether the ceiling or the recording stands (`milestones/M03/open.md` row 9). Not re-recorded |
| M02 | tag `m02`, commit `71eff00`, recorded on `main` after the close PR (#13) merged, 2026-09-24; committed in M03 PR 1 as an LFS object (ADR-0005 amendment 1) | seed PR 14's `two-key` red naming `thresholds.yaml`, and PR 15's "one seat"; PR 16's `ruling-cited` red on `g-010`; PR 17's and PR 18's `checks` red on the edge and the renamed id; `gh pr merge 14 --admin` refused, and rule suite 4192991324 in GitHub's record; the admin role added to `bypass_actors` and `validate` going RED (job 107206831180), then `[]`; PR 12's `two-key` green on the retirement with two keys; the envelope for `8033c2a` with `F2_1` and `F2_2`, and row 2 reading GREEN under `make ledger` | recorded, 5:48 (347.7 s), 6.0 MB. **Over the five-minute ceiling above by 48 seconds**, as M01's is by 69. Not re-recorded to fit (SPEC/00 §10.2: recordings are committed once). Whether the ceiling or the two recordings stand is ruled at M03 PR 1 (`milestones/M03/rulings/pr1.md`, `milestones/M03/open.md` row 9) |

M00's video was recorded on `main` at tag `m00`, after the close PR
merged, and committed in M00 PR 4 (ADR-0005). The live `make evals-local`
in it is a laptop run and is not evidence; its counts may differ from the
recorded envelope's, which is Finding F0.4.

From M01, a milestone's video is committed in the **next** milestone's
PR 1, never in a PR of its own milestone (ADR-0005 amendment 1). M00 PR 4
was the one exception, and it spent M00's cap.

## Storage and size

M00.mp4 is a plain blob (84.4 MiB); recordings from M01 are LFS objects
under .gitattributes, whose second line keeps the filter off M00.mp4. It is not migrated: a migration would rewrite
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
