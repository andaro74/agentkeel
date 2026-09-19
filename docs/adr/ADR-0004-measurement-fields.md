---
adr: ADR-0004
title: Measurement fields; the control is never gated
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Product          # §5 gate list, §6 envelope fields, §8 M00 expected output, §10.3 command name; amendment 1: how a PR lands on main; amendment 2: §6's $id sentence, checks.F1_4
  - Threshold Owner  # cost-cap lives in thresholds.yaml; the regression bar reads the agent under test; amendment 2: the frozen base, the cap for two subjects, over-cap is RED
  - Data Owner       # scope on every per-golden result
  - Engineering      # the envelope schema, verdict.gate, replay_history, `make ledger-plain`; amendment 2: one subject per envelope, control_card_ref, tokens_in, F1.4 in build and gate
amendments: 2
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

## Amendment 1 (M00 PR 3, 2026-09-18)

Two items, ruled at the close.

**1. A PR lands on `main` as a merge commit. Product.** Not a rebase, not
a squash.

Envelopes are keyed to the commit they measured:
`evals/history/<commit>.json`, and the `commit` field inside it. A rebase
or a squash rewrites that commit, so the file names a sha that is on no
branch, and `evals.yml`'s "is this tree already measured?" step
(`git merge-base --is-ancestor`) stops finding it. The measurement would
have to be taken again to say the same thing.

The second reason is authorship. `evals/history/**` is CI-written
(ADR-0003): the `record` job commits as `github-actions[bot]`, and who
wrote the file is part of what makes it evidence. A squash puts the
merging human's name on the bot's commit. A rebase re-signs it. Either
way the tree stops showing that no human wrote the envelope.

So:

- The repository ruleset on `main` keeps `merge` in
  `allowed_merge_methods` and does not add `required_linear_history`.
  Security owns the ruleset; on 2026-09-18 it allows merge, squash and
  rebase, and has no linear-history rule. Nothing to change today. It is
  named here so that adding one later is a change to this ADR.
- CLAUDE.md was to lose the words "linear history". The phrase is not in
  CLAUDE.md, or anywhere else in the tree — `grep -rn linear` finds
  nothing. There was nothing to remove, and this paragraph is the record
  of having looked.
- `git log --merges main` is what F0.3 is read on
  (`milestones/M00/feasibility.md` §5). A squashed PR has no merge commit
  for that grep to find, so the falsifier's own observer depends on this
  rule.

**2. Which card a later envelope points at (report 1.4). Engineering,
for M01 PR 1.** ADR-0004 left this open under Consequences. A later
envelope points at the baseline card **at tag `m00`**, by the content
hash of that card, recorded once as `baseline_card_sha` in
`thresholds.yaml`. A card whose hash differs is a build error, not a new
base. That is the fixed reference the Consequences paragraph named as one
of two options; the other, "the same run's card", is what PR 2 built and
what M00's own measurement used.

Not built here. It is noted in `milestones/M00/feasibility.md` §7 and
built at M01 PR 1. `thresholds.yaml` is the Threshold Owner's file, so
the line that lands in it carries the Threshold Owner's key as well as
Engineering's.

## Amendment 2 (M01 PR 1, 2026-09-19)

The last amendment this ADR can take. The next change to these fields is
a new ADR. Ruled for M01 PR 1 (`milestones/M01/rulings/pr1.md`; M01 open
items 2, 5, 11 and 22, and the ruling on `product-spec-reviewer` BLOCK 3,
`milestones/M01/feasibility.md` §2).

**1. The base is the card at tag `m00`, by hash, in `thresholds.yaml`.**
Engineering with the Threshold Owner, two keys. Amendment 1 named the
field `baseline_card_sha`; it lands as

```yaml
baseline_card:
  path: evals/history/9407615dcde09308490f6699c21a18100bfedcd2.baseline-card.json
  sha256: b0219756cad63be67fb51aa4632dd015084840833341f15235fab4569adc3295
```

"At tag `m00`" means the card row 0 cites, not the last card on the
tagged tree (`55dadb2`). The hash is of the card's content
(`canonical_sha256`), so line endings do not move it.

**2. One envelope per commit, one subject: the agent when one ran,
otherwise the control.** Engineering with the Threshold Owner. The control
is still re-run on every `make evals` (P6), and `build card` writes
`<commit>.baseline-card.json` as before.

- **An agent ran.** The envelope's `goldens` hold `scope: agent` results
  only. It names this run's control card in a new field,
  `control_card_ref: {path, sha256}`. `baseline_card_ref` names the
  frozen card of item 1, and `build` refuses (exit 3) unless its hash
  equals `thresholds.yaml` `baseline_card.sha256`. The check that a card
  is for the run's own commit moves to `control_card_ref`.
- **No agent ran.** The envelope is the control's, in M00's form:
  `goldens` hold `scope: control` results, `control_card_ref` is null,
  and `baseline_card_ref` names this run's own card, commit-matched, as at
  M00. M01 PR 1's run is this case: refagent's runner is M01 PR 2.

A run always writes an envelope (ruling A on the M01 PR 1 Unsure items,
which replaces the earlier ruling that such a run writes the card only).

**3. Schema.** Engineering. `control_card_ref` (object or null) and
`tokens_in` (integer ≥ 0) join the schema and are **not** in `required`,
so M00's three envelopes still validate and replay. `verdict.gate`
rejects an envelope that has any `scope: agent` result and:

- also has a `scope: control` result;
- lacks `control_card_ref` or `tokens_in`;
- names a `baseline_card_ref` whose hash is not `thresholds.yaml`'s;
- names a `control_card_ref` that does not resolve, does not hash to the
  ref, or is for another commit.

An envelope with control results only is read by M00's rules, and is
rejected if it names a `control_card_ref`. The `thresholds.yaml`
`baseline_card` hash is checked only when a result is `scope: agent`.

**4. F1.4, read twice (SPEC/01 §4).** Engineering; Product for the check.
For `scope: agent` results of kind `ordinary` and `trap`,
`pass = score and cites`. `build` also writes `checks.F1_4`: `fail` when
any `scope: agent` result of kind `ordinary` has `cites: false`, with the
CI run URL. A failed check is RED whatever the history, so refagent
answering without citing turns the row RED on its first run (ruling on
BLOCK 3). `verdict.gate` works both out again from `score` and `cites`
and goes RED where the envelope differs. The control is scored as it was:
the card's composition does not change, because its hash is the base.

**5. Over the cap is a recorded RED.** Threshold Owner (M01 item 22).
`cost-cap` no longer exits before `build`: it prints the spend and exits
0. `build` writes `tokens_in` and sets the verdict RED when
`tokens_in + tokens_out` is over `cost_cap.tokens_per_run`. The gate
works out the same from the envelope and `thresholds.yaml` and gives the
reason `cost-cap: N over M`. Two readers, one rule, P5 holds. The cap for
two subjects is 150,000 tokens, an upward move with two keys (Threshold
Owner and Engineering). `tokens_in` and `tokens_out` on the envelope are
the run's: on an agent envelope, the agent's replies plus the control
card's totals, so the cap covers what the run spent; on a control envelope,
the control's. An over-cap control-only run is a recorded RED like any
other (ruling A).

**6. Control drift (Finding F0.4).** The gate prints this run's control
card counts beside the frozen card's, as a note. Not gated.

**7. The Measured cell** for an agent envelope reads:
`agent: traps a/3; ordinary a/9; guardrail a/3; control: <this run's
control card tallies>; never_passed n; regressed n; plants f/e; checks…;
VERDICT; envelope <commit>; base b0219756`. Row 0's cell, on an M00
envelope, is unchanged, and `make ledger` still exits 0 on it.

**8. Agent history starts empty at M01.** `replay_history` keys
`(agent, id)` have no rows until refagent's first CI envelope.

**9. SPEC/00 §6** (M01 item 2, Product) gains, after "Envelope
(`verdict.schema.json`": "— the schema's `$id`; the file is
`src/verdict/schema.json`". Both names were true, and a reader had to
know that.

## Consequences

- Amendment 1 used the first of this ADR's two amendments. Amendment 2
  uses the second. The next change to these fields is a new ADR.
- SPEC/00 §5 (`regression`, `cost-cap`), §6 (envelope fields), §8 M00
  (expected gate output, Finding F0.4) and §10.3, §10.4, §15 (the command
  name) are amended in the same commit.
- §8 M03 still lists `cost-cap` as M03 build, and §14 still says "per-PR".
  The bar is per run today. What M03 adds to it is SPEC/03's to say.
- A delta against the control now has a base that moves from run to run.
  Which card a later envelope points at (the same run's, or the `m00`
  card as a fixed reference) was left open here and is ruled in
  amendment 1, item 2: the `m00` card, by content hash.
- One envelope per commit holds one scope at M00. From M01 a run has two
  subjects, the control and refagent. Whether they share an envelope is
  M01 PR 1's to settle; the schema allows both scopes in one file.
- A guardrail plant is counted on `agent` results only. The baseline has
  no guardrail and never will, so from M03 a control run does not go RED
  on three plants it cannot fire.
