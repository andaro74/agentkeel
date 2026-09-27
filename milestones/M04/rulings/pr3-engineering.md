---
# M04 PR 3 (#27), Engineering's key: the code, with the cold review.
# Product's file is rulings/pr3.md; the Threshold Owner's
# pr3-threshold-owner.md; Security's pr3-security.md.
ruling: pr3-engineering
seat: Engineering
authorises:
  - Makefile
  - scripts/observe_pr.py
  - scripts/rule_swaps.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/schema.json
  - tests/test_build.py
  - tests/test_construct.py
  - tests/test_evals_workflow.py
  - tests/test_gate.py
  - tests/test_m04_seeds.py
  - tests/test_observe_pr.py
  - tests/test_refagent.py
  - tests/test_rule_swaps.py
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#4-falsifiers
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - milestones/M04/rulings/pr3.md
  - https://github.com/andaro74/agentkeel/pull/25
  - https://github.com/andaro74/agentkeel/pull/26
pr: 27
---

# M04 PR 3, the repair: Engineering's cold review

Read cold by `engineering-cold-reviewer`: `git diff da6feae...fe31b6c`
(23 files) and ledger row 4 only. 2 BLOCK, 2 FINDING, 8 NOTE; the report
is in the PR body verbatim. `threshold-owner` (0, 1, 11) and
`security-reviewer` (2, 4, 6) read the same diff; their items are ruled
in `pr3.md` and `pr3-security.md`. All three reports say they read the
diff. The human rules as Engineering before the merge.

## Dispositions

| # | Item | Status |
|---|---|---|
| B1 | A swap branch could replace the gate that rules it (the card path came from the envelope; one worktree for both swaps) | **Repaired**: the two paths are fixed from the measured sha, read at the bot's commit; a fresh worktree per swap; the card is not written over other bytes at HEAD; the gate's environment has no credentials. The same item as security-reviewer B1. `test_an_envelope_naming_another_card_path_cannot_put_code_where_the_gate_imports` |
| B2 | `rule_swaps` parsed the envelope: a reader outside `build`, `gate` and `replay_history` | **Repaired** with B1: it copies bytes and reads only the gate's own `--json` output. `test_it_reads_no_envelope_and_rules_on_nothing_itself` |
| F1 | The evals job could fail because of a swap | **Repaired**: any failure for one swap is its `verdict: null` with a note; the gate REJECTs a file that is not UTF-8 instead of crashing (a gate bug the test found); `build` takes an empty list as no field. `test_nothing_on_a_swap_branch_stops_the_run` |
| F2 | PR 4 could re-run the equivalent swap's result | **Ruled** (Product, `pr3.md` §3, drafted): the first run decides F4.2; a GREEN at PR 4 is recorded beside it |
| N1 | Shape | **Recorded**: the machinery lands and runs here, PR 4's run reads (row 1's precedent) |
| N2 | The seeds are not weakened on `main`; on a moved pin the incumbent lookup is a constant | **Recorded**. Each seed was also run with its reader switched off on Sonnet 4.5's pin: S1, S3, S4 and S5 each failed on its planted assertion |
| N3 | `test_refagent` no longer names the model | **Recorded**: the gate and the Threshold Owner hold the pin |
| N4 | The Measured cell cannot answer F4.1 or F4.2 by itself | **Recorded**: the close reads `swaps[].reasons`, `required_on_head` and `evals_on_measured` in the envelope, and says so in the row |
| N5 | The recorded verdict is HEAD's gate over HEAD's history, for the last commit the bot measured | **Recorded**: `envelope_commit`, `measured_commit` and `evals_on_measured` are kept beside it |
| N6 | "566 passed" | **Recorded**: that count is the full suite on each swap's pin, before the read's tests were added; this head: 582 passed, 1 skipped |
| N7 | A badly joined condition in `build.py` | **Repaired** in the F1 rewrite |
| N8 | The Security ruling's readback | **Recorded**: `pr3-security.md` §3, from the human's saved `cdk diff` and `get-role-policy` output |

## The second read (`fe31b6c..e8ab126`)

`engineering-cold-reviewer` read the repair: 0 BLOCK, 4 FINDING, 7 NOTE,
verbatim in the PR body. It found B1, B2, the credentials item and F1 held
against every attack it tried.

| # | Item | Status |
|---|---|---|
| F1 | `card_at` crashed on a card that was not UTF-8 or not a mapping | **Repaired**: REJECTED; and with `--strict-cards` no card is opened off its fixed path |
| F2 | The credentials test would pass with the repair reverted | **Repaired**: the test captures the gate's process at the call site: its environment, `--strict-cards`, its timeout, and a different worktree for each swap |
| F3 | Three hostile cases had no test; "a worktree per swap" was not tested | **Repaired**: the timeout, the card over other bytes, the card-write path real swaps take, and a worktree per swap are each a test; the README says only what is tested |
| F4 | Row 4's Falsifiers cell said PR 4's run decides F4.2 | **Repaired** (Product): the cell says the first run decides, read again at PR 4 |
| N1 | The `evals.yml` comment | **Repaired** (Security) |
| N2 | The joined line in `observe_pr.py` | **Repaired** |
| N3 | No swaps observed means no field, silently | **Recorded**: PR 4's read rests on `f4_swaps.yaml` listing both, and on the row's "RED if PR 4's run cannot read the swap PRs" |
| N4 | The spoofable bot author | **Recorded**, in `pr3-security.md` §1 |
| N5 | `show()` reads a whole blob | **Recorded**: bounded by 60 s per call |
| N6 | The P5 guard is a string match | **Recorded** |
| N7 | No CI envelope carries `swaps` yet | **Recorded**: this PR's own run is its first |

## Falsify it

    git diff --stat da6feae...HEAD -- src/baseline/            # empty
    uv run pytest -q                                           # all pass on a clean tree
    uv run pytest -q tests/test_rule_swaps.py -rA              # the hostile cases
    uv run python -m src.validate                              # exit 0
    uv run python -m src.gates.ruling_cited --base origin/main --pr 27
    grep -n "json.loads(envelope" scripts/rule_swaps.py        # nothing (B2)
    GITHUB_TOKEN=$(gh auth token) uv run python scripts/observe_pr.py milestones/M04/runs/f4_swaps.yaml --out swaps.json
    uv run python scripts/rule_swaps.py swaps.json --out swaps-ruled.json   # local, not evidence
