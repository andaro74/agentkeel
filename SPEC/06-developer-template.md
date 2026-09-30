# SPEC/06 — Developer template

Status: DRAFT · Owner: Product seat · Milestone M06 · Opened at M06 PR 1
(`milestones/M06/rulings/pr1.md`) · Build list: SPEC/00 §8 M06, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M06`),
as cut in §9 and as amended at this PR (§10: the knowledge base to M07) ·
To be reviewed by `product-spec-reviewer` before anything else in PR 1 is
written (`milestones/M06/feasibility.md` §1).

## 1. The claim

**Claim 6.** A developer ships a governed agent from the template in under
one day.

For a director: *a team creates a governed agent from the template, without
touching the safety pipeline* (SPEC/00 §10.3, M06). The table's word
"Marketing" is dropped here: the developer who is timed is the author
(§2), not a marketing team, and the sentence must not say otherwise.

Threats answered (SPEC/00 §3): the negligent developer (forgets a seat,
ships no goldens); the malicious developer (edits a workflow, bypasses a
check). M02 answered both inside this repository, for one human. M06
answers them for a second repository and a second person, who has write
access and nothing more.

**"Ships a governed agent" means all of these, in the new repository, and
nothing less** (each is read, none is taken on the developer's word):

1. The repository was created from the template.
2. Its first pull request was refused for its planted reasons, an
   unassigned seat and no goldens (F6.1), then made green and merged.
3. The merge was deployed by the platform's deploy workflow, not the
   repository's own: a signed bundle, verified, in the construct (claim
   1's controls, reached from a repository that is not this one).
4. The deployed agent answered one of its own goldens in the runtime.
5. The registry holds the agent, and Grafana panel 1 shows it (F6.4).

**"Under one day"** is the elapsed time between two records GitHub keeps,
never the developer's clock (M05's rule for attempt times): the new
repository's `created_at`, and the completion of the deploy run that
satisfies item 3 above. The bar is one working day, **8 hours (28,800 s)**, as
`quickstart.max_seconds` in `thresholds.yaml` with `relaxes: up`
(Threshold Owner, proposed; §11 Q5). Breaks are not subtracted. The
elapsed time is the measured value for claim 6 (SPEC/00 §8 M06, F6.3).

## 2. Words used here

- **The template.** A GitHub template repository that a developer creates
  an agent repository from. It ships refagent as the example (SPEC/00 §8
  M06), a manifest with every seat null, an empty goldens folder, and
  caller workflows whose jobs `uses:` the platform's reusable workflows.
  Where its source lives, and which seat owns that path, is §11 Q1 and Q2.
- **An agent repository.** A repository created from the template. The
  developer has **write** on it and nothing more: no admin, so no edit to
  its rulesets, its settings or its secrets.
- **The platform's workflows.** The workflows that evaluate, sign and
  deploy an agent, owned by Security in this repository. An agent
  repository calls them; it does not contain them.
- **Required workflow.** A workflow the platform requires on an agent
  repository's default branch that the repository's own files cannot
  replace or satisfy. On GitHub this is the `workflows` rule of an
  **organization** ruleset; a repository ruleset can only require a
  status check by name (§3.2). Whether this account can have one is §11
  Q1.
- **Seat assigned.** A manifest seat whose value is a real GitHub login
  (or team) with access to the repository. Null, empty or a login GitHub
  does not answer for is unassigned. Seats to IdP groups is SPEC/00 §6's
  wording; there is no IdP (§11 Q3).
- **Goldens, for an agent repository.** The repository's own golden files,
  in SPEC/00 §6's shape. "Empty" is fewer than the minimum the Data Owner
  rules (proposed: one ordinary and one trap; §11 Q4).
- **The registry.** A DynamoDB table in the agent account holding each
  agent's manifest, flattened, written on merge to an agent repository's
  default branch by the platform's workflow. One row per agent name.
- **Grafana panel 1.** The registry panel: one row per agent, read from the
  registry and from nothing else. Panel 2 is the verdict history (§9 cut
  1).
- **The second developer.** The author, on a fresh Windows user profile
  with nothing installed, and a second GitHub account with write access
  only (ruled by the human, 2026-09-30). No AWS credentials on that
  profile: the developer ships through CI and never holds a platform
  credential. The one-human rule (R1) still holds for seats; the second
  account is a second login, not a second seat holder (§8).
- **Stated before.** An expected reading committed **and pushed** before
  the attempt it states, so that GitHub dates it (`open.md` row 17, ruled
  by Product at M06 open).

## 3. The false state

Claim 6 is false if any of these is on `main`. Each names something a
reader can look at.

**Live today.**

1. **There is no template and no agent repository** (all falsifiers).
   `gh api repos/andaro74/agentkeel --jq .is_template` answers `false`;
   the account owns no organization (`gh api user/orgs` answers `[]`, read
   2026-09-30). Nothing a developer could create an agent from exists.
2. **A required check is a name, and any workflow can answer to it**
   (F6.2). `infra/ruleset/main.json` requires `checks`, `cold-review-ruling`,
   `evals`, `ruling-cited` and `two-key` as contexts, none with an
   `integration_id`, on a repository ruleset. A job named `evals` in a
   workflow the pull request itself adds reports a check of that name.
   Inside this repository `ruling-cited` asks a ruling for the workflow
   path and `validate` asks its hash in `infra/workflows.sha256`, and both
   are files the same pull request can carry (`open.md` row 8: the reader
   is the PR's own code). Expected, not attempted here.
3. **Every seat is unassigned and validate passes** (F6.1).
   `agents/refagent/manifest.yaml` and `agents/ratings-helper/manifest.yaml`
   carry `seats:` with all seven values `null`, and `make validate` is
   green on `main`. No check reads a seat's value.
4. **No agent has goldens of its own** (F6.1). Goldens are one folder,
   `evals/goldens/v1/`, keyed to refagent's questions. Nothing asks an
   agent to bring any.
5. **The deploy role trusts one repository** (item 3 of "ships").
   `infra/bootstrap/app.py` `SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"`,
   with `job_workflow_ref` exact to this repository's `deploy.yml` on
   `main`; `src/bundle/verify.py` accepts that one signing identity. An
   agent repository can neither assume the role nor sign a bundle that
   `verify` accepts. `deploy.yml` packs `agents/refagent` only.
6. **There is no registry and no Grafana** (F6.4). No table, no workspace,
   no panel. Panel 1 cannot show a wrong agent because it does not exist;
   the seed (§5, S4) is the false state a panel can have.
7. **There is no quickstart** (F6.3). `docs/developer/` does not exist.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F6.1 | a green first PR with an unassigned seat (or no goldens) | S1's fixture passed by its reader in a copy of the tree (`checks.F6_1: fail` from the seed test); live: the timed run's first pull request in the agent repository with any required check green while a seat is null or the goldens are empty |
| F6.2 | a repository without the required workflow can merge | S2's attempt merged: a pull request in an agent repository that removes the caller's `uses:` line, or replaces the job with one of the same name that runs no platform code, and is mergeable (GitHub's `mergeable_state` `clean`, or merged) |
| F6.3 | the timed quickstart exceeds one working day | S3's elapsed time, read from GitHub's two records (§1), over `quickstart.max_seconds`, or unread |
| F6.4 | Grafana panel 1 shows an agent the registry does not | S4's fixture passed by its reader (`checks.F6_4: fail`); live: panel 1's data, read through Grafana's API, names an agent with no registry row, or the reading is absent |

**Where each reading comes from** (the M04 and M05 lesson, planned at
open, not found at the close).

- **On every agent envelope, from PR 2's merge: `F6_1` and `F6_4`**, from
  S1's and S4's seed tests: their readers refusing their fixtures in a copy
  of the tree. **Test-only witnesses**, and the ledger says so.
  `CLAIM_6_CHECKS` in the gate is `F6_1`, `F6_4`.
- **F6.2, F6.3 and F6.4's live half are recorded, not gated.** They live
  in an agent repository and in Grafana, which exist only after PR 2
  merges (§5.1). `scripts/observe_template.py` (Engineering) reads each
  from GitHub's and Grafana's records and writes raw observations; `build`
  copies them into an optional envelope field `template` (per seed: made,
  refused, the record read, the elapsed seconds); the gate rules nothing
  on them. **Row 6's Measured cell reads them**, as row 5's read
  `containment`: an attempt that merged, a time over the bar, a panel row
  with no registry row, or anything unread makes row 6's cell RED whatever
  refagent's own verdict. Written here at open; lands at PR 2.
- **A human-written file feeds no reading by itself.** The run file names
  the repository and the pull request; the observer reads GitHub. A name
  it cannot find is unread.

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
none is copied to `evals/history/`.

| Seed | Falsifier | Planted as | Fails today because | Read by (PR 2) |
|---|---|---|---|---|
| S1 first PR: unassigned seat, no goldens | F6.1 | `tests/fixtures/m06/s1-first-pr/`: an agent folder as the template ships it, `manifest.yaml` with all seven seats `null` and an empty `goldens/` | `make validate` on a copy of the tree with it applied is green: no check reads a seat's value or an agent's goldens | two `validate` checks: every seat a real login with access (§11 Q3); an agent's goldens at or over the Data Owner's minimum (§11 Q4). The same checks run in an agent repository through the required workflow |
| S2 `uses:` removed | F6.2 | `runs/f6_2_uses.yaml`: in an agent repository, a pull request that deletes the caller workflow's `uses:` line and adds a job of the same name that echoes success; `observed: null` | the attempt is not made; there is no agent repository. In this repository the same shape is not refused by anything that reads outside the pull request (§3.2) | the organization ruleset's `workflows` rule, requiring the platform's workflow from its own repository at a pinned ref; the observer reads the pull request's `mergeable_state` and the rule suite GitHub recorded |
| S3 the timed quickstart | F6.3 | `runs/f6_3_quickstart.yaml`: the steps of `docs/developer/quickstart.md`, the second developer, the agent's name (fictional, named by Product before the run), `observed: null` | the attempt is not made; there is no template and no quickstart | the observer reads the repository's `created_at` and the deploy run's completion from GitHub, and the answer, the registry row and panel 1 from AWS and Grafana (§1, items 1 to 5) |
| S4 panel 1 shows an agent the registry does not | F6.4 | `tests/fixtures/m06/s4-panel1.json`: panel 1's data frame as Grafana's `/api/ds/query` returns it, naming `ghost-agent`, beside `s4-registry.json`, a registry scan without it | nothing compares a panel with the registry; there is no panel | `scripts/observe_template.py`'s panel reading: panel 1's rows equal to a registry scan, by agent name, both read in the same minute; the dashboard's panel 1 query names the registry as its only source |

### 5.1 When each is measured

**A named P3 exception** (ruled by the human at M06 open, 2026-09-30, as
"if that needs PR 2's merge"). The template, the organization ruleset,
the deploy role's new trust and the registry write all run from `main`:
an agent repository calls the platform's workflows at a ref on `main`,
and the deploy role trusts `main` only (claim 1). A pull request refused
by a required workflow cannot exist before the workflow is on `main`, and
a quickstart cannot be timed against a template that is on a branch. So:

- **PR 2's run, on the PR.** S1 and S4 read by their tests (test-only
  witnesses). The organization, its ruleset and the Grafana workspace are
  made by hand during PR 2 (§11 Q1, Q6), after reading the plan.
- **After PR 2 merges.** The template is published from `main`. **S2 is
  attempted, then S3 is timed, and PR 3's run records both** with S4's
  live half. PR 3 is the repair and that read. If the read misses, row 6
  closes RED at PR 4 with that as the finding; there is no fifth PR.
- **S3 is made once.** SPEC/00 §10.5: timed on a clean account by the
  author at M06 PR 3. A failed step is kept and explained (§10.5,
  recordings), not retaken; a second timing is a second attempt, recorded
  beside the first, and the first is the measured value.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1. Each with one seat and one path; the paths marked
† have no seat today (§11 Q2).

- **The bar** (`thresholds.yaml`, Threshold Owner): `quickstart.max_seconds:
  28800`, `relaxes: up`.
- **The organization and its ruleset** (Security; by hand, exported beside
  `infra/ruleset/main.json` so `validate` compares the live ruleset with
  the export, as M02 does for `main`): the `workflows` rule on every
  agent repository's default branch, `bypass_actors: []`.
- **The platform's reusable workflows** (`.github/workflows/`, Security):
  evals, sign and deploy, called by an agent repository by path and ref.
  Their hashes in `infra/workflows.sha256`.
- **The deploy role's trust and the signing identity** (`infra/bootstrap/`,
  `src/bundle/verify.py`; Security, Engineering): `job_workflow_ref` exact
  to the reusable deploy workflow at `main`, `sub` scoped to the
  organization's repositories; `verify` accepting the reusable workflow as
  the build signer and the caller repository by id.
- **The template** † (§11 Q1, Q2): the example agent, a null-seat manifest,
  an empty goldens folder, the caller workflows, a README that points at
  the quickstart.
- **The two `validate` checks** (`src/validate/`, Engineering): S1's
  reader.
- **The registry** (`infra/`, Security; the write step, Engineering): the
  table, and the step in the reusable deploy workflow that writes the
  flattened manifest on merge.
- **Grafana panel 1** (Security for the workspace, Engineering for the
  dashboard JSON, §11 Q6): the panel's query names the registry only.
- **`scripts/observe_template.py`** (Engineering): S2, S3 and S4's live
  readings; S4's fixture reading.
- **`template`**, `CLAIM_6_CHECKS` (`F6_1`, `F6_4`) and row 6's reading of
  `template` (`src/verdict/`, `src/ledger.py`, Engineering); the step in
  `evals.yml` (Security).
- **The documents** (Product): `docs/developer/quickstart.md`,
  `manifest.md`, `goldens.md`, `edges.md`, `docs/refagent/README.md` and
  `walkthrough.md`. Each says what is not built (SPEC/00 §10.5): no
  judge, no HITL, no knowledge base, no edge in use, no FRAGILE.

## 7. Expected on the plant (row 6)

- **PR 1.** refagent's envelope, gated and recorded as at M05; it says
  nothing about claim 6. `make plants` lists S1 to S4 (seeds, not golden
  plants). `uv run pytest tests/test_m06_seeds.py` shows four expected
  failures. `make validate` passes: nothing reads a seat's value, an
  agent's goldens, a run file or a panel. `make ledger` exits 0 with row 6
  OPEN and its Measured cell empty.
- **PR 2's run, stated before it** (pushed first, §2). S1 and S4 refused
  by their readers for their planted reasons. refagent's envelope
  otherwise as at M05: ordinary 9/9, traps 2/2, guardrail 2/3, red team
  5/5, golden plants 7/7. refagent's own seats assigned in the same PR,
  since S1's reader reads every manifest (a Security field, §11 Q3).
- **PR 3's run, stated before it.** S2 refused by the required workflow,
  the pull request not mergeable; S3's elapsed time under 28,800 s, with
  all five items of §1 read; panel 1's rows equal to the registry's.
- **The row goes RED** if a first pull request is green with a seat
  unassigned or no goldens; if S2's pull request can merge; if S3 is over
  the bar or any of its five items is unread; if panel 1 shows an agent
  the registry does not; if a seed's test passes for a reason other than
  its reader; or if `make ledger` stops matching rows 0 to 5.

## 8. Controls with no seeded case at M06

SPEC/00 §10.5: no document describes these as working.

- **A second person writing a ruling as a seat they do not hold.** Seats
  are one human (R1), and a ruling's `seat:` is a line in a file any
  writer can commit. With a second login, `ruling-cited` and `two-key`
  still read the line, not who wrote it. M06 adds a second login, not a
  second seat holder, and does not close this.
- An agent repository in another organization (SPEC/00 §12: required
  workflows assume one organization; the workflow-hash check is the only
  cross-organization guard).
- An organization owner removing the ruleset: `bypass_actors: []` binds
  the owner at merge, not at the settings page (as M02 for `main`).
- Anything the example agent does beyond refagent's M05 controls: its
  containment is M05's, reached through the construct, and is not
  re-measured here.
- The registry's row for an agent that is retired (M07) or deleted.
- Panel 2 (§9 cut 1), and any panel reading an envelope (M07, F7.4).

## 9. Cut list

In order, if the cap is threatened (SPEC/00 §8 M06). None cuts S1 to S4,
their readers, the template, the organization ruleset, the registry,
panel 1, Acts 1–2 or `docs/refagent/`.

| # | Item | Milestone | Why |
|---|---|---|---|
| 1 | Grafana panel 2 (verdict history) | M07 | SPEC/00 §8 M06's first cut. No M06 falsifier reads it |
| 2 | Act 3 (the reference agent) | M07 | SPEC/00 §8 M06's second cut. Act 3 shows a HITL refusal and a Braintrust trace, both M07's; recorded now it would show neither. **Proposed as taken at open** (§11 Q7) |
| a | FRAGILE, the state and its ruling (`open.md` row 25) | M07, with the judge | **Proposed as taken at open** (§11 Q7). Nothing marks a golden FRAGILE without a judge's score to disagree with; `goldens.md` says it is not built |

Never cut: S1 to S4 and their readers; the template; the required
workflow; the registry and panel 1; Acts 1–2; `docs/refagent/`.

## 10. Not in M06

- **The Bedrock Knowledge Base over the production bucket, and refagent
  retrieving from it**, with the cached-answer seed, F3.5's second half
  and `g-014` counted as a plant: **moved to M07** (ruled by the human at
  M06 open, 2026-09-30; SPEC/00 §8 M06 and M07 amended in this PR). **A
  finding, not a cut: this is its fourth move** (M01 → M03 at M01 open,
  M03 → M04 at M03 open, M04 → M06 at M04 open, M06 → M07 now). It feeds
  no M06 falsifier. The `open.md` rows that ride it (18, 22, 23, 24) move
  with it.
- The `open.md` rows dated M06 that feed no M06 falsifier are placed in
  `feasibility.md` §6, each with a seat and a date; none is dropped.
- Any change to `src/baseline/` (ADR-0002), to refagent's model pin, or
  to a bar other than adding `quickstart.max_seconds`.
- The CLI (`agent evals --local`, `agent upgrade`): M07 (P11).
- An account-per-team landing zone, and SCPs (R3, SPEC/00 §12; `open.md`
  row 48, ruled at M06 open: deferred with the landing zone, re-ruled at
  M08 open).

## 11. Needs a ruling before the seeds

Each names its seat. The seeds are written after these are ruled.

- **Q1 — Where the template and the agent repositories live** (Security,
  Product). SPEC/00 names a template *repo* and required workflows
  (§12: "assume the same GitHub org"). The account has no organization.
  Proposed: a GitHub organization on the Free plan holding the template
  and the agent repositories, public, with an organization ruleset whose
  `workflows` rule requires the platform's workflow. **Unread:** whether
  GitHub Free for organizations offers the `workflows` rule on public
  repositories; Security reads it from GitHub before PR 2. If it does not,
  F6.2 has no reader that a writer cannot answer (§3.2), and that is the
  finding. `agentkeel` itself stays where it is: moving it would change
  the deploy role's `sub` and the signing identity (§3.5).
- **Q2 — The template's source path and its seat** (Product; a SPEC/00 §5
  amendment). If the template's files are kept in this repository (for
  example `template/`), that path has no seat today, and a file no seat
  owns is deleted. If they live only in the template repository, the
  gates of this repository do not read them.
- **Q3 — What a seat is assigned to** (Security). SPEC/00 §6 says IdP
  groups; there is no IdP. Proposed: a GitHub login with access to the
  repository, checked as M02 checks CODEOWNERS logins.
- **Q4 — The goldens minimum** (Data Owner). Proposed: one ordinary and
  one trap, in SPEC/00 §6's shape, before a first pull request can be
  green. Whether those goldens are regression-gated from the first run is
  P7's answer: a golden that has never passed does not gate.
- **Q5 — The bar** (Threshold Owner). 8 hours, wall clock, between two
  GitHub records (§1), breaks not subtracted.
- **Q6 — Where Grafana runs** (Security). Amazon Managed Grafana needs
  IAM Identity Center or SAML; the agent account is the organization's
  management account (`open.md` row 48). A Grafana on a laptop is not
  evidence (P11).
- **Q7 — Cuts 2 and a taken at open** (Product; the Data Owner for a).
