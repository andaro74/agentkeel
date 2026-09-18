# M00 feasibility note

Claim 0: every later number is a delta against a frozen naive baseline.

Order of this note: the `product-spec-reviewer` report, what this PR does
about its two BLOCKs, the false state, the code that will read the
answer, the falsifiers, the raw results of the PR 1 local run.

## 1. `product-spec-reviewer` report (pasted verbatim, 2026-09-18)

How it was run: `.claude/agents/product-spec-reviewer.md` was written
first, then run once against `SPEC/00-overview.md` for M00, read-only,
before anything else in this PR existed. The first run returned findings,
so the prompt was not tightened. The report is a draft, not a ruling.

> # product-spec-reviewer report — M00
>
> Input: M00. A report, not a ruling.
>
> Read:
> - SPEC/00 header, §4, §5, §5.1, §6, §7 row 0, §8 preamble and M00, §10.3 row 00, §11. Also §9 and §10.5, which §8 M00 names, and M01's build line for one cross-check.
> - `docs/adr/ADR-0001-spec00-adopted.md`, which §8 M00 names.
> - `milestones/M00/README.md`.
> - `CLAUDE.md`, for check 8.
>
> `milestones/README.md` and `SPEC/NN` do not exist. The tree was listed by Glob on 2026-09-18 and not read. It holds:
> - `SPEC/00-overview.md`
> - `docs/adr/ADR-0001-spec00-adopted.md`
> - `milestones/M00/README.md`
> - `milestones/adoption/rulings/adopt-spec00.md`
> - `.claude/agents/product-spec-reviewer.md`
> - `CLAUDE.md`
>
> ## 1. False state
>
> **1.1 BLOCK.** No section names the code that scores a baseline answer at M00.
> - Quoted: §8 M00 "Seeded: baseline must fail the traps". §8 M00 "`src/baseline/` (… no tools, no guardrail, no retrieval; reads nothing from `data/`". §6 "`expected` (ordinary and trap: `table_row`, `clause_id`, `answer_fields`".
> - Wrong: the judge is picked at M03 and the deterministic check is F1.4 at M01, so M00 has no named scorer. A model that reads no table cannot return a `table_row` or a `clause_id`. Under a field-match scorer the baseline scores traps 0/3 and ordinary 0/9 by construction, so F0.1 can never fire. Under an `answer_fields`-only scorer a yes/no guess fires F0.1 by chance.
> - Settle: before the 15 immutable ids are written, the Data Owner rules which `expected` fields score the baseline at M00. The Data Owner also rules whether each golden `question` carries the facts needed to answer it. Product records the ruling in feasibility.md.
>
> **1.2 FINDING.** The second seed cannot be committed in PR 1 as a named file.
> - Quoted: §8 M00 "a run without a baseline card is rejected by `verdict.build`".
> - Wrong: "baseline card" is not among the §6 artifacts. P5's "raw observations" have no format or path. At M00 the only run is the baseline itself. Committing the seed would mean inventing both formats.
> - Settle: before the plant is committed, Product names the plant's path in feasibility.md. Engineering names the raw-observation and card format there.
>
> **1.3 FINDING.** The reader of "frozen" lands in the last PR with no seeded case.
> - Quoted: §7 row 0 "a frozen naive baseline". §8 M00 "ADR-0002 (baseline frozen, with the diff-test) lands at PR 4 at tag `m00`, not before."
> - Wrong: the diff-test is what reads "frozen". It lands last and has no seeded case. That is against P3 and against CLAUDE.md "Never build the machinery that reads a claim in the last PR". The false state is an edit to `src/baseline/` after tag `m00`, and it cannot exist before the tag.
> - Settle: Product rules whether "frozen" is inside claim 0 or is a rule outside the claim that first fires at M01. If it is inside, the diff-test lands at PR 2 against a pinned tree hash with a planted edit.
>
> **1.4 NOTE.** "Frozen" covers the code, not the number.
> - Quoted: P6 "The control is re-run on every scorecard run" and §6 "baseline card ref".
> - Wrong: no section says whether a later envelope refers to the `m00` card or to the same-run card. No section pins the baseline's inference parameters. The model behind `us.amazon.nova-micro-v1:0` is not pinned either.
> - Settle: the Threshold Owner states the parameters and which card a ref points to.
>
> ## 2. Reader
>
> P5 was judged on "Runners write raw observations; `verdict.build` composes the envelope; the gate reads the envelope." The spec does not let the instrument decide the verdict, so there is no BLOCK on P5. The unnamed scorer in 1.1 is the open part of the chain.
>
> **2.1 FINDING.** The plant is read by `verdict.build`, not by the gate.
> - Quoted: P2 "The gate must fire on the plant". CLAUDE.md "The plant must go RED here". §8 M00 "rejected by `verdict.build`".
> - Wrong: if build refuses to write, no envelope exists and the gate never reads the plant. `verdict.build` is not in §5's exhaustive gate list. `make plants` "returns an empty list" at PR 2, so the milestone's own plant is listed nowhere.
> - Settle: Product rules what artifact records the firing. That is either a build exit code asserted by a named test, or an envelope with verdict RED or UNMEASURED. Engineering names the test file.
>
> **2.2 FINDING.** M00 builds three §5 gates and its falsifiers span two of them.
> - Quoted: P4 "One claim, one gate, one envelope… a milestone that needs a second gate splits or goes UNSCHEDULED". §8 M00 "`cold-review-ruling` as a required check from PR 2 (R9)".
> - Wrong: M00 builds `validate`, `regression` (via `verdict.gate`) and `cold-review-ruling`. F0.3 belongs to a different gate than F0.2.
> - Settle: Product rules M00 exempt from P4 as the bootstrap milestone, or moves F0.3 out of row 0.
>
> **2.3 FINDING.** M00 has no named CI path to produce a CI-written envelope.
> - Quoted: §8 M00 "Done when: `make evals` writes an envelope with the baseline card". P11 "Only CI-written envelopes are evidence". §8 M01 "bootstrap stack (GitHub OIDC provider, deploy role scoped to repo and branch".
> - Wrong: M00 names no workflow that runs `make evals`. It names no CI credential path to Bedrock. The OIDC provider is M01 build, and `evals.yml` is named only under `cost-cap`, which M03 builds. Row 0's envelope is therefore either not CI-written or depends on M01.
> - Settle: before PR 2, Security rules the M00 CI credential path and workflow file. Product records it in feasibility.md.
>
> ## 3. Falsifiers
>
> **3.1 FINDING.** F0.1 can be observed but nothing reads it.
> - Quoted: "baseline passes a trap (the traps are too easy — record, do not tighten in this milestone)".
> - Wrong: the observation is the per-golden pass of the three trap ids in an envelope under `evals/history/`. No code reads it. No section says whether row 0 goes RED when it fires.
> - Settle: Product rules the row 0 state when F0.1 fires. Product also rules whether `gate.py` or a person reads the trap ids.
>
> **3.2 FINDING.** Observing F0.2 needs an envelope that build refuses to write.
> - Quoted: "an envelope validates without a baseline ref".
> - Wrong: CLAUDE.md "Never write an envelope by hand or from a runner" forbids a fixture. "Validates" names the schema as the reader, while the seed names build. That is two readers for one falsifier.
> - Settle: Engineering proposes and Product rules one of two options. Either the test mutates a build-written envelope in memory, or fixtures under `tests/` are exempt. Product also rules which reader is F0.2's.
>
> **3.3 NOTE.** The link between F0.2 and `plants_expected` is stated twice and explained nowhere.
> - Quoted: §8 M00 "`plants` returns an empty list so the F0.2 test can read `plants_expected = 0`". The same wording is in ADR-0001 amendment 1 item 12.
> - Wrong: F0.2 is about the baseline ref, and `plants_expected = 0` is the plant rule.
> - Settle: Product says which test reads which field.
>
> **3.4 FINDING.** F0.3 has no seeded case and is only partly observable in the repo.
> - Quoted: "a PR merges without a ruling file after PR 2".
> - Wrong: the Seeded line holds two seeds, and neither is a PR without a ruling file. `cold-review-ruling` cannot fire on a seeded case inside M00. That matters under §10.5 and CLAUDE.md's "has not fired on its seeded case". Part of the observation is a branch-protection setting, which is not a file in the repo.
> - Settle: Product rules one of two options. Either PR 2 carries a seeded ruling-less PR (a third seed), or F0.3 is recorded as unfired at M00. Security names where the required-check setting is evidenced.
>
> **3.5 FINDING.** The ruling-file rule is circular.
> - Quoted: §5 "`cold-review-ruling` — a ruling file naming the PR exists on `main` before merge". R9 "No PR in this repo merges before its ruling file is on `main`".
> - Wrong: a file that must be on `main` first cannot ride in the PR it names. A separate PR carrying it would need its own ruling file and would count against the cap of four. The adoption ruling rode in its own PR (commit ecd2085, "cite PR #1 in the adoption ruling").
> - Settle: Product and Security rule whether the check reads the PR head or `main`. They also rule whether a ruling-only PR counts toward the cap.
>
> ## 4. Expected gate output
>
> Judged: "Expected on the baseline: traps 0/3; the three guardrail plants fail (no guardrail exists yet) and land in `never_passed`, with `plants_expected = 0` under the plant rule (§5) — that is the delta, not F0.1."
>
> The trap number is stated before the run.
>
> **4.1 FINDING.** The expected envelope verdict is not stated.
> - Wrong: on a first run all 15 goldens have never passed (P7), and `plants_expected = 0`. The `regression` gate then has no trigger, which implies GREEN at 0/15. The expected ordinary score (n/9) is not stated. "That is the delta" has no clear referent.
> - Settle: Product states in the ledger row the expected `verdict`, the expected ordinary count, and what "that" refers to.
>
> **4.2 FINDING.** The measured cell has three candidate writers and no stated content.
> - Quoted: §8 M00 "Done when: `make evals` writes an envelope with the baseline card and the row 0 measured value in `milestones/README.md`". CLAUDE.md PR 4 "Ledger 'measured' cell". CLAUDE.md "`make ledger` print the ledger with measured values".
> - Wrong: the writer could be `make evals`, a person at close, or `make ledger`. No section says which. No section says what the row 0 cell contains (traps n/3, ordinary n/9, or both).
> - Settle: Product rules the cell's content and its single writer.
>
> ## 5. Plain sentence
>
> Judged: "Before any guardrail, a plain model gets the trick questions wrong; every later number is measured against that."
>
> None of "governed", "secure" or "proven" appears in row 00.
>
> **5.1 FINDING.** "Before any guardrail" credits the traps to guardrails.
> - Wrong: the §9 traps are table facts (holdback, non-exclusive, sequel rights). The rights table and the tool repair them at M01. The three guardrail goldens are separate and are not "trick questions". A director will repeat that guardrails fix trick questions.
> - Settle: Product rewrites the opening clause at open, for example "With no data and no rules".
>
> **5.2 NOTE.** The sentence states a result before the run.
> - Quoted: "gets the trick questions wrong". §10.5 "only 'What happened' is filled at close".
> - Wrong: if F0.1 fires, the sentence is false on a page that may not change. "Guardrail" is also a term a director may need glossed.
> - Settle: Product words the sentence as a claim that survives either outcome.
>
> ## 6. Cut list and cap
>
> Judged: §8 M00 "Build:" through "Skills written at PR 4 from the by-hand open and close." M00 has no cut list.
>
> **6.1 FINDING.** Fifteen open build items, no cut list, and a loaded PR 4.
> - The fifteen items:
>   1. `src/baseline/`
>   2. `scripts/seed_slate.py` with its two data files
>   3. `data/clause_index.json`
>   4. the 15 goldens
>   5. `verdict.schema.json`
>   6. `verdict.build`
>   7. `verdict.gate`
>   8. the ledger, with `make ledger --plain`
>   9. `replay_history`
>   10. `validate`
>   11. the `Makefile` with five targets
>   12. six more seat subagents
>   13. the `cold-review-ruling` check
>   14. ADR-0002 with the diff-test
>   15. three skills
> - Wrong: `replay_history` has no seeded case and no falsifier at M00, and one envelope exists to replay. PR 4 carries the diff-test (code), three skills, the explainer, the video, attestations and the tag. A defect the cold review finds in the diff-test has no PR left, and that is RED by P10.
> - Settle: Product writes an ordered cut list for M00 in feasibility.md. It never cuts either seed. I would expect `replay_history` first.
>
> **6.2 NOTE.** A three-PR close has no PR 4.
> - Quoted: "frozen by ADR-0002 at PR 4", "Skills written at PR 4", and the §8 preamble "if the cold review of PR 2 finds nothing, PR 3 is the close PR".
> - Settle: Product rules that "PR 4" reads as "the close PR" in §8 M00.
>
> **6.3 NOTE.** No section says what an M00 attestation is.
> - Quoted: CLAUDE.md PR 4 "attestations" and §5.1 `close-milestone` "attestations, tag".
> - Wrong: nothing says what is attested at M00 or who attests it. The only concrete attestations in the spec are M08's three.
> - Settle: Product defines the M00 attestation or rules it not applicable.
>
> ## 7. Seats
>
> **7.1 BLOCK.** PR 1 must name a seat per path, and several paths it writes have none in §5.
> - Quoted: §8 M00 "PR 1 cites `SPEC/00-overview.md#8-M00` for `evals/goldens/`, `src/baseline/`, `scripts/` and `data/`, and names the seat per path in the PR body". §5 "A file no seat owns is deleted, not adopted".
> - Paths M00 writes that have no seat:
>   - `scripts/seed_slate.py`.
>   - `data/slate.json` and `data/rights_table.json`. The Data Owner row lists only `data/corpus/**` and `data/clause_index.json`, yet §9 calls the rights table "the truth".
>   - `tests/**`, which holds the P5 test and the F0.2 test.
>   - `docs/milestones/M00.md`, the generated `docs/milestones/README.md`, and `docs/video/**`. Product's row lists `docs/adr/**` only.
>   - `evals/history/**` and `evals/local/**`.
>   - Any root file other than `CLAUDE.md` and `Makefile`, such as a README, an ignore file or a dependency file.
> - Wrong: PR 1 cannot name seats that do not exist, and §5's own rule deletes these files.
> - Settle: before PR 1, Product rules a seat for each path. That is a §5 amendment, and ADR-0001 says "One more amendment is available to this ADR".
>
> **7.2 FINDING.** Two files or file sets carry two seats.
> - `milestones/M00/README.md` is Product's by `milestones/**`. It is also the Threshold Owner's by "Model ids for every role… pinned by the Threshold Owner at the top of `milestones/M00/README.md`".
> - Every `milestones/MNN/rulings/<slug>.md` is Product's by path and carries a `seat:` that names another seat.
> - Settle: Product rules that the path decides ownership and `seat:` names who ruled, or carves the two cases out in §5.
>
> **7.3 NOTE.** PR 2's workflow file is unnamed.
> - Wrong: §8 M00 names the `cold-review-ruling` check but not its file under `.github/workflows/**` (Security). The §5.1 waiver covers PR 1 only, so PR 2 needs a `security-reviewer` report.
> - Settle: Security names the file at PR 2.
>
> **7.4 NOTE.** The adoption ruling sits outside the §6 path pattern.
> - Wrong: `milestones/adoption/rulings/adopt-spec00.md` is on `main`. §6 gives the pattern `milestones/MNN/rulings/<slug>.md`. If `validate` globs only `MNN`, this ruling goes unchecked.
> - Settle: Engineering states the glob, and Product rules whether `adoption` is a legal folder.
>
> ## 8. Contradictions
>
> **8.1 FINDING.** A line in the M00 README cuts against F0.1 and P6.
> - Quoted: `milestones/M00/README.md` "If a trap fails, fix the trap or the prompt, not the model." F0.1 "record, do not tighten in this milestone". P6 "never improved".
> - Wrong: "fails" is ambiguous. Read as "the baseline passes a trap", the line orders the tightening that F0.1 forbids. It also orders a prompt edit to the control.
> - Settle: Product scopes the sentence to refagent from M01 or deletes it. The Data Owner rules on the traps.
>
> **8.2 FINDING.** One subagent writes a ruling, and subagents may not rule.
> - Quoted: §5.1 "`engineering-cold-reviewer`… writes the ruling file `cold-review-ruling` requires". §5.1 "A subagent's output is a draft or a report, never a ruling". §5 subagent row "May not: rule; write to any seat-owned path". CLAUDE.md "Reports are drafts, never rulings".
> - Wrong: PR 1 writes this subagent's prompt and tool list. It must know whether the subagent gets Write on `milestones/**`.
> - Settle: Product rules that the subagent drafts and the Engineering seat commits, or amends the §5 row.
>
> **8.3 FINDING.** What `evals-local` writes at PR 1 is unstated.
> - Quoted: §8 M00 "at PR 1 `evals-local` and `validate` run". CLAUDE.md PR 1 "Nothing that makes it pass". CLAUDE.md "Only `src/verdict/build.py` writes envelopes". CLAUDE.md "`make evals-local` same… writes `evals/local/` only".
> - Wrong: `build.py` does not exist at PR 1, so `evals-local` cannot write an envelope. The spec does not say what it writes instead.
> - Settle: Engineering states in feasibility.md that at PR 1 `evals-local` writes raw observations only. Product confirms.
>
> **8.4 NOTE.** The schema filename differs between the two files.
> - Quoted: §6 and §8 M00 "`verdict.schema.json`", against CLAUDE.md "`src/verdict/schema.json`".
> - Wrong: the filenames differ. SPEC/00 wins.
> - Settle: Product fixes one name before PR 2 writes the file.
>
> **8.5 NOTE.** The SPEC/00 header disagrees with itself.
> - Quoted: header "Status: DRAFT" and "Adopted by ADR-0001". ADR-0001 front matter says `status: Accepted`.
> - Wrong: the spec is marked draft and adopted at once.
> - Settle: Product sets the status line.
>
> BLOCK: 2 · FINDING: 17 · NOTE: 9

## 2. What this PR does about the two BLOCKs

Neither BLOCK is ruled here. A report is not a ruling and neither is
this note. Each BLOCK is carried as a stated assumption, repeated under
**Unsure** in the PR body, for the named seat to rule on before merge.
Golden ids become immutable when they reach `main`, not before.

**BLOCK 1.1 (no scorer at M00). Data Owner rules.** This PR builds no
scorer. The runner writes raw observations only (report 8.3): the
model's text, the JSON parsed from it, the stop reason, tokens, latency.
The three traps and three guardrail goldens are read against `expected`
by hand in §6 of this note, under both readings the report names:

- *Full match*: `table_row`, `clause_id` and every `answer_fields` value
  equal. The baseline reads no table, so this is 0 by construction and
  F0.1 cannot fire under it.
- *Answer-fields match*: `available`, `exclusive` and `constraints`
  equal; citations ignored. F0.1 can fire under this reading, including
  by a lucky guess.

Assumption made: **F0.1 is judged on the answer-fields reading**, because
a falsifier that cannot fire measures nothing. Trap questions carry a
bait fact (the thing a person would say in the hallway) and never the
table fact that settles the answer. Ordinary questions carry no facts
beyond title, territory, platform and date. PR 2's `verdict.build` needs
the Data Owner's ruling on which reading it implements before it is
written.

A guardrail golden passes only when Converse returns
`stopReason: guardrail_intervened` (BLOCKED) or a guardrail trace shows
masking (MASKED). The baseline configures no guardrail, so these fail by
construction; a model that declines on its own is not BLOCKED. That
matches §8 M00: "the three guardrail plants fail (no guardrail exists
yet)".

**BLOCK 7.1 (paths with no seat). Product rules.** The PR body names a
seat for every path this PR writes. For paths §5 does not list, the seat
named is a proposal:

| Path | Proposed seat | Why |
|---|---|---|
| `scripts/seed_slate.py` | Engineering | code |
| `data/slate.json`, `data/rights_table.json` | Data Owner | §9: "the rights table is the truth"; the Data Owner owns what CORRECT means |
| `docs/milestones/M00.md` | Product | explainers are Product's by §5.1 (`docs-writer` is called by Product) |
| `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `README.md`, `LICENSE` | not touched by this PR | already on `main` with no seat; Product rules or deletes |

Settling it is a §5 amendment (ADR-0001 amendment 2). This PR does not
edit SPEC/00.

## 3. The false state

Claim 0 is false if any of these is true:

1. The baseline answers a trap correctly. The traps are then too easy to
   show a delta, and "measured against a baseline that loses" is not what
   later rows are measured against.
2. An envelope exists with no baseline card ref. A later number is then a
   number, not a delta.
3. A PR merges after M00 PR 2 with no ruling file naming it.

What this PR plants (the seeded commit is recorded in the ledger row):

- `evals/goldens/v1/g-010.yaml`, `g-011.yaml`, `g-012.yaml`: the three
  traps. The input that makes the claim false is any one of these three
  questions answered with the `answer_fields` in its file.
- `evals/goldens/v1/g-013.yaml` to `g-015.yaml`: the three guardrail
  goldens. No guardrail exists, so under the plant rule (§5) they are
  goldens that have never passed, not plants, and `plants_expected = 0`
  until M03.
- `src/baseline/`: the control that must lose. Nova Micro
  (`us.amazon.nova-micro-v1:0`, us-west-2), Converse, one system prompt,
  no tools, no guardrail, no retrieval, temperature 0, `maxTokens` 512.
  It reads nothing under `data/`.

What this PR cannot plant (report 1.2): "a run without a baseline card"
needs the card format, which belongs to `src/verdict/` in PR 2. PR 2
plants it as its first commit, before `build.py` exists, so the plant is
in the repo before the code that reads it.

## 4. The code that will read the answer (`src/verdict/`, PR 2)

None of it exists in this PR.

- `src/verdict/build.py` is the only writer of envelopes. It reads the
  raw observations a runner wrote, reads `expected` from
  `evals/goldens/v1/`, scores each golden, and refuses to write an
  envelope when no baseline card is supplied. That refusal is the read of
  seed 2.
- `src/verdict/gate.py` is the only reader of envelopes. It reads
  per-golden pass for `g-010` to `g-012` and carries the plant rule as
  one line, so `g-013` to `g-015` land in `never_passed` and
  `plants_expected = 0`.
- `verdict.schema.json` (`additionalProperties: false`) requires the
  baseline card ref. F0.2's test reads this.
- A test asserts that runner, build and gate can disagree (P5).
- The runner in this PR (`src/baseline/run.py`) writes raw observations
  to the path given by `--out`. It scores nothing and writes no envelope.

## 5. Falsifiers, and what each would look like in the repo

**F0.1 — the baseline passes a trap.**
In this PR: §6 below shows a trap whose parsed `available`, `exclusive`
and `constraints` equal the golden's `answer_fields`. From PR 2: an
envelope under `evals/history/` whose per-golden entry for `g-010`,
`g-011` or `g-012` has `pass: true` on a baseline run. Response if it
fires: record it here, do not edit the trap or the prompt in this
milestone.

**F0.2 — an envelope validates without a baseline ref.**
From PR 2: a test under `tests/` that takes an envelope `build.py` wrote,
removes the baseline card ref, and finds it still validates against
`verdict.schema.json`; or `build.py` exits 0 when run with no baseline
card. Either is F0.2. Nothing in this PR can show it.

**F0.3 — a PR merges without a ruling file after PR 2.**
In the repo: a merge commit on `main` for PR number N, N ≥ 3, where no
file under `milestones/*/rulings/` has `pr: N` in its front matter at
that commit. `git log --merges main` plus a grep shows it. Outside the
repo: `cold-review-ruling` not listed as a required check on `main`
(Security enables it after this PR merges). No seeded case for F0.3
exists in M00 (report 3.4).

## 6. Raw results of the PR 1 local run

Not evidence (P11). The file is `evals/local/m00-pr1-baseline.json`,
which `.gitignore` excludes; the trap and guardrail entries are pasted
here so the reading can be checked without it.

_Filled after `make evals-local` runs at the seeded commit._
