# M02 feasibility note

Milestone M02, claim 2: *Seat-owned files change only with a ruling;
relaxations need two keys.* SPEC/02 is `SPEC/02-seats-and-change-gates.md`.
Opened at M02 PR 1 (#11), 2026-09-22, through `/open-milestone`.

This note names the commit and inputs that make the claim false (§3), the
code that reads the answer (§4), the falsifiers (§5), and what happened to
every item M01 carried in (`milestones/M02/open.md`, §6).

## 1. `product-spec-reviewer` report (pasted verbatim, 2026-09-22)

Run against SPEC/02 as first drafted, before anything else in PR 1 was
written. SPEC/02 was revised once afterwards, on the rulings in §2; the
report is of the first draft and is not edited to match.

---

Review of `C:\Users\andar\code\agentkeel\SPEC\02-seats-and-change-gates.md` (uncommitted draft, branch m02-pr1) for M02 PR 1. Also read: SPEC/00 §4, §5, §5.1, §6, §7 row 2, §8 M02, §10.3 row 02, §11; `milestones/README.md`; `milestones/M02/open.md`; and the files SPEC/02 names (`thresholds.yaml`, `g-005`, `g-010`, `g-012`, `tests/fixtures/README.md`, `infra/ruleset/main.json`, `agents/refagent/manifest.yaml`, ADR-0003 front matter, `src/manifest/schema.json`). No `milestones/M02/README.md` exists yet.

Facts checked against the tree: `cost_cap.tokens_per_run` is 150000 (S1 matches). `g-010` has `available: false`, `constraints: [holdback]` and passed in agent history at M01 (S2's "id with a pass in history" holds). `g-005` exists, no `g-099` exists (S5 holds). `agents/ratings-helper/` does not exist; refagent's manifest has `may_call: []` (S3 holds). Nothing under `src/` or `scripts/` reads `may_call`, `CODEOWNERS` or `bypass_actors`; the manifest schema checks shape only (§3's "nothing in the repo would stop any of them" holds for S1–S5). No `.github/CODEOWNERS`. ADR-0003 has one amendment, so "amendment 2" is available and is its last. SPEC/02 uses none of "governed", "secure", "proven".

---

**1. BLOCK — check 1, false state.** §1: "**no seat-owned path on `main` changed without a file that names the seat, the path and the PR, and no relaxation changed without two such files from two seats.**" §3.1 names the false state for the second half: "and no ruling on `main` with `pr:` equal to that PR covers `thresholds.yaml`, or only one does." §5 S1 plants only the first: "`cost_cap.tokens_per_run` 150000 → 300000, nothing else". A seed with zero rulings is refused by `ruling-cited` and by any `two-key` that counts "at least one", so nothing planted distinguishes `two-key` from `ruling-cited`, and neither "one key" nor "two files, same seat" has a plantable false state in PR 1. M01 closed RED on the unseeded second half of its claim. Settle: Product rules whether S1 (or a sixth seed) also carries one Threshold Owner ruling with the seed PR's `pr:`, so the refusal can only come from `two-key`.

**2. FINDING — checks 2 and 3, reader for Door 2.** §5.1: "Door 2 is PR 3 itself" and "`F2_2` is read by PR 3's run from `f2_2_three_doors.yaml`"; §4 F2.2 needs "a merge with two rulings on `main`". PR 3's run cannot observe PR 3's own merge; if PR 3 is the close, no PR reads it, and if PR 4 reads it, F2.2 is measured in the last PR against P3 ("never the last PR"). Settle: Product rules whether Door 2's record is "`two-key` green on the PR with two rulings in the merge ref", read on PR 3, or its merge, read by PR 4 with the cap then fixed at four.

**3. FINDING — check 3, Door 3 observation.** §4 F2.2: "the GitHub API's record of each does not show, respectively, ... a merge refused to the owner with `bypass_actors` `[]` at that time"; §4: "A human-written file feeds no check by itself; the check is the CI lookup of the PR number." A refused `gh pr merge --admin` leaves nothing on the PR's record; the lookup can show S1's PR is unmerged, not that the owner tried and was refused, so Door 3 rests on "the response text is kept as the human's own output" (§5.1), which is the vacuous shape open.md row 17 names. Settle: Security names the API record (rule-suites or audit log) that shows the refused attempt, or §4 says F2.2 Door 3 is witnessed by the human's output alone.

**4. FINDING — check 4, expected output on the seed PRs.** §5.1: "each from a branch off PR 2's head so that the merge ref carries the gate workflow, each targeting `main`. Each is expected to show the required check red". Such a PR's diff against `main` is all of PR 2 plus the seed, and PR 2's rulings carry PR 2's `pr:`, so `ruling-cited` is red on every PR 2 path whether or not it sees the seed; "red" is then not the expected number for the seed. Settle: Product, with Security, states what `observe_pr.py` reads to show the seed's path is among the listed uncovered paths, or moves the seed PRs to after PR 2 merges.

**5. FINDING — check 5, plain sentence.** SPEC/00 §10.3 row 02: "changes only when the person who owns it says so, and loosening one needs two owners." §1: "It does not stop one person from writing both files: R1 says every seat is one person". A director reads "two owners" as two people; the control fires on two files one person writes. Settle: Product rewrites the sentence (SPEC/00 amendment) or the explainer's "For the business user" says one person holds every seat at M02.

**6. FINDING — check 6, cut list.** §9 row 5 cuts "`scripts/observe_pr.py` for the seed PRs; the human's run files then feed `F2_1` from junit alone" while §5 lists S4's reader as "`scripts/observe_pr.py`" and §9 says "None cuts a seeded case." Cutting item 5 leaves S4 with no reader; and §4's "the five tests in `tests/test_m02_seeds.py`, each of which applies its seed to a copy of the tree" cannot include S4, which §7 confirms ("S1, S2, S3 and S5 each refused"), so S4's test is unstated. Settle: Product removes row 5 from the cut list or names S4's junit reader.

**7. FINDING — check 7, seat.** §2: "made machine-readable at M02 as `.github/CODEOWNERS` (Security, ADR-0003 amendment 2)". `.github/CODEOWNERS` matches no row of SPEC/00 §5 (Security holds `.github/workflows/**`), and §5 says "A file no seat owns is deleted"; an ADR names a seat for a rule change, it does not add a path to §5's table. Settle: Product amends §5's Security row for `.github/CODEOWNERS`, noting ADR-0003 amendment 2 is that ADR's last.

**8. FINDING — check 8, "on `main`".** SPEC/00 §5: "`ruling-cited` — a PR touching a seat-owned path cites a ruling on `main`"; R9: "No PR in this repo merges before its ruling file is on `main`." SPEC/02 §1: "`ruling-cited` and `two-key` read the PR's merge ref: a ruling the PR carries counts". SPEC/02 rules open.md row 1 by reinterpreting SPEC/00's wording, and SPEC/00 wins. Settle: Product amends §5 and R9 to say "in the merge ref" (an ADR), or SPEC/02 §1 stands and R9 is false as written.

**9. FINDING — check 8, open.md row 21.** open.md row 21: "Which seat `two-key` counts for Engineering's key (#7 Unsure 4). | Product | M02 PR 1". §2 "Two keys": "Two ruling files, each with one `seat:`, the two seats distinct" does not answer it, and `thresholds.yaml`'s header cites "Engineering in `milestones/M01/rulings/pr1.md` (ruling B)" as a key already counted. Settle: Product rules in §2 whether Engineering's file counts as a key on a Threshold Owner path.

**10. NOTE — check 8, contradiction resolved by SPEC/02.** open.md row 3: "Retire `g-012` ... | Data Owner | M02 PR 1" vs §5.1: "It is M02 PR 3, whether PR 3 is the repair or the close." SPEC/02 rules; recorded because it is the second named P3 exception in two milestones and it feeds finding 2.

**11. NOTE — check 8, `ratings-helper`.** SPEC/00 §8 M01: "`ratings-helper` stub as the second tenant so the edge exists"; CLAUDE.md lists `agents/ratings-helper/`; the tree has neither. SPEC/02 §5 S3 ("no `agents/ratings-helper/` exists") is right and §6 builds it at PR 2; SPEC/00 §8 M01 and CLAUDE.md say it was M01's. Product owns both; a line in feasibility.md that M01 did not build it settles it.

**12. NOTE — check 8, ledger header.** §3: "nothing in the repo would stop any of them"; SPEC/00 §5: "the header of `milestones/README.md` lists what it checked at each tag". The header's last row is "M01 PR 1 (no tag)"; nothing records what `validate` checked at M01 PR 2, PR 3 or `m01`, so §3's line is checked against the tree, not the header. Product adds the missing rows, or §6's "Ledger header: M02 PR 2 adds its row" states what it inherits.

**13. NOTE — check 2, P5.** §4: "`verdict.gate` re-reads the junit file and the run file and rejects a disagreement." P5: "the gate reads the envelope." A gate that reads raw observations is a gate that reads instruments; Engineering's test that "the three can disagree" should be the disagreement check, not the gate. Product rules whether §4's sentence stands.

**14. NOTE — check 8, two smaller disagreements.** SPEC/00 §8 M02 F2.2: "Door 3 blocked by two gates" vs §4 F2.2's one gate, "refused to the owner with `bypass_actors` `[]`". SPEC/00 §8 M02 build: "workflow-hash check in `validate`" landed at M01 PR 1 (ledger header); §6 omits it and open.md row 7's fix ("`ruling-cited` on `infra/**` closes the first") is stated nowhere in SPEC/02. Product.

**15. NOTE — check 6, cap.** open.md dates twelve rows to "M02 PR 1" (rows 9–18, 20–22) including the failed deploy fix (row 9), the eval-role stack removal (row 16) and the first LFS object (row 14); SPEC/02 names rows 1, 3, 4, 17 and 20 only. Any of the rest that needs a fix PR of its own spends the cap before PR 2. Product decides which of them PR 1 carries and records the rest in feasibility.md.

BLOCK: 1 · FINDING: 8 · NOTE: 6

---

## 2. Rulings

Drafted by the session for the seats named; the human rules (R1) before
this PR merges, and a ruling the human changes is changed here and in
SPEC/02 before the merge, not after.

### 2.1 The BLOCK, ruled before any seed was committed

**BLOCK 1 — Product.** Ruled as the reviewer proposed. S1 carries
exactly one ruling file, `seat: Threshold Owner`, covering
`thresholds.yaml`, so `ruling-cited` is satisfied and only `two-key` can
refuse it. A second form of S1 carries two files from that one seat, so
`two-key` must count seats and not files. Both are in `6ff333a`, and
`tests/fixtures/README.md` says the files exist only in the patches and
on the seed branches. The reviewer's reading of M01 is right: the half
of the claim that costs the most to get wrong is the one that most needs
its own seed.

### 2.2 The FINDINGs

| # | Seat | Ruling |
|---|---|---|
| 2 | Product | Door 2 is **PR 2's own merge**: PR 2 retires `g-012` with two files, Data Owner and Threshold Owner, and adds `g-021`; `two-key` runs on PR 2's merge ref and reads it. Door 2's record is that check run's success on PR 2's head sha plus the merge commit carrying both files, read by PR 3's run from `f2_2_three_doors.yaml`. Not PR 4: the cap stays four with none spent on a demonstration, and nothing is first read in the last PR. The gate reading its own PR is the shape M01 PR 2 used for `verify` on the bundle that PR signed; the seeds in the same run are what show the gate can also refuse. SPEC/02 §5.1. Open.md rows 3 and 4 move to PR 2. |
| 3 | Security (draft) | `observe_pr.py` looks for the refused evaluation in the rule-suites API, by actor, ref and time. Whether that API records a refused `--admin` merge is read at the attempt and not assumed. If it does not, Door 3 rests on the PR's unmerged state and the human's own output, and this note's §7 and the ruling file say so as a weaker witness. Door 3 is two gates (note 14): attempt 2, the ruleset edit, is read by `validate` and needs no API record of the attempt itself, only of the ruleset's `updated_at`. SPEC/02 §4, §5.1; `f2_1_bypass.yaml`. |
| 4 | Product, with Security | The seed PRs are opened **from `main` after PR 2 merges**, before PR 3's first CI run, and read by PR 3's run. A PR off PR 2's head would carry PR 2's diff and be red on PR 2's paths whatever it saw. This is the named P3 exception, as ADR-0007 named M01's: a PR refused by a gate on `main` cannot exist before the gate is on `main`. SPEC/02 §5.1. The risk is named in `milestones/M02/README.md`: if PR 3 is the close, the reading rides in the close, which is how M01 went RED. |
| 5 | Product | The §10.3 sentence stands; SPEC/00 §5 R1 already says every seat is one person. The explainer's "Why it matters" and "For the business user" say, in plain words, that at M02 one person holds every seat and "two owners" is two rulings one person can write. `docs/milestones/M02.md`. |
| 6 | Product | Row 5 removed from the cut list; `observe_pr.py` is never-cut as S4's reader. S4's test is `test_s4_the_owner_was_refused`: it reads `f2_1_bypass.yaml` and requires `bypass_actors: []` in the export. SPEC/02 §5, §9. |
| 7 | Product, for Security | SPEC/00 §5's Security row now names `.github/CODEOWNERS`, by ADR-0003 amendment 2, that ADR's last. `bc35c39`. |
| 8 | Product, for Security | ADR-0008: a ruling is on `main` at the merge commit; `cold-review-ruling`, `ruling-cited` and `two-key` read the merge ref. SPEC/00 §5's `ruling-cited` line and R9's last sentence are amended to say so, and the old wording is quoted in place. `bc35c39`. Open.md row 1 closes on it. |
| 9 | Product | Engineering's file counts as a key like any other seat's. R1 makes any two seats one person; excluding Engineering would make the seat with the most files the one that can never say yes, and buy nothing. M01 PR 1's two keys stand. SPEC/02 §2. Open.md row 21 closes. |

### 2.3 The NOTEs

| # | Seat | What was done |
|---|---|---|
| 10 | Product | Rows 3 and 4 move to PR 2 (finding 2). Recorded in §6. |
| 11 | Product | M01 did not build `ratings-helper`: SPEC/01 §10 cut it at open (ruling SCOPE). SPEC/00 §8 M01's line and CLAUDE.md's tree said it was M01's; CLAUDE.md's tree now says "manifest-only stub from M02 PR 2 (cut from M01 at open); code at M07". SPEC/00 §8 M01 is left as written, dated by SPEC/01 §10; a §8 edit to a closed milestone's entry is not made. |
| 12 | Product | Three header rows added to `milestones/README.md`: M01 PR 2, `m01`, M02 PR 1. `validate` grew only at M01 PR 2 (`git log m01 -- src/validate`). |
| 13 | Product | §4 rewritten: `verdict.gate` reads the envelope and nothing else; `build` writes `checks.F2_1` and `F2_2` from the junit file and the observation files as it writes `checks.F1_1`; `tests/test_p5_disagree.py` holds that they can disagree. |
| 14 | Product | F2.2 Door 3 now says two gates. SPEC/02 §6 says `ruling-cited` on `.github/workflows/**` and `infra/**` needs a Security ruling covering a workflow and its hash together (row 7's first half); §8 and §10 say the second half, hashing what a workflow runs, is M05's. |
| 15 | Product | §6 below. PR 1 carries rows 1, 2, 8, 9, 14 (with 2), 17, 21, 22; the rest are re-dated with a seat. |

### 2.4 Rulings for M02 PR 2 open

Named in `milestones/M02/README.md`, "For the seats, at M02 PR 2 open".
Each is a decision a seat makes before PR 2's first commit; none is made
here.

## 3. The false state

SPEC/02 §3, with the commit that plants each:

| Seed | Commit | What is on the branch |
|---|---|---|
| S1 one key | `6ff333a` | `tests/fixtures/m02/s1-one-key.patch`: `cost_cap.tokens_per_run` 150000 → 300000 and one Threshold Owner ruling file with `pr: 0` |
| S1 two files, one seat | `6ff333a` | `s1-two-files-one-seat.patch`: the same, plus a second Threshold Owner file |
| S2 | `74a38be` | `s2-golden-greened.patch`: `g-010`'s `available` true, `constraints` empty; no ruling |
| S3 | `d8fbdb1` | `s3-one-sided-edge.patch`: `may_call: [ratings-helper@v1]`; no callee; no ruling |
| S4 | `9eb539c` | `milestones/M02/runs/f2_1_bypass.yaml`, `observed: null`; with `f2_1_seed_prs.yaml` and `f2_2_three_doors.yaml`, `observed: null` |
| S5 | `479abb9` | `s5-golden-renamed.patch`: `g-005.yaml` → `g-099.yaml`, id changed, `retired` untouched; no ruling |

`git show <commit> --stat` shows the seed, its test, and no reader. At
`479abb9`, `uv run pytest tests/test_m02_seeds.py` gives 6 xfailed.
Nothing in the tree at PR 1 would refuse any of the five on a real PR:
`cold-review-ruling` reads no path, `validate` reads no diff and no
ruleset, `evals` reads goldens as they are.

## 4. The code that reads the answer

SPEC/02 §6, all PR 2: `.github/CODEOWNERS`; `src/gates/ruling_cited.py`
and `two_key.py` under `gates.yml` as required checks; `validate`'s edge,
cycle, ceiling, login, golden-id and live-ruleset checks; computed
semver; the `ratings-helper` manifest stub; `scripts/observe_pr.py`.
None is in PR 1. `make plants` says "not in the tree yet" beside each.

## 5. Falsifiers, and what each would look like in the repo

SPEC/02 §4. F2.1: a seeded change's merge commit on `main`, or
`checks.F2_1: fail`, or a run file recording anything but the expected
refusal. F2.2: the three doors' PR numbers in `f2_2_three_doors.yaml`
whose API records do not show a refusal naming the seed's path, a merge
with two files from two seats, and the owner refused with `bypass_actors`
`[]` and `validate` RED on the ruleset that would have allowed it.

## 6. What M01 carried in (`milestones/M02/open.md`), row by row

Every row is answered here or moved on with a seat and a date. None is
dropped. Rows 9, 2 and 8 were the three the human named for this PR, in
that order.

| # | Seat | Now |
|---|---|---|
| 1 | Security | **Ruled: ADR-0008.** The gates read the merge ref; a ruling is on `main` at the merge commit. SPEC/00 §5 and R9 amended. Closed. |
| 2 | Product | **This PR, when the recording is given.** No file matching a recording made since tag `m01` was found on this machine (Captures, Screen Recordings, Downloads, Desktop, Documents). `.gitattributes` already tracks `docs/video/**/*.mp4` as LFS; the row in `docs/video/README.md` is written when the file's length is known. If it is not in this PR when it merges, it is re-dated to PR 2 and is a finding about this project (ADR-0005 §3). |
| 3 | Data Owner | **Moved to PR 2** as Door 2 (finding 2): `g-012` retired with two files, Data Owner and Threshold Owner, both `pr: 12`. A retirement in PR 1 would merge through no gate and show nothing. |
| 4 | Data Owner, Threshold Owner | **Moved to PR 2** with row 3: `g-021`, `sequel_no_inherit`, never passed by the control (P7). |
| 5 | Security | **PR 2**: it is a reader (S4's second gate, `validate`'s live-vs-export diff with `bypass_actors: []`). Whether `GITHUB_TOKEN` on a PR run can read the ruleset is Security's at PR 2 open. |
| 6 | Engineering | **PR 2**: `two-key`'s human-commit-under-`evals/history/**` case makes "CI-written" a gate. No seeded case at M02 (SPEC/02 §8). |
| 7 | Security | **PR 2** for the first half: `ruling-cited` on `.github/workflows/**` and `infra/**` covers a workflow and its hash edited together. **M05** for the second half, hashing what a workflow runs (SPEC/02 §10). |
| 8 | Product | **Done**, `a3db944`: the cold-review skill requires the caller to hand each seat subagent the diff as a file and each report to open with "Read: the diff …" or "Read: the tree …"; a tree report is a weaker witness. Nothing mechanical reads the line. |
| 9 | Security | **Done**, `25b2743` (the test, failing on the table for `kms:CreateGrant`) then `9ea6405` (`TableEncryption.DEFAULT`; README step 3 sets `AWS_DEPLOY_ROLE_ARN`; the README's last section says what has been deployed). The rendered template differs from `main` by one line. This PR's merge is the next deploy; the human reads the diff first and runs it. M01 row 1 stays RED. |
| 10 | Security | **PR 2**, read from the deploy that this PR's merge triggers: image pull through the runtime's interface; cfn-exec's `vpc-lattice` actions from CloudTrail; the load check's answer. |
| 11 | Security, with Engineering | **PR 2** for the fork-PR half: `gates.yml` must run on a fork PR with no secrets, and a fork PR with no envelope is a `ruling-cited` question. **M05 open** for the rest, which are evidence-integrity items (the envelope by the PR's own code, bytes changing mid-run, the image not reproducible): M05 is the milestone whose claim is that the evidence is complete. |
| 12 | Engineering | **PR 2**, with `scripts/observe_pr.py`, which is the same family as `observe_attempt.py`: the refusing `principal` read first, then agent raw replayable, `both()`, `message_must_contain`, `thresholds_at`'s fallback. |
| 13 | Engineering | **PR 2**, as small commits the cold review can see one by one. |
| 14 | Engineering | The LFS object: with row 2. The `infra` default group: **closed**; `pyproject.toml` already carries it with its reason, and the install cost in jobs that do not synth is accepted until a job's time shows it matters. |
| 15 | Security | **M05 open**, all of it: each item is a containment or evidence item, and M05 is that milestone. Security may pull any into PR 2; none is a reader of claim 2. |
| 16 | Security | **PR 2**: `gates.yml` is a second workflow file, so `workflow-hash` refusing it unlisted is observed on PR 2's first run and recorded. `infra/eval-role/` is removed in PR 2 after the human runs `npx aws-cdk@2 destroy` on `AgentkeelM00EvalRole`; this PR does not delete a directory whose stack may still exist. |
| 17 | Security, with Product | **Ruled in SPEC/02 §5.1**: the human's own output is kept in every M02 run file (`f2_1_bypass.yaml` says so), and `observe_pr.py` is run once at PR 2 against a known record (PR #10) before a run depends on it. |
| 18 | Threshold Owner | **PR 2**, all six, with the `relaxes:` field PR 2 adds to every bar. Drafts for the seat: Nova Micro stays the control (ADR-0002 froze it; fairness is a property of the delta, not of the control); the cap stays 150,000 until refagent grows a knowledge base at M03 (54,156 measured, and a move now would re-plant S1); USD 300 monthly stands; `check_model_access` stdout committed under `runs/` at PR 2; one cap for two run shapes stands as ruled m; `max_tokens_per_session` and `daily_usd` ruled at PR 2, and `daily_usd` renamed in the manifest schema to stop the collision. |
| 19 | Threshold Owner | **M04 PR 1**, as dated. |
| 20 | Tool Owner | **PR 2**, with the `ratings-helper` manifest stub and computed semver (SPEC/02 §6): semver computed, the not-found branch, nested `row`, `pinned_roles`, `territory` and `platform` typing. |
| 21 | Product | **Ruled in SPEC/02 §2**: Engineering's file counts as a key. Closed. |
| 22 | Product | **Done**, `a3db944`: ADR-0006 amendment 1 (seven names); a comment beside S6's `command:` says KMS refuses the alias form and the attempt used the key id; the observation is untouched. |
| 23 | Security | **M05 open**, as dated. |

## 7. What PR 1 does not do

- It builds no reader: no `src/gates/`, no CODEOWNERS, no `validate`
  growth, no `observe_pr.py`. `make plants` says so.
- It does not retire `g-012` or add `g-021` (PR 2, Door 2).
- It does not make any check required on the `main` ruleset, and it
  does not export the ruleset.
- It does not delete `infra/eval-role/` (PR 2, after the destroy).
- It does not move any bar: `thresholds.yaml` is untouched, so S1's
  patch applies at PR 2.
- It carries no envelope of its own making: this PR's run writes
  refagent's envelope in runner mode through `evals.yml`, as at M01.
- It does not measure claim 2. Door 3's API record is not known to
  exist until the attempt (finding 3), and this note says so.
