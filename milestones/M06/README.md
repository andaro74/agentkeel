# M06 — Developer template

## Ledger row

Written at M06 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 6 |
|---|---|
| Claim | A developer ships a governed agent from the template in under one day |
| Falsifiers | F6.1 a first pull request in an agent repository is mergeable while a seat is unassigned (not a real GitHub login with access) or its goldens are under the minimum (one ordinary, one trap). F6.2 a pull request in an agent repository merges without the platform's check (a required status check bound to the platform's GitHub App by `integration_id`) having run on it and passed. F6.3 the timed quickstart, from the agent repository's `created_at` to the last of its four records (the first pull request refused then merged, the platform's deploy, the agent's answer to one of its own goldens, the registry and panel 1 listing it), exceeds `quickstart.max_seconds` (28,800 s wall clock, from PR 2), or a record is unread (the measured value for claim 6). F6.4 Grafana panel 1 shows an agent the registry does not. |
| Seeded commit | `672fc1d` (S1a an unassigned seat); `1a576f4` (S1b goldens under the minimum); `0f3b977` (S2 a stand-in for the platform check); `b4eb959` (S3 the timed quickstart); `06c485a` (S4 panel 1 against the registry, two tests, one per reader), each its own commit before any reader (SPEC/06 §5). S2 and S3 are attempts to make, `observed: null`; S1a, S1b and S4 are fixtures |
| Expected gate output | PR 1: refagent's envelope as at M05; it says nothing about claim 6. `make plants` lists S1a, S1b, S2, S3 and S4 (seeded cases, not golden plants); `tests/test_m06_seeds.py` shows 6 expected failures. PR 2, on the PR: S1a, S1b and S4 refused by their readers for their planted reasons (`validate` refuses the null seats, the missing goldens and a panel 1 query with a second source; `build.panel_not_in_registry` finds `ghost-agent`); both manifests' seats assigned. From PR 2's merge the gate requires `F6_1` and `F6_4` on every agent envelope, **from the seed tests alone: test-only witnesses**. F6.1's and F6.4's live halves, F6.2 and F6.3 are **recorded in the envelope's `template` and read by this row's cell, not gated** (SPEC/06 §4, ruled at open): the observer writes raw observations only and `build` rules on them. **A named P3 exception (SPEC/06 §5.1):** the platform check posts from `agentkeel`'s `main`, the deploy role trusts `main` only and the template is published from what PR 2 merges, so after PR 2's merge the owner reads that the template works from a test repository, S2 is attempted, S3 is timed once by the second developer (`floresinnovations`, write only), and **PR 3's run records them**; PR 3 is that read and cannot be skipped, and the repair. Stated before, and pushed before each attempt: the first pull request not mergeable on its planted reasons; S2 not mergeable, the stand-in's check run a success on its head and none from the App (amended at PR 2: the App reaches S2 too, so S2 carries one null seat); S3 under 28,800 s with all four records read; panel 1's rows equal to the registry's. refagent otherwise as at M05: ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5, golden plants 7/7. RED if a first pull request is mergeable with a seat unassigned or goldens under the minimum; if S2 can merge; if S3 is over the bar or a record is unread; if panel 1 shows an agent the registry does not; if a seed's test passes but by its reader; if PR 3's run cannot read S2 and S3; or if `make ledger` stops matching rows 0 to 5 |
| Measured | — |
| PRs used / cap | 2 / 4 |
| State | OPEN |

### Open detail (PR 1, 2026-09-30)

- **Opened through `/open-milestone`.** SPEC/06 was written first
  (`69721b6`) and `product-spec-reviewer` run on it (3 BLOCK, 16 FINDING,
  4 NOTE), pasted verbatim in `feasibility.md` §1. The human ruled every
  item before any seed, BLOCK 1 as option (d) after two reads of GitHub's
  documentation and the rest "as proposed", and SPEC/06 was revised once
  on the rulings (`b0aefa1`, before the first seed `672fc1d`).
- **BLOCK 1 changed what "required workflow" means here.** GitHub
  documents the organisation ruleset's `workflows` rule for Enterprise
  Cloud only (read 2026-09-30); the account has no organisation, and the
  human ruled against a paid plan. The platform check is a required status
  check bound to a GitHub App the platform owns (`integration_id`), posted
  from `agentkeel`'s `main`: a job of the same name in a pull request's own
  workflow does not satisfy it (BLOCK 2's attack, S2). The documentation,
  not an attempt: PR 2 reads the first ruleset back.
- **M01's, M03's, M04's and M05's P3 exception again.** The platform check,
  the deploy role and the template all run from `main`, so S2 and S3 are
  made after PR 2 merges and read by PR 3's run. PR 3 is that read and
  cannot be skipped (NOTE 22).
- **M05's lesson, planned at open.** The live readings are recorded in the
  envelope's `template` and read by row 6's cell; they gate no pull
  request. `F6_1` and `F6_4` on every envelope come from the seed tests, as
  test-only witnesses. The observer writes raw lists; `build` compares
  (BLOCK 3).
- **Planted** in five commits, one per seed, `672fc1d` to `06c485a`, each
  with its test in `tests/test_m06_seeds.py`, before any code that reads
  them: 6 expected failures (S4 has one test per reader), each run once
  with `--runxfail` and its message read (`feasibility.md` §3). S1 was split
  in two so a reader that catches one fault cannot pass the other (finding
  10).
- **What is live today, in the repo:** no template and no organisation;
  required checks that are names any workflow can answer to; every seat in
  both manifests null with `validate` green; one folder of goldens, all
  refagent's; a deploy role, an eval role and a `verify` that trust one
  repository; no registry, no Grafana, no quickstart.
- **The second developer** is the author as `floresinnovations` (id
  336113686), write only, on a fresh Windows profile with no AWS
  credentials; set up and ruled at open (`feasibility.md` §2, NOTE 23), with
  `andaro74` on GitHub Pro so that the author holds one free account.
- **Moved at open** by SPEC/00 amendment, not cut: the knowledge base, with
  the cached-answer seed, F3.5's second half and `g-014`, to M07, **its
  fourth move, a finding**; FRAGILE to M07. SPEC/00 R1, §6 (seats to GitHub
  logins), §8 M06 and M07 and §10.3 row 06 are amended.
- **Also in this PR:** M05's video (`open.md` row 1, `eb5dcec`); rows 2, 3,
  17 and 48 ruled at open (`runs/security_account.md`, `rulings/pr1.md`);
  every `open.md` row placed in `feasibility.md` §6.

### PR 2 detail (the measure, 2026-09-30)

- **The reads SPEC/06 §11 owed, then the rulings** (`feasibility.md` §8,
  R1 to R9), before the first commit (`86eb01a`): Managed Grafana over
  Athena (Identity Center was already on in the agent account); the
  platform check from `agentkeel`'s `main` on a schedule, with nothing to
  forge; `agentkeel`'s own deploy for every agent, so no trust widened.
- **The readers, each marker off in its own commit:** S1a (`4d961cd`,
  after the seats in `1dc781b`), S1b (`95e3824`), S4's query (`2a9e793`,
  after `panel1.json` in `9eff4bc`), S4's comparison (`6435f5c`). Cold
  review F4's cross-assertions land with S1a's and S1b's; F2's reader
  field with S4's. `F6_1` and `F6_4` from the seed tests, required from
  `c2a15d0`; `template` and row 6's reading of it in the same commit.
- **Built for PR 3's read:** the observer, `build answer`, the platform
  check (`platform-check.yml`, `src/validate/agent.py`,
  `scripts/platform_check.py`), the agent deploy (`deploy.yml`'s three new
  jobs, `infra/construct/agent.Dockerfile`, `scripts/registry.py`), the
  bootstrap's registry and image template, the security account's answer
  role and tag-keyed prefix, the Grafana stack, the template's source
  (`scripts/make_template.py`), the quickstart and `docs/refagent/`.
- **Changed from the plan, and said so:** S2 carries one null seat (the
  App reaches it too); a seat needs admin; template images are
  `agentkeel/<name>`; F6.3 times GitHub's and AWS's records only, and reads
  the registry row and panel 1's row untimed; cut 3 taken.
- **Reviewed:** five seat reports and two cold reads, every BLOCK and
  FINDING repaired in this PR or named in SPEC/06 §8 (`rulings/pr2-*.md`).
- **Still the human's, during this PR, before the merge:** the
  organisation, the App and its key, `platform_identity.json` and
  `agent.json` filled with them, the `platform-app` environment, the
  bootstrap, security and Grafana deploys after reading each `cdk diff`,
  the workspace and its data source, and the repository variables. After
  the merge: the template from `scripts/make_template.py`, the owner's
  test repository, then S2, then S3, read by PR 3's run.
