---
# M02 PR 3 (#13), Security's key on the ruleset export. The rest of PR 3's
# rulings are written in the PR 3 session.
ruling: pr3-security
seat: Security
authorises:
  - infra/ruleset/main.json
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-security.md
pr: 13
---

# Ruling: M02 PR 3, Security (the export)

`ruling-cited` and `two-key` were made required on the live `main`
ruleset after PR 2 merged, and the ruleset was exported at once as this
PR's first commit (pr2-security.md item 4). `bypass_actors` is `[]`.
