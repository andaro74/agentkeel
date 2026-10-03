# M07 — Upgrade, retire, surfaces

## Ledger row

Written at M07 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 7 |
|---|---|
| Claim | An agent takes a platform, model or retirement upgrade without a workflow edit |
| Falsifiers | F7.0 no agent from the template exists to upgrade: the owner's test's fixed head is refused, or not merged, deployed, answering and listed; the timed run's agent the same; or the platform check dispatched from a branch reaches the App's key (added at M07 PR 1). F7.1 an upgrade requires a manual edit: no pull request the platform opened arrives, or a workflow or a person's commit was needed to merge it; a ruling file is not a person's edit (reworded at M07 PR 1). F7.2 a retired agent still answers. F7.3 a rollback leaves the new digest live. F7.4 a Grafana panel shows GREEN where the envelope says RED (read through Grafana's query API, as F6.4; not Playwright). F7.5 `plants_expected ≠ plants_fired` for the surfaces. |
| Seeded commit | `c870bca` (S0 the template's repair read by CI: the owner's test, the App token's bounds); `ef3d88a` (S1 a platform bump opens a draft pull request); `3872c13` (S2 a retired agent's target is gone); `ea53ef4`, its run file made to parse in `a46c98f` (S3 a `model-watch` pull request merged and rolled back); `e814efe` (S4 panel 2 forced to show GREEN on a RED envelope, two tests, one per reader); `f36adee` (S5 a surface plant goes silent); the fixtures given their held cases and three more uncovered ones in `4240d9e`, on the PR's own review, each its own commit before any reader (SPEC/07 §5). S0 to S3 are each a fixture and a run file with `observed: null`; S4 and S5 are fixtures. SPEC/06's S3 (`b4eb959`, the timed quickstart) is received, not re-planted |
| Expected gate output | PR 1: refagent's envelope as at M06; it says nothing about claim 7. `make plants` lists S0 to S5 (seeded cases, not golden plants); `tests/test_m07_seeds.py` shows 13 expected failures, and `tests/test_m06_seeds.py` still 1 (S3's). PR 2, on the PR: the nine fixture tests pass, each by its reader, and the four run-file tests stay expected failures; from PR 2's merge the gate requires `F7_0` to `F7_5` on every agent envelope, **from the seed tests alone: test-only witnesses**. The live readings are **recorded in the envelope's `upgrade` and read by this row's cell, with `template`, not gated** (SPEC/07 §4): the observer writes raw observations with the viewpoint it read from, and `build` rules on them. **A named P3 exception (SPEC/07 §5.1):** the platform check, the deploy, `platform-upgrade`, `model-watch` and the retire job run from `agentkeel`'s `main`, and the App's grant is made by hand after PR 2 merges, when `main` no longer mints a token with no repository. The platform check dispatched from a branch is attempted first, before any grant, and must be read as refused. Then, after PR 2's merge, each stated before and pushed: the grant made and read back; SPEC/06's S2 read on a new head; the owner's test, steps 2 to 4; SPEC/06's S3 timed once by `floresinnovations`; the template re-made and S1's pull requests; the App's token asked to relax a ruleset; `model-watch`'s swap to Haiku 4.5 and its rollback (independent of the others; its two pull requests on `main` are outside the cap); `owner-check` retired, last. PR 3 is the repair and carries every attempt's `observed` entry to `main`; PR 4 is the close. **Amended at PR 3 (Product, `rulings/pr3.md`): that cannot hold. The owner's test's deploy failed in the platform's own `deploy.yml` (run 37023118799), the deploy runs from `main`, and no later attempt can be made until the fix is merged. So PR 3 is the workflow fix and every repair owed before the next attempts, merged once, and carries one `observed` entry, the owner's test's; PR 4 carries every other attempt's entry and is the close, so those are read from the anonymous viewpoint alone (SPEC/07 §4). The owner's test is not re-made: its deploy missed `upgrade.deploy_max_seconds`, F7.0 fired, and this row is expected to close RED.** **The cell cites PR 4's run's envelope**, which carries the App-viewpoint observation `main`'s scheduled observer made, named, beside its own anonymous one. Stated at open: the owner's test's new head refused on the seats and the goldens and nothing else, its fixed head merged, deployed within 3,600 s, answering and listed; S1's draft pull request from the App within 4,500 s, platform-owned files only, no person's edit, major or minor as read; S2 retired within 3,600 s of its pull request's merge, its one invocation refused; a revert leaving the tree's digest live. Haiku 4.5's envelope is **not stated**: it has never been run. If it is RED the swap is not merged, F7.3 is read on `owner-check`'s platform upgrade reverted, and `upgrade.taken` stays under 3. The measured value is `upgrade.taken`, n of 3. RED if F7.0 is unread or fired; if `taken` is under 3; if a trigger gets no pull request from the platform, or one that needed a workflow or a person's edit; if the retired agent answers or its runtime stands; if a revert leaves the upgrade's digest live; if panel 2 shows GREEN on a RED envelope or the surfaces' counts differ; if a seed's test passes but by its reader; if PR 4's run cannot read an attempt; or if `make ledger` stops matching rows 0 to 6. **Amended at the close (Product, `rulings/pr4.md`): the swap read RED and was not merged, and the rollback was read on `window-check`'s platform upgrade reverted, not `owner-check`'s: `owner-check` is retired before the closing run, which deletes the runtime F7.3 reads.** |
| Measured | agent: traps 2/2 (g-010, g-011); ordinary 9/9; guardrail 2/3; redteam 5/5; control: traps 0/2; ordinary 1/9; guardrail 0/3; redteam 0/5; mode runtime; never_passed 1; regressed 0; plants 7/7; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; F1_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F1_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F1_3 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F1_4 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F2_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F2_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F3_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F3_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F3_3 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F3_5 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F3_6 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F4_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F4_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F4_4 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F5_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F6_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F6_4 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_0 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_1 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_2 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_3 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_4 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; F7_5 pass https://github.com/andaro74/agentkeel/actions/runs/37149475766; taken 2 of 3; F7_0 not held (relaxation detected); F7_1 unread; F7_2 held 368 s; F7_3 held; F7_4 held; F7_5 held; surface plants 2/2; claim 6 later F6_1 not held; claim 6 later F6_3 held 3615 s; F7_0 not held: owner_test: deployed 32264 s after the merge, over upgrade.deploy_max_seconds 3600; F7_1 unread: model andaro74/agentkeel#43: unread: the pull request has not merged; taken 2 of 3: model unread; RED; envelope `dee74c3cf4102bfb6d4315faafb161c154618ed9`; base b0219756 |
| PRs used / cap | 5 / 4 |
| State | RED |

### Open detail (PR 1, 2026-10-01)

- **Opened through `/open-milestone`.** M06 is closed (RED, tag `m06` on
  `57b9bf6`). SPEC/07 was written first (`83eb558`) and
  `product-spec-reviewer` run on it (3 BLOCK, 26 FINDING, 12 NOTE), pasted
  verbatim in `feasibility.md` §1. The human ruled every item on
  2026-10-01, "as proposed", before any seed (`66e6c0f`): the three BLOCKs
  as option (a). SPEC/07 was revised once on the rulings (`addd8cc`) and
  SPEC/00 amended (`956fdc2`), both before the first seed (`c870bca`).
- **The precondition is a seed.** An upgrade needs an agent made from the
  template, and at M06's close there is none: the platform's App refuses
  every head of every agent repository. So the template's repair is S0,
  read by CI through the owner's test, with a new falsifier, F7.0; and
  SPEC/06's S3, the timed quickstart, is received and never cut. The
  agents that take the upgrades are `owner-check` and the timed run's.
- **BLOCK 1: a retirement arrives as a pull request.** The platform opens
  a draft that sets `rollout: retired`; the agent's seats merge it; the
  deploy path retires instead of deploying. Archiving a repository is not
  the trigger.
- **BLOCK 2: a ruling file is not a person's edit.** A model upgrade in
  `agentkeel` cannot merge without a seat ruling it; F7.1 reads every
  other path on the pull request.
- **BLOCK 3: what is not built.** M08 adds no code path, so a code item
  cut from M07 is cut from the project. Taken at open and recorded in
  SPEC/00 §12: the knowledge base (its fifth move), the judge and FRAGILE,
  the Braintrust mirror, HITL as a Gateway tool with `ratings-helper`'s
  code, the gateway, k6 and the CLI. **Not measured in this project** with
  them: the cached-answer seed, F3.5's second half, `g-014` as a plant,
  and S5 of SPEC/05's live half. Six contradictions with M08's text, R6
  and SPEC/00 §15 are recorded in SPEC/00 §8 M07 and are **owed to M08's
  `open.md` at this milestone's close**. One is a number the ledger gives
  today: rows 1, 4, 5 and 6 are RED, so §15's "at least seven are GREEN"
  cannot be met.
- **F7.1 and F7.4 reworded.** As written, F7.1 ("a manual workflow edit")
  could not fire in an agent repository, which has no workflow. F7.4 is
  read through Grafana's query API, as F6.4 was; Playwright is not used.
- **M06's P3 exception again, and M06's lesson.** Everything live runs
  from `main`, so the attempts are made after PR 2 merges and their
  `observed` entries reach `main` in PR 3. The live readings are recorded
  in the envelope's `upgrade` and read by row 7's cell; they gate no pull
  request. `F7_0` to `F7_5` on every envelope come from the seed tests, as
  test-only witnesses.
- **The grant is not in this PR and not before PR 2's merge.** Until
  `main` stops minting a token with no repository (`scope = {}`), the App
  is not granted Administration: write. `rulings/pr2-security.md` rules
  each bound of `open.md` row 2 and one permission set per workflow first.
- **Planted** in six commits, one per seed, `c870bca` to `f36adee`, each
  with its tests in `tests/test_m07_seeds.py`, before any code that reads
  them: 13 expected failures, each run once with `--runxfail` and its
  message read (`feasibility.md` §3). S3's run file did not parse at
  first; the strict marker failed the run on it, and `a46c98f` repaired
  the file.
- **Row 20's read, recorded** (`runs/platform_app_environment.json`,
  `runs/platform_app_branch_policies.json`, 2026-10-02T02:12Z): the
  `platform-app` environment has one branch policy, `main`, and
  `can_admins_bypass: true`. Whether the second is inside the bound is
  Security's, before PR 2 (SPEC/07 §11, R1).
- **`legal-compliance` added** (R8, `340a034`), with its CODEOWNERS line
  under Product, and run once on the slate, the corpus and S2.
- **Also in this PR:** M06's video (`1d18c2d`, `open.md` row 1); every
  `open.md` row placed in `feasibility.md` §6.
- **This PR ran twice.** The first run (`9f2ce07`) was RED on `F4_4`
  alone: p95 14,281 ms, 2.06 times the incumbent's median. The second
  (`0f4b72a`), stated before it was made, was GREEN at 5,830 ms with the
  same counts. The PR changes nothing refagent runs. Both envelopes stay,
  and the bar was not moved (`rulings/pr1.md`, Unsure Q).
- **What is live today, in the repo:** no agent from the template;
  `app_token()` callable with no repository; nothing that reads the
  installation or the key's environment; no `platform-upgrade`, no
  `model-watch`, no retire job; `rollout` with one value; a registry with
  no `retired_at`; one Grafana panel; no plant list for the surfaces.

### PR 2 detail (the measure, 2026-10-02)

- **The reads SPEC/07 §11 owed, then the rulings.** The reads are
  `runs/pr2_reads.md` (`16d9f84`). The human ruled every item of
  `rulings/pr2-security.md` and `rulings/pr2-threshold-owner.md` on
  2026-10-02, "as proposed", before any PR 2 code (`aaa57b5` records
  them): three Apps, each key in its own environment on `main`; the
  installations stay on "all repositories"; a retirement is a stack
  update with no new IAM; the seeded relaxation is one dispatch from
  `main`; the observer stores under `observations/`; three bars; the p95
  bar stays at 2.0; the candidate is Haiku 4.5.
- **S0's fixtures reshaped first, before any reader** (`4d12603`): one
  grant per App, in the ruling's own block's shape. Every reason PR 1
  planted is still asked for.
- **The readers, each marker off in its own commit:** `app_token()`
  refusing a call with no repository (`580be7f`); `grant_errors` for the
  installation and the environment (`3b67946`);
  `scripts/platform_upgrade.py` `diff` (`10cf8eb`); `build.f7_2`,
  `build.f7_3`, `build.panel_verdict_mismatch` through
  `replay_history.verdicts`, `plants.SURFACE_PLANTS` and
  `build.surface_plants` (`95b485c`); `validate`'s panel 2 check
  (`d8f8118`). Nine fixture tests pass; the four run-file markers stay.
- **The envelope:** `upgrade` (F7.0 to F7.5, each read or not, held or
  not, with its viewpoint; the surfaces' plant counts; `taken`, n of 3),
  `F7_0` to `F7_5` required by the gate from `eed43f5`, and row 7's
  reading of `upgrade` with `template` (`READ_THE_UPGRADE`). The three
  bars are `a34bcfa`, with a two-key test on them and on
  `quickstart.max_seconds` (`open.md` row 23).
- **Built for the attempts, none of it run:** the observer
  (`scripts/observe_upgrade.py`, `020553f`), which reads from the
  viewpoint it says; `platform-upgrade.yml`, `model-watch.yml`,
  `observe.yml` and `deploy.yml`'s retire jobs, each keyed job in its own
  environment on `main`'s code with the grant read back first (`84a1eb3`);
  `scripts/retire_agent.py`, `scripts/model_watch.py`, the registry's
  `retire`, the construct's stack without a runtime (`fc8509e`); the
  security account's `bundles/` and `observations/`, and the bootstrap's
  and Grafana's changes (`9fdbfe2`); `docs/developer/upgrade.md`,
  `docs/platform/surfaces.md`, `docs/compliance/map.md`.
- **Inherited from PR 1's review, repaired:** `template.py` reads
  `merged` before the unread return, and holds "refused first" to the
  App's own reasons; `deploy.yml`'s 412 path says whose answer record
  stands; `legal-compliance` run under its own name.
- **Changed from SPEC/07 §6's words, and said so** (SPEC/07 §12;
  `rulings/pr2-security.md` item 13, which the Security seat had not
  ruled on 2026-10-02): `agentkeel-upgrades` is a public App; `model-watch`
  reads Bedrock as a role of its own; the eval role reads a template
  agent's runtime; panel 2 reads a table in the agent account;
  `platform-upgrade` lists agents from GitHub, not the registry; the idle
  trigger for a retirement is not built; "live" for an upgrade since
  replaced is read from its deploy run and its image.
- **Stated before its run, and pushed first:** `runs/pr2_expected.md`.
  Every live reading unread, `taken` 0 of 3, refagent as at M06, GREEN.
- **The seat reviews, read on `a2c5a61...1b376a3`, before the pull
  request was opened:** engineering-cold-reviewer 2 BLOCK and 15
  FINDING, security-reviewer 1 and 7, platform-architect 1 and 5,
  threshold-owner 0 and 6. Three BLOCKs were code and are repaired
  (`b3196d6`): the retire job recorded a retirement whatever its one
  invocation returned; the reader of the grant minted a token on every
  installation, a stranger's included, while three places said it did
  not; `evals.yml` opened envelopes with `jq`. The fourth is the seats':
  both ruling files are drafts and item 13 is not ruled. The readers the
  cold review probed no longer hold on a missing record (`ccb2be8`).
  Each finding and what was done with it:
  `rulings/pr2-engineering.md`, `rulings/pr2-security.md` section 14,
  `rulings/pr2-threshold-owner.md` section 5.
- **Found and not repaired, Product's:** SPEC/07 §2 makes CI's own
  envelope commit a person's edit, so the model upgrade cannot read as
  held and `taken` is at most 2 of 3 as the definition stands (SPEC/07
  §12).
- **Still the human's:** before the merge, the two new Apps, their
  environments and keys, the two ids into the grant block, and each
  stack after reading its `cdk diff` (`runs/pr2_by_hand.md`). After the
  merge, and only then: Administration: write for `agentkeel-platform`,
  then each attempt, stated before and pushed first (SPEC/07 §5.1).
- **What is live after this PR merges and before any grant:** the
  platform check still refuses every head (the `rulesets` token cannot be
  minted until the grant), now saying so; no agent from the template
  exists; nothing has been upgraded, retired or rolled back.

### PR 3 detail (the repair, 2026-10-02)

- **What PR 3 is, ruled by Product on 2026-10-02** (`rulings/pr3.md`).
  The row above says PR 3 "carries every attempt's `observed` entry to
  `main`". That cannot hold. The first deploy of an agent from the
  template failed in the platform's own `deploy.yml`; the deploy runs
  from `main`; so no later attempt can be made until the fix is merged.
  PR 3 is the workflow fix and every repair owed before the next
  attempts, merged once. It carries one `observed` entry, the owner's
  test's. PR 4 carries every other attempt's entry and is the close. A
  fifth PR is a RED close.
- **What that costs, said.** The observer on `main` reads the run files
  as they are on `main`. An attempt recorded only on PR 4's branch is
  read from the anonymous viewpoint alone (SPEC/07 §4). The repositories
  are public, and nothing the attempts read is hidden from an anonymous
  caller but a pull request's `mergeable_state`, which no M07 reading
  rules on. The App's viewpoint will have read the owner's test, the
  dispatch and SPEC/06's S2, whose run files are on `main`.
- **The finding: the owner's test missed its deploy bar, because of the
  platform's own workflow.** Made once, on 2026-10-02, as stated before
  it, on `agentkeel-studio/owner-check` pull request 1. From GitHub's
  record: the empty head `0f155ed` refused by the App at 14:27:33Z on
  the seats and the goldens and nothing else; the fixed head `0c99008`
  passed at 14:35:33Z; merged as `5249dec` at 14:39:32Z; the App passed
  the merge commit at 14:47:11Z. The next deploy run, 37023118799
  (14:54:00Z), signed the agent and failed at `deploy-agent`'s first
  read: `sign-agent` uploaded three paths under two roots, GitHub rooted
  the artifact at their common parent, and `bundle.cosign.json` was not
  where `deploy-agent` reads it. M06 PR 2's code, never reached before,
  because the App refused every head until the grant. Nothing was
  deployed and nothing was written to AWS. Eleven more scheduled deploy
  runs failed the same way by 17:22Z. The bar,
  `upgrade.deploy_max_seconds` (3,600 s), passed at 15:39:32Z.
- **So F7.0 fired, and row 7 is expected to close RED on it.** The
  attempt is not re-made and not restated (Product, `rulings/pr3.md`):
  it was stated before, made once, and what it measured is that the
  platform could not deploy the first agent made from its template
  within the hour. `runs/f7_0_owner_test.yaml` carries its one
  `observed` entry; the observer reads GitHub and AWS, and `build` rules.
  When the fix is on `main` the deploy is expected to complete, hours
  late, and the reading stays a miss. The remaining attempts are still
  made and measured, and `upgrade.taken` is still counted.
- **The fix** (`f5d2f6c`, Security; Engineering for the test):
  `sign-agent` stages the three files under one folder and uploads it
  whole; `tests/test_m07_workflows.py` holds both jobs to that layout.
  It has not run on `main`: the first run that reaches `deploy-agent`
  after the merge is its measurement.
- **SPEC/07 §2 amended, as Product agreed the wording on 2026-10-02**
  (`8725485`), before the reader changed: CI's own envelope commit on an
  `agentkeel` pull request is not a person's edit. It is that commit only
  when its author and committer are both `github-actions[bot]` and every
  file it touches is one of the three envelope files for another commit
  of the same pull request. Until then the model upgrade could not read
  as held. GitHub does not sign that commit, so the login is a name; the
  paths are what bound it, and the text says so.
- **The repairs the PR 2 reviews left open, each in its own commit, each
  before the attempt it bears on.** None has run live.
  - *Who made a commit* (cold review F5; before S1). `build` reads a
    commit as the App's only when GitHub's record shows the App's bot as
    its author, the commit verified, and its committer the bot or GitHub's
    own signer. Anything else reads as not the App's. **No commit by
    `agentkeel-upgrades` has been read yet.** If its first one carries
    another record, S1 reads as a person's edit and that is the finding.
  - *The relaxation's comparisons* (cold review F6; before the
    relaxation). The observer writes records; `build` compares their
    times. "After the restore" is read from the ruleset itself: it equals
    the export in every field GitHub shows, and GitHub's `updated_at` on
    it is after the call.
  - *The observer's keyed job* (security-reviewer 12; before its first
    keyed run). One read-only token per repository the run files on
    `main` name, minted first, and the key let go before anything is
    read; no agent repository's tree packed beside it; an artifact fetched
    from GitHub's storage with no credential.
  - *13h*: the two roles PR 2 added are in both key-policy lists
    (`530bf98`). owner-check's key takes it when its first deploy makes
    the key. refagent's key takes it when the bootstrap stack is deployed
    by hand (`runs/pr2_by_hand.md` B2).
  - *13j*: the grant is `infra/platform_grant.yaml`, and
    `scripts/platform_check.py` is Security's (ADR-0012; CODEOWNERS as
    the seat agreed the diff). It binds from the next pull request: the
    gates read CODEOWNERS from the base.
  - *13l* (before S1): the keyed `open` job reads the template itself,
    refuses a plan made from another commit, and holds each proposed file
    to the template and the guardrail to `main`'s.
  - *13i* (before S2): the retire job holds the retired head's manifest
    to the one at the registry row's commit and refuses any move but
    `rollout`. The cost: a head that failed to deploy before it was
    retired cannot be retired until it is fixed.
  - *`two-key` reads `deprecated_after`* (threshold-owner F1; before
    `model-watch` first runs), after its seeded case
    (`tests/fixtures/m07/two-key-deprecated-after/`, `f9dc98a`; the reader
    `4462d29`). ADR-0009 amendment 1 said this was read from M04 PR 2. It
    was not.
  - *ADR-0011*: SPEC/04 §2's second-run rule has its ADR. No gate reads
    the rule.
- **Left out of PR 3, and why.** 13n, removing the seeded relaxation's
  step: PR 4's, after the attempt it serves. 13k (what the
  `agentkeel-upgrades` key reaches on `agentkeel`) and 13m (where
  `retired.json` is kept): ruled as accepted, nothing to build.
  Threshold-owner F5 on PR 2 (a swap leaves the old model's
  `deprecated_after` in place): moot while refagent's is null; to M08's
  open list at the close. Nothing that had to precede an attempt was left
  out.
- **The seat reviews, read on `3bfd074...936eb17` before the pull request
  was opened:** engineering-cold-reviewer 1 BLOCK, 3 FINDING, 7 NOTE;
  security-reviewer 0, 5, 19; platform-architect 0, 6, 7; threshold-owner
  0, 5, 9. The BLOCK: the two ruling files this diff rests on were not in
  the tree. They are written now, as drafts, and it clears when the seats
  rule them. Repaired in code, each in its own commit: a restore is a
  change after the detection (`44a86eb`); `two-key` on an unquoted
  timestamp (`b5b3b5f`); the observer revokes its tokens and sends one
  only to GitHub's API host; the `open` job says text, not bytes
  (`4fd46f8`). Each finding and what was done:
  `rulings/pr3-engineering.md`, `pr3-security.md`,
  `pr3-threshold-owner.md`.
- **What the amendment costs, said by the cold review (F3).** None of
  PR 3's repairs has run live. Each first runs during an attempt, and a
  fault one of them shows then has no pull request left: PR 4 is the
  close. It would be recorded as a finding.
- **This PR's own run gets no second run.** Its diff touches
  `infra/construct/`, so under ADR-0011 a p95 miss on it is RED
  (`runs/pr3_expected.md`).
- **Measured at `af8835f`** (run 37047341001; envelope
  `af8835fad82709e2385bf4eff97a175e069bf855`): GREEN, mode runtime, p95
  8,223 ms, 25 checks pass, refagent 9/9, 2/2, 2/3, 5/5, plants 7/7.
  `upgrade.F7_0`'s `owner_test` part read and **not held**: "no deploy
  and answer record 13862 s after the merge, over
  upgrade.deploy_max_seconds 3600". `taken` 0 of 3. As stated, but for
  one line: `template.F6_2` read **not held**, where the statement said
  held. SPEC/06's S2 (`owner-check` pull request 2) reads `behind` since
  pull request 1 merged; no new head was pushed to it before that merge,
  which SPEC/07 §5.1 step 2 asked for. The statement was wrong on a fact
  known when it was written (`runs/pr3_expected.md`).
- **`runs/pr2_by_hand.md` corrected** (`96f3cda`): no local profile
  reaches the security account. B1 was deployed on 2026-10-02 by
  `hector.flores` in the console. No put under `bundles/` or
  `observations/` has been made or refused yet.
- **What is live after this PR merges, before any further attempt:** one
  agent repository whose head the App passed and whose deploy has failed
  on every run since (twelve by 17:22Z on 2026-10-02); no agent from the template deployed; nothing upgraded,
  retired or rolled back. The first deploy run after the merge is the
  fix's measurement.

### After PR 3 merged (2026-10-02)

- **The fix held, and the deploy failed one step later.** PR 3 merged as
  `cba3aac`. The first scheduled deploy run after it, 37066321605
  (21:23Z), verified the bytes, pushed the image to `agentkeel/owner-check`
  and created the stack `agentkeel-owner-check`. `CreateAgentRuntime` was
  refused: the execution role may not `CreateAgentRuntimeEndpoint` on
  `runtime/*`, which is how the service names a runtime's DEFAULT
  endpoint before the runtime has an id. M06 PR 2 narrowed that grant to
  the platform's two prefixes; refagent's runtime predates the narrowing
  and no create ran between. The stack rolled back (`ROLLBACK_COMPLETE`)
  and kept its key (`ce2d6f46-8088-4bd3-a57e-2c014278aa34`) and its table
  (`agentkeel-owner-check-rights`), which a redeploy would collide with.
- **Refused again, one check further along.** With
  `CreateAgentRuntimeEndpoint` on `runtime/*` deployed (B2 from `7a9032d`,
  22:49Z) and the stack and table deleted and the key scheduled for
  deletion, run 37074759767 (22:54Z)
  created the stack again and `CreateAgentRuntime` was refused for
  `TagResource` on `runtime/*`: CloudFormation passes its three
  `aws:cloudformation:*` tags in the create, and the service checks them
  against the runtime it has not named yet. The service checks one action
  at a time. The stack rolled back and kept a second key
  (`fcd9e973-0d4b-4828-8f7a-022d9b414c65`, this time with
  `alias/agentkeel-owner-check`) and the table.
- **Deployed on the third create.** With `TagResource` added (B2 from
  `81508ab`, 23:16Z) and the second stack, table and alias deleted and
  its key scheduled for deletion,
  run 37077850271 created the stack (23:31:39Z), the runtime
  `agentkeel_owner_check-G4vMbRB3Dx` answered `g-001` and `g-002` in it
  (2 observations, 0 errors, GREEN), the signed bundle and the answer
  record were put in the security account, each a first put, and the
  registry row `owner-check` was written at 23:37:12Z. That is 32,260 s
  after pull request 1 merged (14:39:32Z) by the session's count, and
  32,264 s as the envelopes read it; `upgrade.deploy_max_seconds`
  is 3,600. The owner's test stays a miss.
- **The second finding under F7.0, and a repair in the close.** The
  repair is two actions on `runtime/*` in the bootstrap stack, a widening
  of IAM, deployed by hand before any ruling (`runs/pr2_by_hand.md` B2,
  twice) and put to Security in `rulings/pr4-security.md`. It is in PR
  4's branch from its first commit, before the close is written.

### Before the timed run (2026-10-03)

- **Product's two restatements** (`open.md` rows 4 and 31; SPEC/07 §12
  "the restatements R9 owes"): the reader's count of S3's records (the
  start, three timed, two listed, the refusal F6.1's) is what SPEC/06's
  "five" and "four" are read against; `milestones/M06/runs/f6_3_quickstart.yaml`'s
  comment says when the attempt is made and which run reads it. The
  run file's `observed` stays null until the attempt.
- **Product ruled: the owner's test's miss on time does not stop the
  timed run.** The path held end to end on run 37077850271. The agent is
  `window-check`.

### The ids pull request (#42, 2026-10-03): the fourth, so the close is a fifth

- **What it carries.** Two lines in `infra/platform_grant.yaml`: the ids
  of `agentkeel-upgrades` (5169860) and `agentkeel-observer` (5169892),
  made by the human on 2026-10-03 UTC (the evening of the 2nd on the
  human's clock) and read back with the permissions the grant block
  names and no more. Nothing else. `make validate` (20 checks) and
  `make ledger` (exit 0) pass on the cell's new form; at the close the
  cell reads `5 / 4`.
- **Why it is a pull request of its own.** Every keyed job reads the
  grant from `main`'s checkout, and each App's key sits in an environment
  that deploys from `main` alone. With `app_id: null` on `main`, the
  upgrade pull requests (S1), the model swap and the retirement cannot
  be opened, and the relaxation waits on S1. The ids were to go to `main`
  in PR 3 (`runs/pr2_by_hand.md` A4); the Apps were made after PR 3
  merged. That is the finding: a by-hand precondition missed its pull
  request, and the branch for PR 4 is the close, which cannot merge
  before the attempts it records.
- **What it costs.** M07's cap is four pull requests. This is the fourth,
  and the close will be the fifth: **a RED close by the cap's rule**
  (CLAUDE.md: "A fifth PR is a RED close with the finding as the
  result"). No cap raise is proposed. Row 7 was already expected to close
  RED on F7.0; the colour does not change, the reasons are two.
- **The alternative, not taken** (Product, 2026-10-03): carry the ids in
  the close and leave S1, the relaxation, the swap and the retirement to
  M08, with F7.1 to F7.5 unread. Also RED, and less measured.
- **#41, the same content, closed unmerged.** Its one commit `ced3b8a`
  was authored as `floresinnovations`: the quickstart's
  `git config --global` lines for the timed run's developer had been run
  on the owner's own Windows account, and the session's checkout
  inherited them. A Security-path change does not reach `main` under an
  account with no write to this repository, and the author could not be
  corrected without overwriting CI's envelope commit on that branch, so
  #41 was closed (its branch and envelope kept) and #42 opened by
  `andaro74`. The same mistake reached `m07-pr4` once (`d79915c`, the
  timed run's record, no PR and no CI commit on top): amended to
  `78aac19` and force-pushed with a lease on that commit alone, on
  Product's word, 2026-10-03. A closed, unmerged pull request is not
  one of the cap's.

### After the ids merged (2026-10-03)

- **The grant's comparison held live.** The first keyed runs with a
  non-null id: `platform-upgrade.yml` (37093799719, then 37094346708,
  which opened the two drafts) and `observe.yml`'s grant step, each
  within its block.
- **The observer could not put, fifteen times.** `agentkeel-observation-put`
  trusted `sub` for `refs/heads/main`; a job in the environment
  `platform-observer` carries the environment's `sub`. Refused at
  `sts:AssumeRoleWithWebIdentity` from 03:56Z to 11:23Z (37094837939 to
  37119509159). The repair is the trust's subject (`infra/security/app.py`),
  Security's, deployed by `hector.flores` (`runs/pr2_by_hand.md`, "B1
  again"); a third repair in the close, also deployed before any ruling.
  This line first said the relaxation waited for it because "only the
  App's viewpoint sees a ruleset's `bypass_actors`": wrong, and
  corrected in SPEC/07 §12. The observer App's Administration: read
  does not show that field either, and the relaxation is read by PR 4's
  own token.

### Close detail (PR 4, the close, the fifth pull request, 2026-10-03)

**Row 7 is RED**, for three reasons (and, by the row's own list of
conditions at the end of this section, four of them fire: the model's
unmerged pull request fires two). F7.0 fired: the first agent from the
template deployed 32,264 s after its merge, against 3,600. `taken` is 2
of 3: the model upgrade was proposed by the platform and not merged,
because its envelope was RED. And M07 used five pull requests against a
cap of four (`rulings/grant-ids.md`); no cap raise is proposed.

**The measurement.** The Measured cell is copied from `make ledger`'s "as
row M07 reads it" line for the envelope for `dee74c3cf4102bfb6d4315faafb161c154618ed9`, written by CI
run 37149475766 and committed by `github-actions[bot]` (`45bac6a`).
`make ledger` exits 0 against it. As numbers: refagent GREEN in `mode:
runtime`, ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5; plants
7/7; `regressed` 0; `never_passed` 1 (`g-014`); 25 checks pass, `F7_0`
to `F7_5` among them (from the seed tests, test-only witnesses); p95
5,740 ms; 43,617 tokens in, 4,780 out. It carries the App-viewpoint
observation `main`'s scheduled observer made (run 37149528340, read
19:53:53Z, `observations/37149528340.json`), which covers what `main`'s
run files name: the dispatch from a branch, the owner's test and S2.
Every attempt of the close is read by the pull request's own token.

| Falsifier | Read | Held | What the envelope says |
|---|---|---|---|
| F7.0 | yes | **no** | `owner_test`: "deployed 32264 s after the merge, over upgrade.deploy_max_seconds 3600". `dispatch` held; `relaxation` held, `detected`; `timed_run` held |
| F7.1 | **unread** | — | "model andaro74/agentkeel#43: unread: the pull request has not merged". The platform's two pull requests held: arrived 139 s and 144 s after the template's push, deployed 518 s and 511 s after their merges. The retirement's pull request arrived 39 s after its dispatch. The swap's arrived 51 s after `model-watch` began |
| F7.2 | yes | yes | 368 s from the merge to `DeleteAgentRuntime` |
| F7.3 | yes | yes | on `window-check`: the runtime's image carries the tree's digest at the revert and not the upgrade's |
| F7.4 | yes | yes | panel 2's 55 rows, none mismatched with the envelopes. Panel 2 was first read live on the close's first run (`84dc913`), with the same result |
| F7.5 | yes | yes | surface plants 2/2 |
| `upgrade.taken` | | | **2 of 3**: platform and retirement; model unread |
| F6.1 (live half, received from M06) | yes | **no** | "the first commit was refused, and not for its planted fault": the App did not refuse it on the seats or the goldens |
| F6.3 (received) | yes | yes | 3,615 s, under 28,800; the registry row and panel 1's row read |
| F6.2 (received) | yes | no | "S2's mergeable_state is 'behind'", as at PR 3 |
| F6.4 | yes | yes | panel 1's rows equal the registry's |

**Three numbers the session wrote by hand differ from the envelope's,
and the envelope is right.** `runs/pr4_expected.md` gives 147 s and 152 s
for the upgrade drafts and 387 s and 510 s for their deploys. The reader
takes GitHub's record of the template's push (eight seconds after the
commit's own time) and the deploy run's completion, one run for both
agents: 139 s and 144 s; 518 s and 511 s. And the owner's test: the
session wrote 32,260 s, here, in SPEC/07 §12 and in the statement for
attempt 1; the envelope reads 32,264 s, as #42's already did.

**The close ran twice.** Its first run (37147871497, on `84dc913`) wrote
an envelope the gate ruled GREEN, with the same readings, and its
`evals` and `checks` jobs failed on one test that still held that the
run files name two attempts (`tests/test_m07_observer.py`). The entries
had been written since `87bbb50`; the session pushed without reading the
suite to its end. Repaired in `db4a94e`; a test is a measured path, so
CI measured again, and the cell is the second run's. p95 was 7,339 ms on
the first and 5,740 ms on the second.

**What each attempt showed** (`runs/pr4_expected.md` has each statement,
pushed before its attempt, and what happened).

- **The owner's test** (PR 3): the App refused the empty head for the
  seats and the goldens alone and passed the fixed one; merged; then
  three faults of the platform's own stood between the merge and a
  runtime (the signed files' path in `deploy.yml`; two IAM actions the
  execution role lacked). 32,264 s.
- **The timed quickstart** (SPEC/06's S3): one hour, once. Its first
  commit was refused for the developer's typo, not for the planted
  fault, so F6.1 reads not held. The owner started the platform's check
  and deploy by hand; the statement did not allow it.
- **The platform upgrade** (S1): opened by `agentkeel-upgrades` in both
  repositories, one verified commit each, `manifest.yaml`'s
  `platform_version` and nothing else, merged by the seats with no
  commit of a person's, deployed. Taken.
- **The relaxation** (S0's third attempt): GitHub accepted the App's
  call. The ruleset required no platform check for 7 min 21 s; the next
  check failed the new head for it; the owner restored it by hand.
  Detected, not refused. No viewpoint the envelope reads from sees
  `bypass_actors`.
- **The model swap** (S3): `model-watch` opened #43 by itself. Haiku 4.5
  regressed `g-004`. RED, not merged, as ruled. Its envelope is on the
  branch `model-watch/m04_cheaper_swap`, which is kept.
- **The rollback**, on the fallback, read on `window-check` and not
  `owner-check` (Product, before it was made: one envelope cannot read a
  rollback and a retirement on one agent). Held.
- **The retirement** (S2): `owner-check`'s runtime deleted 368 s after
  the merge, its one invocation refused, the row kept with `retired_at`.
  Taken. Two network interfaces stayed behind the kept security group.

**Three repairs were deployed by hand during the attempts, before any
ruling**, from this branch: `CreateAgentRuntimeEndpoint`, then
`TagResource`, on `runtime/*`; and the observer's put role trusting the
environment's subject. `rulings/pr4-security.md` item 1 names each and
puts it to Security after the fact. Item 13n (the relaxation's dispatch
input and step) is removed in the close.

**Statements that were wrong.** Attempt 1 expected `template.F6_1` held;
it reads not held. The record of attempt 6 said "as stated, every line";
the owner's dispatches were not only on late schedules, and that
sentence is withdrawn. A sentence said the App's viewpoint sees
`bypass_actors`; it does not. Each is corrected by an appended note, not
by editing the statement.

**Not recorded.** Act 1, the screen capture of the timed run, was not
made. A read-back from the records was filmed afterwards and is filed as
that (`docs/video/README.md`). Act 2 was not recorded. No row is written
for M07's video: it is recorded after the merge (`milestones/M08/open.md`
row 1).

**Row 7's RED conditions, each checked at the close:** F7.0 unread or
fired (**fires**); `taken` under 3 (**fires**: 2 of 3); a trigger that
gets no pull request from the platform, or one that needed a workflow or
a person's edit (no: each of the three triggers got one, opened by the
App, and none was edited; the swap's was not merged for its own
envelope); the retired agent answers or its runtime stands (no: `F7_2`
held); a revert leaves the upgrade's digest live (no: `F7_3` held, on
`window-check`); panel 2 shows GREEN on a RED envelope or the surfaces'
counts differ (no: `F7_4` held over 55 rows; surface plants 2/2); a
seed's test passes for a reason other than its reader (not for the nine
fixture tests, each of which passes by its reader; the four run-file
tests have no reader: they pass because a human-filled entry exists,
each marker came off in the commit that wrote its entry, and none feeds
a check. `uv run pytest tests/test_m07_seeds.py`: 13 passed); PR 4's run cannot read an
attempt (**fires** for the model: an unmerged pull request reads unread,
as ruled at PR 2); `make ledger` stops matching rows 0 to 6 (no: exit
0). And the cap: five pull requests.

**What is carried.** `milestones/M08/open.md`, 62 rows: 26 new at this
close and 36 of M07's `open.md` that M07 did not close, with two more
added after the second review. Every finding and every Unsure item of
#38, #39, #40 and #42 is ruled or has a row there (`rulings/pr4.md`
sections 5 and 6). #44's own Unsure items are listed in `rulings/pr4.md`
section 7, each with its seat and what is taken until the seat rules.
