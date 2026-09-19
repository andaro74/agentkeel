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
  - docs/adr/ADR-0005-video-follows-the-tag.md
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
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - SPEC/00-overview.md#8-M00
  - SPEC/00-overview.md#10-5
  # the cold read and the Security read of this PR, at e3a3471; both
  # reports are pasted in the PR body, and what they found is below
  - https://github.com/andaro74/agentkeel/pull/5
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

**Corrected here, twice, and both against the envelope.**

1. The close was asked for `never_passed 13`. The envelope says 14.
   Thirteen is the first CI run's number, at `8fb4b80`, where the control
   also got `g-006` right; at `9407615` it got no ordinary golden right,
   so fourteen of the fifteen have never passed.
2. "The control scored 2 of 15" is wrong for the measured run and stood
   in two places in the first draft of this PR. The envelope has one
   `pass: true`, `g-012`. Two of fifteen is the union across four runs —
   `g-001` on the plant, `g-006` on the first CI run, `g-012` every time
   — and no single run has passed two. `milestones/M00/README.md` and the
   explainer now say one on the measured run and two at best on any run.

The sentence the close was asked to carry verbatim — "GREEN means nothing
regressed against an empty history; it does not mean 2 of 15 passing is
good" — is kept word for word, and the paragraph above it now says which
run gives which number, so the two cannot be read against each other. A
seat can ask for a sentence; the envelope decides what the numbers around
it are. `.claude/skills/close-milestone/SKILL.md` carries that rule
forward, because it ships the sentence as the model for every later
close.

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
observed, with the `describe-stacks` output that says so. The run below
is the first to assume it.

**L. Product — the video follows the tag (ADR-0005).** The first draft of
this close took a departure from SPEC/00 §10.5 in prose and left the SPEC
line standing. CLAUDE.md says SPEC/00 wins, so the line is amended by an
ADR instead: the explainer page is delivered in the close PR, the video
is recorded on `main` after the tag, and an uncommitted video is carried
into the next milestone's `open.md` like any other open item. The rule as
written could not be met — §10.3 wants the row being filled on camera and
§10.2 forbids a retake, and the row is filled by a commit inside the
close PR.

**M. Product — the CLAUDE.md edits.** Two, both on Product's own path and
both authorised by this ruling. The merge-commit rule under ruling I, and
three entries in "Where things are": `docs/video/`, `.claude/skills/`,
and `milestones/MNN/open.md` as the file a close writes for the next
milestone. The third is named separately because it is the line that
makes writing into `milestones/M01/` from an M00 PR a legitimate thing to
do, rather than a habit this PR started.

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

**The run.** Recorded here when it finishes, before the merge. It is
what Security signs S-1 on at M01, and it is also the first observation
of the two things `infra/eval-role/README.md` says are unobserved: that
STS evaluates the `job_workflow_ref` condition, and that this repo issues
that claim in the form the trust policy pins. If the assume is refused,
this PR is RED, the refusal is the finding, and the row is rewritten
before the tag.

> _(pending: the run had not started when this ruling was written — the
> PR was not open yet. No other file may claim this record exists until
> the line below replaces this one.)_

## Cold review

`engineering-cold-reviewer`, read cold at `e3a3471` against `main`
`0c39568`: 2 BLOCK, 7 FINDING, 6 NOTE. Shape, plant, P5 and the frozen
paths were clean; what it stopped was the prose, in the one PR whose
product is prose. Both BLOCKs are repaired in this PR.

### BLOCK

1. **The explainer's headline number was not the envelope's.** "2 of 15"
   in `docs/milestones/M00.md` and `milestones/M00/README.md`, against a
   table on the same page reading 1 of 15 and an envelope with one
   `pass: true`. The skill this PR ships refuses a close on exactly that.
   *Repaired:* see "Corrected here" above. The ruled sentence is kept
   verbatim and the paragraph around it now names the run each number
   belongs to.
2. **Four files cited a record that this ruling did not contain.** The
   S-1 evidence chain ended in an HTML comment.
   *Repaired:* `infra/eval-role/README.md`, `milestones/M00/README.md`,
   `milestones/M00/attestations.md` and `milestones/M01/open.md` now say
   the close PR's own run is the first and that this file records it when
   it finishes; the comment is replaced by a paragraph that says plainly
   that the run had not started.

### FINDING

| # | Finding | Status |
|---|---|---|
| 1 | "never the same two" was false — `g-012` passed in both CI runs, and run 5 passed one, not two; the paragraph also leaned on runs that are not evidence | Repaired: the explainer now counts four runs, says the trap is the same one every time, and separates "ever" from "on the measured run" |
| 2 | "Narrowed to one, and to the single workflow file" described a control no run had assumed (SPEC/00 §10.5) | Repaired: the explainer says deployed, not yet used, and that the first run to use it is recorded with the milestone |
| 3 | ADR-0002's guard shipped with no recorded firing | Repaired: the transcript is in "What a reader can falsify" below. The tag arm still skips, and that is said where it matters |
| 4 | The §10.5 departure was ruled in prose while SPEC/00 stood unamended | Repaired: ruling L, ADR-0005, and §10.5 amended |
| 5 | Row 0 goes GREEN in the same commit as three unsigned attestations | Repaired: `attestations.md` now says what the signatures gate (the tag) and what they do not (the row, which is the envelope's verdict and is held there by `make ledger`) |
| 6 | F0.3 stated as "no change reaches the main branch"; the observer cannot read `bypass_actors` | Repaired: the explainer says what was observed and names the gap |
| 7 | The CLAUDE.md "Where things are" edit was under no ruling | Repaired: ruling M |

### NOTE

Repaired from the notes: the frozen-file check is recursive, so a
sub-package under `src/baseline/` is a change to the control, and
ADR-0002 §1 says so; the card check reads `prompt_sha256` instead of
matching a substring of the card; `.claude/skills/cold-review/SKILL.md`
now says there is no Product reviewer beyond `product-spec-reviewer`, and
that this is the arrangement and not an oversight. Standing: the
explainer's "a team cannot make its agent look better" is absolute about
two keys, which land at M02 — pre-existing from PR 1, and it now sits
under a GREEN row.

## Seat reports

The `engineering-cold-reviewer` and `security-reviewer` reports are
pasted in the PR body, verbatim, with their counts. Security: 0 BLOCK,
11 FINDING, 11 NOTE. It read the trust policy and said this PR's own run
should match `job_workflow_ref`; the run is the test of that. What it
left for the seats is items 28 to 35 of `milestones/M01/open.md`, and one
repair taken here: the deploy claim now carries the `describe-stacks`
output, because every other claim in this close names a run or an
envelope and that one named a console reading.

Its sharpest point is not in the diff. The trust policy pins `sub` in
the immutable form and `job_workflow_ref` in the classic form, and
nothing has confirmed which form this repo issues for the second. That
is the same mistake class that already refused an assume once
(run 35402876499, attempt 2). This PR's run prints the claim before it
assumes, so the log answers it either way.

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
- `git diff --name-only main...HEAD` touches nothing under
  `src/baseline/`, `src/verdict/`, `evals/goldens/`, `rules/`, `data/`,
  `thresholds.yaml`, `.github/`, `evals/history/` or
  `infra/eval-role/app.py`.
- The freeze guard has been seen to fail, not only asserted. Appending
  one newline to `src/baseline/prompt.txt` gives:

  ```
  E   AssertionError: src/baseline/prompt.txt differs from ADR-0002. The control is not edited; it is retired.
  E   assert 'b54d2080c5b9...d1ece358df178' == '2c3d9b754f8c...76c6c383684ab'
  FAILED tests/test_baseline_frozen.py::test_each_file_is_the_frozen_one[prompt.txt]
  ```

  `git checkout src/baseline/prompt.txt` restores 8 passed, 1 skipped.
- Every item M00 did not settle is in `milestones/M01/open.md` with a
  seat and a date, and every finding has a row in the close detail of
  `milestones/M00/README.md` naming the file that holds it.

## What this close does not do

- It does not record the video. `docs/video/milestones/M00.mp4` is
  pending at tag `m00`. This is no longer a departure from SPEC/00 §10.5:
  ruling L amends the line (ADR-0005). The outstanding video is item 27
  of `milestones/M01/open.md`, Product, before M01 PR 1, and M00 is not
  finished until it is committed.
- It does not observe the freeze against the tag.
  `test_the_control_has_not_changed_since_tag_m00` skips until `m00`
  exists; what holds the control today is the three hash assertions, and
  the transcript above is the only record of one of them firing. From the
  tag, `evals` checks out with `fetch-depth: 0` and the fourth assertion
  runs too.
- It does not tag. `git tag m00` is cut on `main` after the merge, by the
  human, and the attestations are signed before it.
