---
# M09 PR 2 (#50), the Rule Owner's key over the one Rule Owner path this PR
# adds, rules/baseline.yaml, and the three rulings SPEC/09 §11 puts to this
# seat before PR 2: R1 (the baseline's day-one content), R2 (the split is
# one key) and R10 (a template agent's pin may be its own; row 37 re-ruled).
# agents/refagent/rules/ and agents/refagent/manifest.yaml are not in the
# diff. The change to src/validate/agent.py's pin reading is Engineering's
# code under this seat's rule (R10) and is keyed in pr2-engineering.md.
ruling: pr2-rule-owner
seat: Rule Owner
authorises:
  - rules/baseline.yaml
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - docs/adr/ADR-0014-per-agent-rules-on-a-platform-baseline.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
  - milestones/M09/feasibility.md
  - milestones/M08/open.md
pr: 50
---

# Ruling: M09 PR 2, Rule Owner

Ruled by: pending

## R1. The baseline on day one (ADR-0014 decision 2)

`rules/baseline.yaml`, in refagent's format: `pii` PHONE ANONYMIZE and
EMAIL ANONYMIZE; `denied_topics` empty; `topics_apply_to: input`;
`content_filters.prompt_attack: off`, as ruled at M03 PR 2
(`agents/refagent/rules/guardrail.yaml:33-36`); the two blocked messages
as defaults an agent file may replace. No `plants`, no `blocks`. An agent
file that carries a `content_filters` key is refused by the merge, with
one reading stated below. The baseline's own firing is not read at M09
(SPEC/09 §8): `g-014` (MASKED) reads `never_passed` in every cell from row
3 to row 8, and the membership reader reads topic names; M09 reads the
baseline's presence in an agent's guardrail, by F9.1's digest and the
read-back, and the agent's own rule's firing. The template README says so.

**What the merge refuses** (`src/validate/agent_rules.py`, the rule-owner
report's list on PR 1, each naming the rule and the way): a baseline
topic's name in the agent's `denied_topics`, examples included, by case or
whitespace too; a baseline PII entity with any action but the baseline's,
lowered or raised (ANONYMIZE to NONE is seed S2); a `content_filters` key
that is not the baseline's own; `topics_apply_to` outside `input` and
`input and output` (the stricter wins); a key the format does not have; a
topic named twice or outside Bedrock's limits; more than thirty topics in
the sum, naming the file that took it over (R5, built); `plants` or
`blocks` in the baseline; a plant with no `blocks` entry, a `blocks` entry
naming a rule the merged guardrail does not build, a `blocks` key no plant
lists, a plant with no golden file or one of another kind or retired. And
not refused: a key absent (inherits), `pii: []` (adds nothing, removes
nothing), an identical entry (dedupes), the agent's own messages.

**One reading, stated so it can be undone.** R1 says an agent file
carrying a `content_filters` key is refused. refagent's own file carries
`content_filters: {prompt_attack: off}` from M03 PR 2, and refagent's files
are agent rules too (SPEC/09 §2). The merge reads a `content_filters`
identical to the baseline's as it reads an identical PII entry: it dedupes
and is not refused; one that differs is refused. So refagent's file is
unchanged, as the brief asked and as R2 reads it. If this seat reads R1
strictly, the key comes out of refagent's file under this seat's key, one
file, not a list entry removed (ADR-0009 entry 5 does not read it), and
the merge refuses any `content_filters` key: a one-line change in
`merge_errors`. Put under Unsure in the PR body.

## R2. The split is one key (ADR-0009 entries 4 and 5 do not fire)

The two PII entries stay in `agents/refagent/rules/guardrail.yaml` beside
the baseline's identical entries, and the merge dedupes them; the diff
touches no file under `agents/refagent/rules/` and not refagent's
manifest. refagent's guardrail keeps id `1088aw3ujhyd`: the bootstrap
stack now builds it from the three files (`infra/bootstrap/app.py`
`guardrail_spec`, the baseline merged under refagent's), the rules
unchanged, the version description's digest new, over the baseline first.
Entry 5 does not fire (nothing removed, no action weakened); entry 4 does
not fire (the id is unchanged). S4's guard and `plants_fired` 7 of 7 on
this PR's envelope are the witness (F9.5), joined into `checks.F9_5` by
build's own count and held again by the gate.

**The version bump is a by-hand step after this PR**: Security deploys
the bootstrap, the stack's `GuardrailVersionForTheManifest` output reads
6, and this seat moves `agents/refagent/manifest.yaml` `guardrail.version`
to it under one key (a version moved up, ADR-0009 entry 1's direction is
down). Until then the deployed runtime and the runner carry version 5,
whose rules are the same rules.

**One more rule, stated once**: an entry in refagent's file that differs
from the baseline's action, in either direction, is refused by the merge
as any agent's would be, so a future baseline change to BLOCK is a Rule
Owner change to both files.

## R10. A template agent's pin may be its own (ADR-0014 decision 4; SPEC/00 §8 M09 item 3; row 37 re-ruled)

`milestones/M08/open.md` row 37, "One guardrail for every agent", is
re-ruled: an agent from the template whose repository carries
`rules/guardrail.yaml` pins a guardrail of its own, on three conditions,
each read by a falsifier:

1. built by the platform from the baseline and the agent's files, with
   the digest the observer computes itself from the merge commit and
   `rules/baseline.yaml` on `main` in the version's description (F9.1;
   `infra/construct/governed_agent.py`, `scripts/observe_rules.py`);
2. not null and not refagent's (`src/validate/agent.guardrail_errors`,
   Engineering's code under this rule; the construct refuses the same);
3. the change of pin in the agent's manifest cites the agent's Rule Owner
   (the agent repository's own seats, read by the platform check).

**The placeholder's life** (R3 with this seat): a pin that resolves to
nothing is admitted while the registry row holds no guardrail for the
agent, and refused once it does (`deploy.yml`'s check with the held pin).
The answer record's pin is the stack's, never the placeholder: F9.1 reads
it, and the construct conditions the invoke on the stack's own resource.

**ADR-0009 entry 4 on the first pin change.** The first change in a
template agent's manifest, from refagent's id to the agent's own with the
baseline's digest in the new version's description, is **not** an entry-4
relaxation: nothing is removed from the call; the guardrail on it carries
every baseline rule and more. A later id change inside an agent repository
is unread at M09 (SPEC/09 §8): an agent repository's own pull requests
have no `two-key` (SPEC/00 §12).

**What a template agent's guardrail carries.** The baseline and the
agent's own rules only. refagent's six topics are refagent's
(`agents/refagent/rules/`), not the platform's, and are not carried. A
topic for the template's shipped clause text is the agent's Rule Owner's
to add (`rule-owner` finding 6 on PR 1): under baseline plus one topic the
fixture agent is no longer blocked on `contract-text-disclosure` for the
clause text it ships, which is not a relaxation of refagent's rules.

An agent without `rules/` is as at M06: it pins refagent's, and the check
and the construct hold it to that.

## What a reader can run

```
uv run pytest tests/test_m09_seeds.py -q -k "s2 or s4 or s5"      # the merge refuses S2 and S5, S4's guard holds
uv run python -m src.validate                                       # the platform baseline, and every agent's rules merging onto it add-only: ok
git diff 460990b...HEAD --stat -- agents/refagent                   # empty: the split touches nothing of refagent's
uv run pytest tests/test_m09_platform.py -q -k refagents_guardrail  # the same rules, the digest over the baseline first
```
