---
adr: ADR-0011
title: One stated second run after a p95 miss on a diff that touches nothing the agent runs
status: Accepted
date: 2026-10-02
seat: Product
authorises:
  - Threshold Owner  # SPEC/04 §2: what follows `F4_4` failing on p95 alone; the bar itself does not move
amendments: 0
---

# ADR-0011 — One stated second run after a p95 miss

Raised by `engineering-cold-reviewer` on M07 PR 2 (F14: SPEC/04 §2
gained a rule and no ADR) and by Product in `milestones/M07/rulings/pr2.md`
(P2). The rule is the Threshold Owner's, ruled on 2026-10-02
(`milestones/M07/rulings/pr2-threshold-owner.md` item 2) and written
into SPEC/04 §2 at M07 PR 2. Ruled by Product at M07 PR 3
(`milestones/M07/rulings/pr3.md`), accepted on `main` at that PR's merge
commit (ADR-0008).

## Context

`F4_4` fails an envelope whose p95 is over 2.0 times the incumbent's
median in the same mode (`thresholds.yaml` `delta_max.p95_ratio_max`).
The gate rules that envelope RED, and `evals` is a required check, so
the pull request cannot merge.

M07 PR 1 ran twice. The first run (`9f2ce07`) was RED on `F4_4` alone:
p95 14,281 ms, 2.06 times the median. The second (`0f4b72a`), 30 minutes
later, was GREEN at 5,830 ms with the same counts. The diff changed
nothing refagent runs. A run asks about nineteen answers, so its p95 is
close to its slowest single call.

That second run was made on Product's ruling (`milestones/M07/rulings/pr1.md`,
Unsure Q), stated before in `milestones/M07/runs/pr1_second_run.yaml`.
There was no rule for it. A rule that exists only in a SPEC paragraph,
about when a RED envelope may be followed by another run, is a rule
change with no ADR (one ADR per rule change).

## Decision

1. **The bar does not move.** `delta_max.p95_ratio_max` stays 2.0, and
   the reading stays as SPEC/04 §2 gives it. Raising the bar is a
   relaxation with two keys (SPEC/02 §2), and is not this rule.
2. **One second run, and only here.** When `F4_4` alone fails, on p95,
   on a pull request whose diff touches nothing the agent runs
   (`agents/`, `src/agent/`, `infra/construct/`, the pin, the guardrail,
   `rules/`, `data/`), one second run may be made. It is stated before
   it is made, in a run file under the milestone's `runs/`, and that
   file is pushed first. There is no third run.
3. **Both envelopes stay** in `evals/history/`. The second rules the
   pull request. Neither is deleted or rewritten.
4. **A swap pull request never gets a second run.** Its p95 is the thing
   under test. One exception: the revert of a merged swap that is RED on
   `F4_4` alone, since a revert restores the incumbent of record
   (`pr2-threshold-owner.md` item 3).
5. **No gate reads this rule.** The run file and the two envelopes are
   its record. A second run made outside it is a finding for the
   Threshold Owner, and is written as one in the pull request that
   carries it.

## Consequences

- M07 PR 1's second run predates this ADR. It is the case the rule was
  written from, and it met every term of it: `F4_4` alone, a diff that
  touched nothing the agent runs, stated before, both envelopes kept.
- The rule's list of what the agent runs does not name
  `.github/workflows/` or `src/verdict/` (threshold-owner N5 on M07 PR
  2). A diff that changes how a run is made or scored is not "nothing
  the agent runs" in spirit and is not excluded by the letter. Left as
  ruled; the Threshold Owner's to tighten, by an amendment to this ADR.
- This is a control with no seeded case. Nothing mechanical stops a
  third run, or a second run on a diff the rule excludes. One person
  holds every seat (R1).
