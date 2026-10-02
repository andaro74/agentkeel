# M07 feasibility

Written at M07 PR 1, the plant (`/open-milestone M07`). SPEC/07 was
drafted first (`83eb558`) and `product-spec-reviewer` run on it before
anything else of PR 1 was written, but for M06's video (`1d18c2d`,
`open.md` row 1) and row 20's environment read
(`runs/platform_app_environment.json`,
`runs/platform_app_branch_policies.json`, read 2026-10-02T02:12Z, which is
2026-10-01 in the session's own time zone).

The claim, and what makes it false today: an agent takes a platform,
model or retirement upgrade without a workflow edit. On `main` at
`57b9bf6` there is no agent from the template to upgrade
(`scripts/platform_check.py` `POST_PERMISSIONS` asks Administration: read,
so `src/validate/agent.py` refuses every head: owner-check #1 at
`0c596c1`, #2 at `e3a8083`), and nothing in the tree opens an upgrade,
retires an agent or reads a rollback.

## 1. `product-spec-reviewer` report (verbatim)

On SPEC/07 at `83eb558`. A report, never a ruling.

Read: the tree at 83eb558, SPEC/07 and the sections named

Also read, because a judged line depends on them: `scripts/platform_check.py`, `src/verdict/template.py`, `src/verdict/plants.py`, `.github/workflows/deploy.yml`, the triggers of `evals.yml` and `cold-review-ruling.yml`, `milestones/M06/runs/f6_0_owner_test.yaml`, `f6_2_standin.yaml`, `f6_3_quickstart.yaml`, `milestones/M06/rulings/pr4.md` (Unsure B), `milestones/M07/runs/platform_app_environment.json` and `platform_app_branch_policies.json`, SPEC/06 §2, §5 to §10, and the file list of `evals/history/`. Not read: `scripts/runtime_for_tree.py`, `scripts/registry.py`, `scripts/make_template.py` beyond its `platform_version` line, `src/validate/agent.py` beyond `ruleset_errors`. Three points below rest on GitHub behaviour I could not check from the repo; each says so.

### Check 1. False state

**1. BLOCK. A retirement never arrives as a pull request.**
§1: "**'Takes an upgrade' means all four of these, and nothing less.** ... 1. **Arrives as a pull request.**" and "`upgrade.taken`: how many of the three seeded upgrades arrived as a pull request the platform opened". §5 S2: "`owner-check` archived by its owner". SPEC/00 §10.3 row 07: "a retirement arrives as a PR".
Wrong: both retirement triggers (archive, `deprecated_after` passed) have no pull request, so clauses 1 and 2 have no state to read for that kind, and "3 of 3" cannot be reached as defined.
Settle: Product rules either that retirement is exempt from clauses 1 and 2, with the §10.3 sentence reworded (a sixth SPEC/00 amendment), or that a retirement is carried by a pull request somewhere.

**2. BLOCK. The model upgrade needs a person's commit by this repo's own gates.**
§2: "**A person's edit.** A commit on an upgrade pull request whose author is not the platform's App". §6 model-watch: "the pull request carries the ruling the gate asks for, drafted, for the seat to rule".
Wrong: `cold-review-ruling.yml` (lines 52 to 54) refuses a ruling without the seat's "Ruled by" line, and `ruling-cited` needs a ruling with that PR's number, so a model-watch pull request in `agentkeel` cannot merge without a human commit on it, and F7.1 fires on S3 by construction.
Settle: Product rules whether a ruling file is excluded from "a person's edit" (and says so in §2 and F7.1), or accepts that the model kind cannot count toward `taken`.

**3. FINDING. S4's false state names an envelope that is not on `main`.**
§5 S4: "the envelope `evals/history/133959f….json` on `main`, RED".
Wrong: no file under `evals/history/` starts `133959f`; it is the breaking swap's first envelope on an unmerged branch (`milestones/M04/runs/f4_swaps.yaml` line 29).
Settle: Product names a RED envelope that is in `evals/history/` (seven files there carry RED or UNMEASURED, e.g. `05bd718…`) before S4's commit.

**4. FINDING. F7.2's "still answers" arm cannot fire live.**
§2 Retired: "'Still answers' (F7.2) means an answer record for the agent under `envelopes/agents/<name>/` with `LastModified` after `retired_at`".
Wrong: answer records are written only by `deploy.yml`'s `deploy-agent` at deploy time, and `platform_check.repositories()` skips an archived repository, so a retired runtime that answers a caller writes no such record; only the fixture can show it.
Settle: Product rules whether S2 gains one invocation of the runtime ARN after `retired_at`, expected `ResourceNotFoundException`; Security names who makes the call.

**5. FINDING. S1's bump may be one string, and "older" has no ordering.**
§1 Platform: "Every agent whose `platform_version` is older gets a draft pull request"; §2: "writes the tag when `HEAD` carries one and the short commit otherwise".
Wrong: PR 2's merge carries no tag, so the seeded bump is `m06` to a short sha, with no stated rule for which is older and no stated expectation of whether any other platform-owned file changes.
Settle: Engineering states the ordering (ancestry in `agentkeel`) and Product states before the run which files S1's diff is expected to touch.

**6. FINDING. The seeded refusal from a branch has no run file and no falsifier arm.**
§5.1 PR 2's run: "`platform-check.yml` dispatched from a branch, its `post` job refused by the environment, read by the workflow-run record".
Wrong: §5 plants no run file for this attempt, F7.0's row in §4 does not name it, and `observe_upgrade.py` reads only "each run file under `milestones/M07/runs/` with an `observed` entry".
Settle: Security rules whether it is a second attempt in `runs/f7_0_owner_test.yaml` or its own file, planted in PR 1.

**7. NOTE. S0 to S3 and S5 are plantable in PR 1 without their readers.**
Each fixture fails today on a missing module, subcommand or function. S1's attempt file cannot name "the timed run's repository" at PR 1: `f6_3_quickstart.yaml` has `agent_name: null`.

### Check 2. Reader

No line lets an observer write a verdict. No P5 BLOCK. The findings are about where the reader runs and whose clock it reads.

**8. FINDING. The reader of every live observation is unruled at PR 1.**
§11 R4: "Whether the observer on `main` can run from a job that checks out `main` only ... or needs a workflow of its own"; §7: "S2 of SPEC/06 as at M06, `blocked` from the App's viewpoint"; §5.1: "PR 4 is the close, whose run reads every attempt".
Wrong: §6 gives a pull request's run the anonymous viewpoint, so PR 4's own run cannot produce the App-viewpoint reading §7 expects; the run files with `observed` filled sit on a branch while the App-viewpoint observer runs `main`'s code.
Settle: Security and Engineering rule R4 before PR 1's ledger row is written, and the row says which run's envelope the Measured cell cites.

**9. FINDING. The retirement job writes the clock F7.2 is read against.**
§2 table, retirement: "`DeleteAgentRuntime` in CloudTrail (`eventTime`) and `retired_at` on the registry row"; §1: "every time GitHub's or AWS's".
Wrong: `retired_at` is a runner's clock written by the instrument (`template.py` says the same of `deployed_at`), and F7.2's two one-hour arms and the "after `retired_at`" arm are measured from it; the platform trigger's `committer.date` is the pusher's clock when the owner pushes the template by hand.
Settle: Engineering rules that `build.f7_2` times from CloudTrail's `eventTime` and the platform trigger from GitHub's push record.

**10. FINDING. S0's, S1's, S2's and S3's fixture tests feed no check.**
§4: "`CLAIM_7_CHECKS` in the gate is `F7_4`, `F7_5`."
Wrong: the readers for the S0 bounds, `platform_upgrade.py diff`, `build.f7_2` and `build.f7_3` land in PR 2, but nothing on the envelope carries their witness, so "the plant must go RED" for four of six seeds is a pytest result only.
Settle: Engineering rules whether `F7_0` to `F7_3` get test-only witnesses in `checks`, as `F6_1` did.

**11. FINDING. "PR 2's run, on the PR" cannot read the live grant.**
§5.1: "PR 2's run, on the PR. ... the permissions reader reading the grant as ruled"; §5: "the live installation is read with the App's JWT, which no test holds".
Wrong: the key is in the `platform-app` environment, `main` only, so the PR's run cannot read the installation; the two lines disagree.
Settle: Security rules that the first live read is `platform-check.yml`'s `post` on `main` after PR 2 merges, and §5.1 says so.

### Check 3. Falsifiers

**12. FINDING. Re-reading S2 "not remade" cannot answer open.md row 5.**
§5.1 step 2: "SPEC/06's S2 read again (... owner-check pull request 2, head `e3a8083`), with the viewpoint recorded; not remade".
Wrong: `platform_check.find` (line 100) skips a head that already has a check run from the App, so `e3a8083` keeps M06's failure with the `bypass_actors` reason; the App never refuses it "on S2's own null seats" (`rulings/pr4.md`, Unsure B).
Settle: Product rules whether S2 gets a new head or is read as the old check run plus a new viewpoint, and says which in §7.

**13. FINDING. Step 1 may turn S2's state from "blocked" to "behind".**
§5.1 order: step 1 merges owner-check pull request 1, then step 2 reads pull request 2.
Wrong: the agent ruleset requires branches up to date; after step 1's merge pull request 2 is behind `main`, and `template.f6_2` holds on `blocked` alone ("`dirty`, `behind` or `draft` block for another reason"). Which state GitHub reports when a check fails and the branch is behind I could not verify.
Settle: Engineering reads it on a scratch repository before the order is fixed; Product rules whether S2 is read before step 1's merge.

**14. FINDING. F7.0 folds claim 6's bar into claim 7.**
§10 amendment 2: "(the owner's test's fixed head refused or not live, or SPEC/06's S3 unread or over its bar)".
Wrong: a quickstart at 9 hours leaves an agent that exists and can be upgraded, yet fires F7.0 and turns row 7 RED; and no line says where claim 6's measured time is recorded now that row 6's cell is closed on `245eb9b`.
Settle: Product rules whether F7.0 reads "exists" (merged, deployed, listed) only, and which cell carries F6.3's elapsed time.

**15. FINDING. Three one-hour limits and a schedule period are bars outside `thresholds.yaml`.**
§4: "within one schedule period plus an hour"; "an hour after"; "not deployed within an hour". §6: "**The bar.** None added."
Wrong: each turns a falsifier, none has a `relaxes:` direction or two keys, and the schedule period of `platform-upgrade.yml` is not stated as a number.
Settle: Threshold Owner rules whether they enter `thresholds.yaml`; Security states the cron.

**16. FINDING. The rollback is unread unless a candidate rules GREEN, and none is known to.**
§7: "its envelope GREEN and merged, else recorded RED and the rollback unread".
Wrong: the only equivalent candidate measured so far went RED on `g-005` (open.md row 67) and Haiku 4.5 was never run (row 66), so F7.3 and `taken` 2 of 3 rest on R6's unmade choice; the revert is itself a pin move the M04 gate rules, and row 58 (first envelope after a merged swap fails `F4_4`) is not addressed.
Settle: Threshold Owner names the candidate and its evidence before S3's run file is planted; Product states the expected gate output for the revert's own pull request.

**17. FINDING. The bundle archive's source expires.**
§6 Retirement: "copy the signed archive the registry's commit was deployed from to `bundles/<name>/<commit>.tar`".
Wrong: the only copy is `deploy.yml`'s Actions artifact, `retention-days: 30`; an agent retired by a passed `deprecated_after` or flagged idle at 90 days has no archive to copy, and F7.2's "no `bundles/…tar`" arm fires.
Settle: Security rules whether the deploy puts the archive in the audit bucket at deploy time.

**18. NOTE. F7.5 has no live half.**
§4 F7.5: "live: `upgrade.surfaces.plants_expected` ... ≠ `plants_fired` (the readers that refused their fixture in the run)". This is the same JUnit count as the test-only half. §4's "the live halves of F7.4 and F7.5" overstates it.

**19. NOTE. `deprecated_after` set from Bedrock has no seeded case.**
§6: "writes `deprecated_after` from `endOfLifeTime` into a draft pull request when it differs". If refagent's pin has no end-of-life date, the seeded run writes nothing. §8 does not list it.

### Check 4. Expected gate output

**20. FINDING. PR 2's expected output omits S1, S2 and S3's fixture tests.**
§7 PR 2: "S0's three bounds read by their tests ... S4 and S5 refused by their readers".
Wrong: §5 lands S1 to S3's readers in PR 2, where a strict `xfail` whose reader exists turns the suite red, and no line says whether their markers come off at PR 2 or after the attempts.
Settle: Engineering states the expected pass and xfail counts of `tests/test_m07_seeds.py` at PR 2.

**21. FINDING. The surfaces' plant count is stated two ways.**
§5 S5: "a surfaces' plant list naming S4 of M06 and S4 of M07"; §6: "a control `surfaces` naming S4 of M06, S4 and S5 of M07"; §7: "`surfaces.plants_expected` 3 and `plants_fired` 3".
Wrong: S5 is both a counted plant and the test of the counter, and the fixture's list has two entries where the control has three.
Settle: Engineering states what "fired" means for S5 and which list gives 3.

**22. NOTE.** §7 does not say whether S1 is expected major or minor. The delta and the falsifiers are otherwise separated: `taken` 1, 2, 3 of 3 is the delta; "The row goes RED" lists the falsifiers.

### Check 5. Plain sentence

**23. FINDING (with item 1).** "a retirement arrives as a PR" is false of the design. "A new model ... arrives" needs a person to name the candidate first (§8: "`model-watch`'s candidate is named by a person"); §1's "the pull request arrives by itself" overstates that.

**24. NOTE.** "the team never edits the pipeline" is true by construction in an agent repository, which has no workflow; S1's fixture plants no workflow file, so the "touching `.github/workflows/`" arm of F7.1 has no plant. No use of "governed", "secure" or "proven" found in SPEC/07 except amendment 5's quotation of row 6.

**25. NOTE. Panel 2 will show GREEN on envelopes whose rows closed RED.**
§2 Panel 2: "returns the verdict column as stored". `245eb9b…json` stores `"verdict": "GREEN"`; row 6 is RED by the ledger's reading of `template`. F7.4 holds, and a director sees GREEN beside a RED milestone. Product rules whether `docs/platform/surfaces.md` or the panel says so.

### Check 6. Cut list and cap

**26. BLOCK. "Not built in this project" is not a cut SPEC/00 allows, and amendment 3 leaves SPEC/00 contradicting itself.**
§9 a, b, c, e: "**not built in this project**: SPEC/00 §12"; §10 amendment 3: "SPEC/00 §15's 'at least seven GREEN' ... not amended; whether they can still be met is read at M08".
Wrong, four ways:
- SPEC/00 §8 M07's cut list is three items, and §8 M06 says of the knowledge base "moving it again is an amendment here, not a cut".
- The cuts remove things M08 names: F8.5 "revoke the Gateway policy", run 1's "prompt injection aimed at the judge rubric", PR 3's "Braintrust experiments". M08 has "Zero new code paths".
- R6 (the judge of record) is a ruling in §11 and is not amended.
- Rows 1, 4, 5 and 6 are RED today, so at most five of nine can be GREEN; "read at M08" defers a number the ledger already gives.
Settle: Product rules amendment 3 together with §8 M08, R6, §9, §10.2 Act 3 and §15, or names each as a recorded contradiction, before any seed.

**27. FINDING. Cut a drops a falsifier half and a seed of M03; row 35 is unplaced.**
§9 a: "with the cached-answer seed, F3.5's second half and `g-014` as a plant".
Wrong: the list "never cuts a seeded case" in SPEC/00's sense only for M07's seeds. F3.5's second half becomes permanently unmeasured and `g-014` permanently never-passed. S5 of M05's live half (open.md row 35) appears nowhere in §9 or §10.
Settle: Product rules each as "not measured in this project" in SPEC/00 §12 by name, row 35 included.

**28. FINDING. About 30 open.md rows dated M07 are placed by a file that does not exist.**
§8: "each row has its seat and milestone in `milestones/M07/feasibility.md` §6".
Wrong: rows 9, 10, 12 to 19, 21, 22, 24 to 26, 28, 33, 35, 37 to 44, 46, 47, 55, 56 and 58 are not placed in SPEC/07, and a code row sent to M08 is not built. Row 9 (the Grafana token, expires 2026-10-31) gates F6.4 and F7.4's reads.
Settle: Product writes that table before the cut list is ruled, with "not built" said where it is true.

**29. FINDING. The CLI is neither built nor cut.**
SPEC/00 §8 M07: "`make upgrade` / `agent upgrade`"; P11: "`agent evals --local` becomes an alias of it at M07, when the CLI exists"; §9 cut 5 names only "`make upgrade` as a local command".
Settle: Product adds the CLI to §9 or §10.

**30. FINDING. The cap. §6 has 15 build items; I would expect retirement and `model-watch` to threaten it.**
§5.1: "After PR 2 merges, in this order ... 1 ... 6. ... **PR 3 is the repair** ... If a step misses, the steps after it are not attempted".
Wrong:
- PR 2 carries three new scheduled paths (`platform-upgrade.yml`, `model-watch.yml`, `deploy.yml`'s `retire`), each run live for the first time after the merge. It also carries two App permission changes, a cross-account `bundles/` prefix, panel 2's source and ten owed rulings.
- One repair PR serves six sequential hand steps. M06 needed its one repair and then found a second defect.
- The chain discards independent readings: step 5 (refagent's swap) depends on nothing in steps 1 to 4.
- The swap and its revert are two more merged pull requests on `main`, each needing a ruling file; SPEC/07 does not say whether they count against the cap.
Settle: Product rules which steps are independent, whether the swap and revert pull requests are outside the cap (as #1 and #29 were, by a ledger line), and which §6 item is cut first if PR 2 slips.

**31. NOTE.** The cut list is ordered (a to e taken at open, then 1 to 5). Its order differs from SPEC/00's (panels 3 and 4 before the compliance page); amendment 3 covers that. Cut 3 moves Act 3 to M08 PR 4 although its script shows "a HITL refusal" and "the Braintrust trace", both cut by c and e.

### Check 7. Seats

**32. FINDING. The `bundles/` prefix has no path or seat named.**
§6 Retirement names `deploy.yml`, `scripts/registry.py`, `scripts/retire_agent.py`. Writing `bundles/<name>/<commit>.tar` in the security account's bucket needs a policy statement and a principal under `infra/security/` and a hand deploy there; R7 lists `DeleteAgentRuntime`, `cdk destroy` and the KMS window only.
Settle: Security adds the path to §6 and the deploy to §5.1.

**33. FINDING. §6 says the App's token is minted in one job, then mints it in two more.**
§6 The token: "the token is minted in the `post` job only"; §6 `platform-upgrade`: "The App needs `contents: write` and `pull_requests: write` on agent repositories"; `model-watch`: "the App installed on `andaro74/agentkeel` too".
Wrong: open.md row 2 asks "which workflows and jobs can mint the token" as a bound; with contents and pull-requests write plus the check it posts itself, the App can open, pass and merge a change in an agent repository with no person. §8's bullet "The platform's pull request merged by the platform" describes a different gap under that heading.
Settle: Security rules the mint points and permission sets per workflow in `pr2-security.md`, and whether the App merging its own pull request is seeded or listed in §8.

**34. FINDING. The template's re-make and `make_template.py`'s change are not in §6.**
§2: "Re-making the template is the owner's push to the template repository (§6; ...)". §6 has no such item, and `scripts/make_template.py` (Engineering) changes at PR 2 per §2 only.
Settle: Engineering and Security add both to §6.

**35. NOTE.** Every other path §6 builds has one seat. `legal-compliance` is "Called by Product, Security" in SPEC/00 §5.1; SPEC/07 gives it Product's front matter, one seat. `.claude/agents/legal-compliance.md` is not yet in the tree or CODEOWNERS, as expected before PR 1. A platform upgrade moving `guardrail` in an agent repository changes a Rule Owner field with no ruling; §8 says so.

### Check 8. Contradictions

**36. FINDING. The grant's order contradicts open.md row 2.**
§5.1: "Before PR 2's first commit: the rulings §11 owes ... then the grant and the organisation's acceptance". Row 2: "`app_token()` with no repository ... must not exist after the grant".
Wrong: granted before PR 2's first commit, `main` still carries `scope = {}` (`scripts/platform_check.py` line 142) for the whole of PR 2.
Settle: Security rules the grant after PR 2's merge.

**37. FINDING. The environment read omits a field and names the wrong file.**
§3 item 2: "Read by hand on 2026-10-02 (`milestones/M07/runs/platform_app_environment.json`): one branch policy, `main`."
Wrong: the policy is in `platform_app_branch_policies.json`, which SPEC/07 never names; the named file shows `"can_admins_bypass": true`, which S0's environment fixture does not cover; neither file carries a read time, and the date given is after the session's date (2026-10-01). Whether admin bypass reaches a branch policy I could not verify.
Settle: Security rules under R1 whether `can_admins_bypass` is inside the bound, and the files gain their read time.

**38. FINDING. §10's amendments miss lines SPEC/07 changes.**
SPEC/00 §8 M07 still reads "Playwright over the surfaces with a plants-fired list" (build) and "a Playwright plant goes silent" (seeded); §6 says `platform_version` is a "pinned tag" and the build list says "on a platform tag". Amendment 2 changes F7.4's wording and §13 only.
Settle: Product adds them to amendments 1 and 2.

**39. NOTE. SPEC/07's header states things that have not happened.**
"Reviewed by `product-spec-reviewer` before anything else in PR 1 was written (`milestones/M07/feasibility.md` §1) and revised once on the rulings in §2 of that note." Neither `feasibility.md` nor `rulings/pr1.md` exists at 83eb558. The line becomes true or false in PR 1; it is false today.

**40. NOTE. R8.** SPEC/00 §5.1: a specialist's "prompt must be exercised on that milestone's seeded case". §5.1 of SPEC/07 runs `legal-compliance` "once on `data/slate.json`, `data/corpus/` and this SPEC's cut list", none of them an M07 seed.

**41. NOTE.** SPEC/00 §12 calls rollback a "manual re-point to the previous digest (M07)"; SPEC/07 measures a revert pull request redeployed by `deploy.yml`. CLAUDE.md says "all five targets"; `make upgrade` would be another. Step 5 may need a bootstrap redeploy by hand for the candidate's model access, as at M04; §5.1 does not list it.

### The five amendments: does SPEC/07 depend on each?

| # | Depends? | Without it |
|---|---|---|
| 1 (S0; SPEC/06's S3 received; "major" reworded) | Yes | S3 and Acts 1 and 2 are already M07's by SPEC/00 §8 M06 as amended at M06 PR 4. S0 as a never-cut seed and the reworded bump are not; S1 as designed would not be SPEC/00's "platform major bump". |
| 2 (F7.0; F7.1 reworded; F7.4 without Playwright) | Yes, all three parts | F7.0 does not exist, F7.1 reads "a manual workflow edit", F7.4 needs Playwright. Incomplete: items 14 and 38. |
| 3 (cut list) | Yes, most of all | Cuts a, b, c, e, 3, 4 and 5 are outside SPEC/00's three-item list; M07 would owe HITL, the knowledge base, the judge, Braintrust, Playwright and Act 4. Incomplete: item 26. |
| 4 (§10.5 "stands") | No | It changes no SPEC/00 text. SPEC/07 depends only on NOTE 23 being extended (open.md row 11), a Product ruling, not an amendment. |
| 5 (row 6 keeps "governed") | No | It changes no SPEC/00 text; it answers open.md row 8. |

A sixth is needed and not proposed: §10.3 row 07's sentence (item 1).

BLOCK: 3 · FINDING: 26 · NOTE: 12

## 2. Rulings on the report

**Ruled by the human on 2026-10-01, in the seats named: "as proposed".**
Each BLOCK is ruled as its option (a); each item in "The other items
that wait" as its first option; each item in the last table as proposed.
The rulings were made before any seed was planted (the first seed commit
follows this one) and are recorded in `rulings/pr1.md`. SPEC/07 is
revised once on them, and SPEC/00 amended, in the commits after this one.
The options are kept below as they were put. The reviewer's facts in
items 3 and 37 were checked against the tree and hold: no
`evals/history/133959f*`; `"can_admins_bypass": true`.

### The BLOCKs

**BLOCK 1 (item 1, with 23). Product. Ruled: (a).**

- (a) *Recommended.* A retirement is carried by a pull request. The
  platform opens a draft pull request in the agent's repository that sets
  the manifest's `rollout` to `retired` (one value added to the schema's
  enum, Engineering). It opens when the row is flagged idle, when the
  pin's `deprecated_after` is within 30 days with no swap open, or when
  the owner dispatches the retire workflow for that agent, which is the
  seeded trigger. The agent's seats merge it; the deploy path, finding
  `rollout: retired` at a head the App passed, retires instead of
  deploying. Archiving the repository is the owner's last step, not the
  trigger. §10.3's sentence stands as written.
- (b) Retirement is exempt from "arrives as a pull request" and "gated";
  §10.3 row 07 is reworded (a sixth amendment), and `taken` counts two
  pull requests and one retirement.

**BLOCK 2 (item 2). Product. Ruled: (a).**

- (a) *Recommended.* A ruling file under `milestones/*/rulings/` is not
  "a person's edit". A seat ruling a change is the gate working, as it
  does for every change in `agentkeel`. F7.1 reads every other path on
  the pull request. §2 and F7.1 say so. Agent repositories ask for no
  ruling (SPEC/06 §8), so nothing changes there.
- (b) The model kind cannot count toward `taken`; the measured value is n
  of 2.

**BLOCK 3 (item 26, with 27, 29, 31). Product. Ruled: (a).**

- (a) *Recommended.* Cuts a, b, c and e are taken at open, by SPEC/00
  amendment, each recorded in SPEC/00 §12 as "not built in this project"
  with its count of moves; F3.5's second half, the cached-answer seed,
  `g-014` as a plant and row 35's live half are named there as "not
  measured in this project". The CLI (`agent upgrade`, `agent evals
  --local`) joins cut e. What they break downstream is named in SPEC/00
  as recorded contradictions, each ruled at M08 open and carried in
  M08's `open.md`: R6 (no judge of record); M08 run 1's sixth attempt
  (the judge rubric) and F8.5's "Gateway policy"; M08 PR 3's Braintrust
  experiments; Act 3's HITL refusal and Braintrust trace; and §15's "at
  least seven GREEN", which rows 1, 4, 5 and 6 already rule out. M08's
  text is M08's to rewrite (one milestone per session).
- (b) The same items stay M07's as ordered cuts, taken only when the cap
  is threatened. M07 then opens owing more than four PRs hold, and the
  cuts are taken at PR 2 or PR 3 with the same contradictions.
- (c) SPEC/00 §8 M08, R6, §10.2 and §15 are all amended now, in this PR.

### The other items that waited, each ruled as its option (a)

| Item | Seat | Options, the first recommended |
|---|---|---|
| 14 | Product | (a) F7.0 reads "exists" only: the owner's test agent and the timed run's agent each merged, deployed, answered and listed. SPEC/06's F6.1 live half and F6.3 are read by `template` on M07's envelopes and quoted in row 7's cell as claim 6's later reading; row 6's cell stays on `245eb9b` and its README gains the reading as a dated note. (b) as drafted: over the bar fires F7.0 |
| 12, 13 | Product; Engineering | (a) S2 gets a new head: the owner pushes one empty commit to `s2-standin` after PR 2's merge, so the repaired App checks it and can refuse it on its own null seats. `floresinnovations` is not touched. It is read **before** owner-check #1 merges, so "behind" cannot enter. (b) the old check run with a new viewpoint, which leaves `open.md` row 5 unanswered |
| 16 | Threshold Owner; Product | (a) `m07_watch_candidate` is Haiku 4.5, the cheaper swap M04 never ran (`open.md` row 66). If its envelope is RED it is not merged, F4's reading is recorded, and **F7.3 is read on the fallback named before the run**: owner-check's platform upgrade merged, then reverted. (b) no fallback: a RED candidate leaves F7.3 unread and row 7 RED |
| 4 | Product; Security | (a) S2 gains one invocation of the retired runtime's ARN by the `retire` job, after the deletion, expecting `ResourceNotFoundException`, recorded raw. (b) the fixture alone |
| 30 | Product | (a) Steps are chained only where one needs the other: the owner's test, S2's re-read and the timed run in order; S1 after the timed run; refagent's swap at any time after PR 2's merge; retirement last. The swap and its revert are outside the cap by a ledger line, as #1 and #29 were. If PR 2 slips, panel 2 with S4 and S5 lands in PR 3. (b) as drafted |
| 36, 33 | Security | The grant is made **after PR 2 merges**, when `main` no longer carries `scope = {}`. The mint points and permission sets per workflow are ruled in `pr2-security.md` before it; whether the App may hold `contents: write` and `pull_requests: write` on agent repositories at all is that ruling's (it is a grant) |
| 38 | Product | Amendments 1 and 2 also change SPEC/00 §8 M07's build line "Playwright over the surfaces with a plants-fired list", its seeded line "a Playwright plant goes silent" (to "a surface plant goes silent"), §6's "pinned tag" and "on a platform tag" |

### Ruled as proposed, recorded in `rulings/pr1.md`

| Item | Seat | Proposed |
|---|---|---|
| 3 | Product | S4 names `6f3d1618f42a…`, a RED envelope on `main`, checked before its commit |
| 5 | Engineering; Product | "Older" is ancestry in `agentkeel`. S1's diff is stated before the run: `manifest.yaml`'s `platform_version` and whichever platform-owned file PR 2 changed |
| 6 | Security | The dispatch from a branch is a second attempt in `runs/f7_0_owner_test.yaml`, planted in PR 1, and an arm of F7.0 |
| 7 | Product | S1's run file names owner-check; the timed run's repository is added, pushed, when Product names the agent |
| 8, 11 | Security; Engineering | A pull request's run reads with the anonymous viewpoint and says so. The App-viewpoint readings come from a scheduled workflow on `main` that reads the run files on `main` and stores its observation; the row's cell cites the envelope of the first `main` run after the close PR's attempts are on `main`. Settled under R4 before PR 2; row 7 says which run its cell cites |
| 9 | Engineering | F7.2 is timed from CloudTrail's `eventTime`; the platform trigger from GitHub's push record |
| 10, 20 | Engineering | `F7_0` to `F7_3` get test-only witnesses in `checks` from their fixture tests at PR 2. Fixture markers come off at PR 2; attempt markers when each run file is filled |
| 15 | Threshold Owner | The limits enter `thresholds.yaml` as `upgrade.*`, each `relaxes: up`, at PR 2, before any attempt. The cron is stated in SPEC/07 |
| 17, 32 | Security | The deploy puts the signed archive under `bundles/` at deploy time; the bucket's policy statement and its hand deploy are in §6 and §5.1 |
| 18, 21 | Engineering | F7.5 is a test-only reading and §4 says so. The surfaces' control names two plants, S4 of M06 and S4 of M07; S5 is the test of the counter and is not counted |
| 19, 22, 24, 25, 35, 41 | Product | Added to §8 or §7 as written by the reviewer; `docs/platform/surfaces.md` says a GREEN envelope can sit under a RED row |
| 28 | Product | §6 of this note places every row before the cut list is ruled |
| 34 | Engineering; Security | Both added to §6 |
| 37 | Security | Whether `can_admins_bypass: true` is inside the bound is ruled under R1; the run files gain their read time and SPEC/07 names both |
| 39 | Product | The header is made true by this file and by `rulings/pr1.md` |
| 40 | Product | `legal-compliance` is also run on S2's retirement: the compliance map's row for a retired agent's records and their retention |
