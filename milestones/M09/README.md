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
| Falsifiers | F9.1 the agent's rules are not in the guardrail its run carries. F9.2 an agent removes or weakens a baseline rule and is merged. F9.3 a planted rule is silent (answered, or blocked with its named rule absent from the trace). F9.4 the platform check refuses an agent's own pin or its guardrail golden, or admits a plant with no named rule. F9.5 the split relaxes refagent (a rule leaves its guardrail, or its plants read under 7 of 7). |
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
   own (SPEC/00 §8 M09 item 3).

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

### What a reader can run

```
git show 02db54e --stat   # the seeds, the tests, SEEDS_M09, the README rows, the run file; no reader
uv run pytest tests/test_m09_seeds.py -q              # 2 passed, 7 xfailed
uv run pytest tests/test_m09_seeds.py -q --runxfail   # 2 passed, 7 failed, each with its planted message
make plants     # S1 to S5 and the run; agent_rules.py, baseline.yaml, observe_rules.py "not in the tree yet"
make validate   # twenty checks, ok
make ledger     # exits 0; row 9 OPEN, Measured empty, 1 / 4
git diff 0ba6d1d...HEAD -- src/validate src/verdict/build.py src/verdict/gate.py scripts infra rules thresholds.yaml evals agents   # empty but for SEEDS_M09 in plants.py
```

Any seed test that passes for a reason other than its reader, or any
reader that appears in this PR, makes the plant wrong.
