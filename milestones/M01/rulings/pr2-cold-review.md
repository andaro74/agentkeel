---
# Cold review of M01 PR 2 (#8), base `main`. DRAFT: not a ruling until the
# Engineering seat reads it and changes `ruling:` to `pr2-cold-review`.
# The four seat reports go in the PR body verbatim; they are not pasted
# here. Product's key for this PR is `pr2.md`, the Threshold Owner's is
# `pr2-threshold-owner.md`, both with the same `pr: 8`.
ruling: pr2-cold-review
seat: Engineering
authorises:
  # NOT .github/workflows/evals.yml, though this review's B1 is about it:
  # that path is Security's (CLAUDE.md's seat table, and `pr2.md` says the
  # same), and `pr2.md` already authorises it. Ruling B is one seat per file,
  # so this file names the path in its body and takes no key over it.
  - src/agent/**
  - src/bundle/**
  - src/manifest/**
  - src/validate/checks.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/cost_cap.py
  - scripts/observe_attempt.py
  - scripts/load_rights_table.py
  - tests/**
  - Makefile
  - pyproject.toml
  - uv.lock
  - .gitignore
  - milestones/M01/rulings/pr2-cold-review.md
evidence:
  - evals/history/a7419f47de8442c94107b68e4f441346edf47e11.json
  - https://github.com/andaro74/agentkeel/actions/runs/35547051640
  - milestones/M01/runs/f1_1_laptop.yaml
  - milestones/M01/runs/f1_3_key_policy.yaml
  - SPEC/00-overview.md#8-M01
pr: 8
---

# M01 PR 2 — cold review

Run at the tip, `3bc732a`, after the diff changed materially since the
first review. Four seats read it: `engineering-cold-reviewer`,
`security-reviewer`, `tool-owner`, `threshold-owner`. No
`product-spec-reviewer` — that seat reads SPEC/NN before PR 1, not here.
No specialist not in the tree (R8).

**Counts: 4 BLOCK · 40 FINDING · 37 NOTE.**

| Seat | BLOCK | FINDING | NOTE |
|---|---|---|---|
| Engineering | 1 | 11 | 9 |
| Security | 1 | 11 | 11 |
| Tool Owner | 1 | 7 | 7 |
| Threshold Owner | 1 | 11 | 10 |

## A limit on three of the four reports, stated before anything is read into

`security-reviewer`, `tool-owner` and `threshold-owner` each reported that
Bash was unavailable to them, so they read **the tree at HEAD** rather than
`git diff main...HEAD`. Their findings are therefore about the state of the
files, not about what this PR changed. Some describe things that predate
PR 2 and some describe things it introduced, and the reports cannot tell
them apart. Nothing below is triaged as "pre-existing" on a reviewer's word
alone; where it matters, the diff was checked by hand and the check is
named. `engineering-cold-reviewer` had Bash and read the diff.

**This is a finding against `.claude/skills/cold-review` itself, not against
this PR.** The skill's rule is "the reviewer reads **the diff** and the
milestone's ledger row", and it was met by one reviewer in four. The skill
names the subagents to call and says nothing about the tools they need, so a
seat subagent whose definition omits Bash silently reviews the tree instead
and its report cannot say which of its findings this PR caused. Nothing in
the skill or in `make validate` would have caught that; it was noticed only
because three reports opened by admitting it.

Seat: **Product** (`.claude/skills/**`). Carried to
`milestones/M02/open.md` as M02's inbox, because the repair is either a tool
grant in each `.claude/agents/*.md` or a line in the skill requiring the
reviewer to state which it read — and either is a change to how every later
milestone is reviewed, which is M02's subject, not a footnote in M01 PR 2.

---

## BLOCK

### B1 — `| tee` masks the gate's exit, so the required check can no longer fail. **Mine, introduced in `442484f`.**

`.github/workflows/evals.yml:217` (line 202 before the cure's comment block):

```yaml
run: make evals ... GATE_EXIT="$RUNNER_TEMP/gate_exit" 2>&1 | tee "$RUNNER_TEMP/evals.out"
```

A one-line `run:` with no `shell:` key runs under `bash -e {0}`. GitHub adds
`-o pipefail` only when `shell: bash` is set explicitly, and it is not set
here — `grep -n "shell:\|pipefail" .github/workflows/evals.yml` returns
lines 91, 158, 180, 194 and 297, none of them this step. So the pipeline's
exit status is `tee`'s. Verified empirically:

```
$ bash -ec 'false | tee /dev/null'; echo $?
0
```

`make evals` exiting non-zero was the job's **only** mechanism for failing
on a RED or REJECTED envelope. Verified by reading every step after it: the
one `exit 1` in the job is `Fail if pytest failed`, which reads
`steps.pytest.outcome`; `gate_exit` is consumed solely by the `record`
job's `if:` (line 278 then, 290 now), where a value other than 0 or 1 skips the commit
and fails nothing.

`infra/ruleset/main.json` makes `evals` a required status check. So since
`442484f`, **a RED envelope reports a green required check**.

Why it has not shown: every RED envelope on this branch — `96331342`,
`977af86`, `cef1500`, `ee2d219`, `6f3d161` — predates `442484f`, which the
delta read confirmed with `git merge-base --is-ancestor`. Both runs after it,
`a7419f4` and `2594d8e`, are GREEN, so the masking was never exercised. The
GREENs are true GREENs; what was gone is the protection, not the result.

The change that caused it was made to satisfy the ruling on runner mode: the
step was piped so a later step could grep `mode:` out of the output. The
requirement was sound and the implementation removed a control while adding
an instrument. That is the exact failure this PR has now recorded five times
in other forms, and the sixth was written by the same hand that wrote the
section about the other five.

**Cured in this PR** (M00 precedent: a cold review's BLOCKs are cured
inside the PR they were found in; PR 3 keeps its scope). `shell: bash` on
the step, which is what adds `-o pipefail`; `infra/workflows.sha256`
rewritten; and `tests/test_evals_workflow.py` holds it — the step that runs
`make evals` must declare `shell: bash`, there must be exactly one such
step, the step may not carry `continue-on-error`, its command may not end in
`|| true` or its kin, the `record` job must still read `gate_exit`, and one
test *runs* both bash invocations rather than asserting the claim from
memory. The last three of those came from the delta read below, which broke
the first version of the test in two ways. A repair touches a measured path,
so **the milestone measured again**; the verdict of that run is in
`evidence:`.

The job has not yet been seen to fail on a RED envelope; that is M03's
seeded case (claim 3), and `tests/test_evals_workflow.py` is sufficient for
M01 because M01's claim is not the eval gate.

### B2 — a fork PR turns the required `evals` check green without measuring anything

`evals.yml:68`; `infra/ruleset/main.json` requires the `evals` context with
`bypass_actors: []`. A skipped job produces a check run with conclusion
`skipped`, which GitHub counts as satisfied.

**Already ruled, as BLOCK C in `pr2.md`**, with the repair carried to PR 3
(split the job so `validate` and `pytest` run on a fork) and the seeded case
carried to M02. `security-reviewer` found it independently and named the
ruleset as the half that makes it a hole, which `pr2.md`'s ruling did not.
That addition stands and is **PR 3 scope**, written out so it cannot be
half-done: split the job so `make validate` and `uv run pytest` run in a job
with no credentials and no `if:`, **and re-export `infra/ruleset/main.json`**
so the required contexts name that job. Splitting without re-exporting
leaves the hole exactly where it is, because the required context would
still be the one a fork skips.

### B3 — SPEC/00 §9 still declares an edge that exists nowhere

`SPEC/00-overview.md:562` — "**Declared call** — `refagent →
ratings-helper@v1` ... Exercises the two-sided edge, budget headers, chain
identity and the graph diff **from M01**." Verified against the tree:
`agents/refagent/manifest.yaml:68-69` is `may_call: []` /
`may_be_called_by: []`, and `ls agents/` returns `__init__.py` and
`refagent/` only. `SPEC/01-signed-bundle.md:300` records the cut: "`ratings-helper`
stub, and the two-sided edge | cut now | M02".

This is **the same §9 that PR 2 amended for BLOCK A**, in this PR. The HITL
bullet took its cut marker — `SPEC/00-overview.md:557`, "**M07 (HITL cut
from M01 at open)**" — and the edge bullet three lines below it did not. The
amendment fixed the two things it was told about and left the third, which
is what an amendment does when it is written against a finding rather than
against the section.

**Cured in this PR.** The edge bullet now carries **M02 (cut from M01 at
open; `may_call: []` until then)** — the same marker form the HITL bullet
took — and names that `agents/ratings-helper/` is not in the tree. Product,
in the §9 amendment it already authorises.

### B4 — the model under test is pinned without a version and without a lifecycle read in the tree

`agents/refagent/manifest.yaml:29-33`, `id: anthropic.claude-sonnet-4-6`,
`version: null`. SPEC/00 §5 gives this seat "agent model id + **version** +
region (A-vs-A compares the pair)". Every other Anthropic id in the same
file carries a dated suffix (`anthropic.claude-sonnet-4-5-20250929-v1:0`
and two more); refagent's is the only unversioned pin, and an unversioned
alias can be re-pointed by the provider with no reader in this repo seeing
it — which is the thing this repo exists to catch.

Against it: the pin **is** supported by better evidence than a listing.
`evals/history/a7419f47...json` records `model_id:
us.anthropic.claude-sonnet-4-6` with 12 of 15 goldens passing, from CI. That
is a call, not a claim, and it is the rule `pr2-threshold-owner.md` set
after Sonnet 5.

**Cured in this PR, and ruled down.** `milestones/M01/runs/model_lifecycle.txt`
holds the listing, dated 2026-09-20, account 581208540944, us-west-2: one
id, `anthropic.claude-sonnet-4-6`, no version suffix, `modelLifecycle`
ACTIVE — plus the wider `contains(modelId, 'sonnet-4-6')` query, so the
absence is shown rather than inferred from an exact-string match. `version`
stays **null under ruling G**: the field records what Bedrock returns, and
Bedrock returns no version. The manifest comment cites the file. What the
record does *not* settle is written in it: with no version there is nothing
to compare if the alias is ever re-pointed, and that is M04's.

---

## The delta read of the cure, `a7419f4..2594d8e`

`engineering-cold-reviewer`, given that range and nothing wider, and **it
confirmed it could execute git before reading** (`git version
2.55.0.windows.4`) — which is the thing three of the four reviewers above
could not do. Every claim it makes was checked by command.

**0 BLOCK · 4 FINDING · 6 NOTE.** It verified: the range does what it claims
and smuggles nothing (the three files outside the cure's description are
this ruling, M02's inbox and the bot's envelope commit, all cited); all four
`workflows.sha256` digests recomputed from `git show 2594d8e:<path>` with LF
endings; `shell: bash` maps to `bash --noprofile --norc -eo pipefail {0}` on
GitHub's runners and the Makefile does propagate the gate's exit
(`Makefile:63`, no leading `-`, so GNU make exits 2); and removing the
`shell:` key does fail the test.

**It found four things, and two of them were mine, in the cure.** All four
are cured in turn, in this PR:

| # | Finding | Cure |
|---|---|---|
| D1 | **The cure's own comment asserted an event that never happened.** `evals.yml` and the test docstring both read "between 442484f and its repair a RED envelope reported green". No RED run exists in that window — every non-GREEN envelope is an ancestor of `442484f`. This ruling said it correctly three paragraphs up; the two artefacts a reader meets *first* dropped the qualification. **It is the same defect the delta was curing, reintroduced by the cure.** | both now read "**would have** reported … no RED run occurred in that window, so the protection was gone and no result was wrong" |
| D2 | **The test asserted less than its own title.** Two edits restore B1's hole with all four tests green: `continue-on-error: true` on the step, and `\|\| true` appended to the command — `measuring_steps` matches the substring `make evals` and never read the rest of the line. Confirmed by injecting `continue-on-error: true` and watching all four pass. | two assertions added — **and the first version of that cure was itself incomplete**: see D2b |
| D3 | **"GREEN on this head" named an envelope for a different commit.** `pr2-body-draft.md` claimed GREEN on `2594d8e` citing `a7419f47…`, which measures the commit before it, and `2594d8e` changes five files none of which is in the workflow's skip-path exclusion list. **The fifth instance** of prose naming a state nothing checked. | cites `2594d8e4…`, carries the 9 + 3 + 3 breakdown, and says it was the fifth |
| D4 | **Two seats, one workflow file.** This ruling is `seat: Engineering` and authorised `.github/workflows/evals.yml`, which CLAUDE.md's seat table and `pr2.md:93` both give to Security — and `pr2.md` already keys it. Ruling B is one seat per file. | the line is out of `authorises`, with a comment saying why; Security's key in `pr2.md` stands alone |

Of its six notes, two are recorded here and four are dropped as not
mattering later:

- **Kept.** The new test is invisible from the envelope: `Makefile:41`
  passes `--check-junit F0_2 tests.test_f0_2`, so a failure in
  `test_evals_workflow.py` fails the job but leaves `checks.F0_2` pass and
  the verdict GREEN. The guard blocks the merge; it does not appear in the
  row or in `make plants`. Said once so nobody later reads a GREEN envelope
  as evidence this guard held.
- **Kept.** The empirical test proves bash, not GitHub. That `shell: bash`
  adds `-o pipefail` on GitHub's runners is a vendor fact this repo cannot
  test; what the repo can hold is the presence of the key, and that is what
  it holds.
- Dropped: the ruling's stale line citations (corrected in place), the
  "nothing else reads the verdict" wording (the other reader is on the
  mutually-exclusive already-measured path), the M02 inbox question
  (answered: it is cited at `pr2.md`), and the cap note (PR 3 and PR 4 are
  spoken for, which ledger row 1 already says).

### D2b — the cure for D2 was incomplete, and the seat caught it, not a reviewer

The first cure for D2 asserted `continue-on-error` **on the step**. The seat
injected it and reported the test still passed. It was right, and the reason
is one GitHub behaviour this seat did not check: `continue-on-error` set on
the **job** applies to every step in it. Injected at job level, all six tests
passed and B1's hole was fully restored.

So D2's cure repeated D2's own mistake in miniature — a guard written against
the one route that had been named, rather than against the thing it claims to
guarantee. That is the third time in this PR, and the second time in this
file, that a check was written narrower than its own title.

`test_neither_the_step_nor_its_job_may_fail_quietly` now reads both levels
through a `job_of()` helper. Four routes, each injected into the real file
and each run:

| Injection | Result |
|---|---|
| step-level `continue-on-error: true` | `FAILED … test_neither_the_step_nor_its_job_may_fail_quietly` |
| **job-level** `continue-on-error: true` | `FAILED … test_neither_the_step_nor_its_job_may_fail_quietly` |
| `\|\| true` appended to the command | `FAILED … test_the_measuring_command_does_not_discard_its_own_status` |
| `shell: bash` removed | `FAILED … test_the_step_that_measures_declares_shell_bash` |

The workflow was restored to sha256 `1a67aebe66e37f00` after the last
injection, the same value it held before the first, and `make validate`
reads `ok workflow-hash`.

**What is still not covered, said rather than left to be found.** A step
whose `if:` is edited to something never true is skipped, and a skipped step
fails nothing; these tests do not read the `if:`. Nor do they cover the
Makefile losing `exit $code`, which lives in another file. The claim these
tests support is narrow and exact: *the four known ways to make this step
stop failing the job are each refused.* It is not "the job cannot be made to
pass a RED envelope".

**One process note, because it cost something.** While injecting and
restoring around an *uncommitted* edit, the D1 fix to `evals.yml` was lost —
the file reverted to its committed state, still carrying the false sentence,
and `make validate` caught it on `workflow-hash`. It was re-applied. A cure
held only in the working tree is not yet a cure; this is an argument for
committing each repair before testing the next.

## Why this file is still DRAFT and not PASS

The condition for PASS was that the delta read find nothing new. **It found
four things**, two of them defects this cure introduced, including one that
is the exact class of defect the cure existed to remove. They are fixed —
and that fix is a further delta, which no reviewer has read.

This seat does not certify its own repair of a mistake it made twice in the
same file within one day. `ruling:` becomes `pr2-cold-review` when the seat
reads the delta above, or ratifies it, and not before.

## FINDING — triage

Repaired: none yet; this is a draft. The table is what each seat settles.

| # | Seat | Finding | Status |
|---|---|---|---|
| 1 | Engineering | `$COMMIT.agent-raw.json` is never committed and no envelope field carries its hash, so refagent's `score`/`cites` are not replayable; the control's are | PR 3 |
| 2 | Engineering | `cites` checks the citation exists in `data/`, never that it matches the golden's own pair | matches row 1's wording; record, do not repair |
| 3 | Engineering | `both()` ANDs two sources into one status and one URL, so no envelope can say which half of F1.1 failed | PR 3 |
| 4 | Engineering | the CloudTrail check never reads `principal`, though `observe_attempt.py` records it; S4's principal is the whole falsifier | **PR 3, and it weakens F1.1 today** |
| 5 | Engineering | F1.3's strength is `message_must_contain` in a human-written run file; delete the line and the check degrades to "any AccessDenied" | PR 3 |
| 6 | Engineering | `milestones/M01/pr2-body-draft.md` is committed and stale: says "This PR is RED on this head" (it is GREEN) and "Sonnet 5" in three places | **cured in this PR** |
| 7 | Engineering | `agents/refagent/server.py:30` hard-codes a Threshold-Owner-owned model profile as a default, and no test asserts the construct's env var | PR 3 |
| 8 | Engineering | `server.py`'s docstring says it does not fall back to the file; `agent.py:59-65` does | PR 3 |
| 9 | Engineering | `tests/fixtures/README.md` still says every seed is `xfail(strict=True)` and that S4/S6 are made after PR 2 merges; both untrue in the tree | **cured in this PR** |
| 10 | Engineering | one ruling file with one `seat:` authorises five seats' paths | R1 makes it one key; M02 enforces; this file takes Engineering's |
| 11 | Engineering | `deploy.yml` lands in the measure PR, refuses unconditionally, and has no PR left to first fire in | name the PR in row 1 |
| 12 | Security | a PR can edit `evals.yml` and `infra/workflows.sha256` together | self-disclosed; M02 |
| 13 | Security | `workflow-hash` hashes workflow text only, not `Makefile`/`src/` | M02 |
| 14 | Security | the required check's envelope is written by the PR's own code | self-disclosed; M02 |
| 15 | Security | `deploy.yml:198` reads `--stack-name AgentkeelBootstrap`; the deploy role's grant is `stack/agentkeel-*/*` and IAM ARN matching is case-sensitive | **PR 3, verified by hand** |
| 16 | Security | BLOCK F is named as cfn-exec only; the **deploy** role also lacks `ecr:*`, `dynamodb:*Item` and `bedrock-agentcore:InvokeAgentRuntime` | **PR 3; F's repair is larger than `pr2.md` states** |
| 17 | Security | the agent ceiling allows `bedrock-agentcore:*` on `*`; `iam:*` and `sts:AssumeRole` capped by omission, not named | Security |
| 18 | Security | `agentkeel-developer` is assumable by the whole account, no MFA or source-identity condition | Security: narrow, or say S4's principal is deliberately wide |
| 19 | Security | the eval role, which runs PR code, carries the `Allow *` deploy boundary | Security |
| 20 | Security | the key policy names five roles; the flow-log role and `BudgetActionRole` are created by this stack and unnamed, against SPEC/01 §6's "named one by one" | Security: name them or amend §6 |
| 21 | Security | `verify.py` exposes `--measure IDENTITY`, so the pinned cosign identity is a flag | Security |
| 22 | Security | `sign-fixture.yml` keeps `contents: write` + `id-token: write` on a `pull_request` trigger after its one-shot job is done | delete at PR 3/4, or a note that it stays |
| 23 | Tool Owner | SPEC/00 §9's rights-table bullet lists nine columns; the schema requires ten (`table_row`) | with B3, in the §9 amendment |
| 24 | Tool Owner | nothing computes the tool's semver; `version: "1.0.0"` is hand-written and read by no code | consistent with the ledger header; **Unsure** in the PR body |
| 25 | Tool Owner | `additionalProperties: false` at the nested `row` level is asserted by no test | PR 3 |
| 26 | Tool Owner | in the not-found branch the tool returns one `clause_candidates` entry, so it decides the clause | Tool Owner |
| 27 | Tool Owner | `src/manifest/schema.json` `pinned_roles` is open at every level | PR 3 |
| 28 | Tool Owner | the manifest schema does not require `may_call`, `may_be_called_by` or `ceilings` | M02 |
| 29 | Tool Owner | the output row types `territory`/`platform` as loose strings where the input uses enums | PR 3 |
| 30 | Threshold Owner | `thresholds.yaml:12-13` still names Sonnet 5 as the model to be measured | PR 3 |
| 31 | Threshold Owner | the cap re-rule promised against PR 2's first measured envelope is now due: 53,771 of 150,000 (36%), against a 58,500 pre-run estimate | M01 close |
| 32 | Threshold Owner | one cap covers two run shapes; the control-only run has effectively no budget | Threshold Owner |
| 33 | Threshold Owner | item 21, "is Nova Micro still a fair control", was re-dated to this PR and is unruled | PR 3 or close |
| 34 | Threshold Owner | "ten of twelve pinned models answered" exists only as a sentence; the script writes nothing | commit the stdout under `milestones/M01/runs/` |
| 35 | Threshold Owner | `build.py:396` takes `model_id` from the runner, and no reader compares it with the manifest's pin | **M04 needs this; PR 3** |
| 36 | Threshold Owner | `max_tokens_per_session` and `daily_usd` land unruled, and `daily_usd` collides by name with Security's Budgets figure | Threshold Owner |
| 37 | Threshold Owner | `build.py:398` sets `judge_model_id: None` as a constant, not a read | before M03 PR 1 |
| 38 | Threshold Owner | `thresholds_at` falls back to the working tree and `rule()` discards the provenance string | PR 3 |
| 39 | Threshold Owner | the envelope carries neither region nor model version, though A-vs-A compares the pair | ADR-0007, with the mode field |
| 40 | Product | `pr2.md:99-100` says the model id "does not move"; it moved in this PR | **cured in this PR** |

## NOTE — the ones that will matter later

- **N1.** No envelope on this branch shows S1, S2, S3, S5 or S8 absent: for
  those the recorded RED is PR 1's `xfail(strict=True)`, and reader and
  passing test land in the same commit. The strict marker is what stops a
  silent pass, and it held. What this PR does record is the gate going RED
  four times and UNMEASURED once before `a7419f4` reads GREEN. **That chain
  belongs in row 1**, not only in git history — it is the PR's best evidence
  that the instrument fires.
- **N2.** The cdk-nag suppression check is weaker than the prose:
  `src/validate/checks.py:306` accepts the literal string `SPEC/01 §6`, and
  all seven suppressions contain it, so the seeded-case branch never decides
  anything. A future suppression passes by pasting the string. Security.
- **N3.** The tip commit has no envelope: the newest is `a7419f4`'s, two
  commits behind `3bc732a`. `gate.latest()` picks the nearest envelope at or
  behind HEAD, so `make ledger` reads it. Row 1 is decided by the merge-commit
  run, which is the right rule — but today's measurement predates two commits
  of this PR, and B1's repair will move it again.
- **N4.** `src/agent/run.py:67` excludes all of `evals/` from the dirty
  check, which includes `evals/goldens/`. `:(exclude)evals/history` is what
  was meant. Narrow, because the baseline runner has no exclusion and runs
  first.
- **N5.** Two eval roles are assumable from `evals.yml` until the M00 stack
  is deleted. Which one PR 2's run used is not readable from the tree; the
  CloudTrail lookups only work for the new one, so a green F1_1/F1_3 implies
  it — inference, not evidence.
- **N6.** R2 holds: `passed == total` gates nothing. GREEN at 12/15 with
  three in `never_passed` is the regression bar working, not a score.
- **N7.** No added line in `docs/**`, `SPEC/**` or `milestones/**` calls an
  unfired control governed, secure or proven. `docs/milestones/M01.md`'s
  "What happened" is empty.

Dropped as not mattering later: the minimal-permissions nits on
`evals.yml:74-75`, `rps_per_edge: 0`, and the `seats` key-closure style.

---

## What a reader can run to falsify this review's own claims

```bash
# B1: the pipe swallows a non-zero exit. Prints 0.
bash -ec 'false | tee /dev/null'; echo $?
grep -n "shell:\|pipefail" .github/workflows/evals.yml   # line 202 is not among them

# B3: the edge SPEC/00 §9 declares at M01 exists nowhere.
grep -n "ratings-helper" SPEC/00-overview.md
grep -n "may_call\|may_be_called_by" agents/refagent/manifest.yaml
ls agents/

# Finding 6: the committed PR body draft contradicts the envelope.
grep -n "RED on this head\|Sonnet 5" milestones/M01/pr2-body-draft.md
python -c "import json;print(json.load(open('evals/history/a7419f47de8442c94107b68e4f441346edf47e11.json'))['verdict'])"

# Finding 15: the deploy role cannot describe the stack deploy.yml reads.
grep -n "describe-stacks" .github/workflows/deploy.yml
grep -n "stack/agentkeel-" infra/bootstrap/app.py

# Finding 9: the fixtures README against the tree.
grep -n "xfail" tests/fixtures/README.md tests/test_m01_seeds.py
```

## What this draft does not do

**It is still DRAFT.** All four BLOCKs and findings 6, 9 and 40 are cured in
this PR, but the cure changed a measured path, so this file does not become
a ruling on the strength of the review that preceded the cure. It re-reads
the delta — the cure commit and the run it produced — and only then does
`ruling:` become `pr2-cold-review`.

What the cure does not touch: the 33 findings triaged to PR 3, M02, M03,
M04 and the seats, and the notes. Those stand as written.

The four reports are not pasted into the PR body yet. The skill requires
them verbatim; the PR body hit GitHub's 65,536-character limit once already
in this PR, so they go as PR comments, as the earlier five did.
