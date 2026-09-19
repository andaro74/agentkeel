# infra/ruleset

Security seat (`infra/**`). M01 open items 30 and 31.

`main.json` is the repository ruleset on `main`, exported as GitHub
returned it:

```
gh api repos/andaro74/agentkeel/rulesets            # the id: 23685206, name main
gh api repos/andaro74/agentkeel/rulesets/23685206 > infra/ruleset/main.json
```

Exported 2026-09-19, at M01 PR 1, after the human set
`allowed_merge_methods` to `["merge"]` (item 30); the export's
`updated_at` is `2026-09-19T13:34:54.934-07:00`. (Git Bash turns a
leading `/` into a Windows path, so the endpoint is written without one.) It is the evidence for
two things, at that date and no later:

- **Merges are merge commits.** `allowed_merge_methods` is `["merge"]`:
  squash and rebase are refused by GitHub, not by convention. ADR-0004
  amendment 1's rule is now mechanical; its text is unchanged.
- **`bypass_actors` is `[]`.** Nobody, including the owner, is listed as
  able to bypass the ruleset (P9). The F0.3 observer could not read this
  (M00 open items 7 and 15); this file says what it was on this date, and
  `checks.F0_3`'s URL says what was observed on the run it names.

What this file does not do:

- `validate` does not read this file at M01; the live-vs-export diff and
  bypass_actors: [] land at M02 PR 1. Until then a ruleset changed in the
  GitHub UI differs from this file and nothing notices.
- The `workflow-hash` check in `validate` (item 29) does not stop a PR
  that edits a workflow from editing `infra/workflows.sha256` in the same
  diff. It catches an edit that forgets the hash file, not one that
  updates both. `ruling-cited` on `infra/**` closes that at M02.
- `workflow-hash` hashes the workflow files' text only. What a workflow
  does also lives in the `Makefile`, `src/` and `scripts/`, which it runs
  and which are not hashed; the same PR can also delete the check from
  `src/validate/checks.py`. It meets SPEC/00 §5's "workflow file hash
  unchanged", not §3's "edits a workflow". Carried to M02.
- `current_user_can_bypass` in the export describes the account that ran
  the command, not every account.
