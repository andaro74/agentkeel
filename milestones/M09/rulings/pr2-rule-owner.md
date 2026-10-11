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

Ruled by andaro74 as Rule Owner, 2026-10-11, as written.

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

**The `content_filters` reading, ruled.** R1 as proposed said an agent
file carrying a `content_filters` key is refused. refagent's own file
carries `content_filters: {prompt_attack: off}` from M03 PR 2, and
refagent's files are agent rules too (SPEC/09 §2). The merge reads a
`content_filters` identical to the baseline's as it reads an identical PII
entry: it dedupes and is not refused; one that differs is refused, so an
agent file still cannot turn a filter on or off. That is the ruling, not
an Unsure (`rule-owner` finding 1 on PR 2), and refagent's file is
unchanged, as R2 reads it; SPEC/09 §2 and the quickstart say "that differs
from the baseline's" from this PR. The strict alternative, dropping the
key from refagent's file, would read at the gate as `content_filters
removed` and `content_filters.prompt_attack removed`, two keys
(`src/gates/two_key.py` reads every mapping key, wider than ADR-0009 entry
5's words; `rule-owner` finding 2), one more reason for this reading.

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
down), in a pull request of its own that cites its own ruling file,
`milestones/M09/rulings/refagent-version-6.md` (seat Rule Owner,
`authorises: agents/refagent/manifest.yaml`, `pr:` that pull request;
`rule-owner` finding 4 on PR 2). Until then the deployed runtime and the
runner carry version 5, whose rules are the same rules; nothing reads
refagent's deployed version description against the tree (F9.1 reads
template agents only), so no page calls version 5 "the baseline's".

**One more rule, stated once**: an entry in refagent's file that differs
from the baseline's action, in either direction, is refused by the merge
as any agent's would be, so a future baseline change to BLOCK is a Rule
Owner change to both files.

## R10. A template agent's pin may be its own (ADR-0014 decision 4; SPEC/00 §8 M09 item 3; row 37 re-ruled)

`milestones/M08/open.md` row 37, "One guardrail for every agent", is
re-ruled: an agent from the template whose repository carries
`rules/guardrail.yaml` pins a guardrail of its own, on three conditions:

1. built by the platform from the baseline and the agent's files, with
   the digest the observer computes itself from the merge commit and
   `rules/baseline.yaml` on `main` in the version's description (F9.1;
   `infra/construct/governed_agent.py`, `scripts/observe_rules.py`);
2. not null and not refagent's (`src/validate/agent.guardrail_errors`,
   Engineering's code under this rule; the construct refuses the same);
3. the change of pin in the agent's manifest cites the agent's Rule Owner.
   **Unread at M09**: a convention the agent's seats hold, not a falsifier.
   The platform check reads that the seats are logins with admin on the
   repository, not that a pull request cites one; an agent repository has
   no `ruling-cited` and no `two-key` (SPEC/09 §12; `rule-owner` finding 3
   on PR 2). Conditions 1 and 2 are read by F9.1 and the check.

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

## The `rule-owner` read

On the diff `460990b...d3897ab` (40 files): **0 BLOCK, 5 FINDING, 4
NOTE**, no relaxation, the baseline R1's, the merge's refusals complete.
Dispositions, each in the commit after `d3897ab`: F1 the dedupe reading
**stated as the ruling** above, SPEC/09 §2 and the quickstart changed by
Product (`pr2.md`); F2 the strict alternative's cost at the gate
**corrected** above; F3 R10's condition 3 **stated as unread** at M09; F4
the version bump's own ruling file **named** above and in the README's
step 2; F5 the baseline's firing is R11, the Data Owner's, in the PR body;
N2 the README's step 2 says no page calls version 5 the baseline's; N3
recorded for ADR-0009's last amendment; N1 and N4 as read. The report,
verbatim:

> Read: the diff 460990b...d3897ab (40 files)
>
> No relaxation. Nothing under ADR-0009's list moves in this diff: `rules/baseline.yaml` is a new file (patch 1503-1559), so no entry is removed and no action weakened; `agents/refagent/rules/` and `agents/refagent/manifest.yaml` are not in the diff (ruling `milestones/M09/rulings/pr2-rule-owner.md:140`, "git diff 460990b...HEAD --stat -- agents/refagent # empty"); refagent's guardrail id `1088aw3ujhyd` and version 5 are unchanged (entry 4 and entry 1 do not fire); the bootstrap builds the same rules from three files (`tests/test_m09_platform.py` in the patch 3646-3651: same topic names, same `pii`, same `messages`, digest over the baseline first). One key (R2) is right. `two_key`'s `RULES` regex (`src/gates/two_key.py:73`) already covers `rules/baseline.yaml`, so a future drop or weakening there is two keys.
>
> **The baseline's content is R1's.** `rules/baseline.yaml` (patch 1540-1559): `topics_apply_to: input`, `denied_topics: []`, PHONE and EMAIL `ANONYMIZE`, `content_filters: {prompt_attack: off}`, two default messages, no `plants`, no `blocks`. `baseline_errors` (`src/validate/agent_rules.py`, patch 2388-2411) refuses a baseline that plants, blocks, lacks a key, or turns the filter on. Held.
>
> **The merge refuses every item on the PR #49 list and inherits/dedupes as SPEC/09 §2 says.** Checked in `merge_errors` and `merge` (patch 2363-2490): unknown key (2455-2457); `topics_apply_to` outside the two values (2458-2460), stricter wins in `_stricter` (2357-2360); baseline topic name by case or whitespace (2342-2344, 2469-2474); baseline PII entity with any other action, lowered or raised (2476-2482); over 30 in the sum naming the file (2485-2489); topic twice or outside Bedrock's limits (2414-2432); plants with no `blocks`, a `blocks` rule not built, a `blocks` id not planted, a golden missing, of another kind, or retired (2506-2547); a guardrail golden no control plants (2584-2589). Absent key inherits (2366-2370); `pii: []` adds nothing and removes nothing (2378-2381, seeded S2); identical entry dedupes; agent messages replace (2370). `merge` never drops a baseline topic or entity. The construct refuses the same file at synth (`infra/construct/governed_agent.py`, patch 835-839) and the bootstrap the same for refagent's (`infra/bootstrap/app.py`, patch 521-523).
>
> **Nothing lets a template agent carry refagent's six topics or lose a baseline rule.** The construct builds only from `rules/baseline.yaml` and the agent's file (patch 840-848); the check refuses a pin with refagent's id (`src/validate/agent.py`, patch 2077-2079) and the construct refuses it again at synth (patch 2756-2761, test at 3610-3617). An agent without `rules/` is held to refagent's pin as at M06 (patch 2069-2073).
>
> FINDING 1 — The `content_filters` reading contradicts SPEC/09 §2 and the quickstart. Code: `src/validate/agent_rules.py` patch 2465, `if "content_filters" in agent and agent["content_filters"] != baseline.get("content_filters")` (an identical key dedupes). SPEC: `SPEC/09-per-agent-rules.md:94-96`, "carries a `content_filters` key at all (the filters are the baseline's alone; `rule-owner` finding 4 on PR 1) ... is **refused**". Quickstart (patch 265-266): "carries a `content_filters` key or a key the format does not have is refused". The template README (patch 328, "turn a content filter on or off") and the baseline's own comment (patch 1523-1524, "a `content_filters` key that differs from this one") say what the code does. My reading as the seat's reviewer: the dedupe reading is acceptable; it is the same rule the merge applies to an identical PII entry, an agent file still cannot turn the filter on or off, and refagent's file stays untouched. Settled when the Rule Owner's ruling states the dedupe reading as the ruling (not an Unsure) and Product changes the SPEC/09 §2 sentence and the quickstart sentence in this PR to "a `content_filters` key that differs from the baseline's". Seats: Rule Owner (the reading), Product (the two lines).
>
> FINDING 2 — The ruling's description of the strict alternative is wrong at the gate. `pr2-rule-owner.md:62-64`: "the key comes out of refagent's file under this seat's key, one file, not a list entry removed (ADR-0009 entry 5 does not read it)". `two_key.py:162-169` (`_entries`) emits a path for every mapping key, and `rule_relaxations` (`two_key.py:194-196`) reports "`<path> removed`" for any path absent on the head; dropping `content_filters` from refagent's file would read as `content_filters removed` and `content_filters.prompt_attack removed`, two keys. The gate reads more than ADR-0009 entry 5's words. This is one more reason for the dedupe reading; the sentence must be corrected either way. Settled when the ruling says the strict reading costs two keys at the gate, or is dropped. Seat: Rule Owner.
>
> FINDING 3 — R10 condition 3 has no reader, and the ruling says each condition is read. `pr2-rule-owner.md:98-99`, "on three conditions, each read by a falsifier"; `:107-108`, "the change of pin in the agent's manifest cites the agent's Rule Owner (the agent repository's own seats, read by the platform check)". Nothing in the diff reads whether a manifest pin change cites a seat: `guardrail_errors` (patch 2047-2083) reads null, refagent's id and the held pin only; the seats check reads that logins administer the repository, not that a diff cites one; an agent repository has no `ruling-cited` and no `two-key` (SPEC/09 §12, `pr2-rule-owner.md:120-122`). Settled when the ruling either names the reader or states condition 3 as unread at M09 (a convention the agent's seats hold, not a falsifier). Seat: Rule Owner.
>
> FINDING 4 — The by-hand version bump has no ruling it can cite. `milestones/M09/README.md` (patch 959-962): "The Rule Owner moves refagent's manifest to the new version ... (R2: one key; the id is unchanged)"; `pr2-rule-owner.md:82-85` says the same. This ruling's `authorises:` is `rules/baseline.yaml` alone (`pr2-rule-owner.md:11-12`); `ruling-cited` needs a ruling on `main` whose `authorises:` matches `agents/refagent/manifest.yaml`. A version moved up is one key, but it still needs its one. Settled when the README step names the ruling file the bump's PR will cite (its own `milestones/M09/rulings/<slug>.md`, seat Rule Owner, `authorises: agents/refagent/manifest.yaml`, `pr:` that PR). Seats: Rule Owner (the ruling), Product (the README line).
>
> FINDING 5 — Plant: the baseline's own rule has no firing plant. `rules/baseline.yaml` patch 1513-1516, "at M09 the baseline's own firing is not read (SPEC/09 §8; g-014, MASKED, reads never_passed in every cell from row 3 to row 8)"; quickstart patch 286-287, "the platform's own two rules (phone and email hidden) have no planted question of their own". The merge itself is covered by seeds S2 and S5 (`tests/test_m09_seeds.py`, patch 4023-4047) and the split by S4's guard plus `plants_fired` 7 of 7 (g-013, g-015, g-016 to g-020; `tests/test_m09_seeds.py:187-199`). The PII rule's firing is R11, already put to the Data Owner in the PR body (README patch 940-941). Not a golden this seat writes. Seat: Data Owner (R11).
>
> NOTE 1 — Pinned. Every pin in the diff is an id and a version: refagent's `1088aw3ujhyd:5` unchanged; the fixture's placeholder `fest1va1desk:1` is admitted only while the registry row holds no guardrail (`src/validate/agent.py` patch 2080-2082, `deploy.yml` patch 39-45) and never reaches the call, the record or the template (`tests/test_m09_platform.py` patch 3582-3594, "fest1va1desk" not in the rendered stack). No DRAFT, no latest. R3/R10's placeholder life is as stated.
>
> NOTE 2 — Between the bootstrap deploy and the bump, refagent's runtime carries version 5 (two-file digest) while the tree's digest is over three files; the ruling says so (`pr2-rule-owner.md:86-87`). Nothing reads refagent's deployed version description against the tree (F9.1 reads template agents only), so that gap is unread, not a finding. Say so in the README step so no page calls refagent's version "the baseline's" before the bump.
>
> NOTE 3 — The gate is stricter than ADR-0009's list for the baseline: `two_key.py:203-204` reads `prompt_attack` on → off and `:214-215` reads `topics_apply_to` "input and output" → "input" as relaxations, neither of which is an entry 1-6. The baseline comment (patch 1533-1535) names only "a drop or a weakening". No change needed now; the Rule Owner's planned ADR-0009 amendment (`docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md:132-138`, one left) is where those two are named. Seats: Rule Owner, Product.
>
> NOTE 4 — Two keys: not required on this diff (no relaxation, no retired rule). The two ruling files that would carry them if FINDING 1's strict reading were taken: `pr2-rule-owner.md` and a second seat's file naming `agents/refagent/rules/guardrail.yaml` in `keys:`; neither exists for that path today, which is consistent with the dedupe reading.
>
> BLOCK: 0 · FINDING: 5 · NOTE: 4

## What a reader can run

```
uv run pytest tests/test_m09_seeds.py -q -k "s2 or s4 or s5"      # the merge refuses S2 and S5, S4's guard holds
uv run python -m src.validate                                       # the platform baseline, and every agent's rules merging onto it add-only: ok
git diff 460990b...HEAD --stat -- agents/refagent                   # empty: the split touches nothing of refagent's
uv run pytest tests/test_m09_platform.py -q -k refagents_guardrail  # the same rules, the digest over the baseline first
```
