---
# Cold review of M02 PR 1 (#11), base main (ec0358d), head 8e2b0a3, by
# engineering-cold-reviewer from the diff and the ledger row. DRAFT until
# the Engineering seat reads it and changes `ruling:` to `pr1-cold-review`.
# Engineering's key for this PR's paths is pr1-engineering.md; this file
# names the same paths and takes no second key over them. The security-
# reviewer report is in the PR body verbatim, not here.
ruling: DRAFT
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - tests/test_m02_seeds.py
  - tests/fixtures/m02/**
  - tests/fixtures/README.md
  - src/verdict/plants.py
  - src/verdict/gate.py
  - .gitattributes
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#5-the-seeded-cases
  - milestones/README.md
  - milestones/M02/README.md
pr: 11
---

# Cold review: M02 PR 1 (plant)

## What was done with it

Read at head `8e2b0a3`. Repairs went in as their own commits after the
review, before the PR opened; the head that opens is later than the one
read, and the diff between them is the repairs below and nothing else.

| # | Finding | Status |
|---|---|---|
| F1 | S1's one ruling file is itself an uncovered `milestones/**` path, so `ruling-cited` as SPEC/02 §6 defined it would refuse S1 before `two-key` is reached | **Repaired** (Product): SPEC/02 §2 "Covers" now says a ruling file with this PR's `pr:` covers itself, whatever its `seat:`. The test's line 65 stands. |
| F2 | SPEC/00 §8 M02 says "threshold relaxed without a ruling"; S1 is relaxed with one key | **Repaired** (Product): §8 M02's seed line amended in place, with the reason, under PR 1's ruling. SPEC/00 wins, so the SPEC says what was planted. |
| F3 | `make plants` names `src/validate/edges.py` and `golden_ids.py`; the tests import `checks.check_edges` and `checks.check_golden_ids_against` | **Repaired** (Engineering): the tests import `src.validate.edges.check` and `src.validate.golden_ids.check`. PR 2 lands those modules or changes both. |
| F4 | `test_s4_the_owner_was_refused` reads keys the run file never lists; `message_must_contain` is an expectation, not an observation | **Repaired** (Engineering, Product): the test takes `message_must_contain` from `attempts[0]`; the run file's header lists every observed key. |
| F5 | The run file says a human-written file feeds no check, and the S4 test passes on what the human typed | **Repaired** (Product, Engineering): the run file and the test's docstring say the test is the weaker witness of the two SPEC/02 §4 names, and `checks.F2_1` passes only if PR 3's API lookup agrees. |
| N1 | Explainer "Why it matters" in the present tense about controls that do not exist | **Repaired** (Product): rewritten as what M02 is to do; "none of that is built yet". |
| N2 | Worktree registered after `git apply`, so a failed apply leaks it | **Repaired** (Engineering): appended before apply. |
| N3 | `-text` landed one commit after S1's patches | Recorded; both patches are `i/lf`. |
| N4 | CLAUDE.md's Security row lacked `.github/CODEOWNERS` | **Repaired** (Product). |
| N5 | Verified as stated | Recorded. |

## The draft, verbatim

Read: the diff ec0358d...8e2b0a3 (32 files)

Read: the diff ec0358d...8e2b0a3 (32 files), the 12 commits ec0358d..8e2b0a3
by subject and `--stat`, ledger row 2, `milestones/M02/README.md`, and the
SPEC/00 §8 M02 subsection this PR cites. Not read: the PR body,
`milestones/M02/feasibility.md` below its front matter, commit bodies.

### 1. Shape — held

- SPEC/02 (`bc35c39`), ledger row 2 on open (`milestones/README.md`,
  `milestones/M02/README.md`), explainer draft with "What happened" empty
  (`docs/milestones/M02.md` lines 55-56: the heading is followed directly by
  "## For the engineer"), feasibility note present (`8e2b0a3`).
- Five seeds, one commit each, each holding only its patch(es) or run files
  and `tests/test_m02_seeds.py`: `6ff333a` (S1, 2 patches), `74a38be` (S2),
  `d8fbdb1` (S3), `9eb539c` (S4, 3 run files), `479abb9` (S5). SPEC/02
  precedes the first seed; the listing (`b3c6b3a`) follows the last.
- Nothing reads a seed: `src/gates/`, `.github/CODEOWNERS`,
  `scripts/observe_pr.py` do not exist at HEAD (`ls` fails on all three);
  `src/validate/checks.py` defines no `check_edges` or
  `check_golden_ids_against` (its six `def check_*` are the M01 set).
- Carried items are not readers of claim 2: `tests/test_bootstrap.py`
  (`25b2743`) reads the bootstrap and construct templates;
  `infra/construct/governed_agent.py` (`9ea6405`) changes one enum.

### 2. The plant — in the repo, not yet RED (PR 1 does not measure)

- The five patches are in the index as LF (`git ls-files --eol`: `i/lf w/lf
  attr/-text` for all five) and every one passes `git apply --check` at HEAD.
- `uv run pytest tests/test_m02_seeds.py tests/test_bootstrap.py -q`:
  46 passed, 6 xfailed. All six seed tests are `xfail(strict=True)`
  (`tests/test_m02_seeds.py` lines 59, 71, 84, 97, 108, 130).
- `make plants` prints the SPEC/02 block with S1–S5 and each reader "not in
  the tree yet"; the SPEC/01 block is unchanged.
- S4's premise holds at HEAD: `infra/ruleset/main.json` has `bypass_actors:
  []` and required checks `checks`, `cold-review-ruling`, `evals` (three,
  as `milestones/M02/runs/f2_1_bypass.yaml` line 12 says).
- Row 9's test can fail: extracted `25b2743` to the scratchpad and ran
  `pytest tests/test_bootstrap.py -k needs_an_action` — 1 failed,
  `{'RefagentRightsTable5C3A455B': ['kms:CreateGrant']}`; at HEAD it passes.

### 3. P5 — held

`src/verdict/gate.py` lines 459-464 change only `print_plants`; no verdict
path touched. `src/verdict/plants.py` adds two dicts and no reader. Nothing
in the diff opens `evals/history/` or writes an envelope. No fixture under
`tests/fixtures/m02/` is an envelope.

### 4. Frozen and owned paths — held

`git diff --name-only ec0358d...8e2b0a3 -- src/baseline/` is empty. Every
seat-owned path in the diff is in a ruling file of its seat: Product in
`rulings/pr1.md`, Security (`infra/construct/governed_agent.py`,
`infra/bootstrap/README.md`) in `rulings/pr1-security.md`, Engineering
(`tests/**`, `src/verdict/*`, `.gitattributes`) in `rulings/pr1-engineering.md`.
`docs/milestones/README.md`'s one changed line is what `src/ledger.py`
lines 91-92 write once `docs/milestones/M02.md` exists. `make validate`: 6 ok.

### 5. Does it work — findings

**FINDING 1 — S1's "one key" premise is refused by SPEC/02's own
definition of `ruling-cited`.** `tests/fixtures/m02/s1-one-key.patch` lines
1-6 add `milestones/M02/rulings/seed-s1-threshold-owner.md`. That path is
`milestones/**`, Product's (SPEC/00 §5). SPEC/02 §2 "Covers": a ruling
covers a path when `seat:` is that path's CODEOWNERS owner. The seed's only
ruling has `seat: Threshold Owner` and `authorises: [thresholds.yaml]`, so
the new ruling file itself is an uncovered seat-owned path and §6's
`ruling-cited` ("for every seat-owned path, a ruling file in the merge ref
that covers it"; the only exemption named is `evals/history/**` by the bot)
refuses S1 before `two-key` is reached. `tests/test_m02_seeds.py` line 65
asserts `ruling_cited.refusal(tree, base=ROOT, pr=0) is None`. As written
the one-key form is again told apart from the no-ruling form by nothing,
which is the product-spec-reviewer's BLOCK reappearing one layer down. The
same rule bites every PR: this PR's `rulings/pr1-engineering.md` is covered
only because `rulings/pr1.md` authorises `milestones/M02/**`. Cure in PR 2
(SPEC/02 §2 or §6, Product): say that a file under `milestones/*/rulings/`
with this PR's `pr:` covers itself, or require a Product key on every PR.
Not a BLOCK: nothing here makes the plant pass; the seed and the test are
both still false states.

**FINDING 2 — the cited ruling names a seed that was not planted.** SPEC/00
§8 M02, the ruling this PR cites, says "Seeded: threshold relaxed without a
ruling". What is planted is a threshold relaxed with one ruling (SPEC/02 §5
row S1; `s1-one-key.patch`). This PR amends SPEC/00 §5's Security row, the
`ruling-cited` line and R9 (diff, `SPEC/00-overview.md` lines 105, 138-140,
743-744) and leaves §8 M02's seed line as it was. CLAUDE.md line 5: SPEC/00
wins. Either §8 M02 gets the same one-line amendment under ADR-0008 or a
sibling, or the no-ruling threshold seed is planted too. Product.

**FINDING 3 — the reader paths `make plants` checks are not the paths the
tests import.** `src/verdict/plants.py` line 37 names S3's reader
`src/validate/edges.py` and line 40 names S5's `src/validate/golden_ids.py`;
`tests/test_m02_seeds.py` lines 99-100 and 137-138 import
`src.validate.checks.check_edges` and `checks.check_golden_ids_against`.
`src/verdict/gate.py` line 461 decides "in the tree" by
`(ROOT / reader).exists()` and nothing else. At PR 2 one of the two is
wrong: either `make plants` keeps saying "not in the tree yet" about a
reader that exists, or the tests import a module that does not. Ledger row
2's "Expected gate output" cites `make plants`. Engineering, PR 2.

**FINDING 4 — `test_s4_the_owner_was_refused` reads keys the run file never
names.** `tests/test_m02_seeds.py` lines 118-122 read
`observed[0]["message_must_contain"]`, `observed[0]["message"]`,
`observed[1]["validate_result"]`, `observed[1]["bypass_actors_after"]`.
`milestones/M02/runs/f2_1_bypass.yaml` lines 22-23 say an observed entry
carries "what, at, and the fields its attempt names"; attempt 1 names
`message_must_contain` (an expectation, listed under `attempts`, not an
observation) and attempt 2 names only prose under `record:`. The human
filling `observed` has no key list, and a missing key is a `KeyError`, not
a refusal with a reason. Take `message_must_contain` from
`run["attempts"][0]`, and list the observed keys in the run file's header.
Engineering, PR 2.

**FINDING 5 — a human-written file feeds the first half of `checks.F2_1`.**
`f2_1_bypass.yaml` line 8: "A human-written file feeds no check by
itself." SPEC/02 §4 "Where each check comes from": `F2_1`'s first source is
"the junit result of the tests in `tests/test_m02_seeds.py`", and
`test_s4_the_owner_was_refused` passes on whatever `observed:` the human
types (`result: refused`, `validate_result: RED`,
`bypass_actors_after: []`) with no comparison to the API. The second source
(`observe_pr.py`, PR 3) is the real witness, and `F2_1` "passes only if
both do", so the design holds; but the sentence in the run file is false
about this test, and a reader of the junit alone would be misled. Either
the S4 test stops reading `observed` and only holds the export's
`bypass_actors: []`, or the run file says the test is a weaker witness.
Engineering and Product, PR 2.

### 6. Claims in prose

None of "governed", "secure", "proven" appears in the diff in the
affirmative; the two uses (`infra/bootstrap/README.md` line 143,
`docs/milestones/M02.md` line 78) are negations.

**NOTE 1** — `docs/milestones/M02.md` lines 9-19 ("Why it matters") are in
the present tense about controls that do not exist at HEAD: "makes the
platform refuse a change", "the repository is set so that nobody can, and
the platform checks that setting every time" — `validate` reads no ruleset
yet (ledger header, M02 PR 1 row). "For the business user" hedges (line
70-71); "Why it matters" does not. Future tense costs a word. Product.

### 7. Notes

**NOTE 2** — `tests/test_m02_seeds.py` lines 44-49: `trees.append(tree)`
runs after `git apply`; a failed apply (the re-plant case SPEC/02 §5 names)
leaves the worktree registered under `.git/worktrees/` until `git worktree
prune`. Append before apply.

**NOTE 3** — `.gitattributes` `-text` for the patches (`4306786`) landed
after S1's two patches (`6ff333a`). Harmless here (`git ls-files --eol`
shows `i/lf` for both), recorded because on a CRLF checkout the order
would have mattered.

**NOTE 4** — SPEC/00 §5's Security row now names `.github/CODEOWNERS`
(ADR-0003 amendment 2); CLAUDE.md's "Seats and paths" Security row does not.
CLAUDE.md line 6 says it gets a PR when the two disagree. Product.

**NOTE 5** — Verified and found as stated: `infra/bootstrap/README.md`'s
`AWS_DEPLOY_ROLE_ARN` is what `.github/workflows/deploy.yml` line 142
reads; `f1_3_key_policy.yaml`'s new lines are a comment and the file's
only readers (`tests/test_m01_seeds.py` line 86,
`.github/workflows/evals.yml` line 242) read fields, not bytes;
`ADR-0003` amendment 2 is its last and `ADR-0006` amendment 1 its first,
both within the two-amendment cap; `tests/test_p5_disagree.py` exists.

BLOCK: 0 · FINDING: 5 · NOTE: 5

## To falsify the repairs

```
git diff 8e2b0a3...HEAD --stat        # the repair commits and nothing else
grep -n "covers itself" SPEC/02-seats-and-change-gates.md
grep -n "with one key" SPEC/00-overview.md
grep -n "from src.validate import" tests/test_m02_seeds.py   # edges, golden_ids
uv run pytest tests/test_m02_seeds.py -q   # 6 xfailed
```
