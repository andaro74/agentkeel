---
adr: ADR-0013
title: M08 builds no control; it builds the adversary and the instrument
status: Accepted
date: 2026-10-04
seat: Product
authorises:
  - Product  # SPEC/00 §8 M08's first line; §9's hostile copy; the cut list M08 opens with
amendments: 0
---

# ADR-0013 — M08 builds no control

## Context

SPEC/00 §8 M08 opened with **"Zero new code paths"**, and with the
sentence that gave that rule somewhere to go: *"any needed code is a
defect in M01–M07 and gets its PR there."*

Neither half holds at M08.

- **There is no PR there.** M01 to M07 are closed and tagged. Each spent
  its cap of four, and M07 spent five and closed RED by the cap (row 7).
  A defect found at M08 in what M05 built has no M05 pull request to go
  to. The sentence was written when M08 was eight milestones away and
  every earlier cap was unspent.
- **"Zero new code paths" has never been true of a milestone's
  reading.** Every claim in this project is read by code written in that
  claim's own milestone: `src/bundle/verify.py` (M01), `src/gates/`
  (M02), `src/validate/overlap.py` (M03), the gate's bars (M04),
  `scripts/observe_containment.py` and `src/verdict/containment.py`
  (M05), `src/verdict/template.py` (M06), `scripts/observe_upgrade.py`
  and `src/verdict/upgrade.py` (M07). A milestone that writes no code
  writes no reading, and a claim nothing reads is not measured. Row 8
  would close with no envelope and no measured value, which the ledger
  records as RED and which would be a worse outcome than the rule was
  written to prevent.

What the rule was protecting is still right: **M08 must not build the
control it then tests.** A drill that ships the refusal it measures
measures its own code, on a tree nobody has run against, and the five
milestones of controls behind it go untested. That is the failure the
words were aimed at, and this ADR keeps it while dropping the words.

## Decision

1. **M08 builds no control.** Nothing M08 adds refuses, records or
   quarantines. Every control the drill tests was built and deployed at
   M01 to M07: the per-agent security group and the VPC's missing route,
   the agent role's and the boundary's explicit denies, the audit
   bucket's policy and its lock, the trail, the flow log, and the
   quarantine policy. M08 changes no file under `infra/`, no bar in
   `thresholds.yaml`, no rule, no golden, and no field of refagent's
   manifest.
2. **M08 builds two things: the adversary and the instrument.**
   - The **adversary** is the hostile copy, which lives in an agent
     repository of its own, made from the template, and not in this
     repository's code (SPEC/00 §9). Its fixture is
     `tests/fixtures/m08/s1-hostile-copy/`.
   - The **instrument** is the reading of the three runs:
     `scripts/observe_drill.py`, which writes raw observations,
     `src/verdict/drill.py`, which rules on them, the envelope's `drill`
     field, and row 8's reading of it in `src/ledger.py`. P5 holds: the
     observer writes no verdict, `build` composes, the gate reads the
     envelope, and the ledger reads the gate.
   - And `incident-responder` (R8), a prompt, which drafts
     `docs/developer/incident.md`.
3. **A fault the drill finds in what M01–M07 built is a finding of that
   milestone**, written in row 8's close detail and in that milestone's
   README as a dated note. Its repair rides M08 PR 3 **only when run 2
   or run 3 cannot be made without it**. Otherwise it is named and not
   repaired in this project, because there is no milestone left to
   repair it in and no cap to spend.
4. **The one exception, and it is not code.** Run 2 removes a control for
   the hostile copy alone — one egress rule on its own security group,
   added and removed by hand under a Security ruling. It is a change to
   one deployed security group, not to the construct, so refagent's
   group is untouched. A construct change would open every agent's.

## Consequences

- Row 8 is measured. The measured value is run 1's attempts refused,
  n of 6, and recorded, m of 6, read from AWS's own records by code
  M08 writes and nothing else reads.
- **Two attempts are expected to miss**, and they stay inside the count:
  the outbound request, which the missing route refuses and no record
  shows (M05's finding), and the made-up key in a tool result, which
  nothing refuses because the filter was never built (SPEC/00 §12).
  Naming them as gaps outside the count would make GREEN reachable. Row
  8 is expected to close RED on them.
- The platform check never reads an agent's code, so the hostile copy
  merges and deploys with nothing skipped. That is stated in SPEC/08 §1
  at open, not found at PR 2.
- Items SPEC/00 §8 M08 asked for that no longer have anything to refer
  to are named, not quietly dropped: there is no judge to inject into,
  no Gateway policy to revoke, no memory to freeze, no Braintrust mirror,
  no GuardDuty delivery and no containment panel (SPEC/00 §12). The
  sixth attempt is `s3:PutBucketPolicy` on the audit bucket, a deny no
  one has attempted; the injection aimed at the judge is **not measured
  in this project**.
- **This ADR cannot be used to justify building a control in M08.** A
  pull request of M08 that adds a refusal, a record or a quarantine
  contradicts decision 1, and the ruling to cite for it does not exist.
- R5 is amended separately at M08 PR 1, with two keys: seven years of
  retention is not set in this project, and the lock stays COMPLIANCE
  with one day.
