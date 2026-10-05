---
# M08 PR 3, Product's key over the Product paths this PR touches: the three
# run files' `expected:` statements (pushed before each run) and `observed:`
# blocks (filled after each run's by-hand making); the "During PR 3" section
# of milestones/M08/README.md; and this ruling file. DRAFT until the human
# rules; the live cell is read by PR 3's run's envelope, not by this file.
# Engineering's file (with the cold review) is rulings/pr3-engineering.md;
# Security's (the run 2 egress rule) is rulings/pr3-security.md.
ruling: pr3
seat: Product
authorises:
  - milestones/M08/runs/drill_run1.yaml
  - milestones/M08/runs/drill_run2.yaml
  - milestones/M08/runs/drill_run3.yaml
  - milestones/M08/README.md
  - milestones/M08/feasibility.md
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/08-game-day-drill.md
  - milestones/M08/rulings/pr1.md
  - milestones/M08/rulings/pr2.md
pr: 47
---

# Ruling: M08 PR 3, Product — DRAFT

To be ruled by andaro74 as Product once the three runs are made.

## What this covers

PR 3 is the repair the PR 2 cold review found (if any; its one FINDING was
folded inside PR 2, `64a550d`) plus **the runs**: run 1 again with its
evidence (F8.4) read for the first time, and runs 2 and 3 (SPEC/08 §5.1).

- **`milestones/M08/runs/drill_run1.yaml`.** An `expected:` block pushed
  before run 1 restates SPEC/08 §7's stated outcome (refused 4 of 6,
  recorded 5 of 6; a2 unread on both halves; a3 recorded not refused; row 8
  RED on a2 and a3). After the owner makes run 1 (`deploy.yml` invokes the
  hostile copy per golden, then the quarantine is attached, one more
  invocation, and detached), `observed:` carries the lookup keys the
  observer uses: for each attempt a `kind` (`trail`, `flow`, `answer` or
  `none`) and the key that kind needs (`request_id`, `eni`+`destination`,
  `object_key`); the window `{opened, closed}`; `quarantine`
  `{role, attached_at, detached_at}`; and the `evidence` block naming the
  records F8.4 reads (added at PR 3, since run 1 closes at the detach).
- **`milestones/M08/runs/drill_run2.yaml`.** An `expected:` block pushed
  before run 2 restates: with the egress rule to the KMS endpoint's group
  added to the hostile copy's SG alone, a1's connect completes (`ACCEPT`
  flow record) and IAM refuses `kms:ListKeys` in the trail, both in the
  bucket within N. `observed:` after the run carries the window,
  `eni`/`destination` and the `request_id`.
- **`milestones/M08/runs/drill_run3.yaml`.** An `expected:` block pushed
  before run 3 restates: with the six attempts removed and `kms` declared,
  the answer record reads GREEN, no refusal by the role and no `REJECT`
  flow in the window, the registry row read as any agent's. `observed:`
  after the run carries the window, `answer_key`, `role`, and the registry
  row's name (how the F8.3 third arm is read — see Unsure below).
- **`milestones/M08/README.md` "During PR 3"** — the dates each run was
  made, the lookup keys, and what each reading said. Written by Product
  after each run.
- No new control (ADR-0013); no `infra/` change; no stack, policy, bar,
  rule, golden or manifest id change.

## What it does not do

- **No close of row 8.** The Measured cell stays `—`; PR 4 closes it from
  PR 3's run's envelope's `drill` field (SPEC/08 §5.1).
- **No change to SPEC/00 or SPEC/08.** Each run's expected is already in
  the authority; the `expected:` block restates it under the "stated
  before, pushed before" rule (SPEC/08 §2) so a reading that differs reads
  as a finding, not a retake.
- **No `docs/`.** The explainer's "What happened" is PR 4's.

## The cold review

To be run on the diff at `228da43...HEAD` before this PR opens, by
`engineering-cold-reviewer` on PR 3's code and run files, and by
`security-reviewer` on run 2's egress ruling (`rulings/pr3-security.md`).
Reports pasted in `rulings/pr3-engineering.md` and the PR body.

## Unsure

- **Panel 1 for run 3's F8.3 third arm.** The Grafana observer token
  expires 2026-10-31 and panel 1 is the registry row's live reading. My
  recommendation: take SPEC/08 §9 cut 1 and read the registry DynamoDB
  table directly through `agentkeel-audit-read`; the F8.3 third arm is
  then named "read through the registry table, not panel 1", and panel 1
  stays named unread. Seat: Product (the cut), Security (the read).
  Recorded under the M08 decision rule; undone by a renewed token before
  PR 3 closes.
- **The two orphan KMS keys (`ce2d6f46…`, `fcd9e973…`).** `open.md` row 6
  says they are read as gone after 2026-10-09; today is 2026-10-04. Read
  by hand before PR 3 closes, recorded in the explainer's "In one
  sentence" neighbour at PR 4 if gone, or carried as a finding if not.
  Seat: Security. Recorded under the M08 decision rule.
- **The `evidence:` record set for run 1.** `drill.evidence` reads each
  record by `key` and `kind`; my recommendation: name the records F8.4
  rests on in `drill_run1.yaml.observed.evidence.records` (the trail
  objects for a4, a5, a6; the flow object for a1; the answer object for
  a3), plus any unnamed refusal the observer finds. Seat: Product (names
  the records), Engineering (the reader runs). Recorded under the M08
  decision rule.
- **The by-hand CLI invocation 404'd on both the quarantine run (run 1,
  00:52:06Z) and the egress-rule run (run 2, 03:27:36Z).** AWS CLI
  2.37.4's `aws bedrock-agentcore invoke-agent-runtime` returned
  UnknownOperationException 404 at the data-plane endpoint on this box,
  while the Python SDK (deploy.yml, 00:48:03Z) worked. Likely cause: the
  invocation shape the CLI used (missing `--qualifier`, or the ARN
  segment resolution) left the request on the wrong endpoint path.
  **Recommendation: stand as-is.** Row 8's state is unchanged (still
  RED), SPEC/08 §5.1 "each run is made once" refuses a retake, and run 3
  does not need by-hand invocation (deploy.yml uses the Python SDK). The
  reading surfaces two findings worth writing down (the deny-all is not
  the one that fired on F8.5, and the egress-rule layer F8.2 reads
  unread). Seat: Product (the reading), Engineering (the by-hand step).
  Recorded under the M08 decision rule; undone by a retake flow and a
  CLI incantation we have not confirmed.
