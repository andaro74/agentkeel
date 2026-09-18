---
# The CI-written envelope is in evidence (BLOCK 1 below is cured). This line
# is still DRAFT because the Engineering seat changes it; the cold reviewer
# and the session that wrote the diff do not rule.
ruling: DRAFT
seat:
  - Engineering
  - Security
  - Threshold Owner
  - Product
authorises:
  # Engineering
  - Makefile
  - pyproject.toml
  - uv.lock
  - scripts/observe_pr_check.py
  - src/cost_cap.py
  - src/ledger.py
  - src/verdict/**
  - tests/**
  # Engineering, CI-written only (ADR-0003): commit 42ed278, by github-actions[bot]
  - evals/history/**
  # Security (ruling R3-1, feasibility.md §2 third round)
  - .github/workflows/evals.yml
  - infra/eval-role/**
  # Threshold Owner (ruling R3-5): one bar, 20,000 tokens per run
  - thresholds.yaml
  # Product
  - milestones/README.md
  - milestones/M00/README.md
  - milestones/M00/feasibility.md
  - milestones/M00/runs/f0_3.yaml
  - milestones/M00/rulings/pr2.md
  - docs/milestones/README.md
evidence:
  # the measurement: the CI run, and the envelope its `record` job committed
  - https://github.com/andaro74/agentkeel/actions/runs/35404446711
  - evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.json
  - evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.baseline-card.json
  - evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.baseline-raw.json
  - SPEC/00-overview.md#8-M00
  # third round: R3-1 to R3-5, the rulings that bound this PR
  - milestones/M00/feasibility.md#2
  # the second seed and the tests that read it; `f9f1342` holds them with no reader
  - tests/fixtures/hand_written_envelope_no_baseline_card_ref.json
  - tests/test_f0_2.py
  - tests/test_p5_disagree.py
  # the F0.3 seeded case: no ruling file, cold-review-ruling failed, closed unmerged
  - https://github.com/andaro74/agentkeel/pull/4
  - https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255
pr: 3
---

# Ruling: M00 PR 2 (measure) — DRAFT

Cites `SPEC/00-overview.md#8-M00` for `src/verdict/`, `replay_history`,
the `Makefile` targets and the tests. §8 M00 does not list `evals.yml`,
`infra/eval-role/` or `thresholds.yaml`; those three are authorised here
by the Security and Threshold Owner seats under R3-1 and R3-5.

## Where this stands

- **The plant went RED locally and in tests, not yet in CI.** On the
  second seed the gate exits 2, REJECTED, `'baseline_card_ref' is a
  required property`. A run with no baseline card makes build exit 3 and
  write nothing. Six tests in `tests/test_f0_2.py` hold that; removing
  `baseline_card_ref` from the schema's `required` list fails four of
  them. None of this is evidence of row 0 (P11).
- **Measured in CI, 2026-09-18.** [Run 35404446711](https://github.com/andaro74/agentkeel/actions/runs/35404446711) at
  `8fb4b80` assumed the role, ran `make evals`, and its `record` job
  committed `evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.*` as `github-actions[bot]` (`42ed278`).
  What the gate reads in that envelope:

  > traps 1/3 (g-012); ordinary 1/9; guardrail 0/3; never_passed 13;
  > regressed 0; plants 0/0; F0_2 pass; F0_3 pass; GREEN

  5,623 tokens against a cap of 20,000. The tree was clean, no call
  failed, and the prompt hash is the plant's (`2c3d9b75`). `make ledger`
  prints the full cell, with both URLs; Product copies it at close.
- **Traps 1/3 on `g-012` is what row 0 expected**, so there is no
  trap-count finding to record. **The ordinary pass moved.** It is
  `g-006` here. It was `g-001` on the PR 1 plant and none on the local
  run at `e12ab7d`. Same prompt, temperature 0, three runs, three
  different answers to which ordinary question the control gets right.
  That is non-determinism in CI evidence now, not only locally, and it
  is what FINDING 6 below is about: `g-006` and `g-012` have now passed
  once, so the next measurement where either fails is RED.
- **GREEN means nothing regressed.** The history was empty. It does not
  mean 2 of 15 is good.
- **`checks.F0_3` is `pass`** because Security put a ruleset on `main`
  between the first run and this one: require a PR, require
  `cold-review-ruling`. The observer cannot read `bypass_actors`
  (Security finding 6), so `pass` does not say the owner cannot bypass.
- **It took three runs.** Attempt 1 had no role. Attempt 2 was refused:
  the role trusted `repo:andaro74/agentkeel:pull_request` and this repo
  issues the immutable subject, `repo:andaro74@3157440/agentkeel@1376369685:…`
  (feasibility.md §9.5). It failed closed. `8fb4b80` fixed the trust
  policy and Security redeployed.

## Cold review

`engineering-cold-reviewer`, read cold at `615f2af` against `main`
`8675bd6`: 2 BLOCK, 12 FINDING, 13 NOTE. What was repaired before the
measurement is marked; the rest stands for the seats.

### BLOCK

1. **The repo holds no measurement.** `evals/history/` is empty; "the
   gate went RED on the plant" is recorded only in tests, prose and a
   local run. Merging now would leave the row to a later PR. *Cured:*
   Security deployed the role, the workflow ran on this PR, and the
   `record` job pushed the three files (`42ed278`). The evidence is at
   the top of this file. The reviewer also asks which counts as "went RED": the
   gate's REJECTED (exit 2) on the seed, or `checks.F0_2` in the
   envelope. Product.
2. **A prose-only push turned `evals` green over a RED, REJECTED or
   hand-written envelope; the gate was never asked.** The "already
   measured" step set an output and every later step skipped. Security's
   report found the same. *Repaired in this PR:* the skip path now runs
   `verdict.gate` on the recorded envelope and the gate's exit code is
   the job's. A hand-written envelope that validates and points at a
   real card still passes the gate; nothing signs an envelope yet.

### FINDING

| # | Finding | Status |
|---|---|---|
| 1 | `make ledger` held the Measured cell to build's verdict, not the gate's | Repaired: `gate.measured_at` rules first; the reviewer's probe is now `test_ledger_sides_with_the_gate_not_with_build` |
| 2 | `make ledger` passed any State over an empty Measured cell | Repaired: GREEN over `—` fails; a closed State must be the cell's verdict |
| 3 | Build and the gate share `plants.plant_ids` and `replay_history`, so cannot disagree on either RED condition by logic | Open. The docstring now says what is shared. Whether to split is Engineering's ruling |
| 4 | UNMEASURED could not be reached from `make evals`: the runner's exit 1 stopped make | Repaired: the chain goes on and build writes UNMEASURED |
| 5 | A list in `table_row` crashed build with a TypeError | Repaired: not a string is not a citation |
| 6 | The regression bar goes RED on noise from the control (temperature 0 is not deterministic; FRAGILE is M03) | **Open. Threshold Owner with Data Owner.** After the first CI envelope, a re-measure where `g-012` fails is RED with no code change. Row 0 says record it; the gate as built blocks on it. `.claude/` is now outside the re-measure diff, so the close PR's skills do not re-measure |
| 7 | The skip key ignores measured inputs that are not in the tree (`checks.F0_3` is read from GitHub) | Open. The workflow header now says so, and that a change to `milestones/M00/runs/f0_3.yaml` measures again |
| 8 | Seat-owned paths cited rulings that were not ruling files | This file. Security and Threshold Owner rule their lines above or they come out of `authorises` |
| 9 | `checks` on the envelope and `cost-cap` at M00 from `thresholds.yaml` depart from SPEC/00 §5, §6, §8 with no ADR | **Open. Product.** ADR-0001 has used both amendments; this needs a new ADR |
| 10 | "CI-written" is `GITHUB_ACTIONS == "true"` | Open until `two-key` (M02). The docstrings and Makefile now say "an environment variable", not "outside CI" |
| 11 | `cost-cap` passed on observations with no usage | Repaired: a reply with no usage fails the cap |
| 12 | The generated page named `make ledger --plain`, which exits 2 under GNU make | Generated page repaired. SPEC/00, CLAUDE.md and the ledger header still say it. Product |

### NOTE

Shape holds: the seed `f9f1342` precedes the reader `f2885b9`; nothing
under `src/baseline/`, `evals/goldens/`, `rules/` or `data/` is touched;
no Measured cell is filled. The F0.2 test can fail. Repaired from the
notes: empty `answer_fields` is refused; a bad history file is REJECTED
(exit 2), not RED; the history-guard test no longer aims at the real
`evals/history/`; the test that pinned the Threshold Owner's number now
checks only that the code can read a cap. Standing: `replay_history` is
a second reader of envelopes (SPEC/00 §8 names it; the seat should rule
once whether P5 admits it); a gate-REJECTED envelope would still be
recorded; the ledger's Seeded commit cell names only `22b5499`, not the
second seed `f9f1342`; history is keyed on golden id only, with one
envelope per commit, which M01 must settle before refagent's passes
become the baseline's regressions.

## Seat reports

The `security-reviewer` (0 BLOCK, 6 FINDING, 12 NOTE) and
`threshold-owner` (0 BLOCK, 7 FINDING, 13 NOTE) reports are pasted in
the PR body, verbatim. What they leave for the seats:

- Security: six models on a role any PR branch can assume for an hour,
  with `cost-cap` reading only what the PR's own runner wrote (R3-1
  names six; M00 calls one). A ruleset on `main`: require a PR, require
  `cold-review-ruling`, `bypass_actors: []`. The F0.3 observer cannot
  read `bypass_actors`. The five action SHAs were resolved from each
  repo's latest release through the API, not checked with `ls-remote`.
- Threshold Owner: whether an over-cap run is a recorded RED or no
  record; which card an envelope points at (report 1.4: the code builds
  "same run"); confirm the baseline parameters before tag `m00`; the
  pin says us-west-2 and the profile serves from three regions.

## What a reader can falsify

- `uv run python -m src.verdict.gate tests/fixtures/hand_written_envelope_no_baseline_card_ref.json`
  prints REJECTED and exits 2. Add a `baseline_card_ref` to a copy and it
  is rejected for the card instead, not accepted.
- `uv run pytest -q`: 66 pass. Delete `"baseline_card_ref",` from
  `required` in `src/verdict/schema.json`: four tests in
  `tests/test_f0_2.py` fail.
- `git show f9f1342 --stat`: the seed and its test, no `src/verdict/`.
- `make evals` on a laptop exits before spending. `make plants` prints
  `plants_expected = 0`. `make ledger --plain` exits 2; `make ledger --
  --plain` rewrites `docs/milestones/README.md` byte for byte.
- `cd infra/eval-role && npx cdk synth`: one role, two statements, no
  wildcard; `cdk.out/AwsSolutions-*-NagReport.csv` has no
  `Non-Compliant` row and `app.py` has no suppression.
- PR #4 is closed, unmerged, and its `cold-review-ruling` run failed.
  `gh api repos/andaro74/agentkeel/rules/branches/main` says whether the
  check is required today.
