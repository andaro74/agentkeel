---
# Cold review of M02 PR 3 (#13), base main (97d3c76), head c789320, by
# engineering-cold-reviewer from the diff and the ledger row. DRAFT until
# the Engineering seat reads it and rules; Engineering's key for this PR's
# paths is pr3-engineering.md, and this file names only itself and takes
# no second key over anything. The three reports (engineering-cold-reviewer,
# security-reviewer, platform-architect) are in the PR body verbatim; their
# items are triaged in the table below.
ruling: pr3-cold-review
seat: Engineering
authorises:
  - milestones/M02/rulings/pr3-cold-review.md
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#4-falsifiers
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-cold-review.md
  - milestones/M02/rulings/pr3.md
  - milestones/M02/rulings/pr3-security.md
  - milestones/M02/rulings/pr3-engineering.md
pr: 13
---

# Cold review: M02 PR 3 (repair, and the reading)

## What was done with it

Read at head `c789320`. Every report opens with `Read: the diff
97d3c76...` and none read the tree for its findings (the security report
names the four tree lines it read for context). The reviewer read the
constant first, as PR 2's cold review asked. Repairs went in as their own
commits after the review (`7c9e6b1` Engineering, `871d90a` Security,
`6b4cf2e` the rulings); the diff between the head read and the head that
this file joins is those repairs and this file. Counts: cold review 0
BLOCK, 3 FINDING, 9 NOTE; security 0/5/10; platform-architect 0/2/5. No
BLOCK anywhere. The `engineering-cold-reviewer` run was cut off once by a
rate limit before it wrote and was resumed from its own transcript with
HEAD unchanged; the report is the resumed run's.

| # | Finding | Status |
|---|---|---|
| cold F1, security F2 | `f2_2_three_doors.yaml` has two top-level `doors:` keys; the first still says door 3 `pr: null`, the loader keeps the second | **Recorded** (Product, `pr3.md` finding 6): the session does not edit run files. The reading is unchanged either way; the human decides before the merge whether to collapse the blocks. Under **Unsure** in the PR body |
| cold F2 | the rulings' `grep -c xfail` line gave the wrong count; the seed module's docstring still said S4 is marked | **Repaired** (`7c9e6b1` the docstring; `6b4cf2e` both rulings: 2 before, 1 at HEAD) |
| cold F3 | the rule suite read by id was not tied to the attempt's time | **Repaired** (Engineering, `7c9e6b1`): `within_window_of_attempt` with the list path's `WINDOW`; a suite a year off is not the refusal; test holds it |
| security F1 | the wiring has not fired in CI inside the diff | **Stands until the run**: the `evals` run on the head after the repairs records the envelope with `F2_2`; its run id goes in `pr3-security.md` and the M02 README before the merge |
| security F3, platform F1 | the boundary redeploy was asserted, not recorded | **Repaired** (Security, `871d90a`): `describe-stacks` and the stack events in `infra/bootstrap/README.md` and `pr3-security.md`; the stale "no agent stack has yet deployed" sentence rewritten |
| security F4 | a failed rule-suites read warns; what F2_1 does then was unstated | **Repaired in prose** (Security, `871d90a`): attempt 1 then passes on the human's output alone, the weaker witness SPEC/02 §5.1 names, and the observation says which; `--remove-on-error` added (N8). The by-id read is not made to fail the step: a record GitHub may one day purge must not fail every later run |
| security F5 | "this PR's first commit" was false | **Repaired** (Security, `871d90a`): the export's position and time |
| platform F2 | the ceiling refused a call once, unplanned; SPEC/01 §9 lists it as a control with no seeded case | **Recorded** (Product, `pr3.md` finding 8): "observed once, unplanned" against that bullet at M03 PR 1; a seeded case at M05, Security |
| cold N1 | the reading is not in the diff; the close checks the envelope against row 2's RED conditions | **Stands**: written at the close from the envelope |
| cold N2 | `judge`'s default is claim 1 only; `rule` passes `required_checks` | **Repaired** (comment, `7c9e6b1`) |
| cold N3 | attempt 2's CI line is recorded, not required; "the checks job" named the wrong job | **Repaired in part** (`7c9e6b1`): the witness string says "the recorded job"; the check still reads the human's `validate_result` and the live list, with the CI line beside it. Engineering, M03 PR 1, with PR 2's cold F3 |
| cold N4, security N15 | `deleted_paths` is history-wide and a rename is not a deletion | **Recorded** (Product, `pr3.md` finding 9, inside finding 3) |
| cold N5 | content beyond PR 2's list, each ruled | **Recorded**: the M02 README's PR 3 detail names each |
| cold N6 | the three envelopes RED under the constant; `12b4646` the first in runtime mode | **Recorded** (row 2's cell, `tests/test_gate.py`) |
| cold N7 | the token step greps `rule_suite:` ids out of a Product file | **Stands**: digits only steer the URL; the step runs no PR code |
| cold N8 | "PRs used" stays 2 / 4 until the close | **Stands** |
| cold N9 | the first refusal of a real PR was claimed without its run URL | **Repaired** (Security, `871d90a`): job 107181506184 on `12b4646` |
| security N6 | `actions: read` is the least scope for a job log; on the non-fork job only | **Stands** |
| security N7 | the forbidden-command list in the workflow test was three strings | **Repaired** (Engineering, `7c9e6b1`): `scripts/`, `src/`, `bash `, `sh `, `./`, `node ` |
| security N9 | `per_page=100` is not paginated; the by-id read carries attempt 1 past that | **Stands**: the test holds it |
| security N10 | the ceiling admits `dynamodb:Scan` on any table for any platform role; the construct's grant is one table | **Stands**: an allow list caps by omission; recorded |
| security N11 | the cdk-nag line for the bootstrap stack is not in the diff | **In the PR body**: `make validate`'s `ok   cdk-nag, both stacks` at the head |
| security N12 | the export's contents, and which contexts `validate`, `regression`, `cost-cap`, `signature` live in | **Stands**: `checks` and `evals`; SPEC/00 §5's names are jobs' steps, not contexts, since M01 PR 2 |
| security N13 | anyone with write can edit the workflow and the hash in one PR; the reader is the PR's own | **Stands**: the header's first gap, M05 |
| platform N1 | the read-back probe does not cover `dynamodb:Scan` | **Recorded** for Security: two rows in `scripts/read_back_grants.py`, run once with admin, at M03 PR 1 |
| platform N2 | the ceiling's `bedrock-agentcore:*` would pass the boundary test for any action under it | **Repaired** (Engineering, `7c9e6b1`): the agent role's grants contain no `bedrock-agentcore:` action |
| platform N3 | the eval role's Deny has no recorded refusal | **Stands**: item 18's probe step; M05 |
| platform N4 | the OIDC provider's origin was never recorded; `app.py`'s subject comment pointed nowhere | **Repaired** (Security, `871d90a`): the README says the provider predates the repository and its origin is landing-zone work; the comment names the two files |
| platform N5 | feasibility and open.md dated the eval-role removal to PR 2 and PR 1 | **Recorded** (Product, `pr3.md` finding 7) |

## What stands for the close, and for M03

At the close of this PR: the run id of the `evals` run that reads the
seed PRs, the attempts and the doors, in `pr3-security.md` and the M02
README; the envelope's `F2_1` and `F2_2` against row 2's four RED
conditions (cold N1). For M03 PR 1 (Product, Engineering): SPEC/01 §9's
ceiling bullet (platform F2), SPEC/02 §2's closed-list amendment with the
deletion sentence (finding 3), attempt 2's CI line required (cold N3, PR
2 cold F3), PR 2's cold N3 and N7, the read-back probe's two rows
(platform N1). For M05 (Security): the bot exemption, the reader taken
from `main`, a seeded case for the ceiling and for the eval role's Deny.

## The draft, verbatim

Read: the diff 97d3c76...c789320 (42 files)

Full text of `C:\Users\andar\code\agentkeel\milestones\M02\rulings\pr3-cold-review.md` (draft; the Engineering seat rules and commits it):

---
# M02 PR 3 (#13), the cold review. Engineering's second file; names only
# itself. Read cold from `git diff 97d3c76...c789320` and
# `git log 97d3c76..c789320`, row 2 of milestones/README.md and
# milestones/M02/README.md. Not read: the PR body, feasibility.md below
# its front matter, commit bodies.
ruling: DRAFT
seat: Engineering
authorises:
  - milestones/M02/rulings/pr3-cold-review.md
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#4-falsifiers
  - SPEC/02-seats-and-change-gates.md#51-when-each-is-measured
  - milestones/M02/rulings/pr2-cold-review.md
  - milestones/M02/rulings/pr3.md
  - milestones/M02/rulings/pr3-security.md
  - milestones/M02/rulings/pr3-engineering.md
pr: 13
---

# Cold review: M02 PR 3 (#13), base `97d3c76`, head `c789320`

Read: the diff 97d3c76...c789320 (42 files), 20 commits, 3 of them
`github-actions[bot]`'s (`a6c6a77`, `031d42b`, `4ac8c47`). The constant
was read first, as PR 2's cold review asked.

## The six checks

1. **Shape.** PR 3 is the repair. The diff holds what PR 2's cold review
   listed ("What stands for PR 3"): the constant (`src/verdict/gate.py:83-84`,
   `74624cb`), the `evals.yml` wiring (`.github/workflows/evals.yml:277-287`,
   `939709d`), `infra/eval-role/` gone (`b7311b3`), `observed_at_pr2_merge`
   filled (`milestones/M02/runs/row10_first_deploy.yaml:104`). It also holds
   four things that list did not name; see N5. Nothing here builds a reader
   in a last PR: PR 3 is not the close (row 2 stays `OPEN`, `2 / 4`,
   `milestones/README.md:35`). Not a BLOCK.
2. **The plant.** S1–S5 under `tests/fixtures/m02/` are untouched by the
   diff (`git diff 97d3c76...c789320 --stat -- tests/fixtures/m02/` is
   empty). The gate going RED on real pull requests is recorded by the
   human in `milestones/M02/runs/f2_1_seed_prs.yaml:29-89` (PRs 14–18, each
   expected check `X`) and `f2_1_bypass.yaml:45-64`; the CI reading of them
   is not in the diff (N1).
3. **P5.** `scripts/observe_pr.py` writes observations, not envelopes
   (`observe_pr.py:404`, "not an envelope; rules nothing"). The three
   envelopes in the diff are bot-authored. No new writer or reader of
   envelopes. `gate.judge` has one caller in `src/`, `gate.rule`
   (`gate.py:438`). Not a BLOCK.
4. **Frozen and owned paths.** `src/baseline/`: no change. Every seat path
   is named by a ruling with `pr: 13`: `infra/**`, `.github/workflows/evals.yml`,
   `.claude/agents/platform-architect.md` (its `seat: security`, line 4) in
   `pr3-security.md:7-13`; `milestones/**`, `CLAUDE.md` in `pr3.md:9-17`;
   `src/`, `scripts/`, `tests/` in `pr3-engineering.md:9-21`;
   `pr3-security.md` covers itself (`src/gates/ruling_cited.py:53`). Not a
   BLOCK.
5. **Does it work.** Read below: F1–F3, N2–N4, N6, N7.
6. **Claims in prose.** The diff's only "governed" is the construct's name
   (`CLAUDE.md:136`). One fired-control claim without a citation: N9.

## BLOCK

None.

## FINDING

**F1 — `milestones/M02/runs/f2_2_three_doors.yaml` has two top-level
`doors:` keys (lines 5 and 18).** The human's fill appended a second
`doors:` block instead of editing the first; `observed:` follows at line
31. Line 17 says door 3 is `pr: null`, line 28 says `pr: 14`.
`yaml.safe_load` keeps the last mapping silently, so `observe_pr.py:355`
reads the filled block and nothing errors; a strict loader would refuse
the file, and nothing in `validate` reads run files. The record says two
things about door 3. Falsify: `git grep -c '^doors:' c789320 --
milestones/M02/runs/f2_2_three_doors.yaml` prints 2. Product's file
(`pr3.md:13`); the session does not edit run files. Product decides
whether the human collapses the two blocks before the merge or the
duplicate is recorded as-is; either way the reading is unchanged.

**F2 — the reader instructions in two rulings give the wrong count.**
`pr3-engineering.md:136` and `pr3.md:107` say
`git show 6daf6c4:tests/test_m02_seeds.py | grep -c xfail` prints 1 before
and 0 at HEAD. It prints 2 at `6daf6c4` and 1 at `c789320`:
`tests/test_m02_seeds.py:7`, the module docstring, still says the S4 test
"is marked `xfail(strict=True)`", which it no longer is (the marker line
was removed in `939709d`). Two repairs: the numbers in both rulings, and
the docstring at line 7 (Engineering). Falsify: `git grep -c xfail
c789320 -- tests/test_m02_seeds.py`.

**F3 — `observe_pr.py:231-241`, `rule_suite_by_id`: the by-id witness is
not tied to the attempt.** `is_the_actors_refusal` (line 240) requires
`result: fail`, the actor's name and `refs/heads/main`, and nothing else:
not `pushed_at` within `WINDOW` of `at` (line 86; the list path applies it
at line 270), not `after_sha`, not the PR. Any failed push by the owner to
`main` on any day, recorded as `rule_suite:` in `f2_1_bypass.yaml:52`,
makes `rule_suite_fail_found` true (line 307), and `build.py:353` accepts
that alone. Falsify: in `tests/test_observe_pr.py` `SUITE`
(line 403), set `pushed_at` a year off; `is_the_actors_refusal` stays
true. Repair (Engineering, small): apply the same `WINDOW` test to the
by-id record and report it. Severity is low because attempt 1's check
already passes on `human_message_contains` alone (N3), which is PR 2's
design, not this PR's.

## NOTE

**N1 — the reading is not in this diff.** No envelope in the diff carries
`F2_2` (`git grep -l '"F2_2"' c789320 -- evals/history/` finds nothing);
the three that are (`12b4646`, `47258f2`, `6daf6c4`) carry `F2_1` without
`F2_2`, as `milestones/README.md:35` says. `milestones/M02/README.md:158`
says what PR 3's run read is written at the close. This review therefore
cannot say the second source passed through `build` and `gate`; the
`evals` run on `c789320` decides, and the row's own RED conditions
(`README.md:35`: a green seed check, an `--admin` merge, `validate` green
with `bypass_actors` non-empty, or the run reading anything else) are what
the close must check that envelope against.

**N2 — the constant's boundary.** `gate.py:157-160`: `merge-base
--is-ancestor 97d3c76 97d3c76` succeeds, so the merge commit itself is
held to claim 1 only; the ledger's "after `97d3c76`" (`README.md:35`) is
exact. PR 2's own envelope is `183496d`'s, an ancestor. A commit git
cannot place is held to both (`tests/test_gate.py:183`). `judge`'s
default stays `CLAIM_1_CHECKS` (`gate.py:281`) and `rule` is the one
caller that passes `required_checks` (`gate.py:438`); a future direct
caller in `src/` would get claim 1 only. Fine today; worth a comment.

**N3 — attempt 2's CI witness is recorded, not required.**
`observe_pr.py:323-327` reads the job the human recorded and grades
`ci_red_lines`; `build.py:356` passes on `human_said.validate_result ==
"RED"` and the live `bypass_actors == []`, and does not read
`ci_red_lines`. So `checks.F2_1`'s attempt-2 half is the human's word
plus the live ruleset now, with CI's line beside it. Also naming: the key
is `checks_job_id` and the witness string says "the checks job's log"
(`observe_pr.py:326`), while the id at `f2_1_bypass.yaml:61` is the
`evals` job's (validate's live compare moved there at PR 2). The log is
read by id, so the reading is right; the words are not. Engineering, M03.

**N4 — `checks.py:156-167`, `deleted_paths`.** `git log --diff-filter=D
--name-only` without `--no-renames` lists a rename as `R`, not `D`, so a
ruling glob that names a path renamed away is still refused. The set is
history-wide and not tied to the ruling's PR: any new ruling may name any
path ever deleted and pass the front-matter check (harmless for
`ruling-cited`, which matches globs against the diff). Both are inside
Product's finding 3 (`pr3.md:82-84`, SPEC/02 §2 at M03 PR 1). CI has the
history: `fetch-depth: 0` at `evals.yml:111` and `:163`.

**N5 — content beyond PR 2's cold review list, each ruled.** The agent
boundary takes `dynamodb:Scan` (`0faf973` test first, `c34da39` action;
`infra/bootstrap/app.py:184-192`, `pr3-security.md`); the CODEOWNERS
login check's token order (`951d98e`, `src/validate/codeowners.py:36-58`);
the ruleset export with `ruling-cited` and `two-key` required
(`12b4646`, `infra/ruleset/main.json`, `bypass_actors: []`); the observer
reading from files the workflow fetches (`ab6219d`, from
`pr2-security.md` item 2). None touches claim 2's plant or its readers'
verdict logic. Recorded so the shape is on the page.

**N6 — the three envelopes.** Bot-authored (`git log --format=%an
97d3c76..c789320 -- evals/history/`), GREEN by `build`, RED under
`c789320`'s gate for `checks.F2_2 is missing`; `tests/test_gate.py:197-206`
holds it and skips when a file is absent (line 205), which cannot happen
on `main`. `12b4646` is the first `mode: runtime` envelope (`git grep -l
'"mode": "runtime"' origin/main -- evals/history/` is empty) and its
54,218 tokens are `tokens_in` 48,862 + `tokens_out` 5,356, as
`README.md:35` says.

**N7 — the token step reads the run file for what to fetch.**
`evals.yml:238` greps `rule_suite:` ids out of `f2_1_bypass.yaml`, a
Product-owned file, to choose which suites the `RULESET_TOKEN` step
fetches; the step runs no code from the PR
(`tests/test_evals_workflow.py:239-251`). A run-file edit can add ids,
not read the secret. Fine. The new `infra/workflows.sha256:26` hash was
not recomputed here; PR 3's own `validate` verifies it.

**N8 — "PRs used" stays `2 / 4` at PR 3** (`README.md:35`), as row 1 did
at M01 PR 3's merge (`616b620`). Consistent with precedent; the close
writes it.

**N9 — a fired-control claim without its evidence.** `pr3-security.md`,
section `infra/bootstrap/app.py`, second paragraph: "the first refusal of
a real pull request by the gate, and on PR 3 itself." That is a firing
worth recording, and a reader should be able to falsify it: cite the
`ruling-cited` check run URL on the head that was refused
(`89819e2` is the commit that answered it). Security, one line.

## What a reader can run

```
git grep -c '^doors:' c789320 -- milestones/M02/runs/f2_2_three_doors.yaml   # 2 (F1)
git grep -c xfail c789320 -- tests/test_m02_seeds.py                           # 1, not 0 (F2)
git grep -l '"F2_2"' c789320 -- evals/history/                                  # nothing (N1)
git grep -l '"mode": "runtime"' origin/main -- evals/history/                   # nothing (N6)
git log --format='%h %an' 97d3c76..c789320 -- evals/history/                    # three bot commits (N6)
```

BLOCK: 0 · FINDING: 3 · NOTE: 9

## To falsify this file's own claims, at the head that carries it

```
uv run pytest -q tests/test_observe_pr.py tests/test_evals_workflow.py tests/test_bootstrap.py tests/test_m02_seeds.py   # the repairs' tests
git log --format='%h %s' c789320..HEAD                                   # the three repair commits, then this file
git grep -c xfail HEAD -- tests/test_m02_seeds.py                        # 1: the docstring's mention
```
