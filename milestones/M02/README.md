# M02 — Seats and change gates

## Ledger row

Written at M02 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 2 |
|---|---|
| Claim | Seat-owned files change only with a ruling; relaxations need two keys |
| Falsifiers | F2.1 any of the five seeded changes merges: a threshold relaxed with one key or with two files from one seat, a golden edited to green a build, an edge declared on one side, the owner merging past a red required check, a golden id renamed. F2.2 the three doors (Door 1 blocked by the gate, Door 2 merged with two keys, Door 3 blocked by two gates) are not reproducible from the PR record. |
| Seeded commit | `6ff333a` (S1, both forms); `74a38be` (S2); `d8fbdb1` (S3); `9eb539c` (S4, the attempt to make, `observed: null`); `479abb9` (S5), each its own commit (SPEC/02 §5) |
| Expected gate output | PR 1: refagent's envelope in runner mode, gated and recorded as at M01; it says nothing about claim 2. `make plants` lists S1–S5 with no reader in the tree; `tests/test_m02_seeds.py` shows 6 expected failures. PR 2, on the PR: S1 (both forms), S2, S3 and S5 refused by `src/gates/` and `validate` in a copy of the tree, each with its planted reason; **Amended at PR 2 (Product, `rulings/pr2.md`; SPEC/02 §4): `checks.F2_1` on PR 2's own envelope is its first source alone, the five seed tests passing on refusing; the second source and `checks.F2_2` are wired at PR 3, because a failing check on PR 2's run would have made `evals`, a required check, red, and PR 2 could not have merged through the ruleset it measures. S4's test keeps its marker until the attempts. Two consequences, read here (cold review of PR 2, F7): PR 2's `checks.F2_1: pass` is a test-only witness of four seeds refused in a copy of the tree, not a pull request refused; and nothing in `gate.py` requires `F2_1` or `F2_2` on an agent envelope until PR 3 sets that constant, so until then a run that omitted them would still rule GREEN.** `two-key` green on PR 2's own two files for `g-012`, which is Door 2 (its check run is `gates.yml`'s `two-key` job on PR 2's head). After PR 2 merges and before PR 3's first CI run: the human makes `ruling-cited` and `two-key` required, opens the seed PRs from `main`, and makes S4's two attempts; PR 3's run looks each up (`scripts/observe_pr.py`) and writes `checks.F2_1` (both halves) and `checks.F2_2` pass. **A named P3 exception (SPEC/02 §5.1): a PR refused by a gate on `main` cannot exist before the gate is on `main`; the machinery is PR 2's, the reading is PR 3's, whether PR 3 is the repair or the close.** **At PR 3 (Product, `rulings/pr3.md`): the constant is `CLAIM_2_CHECKS` in `src/verdict/gate.py` (`74624cb`), required on every agent envelope after `97d3c76`; the three agent envelopes PR 3's branch recorded before it (`12b4646`, `47258f2`, `6daf6c4`) carry `F2_1` alone and rule RED under it, and no Measured cell cites them. The reading is the `evals` run on PR 3's head after `939709d`, which looks the seed PRs (14 to 18), the owner's attempts (rule suite 4192991324; `evals` job 107206831180) and the three doors (PRs 14, 12, 14) up from GitHub's record, with the rule-suites record fetched by the workflow and read from files so the token never reaches the observer. Read beside claim 2, not as part of it: `12b4646`'s run (35861180676) is the first envelope in `mode: runtime`, GREEN at 54,218 tokens, after the agent boundary took `dynamodb:Scan` (`c34da39`); row 1 stays RED as closed, since a later deploy does not reopen a closed row.** RED if any seed PR's check is green, if `--admin` merges, if `validate` stays green with `bypass_actors` non-empty, or if PR 3's run reads anything else. The count of refagent's passes changes by one golden at PR 2, `g-012` retired and `g-021` added never passed; the checks decide the row. |
| Measured | agent: traps 2/3 (g-010, g-011); ordinary 9/9; guardrail 0/3; control: traps 0/3; ordinary 1/9; guardrail 0/3; mode runtime; never_passed 4; regressed 0; plants 0/0; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; F1_1 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F1_2 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F1_3 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F1_4 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F2_1 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; F2_2 pass https://github.com/andaro74/agentkeel/actions/runs/35951008874; GREEN; envelope `8033c2a7a0588e557df577464c190e64a435e88a`; base b0219756 |
| PRs used / cap | 3 / 4 |
| State | GREEN |

### Open detail (PR 1, #11, 2026-09-22)

- Opened through `/open-milestone`. SPEC/02 was written first and
  `product-spec-reviewer` run on it (1 BLOCK, 8 FINDING, 6 NOTE), pasted
  verbatim in `feasibility.md` §1; every item is ruled in §2 and SPEC/02
  was revised once on them, before any seed was committed. This time the
  order of commits is the order of writing: SPEC/02 lands in `bc35c39`,
  before the first seed (`6ff333a`). The M01 cold review's F5 does not
  recur.
- **Planted** in five commits, one per seed, `6ff333a` to `479abb9`,
  each with its test in `tests/test_m02_seeds.py`, before any code that
  reads them. At `479abb9` all six tests (S1 has two forms) are expected
  failures. A seed is a diff to a seat-owned path under
  `tests/fixtures/m02/`, applied to a throwaway worktree by its test;
  S4 is an attempt against the `main` ruleset, `observed: null`.
- **Read in this PR:** nothing. No `src/gates/`, no CODEOWNERS, no
  `validate` growth. `make plants` lists S1–S5 with "not in the tree
  yet" beside each reader.
- **The BLOCK, and what it changed.** The reviewer found that a seed
  with no ruling is refused by `ruling-cited` and by any `two-key`, so
  nothing planted told the two apart and "one key" had no false state.
  S1 now carries exactly one Threshold Owner ruling, so only `two-key`
  can refuse it, and a second form carries two files from that one seat.
  The one-key case is what M01's second half lacked: a seeded case for
  the half of the claim that costs the most to get wrong.
- **Door 2 is PR 2's own merge** (`g-012` retired with two keys, `g-021`
  added), not a PR of its own: a PR merged properly through a gate
  cannot exist before the gate does, and the cap has no PR to spare for
  a demonstration. The seed PRs are opened from `main` after PR 2 merges
  and read by PR 3's run; SPEC/02 §5.1 names that as a P3 exception, as
  ADR-0007 named M01's. If PR 3 is the close, the reading rides in it.
- **Carried work, with its seats' rulings** (`feasibility.md` §6): row 9,
  the construct's rights table on `TableEncryption.DEFAULT` after a test
  that fails on the collision (`25b2743` fails, `9ea6405` passes; the
  rendered template differs from `main` by one line, `SSEEnabled` true
  to false); row 8, the cold-review skill's diff-or-tree line; row 22,
  ADR-0006 amendment 1 and the S6 note; row 1, ADR-0008; row 21, ruled
  in SPEC/02 §2. Rows 3 and 4 move to PR 2 as Door 2. Row 2, M01's
  video, lands in this PR when the recording is given.
- **This PR's run** writes refagent's envelope in runner mode, gated and
  recorded as at M01. It does not measure claim 2. Its merge triggers
  `deploy.yml` on `main`: the first agent deploy since the failed one,
  read at PR 2 (row 10).

### PR 2 detail (#12, 2026-09-22): the measurement

- **Read in this PR**, in the order the commits land them: `relaxes:` and
  `ceilings:` bars (Threshold Owner); `.github/CODEOWNERS` (Security);
  `src/gates/ruling_cited.py`; `src/gates/two_key.py`, and S1 (both
  forms) and S2 lose their markers in that commit; `validate`'s six new
  checks, and S3 and S5 lose theirs in that commit; the `ratings-helper`
  stub; `gates.yml`, committed unlisted first so that `workflow-hash`
  refusing it could be recorded (row 16); `scripts/observe_pr.py` and
  `build`'s three readers, rehearsed against PRs #10 and #11 (row 17);
  a retired golden out of the run and the gate reading the goldens at the
  envelope's commit; then Door 2, `g-012` retired and `g-021` added with
  the Data Owner's and the Threshold Owner's keys.
- **What went RED on the plant, where.** `uv run pytest
  tests/test_m02_seeds.py` at the head: 5 passed, 1 xfailed (S4). The
  strict markers came off in the reader's commits, and each test asserts
  the planted reason is in the refusal. `make plants`: every reader "in
  the tree". Both gates run on this branch against `main` before the
  ruling files existed and refused it: `two-key` on `g-012`'s
  retirement with no key, `ruling-cited` on 50 paths
  (`runs/pr2_gates_before_rulings.yaml`, run at `0fc95a6`); the ruling
  files are what turn them green on PR 2's head, which is Door 2's record.
- **What PR 2 does not do.** It makes nothing required on the ruleset
  and does not export it: `ruling-cited` and `two-key` become required
  after the merge (SPEC/02 §5.1). It does not open a seed PR or make an
  attempt; S4's `observed` stays null. It does not wire `checks.F2_2` or
  `F2_1`'s second source (SPEC/02 §4, amended here). It does not remove
  `infra/eval-role/`: `AgentkeelM00EvalRole` was still `UPDATE_COMPLETE`
  in the account on 2026-09-22 (Unsure E stands). It does not fill
  `observed_at_pr2_merge` in `runs/row10_first_deploy.yaml`: the merge
  is the first arm64 deploy, and the run file records why the refusal by
  name of `822fe2b5` will not fire at it.
- **Read by the call, not assumed.** `runs/api_probes.yaml`: the ruleset
  endpoint answers unauthenticated but omits `bypass_actors`; the
  rule-suites endpoint is 401 without a token and 200 with the human's.
  `validate` therefore reads the ruleset with a token, and an absent
  bypass list is an error naming the token. Whether a workflow's
  `GITHUB_TOKEN` is shown the list is read on this PR's first `checks`
  run.

### PR 3 detail (#13, 2026-09-23): the repair, and the reading

- **Carried onto the branch from PR 2's merge**, before this session:
  the `main` ruleset exported with `ruling-cited` and `two-key` required
  (`12b4646`, Security; `bypass_actors` `[]`); the agent boundary takes
  `dynamodb:Scan` after the first deploy on which the runtime answered
  (run 35817173042) refused all fifteen goldens on it (`0faf973` the
  test, failing first; `c34da39` the action; the bootstrap stack deployed
  by hand after the human read `cdk diff`); row 10 read (`f54422f`); the
  CODEOWNERS login check's token order (`951d98e`); the three run files
  filled by the human (`76be099`, `979b9db`).
- **The human's window, as the run files record it** (SPEC/02 §5.1).
  Seed PRs 14 to 18 opened from `main` between 13:10Z and 13:11Z, each
  showing its expected check red. Attempt 1, `gh pr merge 14 --merge
  --admin`, refused at 13:34:13Z: "3 of 5 required status checks are
  failing", rule suite 4192991324 (`required_status_checks` fail, actor
  `andaro74`, `refs/heads/main`). So the rule-suites API does record a
  refused `--admin` merge; Unsure B of PR 1 and PR 2 is answered yes, by
  the call. Attempt 2, the repository-admin role in `bypass_actors` from
  13:39:33Z to 13:45:29Z (the ruleset's own `updated_at`, in the
  account's timezone in the file): `validate` RED in `evals` job
  107206831180 while listed, `[]` after. Door 1 and Door 3 are PR 14,
  Door 2 is PR 12.
- **Built in this session, in the order the commits land.** `ab6219d`:
  `scripts/observe_pr.py` reads the rule-suites record and the live
  ruleset from files the workflow fetches, and the recorded suite by id,
  which does not age out of the list as `time_period` does. `74624cb`:
  `CLAIM_2_CHECKS` and `M02_PR2_MERGE` in `src/verdict/gate.py`, the
  first item PR 2's cold review left for PR 3. `939709d`: `evals.yml`
  runs the observer on the three run files on the measuring path with
  `actions: read`, hands `make evals` the three observations, and the
  `RULESET_TOKEN` step fetches the rule-suites record beside the live
  ruleset so the observer, code from the PR, never sees the secret;
  S4's `xfail(strict=True)` marker comes off in that commit. `b7311b3`:
  `infra/eval-role/` removed, the stack `DELETE_COMPLETE` at 13:48:15Z
  (row 16; Unsure E). `c7a8242`: `validate` accepts a ruling glob that
  names a deleted path, because four M00 and M01 rulings name files
  under `infra/eval-role/` and a past ruling is not edited.
- **What the branch's last run said before the wiring** (35874322479,
  `6daf6c4`): the envelope GREEN in `mode: runtime` with `F2_1` from
  the first source alone, and the job failed on pytest: S4's strict
  marker refused the filled run file (`XPASS(strict)`), and a test on
  the observer asserted the seed's planted state. Both repaired here.
  The marker did what strict is for.
- **Read under the constant, now.** `12b4646`, `47258f2` and `6daf6c4`
  are agent envelopes after `97d3c76` that carry `F2_1` alone; the gate
  rules each RED from `74624cb` on ("checks.F2_2 is missing"), and
  `tests/test_gate.py` holds it. None is cited by a Measured cell. They
  stay in history as what they were: GREEN under the gate of their day.
- **Before the run, not evidence:** the three observers run locally
  against GitHub with the human's token. Five seeds `found`, unmerged,
  expected check `failure`, required on `main`, path named in the job
  log (status 200); attempt 1 witnessed by the rule-suites API; attempt
  2 by `validate`'s line in the job's log; three doors in the record;
  `build`'s three readers pass on all three. That is what PR 3's CI run
  is expected to read. The reading is that run's.
- **What PR 3's run read:** in the close detail below, from the envelope
  for `8033c2a` (run 35951008874).

### Close detail (PR 3, #13, the close, 2026-09-24)

**Row 2 is GREEN.** The cap was four and three were used. Every seeded
change was refused on a real pull request, both of the owner's attempts
were refused and are in GitHub's record, and the three doors are in the
PR record.

**The measurement.** The Measured cell is copied from the gate's reading
of the envelope for `8033c2a7a0588e557df577464c190e64a435e88a`, written
by the `record` job of CI run 35951008874 as `github-actions[bot]`
(`905f438`), the first run on this branch after the wiring (`939709d`)
and the cold review's repairs. `make ledger` exits 0 against it. Its own
verdict is GREEN and the gate's is GREEN; `mode: runtime`, so the agent
answered inside the construct. What it says, as numbers: agent traps 2/3
(`g-010`, `g-011`), ordinary 9/9, guardrail 0/3; control traps 0/3,
ordinary 1/9, guardrail 0/3; `never_passed` 4 (`g-013` to `g-015`, which
wait for M03's guardrail, and `g-021`, which no agent can pass under
refagent's tool contract, `pr2-data-owner.md`); `regressed` 0; plants
0/0; `F0_2`, `F0_3`, `F1_1` to `F1_4`, `F2_1`, `F2_2` all pass; 54,009
tokens (48,815 in, 5,194 out) against a cap of 150,000. The trap count is
2/3 and not 3/3 because `g-012` was retired at PR 2 (Finding F0.1) and
`g-021` took its place never passed; the checks decide the row, and the
count is read beside them.

**What PR 3's run read** (`checks.F2_1`, both sources, and `checks.F2_2`;
the observer's step in the `evals` job of run 35951008874 wrote the three
observations from the files the `RULESET_TOKEN` step fetched, no warning
fired, and `build` read them as a pass). Row 2's four RED conditions,
each checked against that run: no seed PR's expected check was green
(five `failure` conclusions, each required on `main`, each naming the
seed's path in its job log); `--admin` did not merge (PR 14 unmerged,
rule suite 4192991324 `required_status_checks` fail); `validate` did not
stay green with `bypass_actors` non-empty (RED in job 107206831180 while
the admin role was listed, `[]` now); and the run read nothing else. The
run on the envelope commit (35951237584) then ruled the recorded envelope
GREEN on the skip path, spending nothing.

**What GREEN does not mean.** One person holds every seat, so two keys
are two files one person can write; the gate holds that the change was
named under the seat that owns the path, not that a second person
looked. The checks are run by the pull request's own code, and anyone
with write can edit the workflow and its hash in one PR; what refuses
that is `ruling-cited` on `infra/**`, written by the same person, until
M05 takes the reader from `main`. The bot exemption reads an author name.
The ceiling refused a call once, unplanned, and has no seeded case.

**Still open at this close, for the human before the merge:** the two
top-level `doors:` blocks in `f2_2_three_doors.yaml` (PR 13 Unsure A);
after the merge, `git tag m02` on `main`, then the seed PRs 14 to 18
closed unmerged with their branches kept (SPEC/02 §5.1), and the M02
video recorded at the tag for M03 PR 1.

**Findings and Unsure items: every one has a home.** By source:

| Source | Count | Where each is held |
|---|---|---|
| `product-spec-reviewer` on SPEC/02 | 1 BLOCK, 8 FINDING, 6 NOTE | `feasibility.md` §2, each ruled before the first seed; the BLOCK became S1's one-key form |
| PR 1 seat reports and cold review | security 0/5/13; cold 0/5/5 | `rulings/pr1-cold-review.md` table, every row repaired or recorded; `pr1-security.md` |
| PR 2 seat reports and cold review | cold 0/7/7; security 0/5/5; threshold 0/4/7; tool 0/3/7; data 0/3/6 | `rulings/pr2-cold-review.md` table: repaired in PR 2, ruled by a seat, or recorded with a milestone (M03 PR 1, M05, M06); the M03 and later items are rows 1 to 8 and 12 to 15 of `milestones/M03/open.md` |
| PR 3 seat reports and cold review | cold 0/3/9; security 0/5/10; platform 0/2/5 | `rulings/pr3-cold-review.md` table: repaired in `7c9e6b1`, `871d90a`, `6b4cf2e`, ruled here, or in `milestones/M03/open.md` (rows 1, 2, 3, 8, 10, 15) |
| PR 3's own findings | 9 | `rulings/pr3.md` table, each with a seat and a milestone |
| Unsure, PR 11 (A to H) | 8 | A the video landed (`f6d1e73`; its length is over the ceiling, M03 row 9); B answered yes at the attempt; C, H answered at PR 2 (`pr2-security.md`); D ruled (`pr2-threshold-owner.md` §5); E done at PR 3 (`b7311b3`); F Door 2 was PR 2's merge; G ruled (ADR-0008) |
| Unsure, PR 12 (A to I) | 9 | A, B, C, D, E closed at PR 2 or PR 3 as their text says; F (`822fe2b5` in ECR) M03 row 10; G (`g-021`) M03 row 5; H (SPEC/02 §2's closed list) M03 row 1; I done (`74624cb`) |
| Unsure, PR 13 (A to F) | 6 | A M03 row 10 unless collapsed before the merge; B ruled here: the constant stays PR 2's merge, SPEC/02 §4's words; C M03 row 1; D M03 row 2; E ruled here: the two reads warn, the check names its witness (`pr3-security.md`); F done in this close |
| `milestones/M02/open.md` rows 1 to 24 | 24 | `feasibility.md` §6 answered each at PR 1; rows dated M04, M05, M06, M07 and the two not verified item by item (12, 13) are carried to `milestones/M03/open.md` rows 11 to 16 |

**Settled at this close:** the rule-suites API records a refused
`--admin` merge (PR 1 Unsure B, PR 2 Unsure B, SPEC/02 §5.1's open
question), read by the call: suite 4192991324.

### For the seats, at M02 PR 2 open

- **Security:** make `ruling-cited` and `two-key` required after PR 2
  merges, not before (SPEC/02 §5.1); whether `GITHUB_TOKEN` on a PR run
  can read the live ruleset for `validate`'s diff, or a token with
  `administration:read` is needed; whether `gates.yml` has what it needs
  on a fork PR (row 11); whether the rule-suites API records a refused
  `--admin` merge (finding 3), read at the attempt; destroy
  `AgentkeelM00EvalRole` so PR 2 can remove `infra/eval-role/` (row 16);
  read the first successful deploy (row 10). From the
  `security-reviewer` report on PR 1 (PR body): (a) which ruleset fields
  `validate`'s live-vs-export compare reads (`enforcement`, `conditions`,
  `rules`, `bypass_actors`; not `updated_at`, `node_id`, `_links`), or
  S4 attempt 2 leaves it RED after `bypass_actors` is restored; (b) the
  order of the ruleset edit and the export, or `checks` is red on every
  branch between them for a reason that is not the seed, and S3's and
  S5's expected check proves nothing; (c) which job does the live compare
  and with which token, and that `gates.yml` has no fork condition;
  (d) `ruling_cited.py` reads CODEOWNERS from the base ref (SPEC/02 §6).
- **Threshold Owner:** `relaxes:` on every bar in `thresholds.yaml`; the
  cap against 54,156 measured; `max_tokens_per_session` and `daily_usd`
  (row 18); and, before the seed PRs are opened, that five seed PRs each
  trigger an `evals` run at about 54,000 tokens.
- **Data Owner, Threshold Owner:** the two ruling files for `g-012`'s
  retirement and `g-021`, both `pr:` 12 (rows 3, 4).
- **Tool Owner:** the `ratings-helper` manifest stub and computed semver
  (row 20).
- **Engineering:** `src/gates/`, `scripts/observe_pr.py`, the `validate`
  checks, `two-key`'s human-commit case (row 6), the instruments (row
  12), the smaller items (row 13).
