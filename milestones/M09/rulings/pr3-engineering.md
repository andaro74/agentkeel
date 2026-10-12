---
# M09 PR 3 (#52), the repair. Engineering's key over the Engineering paths
# this PR touches: the platform check's name reading and scratch tree, and
# the tests that read both repairs. Security's file is pr3-security.md (the
# bootstrap), Product's pr3.md (this milestone's README and the three ruling
# files; the run file is unchanged).
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/validate/agent.py
  - tests/test_bootstrap.py
  - tests/test_m09_platform.py
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/rulings/pr2-engineering.md
  - milestones/M09/rulings/pr3-security.md
pr: 52
---

# Ruling: M09 PR 3, Engineering

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-12.

## What this PR is

PR 3 of 4, the repair, under SPEC/09 §5.1's second named exception: the
platform's own deploy path needed repairing before an agent with `rules/`
could deploy, so PR 3 is the repair and the plant run is read by PR 4's
run, which the cell cites. Nothing here changes the claim, a seed, a
golden, a bar, `src/baseline/`, the run file, or `agent_rules`'s reading.
On this PR's envelope, when it is made, `agent_rules` will read not made
and row 9 RED, as at PR 2: no agent repository's record is read by this
diff and no reader changes.

## Repair 2: the held-pin check over the deploy's own copy

Deploy run 38259465892 (`agentkeel-studio/festival-desk` at `cd0ad604`,
2026-10-12 13:58 UTC), the first deploy of an agent with `rules/`, was
refused by `deploy-agent`'s held-pin check, which PR 2 added and which had
never run:

    FAIL the agent's name
         manifest.yaml: name festival-desk is held by agents/festival-desk/ in agentkeel

`deploy.yml` places the signed bundle at `agents/<name>/` in agentkeel's
checkout (the construct reads it there) and runs `src.validate.agent
evaluate --agent agents/<name>` with the registry row's pin.
`name_errors` refuses a name for which `agents/<name>/` exists in
agentkeel, to keep an agent repository from taking a platform agent's
name; in the deploy job the folder it found was the candidate itself. The
pull-request check never reads this: `platform-check.yml` checks the head
out to `agent-src` beside a clean checkout of `main`, and so does
`deploy.yml`'s `sign-agent` job, before the bundle is placed, in the same
run; that is where a name agentkeel holds is refused, twice, before
`deploy-agent` runs.

**Two changes in `src/validate/agent.py`**, both by identity of the folder,
never by name:

1. `name_errors(name, root, agent=None)` takes the folder being checked and
   does not count it as the holder; `evaluate` passes its `agent`. A caller
   that names no folder reads exactly as before.
2. `scratch_tree` skips the platform manifest whose folder *is* the
   candidate when it copies `root/agents/*/manifest.yaml` into the scratch
   tree. Without this, once the name passed, the scratch tree would have
   held `agents/<name>/` already and `copytree` would have raised
   `FileExistsError`: the deploy refused again, by a traceback instead of a
   FAIL line (`security-reviewer` F1 on this PR, read before any deploy saw
   it). Both changes are needed for `deploy-agent` to reach the pin.

`deploy.yml` is not touched: the alternative, a second copy of the bundle
for the check, changes a workflow and its hash under Security for the same
reading.

**Tests**, `tests/test_m09_platform.py`:

- the three cases of the name check on `name_errors` alone (the candidate's
  own folder admitted; no folder named, or another folder with that name,
  refused as before; a name nothing holds admitted either way);
- the deploy's layout end to end: a root holding the platform's two
  manifests, `thresholds.yaml`, the baseline and the bundle at
  `agents/festival-desk/`, with `evaluate` run over the bundle against that
  root, in the absolute form and in the relative `agents/<name>` form
  `deploy.yml` passes with the checkout as cwd: nothing refused; and the
  same bundle at `agent-src` against the same root, refused on the name
  alone, so the collision still fires where it should. Without change 2
  this test raises `FileExistsError` (run once with the skip disabled);
- the call site alone: `evaluate` hands `name_errors` the folder it is
  checking. This test reads only that (cold review F3: its earlier form
  claimed the refusal's absence as well, which held with or without the
  repair because `ROOT/agents/` holds no festival-desk; reworded).

## Repair 1's tests (the bootstrap, Security's path)

`tests/test_m09_platform.py` reads the execution role's three guardrail
statements by Sid (the create on `Resource *` held to the request tag,
`TagResource` at create on `guardrail/*` held to the request tag, the
resource-tag statement unchanged), the deploy boundary's two tag denies
(the conditioned one on an untagged guardrail; refagent's by ARN in both
forms, flat), and that every action the `AWS::Bedrock::Guardrail` and
`GuardrailVersion` handlers hold in their permission lists is granted and
denied by no flat deny on `Resource *`. `tests/test_bootstrap.py`'s
collision test reads flat denies on `Resource *` only: a deny on one named
resource fires on that resource, not on the action, as a conditioned one
fires on its condition. A future flat deny on a named resource that a
construct resource's handler needs would not be read by that test
(`security-reviewer` NOTE 3, cold review NOTE 3); today the only such deny
names refagent's guardrail, which the construct does not render. Recorded.

## What this PR does not do

- No change to `deploy.yml`, `platform-check.yml`, the construct, any
  golden, bar, seed fixture or the run file. `observed` stays `null`; the
  run test's marker stays on. The run is PR 4's.
- No change to what the platform check refuses at a pull request or at
  `sign-agent`.

## Cold review

Run before this PR opened, on the diff `f5ecb25...51695bc` (9 files), the
head before the repairs the review itself asked for. Two reads, both of the
diff. Dispositions, then the reports verbatim.

| # | Finding | Status |
|---|---|---|
| cold F1, sec F2 | `pr3-security.md` named a Data Owner ruling the PR does not carry; `pr3.md` said "four ruling files" | Repaired in the documents commit after the review: the clause struck, "three" written. Product. |
| cold F2, sec F3 | The by-hand deploy was made on a draft of `pr3-security.md` that was read by Security but never committed as ruled; the README said "after it was ruled" | Recorded as it happened in `pr3-security.md` (top), `pr3.md` item 5 and the README; the deployed policies read back from the account and pasted in `pr3-security.md`, which shows the stack holds `infra/bootstrap/` as `c7a8c36` and later hold it. The deploy stands on the "Ruled by" that file gets before #52 merges. Security and Product. |
| cold F3, sec NOTE 3 | The call-site test's name assertions held without the repair (`root` unset) | Repaired: the deploy's layout is now run against its own root (above); the call-site test reads the call site alone and says so. Engineering. |
| sec F1 | With the name passing, `scratch_tree` would raise on the deploy's layout; the deploy refused again | Repaired: change 2 above, read by the layout test, which fails without it. Engineering. |
| cold N1 | "five files of repair 1" in this file's reader block | Reworded. |
| cold N2, sec N6 | run counts stated in rulings, not in the diff | Stand as statements a reader re-runs with the reader blocks. |
| cold N3, sec N3 | the collision test reads flat denies on `*` only | Recorded above. |
| cold N4, sec N4 | residual reach to other projects' untagged guardrails rests on `deploy.yml`, outside the diff | Security's Unsure, in `pr3-security.md` and the PR body. |
| cold N5 | "on this PR's own envelope ... reads" in the present tense before the envelope exists | Reworded above. |
| cold N6 | step 3 partly done and recorded as not the run | Stands; nothing treated as measured. |
| sec N1 | nothing in `app.py` has fired on a guardrail create; the boundary's size limit held at the deploy | Stands; PR 4's deploy is the reading. |
| sec N2 | `sign-agent` and `retire-agent` also check `agent-src` before placing | Taken into the text above and the falsifier below. |
| sec N5 | the platform App installed on "selected repositories" | `pr3-security.md`, Security's Unsure. |
| sec N7 | a laptop path inside a pasted report | Left: the paste is verbatim by the skill's rule. |

### `engineering-cold-reviewer`

> Read: the diff f5ecb25...51695bc (9 files)
>
> Below is the draft ruling text for `C:\Users\andar\code\agentkeel\milestones\M09\rulings\pr3-cold-review.md`. A report, not a ruling; the Engineering seat rules and commits it.
>
> ---
> ruling: DRAFT
> seat: Engineering
> authorises:
>   - src/validate/agent.py
>   - tests/test_bootstrap.py
>   - tests/test_m09_platform.py
> evidence:
>   - git diff f5ecb25...51695bc (9 files; git log origin/main..HEAD: 51695bc 789bcc2 0214789 a614288 c7a8c36 a132c08 740914c 2bc9067)
>   - milestones/README.md row 9 (unchanged by the diff; `git diff origin/main...HEAD -- milestones/README.md` is empty)
>   - milestones/M09/README.md lines 170-245 (the diff's "Repair detail" and "By-hand steps before PR 4's run")
>   - milestones/M09/rulings/pr3.md, pr3-security.md, pr3-engineering.md (new in the diff)
>   - .github/CODEOWNERS (base ref, not in the diff)
> pr: 52
> ---
>
> # Cold review: M09 PR 3 (#52), the repair
>
> Read cold: the diff and row 9 of the ledger. Not the PR body, not the commit message bodies, not the feasibility note. Nothing was run; Bash was used for read-only git only.
>
> ## What was checked, and what held
>
> 1. **Shape (PR 3 = repair).** The diff holds two repairs and their tests, three ruling drafts, and the milestone README's detail. It holds no run file (`git diff origin/main...HEAD -- milestones/M09/runs` empty), no golden, no fixture, no `thresholds.yaml`, no `rules/`, no `src/baseline/` (`git diff --quiet m00 HEAD -- src/baseline/` reports unchanged), no `.github/workflows/`, no `infra/construct/`, no `src/verdict/`, no `scripts/observe_*.py`. Row 9's text at base already names this case: "PR 4's if the deploy path needs a repair, M08's second exception". The measurement is not in this PR. Holds.
> 2. **The plant.** Row 9 at base records the RED: "On PR 2's own envelope `agent_rules` reads unread ... so this row reads RED there". Nothing in the diff writes `agent_rules`, an envelope, or the run file's `observed`. The one change to the platform check (`src/validate/agent.py:97-112`) does not touch the fixture's reading: `tests/test_m09_seeds.py` evaluates `tests/fixtures/m09/s1-festival-desk` with `root=ROOT`, and `ROOT/agents/festival-desk` does not exist, so `name_errors` reads as before there. Holds.
> 3. **P5.** No file under `src/verdict/`, `scripts/`, or `evals/history/` is in the diff. Holds.
> 4. **Frozen and owned paths.** `infra/bootstrap/app.py` and `infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv` are Security (`/infra/` CODEOWNERS:52) and are the two entries of `pr3-security.md` `authorises` (lines 11-12). `src/validate/agent.py`, `tests/test_bootstrap.py`, `tests/test_m09_platform.py` are Engineering (CODEOWNERS:58, 80) and are `pr3-engineering.md` `authorises` (lines 8-10). `milestones/M09/README.md` and the three ruling files are Product (CODEOWNERS:27) and are `pr3.md` `authorises` (lines 9-13). `pr: 52` in all three (pr3.md:17, pr3-security.md:19, pr3-engineering.md:16). Every path in the diff has a seat and a ruling naming it. Holds.
> 5. **The repair's code.** `infra/bootstrap/app.py:790-795` moves `bedrock:CreateGuardrail` to `Resource *` under `Null aws:RequestTag/agentkeel:agent: false`; `app.py:807-812` adds `TagResource` on `guardrail/*` under the same request-tag condition; `app.py:1231-1236` adds the flat deny `NeverTagRefagentsGuardrail` on both ARN forms to the deploy boundary, through `self.deploy_boundary` set at `app.py:278` before `_guardrail` runs (`app.py:299`, the last call in `__init__`), and `iam.PermissionsBoundary.of(self).apply(deploy_boundary)` at `app.py:285` carries it to the execution role. `src/validate/agent.py:110-111` excludes the folder being checked from the collision; `agent.py:183` passes it. `deploy.yml:519-520` rsyncs the bundle to `agents/$NAME/` and deletes `agent-src`, `deploy.yml:564` evaluates `--agent "agents/$NAME"`: that is the refused case. `deploy.yml:428` and `platform-check.yml:139` evaluate `--agent agent-src`, so a name agentkeel holds is still refused before the rsync and at a pull request, as `pr3-engineering.md` says. The commit timestamps: `c7a8c36` (the last `app.py` change) is 2026-10-11 18:06:11 -0700 = 2026-10-12 01:06 UTC, before the 01:19 UTC deploy the ruling states; the four later commits touch no file under `infra/`. The deployed text is HEAD's `app.py`. Holds.
> 6. **Prose.** No "governed", "secure" or "proven" in the added lines (only the construct name `GovernedAgent`). Holds.
>
> ## BLOCK
>
> None.
>
> ## FINDING
>
> **FINDING 1 — a ruling file names a companion ruling the diff does not create.** `milestones/M09/rulings/pr3-security.md:6` (front-matter comment): "the Data Owner's pr3-data-owner.md (R9, R7, R11)". No such file is in the diff, in the tree at 51695bc, or on origin/main (`git ls-tree origin/main milestones/M09/rulings/` lists pr1*, pr2*, refagent-version-6*). No Data Owner path is in the diff, so none is needed; the sentence states a file that does not exist. Same class: `pr3.md:4` says "the four ruling files" while its `authorises` (lines 10-13) lists three and the diff adds three. Settles it: drop the clause at pr3-security.md:6 and write "three" at pr3.md:4. Falsify: `ls milestones/M09/rulings/pr3-data-owner.md`.
>
> **FINDING 2 — the ruling the by-hand deploy "waited for" is not in the repo.** `milestones/M09/README.md:178-179`: "the bootstrap stack deployed 2026-10-12 01:19 UTC from this branch after `pr3-security.md` was ruled". `pr3-security.md:25-27`: "after the first draft was ruled; this second draft ... is ruled again"; `pr3-security.md:216`: "after the first draft read 'Ruled by'". Every version of `pr3-security.md` on the branch is a DRAFT: `git log origin/main..HEAD -S'Ruled by' -- milestones/M09/rulings/pr3-security.md` returns a132c08 and 51695bc, and in both the only occurrences are the sentence "DRAFT until it reads 'Ruled by'" (file line 24) and the line 216 quotation; no commit carries a "Ruled by" signature. The first draft (`a132c08`) reads `pr: 51`. So the stack was changed by hand on a ruling whose ruled form is nowhere a reader can see, and the README states it as done. This is the Security seat's record to settle, not Engineering's: either the ruled first draft is committed (or its text pasted into pr3-security.md under a dated heading), or the README and pr3-security.md say "after the first draft was read by Security, uncommitted" and the deploy stands on the "Ruled by" this file gets before merge. Falsify: `git log origin/main..HEAD -p -- milestones/M09/rulings/pr3-security.md | grep -n '^+Ruled by'` (empty).
>
> **FINDING 3 — the call-site test's name assertions pass on an unrepaired `evaluate`.** `tests/test_m09_platform.py:301-318`, `test_evaluate_hands_the_name_check_the_folder_it_is_checking`: it copies the fixture to `<tmp>/agents/festival-desk` (line 313-314) but calls `evaluate(copy, ...)` with the default `root=ROOT` (line 315). `ROOT/agents/festival-desk` does not exist, so `name_errors` returns `[]` whether or not `agent` is passed, and the asserts at lines 317-318 (`errors["the agent's name"] == []`, no check refused) hold on the pre-repair code. Only line 316 (`seen == [copy]`) reads the repair, and it does: without `agent=agent` at `agent.py:183` it reads `[None]`. The docstring at line 302 ("so the deploy's own copy is not a collision") claims the deploy's case; this test does not read it, and `pr3-engineering.md:68-70` describes it the same way. The collision case is read by `test_the_folder_being_checked_is_not_a_name_collision_with_itself` (lines 283-298) on `name_errors` directly, so the two together cover the repair by composition. Not covered by either: the form the deploy passes, a relative `agents/$NAME` (`deploy.yml:564`) resolved against cwd at `agent.py:111` while `root` is absolute; it matches only when cwd is the checkout root, which `-m src.validate.agent` makes likely but no test reads. Settles it: in the call-site test, place the copy under a `root=tmp_path` that also carries what `evaluate` reads from `root` (`thresholds.yaml`, `agents/*/manifest.yaml`, `rules/baseline.yaml`), or add a case passing a relative `agent` with `monkeypatch.chdir(root)`; and reword the docstring to what the test reads. Falsify: revert `agent.py:183` to `name_errors(doc.get("name"), root)` and run the test; lines 317-318 still pass, only 316 fails.
>
> ## NOTE
>
> **NOTE 1 — a count in a ruling's reader block is wrong.** `pr3-engineering.md:99`: "`git diff f5ecb25...HEAD --stat` # the five files of repair 1, src/validate/agent.py, the tests, this milestone's documents and rulings". The stat shows nine files; repair 1 is two (`infra/bootstrap/app.py`, its NagReport.csv). Wording.
>
> **NOTE 2 — run results stated, not verified here.** `pr3-security.md:297` ("88 passed"), `pr3-engineering.md:101-103` ("8 passed, 1 xfailed", "twenty-one ok"), `pr3-security.md:131-187` (the `cdk diff` table). Statements about runs; nothing was run for this review. The reader-block commands are the way to falsify them.
>
> **NOTE 3 — the collision test now reads flat denies on `Resource "*"` only.** `tests/test_bootstrap.py:431-432`: `if not s.get("Condition") and s["Resource"] == "*"`. A future flat deny on a named resource whose ARN matches a construct resource will not be read by this test. Today the only such deny is `NeverTagRefagentsGuardrail` (`app.py:1231-1236`), which names refagent's guardrail, which the construct does not render. Recorded by the security-reviewer as NOTE 3 and by the comment at `test_bootstrap.py:429-430`; stands.
>
> **NOTE 4 — the residual reach is stated, and the thing it rests on is outside the diff.** `app.py:807-812` lets the execution role `TagResource` any guardrail under `guardrail/*` on a request carrying the agent tag, so the three untagged guardrails of other projects (`pr3-security.md:108-122`) can be tagged and then fall under `app.py:813-818`. The ruling's answer is that the only template the role runs is GovernedAgent's; that constraint lives in `deploy.yml`, which is not in the diff and which no test here reads. Security's Unsure, as the ruling says; no change asked.
>
> **NOTE 5 — a sentence about an envelope that does not exist yet.** `pr3-engineering.md:30-31`: "On this PR's own envelope `agent_rules` still reads not made, and row 9 still reads RED, as at PR 2." The envelope for #52's merge is not made. The reasoning holds from the diff (no agent repository envelope, no reader change); the tense says it is read. Wording.
>
> **NOTE 6 — step 3 is partly done and recorded in the README, correctly as not the run.** `milestones/M09/README.md:188-199` and `pr3.md:36-40`: the fixture repository exists, its first pull request merged at `cd0ad604`, the deploy was refused at run 38259465892. These are statements about the world a reader checks with `gh` (the README's and pr3.md's reader blocks give the commands); the run file is untouched and `observed` stays `null`, so nothing here is treated as measured. Consistent with the row's text.
>
> ## What a reader can run
>
> ```
> git diff f5ecb25...51695bc --stat                                                # 9 files
> git diff f5ecb25...51695bc -- milestones/M09/runs evals/goldens thresholds.yaml rules src/baseline .github/workflows infra/construct src/verdict scripts   # empty
> git diff --quiet m00 51695bc -- src/baseline/ && echo unchanged
> git log origin/main..HEAD --format='%h %ci %s'                                   # c7a8c36 at 01:06 UTC 2026-10-12, before the 01:19 UTC deploy
> git log origin/main..HEAD -p -- milestones/M09/rulings/pr3-security.md | grep -c '^+Ruled by'   # 0 (FINDING 2)
> ls milestones/M09/rulings/pr3-data-owner.md                                      # no such file (FINDING 1)
> grep -n 'agent-src\|agents/\$NAME' .github/workflows/deploy.yml .github/workflows/platform-check.yml   # 428/139 check agent-src; 519-520 rsync; 564 checks agents/$NAME
> ```
>
> BLOCK: 0 · FINDING: 3 · NOTE: 6

### `security-reviewer`, second read

> Read: the diff f5ecb25...51695bc (9 files)
>
> Security review, second read, M09 PR 3 (#52). Patch: C:\Users\andar\AppData\Local\Temp\claude\c--Users-andar-code-agentkeel\df2c1915-48a6-4ef5-b1a2-a21d92877c43\scratchpad\m09-pr3.patch. The 9 files (patch `diff --git` lines 1, 46, 141, 228, 343, 658, 744, 781, 798): infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv, infra/bootstrap/app.py, milestones/M09/README.md, milestones/M09/rulings/pr3-engineering.md, pr3-security.md, pr3.md, src/validate/agent.py, tests/test_bootstrap.py, tests/test_m09_platform.py. Tree read only to follow what the diff makes reachable: C:\Users\andar\code\agentkeel\src\validate\agent.py (whole), C:\Users\andar\code\agentkeel\.github\workflows\deploy.yml, C:\Users\andar\code\agentkeel\.github\workflows\platform-check.yml, C:\Users\andar\code\agentkeel\scripts\platform_check.py lines 643-666, C:\Users\andar\code\agentkeel\src\validate\agent_goldens.py lines 34-37, the test files' `evaluate(` call sites. A report, not a ruling.
>
> **(1) The four findings, against the patch.**
>
> - F1 taken. app.py patch lines 72-80 quote the CreateGuardrail row's condition-keys cell ("aws:RequestTag/${TagKey}, aws:ResourceTag/${TagKey} and aws:TagKeys beside automated-reasoning-policy ... no key on a row of its own") and name the open reading; pr3-security.md patch lines 418-435 (item 4) quote the same cell and state the fallback. As the ruling says (line 581).
> - F2 taken. app.py patch line 119: `resources=[guardrail.attr_guardrail_arn, f"{guardrail.attr_guardrail_arn}:*"]` on `NeverTagRefagentsGuardrail` (sid line 116, DENY line 117, flat: no `conditions`). Test patch line 856 reads both forms: `assert refagent["Resource"] == [arn, {"Fn::Join": ["", [arn, ":*"]]}]`.
> - F3 taken as a count, left open as a call. pr3-security.md patch lines 450-464: `list-guardrails` 2026-10-11, four untagged, three named as other projects'; "enough at M09 (proposed)". app.py patch lines 95-97 say the same. Still Security's Unsure (NOTE 4).
> - F4 taken. app.py patch lines 128-137 retire "tagging included ... out of reach" and write the exception. CSV: 18 `+` lines carry "M09 PR 3 (R3-a, the Service Authorization Reference read 2026-10-11)"; the retired sentence appears in exactly one `+` line, patch line 602, which is the earlier report quoted verbatim, not a live row.
>
> **(2) `name_errors`.** Patch line 753 `def name_errors(name, root=ROOT, agent=None)`; line 767-768 `held = root / "agents" / name` / `if held.is_dir() and not (agent is not None and held.resolve() == agent.resolve())`; line 777 passes `agent=agent` from `evaluate`.
>
> - Can an agent repository make `held.resolve() == agent.resolve()` true? No path found. Both sides are chosen by the workflow, not by repository content: `agent` is the literal `--agent` argument (`agent-src` at platform-check.yml line 139, deploy.yml sign-agent line 428 and retire-agent line 862; `agents/$NAME` at deploy.yml deploy-agent line 564), in Security-hashed files not in this diff. `held` is `<agentkeel checkout>/agents/<name>`, where `name` must match `^[a-z][a-z0-9-]{2,30}$` (tree line 69; patch line 762 keeps the check first): no separator, no dot, so `held` is always a direct child of agentkeel's own `agents/`, and only a symlink committed to agentkeel's `main` could make it resolve to `agent-src`. A symlink inside the agent folder is refused at tree line 172 before `name_errors` runs. `actions/checkout` creates `agent-src` as a directory; the repository cannot make that path itself a link. `$NAME` is the manifest's `name` at the App-passed head, re-held to the same regex (scripts/platform_check.py lines 657-661); not a PR title or branch.
> - At the pull-request check: `agent-src` != `agents/<name>`, so `agents/refagent/` and `agents/ratings-helper/` (the two folders on main; both also in `EXEMPT`, agent_goldens.py lines 34-37, refused one line earlier) and any future platform folder are still refused. Test patch lines 916-920 read exactly this case (`elsewhere = tmp_path / "agent-src"`).
> - At the deploy: deploy-agent's check (line 564) no longer reads a collision, by design. But the same commit is read at `agent-src` with the collision live twice before: platform-check's evaluate, and deploy.yml sign-agent line 426-429, which runs before the bundle is placed (line 431-435), in the same run as deploy-agent at the same `github.sha`, and fails the job on exit 1 (no `|| true`). A held name cannot reach deploy-agent's rsync (line 515-519, `-a` without `--delete`, which would merge onto a platform folder) without passing sign-agent on the same tree. retire-agent (line 858-864) likewise checks `agent-src` before placing. The ruling (pr3-engineering patch lines 283-285, 291-292) names only the pull-request check; the deploy path keeps the check too (NOTE 2).
>
> - FINDING 1 — the repaired check will not reach the pin at deploy-agent: `scratch_tree` raises on the deploy's layout. With patch line 768 letting the name pass, `evaluate` goes on to `scratch_tree(agent, name, root)` (tree line 191). Tree lines 89-92 copy every `root/agents/*/manifest.yaml` into `tree/agents/<x>/manifest.yaml`; at deploy-agent `root/agents/festival-desk/manifest.yaml` is the placed bundle, so `tree/agents/festival-desk/` is created there. Tree line 93 then `shutil.copytree(agent, tree / "agents" / name, ...)` onto that existing folder with `dirs_exist_ok` at its default False: `FileExistsError`, uncaught (line 191 is before the `try`), no result file, exit 1. deploy-agent still refuses the agent's own folder, by a traceback instead of a FAIL line. This layout (root already holding the candidate at `agents/<name>/`) has never run: the held-pin step is PR 2's, run 38259465892 returned at the name check before `scratch_tree`, and sign-agent checks `agent-src`. No test runs it either: every `evaluate(` call in tests uses the default `root=ROOT` with the agent under `tmp_path` (test_m06_readers.py 270-520, test_m08_seeds.py 87, test_m09_seeds.py 116, and the new one at patch line 940, `copy = tmp_path / "agents" / "festival-desk"` with `root` unset), so `ROOT/agents` never holds the candidate. pr3-engineering patch lines 340-342 name "a `deploy-agent` that still refuses the agent's own folder" as what makes that ruling wrong; as the diff stands it would. Fail-closed: no security exposure, but PR 4's deploy would be refused again and the cap is four. Settles it: `scratch_tree` skips the manifest whose `parent.resolve() == agent.resolve()` (or `dirs_exist_ok=True`), and a test calls `evaluate(root / "agents" / "festival-desk", ..., root=root)` with `root` holding the two platform manifests and the bundle. Engineering rules (src/validate/agent.py, tests/).
>
> **(3) Workflows and construct.** Nothing under `.github/workflows/**` or `infra/construct/**` in the 9 files; `infra/workflows.sha256` not in the diff, consistent with deploy.yml and platform-check.yml unchanged. pr3-engineering patch line 333 (`git diff ... -- .github/workflows infra/construct ... # empty`) reads true against the file list. Checklist 1 (permissions, pins, interpolation, pull_request_target, fork secrets): nothing in scope in this diff.
>
> **(4) pr3-security.md against the diff.**
>
> - FINDING 2 — the ruling names a companion file the PR does not carry. pr3-security.md patch lines 354-355: "the Data Owner's pr3-data-owner.md (R9, R7, R11)". No such file in the diff or the tree (milestones/M09/rulings/ holds pr3-security.md, pr3-engineering.md, pr3.md); pr3.md's `authorises:` (patch lines 672-676) lists three rulings and the README, and pr3.md line 710-712 says R9 stands with nothing of the Data Owner's touched. Settles it: strike the clause, or add the file and list it in pr3.md. Security's text; Product's pr3.md says which rulings exist.
> - FINDING 3 — the deploy's commit is unnamed, and the "ruled first draft" it followed is not in the diff. pr3-security.md patch lines 373-376 and 563-564 ("after the first draft read 'Ruled by' (step 1, 2026-10-12 01:19 UTC)"), README patch lines 157-159: no commit hash. The only "Ruled by" strings in the patch are the three "DRAFT until" lines (255, 372, 686) and line 564's own sentence. F2's second ARN form entered at c7a8c36, after a132c08's draft; whether the template synthesised for the by-hand deploy carried `guardrail/<id>:*` in `NeverTagRefagentsGuardrail` cannot be read from the PR (the pasted `cdk diff` table, lines 484-528, is the roles' policies and, as line 530-534 says, does not tabulate the boundary). Settles it: name the commit the deploy was synthesised from in the ruling, or paste `aws iam get-policy-version` of `agentkeel-deploy-boundary` showing that statement's two resources. Security rules.
> - Everything else the ruling says the diff does, the diff does: Resource `*` on CreateGuardrail (patch line 84), TagResource at create on `guardrail/*` held to the request tag (99-103), the flat deny by ARN both forms (115-120), the suppression rewritten (128-137, CSV 18 rows), "deploy.yml and the construct are unchanged; infra/workflows.sha256 is unchanged" (570-571), the construct's report untouched (572-573), "on the diff f5ecb25...a132c08 (5 files)" (579).
>
> **Checklist 2, switched off from inside.** The name check now lives in one line of src/validate/agent.py (Engineering path, `cold-review-ruling`): anyone with write and an Engineering ruling file can widen it; what stops a held name is also the two `--agent agent-src` lines in Security-hashed workflows, which the same person cannot move without a Security ruling and the hash. Nothing mechanical reads that `name_errors` still refuses a held name except tests in the same PR. Plain answer: Engineering plus a ruling file, and the workflow side is Security's. **Checklist 3, IAM.** Unchanged from the first read for app.py: boundary carried stack-wide (tree line 285); flat deny `kms:PutKeyPolicy` stands (R4); the one wildcard, `*` on CreateGuardrail, has its reason at patch lines 66-80. **4 Network, 5 Evidence:** nothing in the diff. **6 cdk-nag:** one suppression touched, `AwsSolutions-IAM5` on `ExecutionRole/DefaultPolicy/Resource`, 17 CSV `+` rows plus app.py lines 124-137; the added reason is specific (action, resource, condition, source, date, both ARN forms); it is one shared paragraph for every wildcard on the role, the standing pattern.
>
> **NOTEs.**
>
> - NOTE 1 — nothing in app.py has fired on a guardrail create: README patch line 176 "No guardrail was attempted". The bootstrap deploy of 01:19 UTC did succeed (README 157-160: version 6 exists), which settles the earlier NOTE 5 (the 6,144-character boundary limit held). Item 4's reading (aws:RequestTag on a plain CreateGuardrail) is still PR 4's.
> - NOTE 2 — the ruling understates the deploy path: deploy.yml sign-agent line 426-429 and retire-agent 858-864 read the collision at `agent-src` before placing, same run, same agentkeel sha as deploy-agent. pr3-engineering's falsifier (patch lines 340-342) could name that too.
> - NOTE 3 — test patch lines 926-943: with `root` unset, `ROOT/agents/festival-desk` does not exist, so `errors["the agent's name"] == []` (line 942) holds with or without the repair; only `seen == [copy]` (941) reads the call site. pr3-engineering lines 299-301 ("hands name_errors that folder and refuses nothing") claims both halves. The first test (908-923) does read the repair, with its own `root`.
> - NOTE 4 — F3's residual reach stands as proposed: three other projects' untagged guardrails are taggable by the execution role on a tagged request from a template `GovernedAgent` renders (pr3-security.md 450-464). A Security Unsure for the PR body, as the ruling says.
> - NOTE 5 — `agentkeel-platform` installed on "selected repositories", not "all" as SPEC/06 §6 reads (pr3-security.md 547-559; README 201-206). Narrower, not wider; but `infra/platform_grant.yaml` (Security, not in diff) evidently does not pin the selection, or the grant read-back would have refused. Security's to rule; SPEC/06 is Product's if amended.
> - NOTE 6 — pr3-security.md patch lines 645-646 ("88 passed", "twenty-one ok") and pr3-engineering 336 are statements about runs, not in the diff; 789bcc2 added two tests after the count was written.
> - NOTE 7 — the pasted report at patch line 588 carries a laptop path (`C:\Users\andar\...`) into a ruling file on a public main. Harmless; noise.
>
> BLOCK: 0 · FINDING: 3 · NOTE: 7

## What a reader can run

```
git diff f5ecb25...HEAD --stat                                  # 9 files: repair 1's two under infra/bootstrap/, src/validate/agent.py, two test files, the README, three rulings
git diff f5ecb25...HEAD -- .github/workflows infra/construct evals/goldens thresholds.yaml src/baseline milestones/M09/runs   # empty
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py tests/test_m06_readers.py tests/test_m08_seeds.py tests/test_m09_seeds.py -q   # the layout test among them
uv run pytest tests/test_m09_platform.py -q -k held_pin_check_admits   # passes; with scratch_tree's skip disabled it raises FileExistsError
uv run pytest tests/test_m09_seeds.py -q                         # 8 passed, 1 xfailed: the run, not made
make validate                                                    # twenty-one ok
gh run view 38259465892 --log-failed | grep -m2 "the agent's name\|is held by"   # the refusal this repairs
grep -n 'agent-src\|agents/\$NAME' .github/workflows/deploy.yml .github/workflows/platform-check.yml   # where the collision still fires (agent-src) and where it must not (agents/$NAME)
```

A `name_errors` that admits a name a platform agent holds at a pull request
or at `sign-agent`, a `deploy-agent` that still refuses the agent's own
folder by the name or by `scratch_tree`, or a change under
`.github/workflows/` in this PR, makes this ruling wrong.
