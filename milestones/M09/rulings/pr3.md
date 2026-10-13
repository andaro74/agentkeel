---
# M09 PR 3 (#52), the repair. Product's key over the Product paths this PR
# touches: this milestone's README (the repair detail and the by-hand steps
# for PR 4's run) and the three ruling files. The Security file is
# pr3-security.md (the bootstrap), the Engineering file pr3-engineering.md
# (the platform check's name reading, the tests, the cold review).
ruling: pr3
seat: Product
authorises:
  - milestones/M09/README.md
  - milestones/M09/rulings/pr3.md
  - milestones/M09/rulings/pr3-security.md
  - milestones/M09/rulings/pr3-engineering.md
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/rulings/pr2.md
pr: 52
---

# Ruling: M09 PR 3, Product

Ruled by andaro74 as Product, 2026-10-12, as written.

## What this PR is

PR 3 of 4, **the repair**, not the run. SPEC/09 §5.1 stated this case at
open: "if the platform's own deploy path needs a repair, PR 3 is that
repair and the plant run is read by PR 4's run, which the cell cites" (M08's
second exception). The deploy path needed two: the execution role's
`CreateGuardrail` grant that never applied (Security, read from the Service
Authorization Reference before any deploy), and the held-pin check that
refused the agent's own folder (Engineering, read from the first deploy's
refusal, run 38259465892). Both are in this PR. The cap stays at four:
PR 4 records the run and closes.

## What is ruled here

1. **The run moves to PR 4, as stated.** The cell cites PR 4's run's
   envelope. Expected on it is unchanged from open (SPEC/09 §7): fired 1 of
   1, F9.1 to F9.5 held, row 9 GREEN, with two readings open for that
   deploy (`pr3-security.md`, item 4 and "What the first deploy read").
2. **R8 is made.** `agentkeel-studio/festival-desk` exists, public, from the
   template, with the platform ruleset equal to the export; its first pull
   request was admitted and merged at `cd0ad604`. The second and third pull
   requests wait for this PR's merge and the deploy that follows.
3. **R9 stands.** `g-030` is unchanged; no golden under `evals/goldens/`
   or in the fixture is touched by this PR. Whether the rule fires on it is
   PR 4's reading.
4. **The README's repair detail and the by-hand steps for PR 4's run** are
   written as this file's companion; the run file is unchanged, `observed:
   null`, until the owner fills it after the deploy.
5. **The by-hand deploy's record.** The bootstrap was deployed from this
   branch on a draft of `pr3-security.md` Security had read but not
   committed as ruled (cold review F2). The README and that file say so,
   and the deployed policies are read back from the account in that file;
   the deploy stands on the "Ruled by" the file receives before this PR
   merges. Product records the sequence; it changes no reading.
6. **PR numbering.** The Rule Owner's version-6 pull request, a by-hand
   step outside the milestone's count, took `#51`, so this PR is `#52`; the
   first draft of `pr3-security.md` said 51 and was corrected before this
   PR opened. The milestone's PR count is still 3 of 4.

## Unsure, for Product

- Whether the two fixtures `#51` had to move (`refagent-version-6-engineering.md`)
  are a finding worth a line in the close: a platform pin bump reaches
  seeds that hard-coded "the platform's version". Proposed: one line in
  M09's close under findings, Engineering's.
- Whether the App installation note (`pr3-security.md`) is a SPEC/06
  correction at M09's close or stays a Security Unsure. Proposed: the
  close names it; SPEC/06 is amended only if Security rules the
  installation stays "selected".

## What a reader can run

```
git diff f5ecb25...HEAD --stat -- milestones/                      # README.md and the three pr3 rulings; the run file untouched
git diff f5ecb25...HEAD -- milestones/M09/runs                    # empty
grep -n "observed: null" milestones/M09/runs/f9_3_plant_run.yaml   # still null
gh pr view 1 -R agentkeel-studio/festival-desk --json mergeCommit -q .mergeCommit.oid   # cd0ad60490ad66a55e201eacda9e09b732a99a7c
make ledger                                                        # row 9 OPEN, Measured empty; "as row M09 reads it" RED on agent_rules not made
```

A changed golden, a filled `observed`, a Measured cell written here, or a
fifth PR proposed, makes this ruling wrong.
