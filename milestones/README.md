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
| M01 PR 1 (no tag) | The M00 checks, and `workflow-hash`: every file under `.github/workflows/` is listed in `infra/workflows.sha256` with the sha256 of its content with LF line endings, and every listed file exists. A PR that edits a workflow can edit the list too; nothing stops that until M02. Not yet: manifest schema and cdk-nag (M01 PR 2); seats to groups, edges, cycles, ceilings (M01 PR 2 when a manifest carries them, else M02); CODEOWNERS (M02). |

## Rows

| # | M | Claim | Falsifiers | Seeded commit | Expected gate output | Measured | PRs used / cap | State |
|---|---|---|---|---|---|---|---|---|
| 0 | M00 | Every later number is a delta against a frozen naive baseline | F0.2 an envelope validates without a baseline ref. F0.3 a PR merges without a ruling file after PR 2. Finding F0.1, not a falsifier: baseline passes a trap (recorded at open: `g-012`). Finding F0.4, not a falsifier (ADR-0004, PR 2): the control is non-deterministic at temperature 0. | `22b5499` (F0.1 plant); `f9f1342` (F0.2 seed) | Baseline card written; `score` and `cites` recorded per golden; traps expected 1/3 on the plant, F0.1 recorded as a finding. `g-013` to `g-015` fail and land in `never_passed`; `plants_expected = 0`. A run without a baseline card is rejected by `verdict.build`. From ADR-0004 (PR 2): every result is `scope: control`, so `regressed` is 0 by construction and `checks.F0_2`, `checks.F0_3` decide the verdict. | control: traps 1/3 (g-012); ordinary 0/9; guardrail 0/3; never_passed 14; regressed 0; plants 0/0; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/35406351135; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; GREEN; envelope `9407615dcde09308490f6699c21a18100bfedcd2` | 4 / 4 | GREEN |
| 1 | M01 | An unsigned or tampered bundle never loads; refagent runs inside the construct | F1.1 an unsigned bundle, a bundle altered after signing, a stack with egress not in the manifest, a deploy from a laptop (the developer role), or an agent built outside the construct loads, deploys or synthesises. F1.2 the construct accepts a role without the boundary. F1.3 the agent role can read its own KMS key policy. F1.4 refagent answers an ordinary golden without a `table_row` and a `clause_id` that exist. | `a7b088e` (S1); `df7c735` (S2 content; its signature over S1's bytes is M01 PR 2's first commit, before `src/bundle/verify.py`); `48669ba` (S3); `1b4c2f6` (S4); `19131e9` (S5); `091cc45` (S6); `2f4cacb` (S7); `6b8b8cf` (S8), each its own commit (SPEC/01 §5) | PR 1: no agent under test, so the envelope is the control's, in M00's form (`control_card_ref` null), gated and recorded as at M00; it says nothing about claim 1. `make plants` lists S1–S8, S7's reader in the tree. On S7: 12 of 12 ordinary and trap results `score` true, `cites` false, `pass` false; `checks.F1_4` fail; build and gate RED. PR 2, on the PR: S1, S2 refused by `verify`, each with its planted reason; S3 (both forms), S5, S8 refused at synth; refagent's envelope has `checks.F1_1`, `F1_2`, `F1_4` pass. No count of refagent's passes is expected: agent history is empty (P7), so the checks decide the row. First `main` run after PR 2 merges: S4 and S6 refused and recorded; `checks.F1_3` from S6; refagent answers from inside the construct. | — | 1 / 4 | OPEN |
| 2 | M02 | Seat-owned files change only with a ruling; relaxations need two keys | — | — | — | — | 0 / 4 | OPEN |
| 3 | M03 | The eval gate goes RED on a regression or a silent plant, and never on a never-passed golden | — | — | — | — | 0 / 4 | OPEN |
| 4 | M04 | A breaking model swap goes RED; an equivalent swap promotes; A-vs-A is zero diff | — | — | — | — | 0 / 4 | OPEN |
| 5 | M05 | Five hostile attempts fail and appear in the security account within 10 minutes | — | — | — | — | 0 / 4 | OPEN |
| 6 | M06 | A developer ships a governed agent from the template in under one day | — | — | — | — | 0 / 4 | OPEN |
| 7 | M07 | An agent takes a platform, model or retirement upgrade without a workflow edit | — | — | — | — | 0 / 4 | OPEN |
| 8 | M08 | The platform detects, contains and recovers from a hostile agent end to end; the evidence is complete without anyone editing it | — | — | — | — | 0 / 4 | OPEN |

Rows 1–8 carry the claim from SPEC/00 §7 only. Falsifiers, seeded commit
and expected gate output are written when each milestone opens.
