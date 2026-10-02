# The `platform-app` environment, read back (open.md row 20; SPEC/07 section 11, R1)

Read-only reads of GitHub's API by `andaro74`'s own token (`gh`, an admin
of `andaro74/agentkeel`), made in M07 PR 1's session. Two readings by
hand. Neither is a check and neither has fired on a seeded case: the
seeded refusal is S0's second attempt (`f7_0_owner_test.yaml`), made
before any grant.

| Read at (UTC) | Command | Output |
|---|---|---|
| 2026-10-02T02:12:02Z | `gh api repos/andaro74/agentkeel/environments/platform-app` | `platform_app_environment.json` |
| 2026-10-02T02:12:02Z | `gh api repos/andaro74/agentkeel/environments/platform-app/deployment-branch-policies` | `platform_app_branch_policies.json` |
| 2026-10-02T03:16:11Z | `gh api repos/andaro74/agentkeel/environments/platform-app/secrets` | one secret, `PLATFORM_APP_PRIVATE_KEY`, created and last updated 2026-10-01T03:33:55Z |
| 2026-10-02T03:16:11Z | `gh api repos/andaro74/agentkeel/actions/secrets` | two secrets, `AGENTKEEL_GRAFANA_TOKEN` and `RULESET_TOKEN`; no `PLATFORM_APP_PRIVATE_KEY` |
| 2026-10-02T03:16:11Z | `gh api repos/andaro74/agentkeel/environments` | one environment, `platform-app` |

What they show: one deployment branch policy, `main`, type branch
(`custom_branch_policies: true`); one protection rule, of type
`branch_policy`; no reviewers, no wait timer; `can_admins_bypass: true`;
the App's key stored as a secret of the environment and not of the
repository. GitHub returns secrets' names, never their values.

What they do not show: whether an admin's bypass reaches a deployment
branch policy (R1); organisation-level secrets (`andaro74/agentkeel` is
under a personal account, which has none); who can add a branch policy,
run, and remove it (any admin of the repository: one person, R1); the
environment's deployment history; the App's installation, which a user's
token cannot list (HTTP 403) and the App's own key must read.
