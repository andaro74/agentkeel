# M09 — Per-agent rules on a platform baseline

A tenth milestone, opened after M08's close by a Product ruling
(ADR-0014). It takes one named gap, `milestones/M08/open.md` row 37, and
reopens none of M08's rows.

## Ledger row

Written at M09 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 9 |
|---|---|
| Claim | An agent made from the template is guarded by its own rules on top of a platform baseline, and each of its rules is shown to fire on a question planted for it |
| Falsifiers | F9.1 an agent repository's rules are not in the guardrail its run carries: the pin its answer record names is refagent's, or a version whose description does not carry the digest of the baseline and the agent's files as the observer computes it. F9.2 an agent removes or weakens a baseline rule and is merged, or the merged guardrail lacks a baseline rule. F9.3 a planted rule is silent: a plant in an agent repository is answered, or blocked with its named rule absent from the trace. F9.4 the platform check refuses an agent's own pin or its guardrail golden, or admits a plant with no named rule or one naming a rule the merge does not build. F9.5 the split relaxes refagent: a topic or PII entity leaves refagent's guardrail, or its plants read under 7 of 7. |
| Seeded commit | `02db54e`: S1 the fixture agent `festival-desk` (the template's folder with `rules/guardrail.yaml`, one topic, `g-030` planted with its `blocks` entry, a pin of its own); S2 the weakened baseline; S3 the silent plant; S5 the unnamed plant; the run file `observed: null`; S4 a guard with no fixture. One commit, before any reader |
| Expected gate output | PR 1: refagent's envelope as at M08; it says nothing about claim 9. `tests/test_m09_seeds.py` 2 passed, 7 xfailed. From PR 2's merge the gate requires `F9_1` to `F9_5`, test-only witnesses. The live reading is recorded in `agent_rules` and read by this row's cell, not gated (SPEC/09 §4); on PR 2's own envelope it reads unread, so the row reads RED there. Named P3 exception: the fixture agent's repository is made after PR 2 merges and read by PR 3's run (PR 4's if the deploy path needs a repair). **Stated at open: fired 1 of 1, F9.1 to F9.5 held, row 9 expected GREEN**, with SPEC/09 §7's risks named. |
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

### Open detail (PR 1, 2026-10-11)

- **Opened through `/open-milestone`.** M08 is closed (RED, tag `m08` on
  `0ba6d1d`, 2026-10-06). SPEC/00 had no M09 and called M08 the last
  milestone; it was amended first (`d848ea9`: §3, §7 row 9, §8's count
  and its M09 entry, §10.3 row 09, §10.5, §15), SPEC/09 written in the
  same commit, and `product-spec-reviewer` run on it before anything
  else of PR 1 (0 BLOCK, 8 FINDING, 7 NOTE; pasted verbatim in
  `feasibility.md` §1). Every finding was taken on the session's
  recommendation and recorded in `feasibility.md` §2 with its seat;
  SPEC/09 was revised once on them and SPEC/00 three lines more
  (`2320218`). ADR-0014 is proposed in the same commit. The seeds are
  `02db54e`. Every ruling file of this PR is a **draft** until Product
  and Engineering rule.
- **M09 builds one control** (ADR-0014): the add-only merge of an
  agent's rules onto a platform baseline and the guardrail built from
  it. It is not described as working until it has fired on the seeded
  case. The reading of it (the plant from the trace, `agent_rules` on
  the envelope, row 9's cell) is the instrument; the gate rules nothing
  on `agent_rules`, so a silent plant in an agent repository stops no
  merge at M09.
- **What is live today, in the tree at `0ba6d1d`:** the template README
  says a `rules/` folder is not read, and nothing reads one; every
  template agent must pin refagent's guardrail
  (`src/validate/agent.py:109-117`); an agent repository may hold no
  guardrail or red-team golden (`agent_goldens.py:35`); `rules/` at the
  root does not exist; nothing reads whether a template agent's rule
  fired. The fixture agent is refused by the platform check on its pin
  and on `g-030`'s kind, which is the plant.
- **Expected GREEN, with the risks named.** Fired 1 of 1 is stated at
  open (SPEC/09 §7). The rule's wording has never been probed; the
  baseline's content and who builds the guardrail are not yet ruled; the
  split may be two keys. A baseline rule's own firing on a template
  agent is not read at M09 (SPEC/09 §8, reviewer finding 1).
- **M08 left no `open.md` for M09.** Its close gave every finding and
  Unsure item a standing home (`milestones/M08/README.md`, close
  detail); M09 takes row 37 of M08's own inbox and nothing else. M08's
  video was committed at its own close (ADR-0005 amendment 2), so this
  PR carries no recording (SPEC/00 §10.5 as amended).
- **The fixture is fictional.** `festival-desk`, a festival that does not
  exist, the slate's titles, one rule. No pharmaceutical content and no
  real product name (the brief for this PR; SPEC/00 §9).

### Read before PR 2, each with the pull request whose merge it must precede

SPEC/09 §11, and the **Unsure** list in PR 1's body. A step is attempted
only when the readings it needs have been ruled; a by-hand deploy waits
for a ruling file that reads "Ruled by".

**Before PR 2 opens** (rulings, not grants):
1. R1 (Rule Owner): the baseline's day-one content; the prompt-attack
   filter.
2. R2 (Rule Owner, Threshold Owner): whether the split is two keys
   (ADR-0009 entries 4 and 5); proposed, the PII entries stay in
   refagent's file beside the baseline's and PR 2 is one key.
3. R3 (Security): which role builds a guardrail for a new agent;
   proposed, the construct in the agent's own stack with the deploy
   role's deny narrowed to a tagged guardrail; the alternative is a
   bootstrap deploy by hand per agent.
4. R4 (Security): whether the observer may read a built guardrail back;
   if not, SPEC/09 §9 cut 3.
5. R5 (Engineering): the 30-topic limit on the merged spec.
6. R6 (Product): the public caller is M10, its own claim.
7. R7 (Data Owner): the blocked observation's shape, as `build` writes it
   today (pharmadelta M00 Unsure 10).
8. R10 (Rule Owner): row 37 re-ruled, a template agent's pin may be its
   own (SPEC/00 §8 M09 item 3), with the placeholder's life, the three
   conditions, ADR-0009 entry 4 on the first pin change, and that a
   template agent carries the baseline and its own rules only, each said
   in words (`rule-owner` findings 1, 2, 6).
8a. R11 (Data Owner): a MASKED plant counted, or the baseline's firing
    unread through M09 (`rule-owner` finding 7).

**Before PR 3's run** (after PR 2 merges; the owner, each stated in
`runs/f9_3_plant_run.yaml` first):
9. R8 (Product): `agentkeel-studio/festival-desk`, public. Make it from
   the template; open the first pull request carrying S1's folder with
   its placeholder pin; the platform check must admit it; merge; let
   `deploy.yml` build the guardrail and deploy it and ask the three
   goldens.
10. R9 (Data Owner): the three goldens as planted; `g-030`'s wording is
    not changed to make the rule fire. If the rule does not block on the
    first probe, the Rule Owner rewords the rule in the agent repository
    before the run is counted.
11. The second pull request: the pin from the registry row and S2's
    `weakened.yaml`; the platform check must refuse it on the rules
    file. The third: the pin alone; merges.
12. If the platform's own deploy path needs a repair, PR 3 is that repair
    and the run is read by PR 4's run (M08's second exception).

### Measure detail (PR 2, 2026-10-11)

- **PR 2 of 4, the measure.** Every reader SPEC/09 §6 names landed, each
  in the commit that took its seed's marker off: `rules/baseline.yaml` and
  `src/validate/agent_rules.py` with the platform check's three changed
  readings (`e2c04ab`; S1, S2, S5 read); `src/verdict/agent_rules.py`,
  `agent_rules` on the envelope, `CLAIM_9_CHECKS` wired and row 9's
  reading (`9d2f3a7`; S3 read), named as `M09_READERS` in the commit after
  it (`2608711`); the guardrail builder, the narrowed grants, the registry
  row, the observer and the two workflow steps (`353a8c4`). The run file's
  marker stays on: `observed` is null until the owner makes the run.
- **The plant goes RED here.** On PR 2's own envelope `agent_rules` reads
  not made: no agent repository with rules exists, so row 9's reading of it
  is RED ("the plant run has not been made", four falsifiers unread,
  planted rules none named) whatever refagent's own verdict. `F9_1` to
  `F9_5` are test-only witnesses on every envelope from the merge; `F9_5`
  is joined by build's own count of refagent's plants, 7 of 7 across the
  split, and the gate holds it again.
- **The rulings decided before PR 2 opened** (2026-10-11, each as proposed
  in PR 1's Unsure table): R1, R2, R3, R4, R6, R10, written as the four
  ruling files of this PR, each a draft until it reads "Ruled by". R5 is
  built (the merge refuses at 31 naming the file). R7 and R11 are put to
  the Data Owner in the PR body. The split is one key (R2): refagent's
  file is unchanged, its identical entries dedupe, its guardrail keeps its
  id and gains a version with the new digest at the next bootstrap deploy.
- **What this PR does not do.** No agent repository is made; no golden
  under `evals/goldens/`, no bar, nothing under `src/baseline/`; no
  gateway, no policy engine, no public caller (R6: M10). refagent's
  manifest still pins version 5: the version bump follows the bootstrap
  deploy, by hand, under the Rule Owner's key.

### By-hand steps before PR 3's run, each with what it must precede

1. **Security deploys the bootstrap stack** (`infra/bootstrap/`, by hand,
   as at every stop): the deploy boundary's narrowed deny, the execution
   role's guardrail grants (R3), the eval role's read-back (R4), and
   refagent's guardrail version 6 with the digest over the baseline. Before
   the fixture repository's first merge: without it the first deploy of an
   agent with `rules/` is refused on `CreateGuardrail`, which is a PR 3
   repair, not a finding of the claim.
2. **The Rule Owner moves refagent's manifest to the new version** once
   the stack's `GuardrailVersionForTheManifest` output reads it (R2: one
   key; the id is unchanged). Before PR 3's run, so refagent's envelope at
   that run carries the baseline's digest. `plants_fired` must stay 7 of 7.
3. **The owner makes `agentkeel-studio/festival-desk`** (R8, public) and
   opens the three pull requests in the order the run file states (R9: the
   golden is never edited), filling `observed` with the numbers and the
   answer record's key; the observer reads the rest.
4. If R4's grant is not deployed when PR 3's run reads, F9.1 reads the
   registry row's digest and the envelope says so (`source: registry`).

### What a reader can run

```
git log 460990b..HEAD --format=%h   # PR 2's commits: e2c04ab, 9d2f3a7, 2608711, 353a8c4, then the documents and the rulings
uv run pytest tests/test_m09_seeds.py -q              # 8 passed, 1 xfailed (the run, not made)
uv run pytest tests/test_m09_seeds.py -q --runxfail   # 8 passed, 1 failed: seed run: the run has not been made
uv run pytest tests/test_m09_readers.py tests/test_m09_platform.py tests/test_p5_disagree.py -q   # the readers, the builder, P5
make plants     # S1 to S5 and the run, every reader "in the tree"
make validate   # twenty-one checks, ok
make ledger     # exits 0; row 9 OPEN, Measured empty; "as row M09 reads it" ends RED on agent_rules not read
git diff 460990b...HEAD --stat -- evals/goldens thresholds.yaml src/baseline agents/refagent/rules agents/refagent/manifest.yaml   # empty
AGENTKEEL_BUNDLE=tests/fixtures/m09/s1-festival-desk CDK_OUTDIR=/tmp/fd PYTHONPATH=. uv run python infra/construct/app.py && grep -c AWS::Bedrock::Guardrail /tmp/fd/AgentkeelAgent.template.json   # 2: the guardrail and its version
```

Any reader that reads an agent repository's rules before the merge from
the working tree, any envelope field written by a runner or the observer,
or a row 9 reading that is not RED on this PR's own envelope, makes the
measure wrong.
