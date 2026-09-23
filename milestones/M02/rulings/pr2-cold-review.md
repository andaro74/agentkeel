---
# Cold review of M02 PR 2 (#12), base main (c77e872), head d4d48de, by
# engineering-cold-reviewer from the diff and the ledger row. DRAFT until
# the Engineering seat reads it and changes `ruling:` to `pr2-cold-review`.
# Engineering's key for this PR's paths is pr2-engineering.md; this file
# names only itself and takes no second key over anything. The four seat
# reports (security-reviewer, threshold-owner, tool-owner, data-owner)
# are in the PR body verbatim; their findings are triaged in the table
# below beside the cold review's.
ruling: pr2-cold-review
seat: Engineering
authorises:
  - milestones/M02/rulings/pr2-cold-review.md
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#4-falsifiers
  - milestones/README.md
  - milestones/M02/README.md
  - milestones/M02/runs/pr2_gates_before_rulings.yaml
  - milestones/M02/runs/rehearsal_doors.json
  - milestones/M02/runs/rehearsal_seed_prs.json
pr: 12
---

# Cold review: M02 PR 2 (measure)

## What was done with it

Read at head `d4d48de`. Every report opens with `Read: the diff
c77e872...d4d48de (60 files)`; none read the tree. Repairs went in as
their own commits after the review, before the PR opened (`648cc75` the
code, the commit after it the prose and rulings); the diff between the
head read and the head that opens is those repairs and this file.
Counts: cold review 0 BLOCK, 7 FINDING, 7 NOTE; security 0/5/5;
threshold-owner 0/4/7; tool-owner 0/3/7; data-owner 0/3/6. No BLOCK
anywhere.

| # | Finding | Status |
|---|---|---|
| cold F1 | `observe_pr.py` raised `IndexError` on the seed's own `principal:` line; S4's and Door 3's instrument untested end to end | **Repaired** (Engineering, `648cc75`): `login_in` takes the comma-separated part that is a login; a test runs `main` on the committed `f2_1_bypass.yaml` with `observed: null` and gets the note, no crash |
| cold F2 | Door 2's reader passed on any merged PR with two seat files and no relaxation | **Repaired** (Engineering): `observe_doors` reads the `two-key` job log for the line `two keys with pr:` on a keyed relaxation, `check_from_doors` requires `relaxation_keyed`; the doors test holds the negative |
| cold F3 | attempt 2's RED rested on the human's typed `validate_result` | **Repaired in part** (Engineering): the observation reads `validate`'s "somebody can bypass main" line from the `checks` job the human records as `checks_job_id`, and says which witness it read. The check still accepts the human's RED with the witness named; PR 3 rules whether the CI line is required once one exists. The seed run file is not edited |
| cold F4, security F1 | the bot exemption reads `%an`, which anyone sets | **Ruled** (Security, `pr2-security.md` item 10): stands until M05 reads the push actor or a signature; named on the platform page under "What is not enforced". No seeded case at M02 |
| cold F5a | `memory` key deleted outright escaped the retention read | **Repaired** (Engineering): `after.get("memory") is None`; test added |
| cold F5b | a guardrail set to null takes one key; only a version moved down is in the closed list | **Recorded** for Product: SPEC/02 §2's list is closed and "adding to it is a SPEC/00 §5 amendment"; nothing turns on it before a guardrail exists (M03 PR 1) |
| cold F6 | the explainer said every planted case was refused | **Repaired** (Product): four of the five, named; S4 waits on the owner's attempts |
| cold F7 | the measurement PR rewrote its own Expected cell | **Recorded in place** (Product): the two consequences the reviewer asked for are now in the cell and in `milestones/M02/README.md`: PR 2's `F2_1: pass` is a test-only witness, and the gate requires `F2_1`/`F2_2` only from PR 3's constant. PR 3's cold review reads that constant first |
| security F2 | whether an Actions token is shown `bypass_actors` is unread | **Stands as written**: this branch had no CI run before the PR opened (it was never pushed); the answer is the `checks` job's `live main ruleset` line on this PR's first run, quoted in the PR body when it exists. If absent, PR 3 repairs as `pr2-security.md` item 2 says |
| security F3 | the RED-`checks` window after the ruleset edit is unbounded | **Ruled** (Security, item 4): the export is committed the same day and opened as PR 3 before any seed PR |
| security F4 | a second key "names" a path by substring anywhere in the body | **Recorded** for Product (SPEC/02 §2, M01 ruling B's shape): a `keys:` field or a fixed body line, at M03 PR 1 with the closed-list amendment below. The two-key files in this PR name the path in a heading |
| security F5 | Product's `milestones/M02/**` key covered edits to other seats' past rulings | **Repaired** (Engineering): a ruling file is owned by the seat in its own `seat:`, as a subagent prompt is; test added |
| security N1 | `app.py` comment named the CDK CLI for a call the AWS CLI makes | **Repaired** (Security) |
| security N2, cold N4 | the arm64 path has not fired on its case; do not write "refused" | **Recorded**: `runs/row10_first_deploy.yaml` says the refusal by name will not fire at this merge and why; `observed_at_pr2_merge` stays null |
| threshold F1 | the ruling answered only part of row 18 | **Repaired** (Threshold Owner, `pr2-threshold-owner.md` §8): Nova Micro as control, one cap for two shapes, the rate, the 4,000's source |
| threshold F2, F3, F4 | a `relaxes:` entry changed, a bar deleted, manifest budgets raised: none in the closed list | **Recorded** for Product: one SPEC/02 §2 amendment (a SPEC/00 §5 amendment by §2's own words) naming the three, at M03 PR 1 before the regression bar lands; the Threshold Owner proposes. A deleted cap already fails closed in `build.token_cap`; a deleted ceiling in `edges.ceilings` |
| threshold N1, N2, N3 | the rate, the 4,000, `check_model_access` | **Repaired / recorded** (Threshold Owner §8, §9): tokens not dollars, one call named; `check_model_access` to PR 3 or ruled unneeded there |
| threshold N4, N5 | `bars` reads one level deep; M03's bar lands as `delta_max`, R10's N as `up` | **Recorded** for M03 PR 1 (Threshold Owner, Engineering) |
| threshold N6 | the stub's pin should cite the lifecycle listing | **Repaired** (Threshold Owner): the manifest comment cites `milestones/M01/runs/model_lifecycle.txt` |
| tool F1 | semver missed a deleted tool schema | **Repaired** (Engineering): the base-side walk; test added |
| tool F2 | the edge check dropped the major | **Repaired** (Engineering): both sides at the same major in `edges.two_sided`; test added |
| tool F3 | ceilings bounded, not computed from the graph | **Recorded** for Product: SPEC/02 §6 says bounds and SPEC/00 §8 M02 says "on the org graph"; computed fan-out and depth at M06 with the second real agent (cut list item 1's home) |
| data F1 | `g-021` cites a row that does not give its answer, and refagent's tool cannot cite it | **Ruled** (Data Owner, `pr2-data-owner.md`): a golden no agent passes at M02, stated plainly; how an absence trap cites is Data Owner's and the not-found candidates Tool Owner's, both at M03 PR 1 |
| data F2 | the retirement removes a trap refagent passed | **Ruled** (Data Owner, Threshold Owner): stated with the number (passable traps 3 to 2) and the reason (Finding F0.1 measures the control's luck in every delta) |
| data F3 | `golden_ids` let a retired golden's file go, after which its id could be reused | **Repaired** (Engineering, Product): any base golden absent from the tree is refused; SPEC/02 §6's line rewritten; test holds both |
| data N1 | CLAUDE.md says `validate` checks golden/retrieval overlap; no such check exists | **Recorded** for Product: the sentence is ahead of the code until the corpus lands (M03) |
| data N2 | scoring never compares the cited row to the golden's | **Recorded** (Data Owner, Engineering, M03 PR 1): the platform page now says "a row and a clause that exist" |
| cold N1 | `two_key.py` reads history outside `src/verdict/` | **Repaired** (Product): CLAUDE.md's P5 line names `replay_history` as the shared reader |
| cold N2 | the README's "50 paths" sentence rested on prose | **Repaired** (Product): `runs/pr2_gates_before_rulings.yaml`, run at `0fc95a6` |
| cold N3 | `gate.rule` discards `where` from `golden_kinds_at` | **Recorded** (Engineering, PR 3): print it as `build` prints its notes; it fails closed meanwhile |
| cold N5 | "proves" on the platform page | **Repaired** (Product): "records" |
| cold N6, data N3 | the control still answers `g-012` every run | **Recorded** (Threshold Owner): a fixed cost while ADR-0002 holds |
| cold N7 | `lines_naming` strips before removing the timestamp | **Recorded** (Engineering, PR 3): fragile, not wrong; job logs carry the prefix |

## What stands for PR 3

In this order: the gate's `CLAIM_2_CHECKS` constant from this PR's merge
sha; `evals.yml` wiring of the three observation flags; cold F3's CI line
once one exists; `infra/eval-role/` after the destroy; `observed_at_pr2_merge`;
cold N3 and N7. The SPEC/02 §2 amendment (threshold F2 to F4, cold F5b,
security F4) is M03 PR 1's, Product's.

## The draft, verbatim

Read: the diff c77e872...d4d48de (60 files)

Read at head `d4d48de`, 16 commits, 60 files, +4084/-56. Nothing was run
that spends money; nothing was run that writes. Where a claim could not be
read from the diff, the command a reader would run is given.

### 1. Shape

Held. PR 2 holds the readers SPEC/02 §6 names and nothing a later PR
would need to build to read the plant: `src/gates/` (diff 2085-2780),
`src/validate/{codeowners,edges,golden_ids,ruleset,semver}.py` and
`check_relaxes` (2871-3436, 2831-2853), `.github/CODEOWNERS` (1-93),
`gates.yml` (176-254), `scripts/observe_pr.py` (1721-2068), `build`'s
three readers (3548-3614), the retired-golden path in `build`, `gate`,
`src/agent/run.py` and `src/verdict/__init__.py` (3437-3679). No seed
file is touched: `tests/fixtures/m02/*.patch` are not in the stat, and
`tests/test_m02_seeds.py` changes by exactly 5 deleted lines, all
`@pytest.mark.xfail` markers (4279-4322; `git show cc6e568 --stat`,
`git show 9068349 --stat`). No reader is left for the last PR. Nothing
under `src/baseline/`. The PR also carries M01 deploy repairs (N4) under
Security's ruling; they are not the measurement.

### 2. The plant

Four of the five seeds went RED on their readers, in the commits that
landed them:

- S1 (both forms) and S2: markers off in `cc6e568`, the commit that adds
  `src/gates/two_key.py` (`git show cc6e568 --stat`: two_key.py,
  test_gates.py, test_m02_seeds.py -3). The tests assert the planted
  reason: `thresholds.yaml`, `cost_cap.tokens_per_run`, "one seat"
  (`git show d4d48de:tests/test_m02_seeds.py`, test_s1_*); `g-010`,
  `Data Owner`, `expected` (test_s2).
- S3 and S5: markers off in `9068349`, the commit that adds `edges.py`
  and `golden_ids.py` (`git show 9068349 --stat`: test_m02_seeds.py -2).
  The tests assert `ratings-helper@v1` + `may_be_called_by` (S3); `g-005`
  + `retired`, and `g-099.yaml` uncovered (S5).
- S4: marker stays (test_s4, `xfail(strict=True)`), `observed: null` in
  `f2_1_bypass.yaml`. Not refused anywhere yet; SPEC/02 §5.1's named P3
  exception, read at PR 3.

Where the RED is recorded: the junit of the `evals` job (evals.yml line
195 at head, `--junitxml`), read into `checks.F2_1` by
`F2_1_CASES` (Makefile, diff 296, 306) through `check_from_cases`, which
fails on a name with no case (`git show d4d48de:src/verdict/build.py`,
lines 261-277). A second RED, `workflow-hash` refusing the unlisted
`gates.yml` at `0e78ef8`, is recorded in
`milestones/M02/runs/row16_second_workflow.yaml` (1664-1699) and is
re-readable with `git checkout 0e78ef8 && make validate`.

What the row's Expected cell says PR 2's own envelope carries was changed
in this PR (F7).

### 3. P5

Held, with one reader to name (N1). `scripts/observe_pr.py` writes a raw
observation and rules nothing (1727-1772, 2036-2063). Only
`src/verdict/build.py` gains `checks` writers (3548-3614, 3648-3653). Only
`src/verdict/gate.py` rules (3673-3678). `src/gates/two_key.py` reads
`evals/history/` through `src.verdict.replay_history` (2629, 2682-2690)
to tell "an id that has ever passed"; SPEC/02 §2 requires it (line 70-71
of SPEC/02 at head). No envelope is written by hand; the copy of
`e97125e...json` in `tests/test_gates.py` (3943, 4000) goes to a tmp
repo, never to `evals/history/`.

### 4. Frozen and owned paths

`src/baseline/` untouched (stat). Every seat-owned path in the diff has a
ruling file with `pr: 12` and the owning seat: `.github/CODEOWNERS`,
`.github/workflows/*`, `infra/**` (pr2-security.md, 920-943);
`thresholds.yaml` and the stub's model/budget fields
(pr2-threshold-owner.md, 1090-1107); `evals/goldens/v1/g-012.yaml`,
`g-021.yaml` (pr2-data-owner.md, 749-764); the stub's edge fields
(pr2-tool-owner.md, 1188-1201); `SPEC/**`, `CLAUDE.md`, `docs/**`,
`milestones/**` (pr2.md, 1250-1277); `src/**`, `scripts/**`, `tests/**`,
`Makefile`, `agents/refagent/Dockerfile`, the rest of the stub
(pr2-engineering.md, 816-835). `docs/milestones/README.md`'s one changed
cell (M01's video) is what `src/ledger.py` line 93-95 writes from
`docs/video/milestones/M01.mp4`, which is tracked at c77e872
(`git ls-tree c77e872 docs/video/milestones/`); generated, not hand-edited.
`data/`, `rules/`, refagent's manifest model ids: untouched.

### 5. Does it work

Findings F1-F5 below. The rest read as intended: `changed()` by blob id
with `hash-object --stdin-paths` (2238-2248); CODEOWNERS from the base
with the one-PR exception said in the output (2378-2389, held by
test_gates 4063-4083); every uncovered path listed (2541-2557); seats
counted not files (2738-2754); a bar with no `relaxes:` cannot move
(2674-2678) and `validate` refuses a bar without one (2849); deleting the
cost cap fails closed in `build.token_cap` ("No cap is a refusal");
deleting a ceiling fails closed in `edges.ceilings` (3065-3066);
`ruleset.check` treats absent `bypass_actors`, an unreadable ruleset and
a non-empty export each as an error, never a pass (3254-3290); the gate
reads goldens at the envelope's commit so row 1's envelope still rules
GREEN (3463-3492, test_retired 4536-4541).

### 6. Claims in prose

One overclaim (F6), one near-miss (N5). No "governed", "secure" or
"proven" about an unfired control. The overview's table names what each
gate refused and says "in a copy of the tree" (567-582).

### 7. Seat-owned paths with a cited ruling

See 4. Every ruling file cites `SPEC/00-overview.md#8-M02`.

### Findings

**F1. `observe_pr.py` crashes on the committed `f2_1_bypass.yaml` (FINDING)**

`scripts/observe_pr.py` line 226 (diff 1952):

```python
actor = str(run.get("principal", "")).split(",")[0].replace("the repository owner", "").strip().split()[-1] if run.get("principal") else ""
```

The seed's `principal:` is `the repository owner, andaro74, with admin on
andaro74/agentkeel` (`git show d4d48de:milestones/M02/runs/f2_1_bypass.yaml`).
`split(",")[0]` is `the repository owner`; the replace leaves `""`;
`.split()` is `[]`; `[-1]` raises `IndexError`. The line runs before the
`observed` checks (1953), so it raises with `observed: null` too, and
`main()` reaches it for any file with `attempts:` (2049-2051), and
`observe_doors` reaches it for door 3 (2015-2018). S4's instrument and
Door 3's are therefore untested end to end: `tests/test_observe_pr.py`
covers `lines_naming`, `rulings_in` and `build`'s readers, not
`observe_bypass`; the rehearsal (row 17) ran seed PRs against #11 and
door 2 against #10 only (1410-1532). The seed file must not be edited;
the parser must. Falsify offline, no token needed:

```
uv run python scripts/observe_pr.py milestones/M02/runs/f2_1_bypass.yaml --out "$TMP/x.json"   # IndexError at line 226
```

Fails loud, not silent, which is why this is not a BLOCK; PR 3 repairs
it before the attempts are looked up, and adds a test on `observe_bypass`
with the seed's own `principal` line and `observed: null`.

**F2. Door 2's reader passes on a merged PR with no relaxation in it (FINDING)**

`build.check_from_doors`, diff 3602-3605: door 2 is `found`, `merged`,
`two_key.conclusion == "success"`, `len(distinct_seats) >= 2`. `two-key`
is green on any PR with no relaxation (two_key.py 2771-2774 prints "no
relaxation in the diff" and exits 0), and `rulings_in` counts every
ruling file with the PR's number (1979-1992), so any merged PR carrying
two seat files satisfies the reader whether or not anything was retired.
The rehearsal shows it: `rehearsal_doors.json` reads #10, which relaxed
nothing, as `distinct_seats [Engineering, Product]` (1462-1465); only
`two_key: null` (no gates.yml then) kept it from passing. Door 2 is
"merged with two keys"; nothing in the observation says there was a
relaxation to key. The fix is the one door 1 already has (2008-2011):
`observe_doors` fetches the `two-key` job log for door 2 and records the
line the gate prints on a keyed relaxation
(`two-key: evals/goldens/v1/g-012.yaml: g-012 retired (retired: M02) (two keys with pr: 12 found)`,
2772-2773), and `check_from_doors` requires it, with the seats read from
the two files that cover and name that path rather than from every file
with `pr: 12`. Falsify: `tests/test_observe_pr.py::test_doors_pass_only_when_all_three_are_in_the_record`
passes with `doors()[1]` carrying no relaxation at all (4426).

**F3. Attempt 2's refusal rests on a human-typed field (FINDING)**

`build.check_from_bypass`, diff 3585-3588: `refused_ruleset` is
`human_said.validate_result == "RED"` and `live_now.bypass_actors == []`.
The live half is true today, before any attempt (`api_probes.yaml` 1392),
so the only term that can fail is what the human typed. SPEC/02 §4's rule
is "the check is the CI lookup of the PR number", and `f2_1_bypass.yaml`'s
header says "a human-written file feeds no check by itself". A CI witness
exists and costs nothing: while the actor is listed, any `checks` run logs
`the live ruleset's bypass_actors is [...], not []: somebody can bypass main`
(ruleset.py, 3270). The run file can record that run's id and
`observe_pr.py` can read the job log for that line, as it reads the seed
PRs' logs. The same holds for `check_from_doors` door 3 (3611-3612).
Until then the observation should say, as attempt 1's `witness` does
(1963-1964), which witness it read.

**F4. The bot exemption reads an author name a human can set (FINDING)**

`src/gates/__init__.py` `bot_only`, diff 2285-2291: `git log --format=%an`
equal to `github-actions[bot]`. `tests/test_gates.py` line 4109 makes a
"bot" commit with `-c user.name=github-actions[bot]`, which is exactly
what a human can do; that commit is exempt from `ruling-cited` (2548)
and is not a relaxation for `two-key` (2733). The claim the exemption
serves ("`github-actions[bot]` authorship under `evals/history/` is part
of what makes them evidence", CLAUDE.md) is stronger than what is read.
Neither SPEC/02 §2 nor `docs/platform/overview.md` "What is not
enforced" (584-595) says the exemption rests on an unverified name; the
nearest line is "nothing signs it (M05)". Name it now in both, and at
M05 read something a human cannot set (the push actor or the commit's
`verification` from the API, or the signature). Falsify: in a clone,
`git -c user.name="github-actions[bot]" -c user.email=x@y commit` a file
under `evals/history/`, then `uv run python -m src.gates.ruling_cited --base origin/main --pr 0` exits 0.

**F5. Two relaxations the closed list means are not read (FINDING)**

- `two_key.py` diff 2727: `if new_mem is None and "memory" in after`.
  Deleting the `memory` key outright escapes; setting it to `null` is
  caught. The manifest schema does not require `memory` (schema.json
  `required`, line 7 at head), so the deletion is a valid manifest.
  Change the test to `after.get("memory") is None`.
- diff 2721-2724: a guardrail set to `null` (`versions` contains `None`)
  is skipped, so removing the guardrail takes one key while moving its
  version down takes two. SPEC/02 §2 line 72 lists only "a guardrail
  version moved down", so this half is a SPEC gap to name (Product), not
  a code gap; refagent's guardrail is `null` at M02 (`git show d4d48de:agents/refagent/manifest.yaml`
  line 45), so nothing turns on it before a guardrail exists (M03).

**F6. The explainer says every planted case was refused (FINDING)**

`docs/milestones/M02.md`, diff 497-498: "there they refused every planted
case in a copy of the repository." Five cases were planted (S1-S5,
`milestones/M02/README.md` row "Seeded commit"); S4 was refused nowhere,
and its test keeps its marker (test_m02_seeds.py, `test_s4_the_owner_was_refused`,
`xfail(strict=True)`; tests/fixtures/README.md 3695-3702 says so). Write
"four of the five" or name S1, S2, S3 and S5, and say S4 waits on the
owner's attempts after the merge.

**F7. The measurement PR rewrote its own Expected cell (FINDING)**

`milestones/README.md` row 2 (diff 1716-1717), SPEC/02 §4 and §7
(332-344, 373-385) and `milestones/M02/README.md` (689-690): at PR 1,
`checks.F2_1` was to fail on PR 2's own run; at PR 2 it passes from the
five seed tests alone, and the second source and `checks.F2_2` move to
PR 3. The reason given, that a RED envelope makes `evals` red and PR 2
cannot merge through a ruleset with `bypass_actors: []`, is right (M01
PR 4's envelope merged only because its verdict was not RED), and it is
recorded in place in bold with the reason, which is what the ledger asks.
Two consequences should be stated where the cell is read: (a) PR 2's
envelope's `checks.F2_1: pass` is a test-only witness of four seeds in a
copy of the tree, not a refusal of a pull request; (b) nothing in
`gate.py` yet requires `F2_1` or `F2_2` on an agent envelope. The
amendment says that constant lands at PR 3 "as `ADR_0007`'s was at M01
PR 3" (342-344); until it does, a run that omitted `--check-cases F2_1`
would still rule GREEN. PR 3's cold review should read that constant as
its first item. The falsifiers F2.1 and F2.2 are unchanged; the row's
Measured cell is still `—`; the cap is 2 of 4.

### Notes

- **N1.** `two_key.py` is a reader of `evals/history/` outside
  `src/verdict/` (2629, 2682-2690), through `replay_history`, which
  `build.py` also uses. SPEC/02 §2 requires the read. CLAUDE.md's P5
  sentence ("only `gate.py` reads them") should name `replay_history` as
  the shared reader so the next cold review does not stop on it.
- **N2.** `milestones/M02/README.md` 718-721 says both gates refused this
  branch before the ruling files existed ("`two-key` on `g-012`'s
  retirement with no key, `ruling-cited` on 50 paths"). Prose only; no run
  file, no log. Nothing turns on it (it is not a plant), and the ledger's
  rule is that prose is not evidence. Either drop the sentence or record
  the two outputs under `runs/` with the commit they were run at.
- **N3.** `gate.rule` discards `where` from `golden_kinds_at`
  (3676: `kinds, _ = ...`), so a shallow clone falls back to the working
  tree without saying so (3482-3483). It fails closed: the kinds then
  differ from the envelope's and line 268 of gate.py fires. Print the
  `where` as `build` prints its notes.
- **N4.** The PR carries M01's deploy repairs under Security's ruling:
  arm64 runner and `refuse_unless_arm64` (112-148), the Dockerfile pin
  (478-483), the two CloudFormation grants (645-657), and
  `tests/test_deploy_image_architecture.py`. Claim 1's runtime has never
  started (`row10_first_deploy.yaml` 1637-1646, `observed_at_pr2_merge:
  null`); that is M01's RED, not M02's measurement. The three-place test
  is right that the reuse branch's refusal by name of `822fe2b5` cannot
  fire at this merge (1652-1661). Whether the arm64 runner image carries
  `docker` and `aws` is listed as unread (1646); it is read at the merge.
- **N5.** `docs/platform/overview.md` 586: "The gate proves the change was
  named and under which seat." The gate has refused seeds in a copy of
  the tree, not a pull request (its own table, 577, says so). "Records"
  is the exact word. Not the forbidden case; close to it.
- **N6.** `src/agent/run.py` skips a retired golden (2077-2081);
  `src/baseline/` still asks it (ADR-0002) and `build` drops the answer
  (3536-3540). Every run from here spends the control's tokens on
  `g-012`. Fine; the Threshold Owner should know it is a fixed cost.
- **N7.** `observe_pr.lines_naming` (1875-1884) strips the raw line before
  removing the timestamp, so the `line.startswith("     ")` branch works
  only on a log with GitHub's timestamp prefix. Only job logs are fed to
  it and the test uses the prefix (4350-4355); fragile, not wrong. The
  `retired`/`one-sided` words carry S5 and S3 regardless.

### What a reader can falsify

```
uv run python scripts/observe_pr.py milestones/M02/runs/f2_1_bypass.yaml --out "$TMP/x.json"   # F1: IndexError
uv run pytest tests/test_observe_pr.py -k doors                          # F2: passes with no relaxation in door 2
git show cc6e568 --stat; git show 9068349 --stat                         # the markers came off with the readers
git show d4d48de:tests/test_m02_seeds.py | grep -n xfail                 # one marker left: S4
uv run pytest tests/test_m02_seeds.py                                    # 5 passed, 1 xfailed
git checkout 0e78ef8 && make validate                                    # row 16: FAIL workflow-hash on gates.yml
uv run python -m src.gates.two_key --base c77e872 --pr 12                # g-012 retired, two keys found
uv run python -m src.gates.ruling_cited --base c77e872 --pr 12           # 0 uncovered
git diff c77e872...d4d48de --stat -- src/baseline tests/fixtures/m02     # nothing
```

BLOCK: 0 · FINDING: 7 · NOTE: 7

## To falsify this file's own claims, at the head that opens

```
uv run pytest tests/test_observe_pr.py tests/test_gates.py tests/test_validate_m02.py   # the repairs' tests
uv run python scripts/observe_pr.py milestones/M02/runs/f2_1_bypass.yaml --out .git/x.json   # no crash; a note
git log --format='%h %s' d4d48de..HEAD                                   # the repairs, then this file
```
