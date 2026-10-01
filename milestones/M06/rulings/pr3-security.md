---
# M06 PR 3 (#36), Security's key. Product's file is pr3.md.
ruling: pr3-security
seat: Security
authorises:
  - infra/ruleset/agent.json
  - infra/ruleset/agent.post.json
  - infra/ruleset/README.md
evidence:
  - SPEC/06-developer-template.md
  - milestones/M06/runs/owner_check_ruleset_24310403.json
pr: 36
---

# Ruling: M06 PR 3, Security

Ruled by andaro74 as Security, 2026-10-01, as written.

## What this authorises

- **`agent.json` in GitHub's form**, re-exported from ruleset 24310403 on
  `agentkeel-studio/owner-check`: PR 2's form plus
  `dismissal_restriction: {enabled: false, allowed_actors: []}` and
  `require_extra_approval_for_unattributed_changes: true`, which GitHub adds
  to an organisation repository's pull request rule. Everything else is
  PR 2's, byte for byte: `bypass_actors: []`, the check bound to
  `integration_id` 5144253, strict up-to-date, merge commits only. The
  compare stays exact on all six fields, so a weaker live ruleset is still
  refused (tested with the second field false).
- **`agent.post.json`**, the body the owner POSTs: the form GitHub accepted
  for 24310403. A POST of `agent.json` itself has not been tried; a test
  holds the body plus GitHub's two fields equal to the export.
- **The README** says both, and that the one read-back is one read of one
  repository.

## The seat report (security-reviewer, the diff `39031e7...b3be039`, verbatim in the PR body)

| # | Status |
|---|---|
| F1 (`require_extra_approval_for_unattributed_changes: true` may ask for an approval, e.g. on an update-branch commit, which a write-only developer cannot give) | Stands, read before S3: the owner test's step 3 now records whether an approval is asked; if one is, the quickstart says so before S3 is timed. Unsure in the PR body |
| F2 (no case with the field false) | Repaired (`b19db9a`) |
| F3 (a POST carrying both fields untried, and the next one is inside the timed run) | Repaired (`b19db9a`): the owner POSTs `agent.post.json`, the form that was accepted |
| N1 (one read, not a guarantee) | Repaired in the README |
| N2 (the fixture typed by hand) | Repaired (`b19db9a`): GitHub's response committed under `milestones/M06/runs/`, loaded by the test |
| N3 (`dismissal_restriction` lets a write holder dismiss a review) | No effect with 0 required approvals; matters only if F1 asks for one |
| N4 (schema drift refuses every head again) | Repaired (`b19db9a`): the refusal names the rule and field |
| N5 (an admin can relax the live ruleset after a success, caught only at the next head) | Unchanged, already a limit in `platform-check.yml` and SPEC/06 §8 |

## What a reader can run

```
uv run pytest tests/test_m06_readers.py -q -k "ruleset or post_body or export"
git diff 39031e7...HEAD -- infra/ruleset/
```
