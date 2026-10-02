# M07 — Upgrade, retire, surfaces

## Ledger row

Written at M07 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 7 |
|---|---|
| Claim | An agent takes a platform, model or retirement upgrade without a workflow edit |
| Falsifiers | F7.0 no agent from the template exists to upgrade: the owner's test's fixed head is refused, or not merged, deployed, answering and listed; the timed run's agent the same; or the platform check dispatched from a branch reaches the App's key (added at M07 PR 1). F7.1 an upgrade requires a manual edit: no pull request the platform opened arrives, or a workflow or a person's commit was needed to merge it; a ruling file is not a person's edit (reworded at M07 PR 1). F7.2 a retired agent still answers. F7.3 a rollback leaves the new digest live. F7.4 a Grafana panel shows GREEN where the envelope says RED (read through Grafana's query API, as F6.4; not Playwright). F7.5 `plants_expected ≠ plants_fired` for the surfaces. |
| Seeded commit | `c870bca` (S0 the template's repair read by CI: the owner's test, the App token's bounds); `ef3d88a` (S1 a platform bump opens a draft pull request); `3872c13` (S2 a retired agent's target is gone); `ea53ef4`, its run file made to parse in `a46c98f` (S3 a `model-watch` pull request merged and rolled back); `e814efe` (S4 panel 2 forced to show GREEN on a RED envelope, two tests, one per reader); `f36adee` (S5 a surface plant goes silent); the fixtures given their held cases and three more uncovered ones in `4240d9e`, on the PR's own review, each its own commit before any reader (SPEC/07 §5). S0 to S3 are each a fixture and a run file with `observed: null`; S4 and S5 are fixtures. SPEC/06's S3 (`b4eb959`, the timed quickstart) is received, not re-planted |
| Expected gate output | PR 1: refagent's envelope as at M06; it says nothing about claim 7. `make plants` lists S0 to S5 (seeded cases, not golden plants); `tests/test_m07_seeds.py` shows 13 expected failures, and `tests/test_m06_seeds.py` still 1 (S3's). PR 2, on the PR: the nine fixture tests pass, each by its reader, and the four run-file tests stay expected failures; from PR 2's merge the gate requires `F7_0` to `F7_5` on every agent envelope, **from the seed tests alone: test-only witnesses**. The live readings are **recorded in the envelope's `upgrade` and read by this row's cell, with `template`, not gated** (SPEC/07 §4): the observer writes raw observations with the viewpoint it read from, and `build` rules on them. **A named P3 exception (SPEC/07 §5.1):** the platform check, the deploy, `platform-upgrade`, `model-watch` and the retire job run from `agentkeel`'s `main`, and the App's grant is made by hand after PR 2 merges, when `main` no longer mints a token with no repository. The platform check dispatched from a branch is attempted first, before any grant, and must be read as refused. Then, after PR 2's merge, each stated before and pushed: the grant made and read back; SPEC/06's S2 read on a new head; the owner's test, steps 2 to 4; SPEC/06's S3 timed once by `floresinnovations`; the template re-made and S1's pull requests; the App's token asked to relax a ruleset; `model-watch`'s swap to Haiku 4.5 and its rollback (independent of the others; its two pull requests on `main` are outside the cap); `owner-check` retired, last. PR 3 is the repair and carries every attempt's `observed` entry to `main`; PR 4 is the close. **The cell cites PR 4's run's envelope**, which carries the App-viewpoint observation `main`'s scheduled observer made, named, beside its own anonymous one. Stated at open: the owner's test's new head refused on the seats and the goldens and nothing else, its fixed head merged, deployed within 3,600 s, answering and listed; S1's draft pull request from the App within 4,500 s, platform-owned files only, no person's edit, major or minor as read; S2 retired within 3,600 s of its pull request's merge, its one invocation refused; a revert leaving the tree's digest live. Haiku 4.5's envelope is **not stated**: it has never been run. If it is RED the swap is not merged, F7.3 is read on `owner-check`'s platform upgrade reverted, and `upgrade.taken` stays under 3. The measured value is `upgrade.taken`, n of 3. RED if F7.0 is unread or fired; if `taken` is under 3; if a trigger gets no pull request from the platform, or one that needed a workflow or a person's edit; if the retired agent answers or its runtime stands; if a revert leaves the upgrade's digest live; if panel 2 shows GREEN on a RED envelope or the surfaces' counts differ; if a seed's test passes but by its reader; if PR 4's run cannot read an attempt; or if `make ledger` stops matching rows 0 to 6 |
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

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
