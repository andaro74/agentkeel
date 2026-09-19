---
adr: ADR-0004
title: Measurement fields; the control is never gated
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Product          # §5 gate list, §6 envelope fields, §8 M00 expected output, §10.3 command name
  - Threshold Owner  # cost-cap lives in thresholds.yaml; the regression bar reads the agent under test
  - Data Owner       # scope on every per-golden result
  - Engineering      # the envelope schema, verdict.gate, replay_history, `make ledger-plain`
amendments: 0
---

# ADR-0004 — Measurement fields; the control is never gated

ADR-0002 stays reserved for the baseline freeze at the M00 close PR.

## Context

M00 PR 2 built the reader and measured. Four things it built were not in
SPEC/00, and the cold review and the Threshold Owner's report said so
(`milestones/M00/rulings/pr2.md`, FINDING 6 and FINDING 9):

1. The envelope carried `checks`, which §6 did not list.
2. `cost-cap` read `thresholds.yaml` at M00. §5 put the cap "in
   `evals.yml`" and §8 listed `cost-cap` under M03.
3. The regression bar read the baseline. The baseline is not
   deterministic at temperature 0: across three runs on one prompt hash
   the one ordinary golden it got right was `g-001`, then none, then
   `g-006` (`milestones/M00/feasibility.md` §6.5). Once CI recorded a
   pass, the next run where that golden failed would go RED with no
   change to the code. Row 0 said to record that. The gate blocked on it.
4. `make ledger --plain` cannot run. GNU make takes `--plain` for an
   option of its own and exits 2.

## Decision

1. **`scope` on every per-golden result.** Threshold Owner, Data Owner.
   `control` or `agent`. No third value until a milestone needs one. It
   is on each result in the envelope, and once on the baseline card
   (`scope: control`). `verdict.build` works it out: a run is the control
   when its raw observations are the ones the card was scored from.
   Nobody passes it in.
2. **The control is never gated.** Threshold Owner. The regression bar
   applies to the agent under test. `verdict.gate` reads `scope: agent`
   results for `regressed` and for the plant count. `control` results
   are reported in the envelope and in the gate's one-line reading, and
   never block. An envelope cannot call a result `control` to get out
   from under the bar: the gate rejects a `control` result that differs
   from the baseline card's.
3. **`replay_history` keys on (scope, golden id).** A control pass is not
   an agent pass, so the baseline's luck does not become refagent's bar
   at M01. Control history is kept for the M04 A-vs-A comparison, not
   for gating.
4. **At M00 every result is `control`.** `regressed` is 0 by
   construction. `checks.F0_2` and `checks.F0_3` decide the verdict.
5. **`checks` is an envelope field.** Keyed by falsifier id; each entry
   is `pass` or `fail` and the URL of the CI evidence. A failed check is
   RED whatever the scope.
6. **`cost-cap` reads `thresholds.yaml`**, the Threshold Owner's file,
   from M00 PR 2: tokens per run. `evals.yml` is Security's path; a bar
   there would not be the Threshold Owner's to move. A cap relaxes
   upward, and raising it needs two keys.
7. **`make ledger-plain`** is a separate target. Engineering. SPEC/00
   and CLAUDE.md no longer name `make ledger --plain`.
8. **Finding F0.4, not a falsifier.** Product. The control is
   non-deterministic at temperature 0. It is recorded run by run in
   feasibility.md §6.5, with any trap count other than 1/3, and it is
   the seed for SPEC/04's A-vs-A design. It does not decide row 0.

## Schema compatibility

Engineering, Product. `scope` is required from this commit. The one
envelope written before it, for `8fb4b80`, no longer validates. It moves
to `evals/history/pre-scope/`, outside the folder `replay_history` reads,
and stays cited in `rulings/pr2.md` as the gate before scope existed.
`replay_history` refuses a file that does not validate, as built. There
is no tolerance flag. The move is a human commit under `evals/history/`,
which ADR-0003 makes a two-key change: the two keys are Engineering and
Product, and `two-key` itself is not built until M02.

## Consequences

- SPEC/00 §5 (`regression`, `cost-cap`), §6 (envelope fields), §8 M00
  (expected gate output, Finding F0.4) and §10.3, §10.4, §15 (the command
  name) are amended in the same commit.
- §8 M03 still lists `cost-cap` as M03 build, and §14 still says "per-PR".
  The bar is per run today. What M03 adds to it is SPEC/03's to say.
- A delta against the control now has a base that moves from run to run.
  Which card a later envelope points at (the same run's, or the `m00`
  card as a fixed reference) is still the Threshold Owner's to rule,
  before M01 PR 1.
- One envelope per commit holds one scope at M00. From M01 a run has two
  subjects, the control and refagent. Whether they share an envelope is
  M01 PR 1's to settle; the schema allows both scopes in one file.
- A guardrail plant is counted on `agent` results only. The baseline has
  no guardrail and never will, so from M03 a control run does not go RED
  on three plants it cannot fire.
