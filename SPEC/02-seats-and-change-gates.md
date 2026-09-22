# SPEC/02 — Seats and change gates

Status: DRAFT · Owner: Product seat · Milestone M02 · Opened at M02 PR 1
(`milestones/M02/rulings/pr1.md`) · Build list: SPEC/00 §8 M02, which is
the ruling for this milestone's build paths (`SPEC/00-overview.md#8-M02`)
· Reviewed by `product-spec-reviewer` before the rest of PR 1 was
written (1 BLOCK, 8 FINDING, 6 NOTE; `milestones/M02/feasibility.md`
§1) and revised once on the rulings in §2 of that note.

## 1. The claim

**Claim 2.** Seat-owned files change only with a ruling; relaxations need
two keys.

For a director: *a rule, a test, or a threshold changes only when the
person who owns it says so, and loosening one needs two owners*
(SPEC/00 §10.3, M02).

Threats answered (SPEC/00 §3): the negligent developer who loosens a bar
to go green; the malicious developer who bypasses a check; the insider
who silently changes what is checked.

**What "says so" means here.** Every seat is one person (R1), and no
gate waits for a human approval. So "the owner says so" is not a review
button. It is a ruling file under `milestones/**` whose `seat:` is the
seat that owns the path, whose `authorises:` names the path, and whose
`pr:` is the PR that changed it. The gate reads that file, not a person.
What the claim measures is therefore this: **no seat-owned path on
`main` changed without a file that names the seat, the path and the PR,
and no relaxation changed without two such files from two distinct
seats.** At M02 one person holds every seat, so "two owners" in the
plain sentence is two files from two seats, written by one person. The
explainer's "For the business user" says so in those words
(`product-spec-reviewer` finding 5); no page says a person approved
anything.

**What "on `main`" means for a ruling** (`milestones/M02/open.md` row 1,
Security; ADR-0008, Product, amending SPEC/00 §5 and R9). `ruling-cited`
and `two-key` read the PR's merge ref: a ruling the PR carries counts,
as it has for `cold-review-ruling` since M00. The ruling is on `main` at
the merge commit, which is the first moment anything in the PR is. The
alternative, a ruling PR before every PR, doubles the count against a
cap of four. A ruling in the merge ref is more than a permission slip
only because of what the gate checks about it: its `seat:` must be the
CODEOWNERS owner of every path it authorises; its `authorises:` must
cover every seat-owned path in the diff; a relaxation needs a second
file with a different `seat:` and the same `pr:`; and the file lives
under `milestones/**`, so it stays on `main`, keyed by PR number. That
is the whole control. It does not stop one person from writing both
files, and nothing here pretends otherwise.

## 2. Words used here

- **Seat-owned path.** A path in the SPEC/00 §5 table, made
  machine-readable at M02 as `.github/CODEOWNERS`, which §5's Security
  row names from ADR-0003 amendment 2 (that ADR's last). Every file on
  `main` matches one owner line; `validate` fails on a file that matches
  none or two.
- **Ruling.** A file `milestones/*/rulings/<slug>.md` with the front
  matter SPEC/00 §6 names. `SPEC/00-overview.md#8-MNN` is the ruling for
  milestone NN's build paths; a PR cites it by that anchor in a ruling
  file's `evidence:`. An ADR is evidence, never a ruling on its own.
- **Covers.** A ruling covers a changed path when `seat:` is that path's
  CODEOWNERS owner, one of its `authorises:` globs matches the path, and
  `pr:` is this PR's number.
- **Relaxation.** Any of: a bar in `thresholds.yaml` moved in the
  direction its own `relaxes:` field names; a golden's `retired` set from
  null; a golden's `expected` changed on an id that has ever passed in
  `evals/history/`; a file under `rules/**` or `agents/*/rules/**`
  deleted, or a guardrail version moved down; a manifest's
  `memory.retention` shortened; a commit under `evals/history/**` whose
  author is not `github-actions[bot]`. The list is closed; adding to it
  is a SPEC/00 §5 amendment.
- **Two keys.** Two ruling files, each with one `seat:`, the two seats
  distinct, both with this PR's `pr:`. The file of the seat that owns the
  path covers it; the other names the path in its body (M01 PR 1, ruling
  B). **Engineering's file counts as a key like any other seat's**
  (open.md row 21, Product): R1 makes any two seats one person, so
  excluding Engineering would buy nothing and would make the seat with
  the most files the one that can never say yes. M01 PR 1's two keys on
  `thresholds.yaml`, Threshold Owner and Engineering, stand.
- **Edge.** `may_call` on the caller and `may_be_called_by` on the
  callee, each naming the other. One side alone is one-sided.
- **Bypass.** Merging a PR to `main` while a required status check is
  not green, or changing the `main` ruleset so that someone could
  (`bypass_actors` not `[]`, a required check removed, enforcement off).

## 3. The false state

Claim 2 is false if any of these is on `main`. Each names something a
reader can look at with `git log` and the GitHub API.

1. A merge commit whose diff raises `cost_cap.tokens_per_run` in
   `thresholds.yaml`, and fewer than two rulings on `main` from two
   distinct seats, each with `pr:` equal to that PR, cover
   `thresholds.yaml`: none, one, or two from the same seat.
2. A merge commit whose diff changes a golden's `expected` so that an
   answer it was written to catch now passes, with no Data Owner ruling
   covering it.
3. A merge commit whose diff puts `ratings-helper` in refagent's
   `may_call` while no manifest on `main` says `ratings-helper` may be
   called by refagent.
4. A PR whose required check is red, merged by the repository owner; or
   a `main` ruleset on GitHub that differs from `infra/ruleset/main.json`
   while nothing in the repo is RED.
5. A merge commit in which a golden file disappears and a file with the
   same content and a new `id` appears, with no `retired:` set on the old
   id.

At PR 1 none of the five is on `main` and nothing in the repo would stop
any of them: `cold-review-ruling` checks that a ruling file with the PR's
number exists and reads no path; `validate` reads no diff and no
ruleset; `evals` reads goldens as they are, not as they were.

## 4. Falsifiers

| Id | Fires when | What it looks like in the repo |
|---|---|---|
| F2.1 | any of the five seeded changes merges | the merge commit on `main`; `checks.F2_1: fail` in an agent envelope under `evals/history/`; a seed's run file under `milestones/M02/runs/` recording anything but the expected refusal |
| F2.2 | the three doors are not reproducible from the PR record | `milestones/M02/runs/f2_2_three_doors.yaml` names three PRs; the GitHub API's record of them does not show, respectively, a merge refused by a required check that names the seed's path; a merge with two rulings from two seats in the merge commit; and the owner's merge refused with `bypass_actors` `[]` at that time and `validate` RED on the ruleset that would have allowed it (Door 3 is two gates, SPEC/00 §8 M02); `checks.F2_2: fail` |

**Where each check comes from.** `F2_1` is read from two sources and
passes only if both do. First, at PR 2, the junit result of the tests in
`tests/test_m02_seeds.py`: S1 (both forms), S2, S3 and S5 each apply
their seed to a copy of the tree and ask `src/gates/` and `validate` to
refuse it; S4's test reads `f2_1_bypass.yaml` and the ruleset export.
Second, at PR 3, the GitHub API's record of the seed PRs and of S4's
attempts, looked up by `scripts/observe_pr.py` from the run files the
human wrote, as `scripts/observe_attempt.py` reads CloudTrail at M01.
`F2_2` is read the same way from `f2_2_three_doors.yaml`, at PR 3. A
human-written file feeds no check by itself; the check is the CI lookup
of the PR number.

**P5.** The gate that refuses a PR is a workflow (`gates.yml`, Security)
running `src/gates/` (Engineering); it never writes an envelope.
`verdict.build` writes `checks.F2_1` and `checks.F2_2` from the junit
file and the observation files, exactly as it writes `checks.F1_1` at
M01. `verdict.gate` reads the envelope and nothing else, and
`tests/test_p5_disagree.py` holds that the two can disagree.

## 5. The seeded cases

SPEC/00 §8 M02 lists five seeds. Each is a change to a seat-owned path
with too few rulings, or a bypass. Each is planted at PR 1 as a diff
under `tests/fixtures/m02/`, one commit per seed, with its test in
`tests/test_m02_seeds.py`, before any code that reads it; each test is
`xfail(strict=True)` until its reader lands.

| Seed | Falsifier | Planted as | Read by (PR 2 unless said) |
|---|---|---|---|
| S1 threshold relaxed, one key | F2.1 | `tests/fixtures/m02/s1-one-key.patch`: `cost_cap.tokens_per_run` 150000 → 300000 plus **one** ruling file, `seat: Threshold Owner`, covering `thresholds.yaml`. `ruling-cited` is satisfied; only `two-key` can refuse it (BLOCK 1). Second form, `s1-two-files-one-seat.patch`: the same change with two ruling files, both Threshold Owner. Two files are not two seats | `two-key` |
| S2 golden edited to green | F2.1 | `s2-golden-greened.patch`: `g-010`'s `expected.answer_fields.available` false → true and `constraints` emptied, so the trap rewards the answer it was written to catch; no ruling | `ruling-cited` (Data Owner path, no ruling) and `two-key` (`expected` changed on an id with a pass in history) |
| S3 one-sided edge | F2.1 | `s3-one-sided-edge.patch`: `may_call: [ratings-helper@v1]` in refagent's manifest; no `agents/ratings-helper/` exists to say it may be called; no ruling | `validate`, edges two-sided; `ruling-cited` |
| S4 owner bypasses a red check | F2.1, F2.2 Door 3 | `milestones/M02/runs/f2_1_bypass.yaml`: two attempts by the human as repository owner, `observed: null` until made (§5.1). Its test, `test_s4_the_owner_was_refused`, reads the run file and requires `bypass_actors: []` in `infra/ruleset/main.json` | the `main` ruleset (`bypass_actors: []`, required checks); `validate`'s live-vs-export diff; `scripts/observe_pr.py` at PR 3 |
| S5 golden id renamed | F2.1 | `s5-golden-renamed.patch`: `g-005.yaml` deleted, `g-099.yaml` added with the same content and `id: g-099`; `retired` untouched; no ruling. Passes today's `validate` | `validate`, "an id on `main` never disappears; it is retired"; `ruling-cited` |

Each patch is a unified diff against the tree at PR 1's base, applied
with `git apply`. If a base file changes before PR 2 so that a patch no
longer applies, PR 2's first commit re-plants that seed, still before
its reader (as S2's signature was re-planted at M01 PR 2). `g-099` is
burned: no golden ever gets that id (`tests/fixtures/README.md`). The
seed ruling files inside S1's patches carry `pr: 0`; the human sets the
seed PR's number when opening it, and the run file records the edit.

### 5.1 When each is measured

- **PR 2's run, on the PR.** S1 (both forms), S2, S3 and S5 are applied
  to a copy of the tree by their tests and refused by `src/gates/` and
  `validate`. That is the gate logic measured, on the PR that lands it,
  as M01 PR 2 measured `verify` on S1 and S2. It is not yet a PR refused.
- **Door 2 is PR 2's own merge.** PR 2 retires `g-012` (Finding F0.1)
  with two ruling files, Data Owner and Threshold Owner, and adds `g-021`
  (`sequel_no_inherit`; open.md rows 3 and 4, moved from PR 1 to PR 2 by
  Product). `two-key` runs on PR 2's merge ref and reads that retirement;
  its green check run and the merge commit with both files are Door 2's
  record. The gate reads its own PR here, as M01 PR 2's `verify` read the
  bundle that PR signed; the seeds in the same run are what show the
  gate can also refuse.
- **After PR 2 merges, before PR 3's first CI run**, the human, as
  Security, makes `ruling-cited` and `two-key` required checks on the
  `main` ruleset and exports it (`infra/ruleset/main.json`, in PR 3).
  Then the human opens the seed PRs S1 (both forms), S2, S3 and S5 from
  `main`, each expected to show its check red naming the seed's path,
  and the merge button refused. Their numbers go in
  `milestones/M02/runs/f2_1_seed_prs.yaml`. They are opened from `main`
  and not from PR 2's head because a PR off PR 2's head would carry PR
  2's diff too, and `ruling-cited` would be red on PR 2's paths whether
  or not it saw the seed (finding 4).
- **S4, in the same window.** Attempt 1: `gh pr merge --admin` on S1's
  PR. Expected: refused by GitHub, since `bypass_actors` is `[]`; the
  response is kept as the human's own output (row 17), and
  `observe_pr.py` looks for the refused evaluation in the rule-suites
  API (`GET /repos/{owner}/{repo}/rulesets/rule-suites`, by actor, ref
  and time). Whether that API records a refused merge is read at the
  attempt, not assumed: if it does not, Door 3 rests on the human's
  output and the PR's unmerged state alone, `feasibility.md` says so,
  and Security's Unsure item names it (finding 3). Attempt 2: the human
  adds their own account to `bypass_actors` on the live ruleset, runs
  `validate` on any branch, expects RED on the live-vs-export diff, and
  removes it again; the ruleset's `updated_at` before and after are
  recorded. Both go in `f2_1_bypass.yaml`.
- **PR 3's run** reads the seed PRs, S4's attempts and the three doors
  from the API and writes `checks.F2_1`'s second half and `checks.F2_2`.
  This is the part of claim 2 first measured after PR 2 merges, named
  here as a P3 exception as ADR-0007 named M01's: a PR refused by a gate
  on `main` cannot exist before the gate is on `main`. PR 3 is the
  repair PR or the close PR; either way its run reads them, with
  machinery from PR 2. If PR 3 is the close and its run reads
  anything but the expected refusals, row 2 is RED.
- **Never**: none of the five merges. A seed PR is closed unmerged after
  its refusal is recorded; the branch is kept.

These are seeded cases for claim 2, not plants under SPEC/00 §5's plant
rule; they never enter `plants_expected`. `make plants` lists them with
their reader's path and whether it exists yet.

## 6. The code that reads the answer (PR 2)

None of it is in PR 1.

- **`.github/CODEOWNERS`** (Security): the SPEC/00 §5 table as owner
  lines, one GitHub login per seat. At M02 every seat's login is the same
  one person (R1), and `validate` checks that each login in CODEOWNERS
  and in every manifest's `seats:` is a real login and that the two
  agree. GitHub's own code-owner review is **not** required
  (`require_code_owner_review` stays false): R1 forbids a gate that
  waits for a human. CODEOWNERS is routing; the gates below are the
  enforcement.
- **`src/gates/ruling_cited.py`** (Engineering), run by `gates.yml`
  (Security) on every PR as the required check `ruling-cited`: for every
  path in `git diff base...merge-ref`, the CODEOWNERS owner; for every
  seat-owned path, a ruling file in the merge ref that covers it. Paths
  under `evals/history/**` by `github-actions[bot]` are exempt. Exit 1
  with every uncovered path listed, never the first; the list is in the
  job log, which `observe_pr.py` reads. A PR that edits a workflow and
  `infra/workflows.sha256` together now needs a Security ruling covering
  both (open.md row 7, first half).
- **`src/gates/two_key.py`**, the required check `two-key`: detects each
  relaxation in §2 against the base ref and the history, and requires
  two covering rulings from distinct seats. `thresholds.yaml` gains a
  `relaxes: up|down` field per bar (Threshold Owner), read here instead
  of a comment.
- **`validate` grows** by: CODEOWNERS complete and single-owner over the
  tree; logins real and agreeing with manifests; edges two-sided across
  `agents/*/manifest.yaml`; no cycle in the call graph; ceilings within
  `thresholds.yaml` bounds; live `main` ruleset equal to
  `infra/ruleset/main.json` with `bypass_actors: []` (open.md row 5); a
  golden id present on `main` is present in the PR or has `retired:` set
  (S5). The ledger header gains a row for M02 PR 2 listing exactly what
  landed, under the rows for M01 PR 2 and `m01` that PR 1 adds (note 12).
- **Computed semver** (Tool Owner, row 20): `validate` computes the
  version each tool schema and each edge would need from the diff
  against `main` (schema or edge change = major) and fails when the
  manifest asserts a smaller one.
- **`agents/ratings-helper/manifest.yaml`** (Tool Owner for the edge,
  Threshold Owner for the model fields, Engineering for the rest): a
  manifest-only stub with `may_be_called_by: [refagent]`, so that the
  two-sided edge exists and S3 has a side to be missing. SPEC/00 §8 M01
  and CLAUDE.md list it under M01; M01 cut it at open (SPEC/01 §10) and
  did not build it. Its code, the 12-row table and budget headers are M07
  (§10).
- **`scripts/observe_pr.py`** (Engineering): given a run file naming PR
  numbers and attempts, asks the GitHub API what happened to each
  (check-run conclusions on the head sha, the job log's uncovered-path
  list, the merge state, rule-suite evaluations) and writes the raw
  observation `build` reads for `F2_1` and `F2_2`.
- **`docs/platform/overview.md`** (Product, SPEC/00 §10.1 lists it at
  M02), by hand: `docs-writer` is M03.

## 7. Expected on the plant (row 2)

- **PR 1.** refagent's envelope in runner mode, gated and recorded as at
  M01; it says nothing about claim 2. `make plants` lists S1–S5, each
  with no reader in the tree. `uv run pytest tests/test_m02_seeds.py`
  shows six expected failures (S1 has two). `make validate` passes on
  the seeds as committed: a patch file is not a golden, a threshold or a
  manifest, and `f2_1_bypass.yaml` is not a ruling.
- **PR 2's run on the PR.** S1 (both forms), S2, S3 and S5 each refused
  with the planted reason among the reasons; S4's test fails on
  `observed: null`, which is the row RED until the attempts are made;
  `checks.F2_1` therefore fails on PR 2's own run and passes only at PR
  3. `two-key` green on PR 2 with the two files for `g-012`. No count of
  refagent's passes changes; the checks decide the row.
- **PR 3's run.** `checks.F2_1` pass on both halves; `checks.F2_2` pass:
  three PR numbers, three records.
- **The row goes RED** if any seed PR's required check is green, if
  `gh pr merge --admin` succeeds, if `validate` stays green with
  `bypass_actors` non-empty, or if PR 3's run reads anything else.

## 8. Controls with no seeded case at M02

SPEC/00 §10.5: no document describes these as working.

- a relaxation of `rules/**` or a guardrail version (no `rules/` exists
  before M03);
- `memory.retention` shortened (no memory before M07);
- a human commit under `evals/history/**` (the case exists in the gate;
  nobody plants a hand-written envelope on `main`);
- the cycle and ceiling checks (one edge, no cycle possible);
- computed semver on a real schema change (M07's upgrade is the case);
- the workflow-hash check's second half (open.md row 7): what a
  workflow runs in `Makefile`, `src/` and `scripts/` is still not hashed.

## 9. Cut list

In order. None cuts a seeded case or a seed's reader.

| # | Item | Milestone if cut |
|---|---|---|
| 1 | Ceilings within bounds | M06 (the template's second agent) |
| 2 | Cycle check on the call graph | M06 |
| 3 | Computed semver | M07 (`docs/developer/upgrade.md` lists it) |
| 4 | Seats → real logins checked against the API | M06 |
| 5 | `docs/platform/overview.md` | M03, with `docs-writer` |

Never cut: CODEOWNERS; `ruling-cited`; `two-key`; edges two-sided (S3
reads it); the id-disappears check (S5); `bypass_actors: []` in
`validate` (S4); `scripts/observe_pr.py` (S4's reader, and F2.2's); the
five seeds; Door 2.

## 10. Not in M02

- `ratings-helper` as running code with its table and budget headers:
  M07 (surfaces), with chain identity.
- GitHub code-owner review as a gate: never (R1).
- A CloudFormation Hook or SCP binding an author who installs no checks:
  M05 (row 23).
- Hashing what a workflow runs, not only its text: M05, with the
  write-once audit.
