---
adr: ADR-0014
title: Per-agent guardrail rules on a platform baseline; a tenth milestone after the last
status: Proposed
date: 2026-10-11
seat: Product
authorises:
  - Product  # SPEC/00 §7 row 9, §8's count and its M09 entry, §10.3 row 09, §10.5, §15: a milestone after "the last"
  - Rule Owner  # `rules/baseline.yaml` is a Rule Owner file; an agent's `rules/` is read; a template agent's pin may be its own (M08 open.md row 37 re-ruled, SPEC/00 §8 M09 item 3)
  - Security  # which role builds a guardrail for an agent that is not refagent (SPEC/09 §11 R3), ruled at PR 2
amendments: 0
---

# ADR-0014 — Per-agent guardrail rules on a platform baseline

Proposed by the session at M09 PR 1 and put to Product
(`milestones/M09/rulings/pr1.md`). Accepted when that ruling reads
"Ruled by", on `main` at the merge commit of M09 PR 1 (ADR-0008).

## Context

Three things stand in the tree at `0ba6d1d` (tag `m08`):

- **An agent from the template is guarded by refagent's rules.** The
  platform check holds every template agent's `guardrail` pin equal to
  refagent's (`src/validate/agent.py:109-117`, the M06 rule "one
  guardrail for every agent"); the construct conditions the agent's model
  call on that pin. refagent's six denied topics are about title
  availability. An agent on another subject is checked against them and
  against nothing of its own. The template README says it plainly: "A
  `rules/` folder here is not read."
- **An agent repository may hold no guardrail or red-team golden**
  (`src/validate/agent_goldens.py:35`), so nothing can show a rule firing
  on a template agent's runtime.
- **SPEC/00 §8 called M08 the last milestone**, and M08 closed RED on
  2026-10-06 with "then building stops" (ADR-0013). The gap above was
  named at M06 (SPEC/06 §8, "One guardrail for every agent"), carried to
  M07, and left by M08's open as "a named gap to re-rule, not work"
  (`milestones/M08/open.md` row 37). Nothing was ever planted for it.

## Decision

1. **M09 is opened, after M08's close, by a Product ruling.** It is not a
   finding of M08 and reopens none of M08's rows; M08's close detail,
   its findings' homes and its tag stand. SPEC/00's count becomes ten
   milestones and at most 40 PRs. M09 takes row 37 and nothing else from
   M08's gaps. **This ADR does not amend ADR-0013:** M08 built no
   control, and that stays true of M08. M09 is a different milestone and
   builds one control, under its own claim, measured on its own seeded
   case before any document calls it working (SPEC/00 §10.5).
2. **A platform baseline exists as a Rule Owner file**, `rules/baseline.yaml`,
   in refagent's format, separate from refagent's topics. refagent's six
   topics stay in `agents/refagent/rules/` as refagent's own agent rules.
   What the baseline holds on day one is the Rule Owner's ruling at PR 2
   (SPEC/09 §11 R1; proposed: the two PII entities and the prompt-attack
   filter off, as ruled at M03).
3. **An agent repository's `rules/guardrail.yaml` is read**, and merged
   onto the baseline **add-only**. An agent can add rules; it cannot
   remove or weaken a baseline rule, and a file that tries is refused by
   the platform check with the rule and the way named. This is the
   control M09 builds.
4. **One guardrail per agent**, built by the platform from the merged
   rules; the agent's manifest pins its id and version, and the platform
   check accepts a pin that is not null and not refagent's for an agent
   that is not refagent. **This re-rules `milestones/M08/open.md` row
   37** (SPEC/00 §8 M09 item 3), under the Rule Owner. Which role builds
   it is Security's ruling at PR 2 (SPEC/09 §11 R3): the deploy role's
   deny on every guardrail action but Apply (`infra/bootstrap/app.py:134-136`)
   was Security's at M03 PR 2 and is not narrowed by this ADR.
5. **A plant in an agent repository is read from the trace**, by the
   membership rule `build` has applied to refagent's plants since M03
   PR 3: fired only when its named rule is among the topics the trace
   records. Its result is recorded in the envelope's `agent_rules` field
   after the merge and read by row 9's cell; **it stops no merge at M09**
   (SPEC/00 §8 M09 item 5).
6. **The guardrail stays on the model call.** No gateway, no policy
   engine, no Cedar, no per-tool limit, no log-only mode: SPEC/00 §12's
   list is unchanged, and SPEC/09 §12 repeats it. The public caller is
   proposed as M10, with a claim of its own, not folded into M09.

## How this stands beside ADR-0013 and SPEC/00 §12

- **ADR-0013** said M08 builds no control and that a fault the drill
  found in M01–M07 is named, not repaired, because no milestone was left.
  Both stay true of M08. M09 is not the repair milestone ADR-0013 said
  did not exist: it repairs nothing M08 found (M08's five findings keep
  their standing homes in row 8's close detail) and builds one control
  for one claim of its own. A pull request of M09 that repairs an M08
  finding under this ADR contradicts it; the ruling to cite for that
  does not exist.
- **SPEC/00 §12** names what is not built in this project. The per-agent
  guardrail is not on that list; it was a named gap in SPEC/06 §8 and
  M08's `open.md`, which is where a control waits for a milestone. This
  ADR moves it from a gap to a claim. Everything on §12's list stays
  there; M09's cut list and §12 repeat the items a reader might expect
  M09 to build (the gateway, the policy engine) so that no document
  describes them as working.
- **ADR-0009 entry 5** reads an entry removed from a list under
  `agents/*/rules/` as a relaxation, two keys. Separating the baseline
  from refagent's file may trip it (SPEC/09 §11 R2); this ADR does not
  change the list. If the Rule Owner moves the PII entries out of
  refagent's file, PR 2 carries two keys.

## Consequences

- Row 9 is measured: the fixture agent's planted rules fired, n of m,
  read from its answer record after the merge, with F9.1 to F9.5 held.
  Expected 1 of 1 (SPEC/09 §7), with the risks §7 names.
- The template README's sentence "A `rules/` folder here is not read" is
  the false state and is corrected at PR 2, after the reader exists,
  never before.
- `rules/baseline.yaml` is a Rule Owner path from the day it exists;
  `.github/CODEOWNERS` already lists `/rules/` under that seat (M02), so
  no CODEOWNERS edit is needed for it.
- Every new agent's guardrail is one more Bedrock Guardrail in the agent
  account, with retained versions on each rules change, as refagent's
  (SPEC/09 §8). Removing old versions stays by hand.
- SPEC/00 §15's three clauses M08's close read as not met are re-read at
  M09's close over ten rows and moved to fit nothing (SPEC/00 §15 as
  amended at this PR).
