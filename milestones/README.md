# Ledger

One file. `make ledger` and `docs-current` read it. Rows are written on
milestone open and the "Measured" cell is filled at close.
`docs/milestones/README.md` is generated from this file by
`make ledger-plain`; neither exists before M00 PR 2.

The adoption PR (#1, `milestones/adoption/rulings/adopt-spec00.md`) is
not counted against any milestone's cap of four.

States: OPEN → GREEN | RED | UNMEASURED | UNSCHEDULED (two-key) | RETIRED.
A milestone that closes without a measurement is RED.

## What `make validate` checked, by tag

"validate was green" means only what its row here says.

| At | `make validate` checks |
|---|---|
| M00 PR 1 (no tag) | Golden files `evals/goldens/v1/g-NNN.yaml`: the §6 fields and no others, `id` format `g-NNN` and equal to the file name, no duplicate id, `kind` in `ordinary\|trap\|guardrail\|redteam`, `expected` shaped for its kind, `added` a milestone id (`MNN`), `retired` null or a milestone id. Ruling files `milestones/*/rulings/*.md`: front matter has `ruling`, `seat`, `authorises`, `evidence`, `pr`; every `authorises` path matches something in the tree. Every ordinary and trap golden's `table_row` is in `data/rights_table.json` and its `clause_id` is in `data/clause_index.json`. Nothing else: not answers, not seats, not that an id never changed. |
| `m00` (this tag) | The same three checks, unchanged. `validate` did not grow in M00 PR 2 or PR 3: it still reads only golden front matter, golden citations and ruling front matter. It does not read an envelope, a seat, a measured cell or the baseline. The freeze on `src/baseline/` (ADR-0002) is held by `pytest`, not by `validate`. Schema, seats, edges, semver and cdk-nag are M01+. |

## Rows

| # | M | Claim | Falsifiers | Seeded commit | Expected gate output | Measured | PRs used / cap | State |
|---|---|---|---|---|---|---|---|---|
| 0 | M00 | Every later number is a delta against a frozen naive baseline | F0.2 an envelope validates without a baseline ref. F0.3 a PR merges without a ruling file after PR 2. Finding F0.1, not a falsifier: baseline passes a trap (recorded at open: `g-012`). Finding F0.4, not a falsifier (ADR-0004, PR 2): the control is non-deterministic at temperature 0. | `22b5499` | Baseline card written; `score` and `cites` recorded per golden; traps expected 1/3 on the plant, F0.1 recorded as a finding. `g-013` to `g-015` fail and land in `never_passed`; `plants_expected = 0`. A run without a baseline card is rejected by `verdict.build`. From ADR-0004 (PR 2): every result is `scope: control`, so `regressed` is 0 by construction and `checks.F0_2`, `checks.F0_3` decide the verdict. | control: traps 1/3 (g-012); ordinary 0/9; guardrail 0/3; never_passed 14; regressed 0; plants 0/0; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/35406351135; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; GREEN; envelope `9407615dcde09308490f6699c21a18100bfedcd2` | 3 / 4 | GREEN |
| 1 | M01 | An unsigned or tampered bundle never loads; refagent runs inside the construct | — | — | — | — | 0 / 4 | OPEN |
| 2 | M02 | Seat-owned files change only with a ruling; relaxations need two keys | — | — | — | — | 0 / 4 | OPEN |
| 3 | M03 | The eval gate goes RED on a regression or a silent plant, and never on a never-passed golden | — | — | — | — | 0 / 4 | OPEN |
| 4 | M04 | A breaking model swap goes RED; an equivalent swap promotes; A-vs-A is zero diff | — | — | — | — | 0 / 4 | OPEN |
| 5 | M05 | Five hostile attempts fail and appear in the security account within 10 minutes | — | — | — | — | 0 / 4 | OPEN |
| 6 | M06 | A developer ships a governed agent from the template in under one day | — | — | — | — | 0 / 4 | OPEN |
| 7 | M07 | An agent takes a platform, model or retirement upgrade without a workflow edit | — | — | — | — | 0 / 4 | OPEN |
| 8 | M08 | The platform detects, contains and recovers from a hostile agent end to end; the evidence is complete without anyone editing it | — | — | — | — | 0 / 4 | OPEN |

Rows 1–8 carry the claim from SPEC/00 §7 only. Falsifiers, seeded commit
and expected gate output are written when each milestone opens.
