---
# M08 PR 1 (#45), Security's key over the Security paths this PR touches:
# the CODEOWNERS line for incident-responder, the specialist's own prompt
# file (seat: security), and R5's second key (seven years not set, two
# keys with Product's pr1.md).
ruling: pr1-security
seat: Security
authorises:
  - .github/CODEOWNERS
  - .claude/agents/incident-responder.md
evidence:
  - SPEC/00-overview.md#8-M08
  - SPEC/00-overview.md
  - milestones/M08/rulings/pr1.md
  - docs/adr/ADR-0013-m08-builds-no-control.md
pr: 45
---

# Ruling: M08 PR 1, Security

Ruled by andaro74 as Security, 2026-10-04, as written.

## What this covers

Three Security paths in PR 1, and R5's second key. PR 1 builds no stack,
no workflow, no key policy and makes no grant; the one AWS change M08
makes, run 2's egress rule, is PR 3's and waits for its own Security
ruling (SPEC/08 §11 R1).

1. **`.claude/agents/incident-responder.md`** (`seat: security`). The
   specialist M08 adds (R8), called by Security. It drafts
   `docs/developer/incident.md`, which Product commits (`docs/**` is
   Product's), as `docs-writer` drafts the explainers; it states a run
   before it is made; and it checks the security account's records
   against the envelope (F8.4). It never rules, never attaches a
   quarantine, and never touches AWS. SPEC/00 §5.1's "owns
   `docs/developer/incident.md`" is read as "drafts": the seat commits.
2. **`.github/CODEOWNERS`**: one line added,
   `/.claude/agents/incident-responder.md @andaro74`, under the Security
   header, so `validate`'s "CODEOWNERS complete, single-owner" check
   passes (a file no line matches fails it). No other line changes.
3. **R5, second key** (with Product's `pr1.md`, ruling 4). **Seven years
   of retention is not set in this project.** The audit bucket's lock
   stays COMPLIANCE with one day (`infra/security/app.py`, `LOCK_DAYS =
   1`, unchanged). A longer lock on a shared bucket cannot be undone by
   anyone short of closing the account, and nothing M08 measures needs
   it: F8.4 reads the lock each record carries, as it is, and the
   explainer says the one-day lock lapses before the close. This closes
   SPEC/00 §8 M08's "seven-year retention" and R5's carried seven years
   (SPEC/05 §9 cut e): it is not built.

## Read before PR 2 (SPEC/08 §11), Security's items

- **R1.** Run 2's egress rule: its exact form, that it is added to the
  hostile copy's security group alone, and that it is removed when run 2
  closes. A widening of a live boundary; it waits for a PR 3 ruling that
  reads "Ruled by", and its diff is kept with `2>&1`.
- **R2.** `agentkeel-audit-read` already holds what `observe_drill.py`
  needs, including `AWSLogs/`, where a1, a4, a5 and a6 are recorded, and
  `bundles/` list-only (SPEC/08 §6, §8). No grant is widened at M08.
- **R3.** Whether the drill's records need a prefix of their own
  (proposed: ride `agents/drill-agent/` as any agent's).

## Unsure

- Whether the quarantine lookup in `infra/audit/README.md` should be
  reconciled to name the drill-agent stack before run 1
  (incident-responder F1); as it stands the runbook substitutes the
  stack name. Security, before run 1.
