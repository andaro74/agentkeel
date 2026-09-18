---
# Both CI-written envelopes are in evidence. This line is the Engineering
# seat's; it is changed in a commit of its own.
ruling: DRAFT
seat:
  - Engineering
  - Security
  - Threshold Owner
  - Data Owner
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
  # Engineering, CI-written only (ADR-0003): commit 42ed278, by github-actions[bot].
  # One human commit moved the pre-scope envelope to evals/history/pre-scope/:
  # a two-key change, ruled by Engineering and Product (ADR-0004).
  - evals/history/**
  # Security (ruling R3-1, feasibility.md §2 third round)
  - .github/workflows/evals.yml
  - infra/eval-role/**
  # Threshold Owner (ruling R3-5): one bar, 20,000 tokens per run
  - thresholds.yaml
  # Product. ADR-0004 also names Threshold Owner, Data Owner and Engineering
  # as the seats whose rules it changes (ruling A, fourth round).
  - SPEC/00-overview.md
  - CLAUDE.md
  - docs/adr/ADR-0004-measurement-fields.md
  - milestones/README.md
  - milestones/M00/README.md
  - milestones/M00/feasibility.md
  - milestones/M00/runs/f0_3.yaml
  - milestones/M00/rulings/pr2.md
  - docs/milestones/README.md
evidence:
  # PRIMARY. The measurement under ADR-0004: the CI run at 9407615, and the
  # envelope, card and raw observations its `record` job committed (76fa683).
  - https://github.com/andaro74/agentkeel/actions/runs/35406351135
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.json
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-card.json
  - evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-raw.json
  # SECONDARY. The gate before scope existed: the first CI run, at 8fb4b80,
  # and its envelope (42ed278). Moved to pre-scope/, not edited; the gate
  # does not read it. Its card and raw file stay where CI wrote them, so its
  # baseline_card_ref still resolves.
  - https://github.com/andaro74/agentkeel/actions/runs/35404446711
  - evals/history/pre-scope/8fb4b809abcdc00919012e7db65baa495779d3c8.json
  - evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.baseline-card.json
  - evals/history/8fb4b809abcdc00919012e7db65baa495779d3c8.baseline-raw.json
  - SPEC/00-overview.md#8-M00
  # third round: R3-1 to R3-5, the rulings that bound this PR;
  # fourth round: A to F, the rulings on what it found
  - milestones/M00/feasibility.md#2
  - docs/adr/ADR-0004-measurement-fields.md
  # Finding F0.4, run by run
  - milestones/M00/feasibility.md#6.5
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

## Rulings on what this PR found (fourth round)

The seats ruled six of the twelve items this PR listed as Unsure. They
are in feasibility.md §2, fourth round, and ADR-0004, and applied in one
commit. **A:** every result carries `scope`; the baseline is the control
and is never gated; `replay_history` keys on (scope, golden id); Finding
F0.4. **B:** ADR-0004 and the SPEC/00 amendments. **C:** "B1.6" is
ADR-0001 amendment 1, item 6. **D:** `make ledger-plain`. **E:** Finding
S-1; the CI role allows the baseline's profile only, to `evals.yml`
only. **F:** the repairs before measuring are accepted and PR 3 is the
close.

One part of E could not be done: `MaxSessionDuration` 900. IAM's floor
is 3600. It stays at the floor.

Ruling A changes a measured path, so `evals` measures again. The first
envelope, for `8fb4b80`, stays as evidence of the gate before scope
existed, under `evals/history/pre-scope/`.

## The measurement this ruling rests on

[Run 35406351135](https://github.com/andaro74/agentkeel/actions/runs/35406351135) at `9407615`, the commit that applied rulings
A to E. Its `record` job committed `evals/history/9407615dcde09308490f6699c21a18100bfedcd2.*` as
`github-actions[bot]` (`76fa683`). What the gate reads in that envelope:

> control: traps 1/3 (g-012); ordinary 0/9; guardrail 0/3; never_passed
> 14; regressed 0; plants 0/0; F0_2 pass; F0_3 pass; GREEN

- **As the ruling expected:** all fifteen results are `scope: control`;
  `regressed` is 0 by construction; `checks.F0_2` and `checks.F0_3` pass
  and decide the verdict; GREEN. 5,912 tokens against a cap of 20,000.
  Clean tree, no failed call, the plant's prompt hash.
- **Traps 1/3 on `g-012`,** as row 0 expects. No trap-count entry under
  Finding F0.4.
- **Ordinary 0/9.** The first CI run had 1/9, on `g-006`. That is
  Finding F0.4, now in CI evidence twice over: feasibility.md §6.5 has
  the five runs side by side. Under the first gate, a second measurement
  beside the first would have been RED on `g-006`. Under ADR-0004 it is
  reported and not gated.
- **GREEN means no check failed and nothing the gate reads regressed.**
  At M00 the gate reads no golden at all. It does not mean 1 of 15 is good.
- `make ledger` prints the full cell, with both URLs. Product copies it
  at the close.

What the run also showed:

- The role's new trust condition names `job_workflow_ref`. The run
  printed the claim: `andaro74/agentkeel/.github/workflows/evals.yml@refs/pull/3/merge`.
  The pinned pattern matches it. This run assumed the role **as deployed
  at `8fb4b80`**, the wider one; S-1 takes effect when Security redeploys,
  and only a run that assumes the redeployed role shows STS evaluates
  the claim.
- The `record` job's push does start runs of both workflows, by
  `github-actions[bot]`, which GitHub parks at `action_required` with no
  jobs. The header of `evals.yml` says such a push "starts no workflow".
  The effect is what it says (the envelope commit has no checks; the
  next human push is what `cold-review-ruling` reads). The sentence is
  not exact. Left as is: `evals.yml` is a measured path, and a comment is
  not worth a third measurement. For the close PR.

## Where this stands

The section below was written at the first measurement, before the
fourth round of rulings. It stands as the record of that run.

- **The plant goes RED.** On the second seed the gate exits 2, REJECTED,
  `'baseline_card_ref' is a required property`. A run with no baseline
  card makes build exit 3 and write nothing. Six tests in
  `tests/test_f0_2.py` hold that; removing `baseline_card_ref` from the
  schema's `required` list fails four of them. Those tests ran in the CI
  run below, and their junit result is `checks.F0_2: pass` in the
  envelope. Run locally, the same commands are not evidence (P11).
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
| 6 | The regression bar goes RED on noise from the control (temperature 0 is not deterministic; FRAGILE is M03) | **Ruled (A) and repaired.** The control is never gated; `test_the_control_is_never_gated` fails if the gate reads control results for `regressed`. The noise is Finding F0.4, recorded run by run in feasibility.md §6.5 |
| 7 | The skip key ignores measured inputs that are not in the tree (`checks.F0_3` is read from GitHub) | Open. The workflow header now says so, and that a change to `milestones/M00/runs/f0_3.yaml` measures again |
| 8 | Seat-owned paths cited rulings that were not ruling files | This file. Security and Threshold Owner rule their lines above or they come out of `authorises` |
| 9 | `checks` on the envelope and `cost-cap` at M00 from `thresholds.yaml` depart from SPEC/00 §5, §6, §8 with no ADR | **Ruled (B).** ADR-0004; SPEC/00 §5, §6, §8 M00 amended. §8 M03 and §14 still say what they said about `cost-cap`; ADR-0004 says so |
| 10 | "CI-written" is `GITHUB_ACTIONS == "true"` | Open until `two-key` (M02). The docstrings and Makefile now say "an environment variable", not "outside CI" |
| 11 | `cost-cap` passed on observations with no usage | Repaired: a reply with no usage fails the cap |
| 12 | The generated page named `make ledger --plain`, which exits 2 under GNU make | **Ruled (D) and repaired.** `make ledger-plain`; SPEC/00, CLAUDE.md and the ledger header name it |

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

- Security: ~~six models on a role any PR branch can assume~~ ruled (E,
  Finding S-1): one profile, one workflow file; the hour stays, because
  IAM allows no less; spend outside the runner is M01. **Security must
  redeploy `infra/eval-role/` for S-1 to take effect.** The ruleset on
  `main` is in place (require a PR, require `cold-review-ruling`). The
  F0.3 observer cannot read `bypass_actors`. The five action SHAs were resolved from each
  repo's latest release through the API, not checked with `ls-remote`.
- Threshold Owner: whether an over-cap run is a recorded RED or no
  record; which card an envelope points at (report 1.4: the code builds
  "same run"); confirm the baseline parameters before tag `m00`; the
  pin says us-west-2 and the profile serves from three regions.

## What a reader can falsify

- `uv run python -m src.verdict.gate tests/fixtures/hand_written_envelope_no_baseline_card_ref.json`
  prints REJECTED and exits 2. Add a `baseline_card_ref` to a copy and it
  is rejected for the card instead, not accepted.
- `uv run pytest -q`: 75 pass. Delete `"baseline_card_ref",` from
  `required` in `src/verdict/schema.json`: four tests in
  `tests/test_f0_2.py` fail.
- `git show f9f1342 --stat`: the seed and its test, no `src/verdict/`.
- `make evals` on a laptop exits before spending. `make plants` prints
  `plants_expected = 0`. `make ledger-plain` rewrites
  `docs/milestones/README.md` byte for byte.
- Scope: in `src/verdict/gate.py`, drop `results[g]["scope"] == "agent"
  and` from the `regressed` line. `test_the_control_is_never_gated`
  fails. Copy `evals/history/pre-scope/8fb4b80….json` into
  `evals/history/`: the gate refuses to replay it (`'scope' is a required
  property`), and `test_the_pre_scope_envelope_is_kept_and_is_not_read`
  says the same.
- `cd infra/eval-role && npx cdk synth`: one role, two statements, no
  wildcard; `cdk.out/AwsSolutions-*-NagReport.csv` has no
  `Non-Compliant` row and `app.py` has no suppression.
- PR #4 is closed, unmerged, and its `cold-review-ruling` run failed.
  `gh api repos/andaro74/agentkeel/rules/branches/main` says whether the
  check is required today.
