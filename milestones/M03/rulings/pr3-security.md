---
# M03 PR 3 (#21), Security's key. Drafted by the session from the
# security-reviewer reports on this PR; for the human to rule as Security.
# Product's file is pr3.md.
ruling: pr3-security
seat: Security
authorises:
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - infra/ingest/README.md
evidence:
  - SPEC/00-overview.md#8-M03
  - milestones/M03/rulings/pr2-security.md
  - milestones/M03/rulings/pr3.md
  - milestones/M03/runs/pr3_stop_a_cdk_diff.md
  - milestones/M03/runs/pr3_stop_a_read_back.md
  - milestones/M03/runs/pr3_stop_b_ingest.md
  - milestones/M03/runs/guardrail_probes.md
pr: 21
---

# Ruling: M03 PR 3, Security

DRAFT. For the human to rule as Security. `security-reviewer` read this PR
three times, each report in the PR body: before stop A, from the tree at
`9ff9f95` (0 BLOCK, 4 FINDING, 16 NOTE); before stop B, from the tree at
`47ee02d` (0 BLOCK, 2 FINDING, 16 NOTE); for the cold review, the diff
`a423292...62e7980` (0 BLOCK, 2 FINDING, 12 NOTE). No workflow, CODEOWNERS,
key policy, cosign identity or IAM policy document changes.

## The code

`infra/bootstrap/app.py` (`d02be78`): the synth refuses a `blocks` rule in
either control that `guardrail.yaml` does not build; the `ParamGuardrail`
description no longer says GovernedAgent reads it (N9 on PR 2, folded into
this bootstrap change as ruled). The template is 47,601 bytes minified at
the head, against CloudFormation's 51,200-byte inline limit (the session's
reading, `json.dumps` compact of the synth).

## What the human did (2026-09-26)

1. **Stop A**, the bootstrap redeploy, from a checkout of `0a90d52` with no
   tracked change. `cdk diff --strict`: the guardrail version replaced and
   the parameter's description; the guardrail itself and every IAM policy
   document unchanged; ten metadata-only changes, the suppression reasons'
   `§` against `?`, PR 2's "10 changes omitted". Read-back before and after:
   81 cases, byte-identical, 0 mismatches. Version 5 READY; version 4
   retained.
2. **Stop B**, the ingest redeploy (`pr3.md` ruling C), from a checkout of
   `70e7d53` with no tracked change. `cdk diff --strict`, a change set: one
   change, the promoter's `GUARDRAIL_VERSION` 4 to 5, in place, as the
   session's comparison of the templates at `0ee873e` and the branch
   predicted. After: the promoter configured with `1088aw3ujhyd`, `5`,
   `e12988c5…`; version 4 READY. Configured, not yet scanning: the
   promoter has not run since.

## Findings, and where each is held

| # | Finding | Status |
|---|---|---|
| before A, F1 | `cdk diff` must show nothing but the version, the parameter and the output | **held**: the diff, pasted whole |
| before A, F2 | the manifest moves only after `get-guardrail` of the new version is read | **held**: `47ee02d` after `9736c66` |
| before A, F3 | the read-back simulates `ApplyGuardrail` on the unversioned ARN only | recorded: the eval role's first use of version 5 is this PR's CI run (to cite) |
| before A, F4 / N8 | the eval role's invoke is not conditioned on the guardrail; the plants (F3_2) catch a dropped `guardrailConfig`, IAM does not | recorded; **proposed M05** (IAM ceilings, R5) |
| before B, F1 | the ingest inputs since `0ee873e` not all diffed | **read**: only the manifest (and a README) changed; `fingerprint_of`, `pyproject.toml`, `uv.lock` unchanged; templates compared |
| before B, F2 | a stop B read-back owed | **done** `0966593` |
| cold, F1 | stop B cited `pr3.md`, not in the tree | **held**: `pr3.md` ruling C, in this PR |
| cold, F2 | no non-admin principal has read version 5 | open: this PR's run (the eval role), and the merge deploy's load check (the runtime's condition at `:5`), named as pending, not claimed |
| before B, NOTE | "the earlier deploy stored `?`" was an inference | **repaired** `70e7d53`; whether the deployed template reads `§` now: the next bootstrap diff |
| before B, NOTE | "version 4 retained" rested on RETAIN | **read** at stop B: READY |
| cold, N4 (Eng.) | "clean checkout" with untracked files present | **repaired** `e88259c` |
| N9 (PR 2) | the parameter's description | **settled** `d02be78`, deployed at stop A |
| F3 (PR 2) | the 10 omitted changes | **settled** as metadata only |
| N10 | `<arn>:*` lets the eval role, the agent role and the promoter apply DRAFT and versions 1 to 5; only the runtime's invoke is pinned (to 5 after the merge) | recorded, wider in fact; **proposed M05** |
| N16 | the template at 47,601 of 51,200 bytes | recorded; **proposed M04 PR 1**, before any addition to this stack |
| NOTE | the promoter's record keeps no guardrail version; S5's scan is version 4's by `admitted_at` | recorded; **proposed M04 PR 1**, when refagent first reads the corpus |
| NOTE | nothing mechanical compares deployed pins with the manifest (the promoter, the guardrail version) | recorded; M05 |
| N6, N7, N11, N13, N14, F4 (PR 2) | as `pr2-security.md` | unchanged |

Nothing here may say the version 5 grants or the named-rule scoring work
in AWS until this PR's envelope, and the merge deploy's load check, show
them.
