# SPEC/04 — Model swap

Status: DRAFT · Owner: Product seat · Milestone M04 · Opened at M04 PR 1
(`milestones/M04/rulings/pr1.md`) · Build list: SPEC/00 §8 M04, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M04`),
as cut in §9 · Reviewed by `product-spec-reviewer` before the rest of
PR 1 was written (1 BLOCK, 12 FINDING, 4 NOTE;
`milestones/M04/feasibility.md` §1) and revised once on the rulings in
§2 of that note.

## 1. The claim

**Claim 4.** A breaking model swap goes RED; an equivalent swap
promotes; A-vs-A is zero diff.

For a director: *when a team switches the agent to a different model,
the switch is tested on its own proposal before it can go in; if a test
that used to pass now fails, or answers get much slower, it can't go in*
(SPEC/00 §10.3, M04, as amended at M04 PR 1 on finding 12: the shadow run
of `model-watch` is M07's, and the equivalent candidate is not a newer
version).

Threat answered (SPEC/00 §3): model regression or deprecation. A new
model breaks a tool format or slows past the bar, or the pinned model is
retired under the agent.

**Three parts.**

- *A breaking swap goes RED.* A pull request that moves refagent's pin
  to a model that cannot use the tool as refagent's contract requires
  gets a RED envelope, for that reason (§7), and cannot merge.
- *An equivalent swap promotes.* A pull request that moves the pin to a
  model the Threshold Owner has named equivalent gets a GREEN envelope
  and every required check green. **"Promotes" means mergeable, not
  merged** (ruling 1, `rulings/pr1.md`): the equivalent candidate, Sonnet
  4.5, is older than the incumbent, Sonnet 4.6, and merging it would move
  production to the older model to prove a point.
- *A-vs-A is zero diff.* Two runs of the same pin (id, version, region)
  in one CI job give the same `pass` for every golden. If they do not,
  the suite is flaky and **the milestone stops** (SPEC/00 §8 M04): row 4
  closes RED with the flaky golden as the finding.

**Why refagent should give zero diff when the control does not.** The
control is non-deterministic at temperature 0 (Finding F0.4, SPEC/00 §8
M00; `milestones/M00/feasibility.md` §6.5), which SPEC/00 names as the
seed for this design. The control is a model answering from memory with
no tool; refagent answers from a row the tool returns, which fixes most
of what the answer says. Eleven envelopes on the incumbent pin
(`8b99586` to `164a95b`) show no golden changing between runs that did
not change the agent. That is a record across commits, not an A-vs-A;
M04 measures it in one job. The control runs A-vs-A too, **reported and
never gated** (ADR-0004): its diff is F0.4 measured, not `F4_3`.

## 2. Words used here

- **Pin.** refagent's `model` in `agents/refagent/manifest.yaml`: `id`,
  `version`, `profile`, `region`, and `deprecated_after` (Threshold Owner;
  `profile` and `deprecated_after` by ADR-0010, finding 10). The gate
  refuses an envelope whose model is not the pin at its commit
  (ADR-0007, T3), so a swap is always a change to the pin in a pull
  request, never a flag on a run.
- **Incumbent.** The pin in the manifest at the merge-base of the
  envelope's commit with `main`. At M04 open: Sonnet 4.6, `id`
  `anthropic.claude-sonnet-4-6`, profile `us.anthropic.claude-sonnet-4-6`,
  `version: null`, `us-west-2`. On a pull request that does not change
  the pin, the incumbent is the pin under test.
- **Candidates** (`pinned_roles`, Threshold Owner; each answered a call
  on 2026-09-26, `milestones/M04/runs/model_access_2026-09-26.md`; each
  profile routes to us-east-1, us-east-2 and us-west-2):
  - *equivalent*: Sonnet 4.5, `anthropic.claude-sonnet-4-5-20250929-v1:0`.
    Named equivalent **before** any run. If its run regresses a golden,
    F4.2 fires and that is recorded as the finding; the label is not
    moved after the result;
  - *breaking*: Llama 3.1 8B, `meta.llama3-1-8b-instruct-v1:0`;
  - *cheaper*: Haiku 4.5, `anthropic.claude-haiku-4-5-20251001-v1:0`.
    Reported, not a falsifier; its run is cut first (§9), and it stays on
    the eval role's list either way;
  - *deprecation plant*: Sonnet 4, `anthropic.claude-sonnet-4-20250514-v1:0`.
    `LEGACY`, refused on every call, `endOfLifeTime` 2026-10-14T08:00Z
    (read 2026-09-26). S5's model and nobody's swap: a model that cannot
    be called cannot show a before.
- **Breaking.** A swap under which a golden that has passed before now
  fails (P7).
- **Tool-grounded.** An ordinary or trap answer is tool-grounded when the
  same answer made a `check_availability` call with `status: success`
  whose output's `row.table_row` equals the answer's `table_row`, and
  whose `clause_candidates` include the answer's `clause_id`. SPEC/00 §9:
  "the rights table is the truth ... never inferred". Part of CORRECT
  from PR 2 (the Data Owner, ruling on finding 4). **Ruled at PR 2, before
  the reader landed** (`rulings/pr2-data-owner.md`): `g-021`, the one
  answer where no row governs (`found: false`, `row: null`), is retired
  with two keys and nothing is added; the absence form it needs, with the
  Tool Owner's question of which clauses a not-found result offers, is
  M06's. And the answer is grounded **on the golden's own row**: its
  `table_row` is also the golden's `expected.table_row` (data-owner F5).
  A call on the wrong title returns the wrong row, which grounding alone
  would accept; the call's input is not read. The row only, not the
  clause. SPEC/00 §9 is amended at PR 1 to say CORRECT includes grounding
  from PR 2.
- **`delta_max`.** The relative bar SPEC/00 §8 M04 names ("within
  `delta_max` of the incumbent"; "one policy, not both", changed here
  under its own "unless a ruling changes it" by ruling 2). **It applies
  to p95 latency and to the agent's tokens per run, not to goldens.** A
  golden that has passed and now fails blocks under any model (P7, R2,
  claim 3); a relative bar on goldens would let a swap regress one, and
  contradict row 3. Two bars, stated before any run (the Threshold
  Owner, ruling on finding 3):
  - `p95_ms` no more than **2.0×** the incumbent's;
  - the agent's tokens (in plus out, the agent's side only) no more than
    **1.5×** the incumbent's.
  "The incumbent's" is the median over the envelopes in `evals/history/`
  on the incumbent pin (its profile and region) **in the same `mode`** as
  the envelope ruled. An envelope with no `mode` (version 1, before
  ADR-0007) is not counted. The run's side of each comparison is **its
  first refagent run**: p95 over that run's latencies, and that run's
  tokens, the agent's side only. `build` writes that run's tokens as an
  envelope field of its own, optional so no past envelope becomes invalid,
  and the bar reads that field: the envelope's `tokens_in` and
  `tokens_out` count every run the job made, and with A-vs-A they hold
  two agent runs (threshold-owner F1, second read). A-vs-A's second run is
  compared with the first and never with the bar, and never lifts the
  incumbent's median. **A bar with no incumbent envelope in that mode writes
  `F4_4: fail`, and the envelope is RED**, with the reason; a mode the
  incumbent never ran in is not a way past the bar (threshold-owner F1 to
  F3 on PR 1).
  The bars apply to **every agent envelope**, not only to swaps: F4.4 is
  "a p95 regression beyond the bar", whatever the diff (threshold-owner
  F4). A prompt or tool change that makes the agent 1.5 times as costly
  is held to the same bar, and relaxing it is two keys.
  `cost_cap.tokens_per_run` stays beside them: it is a budget, absolute
  and per run, not a quality bar. SPEC/00 §8 M04's "one policy, not
  both" is about quality bars (threshold-owner F5).
  **The rule for a miss on p95, added at M07 PR 2** (the Threshold Owner,
  ruled 2026-10-02, `milestones/M07/rulings/pr2-threshold-owner.md` item
  2; written here by Product). The bar stays at 2.0 and the reading stays
  as it is. M07 PR 1's first run was RED on `F4_4` alone at 14,281 ms,
  2.06 times the incumbent's median, and GREEN 30 minutes later at 5,830
  ms, on a diff that changed nothing refagent runs: with about nineteen
  answers in a run, p95 is close to the slowest single call. So: when
  `F4_4` alone fails on a pull request whose diff touches **nothing the
  agent runs** (`agents/`, `src/agent/`, `infra/construct/`, the pin, the
  guardrail, `rules/`, `data/`), **one** second run may be made. It is
  stated before, in a run file under the milestone's `runs/`, and pushed
  first. Both envelopes stay in `evals/history/`; the second rules. There
  is no third. **A swap pull request never gets a second run**: its p95
  is the thing under test. One exception, named with it (item 3): the
  revert of a merged swap that is RED on `F4_4` alone, since a revert
  restores the incumbent of record. Raising `p95_ratio_max` is not this
  rule; it is a relaxation, with two keys. No gate reads this rule: the
  run file and both envelopes are its record, and a second run made
  outside it is a finding for the Threshold Owner.
- **p95.** `p95_ms` on the envelope, from the per-answer `latency_ms` the
  runner or the runtime records (from M01 PR 2). Not k6 at M04 (§9). On
  the incumbent pin before the guardrail, six `runner` envelopes ranged
  4,845 to 8,641 ms and five `runtime` envelopes 5,415 to 7,996 ms. The
  bar compares with a median, so the comparison that matters is the worst
  run against it: across all thirty Sonnet 4.6 envelopes the slowest is
  1.63× their median, and 1.48× the runner median. 2.0× clears every run
  on record with no change to the model (threshold-owner note 10).
- **A-vs-A.** Two runs of refagent, and two of the control, on the same
  tree and pin in one `evals` job. Zero diff means every golden's `pass`
  is the same in both. Latency, tokens and text are not compared.
- **`deprecated_after`.** The manifest field (SPEC/00 §6; the schema
  allows a date or null). Bedrock publishes `modelLifecycle.endOfLifeTime`
  only once a model is `LEGACY`: on 2026-09-26 the incumbent and all three
  candidates are `ACTIVE` with none, so refagent's null is a reading ("no
  date announced"), not a gap. At M04 the date is set by hand from that
  reading; setting it from Bedrock by code is cut to M07 (§9, cut g).
  Moving the date later, setting it to null, or removing it, **with
  `model.id` unchanged**, is a relaxation, the Threshold Owner's key
  (ADR-0009 amendment 1, entry 6; threshold-owner F6). A swap changes the
  id, so its date is not compared with the old one; instead a swap to a
  model Bedrock marks `LEGACY` carries that model's `endOfLifeTime` as
  its `deprecated_after`, and the swap's Threshold Owner ruling records
  the `modelLifecycle` it read (threshold-owner F4, second read).
- **`version`.** For an id that carries a version, `version` records that
  suffix (Sonnet 4.5: `20250929-v1:0`); it is null only when the id has
  none, as Sonnet 4.6's has not (ruling G). The swap PRs follow this; the
  seed patches stay as planted (threshold-owner F8).

## 3. The false state

Claim 4 is false if any of these is on `main`. Each names something a
reader can look at.

**Live today.**

1. **A breaking swap can rule GREEN** (S1). `verdict.build.score_one`
   passes an ordinary or trap answer when its fields match and its
   `table_row` and `clause_id` exist. It never reads `tool_calls`, which
   the runner records for every answer (`agents/refagent/agent.py`). A
   model that prints its tool call as text, or calls the tool with
   arguments the schema refuses, and then states a plausible row, passes.
   Nothing in the envelope says the tool was not used.
2. **An equivalent swap cannot promote** (S2). The eval role may invoke
   `amazon.nova-micro-v1:0` and `anthropic.claude-sonnet-4-6` and nothing
   else (`infra/bootstrap/app.py`, `MODELS`). A swap PR to Sonnet 4.5 is
   refused on every call, every golden fails, and the gate rules RED. The
   refusal is IAM's, not the gate's reading of the model.
3. **Nothing runs A-vs-A** (S3). Each envelope is one run of refagent.
   No check compares two runs of one pin, so a flaky golden shows up
   only as a regression on some later PR, blamed on that PR's diff.
4. **A p95 regression is GREEN** (S4). `p95_ms` is written on every
   agent envelope and read by nothing. `thresholds.yaml` has no bar for
   it, and none for the agent's tokens relative to the incumbent.
5. **A pin past its end of life passes `validate`** (S5). `validate`
   does not read `deprecated_after`. No falsifier of claim 4 names this;
   SPEC/00 §8 M04's build list does, and SPEC/00 §10.5 allows no control
   without a seeded case.

**Held today, and named so nobody plants them as open.**

6. **A run that measured another model counts.** The gate REJECTs an
   envelope off the pin (ADR-0007, T3), and a pin whose `id` and
   `profile` disagree.
7. **A breaking swap that fails a golden outright merges.** A golden
   that has passed and now fails is `regressed` and RED (claim 3, guard
   1 of SPEC/03 §5.2).

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F4.1 | the breaking swap is GREEN | S1's raw run built and gated GREEN in a copy of the tree; or the breaking swap PR's `evals` check green, or its envelope GREEN, or RED for a reason other than §7's; `checks.F4_1: fail` from the seed test; from PR 3, the live swap in the envelope's `swaps`, recorded and not gated (§4) |
| F4.2 | the equivalent swap is RED | S2's pin not among the models the eval role may invoke; or the equivalent swap PR's envelope RED or REJECTED, or a required check on it red for a reason of its own; `checks.F4_2: fail` from the seed test; from PR 3, the live swap in the envelope's `swaps`, recorded and not gated (§4) |
| F4.3 | A-vs-A shows a diff | refagent's two runs in one `evals` job with any golden's `pass` different; `checks.F4_3: fail`, the differing ids in the envelope's `a_vs_a`. The milestone stops (§1) |
| F4.4 | a p95 regression beyond the bar is GREEN | S4's raw run built and gated GREEN; or an agent envelope whose `p95_ms` or agent tokens are over the bar at its commit, ruled GREEN; `checks.F4_4: fail` |

**Where each check comes from** (ruling on BLOCK 1, M02's pattern).

- **From PR 2's merge, on every agent envelope:** `F4_1` from the S1
  test, `F4_2` from the S2 test, `F4_4` from the S4 test and the gate's
  own reading of the run's `p95_ms` and tokens. `F4_1` and `F4_2` from a
  seed test alone are **test-only witnesses**, as M03's `F3_1` was, and
  the ledger says so.
- **`F4_3`, on the envelopes where A-vs-A runs:** PR 2's own run, and
  any run whose pin differs from the incumbent (a swap). From the run's
  own two refagent raws, compared by `verdict.build`. Not on other PRs:
  it doubles the spend, and a flake after the close would block every
  M05 PR with no FRAGILE to hold it (finding 6).
- **The swap PRs, from PR 3 (amended at PR 3, Product):** looked up in
  GitHub's record by `scripts/observe_pr.py` (M02's reader) from
  `milestones/M04/runs/f4_swaps.yaml`, and each one's own envelope ruled
  by the gate at its commit (`scripts/rule_swaps.py`). `build` records
  both in the envelope's optional `swaps`, and **nothing gates it**:
  `F4_1` and `F4_2` stay the seed tests' witnesses. As first written,
  `build` wrote each check as pass only when both sources passed. The
  equivalent swap's first run regressed `g-005` in both of its runs, so
  F4.2 fired; a check that failed on every envelope from then on would
  have blocked every later pull request for a result that is already the
  finding, and the one run that read it could not have merged. The
  ledger's Measured cell prints `swaps`, so `make ledger` holds row 4 to
  a CI-written envelope. A named P3 exception (§5.1).
- **A swap PR never reads itself.** `observe_pr` skips the pull request
  its own run is on, and `rule_swaps` writes it unread. Once `main` is
  merged into a swap branch its tree carries `f4_swaps.yaml`, so its run
  records the other swap; recorded only, as everywhere.

`CLAIM_4_CHECKS` in the gate: `F4_1`, `F4_2` and `F4_4` on every agent
envelope from PR 2's merge commit; `F4_3` on the envelopes above.

**P5.** `verdict.build` writes the checks; `verdict.gate` reads the
envelope, the tree at the envelope's commit and history.
`tests/test_p5_disagree.py` gains a case for each new check.

## 5. The seeded cases

Planted at PR 1 under `tests/fixtures/m04/`, one commit per seed, each
with its test in `tests/test_m04_seeds.py` marked
`xfail(strict=True, raises=...)` naming the one exception its planted
reason raises, and run once with `--runxfail` so the message is read.
Each test asserts the planted reason, not only the verdict. The marker
comes off in the commit that lands the reader. If a reader lands under
another name, PR 2 changes the call, never what the seed adds. Each seed
is named in `tests/fixtures/README.md` and listed in
`src/verdict/plants.py` as `SEEDS_M04`; no seed is copied to
`evals/history/`.

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S1 a breaking swap | F4.1 | `s1-breaking-pin.patch`: the pin moved to Llama 3.1 8B. `s1-breaking-raw.json`: refagent's raw run under that pin, in the runner's shape, where every ordinary and trap answer has the expected fields and a real `table_row` and `clause_id`, and no successful tool call (the call printed as text in the reply, or refused by the schema). The worst case, not a prediction of what Llama does | `score_one` does not read `tool_calls`: every citing golden passes and the gate rules GREEN | `score_one` passes a citing golden only when it is tool-grounded (§2) |
| S2 an equivalent swap refused | F4.2 | `s2-equivalent-pin.patch`: the pin moved to Sonnet 4.5, nothing else changed | Sonnet 4.5 is not among the models the eval role may invoke: every call is `AccessDeniedException` | the eval role's candidate list in the bootstrap stack (Security), deployed by the human |
| S3 A-vs-A with a diff | F4.3 | `s3-a.json`, `s3-b.json`: two raw runs of the incumbent pin, identical but for `g-006`, which passes in one and fails in the other | nothing compares two runs; each alone builds GREEN | `build` given a second raw of the same pin writes `F4_3` and `a_vs_a` |
| S4 a slow swap | F4.4 | `s4-slow-raw.json`: a raw run on the incumbent pin with every answer as the incumbent's and every `latency_ms` three times its value; `s4-heavy-raw.json`: the same with the agent's tokens two times | no bar reads `p95_ms` or the agent's tokens against the incumbent; the gate rules both GREEN | the `delta_max` bars in `thresholds.yaml` and the gate reading them |
| S5 a pin past its end of life | none (SPEC/00 §8 M04) | `s5-deprecated-pin.patch`: the pin moved to Sonnet 4 with `deprecated_after: 2026-10-14`, Bedrock's `endOfLifeTime` | `validate` does not read `deprecated_after` and is green | `validate`: a pin whose `deprecated_after` is within 30 days of the run, or past, fails; null passes |

**S5 has a date.** Bedrock ends Sonnet 4 on 2026-10-14. Read before
then, S5 is "fails 30 days before". Read after, it is "already past",
which the same check refuses; the feasibility note says which the reader
met.

### 5.1 When each is measured

- **PR 2's run, on the PR.** S1, S3, S4 and S5 read by their tests;
  `F4_3` from the run's own A-vs-A; `F4_4` from the run's own `p95_ms`
  and tokens.
- **The bootstrap redeploy, during PR 2.** Security adds the three
  candidates to a new list the eval role alone may invoke. `MODELS` is
  not changed: it also feeds the agent boundary and the deploy role
  (note 15). The template's size is measured before the edit (47,601 of
  51,200 bytes at M03's close; `open.md` row 7). The human reads
  `cdk diff --strict`, which also answers whether the deployed template
  reads `§` (`open.md` row 6), and deploys. S2's test then passes.
- **`pinned_roles` first, during PR 2.** The Threshold Owner completes
  region and version on every swap role (`open.md` row 14) before either
  swap PR is opened (threshold-owner F5, second read). The manifest edit
  moves the context the seed patches carry: PR 2 regenerates the three pin
  patches in the commit that edits the manifest, and re-runs each seed
  with `--runxfail`. Rebasing a patch's context is not changing what the
  seed adds; the lines a patch changes stay as planted (cold review N4).
- **The swap PRs, during PR 2.** After the readers land, the human opens
  two draft PRs against `main`, each branched from PR 2's head and each
  changing only the pin: one to the breaking candidate, one to the
  equivalent. Each runs refagent in `mode: runner` (its bundle differs
  from the deployed one), with A-vs-A. Their numbers go in
  `milestones/M04/runs/f4_swaps.yaml`, and their rulings (Threshold
  Owner, `pr:` each swap PR) into PR 2. **Amended at PR 3:** PR 2 (#24)
  merged before either joined it, and the swap PRs (#25, #26) ran after,
  so both are in PR 3.
- **After PR 3 merges** (amended at PR 3; was "after PR 2 merges"). The
  swap PRs' rulings are on `main`. `main` is merged into each swap
  branch, which leaves its diff the pin alone, and its checks run again
  on PR 3's repaired tests. PR 4's run looks both up: the named P3
  exception, as M02 read its seed PRs at PR 3. **PR 3 is the repair and
  the read's machinery; PR 4's run is the read.** PR 4 records the swaps'
  new envelopes in `f4_swaps.yaml`, which is not prose, so its run
  measures and reads them rather than reuse an earlier envelope
  (security-reviewer F3 on PR 3). The machinery is not
  built in the last PR: it lands and runs at PR 3, where it reads the
  swaps as they stand then. If either misses at PR 4, row 4 closes RED
  with that as the finding. There is no fifth PR.
- **Amended at PR 4, before its run (Product, `rulings/pr4.md`): a
  second named P3 exception.** Row 4's cell reads the recorded swaps
  (`READ_THE_SWAPS` in `src/verdict/gate.py`): a swap that misses its
  falsifier's verdict, or is unread, makes the cell RED whatever
  refagent's own verdict. It lands in the last PR because PR 3 left
  `make ledger` unable to write the RED §7 names beside refagent's
  GREEN, which the cold review of PR 4 found (B1). It gates no pull
  request, leaves `rule` unchanged, and can only turn row 4's cell RED.
- **Never:** no swap PR merges. The equivalent swap is closed unmerged
  once read.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1. In the order the commits land:

- **Tool grounding** (`src/verdict/build.py`, Engineering; the Data
  Owner's ruling on CORRECT, finding 4): S1's reader, as §2 defines it.
  `g-021` is ruled first (§2).
- **`deprecated_after`** (`src/validate/`, Engineering): S5's reader.
  refagent's own stays null, recorded against Bedrock's reading.
- **`delta_max`** (`thresholds.yaml`, Threshold Owner): two bars,
  `relative.p95_ratio_max: 2.0` and `relative.agent_tokens_ratio_max: 1.5`, each
  relaxing upward. Adding a bar is not a relaxation (ADR-0009). The gate
  reads them at the envelope's commit, finds the incumbent (§2), and
  writes the reason. S4's reader.
- **A-vs-A** (`evals.yml`, Security; `build`, Engineering): the job runs
  refagent and the control twice when §4 says; `build` takes the second
  raws, refuses a pair whose pin, region or commit differ, and writes
  `F4_3` and an optional envelope field `a_vs_a`: `{"agent": [ids that
  differ], "control": [ids that differ]}`. Optional, so no envelope in
  history becomes invalid (ADR-0007's rule). S3's reader.
- **The cap** (Threshold Owner): re-ruled against PR 2's measured spend
  with A-vs-A (`open.md` row 12). The envelope's `tokens_in` and
  `tokens_out` count every run the job made. A raise is two keys
  (ADR-0009, entry 3's consequence). At `cb06c0d` the run spent 52,131
  (47,034 in, 5,097 out) against 150,000; A-vs-A roughly doubles it.
- **The eval role's candidate list** (`infra/bootstrap/app.py`,
  Security). S2's reader.
- **`pinned_roles`** (Threshold Owner): region and version on every
  swap role, and the stub's model fields (`open.md` row 14).
- **`scripts/observe_pr.py`** (Engineering) given
  `milestones/M04/runs/f4_swaps.yaml`; it skips its own PR. Written at
  PR 2; wired at PR 3 with `scripts/rule_swaps.py`; read at PR 4's run
  (amended at PR 3).
- **`CLAIM_4_CHECKS`** in the gate; the new `--check-*` in `build` and
  `evals.yml`.

## 7. Expected on the plant (row 4)

- **PR 1.** refagent's envelope, gated and recorded as at M03; it says
  nothing about claim 4. PR 1 leaves `agents/refagent/**` and
  `data/rights_table.json` alone, so its run can be the first
  `mode: runtime` envelope at guardrail version 5 (`open.md` row 10);
  whether it is, the envelope says. `make plants` lists S1 to S5.
  `uv run pytest tests/test_m04_seeds.py` shows six expected failures
  (S4 has two cases, p95 and tokens).
  `make validate` passes: a patch is not a manifest. `make ledger` exits
  0.
- **PR 2's run on the PR, stated before it.** S1 to S5 refused, each for
  its planted reason. refagent under grounding: **ordinary 9/9, traps
  2/2**; fewer is a finding, not a count to lower. Restated at PR 2,
  before its run (data-owner F16): `g-021` was retired before grounding
  landed, with two keys, and nothing was added (M04 `open.md` row 5; the
  absence form is M06's), so the traps are `g-010` and `g-011` and no new
  id is in `never_passed`. Those counts were never grounded in an
  envelope: PR 2's run is the first measurement of them (data-owner F7).
  A-vs-A zero diff for refagent, on PR 2's own run (the `a-vs-a` label);
  the control's diff recorded, not gated. p95 and tokens within their
  bars.
- **The reading run (PR 4's; PR 3's as first written), stated before it.** The breaking swap PR RED with at
  least one citing golden `regressed`, ungrounded or with wrong fields,
  and none of these: REJECTED, access errors, the cost cap. Any other
  RED is a finding, not a pass (finding 2). The equivalent swap PR GREEN
  with every required check green and A-vs-A zero diff.
- **The row goes RED** if a seed's test passes for a reason other than
  its reader; if the breaking swap is GREEN or RED for another reason;
  if the equivalent swap is RED or any of its required checks stays red
  for a reason of its own; if refagent's A-vs-A shows any diff; if a p95
  or token count over its bar rules GREEN; if PR 4's run cannot read the
  swap PRs; or if `make ledger` stops matching rows 0 to 3 when a bar
  lands. **Recorded at PR 3, before the reading run:** the equivalent
  swap's first run (#26, `9ff21d5`) regressed `g-005`, the same way in
  both runs (available, clause `EM-1`, no embargo, where 01:30 UTC is
  still 13 May in São Paulo). **That run decides F4.2** (Product, on
  threshold-owner's finding and the cold review's F2 on PR 3): §2 named
  the candidate before any run, and nothing since has touched the model,
  `g-005` or the rights table, so a different answer at the reading run
  would be a difference between jobs, not a fix. The reading run records
  the swaps on the repaired tree; a GREEN there is recorded beside the
  first run, and row 4 closes RED on F4.2 either way.

## 8. Controls with no seeded case at M04

SPEC/00 §10.5: no document describes these as working.

- noticing that Bedrock has announced an end-of-life date, and setting
  `deprecated_after` from it: nothing polls Bedrock until `model-watch`
  (M07; §9 cut g). Until then the Threshold Owner reads `modelLifecycle`
  on every swap PR and records it in the swap's ruling;
- the model changing under an unchanged pin (a provider update with no
  diff): A-vs-A catches it only inside one job, and only where A-vs-A
  runs. `model-watch`, M07;
- the cheaper swap's economics: Haiku 4.5's run is reported, not ruled;
- a model called without the pinned guardrail, or around the agent's
  own profile (M05; `open.md` row 26, and new item 40 in
  `milestones/M04/feasibility.md` §6);
- the judge, and a judge model swap (R6): §9, M07;
- the guardrail on a candidate's answers: every topic is assessed on the
  question only (`topics_apply_to: input`, `open.md` row 17), so a swap's
  plants fire before the candidate is called. "Plants 7 of 7" on a swap
  PR says nothing about the new model. The PII rule reads the answer as
  well, but its plant, `g-014`, is not counted until M06 (cut f). M06,
  with retrieval (rule-owner F7 on PR 1; note 6 on the second read).

## 9. Cut list

Cuts a to g are **taken at open** (rulings 4 and 6, and finding 7). The
numbered cuts are taken in order, item 1 first, only if the cap is
threatened. None cuts a seed, a seed's reader, A-vs-A, the two swap PRs
or the eval role's candidate list.

| # | Item | Milestone | Why |
|---|---|---|---|
| a | `model-watch` as a scheduled workflow: polls Bedrock, shadow run, draft PR, never merges | M07 | A PR opened with `GITHUB_TOKEN` starts no workflow, so its shadow run needs a GitHub App or a token (Security). M07's claim is that a model upgrade arrives as a PR; Act 4 is recorded at M07. At M04 the swap PR's own `evals` run is the test |
| b | The Bedrock Evaluations judge pinned in the manifest, its rubric, the graded-examples set, `model-watch` covering the judge (R6), and `admitted_false_fails.json` (SPEC/03 cuts 2 and 3; their second move) | M07 | R6 in one milestone, with `model-watch`; before M08 aims an injection at the judge. Until then "correct" is the answer's fields compared by code, and from PR 2 tool-grounded |
| c | The Braintrust mirror, its divergence check, and redaction before upload (SPEC/03 cut 1; second move) | M07 | SPEC/03 tied its first diff to `model-watch`'s draft PR |
| d | FRAGILE (SPEC/03 cut 4; second move) | M06 | At M04 an A-vs-A diff stops the milestone; nothing is marked fragile. `docs/developer/goldens.md` (M06) documents it |
| e | k6 | M05 | M05's build list brings k6 for fan-out at the ceiling. Until then p95 is the per-answer latency (§2) |
| f | The knowledge base over the production bucket and refagent retrieving from it (SPEC/03 cut 6; second move); with it the cached-answer seed, F3.5's second half, `g-014` counted as a plant, and M04 `open.md` rows 3, 8, 9, 15, 17, 18 | M06 | Not claim 4. The refagent the template ships must read its corpus, and `docs/refagent/walkthrough.md` traces a retrieval. SPEC/00 §9 is amended in this PR to say so. A third move is a SPEC/00 amendment, not a cut |
| g | `deprecated_after` set from Bedrock by code | M07 | Polling Bedrock is `model-watch`'s job. S5's reader checks the date the manifest carries |
| 1 | The cheaper swap's run (Haiku 4.5) | M07 | Reported, not a falsifier |
| 2 | `open.md` rows 11 and 22 (the rights-table marker re-read; `server.py`'s profile default; the gate taking build's token sums) | M05 | Engineering fixes to the runtime reading, not claim 4's readers |

Never cut: S1 to S5 and their readers; A-vs-A in `evals`; the breaking
and equivalent swap PRs; the eval role's candidate list; the `delta_max`
bars.

## 10. Not in M04

- Merging a swap. "Promotes" is mergeable (§1).
- A relaxation. **A model id change is not on ADR-0009's list** (ruling
  3, Threshold Owner): the measured gate is its control, and the
  Threshold Owner's ruling on the swap PR is its key. A cheaper model
  that regresses nothing is not a lower bar. CLAUDE.md's seat table is
  amended in this PR to say so (finding 9).
- The gateway (`milestones/M04/runs/llm_gateway_probe.md`; M05 open).
- Any change to `src/baseline/` (ADR-0002). The control stays Nova Micro
  at `m00`; a swap moves the agent, never the control.
- A second agent's model (M06).
