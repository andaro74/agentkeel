---
# M06 PR 2 (#35), the Threshold Owner's key. Product's file is pr2.md.
ruling: pr2-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/06-developer-template.md
  - milestones/M06/feasibility.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
pr: 35
---

# Ruling: M06 PR 2, Threshold Owner

Ruled by andaro74 as Threshold Owner, 2026-10-01, as written.

## What this authorises

`quickstart.max_seconds: 28800`, `relaxes: up` (SPEC/06 §1, finding 8 on
M06 PR 1): one working day, wall clock, breaks not subtracted. Adding a bar
is not a relaxation (ADR-0009: the list is closed), so no second key.
Absolute, not relative: it is not a quality bar and has no incumbent
(SPEC/00 §8 M04). Recorded in `template` by `build`, held again by the gate
at the envelope's commit, read by row 6; it gates no pull request. No other
bar, no model pin and no `deprecated_after` moves in this PR (the
manifests change `seats` and one comment).

## The seat report (verbatim in the PR body; read the tree, a weaker witness)

| # | Status |
|---|---|
| F1 (absolute, not stated why) | Repaired in the bar's comment (`5b817fe`) |
| F2 (the comment and the ruled finding time panel 1; the reader does not) | Repaired: the comment says the registry row and panel 1's row are read untimed; F6.3 now requires both (cold review F2) |
| N8 (the registry row's time is a runner's clock, rewritten by a redeploy) | Repaired: F6.3 times the deploy run that wrote the first answer record, by GitHub's completion, and the answer by S3's `LastModified` |
| N6 (tests) | `template_misses` with no bar is tested through `quickstart_at`; a two-key test on this bar's move is carried to PR 3 |
| N7 (a shallow clone reads today's bar) | Stands as for `detection_at`; PR 3's run fetches full history, as every run does |

## What a reader can run

```
git diff ef7e48e...HEAD -- thresholds.yaml
uv run pytest tests/test_m06_readers.py -q -k "bar or template"
```
