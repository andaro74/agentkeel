---
# M02 PR 3 (#13), Product's key. Security's file is rulings/pr3-security.md,
# Engineering's rulings/pr3-engineering.md; the cold review of this PR is
# rulings/pr3-cold-review.md, Engineering's second file, which names only
# itself. This file was opened with the row 10 reading and the three run
# files at the start of the branch and grew in the PR 3 session.
ruling: pr3
seat: Product
authorises:
  - milestones/M02/runs/row10_first_deploy.yaml
  - milestones/M02/runs/f2_1_seed_prs.yaml
  - milestones/M02/runs/f2_1_bypass.yaml
  - milestones/M02/runs/f2_2_three_doors.yaml
  - milestones/M02/rulings/pr3.md
  - milestones/M02/rulings/pr3-engineering.md
  - milestones/README.md
  - milestones/M02/README.md
  - milestones/M02/attestations.md
  - milestones/M03/open.md
  - CLAUDE.md
  - docs/milestones/M02.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/platform/overview.md
evidence:
  - SPEC/00-overview.md#8-M02
  - evals/history/8033c2a7a0588e557df577464c190e64a435e88a.json
  - https://github.com/andaro74/agentkeel/actions/runs/35951008874
  - milestones/M02/rulings/pr3-cold-review.md
  - SPEC/02-seats-and-change-gates.md#4-falsifiers
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-cold-review.md
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
  - https://github.com/andaro74/agentkeel/actions/runs/35861180676
  - https://github.com/andaro74/agentkeel/actions/runs/35874322479
pr: 13
---

# Ruling: M02 PR 3, Product (row 10 read; the reading; the close)

Ruled by andaro74 as Product, 2026-09-24.

## The close

This PR closes M02 through `/close-milestone`: the cold review of PR 2
found repairs and this PR carried them, its own cold review found no
BLOCK, and its run read what row 2 expected. The Measured cell in
`milestones/README.md` is the line `make ledger` prints for the envelope
`8033c2a7a0588e557df577464c190e64a435e88a` (run 35951008874, recorded by
`github-actions[bot]` in `905f438`), copied by a script and never
retyped; `make ledger` exits 0; State GREEN; PRs used 3 / 4. The close
detail in `milestones/M02/README.md` checks the envelope against row 2's
four RED conditions and lists every finding and Unsure item with its
home; `milestones/M03/open.md` carries what is not closed.
`docs/milestones/M02.md` "What happened" uses the envelope's numbers and
says what GREEN does not mean. `docs/video/README.md` gains M02's row and
corrects M01's, which said "not recorded" after the file had landed and
whose recording is 6:09, over the five-minute ceiling. `docs/milestones/
README.md` is `make ledger-plain`'s. `git tag m02` is the human's, on
`main`, after the merge.

Two numbers changed from what a reader of PR 2 would expect, and why:
the agent's traps are 2/3, not 3/3, because `g-012` was retired at PR 2
and `g-021` took its place never passed; `never_passed` is 4, not 3, for
the same reason. Both are the envelope's, and the checks decide the row.

Two Unsure items of this PR are ruled here rather than carried: B, the
constant stays PR 2's merge commit as SPEC/02 §4 says, with the three
earlier branch envelopes recorded as RED under it; E, the two new reads
in the token step warn rather than fail, and the check names its witness.

`milestones/M02/runs/row10_first_deploy.yaml` gains
`observed_at_pr2_merge`, read from run 35817173042 and the account on
2026-09-23: the arm64 image built fresh, the stack `UPDATE_COMPLETE`,
the runtime started and answered every golden, and every answer was
`AccessDeniedException` on `dynamodb:Scan` because the agent boundary,
not the role, refused it. Two of row 10's three open readings close
(the load check's answer; the runner carries `docker` and `aws`); the
third, cfn-exec's `vpc-lattice` actions, stays open: CloudTrail holds no
such event by any principal. The file is valid YAML again; it had not
been since `d8783f6`.

M01 row 1 stays RED as ruled at its close: a later deploy does not
reopen it. This reading is M02 PR 3's.

## The three run files, filled by the human on 2026-09-23

`f2_1_seed_prs.yaml`: PRs 14 to 18, opened from `main` between 13:10Z
and 13:11Z. `f2_1_bypass.yaml`: attempt 1 refused at 13:34:13Z (rule
suite 4192991324, the API's record; Unsure B answered yes); attempt 2
at 13:40Z, validate RED in run 35862459367's `evals` job while the
repository-admin role was listed, restored at 13:45:29Z.
`f2_2_three_doors.yaml`: doors 1 and 3 are PR 14, door 2 is PR 12.
Run once against the API before this PR's run depends on them: every
seed refused with its path named, both attempts witnessed, three doors
in the record. The reading itself is PR 3's run.

## The ledger at PR 3

`milestones/README.md` row 2's Expected cell gains one amendment, in
bold, after the P3 exception it already names, and
`milestones/M02/README.md` carries the same cell and a PR 3 detail
section. The amendment says four things a reader of the row needs and
the row did not: which commit sets the constant PR 2's cold review
asked for first (`74624cb`); that the three agent envelopes this branch
recorded before it (`12b4646`, `47258f2`, `6daf6c4`) carry `F2_1` alone
and rule RED under it, with no Measured cell citing them; which run is
the reading (the `evals` run on PR 3's head after `939709d`) and what it
looks up; and, beside claim 2 and not as part of it, that `12b4646`'s
run was the first envelope in `mode: runtime`, GREEN at 54,218 tokens,
after the boundary took `dynamodb:Scan`. Row 1 is not reopened by it.

The header table gains a row for M02 PR 3: `validate` is unchanged but
for the ruling front-matter check, which now also matches a glob against
paths deleted from the tree (Engineering, `c7a8242`). The reason is
recorded there: `infra/eval-role/` is removed in this PR and four M00
and M01 rulings authorise files under it. This ruling records the gap
that change closes as a finding for Product: **a ruling cannot name a
deletion precisely.** `ruling-cited` requires a deleted path to be
covered by a glob, and the front-matter check refused any glob that
matched nothing in the tree, so before `c7a8242` the only way to delete
an authorised file was a glob broad enough to match its neighbours.
The check now reads history; SPEC/02 §2 does not say how a ruling names
a deletion, and that sentence is M03 PR 1's, with the closed-list
amendment already assigned there.

`CLAUDE.md`'s "Where things are" says `infra/eval-role/` is gone.

## Findings recorded here, with their homes

| # | Finding | Home |
|---|---|---|
| 1 | The three branch envelopes before the constant rule RED under it | Recorded in row 2's cell and `tests/test_gate.py`; nothing cites them; no action |
| 2 | `time_period=month` on the rule-suites list: after a month the list no longer holds attempt 1 | Engineering, `ab6219d`: the recorded suite is read by id, which does not age; the list is kept beside it and the observation says which source it read |
| 3 | A ruling cannot name a deletion precisely (above) | Product, SPEC/02 §2 at M03 PR 1 |
| 4 | The bot exemption still reads `%an` (PR 2 cold F4) | Security, M05, unchanged |
| 5 | The reading is made by the PR's own code (`evals.yml` header, first gap) | Unchanged; M05 |
| 6 | `f2_2_three_doors.yaml` carries two top-level `doors:` keys: the human's fill appended a block instead of editing the first, which still says door 3 `pr: null` (cold F1, security F2). PyYAML keeps the last mapping, so the observer reads the filled block and the reading is unchanged; a strict loader would refuse the file | Product, the human: the session does not edit run files. Collapse the two blocks before the merge, or leave the duplicate as the record of the fill; either way the reading stands. Named under **Unsure** in the PR body |
| 7 | `feasibility.md` §6 row 16 dated the `infra/eval-role/` removal to PR 2 and `open.md` row 16 to PR 1; it landed in PR 3 (`b7311b3`) after the destroy (platform N5) | Recorded here; neither file is rewritten |
| 8 | The ceiling refused a call once, unplanned (run 35817173042), and SPEC/01 §9 lists it as a control with no seeded case (platform F2) | Product, SPEC/01 §9 at M03 PR 1: "observed once, unplanned"; a seeded case at M05, Security |
| 9 | `validate`'s front-matter check accepts any glob that ever matched a deleted path, and a rename is not a deletion (cold N4, security N15) | Inside finding 3, SPEC/02 §2 at M03 PR 1 |

## What a reader can run

```
uv run python -m src.ledger                       # row 2's cell is still —; the latest envelope's line
git show 74624cb --stat                           # the constant, its fixture flags, its tests
git show 939709d --stat                           # the wiring and S4's marker, one commit
git show 6daf6c4:tests/test_m02_seeds.py | grep -c xfail   # 2 before (the marker and the docstring); 1 at HEAD, the docstring
```
