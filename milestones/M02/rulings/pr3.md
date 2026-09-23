---
# M02 PR 3 (#13), Product's key, for the run file carried onto the branch
# from PR 2's merge. Security's file is rulings/pr3-security.md,
# Engineering's rulings/pr3-engineering.md. The rest of PR 3 (the reading
# of the seed PRs and the doors, the ledger, the explainer if this is the
# close) is written in the PR 3 session, and this file grows then.
ruling: pr3
seat: Product
authorises:
  - milestones/M02/runs/row10_first_deploy.yaml
  - milestones/M02/runs/f2_1_seed_prs.yaml
  - milestones/M02/runs/f2_1_bypass.yaml
  - milestones/M02/runs/f2_2_three_doors.yaml
  - milestones/M02/rulings/pr3.md
  - milestones/M02/rulings/pr3-engineering.md
evidence:
  - SPEC/00-overview.md#8-M02
  - https://github.com/andaro74/agentkeel/actions/runs/35817173042
pr: 13
---

# Ruling: M02 PR 3, Product (row 10 read)

Drafted by the session; the human rules as Product before the merge.

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
