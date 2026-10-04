---
# M08 PR 2, Security's key over the Security paths this PR touches: the one
# new step in evals.yml and the evals.yml hash in infra/workflows.sha256.
# It makes no grant and widens no permission. The observer reads the audit
# bucket as agentkeel-audit-read, which already holds the prefixes it needs
# (SPEC/08 §11 R2); no role, policy or security group is changed by this PR.
# Product's file is rulings/pr2.md; Engineering's (with the cold review) is
# rulings/pr2-engineering.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/workflows/evals.yml
  - infra/workflows.sha256
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md
  - milestones/M08/README.md
  - milestones/M08/feasibility.md
pr: 46
---

# Ruling: M08 PR 2, Security

Ruled by andaro74 as Security, 2026-10-04, as written.

## What this covers

- **One new step in `evals.yml`** ("Look up M08's game-day drill in the
  security account's audit bucket"), in the `agentkeel-audit-read` credentials
  block, beside M05's, M06's and M07's reads. It runs
  `scripts/observe_drill.py` over the three M08 run files and hands
  `make evals` `DRILL_OBS`. No `if:` on a PR-controlled value; the step runs
  on the base workflow only, as the others do.
- **The `evals.yml` sha256 in `infra/workflows.sha256`**, recomputed after the
  step was added, with a header line naming the M08 edit.

## What it does not do

- **No grant, no widening.** `observe_drill.py` reads the audit bucket as
  `agentkeel-audit-read`, which already holds `s3:ListObjectVersions` and
  `s3:GetObjectRetention` on `AWSLogs/`, `agents/`, `envelopes/agents/`,
  `test/` and `observations/` (`READ_PREFIXES`), and `bundles/` is list-only
  (SPEC/08 §6, §8; §11 R2). A prefix this role cannot read is written unread,
  not granted. No `infra/` stack, role, policy or security group changes in
  this PR.
- **Run 2's egress rule is not in this PR.** It is added and removed by hand
  on the hostile copy's own security group after PR 2 merges, under a separate
  Security ruling that reads "Ruled by" (SPEC/08 §5.1, §11 R1). A construct
  change — which would open refagent's group too — is not made (SPEC/08 §6).

## The cold review (security-reviewer): 0 BLOCK, 1 FINDING, 11 NOTE

The report is pasted in the PR body. Its one FINDING asked whether
`agentkeel-audit-read` holds the two S3 actions `observe_drill.py` adds —
`s3:GetObjectRetention` and `s3:ListBucketVersions` (for F8.4's evidence
reading) — since the grant is in `infra/security/`, which this PR does not
touch. **Confirmed held**: `infra/security/app.py:352` grants
`s3:ListBucketVersions` and `:357` grants `s3:GetObjectRetention`, both over
`READ_PREFIXES` (`AWSLogs/`, `agents/`, `test/`, `envelopes/agents/`,
`observations/`); `bundles/` is list-only (SPEC/08 §8). No grant is widened,
and the reader fails safe if a prefix is ever missing (retention `"unread"`,
versions `found: false`, which row 8 reads as unread). The eleven NOTEs record
that permissions, pinning, placement, egress and the write-once evidence are
unchanged; the workflow hash is settled by `make validate` in CI.

## For the by-hand steps

The quarantine attach/detach, run 2's egress rule, and the drill-agent repo
are the owner's by-hand work (SPEC/08 §5.1; `milestones/M08/README.md`). This
ruling authorises only the reader's observer step, not those.

## Unsure

- `observe_drill.py` reads panel 1 (run 3's registry arm, F8.3) from
  `AGENTKEEL_PANEL_FILE`, which `evals.yml` writes in the eval-role block
  *after* the audit-read block where the observer runs. For PR 2 no run 3
  exists, so this does not bite; at PR 3, if panel 1 reads empty for ordering,
  F8.3's third arm is named unread and SPEC/08 §9 cut 1 reads the registry
  table directly. Seat: Security (the workflow), Engineering (the observer).
  Recorded under the M08 decision rule; undone by a step reordering, which is
  a PR 3 repair if run 3 needs it.
