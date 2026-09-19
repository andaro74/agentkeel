---
# Ruled at the M00 close, before the PR opened. The milestone closes in
# three PRs: ruling F (feasibility.md §2, fourth round) found both of
# PR 2's BLOCKs cured inside PR 2, so there is no repair PR.
ruling: pr3
seat:
  - Product
  - Threshold Owner
  - Engineering
  - Security
authorises:
  # Product
  - SPEC/00-overview.md
  - CLAUDE.md
  - docs/adr/ADR-0002-baseline-frozen.md
  - docs/adr/ADR-0004-measurement-fields.md
  - docs/milestones/M00.md
  - docs/milestones/README.md
  - docs/video/README.md
  - .claude/skills/**
  - milestones/README.md
  - milestones/M00/README.md
  - milestones/M00/feasibility.md
  - milestones/M00/attestations.md
  - milestones/M00/rulings/pr3.md
  - milestones/M01/open.md
  # Engineering. ADR-0002 also names Threshold Owner (the frozen
  # parameters) and Product (SPEC/00 §8 M00) as the seats whose rules it
  # changes.
  - tests/test_baseline_frozen.py
  # Security (ruling K): Finding S-1 is recorded as deployed and not yet
  # observed. infra/eval-role/app.py is not touched.
  - infra/eval-role/README.md
evidence:
  # PRIMARY. The measurement row 0 rests on: the CI run at 9407615 and the
  # envelope, card and raw observations its `record` job committed (76fa683).
  - https://github.com/andaro74/agentkeel/actions/runs/35406351135
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.json
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-card.json
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-raw.json
  # The same envelope, ruled on again on `main` after the merge of PR #3,
  # with no tokens spent: the push run found nothing measured had changed.
  - https://github.com/andaro74/agentkeel/actions/runs/35408681217
  # The rulings this close rests on: F (PR 3 is the close), and G to K,
  # taken before this PR was written.
  - milestones/M00/rulings/pr2.md
  - milestones/M00/feasibility.md#2
  # Finding F0.4, run by run, including this PR's own run
  - milestones/M00/feasibility.md#6.5
  - docs/adr/ADR-0002-baseline-frozen.md
  - docs/adr/ADR-0004-measurement-fields.md
  - SPEC/00-overview.md#8-M00
pr: 5
---

# Ruling: M00 PR 3 (close)

Cites `SPEC/00-overview.md#8-M00` for ADR-0002 and the skills, both of
which §8 M00 lists as the close PR's work, and ADR-0004 amendment 1 for
the merge-commit rule. `infra/eval-role/README.md` is authorised by the
Security seat under ruling K; `tests/test_baseline_frozen.py` by
Engineering under ADR-0002.

## The row

Row 0 is GREEN on the envelope for
`9407615dcde09308490f6699c21a18100bfedcd2`. The Measured cell is copied
from what `make ledger` prints from that envelope, not retyped:

> control: traps 1/3 (g-012); ordinary 0/9; guardrail 0/3; never_passed
> 14; regressed 0; plants 0/0; F0_2 pass …/runs/35406351135; F0_3 pass
> …/runs/35401176820/job/105781176255; GREEN; envelope `9407615…`

`make ledger` exits 0 against it and exits 1 if the cell is changed by a
character.

**Corrected here:** the close was asked for `never_passed 13`. The
envelope says 14. Thirteen is the first CI run's number, at `8fb4b80`,
where the control also got `g-006` right; at `9407615` it got no ordinary
golden right, so fourteen of the fifteen have never passed. The envelope
is what the row and the explainer say.

## The rulings taken at this close

**G. Threshold Owner — baseline parameters confirmed as measured.**
`us.amazon.nova-micro-v1:0`, us-west-2, temperature 0, `maxTokens` 512,
prompt sha256 `2c3d9b75…` as in the card at `9407615`. Confirmed, not
changed; recorded in `milestones/M00/README.md` as confirmed before tag
`m00`; frozen by ADR-0002 from the tag.

**H. Product — what "the plant went RED" means.** The gate's REJECTED on
the seed (`f9f1342`), and then `checks.F0_2: pass` in the envelope as the
measurement that the rejection holds in CI. Both, in that order. The
explainer says both in that order. This closes report 4.1.

**I. Product — merge commits, not rebase or squash,** from PR #3 onward.
ADR-0004 amendment 1. The ruleset on `main` allows `merge` and has no
`required_linear_history` rule; CLAUDE.md now states the rule positively,
because the words "linear history" it was to lose are not in the tree.

**J. Engineering, for M01 PR 1 — which card a later envelope points at**
(report 1.4). The card at tag `m00`, by content hash, recorded once in
`thresholds.yaml` as `baseline_card_sha`. Not built here;
`feasibility.md` §7 item 5.

**K. Security — Finding S-1.** The narrowed role was redeployed on
2026-09-19T00:20:25Z and no run had assumed it at the time this PR was
written. Recorded in `infra/eval-role/README.md` as deployed and not
observed. The run below is the first to assume it.

## This PR's own measurement

The close PR changes `tests/` and `infra/eval-role/README.md`. Neither is
excluded from `evals.yml`'s "already measured" step, so this PR spends
tokens and writes its own envelope, and is the first run to assume the
eval role as redeployed for S-1.

Row 0 stays on `9407615`. That envelope is the measurement of the tree
that reads the plant; adding a test that reads `src/baseline/` does not
re-open the claim. This PR's run is recorded here and in
`feasibility.md` §6.5 as another reading of the control under Finding
F0.4.

<!-- The run is recorded here when it completes; it is what Security
signs S-1 on, at M01. -->

## What a reader can falsify

- `make ledger` exits 0. Change one character of row 0's Measured cell
  and it exits 1, printing the ledger line and the envelope line side by
  side.
- `uv run pytest tests/test_baseline_frozen.py -q`: 8 pass, 1 skip (the
  skip is the diff against tag `m00`, which is not cut yet). Add a blank
  line to `src/baseline/prompt.txt` and
  `test_each_file_is_the_frozen_one[prompt.txt]` fails.
- `uv run pytest -q`: the whole suite, including the six F0.2 tests the
  envelope's `checks.F0_2` reports on.
- `make validate`: golden front matter, golden citations, ruling front
  matter — including that every `authorises` path above matches something
  in the tree.
- `make ledger-plain` rewrites `docs/milestones/README.md`; M00's row
  reads GREEN and its video reads "not recorded".
- `git show <this PR's head> --stat`: nothing under `src/baseline/`,
  `evals/goldens/`, `rules/`, `data/` or `evals/history/`.
- Every item M00 did not settle is in `milestones/M01/open.md` with a
  seat and a date, and every finding has a row in the close detail of
  `milestones/M00/README.md` naming the file that holds it.

## What this close does not do

- It does not record the video. `docs/video/milestones/M00.mp4` is
  pending at tag `m00`; SPEC/00 §10.5 wants it in the close PR. The
  departure is ruled by Product here and carried as item 27 of
  `milestones/M01/open.md`.
- It does not tag. `git tag m00` is cut on `main` after the merge, by the
  human, and the attestations are signed before it.
