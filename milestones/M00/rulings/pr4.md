---
# M00 PR 4: the M00 video, committed after the tag (ADR-0005). The last of
# M00's four PRs. Nothing measured changes: every path is under docs/ or
# milestones/**/*.md, which evals.yml excludes.
ruling: pr4
seat:
  - Product
authorises:
  - docs/video/milestones/M00.mp4
  - docs/video/README.md
  - docs/milestones/M00.md
  - docs/milestones/README.md
  - milestones/README.md
  - milestones/M00/README.md
  - milestones/M00/rulings/pr4.md
  - milestones/M01/open.md
evidence:
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - SPEC/00-overview.md#10-5
  # the tag the video was recorded at: m00 -> cfbd8ba, the merge of PR #5
  - https://github.com/andaro74/agentkeel/releases/tag/m00
pr: 6
---

# Ruling: M00 PR 4 (the video)

ADR-0005: the milestone video is recorded on `main` after `git tag m00`
and committed in its own PR, with the tag in its entry. This is that PR.

- `docs/video/milestones/M00.mp4`: 4:16 (the cap is 5:00), 84.4 MiB
  (GitHub rejects files over 100 MB). Recorded 2026-09-19 at tag `m00`,
  commit `cfbd8ba`. Committed as recorded; it was first pushed as
  `m00-pr4.mp4` and is renamed to the path SPEC/00 §10.3 and
  `src/ledger.py` read. A rename is not an edit.
- `docs/video/README.md` and the explainer's Watch line carry the tag,
  the commit, the date and the length.
- `milestones/README.md` row 0 and `milestones/M00/README.md`: PRs used
  `4 / 4`. The cap is spent; M00 has no fifth PR.
- `milestones/M01/open.md` item 27 is done.
- `docs/milestones/README.md` is rewritten by `make ledger-plain`, which
  now links the video.

No seat subagent applies: every path is Product's, and Product has no
reviewer beyond `product-spec-reviewer`, which reads SPEC/NN before a
PR 1 (`.claude/skills/cold-review/SKILL.md`).

## What a reader can falsify

- `make ledger` exits 0; row 0 is unchanged but for `4 / 4`.
- `make ledger-plain` rewrites `docs/milestones/README.md` byte for
  byte, with M00's Video cell reading `watch`.
- `git diff --name-only main...HEAD` touches nothing under `src/`,
  `tests/`, `evals/`, `infra/`, `.github/` or `thresholds.yaml`, and the
  PR's `evals` run takes the "already measured" path.
- `git rev-parse m00^{commit}` is `cfbd8ba`; the tag has not moved.
