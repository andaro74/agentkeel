# refagent, the reference agent

refagent answers one kind of question for a film distributor's rights
team: can this title be published in this territory, on this platform, on
this date? The slate, the rights table and the licence clauses are all
fictional. refagent is the example every agent from the template starts as
(`docs/developer/quickstart.md`).

It is small on purpose. One model call, one tool, one table:

| Part | Where | Owner |
|---|---|---|
| The question it is given, and how it must answer | `agents/refagent/prompt.txt` | Engineering |
| The one tool, `check_availability`, which returns the governing row | `agents/refagent/tools/check_availability.json` | Tool Owner |
| The rights table it answers from (40 rows) | `data/rights_table.json`, loaded into DynamoDB on deploy | Data Owner |
| The clauses a row can be read under | `data/clause_index.json` | Data Owner |
| What it must refuse, and the guardrail built from it | `agents/refagent/rules/` | Rule Owner |
| Its model, guardrail, network, owners and limits | `agents/refagent/manifest.yaml` | each field's seat |
| Its tests | `evals/goldens/v1/` (19 live, by kind below) | Data Owner |

## What the record says it does

From the envelope of M06 PR 1's merge (`evals/history/827ee8b….json`, run
in the deployed runtime): ordinary questions 9 of 9, traps 2 of 2,
guardrail cases 2 of 3, red-team attacks 5 of 5, every planted test
fired (7 of 7), 48,667 tokens for the run with the frozen control beside
it. Nothing regressed. One golden, `g-014`, has never passed and does not
gate (it waits for the knowledge base, M07).

What each milestone measured about it, as the ledger records it:

| Row | Claim | State |
|---|---|---|
| 1 | An unsigned or tampered bundle never loads; refagent runs inside the construct | RED |
| 3 | The eval gate goes RED on a regression or a silent plant | GREEN |
| 4 | A breaking model swap goes RED; an equivalent one promotes | RED |
| 5 | Five hostile attempts fail and are recorded within 10 minutes | RED |

A RED row is a finding, not a broken agent: each explainer
(`docs/milestones/`) says what was missed and where it is carried.

## What is not built

No judge: an answer is checked by code, field by field, against the
golden. No human-in-the-loop step. No knowledge base: refagent does not
read the licence text. No calls to or from another agent. No FRAGILE
marking. Each is M07's.

How one question goes through it: `walkthrough.md`.
