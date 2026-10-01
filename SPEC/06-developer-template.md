# SPEC/06 — Developer template

Status: DRAFT · Owner: Product seat · Milestone M06 · Opened at M06 PR 1
(`milestones/M06/rulings/pr1.md`) · Build list: SPEC/00 §8 M06, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M06`),
as cut in §9 and as amended at this PR (§10) · Reviewed by
`product-spec-reviewer` before anything else in PR 1 was written (3 BLOCK,
16 FINDING, 4 NOTE on `69721b6`; `milestones/M06/feasibility.md` §1) and
revised once on the rulings in §2 of that note, all made by the human on
2026-09-30, BLOCK 1 as option (d) and the rest "as proposed".

## 1. The claim

**Claim 6.** A developer ships a governed agent from the template in under
one day.

For a director: *one developer creates an agent from the template and
ships it in a day, without touching the safety pipeline* (SPEC/00 §10.3
row 06, amended at this PR on finding 13: the developer timed is one
person, the author, and "governed" is not said of controls that have not
fired).

Threats answered (SPEC/00 §3): the negligent developer (forgets a seat,
ships no goldens); the malicious developer (edits a workflow, bypasses a
check). M02 answered both inside this repository, for one human. M06
answers them for a second repository and a second login, which has write
access and nothing more.

**"Ships" means all five of these, in the new repository, and nothing
less.** Each is read from a record; none is taken on the developer's word.

1. **Created.** The organisation owner created the repository from the
   template (finding 4). Its `created_at` starts the clock.
2. **Refused, then merged.** Its first pull request was not mergeable
   while a seat was unassigned or its goldens were under the minimum
   (F6.1), then was made green and merged.
3. **Deployed by the platform.** The merge was deployed by the platform's
   deploy path, not the repository's own: a signed bundle, verified, in
   the construct (claim 1's controls, reached from a repository that is
   not this one).
4. **Answered.** The deployed agent answered one of its own goldens in
   the runtime, recorded in an envelope `build` wrote (§6).
5. **Listed.** The registry holds the agent, and Grafana panel 1 shows it
   (F6.4).

**"Under one day"** is the elapsed time from item 1's record to the
**last** of items 2 to 5's records (finding 8), every time GitHub's or
AWS's, never the developer's clock. The bar is one working day, **28,800 s
wall clock, breaks not subtracted**, as `quickstart.max_seconds` in
`thresholds.yaml` with `relaxes: up` (Threshold Owner). Nothing is
prepared before `created_at` beyond the account set-up recorded in
`feasibility.md` §2 (NOTE 23). The elapsed time is the measured value for
claim 6 (SPEC/00 §8 M06, F6.3).

## 2. Words used here

- **The template.** A GitHub template repository in the organisation.
  It ships refagent as the example (SPEC/00 §8 M06), a manifest with every
  seat null, an empty goldens folder, a README that points at the
  quickstart, and no workflow: the platform check is `agentkeel`'s, run
  from its `main` on a schedule (§6), and nothing in the template asks for it. Its source lives there only; nothing of it sits under a
  path with no seat in `agentkeel` (finding 16).
- **The organisation.** A GitHub organisation on the Free plan, owned by
  `andaro74`, holding the template and the agent repositories, all
  public. Member repository creation is off (finding 4). `agentkeel`
  stays under the personal account: moving it would change the deploy
  role's `sub` and the signing identity (§3.5).
- **An agent repository.** A repository the owner creates from the
  template. The developer has **write** on it and nothing more: no admin,
  so no edit to its ruleset, settings or secrets.
- **The platform check** (BLOCK 1, option (d)). A required status check on
  each agent repository's default branch whose ruleset names an
  `integration_id`: a GitHub App the platform owns. GitHub accepts that
  check only from that App ("The optional integration ID that this status
  check must originate from", REST reference for repository rules). The
  check is posted by a workflow in `agentkeel` that runs from `main` on a
  schedule, evaluates the pull request's head with the platform's code,
  and holds the App's key (Security; §6). A job of the same name in the pull request's
  own workflow files runs as the GitHub Actions app and does not satisfy
  it. If `agentkeel`'s run never reaches the pull request, no check
  arrives and the pull request stays blocked. GitHub documents the `workflows` rule, the
  first-party form of this, for Enterprise Cloud only (read 2026-09-30),
  so M06 does not use it.
- **Seat assigned** (NOTE 20, Q3). A manifest seat whose value is a real
  GitHub login that **administers** the repository, checked as M02 checks
  CODEOWNERS logins. Null, empty, a string that is not a login, or a login
  with write alone is unassigned (amended at PR 2, security-reviewer F11:
  "with access" let the write developer fill every seat). SPEC/00 R1 and §6
  are amended at this PR from "IdP groups". Under R1 every seat is
  `andaro74`; the second developer's login holds none, and the check now
  says so.
- **Goldens, for an agent repository** (finding 7, Q4). The repository's
  own golden files in SPEC/00 §6's shape: at least **one ordinary and one
  trap**. For an agent that is not refagent, `table_row` and `clause_id`
  name a row and a clause in that agent's own data, carried in its
  repository; the Data Owner rules the files at PR 2. Fewer is "under the
  minimum". A golden that has never passed does not gate (P7).
- **The registry.** A DynamoDB table in the agent account holding each
  agent's manifest, flattened, written by the platform's deploy path on a
  merge to an agent repository's default branch. One row per agent name.
- **Grafana panel 1.** The registry panel: one row per agent, whose query
  names the registry and nothing else. Panel 2 is the verdict history (§9
  cut 1).
- **The second developer.** The author, on a fresh Windows user profile,
  as `floresinnovations` (id 336113686), a GitHub account with write on
  the agent repository only (ruled 2026-09-30; `feasibility.md` §2, NOTE
  23). No AWS credentials on that profile: the developer ships through CI
  and never holds a platform credential.
- **The template works** (finding 9). Read from PR 2's own run: the
  template's example agent deployed from a test repository the owner
  creates and owns, through the platform check and the deploy path. That
  run is `andaro74`'s, is not a quickstart run and is not timed. Any run of
  the quickstart by the second developer is an attempt and is recorded.
- **Stated before.** An expected reading committed **and pushed** before
  the attempt it states, so that GitHub dates it (`open.md` row 17, ruled
  by Product at M06 open).

## 3. The false state

Claim 6 is false if any of these is on `main`. Each names something a
reader can look at.

**Live today.**

1. **There is no template and no agent repository** (all falsifiers).
   `gh api repos/andaro74/agentkeel --jq .is_template` answers `false`;
   the account owns no organisation (`gh api user/orgs` answers `[]`, read
   2026-09-30). Nothing a developer could create an agent from exists.
2. **A required check is a name, and any workflow can answer to it**
   (F6.2). `infra/ruleset/main.json` requires `checks`, `cold-review-ruling`,
   `evals`, `ruling-cited` and `two-key` as contexts, none with an
   `integration_id`. A job named `evals` in a workflow the pull request
   itself adds reports a check of that name. Inside this repository
   `ruling-cited` asks a ruling for the workflow path and `validate` asks
   its hash in `infra/workflows.sha256`, and both are files the same pull
   request can carry (`open.md` row 8: the reader is the PR's own code).
   Expected, not attempted here.
3. **Every seat is unassigned and validate passes** (F6.1).
   `agents/refagent/manifest.yaml` and `agents/ratings-helper/manifest.yaml`
   carry `seats:` with all seven values `null`, and `make validate` is
   green on `main`. No check reads a seat's value, though SPEC/00 R1 lists
   "seats assigned to real groups" among `validate`'s checks from M01
   (NOTE 20): the promise was never built.
4. **No agent has goldens of its own** (F6.1). Goldens are one folder,
   `evals/goldens/v1/`, keyed to refagent's questions and to
   `data/rights_table.json` and `data/clause_index.json`. Nothing asks an
   agent to bring any.
5. **The platform trusts one repository** (item 3 of "ships").
   `infra/bootstrap/app.py` `SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"`:
   the deploy role trusts it with `job_workflow_ref` exact to this
   repository's `deploy.yml` on `main`, and the eval role trusts its
   `pull_request` and `main` subjects. `src/bundle/verify.py` accepts one
   signing identity and one repository id. `deploy.yml` packs
   `agents/refagent` only. An agent repository can assume neither role nor
   sign a bundle that `verify` accepts.
6. **There is no registry and no Grafana** (F6.4). No table, no workspace,
   no panel. Panel 1 cannot show a wrong agent because it does not exist;
   the seed (§5, S4) is the false state a panel can have.
7. **There is no quickstart** (F6.3). `docs/developer/` does not exist.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F6.1 | a first pull request is mergeable with an unassigned seat or goldens under the minimum (finding 6) | S1a's or S1b's fixture passed by its reader in a copy of the tree (`checks.F6_1: fail` from the seed tests); live: the timed run's first pull request with `mergeable_state` `clean` (or merged) while a seat is null or the goldens are under the minimum, read from GitHub by the observer and ruled on by `build` |
| F6.2 | a pull request in an agent repository merges without the platform's check having run on it and passed (BLOCK 2) | S2's pull request merged, or the platform's App passing its head; S2 carries a stand-in job of the check's name and one null seat, so the App, which reaches every pull request (R2), refuses it (amended at PR 2) |
| F6.3 | the timed quickstart exceeds one working day | S3's elapsed time (§1) over `quickstart.max_seconds`, or any of its five records unread |
| F6.4 | Grafana panel 1 shows an agent the registry does not | S4's fixture passed by its reader (`checks.F6_4: fail`); live: panel 1's rows, read through Grafana's API, name an agent with no registry row, or either list is unread |

**Where each reading comes from** (the M04 and M05 lesson, planned at
open, not found at the close).

- **On every agent envelope, from PR 2's merge: `F6_1` and `F6_4`**, from
  S1a's, S1b's and S4's seed tests: their readers refusing their fixtures
  in a copy of the tree. **Test-only witnesses**, and the ledger says so.
  `CLAIM_6_CHECKS` in the gate is `F6_1`, `F6_4`.
- **F6.1's and F6.4's live halves, F6.2 and F6.3 are recorded, not
  gated.** They live in an agent repository, in the organisation and in
  Grafana, which exist only after PR 2 merges (§5.1).
  `scripts/observe_template.py` (Engineering) writes raw observations
  only (BLOCK 3): the first pull request's required checks and
  `mergeable_state`; S2's pull request's check runs, with each run's App,
  and its merge state; the five records' times; panel 1's rows as
  Grafana's API returns them and a registry scan, each with the time it
  was read. `build` rules on them, compares panel 1's rows with the
  registry's by agent name, and writes an optional envelope field
  `template`; the gate rules nothing on it. **Row 6's Measured cell reads
  it**, as row 5's read `containment`: a first pull request mergeable
  while it should not be, an S2 merge, a time over the bar, a panel row
  with no registry row, or anything unread makes row 6's cell RED
  whatever refagent's own verdict. Written here at open; lands at PR 2.
- **A human-written file feeds no reading by itself.** The run file names
  the repository and the pull requests; the observer reads GitHub,
  Grafana and AWS. A name it cannot find is unread.

**P5.** Observers write raw observations; `verdict.build` writes the
checks and `template`; the gate reads the envelope and the ledger reads
the gate. `tests/test_p5_disagree.py` gains a case for each new check.

## 5. The seeded cases

Planted at PR 1, one commit per seed, each before any reader. Code seeds
are fixtures under `tests/fixtures/m06/`; attempt seeds are run files
under `milestones/M06/runs/`, each the attempt to make with
`observed: null`. Each has its test in `tests/test_m06_seeds.py`, marked
`xfail(strict=True, raises=...)` naming the one exception its planted
reason raises, run once with `--runxfail` so the message is read;
preconditions raise `SeedBroken`. Each is named in
`tests/fixtures/README.md` and in `src/verdict/plants.py` as `SEEDS_M06`;
none is copied to `evals/history/`. Five seeds (finding 10 split S1).

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S1a an unassigned seat | F6.1 | `tests/fixtures/m06/s1a-unassigned-seat/`: an agent folder as the template ships it, `manifest.yaml` with all seven seats `null`, and one ordinary and one trap golden | `make validate` over a copy of the tree with it applied is green: no check reads a seat's value | a `validate` check: every seat a real GitHub login with access (§2). The same check runs in an agent repository under the platform check |
| S1b goldens under the minimum | F6.1 | `tests/fixtures/m06/s1b-no-goldens/`: the same agent folder with every seat `andaro74` and an empty `goldens/` | `make validate` over a copy of the tree with it applied is green: no check reads an agent's goldens | a `validate` check: an agent's goldens at or over one ordinary and one trap (§2) |
| S2 a stand-in for the platform check | F6.2 | `runs/f6_2_standin.yaml`: in an agent repository, a pull request whose own workflow file adds a job with the platform check's name that echoes success, and deletes the caller's request to `agentkeel`; `observed: null` | the attempt is not made; there is no agent repository. In this repository the same shape is answered by the pull request's own files (§3.2) | the agent repository's ruleset: the platform check required with the App's `integration_id`; the observer reads the pull request's check runs, each with its App, and its `mergeable_state` |
| S3 the timed quickstart | F6.1, F6.3 | `runs/f6_3_quickstart.yaml`: the steps of `docs/developer/quickstart.md`; the second developer (`floresinnovations`, id 336113686, set up as `feasibility.md` §2 records); the agent's name, fictional, named by Product before the run; `observed: null` | the attempt is not made; there is no template and no quickstart | the observer reads the five records of §1 from GitHub, AWS and Grafana, and the first pull request's checks and merge state (F6.1's live half) |
| S4 panel 1 shows an agent the registry does not | F6.4 | `tests/fixtures/m06/s4-panel1/`: `dashboard.json`, a dashboard whose panel 1 query names a second source beside the registry; `frame.json`, panel 1's rows as Grafana's `/api/ds/query` returns them, naming `ghost-agent`; `registry.json`, a registry scan without it | nothing reads a panel's query or compares a panel with the registry; there is no panel | `validate` refuses a panel 1 query that names anything but the registry (finding 11); `build` compares panel 1's rows with the registry's by agent name (BLOCK 3) |

### 5.1 When each is measured

**A named P3 exception** (ruled by the human at M06 open, 2026-09-30:
"if that needs PR 2's merge, name it a P3 exception at open"). The
platform check posts from `agentkeel`'s `main`, the deploy role trusts
`main` only (claim 1), and the template is published from what PR 2
merges. A pull request refused by the platform check cannot exist before
the check is on `main`, and a quickstart cannot be timed against a
template that is on a branch. So:

- **PR 2's run, on the PR.** S1a, S1b and S4 read by their tests
  (test-only witnesses). During PR 2 the owner makes the organisation,
  the App and the Grafana workspace by hand (Security, after reading the
  plan).
- **After PR 2 merges, PR 3 repairs** (amended at PR 3). The owner's test
  repository showed the platform check's ruleset reader refusing every
  agent repository: GitHub adds two fields to an organisation repository's
  pull request rule that PR 2's export lacked. The check runs from `main`,
  so nothing can pass until PR 3 merges. **PR 3 is that repair and cannot
  be skipped.**
- **After PR 3 merges.** The owner reads that the template works (§2),
  from a test repository. Then **S2 is attempted, then S3 is timed, and
  PR 4's run records both** with F6.1's and S4's live halves. **PR 4 is
  that read and the close.** If the read misses, row 6 closes RED at PR 4
  with that as the finding; there is no fifth PR.
- **S3 is made once.** SPEC/00 §10.5: timed on a clean account by the
  author after M06 PR 3 merges (amended at PR 3). A failed step is kept and explained, not retaken; a
  second timing is a second attempt, recorded beside the first, and the
  first is the measured value. A repository deleted during an attempt is
  recorded, never replaced by a later one's `created_at` (finding 4).
- **Amended at M06 PR 4** (`milestones/M06/rulings/pr4.md`): row 6 closed
  RED. S2 was made and read by PR 4's run; the owner's test missed at step
  2 and S3 was not attempted. S3, its timing and Act 1 move to M07 with
  the App's repair (SPEC/00 §8 M06 and §10.5 as amended;
  `milestones/M07/open.md` rows 2, 4, 31). The bullets above stand as
  M06's plan.
- **Act 1 is recorded during S3** (finding 14): the unedited screen
  capture of the timed run is SPEC/00 §10.2's Act 1. Act 2 is recorded at
  the close, against M02's pull requests.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1. Each with one seat and one path (finding 16). The
lists below are written from the reads §11 owed, ruled by the human on
2026-09-30 (`milestones/M06/feasibility.md` §8, R1 to R9).

- **The bar** (`thresholds.yaml`, Threshold Owner): `quickstart.max_seconds:
  28800`, `relaxes: up`.
- **The organisation, the App and each agent repository's ruleset**
  (Security; by hand): member repository creation off; the App owned by
  the organisation, installed on all its repositories, with checks write,
  pull requests read, contents read and administration read. A free
  organisation has no organisation rulesets, so each agent repository
  carries a repository ruleset equal to `infra/ruleset/agent.json`: the
  platform check required with the App's `integration_id`, branches up to
  date before merge, a pull request required, `bypass_actors: []`. The
  owner applies it from the export when creating the repository.
- **The platform check** (`.github/workflows/platform-check.yml`,
  Security; R2). Scheduled on `agentkeel`'s `main`, every 5 minutes, and
  by hand. One job, holding no secret, lists the organisation's open pull
  requests, checks out each unchecked head **as data** beside a checkout
  of `main`, and runs `python -m src.validate.agent` over it; a second
  job, in the environment `platform-app` (deployment branch `main` only),
  holds the App's key and posts the check on the head it was given. The
  check also fails when the repository's live ruleset is not the export.
  No request comes from an agent repository. Its hash in
  `infra/workflows.sha256`.
- **The checks in an agent repository** (`src/validate/agent.py`,
  Engineering; R6). The agent folder is placed at `agents/<name>/` in a
  checkout of `main`, as the seed tests place it, and these run: manifest
  schema; edges two-sided, no cycle, ceilings within bounds;
  `deprecated_after`; **seats assigned** (S1a's reader); **an agent's
  goldens** (S1b's reader: shape, at least one ordinary and one trap, each
  citing its own `data/`); **the agent's name** (`refagent`, a name held by
  another agent in the tree, or one that is not lower-case letters, digits
  and hyphens is refused; a name held in the registry by another
  repository is refused at deploy, item 9 below). Not run, because they
  read files only `agentkeel` has: golden front matter and citations over
  `evals/goldens/v1/`, ruling front matter, the workflow hashes, cdk-nag,
  CODEOWNERS, `relaxes:`, golden ids against `origin/main`, computed
  semver, the live `main` ruleset, plant controls, golden/corpus overlap
  and the corpus.
- **The per-agent platform changes** (Security; finding 5, R3, R4). Each is
  automatic from `main` once PR 2 builds it, or a step of the timed run:

  | # | Change | How |
  |---|---|---|
  | 1 | The repository's ruleset | Timed: the owner applies `infra/ruleset/agent.post.json`, and the live ruleset must equal `infra/ruleset/agent.json`, GitHub's form of it (amended at PR 3); the platform check fails while it differs |
  | 2 | The App on the repository; the developer's write | Automatic (installed on all repositories); timed (the owner, seconds) |
  | 3 | The deploy role's and the eval role's trust; `verify`'s identity | **None.** `agentkeel`'s `deploy.yml` on `main` deploys every agent (R3); `verify`'s identity and repository id move to `infra/platform_identity.json` (Security) and do not widen |
  | 4 | The image repository | Automatic: `agentkeel/<name>`, made on the first push from an ECR repository creation template for the namespace `agentkeel` (immutable tags, AES-256; a template matches a namespace, not a name prefix, so not `agentkeel-<name>`), and `ecr:CreateRepository` on `repository/agentkeel/*` for the deploy role |
  | 5 | The agent's key `alias/agentkeel-<name>` | Automatic: made in the agent's own stack, its policy denying every platform role the actions R4 names (refagent's key stays in the bootstrap) |
  | 6 | The guardrail | None at M06: an agent from the template pins the platform's guardrail, refagent's, by id and version (Rule Owner); a guardrail per agent is M07's |
  | 7 | The rights table, inference profile and runtime | Automatic (the construct). An agent other than refagent gets the runtime name `agentkeel_<name>`; the deploy role may call `runtime/agentkeel_*` and refagent's; the table marker parameter is `/agentkeel/marker/<name>/rights-table-digest` |
  | 8 | The audit bucket's policy (`open.md` row 29) | Automatic: one statement for agent roles under `/agentkeel/agents/` other than refagent's, on `agents/${aws:PrincipalTag/agentkeel:agent}/*`; refagent's statements stay by exact ARN |
  | 9 | The registry row | Automatic: the deploy writes it, refusing a name already held by another repository |
  | 10 | Spend | None: the account's Bedrock budget stops the eval role only; a budget per agent is M07's (`open.md` row 34) |

- **The registry** (`infra/bootstrap/`, Security): the DynamoDB table
  `agentkeel-registry`, key `name`, written by the deploy with the
  repository, its id, the commit deployed and the time.
- **Grafana** (Security; R1): `infra/grafana/` (a stack: Athena's DynamoDB
  connector, its spill bucket, the workgroup, the workspace's role) and
  `infra/grafana/panel1.json`, whose panel 1 query names the registry and
  nothing else. The workspace is made by hand.
- **Three `validate` checks in `agentkeel`** (`src/validate/`, Engineering):
  S1a's and S1b's readers over every `agents/*/`, and S4's query reader over
  `infra/grafana/panel1.json` (R8).
- **`scripts/observe_template.py`** (Engineering): raw observations only.
- **`template`**, `CLAIM_6_CHECKS` (`F6_1`, `F6_4`), `build`'s comparisons
  and row 6's reading of `template` (`src/verdict/`, `src/ledger.py`,
  Engineering); the step in `evals.yml` (Security). **Item 4's envelope**
  (R7): `build` writes it in the deploy run, keyed to the agent
  repository's commit, put once under `envelopes/agents/<name>/<commit>.json`
  in the security account's bucket; the observer records its key and
  sha256.
- **The seats** (the manifests' `seats`, Security): refagent's and
  ratings-helper's, both assigned in PR 2, since S1a's reader reads every
  manifest (finding 12).
- **The template** (the template repository, made by hand from files PR 2
  hands the owner; Engineering for the example agent, Product for its
  README). Nothing of it is under a path in `agentkeel` with no seat. It
  ships refagent as the example agent at the repository's root, every seat
  null, an empty `goldens/`, and no workflow.
- **The documents** (Product): `docs/developer/quickstart.md`,
  `manifest.md`, `goldens.md`, `edges.md` (§9 cut 3), `docs/refagent/README.md`
  and `walkthrough.md`. Each says what is not built (SPEC/00 §10.5): no
  judge, no HITL, no knowledge base, no edge in use, no FRAGILE.

## 7. Expected on the plant (row 6)

- **PR 1.** refagent's envelope, gated and recorded as at M05; it says
  nothing about claim 6. `make plants` lists S1a, S1b, S2, S3 and S4
  (seeds, not golden plants). `uv run pytest tests/test_m06_seeds.py`
  shows five expected failures. `make validate` passes: nothing reads a
  seat's value, an agent's goldens, a run file or a panel. `make ledger`
  exits 0 with row 6 OPEN and its Measured cell empty.
- **PR 2's run, stated before it** (pushed first, §2). S1a, S1b and S4
  refused by their readers for their planted reasons. Both manifests'
  seats assigned. refagent's envelope otherwise as at M05: ordinary 9/9,
  traps 2/2, guardrail 2/3, red team 5/5, golden plants 7/7.
- **PR 4's run, stated before it** (PR 3's, until amended at PR 3). The timed run's first pull request not
  mergeable while a seat was null or the goldens were under the minimum;
  S2's pull request not mergeable, the stand-in's check run a success on
  its head and none from the App (amended at PR 2: S2 carries one null
  seat, since the App reaches it too); S3's elapsed time under 28,800 s with all five records read;
  panel 1's rows equal to the registry's.
- **The row goes RED** if a first pull request is mergeable with a seat
  unassigned or goldens under the minimum; if S2's pull request can merge;
  if S3 is over the bar or any of its five records is unread; if panel 1
  shows an agent the registry does not; if a seed's test passes for a
  reason other than its reader; or if `make ledger` stops matching rows 0
  to 5.

## 8. Controls with no seeded case at M06

SPEC/00 §10.5: no document describes these as working.

- **A second person writing a ruling as a seat they do not hold.** A
  ruling's `seat:` is a line in a file any writer can commit, and
  `ruling-cited` and `two-key` read the line, not who wrote it. M06 adds a
  second login, not a second seat holder, and does not close this.
- **`agentkeel`'s own required checks** (finding 17; `open.md` row 8).
  The App check closes row 8 for agent repositories only. In `agentkeel`
  a job of a required check's name, in a pull request's own workflow
  file, still answers to it; and a same-repository pull request there can
  change the workflow that holds the App's key. Carried to M07.
- **What `deploy.yml` on `main` now deploys** (finding 18, as R3 changed
  it; platform-architect F7 on PR 2). The deploy and eval roles' trust and
  `verify`'s identity did not widen. What widened: `deploy.yml` on `main`
  builds and deploys the content of any organisation repository whose
  default-branch head the App passed, and its own role puts under
  `envelopes/agents/`. No seed attempts a repository outside the
  organisation, or a head the App did not pass.
- **The App key's protection is a setting nothing reads back**
  (security-reviewer F12 on PR 2). The environment `platform-app`, its
  deployment branch (`main` only) and the key's being in that environment
  rather than at repository level are GitHub settings; `validate` reads
  none of them. An App result is also final for its commit: a head passed
  before `main`'s rules changed stays passed.
- **The new per-agent controls** (platform-architect F8 on PR 2): an agent
  from the template's key policy (its own role only; no platform role
  alters it), the tag-keyed audit prefix, the deploy role's
  `runtime/agentkeel_*`, the image repository template's tag immutability,
  the connector reading the registry alone, and the platform's Dockerfile
  in place of the agent's. M05's seeds read refagent's exact-ARN
  statements and refagent's bootstrap key, not these.
- **What an agent repository's own pull requests are not asked**
  (feasibility §8, R6): no ruling file, no `ruling-cited`, no `two-key` on a
  retired golden, no golden-id or semver check against its default branch.
  The seats are named in its manifest; nothing proves the seat holder read
  a change. M07, with the CLI.
- **One guardrail for every agent** (R4 row 6): an agent from the template
  pins refagent's, whose denied topics are about title availability; an
  agent moved to another subject is checked against them. And the agent's
  own code decides what the input topics see: it builds the request, and
  `topics_apply_to: input` checks only what it puts in `guardContent`
  (rule-owner on PR 2). No golden in an agent repository may be a
  guardrail or red-team case, so nothing checks the guardrail on a template
  agent's runtime. A guardrail per agent, and a check outside the agent's
  code, are M07's.
- **The registry's name binding** (R4 row 9) is written before a stack is
  touched; no seed attempts a second repository claiming a name.
- **What nothing checks in an agent repository's goldens** (data-owner F5
  on PR 2): their answers gate nothing (they are run after merge and
  recorded); a change to `expected` needs no ruling; nothing reads that
  `answer_fields` follow from the cited row, that a trap is a trap, that
  the titles are fictional, or a golden/corpus overlap (the agent has no
  corpus at M06). The shipped tool reads refagent's row fields and clause
  ids only.
- **The agent account is shared with other projects** (feasibility §8;
  platform-architect F6 on PR 2). Their runtimes and stacks sit beside the
  platform's, and an admin of the account reaches all of them (`open.md`
  row 48). It is also the organisation's management account, which reaches
  the security account through Organizations and holds the Identity Center
  instance that can give a permission set there, so R3's second account is
  not independent of the first. Any principal in it that may create or tag
  a role under `/agentkeel/agents/` can write under a template agent's
  audit prefix, which is bound by tag where refagent's is bound by ARN.
  Nothing reserves the `agentkeel_` runtime prefix. The Grafana workspace
  role trusts any workspace in the account until the workspace exists.
- An agent repository in another organisation (SPEC/00 §12).
- An organisation owner removing a ruleset or the App: `bypass_actors: []`
  binds the owner at merge, not at the settings page (as M02 for `main`).
- Anything the example agent does beyond refagent's M05 controls: its
  containment is M05's, reached through the construct, and is not
  re-measured here.
- **Panel 1's columns live in the account's shared Glue database**
  (`default`.`agentkeel-registry`, added at PR 2 when the connector, with no
  row to infer from, knew only `name`). Any principal in the account that
  may write Glue tables can change what panel 1 shows until the next
  deploy of `infra/grafana/`. F6.4 compares panel 1 with a direct registry
  scan, so such an edit reads as fired or unread, not held; no seeded case
  attempts it (security-reviewer N2 on the post-review delta).
- A private agent repository is refused by the App and not deployed, but
  no seeded case has made one (security-reviewer F1 on the delta).
- The registry's row for an agent that is retired (M07) or deleted.
- Panel 2 (§9 cut 1), and any panel reading an envelope (M07, F7.4).

## 9. Cut list

In order, if the cap is threatened. None cuts S1a to S4, their readers,
the template, the platform check, the registry, panel 1, Acts 1–2 or
`docs/refagent/`.

| # | Item | Milestone | Why |
|---|---|---|---|
| 1 | Grafana panel 2 (verdict history) | M07 | SPEC/00 §8 M06's first cut. No M06 falsifier reads it |
| 2 | Act 3 (the reference agent) | M07 | SPEC/00 §8 M06's second cut. Act 3 shows a HITL refusal and a Braintrust trace, both M07's |
| 3 | `docs/developer/manifest.md`, `goldens.md`, `edges.md` | M07 | Added at open (finding 14) to relieve PR 2. The quickstart stays: F6.3 times it |

## 10. Not in M06

Amendments to SPEC/00 §8 M06 made in this PR (`rulings/pr1.md`):

- **The Bedrock Knowledge Base over the production bucket, and refagent
  retrieving from it**, with the cached-answer seed, F3.5's second half
  and `g-014` counted as a plant: **moved to M07** (ruled by the human at
  M06 open, 2026-09-30). **A finding, not a cut: this is its fourth
  move** (M01 → M03 at M01 open, M03 → M04 at M03 open, M04 → M06 at M04
  open, M06 → M07 now; NOTE 21). It feeds no M06 falsifier. `open.md`
  rows 11, 18, 21, 22, 23 and 24 move with it.
- **FRAGILE, the state and its ruling** (`open.md` row 25): **moved to
  M07**, with the judge (finding 15). Nothing marks a golden FRAGILE
  without a judge's score to disagree with.

Also not in M06:

- The `open.md` rows dated M06 that feed no M06 falsifier are placed in
  `feasibility.md` §6, each with a seat and a date; none is dropped.
- Any change to `src/baseline/` (ADR-0002), to refagent's model pin, or
  to a bar other than adding `quickstart.max_seconds`.
- The CLI (`agent evals --local`, `agent upgrade`): M07 (P11).
- An account-per-team landing zone, and SCPs (R3, SPEC/00 §12; `open.md`
  row 48, ruled at M06 open: deferred with the landing zone, re-ruled at
  M08 open).

## 11. Read before PR 2

Read by their seats on 2026-09-30, read-only, and ruled by the human the
same day (`milestones/M06/feasibility.md` §8): Grafana (R1: Managed Grafana
over Athena; Identity Center was already active in the agent account), the
trigger (R2: a schedule on `main`, nothing to forge), the deploy (R3:
`agentkeel`'s own, trust unchanged), the per-agent list (R4, §6), the
golden files (R5), the checks in an agent repository (R6, §6) and item 4's
envelope (R7, §6).
