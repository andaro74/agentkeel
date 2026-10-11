---
# M09 PR 2 (#50), Engineering's key over the Engineering paths this PR
# touches: the two readers, the platform check's three changed readings,
# validate's new check, build, the gate, the schema, the answer record's
# schema, the ledger, the Makefile, the registry script, the observer, the
# tests and the fixtures README. The cold review (engineering-cold-reviewer)
# ran on this PR's diff before it opened (R9); its report is below.
# src/validate/agent.py's pin reading is Engineering's code under the Rule
# Owner's rule R10 (pr2-rule-owner.md).
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/validate/agent_rules.py
  - src/validate/agent.py
  - src/validate/agent_goldens.py
  - src/validate/checks.py
  - src/verdict/agent_rules.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/schema.json
  - src/verdict/answer.schema.json
  - src/verdict/__init__.py
  - src/ledger.py
  - Makefile
  - scripts/observe_rules.py
  - scripts/registry.py
  - tests/test_m09_seeds.py
  - tests/test_m09_readers.py
  - tests/test_m09_platform.py
  - tests/test_p5_disagree.py
  - tests/test_gate.py
  - tests/test_m07_readers.py
  - tests/test_bootstrap.py
  - tests/fixtures/README.md
evidence:
  - SPEC/09-per-agent-rules.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M09/feasibility.md
  - milestones/M09/rulings/pr1-engineering.md
  - milestones/M09/rulings/pr2.md
pr: 50
---

# Ruling: M09 PR 2, Engineering

Ruled by andaro74 as Engineering, 2026-10-11, as written.

## What this covers

The readers SPEC/09 §6 names, by the names the seed tests fixed:

- **`src/validate/agent_rules.py`**: `load`, `merge`, `merge_errors`,
  `rules_errors(agent_dir, rules=None)`, `digest`, `baseline_errors` and
  `check` (validate's twenty-first check). Add-only as SPEC/09 §2 and the
  rule-owner report's list; the thirty-topic limit refuses at the count
  naming the file that took it over (R5, this seat); Bedrock's per-topic
  limits are read here, before a deploy fails (cut 5 not taken, PR 1's
  Unsure). S1, S2 and S5 read.
- **`src/validate/agent.py`**: `guardrail_errors` admits, for an agent with
  `rules/`, a pin that is not null and not refagent's, and refuses one the
  registry does not hold when the deploy gives it (`--held-guardrail`);
  `evaluate` calls `rules_errors`. **`agent_goldens.py`**: the four kinds,
  `expected` shaped per kind, a plant named by its control (F9.4).
- **`src/verdict/agent_rules.py`**: `plants(record, blocks)` returning
  `{read, held, expected, fired, reasons, fired_by}` by the membership
  rule; `guardrail(record, read_back, tree_digest)` for F9.1 (the registry
  row stands in when the read-back is not granted, named `source:
  registry`); `heads` and `weakened` for F9.4 and F9.2; `record` for build.
  S3 read.
- **`src/verdict/build.py`**: `--rules` into `agent_rules`, recorded,
  never gated; `F9_5` joined with build's own count of refagent's plants;
  `build answer` writes each golden's observation (`stop_reason`,
  `guardrail_topics`, `parsed`: R7's shape) and the stack's pin
  (`--guardrail`), and scores an agent's plant by its own controls'
  `blocks`. **`gate.py`**: `CLAIM_9_CHECKS`, held from `M09_READERS`
  (`9d2f3a7`, named in `2608711`); `F9_5` held again to the gate's own
  count (P5); `READ_THE_RULES`, `rules_misses`, `rules_reading`;
  `measured(rules=...)`. **`ledger.py`** prints row 9's reading.
- **`scripts/observe_rules.py`**: raw records only; the digest computed
  from bytes it fetched by the merge commit and `git show` of main's
  baseline (cold review N7 on PR 1); a run file with `observed: null`
  written not made. **`scripts/registry.py`**: `write --guardrail
  --rules-digest`, `guardrail --name`.
- **Tests**: `test_m09_seeds.py` (six markers off, the run's on),
  `test_m09_readers.py`, `test_m09_platform.py`, five P5 cases, the
  required-checks list and the check count in two older tests.

`tests/test_m09_seeds.py`: 8 passed, 1 xfailed; `--runxfail` 8 passed, 1
failed (the run not made). The full suite passes on the committed tree.
`make validate` twenty-one ok; `make ledger` exit 0 and row 9's reading of
the latest envelope RED on `agent_rules not read`.

## From the other two reads

- `security-reviewer` (0 BLOCK, 1 FINDING, 22 NOTE; verbatim in the PR
  body and `pr2-security.md`): the observer's two unguarded reads (the run
  file, an earlier part's file) now write an observation with the error,
  never a failed job. **Repaired.**
- `rule-owner` (0 BLOCK, 5 FINDING, 4 NOTE; verbatim in the PR body and
  `pr2-rule-owner.md`): no item on this seat's paths beyond what the
  Rule Owner's and Product's files take.

## Unsure, for this seat

- The M02 seed test (`test_s1_one_key_on_a_relaxation_is_refused`) diffs
  the working tree against a worktree of HEAD, so it fails locally while
  seat-owned files are uncommitted and passes on the committed tree; CI
  checks out a commit. Not changed here.
- `plants` returns `fired_by` (the topics read per hit) as PR 1's
  Engineering Unsure proposed; the reasons carry the miss. The cell quotes
  neither at M09: `rules_reading` prints n of m and each falsifier's state.

## Cold review

`engineering-cold-reviewer`, on the diff `460990b...d3897ab` (40 files),
without the PR body: **0 BLOCK, 5 FINDING, 5 NOTE**. Shape, plant, P5 and
owned paths held. Each item's disposition, then the report verbatim. The
repairs are the commit after `d3897ab`, before the PR opened; the
measurement is of the tree that ships.

| # | Disposition | Seat |
|---|---|---|
| F1 | **Repaired.** F9_2's guardrail half is read from the read-back alone and is **unread**, not a miss, when the read is not granted: `baseline_in_guardrail: null` on the entry (schema), the cell says "(guardrail half unread)", and `rules_misses` finds nothing on it. The README's by-hand step 4 and `pr2-security.md` R4 say so. The grant deployed before PR 3's run makes both halves read | Engineering; Security (the sentence) |
| F2 | **Repaired.** `_check` takes the platform App's run only (`infra/platform_identity.json`'s `platform_app_id`, which the observer records on every run) and the latest by `completed_at` (N2); a test with an impostor App and an older run | Engineering |
| F3 | **Repaired by Security** (`pr2-security.md`): `TagResource` out of the request-tag statement; the deploy boundary denies `TagResource` and `UntagResource` on an untagged guardrail; a test | Security |
| F4 | **Repaired.** The test writes its own run file with `observed: null` | Engineering |
| F5 | **Repaired.** `merge_errors` refuses a `messages` that is not the two strings, naming it; `merge` no longer raises on it; a test | Engineering |
| N1 | **Taken.** `M09_READERS` a plain string, the guard dropped | Engineering |
| N2 | Repaired with F2 | Engineering |
| N3 | Kept as it is: `read_from` on the envelope says which ref was read | Engineering |
| N4 | **Taken by Product** (`pr2.md`): the quickstart says no agent with `rules/` has been deployed yet | Product |
| N5 | Recorded | Engineering |

### The report, verbatim

> Read: the diff 460990b...d3897ab (40 files)
>
> What I read: `git diff origin/main...HEAD` (40 files, the copy at `.git/cold-review.patch`), `git log origin/main..HEAD` (five commits: e2c04ab, 9d2f3a7, 2608711, 353a8c4, d3897ab), row 9 and the "M09 PR 2 (no tag)" header row of `milestones/README.md` (lines 65 and 50), and `milestones/M09/README.md`. No PR body, no commit message bodies.
>
> What I ran (nothing that costs money), all on the committed tree:
> - `uv run pytest tests/test_m09_seeds.py -q` → 8 passed, 1 xfailed (as stated)
> - `--runxfail` → 8 passed, 1 failed: `test_the_plant_run_was_made`, "seed run: the run has not been made" (as stated)
> - `uv run pytest tests/test_m09_readers.py tests/test_m09_platform.py tests/test_p5_disagree.py -q` → 47 passed
> - `make validate` → 21 checks ok, the new one last: "the platform baseline, and every agent's rules merging onto it add-only"
> - `make ledger` → exit 0; row 9 OPEN, Measured `—`; "as row M09 reads it" ends `agent_rules not read: the envelope records no plant run; RED; envelope 20a698eb…` (the plant going RED under the measurement)
> - `make plants` → S1–S5 and the run listed, every reader "in the tree"
> - `git diff origin/main...HEAD --stat -- evals/goldens thresholds.yaml src/baseline agents/ data/ .github/CODEOWNERS .claude/ SPEC/ docs/adr` → empty
> - `git rev-parse 9d2f3a7` → `9d2f3a7356d5ee7e…`, matching `M09_READERS`
>
> **1. Shape (PR 2 of 4).** Held. The diff holds the readers SPEC/09 §6 names and nothing that makes the plant pass: no fixture repository, no golden under `evals/goldens/`, no bar, nothing under `src/baseline/`, no gateway, no policy engine, no public caller (`git diff --stat` on those paths is empty). The reader of the claim is not built in a last PR: `src/verdict/agent_rules.py`, `agent_rules` on the envelope, `CLAIM_9_CHECKS` and `READ_THE_RULES` land here. The Product paths (`docs/developer/*`, `docs/milestones/M09.md`, `milestones/**`) are under `rulings/pr2.md`; "What happened" in `docs/milestones/M09.md` is untouched (only the Run and The check rows change, lines 67–68).
>
> **2. The plant.** Held. On this PR's own envelope `agent_rules` is absent (no run file `observed`, so `scripts/observe_rules.py` writes `made: false` and `build --rules` records every falsifier unread; on the latest CI envelope there is no field at all) and `gate.rules_misses` (`src/verdict/gate.py`, new lines 1089–1116) returns a miss in either case; `measured(rules=True)` turns a GREEN verdict RED. `make ledger` prints, as row M09 reads it, `agent_rules not read: the envelope records no plant run; RED`. The markers came off in the commits that landed each reader (`tests/test_m09_seeds.py` diff: S1 x2, S2 x2, S5 in e2c04ab; S3 in 9d2f3a7); the run file's stays on and fails under `--runxfail` for its planted reason. The check cannot pass on empty input: `plants()` with no named plant is `held: False` ("no plant is named", `src/verdict/agent_rules.py` ~line 103), and `rules_misses` adds "none is named, so none can have fired" when `expected < 1`.
>
> **3. P5.** Held. `scripts/observe_rules.py` writes a JSON observation with `"what": "...not an envelope; rules nothing"` and reads the answer record, GitHub, the registry and `GetGuardrail`; it reads no envelope. Only `src/verdict/build.py` writes `agent_rules` (`compose_envelope`, under `if gated and rules_reading is not None`) and the answer record's new `observations`/`guardrail` (`compose_answer`). Only `src/verdict/gate.py` reads `agent_rules` (`rules_misses`, `rules_reading`); `src/ledger.py` goes through `gate.measured_at`. The gate holds `F9_5` to its own plant count again (`judge`, inside the agent-scope block, after the F7_5 clause), and `tests/test_p5_disagree.py` has a case for each.
>
> **4. Frozen and owned paths.** Held. `src/baseline/` untouched. `rules/baseline.yaml` (Rule Owner) is in `rulings/pr2-rule-owner.md` `authorises`; `.github/workflows/deploy.yml`, `evals.yml`, `infra/**`, `infra/workflows.sha256` (Security) in `pr2-security.md`; the Product paths in `pr2.md`; every Engineering path in `pr2-engineering.md`. `agents/refagent/**`, `evals/goldens/`, `thresholds.yaml`, `data/`, `.github/CODEOWNERS` are not in the diff. `scripts/observe_rules.py` is matched by the existing `/scripts/observe_*.py` line (CODEOWNERS:69) and `rules/baseline.yaml` by `/rules/` (CODEOWNERS:35), so no CODEOWNERS line is owed. All four ruling files carry `ruling`, `seat`, `authorises`, `evidence`, `pr: 50` and read "Ruled by: pending".
>
> **FINDING 1 — the registry fallback (SPEC/09 §9 cut 3) can never hold F9_2, so without R4's grant deployed row 9 is RED whatever the run shows.** `src/verdict/agent_rules.py`, `weakened()`: when `read_back.source` is not `"read_back"` it appends "the built guardrail was not read back: whether it holds every baseline rule rests on F9_1's digest" to `reasons`, and `_entry` makes `held` False whenever `reasons` is non-empty. `gate.rules_misses` then reports `F9_2 not held` and the cell reads RED. `tests/test_m09_readers.py::test_the_registry_row_stands_in_for_the_read_back_when_the_read_is_not_granted` asserts exactly this (`reading["F9_2"]["held"] is False`). But `milestones/M09/README.md` lines 160–161 ("If R4's grant is not deployed when PR 3's run reads, F9.1 reads the registry row's digest and the envelope says so") and `rulings/pr2-security.md` R4 ("F9.1 reads the registry row's digest instead") present the fallback as keeping the reading alive. It does not: the fallback keeps F9_1 and loses F9_2. Either say so in the README's by-hand step 4 (the grant must be deployed before PR 3's run or the row is RED on F9_2), or make the fallback an `unread` second half of F9_2 rather than a `not held` — a decision to state before PR 3, not after.
>
> **FINDING 2 — the heads reader takes any check run named `platform-check`, not the platform App's.** `src/verdict/agent_rules.py`, `_check()`: `runs = [r for r in pull.get("check_runs") ... if r.get("name") == "platform-check"]; return runs[-1]`. The observer records `app_id` on every run (`scripts/observe_rules.py`, `check_runs()`), and `scripts/platform_check.py:100` holds a run to the App's id, but the reader ignores it. A workflow job in the fixture repository named `platform-check` posts a check run of that name through GitHub Actions, and F9_2/F9_4 would be read from it. Hold `_check` to the App id the observer wrote (5144253, which `test_the_observer_computes_the_digest_from_the_merge_commit_and_main_and_reads_the_checks` already uses) or record which app's run was read in the entry.
>
> **FINDING 3 (Security's path, named for the seat) — the execution role can tag refagent's untagged guardrail and then reach it.** `infra/bootstrap/app.py`, statement `MakeAnAgentsGuardrailOnlyWithItsTag`: `actions=["bedrock:CreateGuardrail", "bedrock:TagResource"]`, `resources=[guardrail/*]`, `conditions={"Null": {"aws:RequestTag/agentkeel:agent": "false"}}`. A `TagResource` on refagent's guardrail with `agentkeel:agent` in the request satisfies this allow, and the deploy boundary's narrowed deny (`NeverTouchAGuardrailThatIsNotATaggedAgentsOwn`, condition both RequestTag and ResourceTag null) does not fire because RequestTag is present. Once tagged, every action in `ReadUpdateVersionAndRemoveATaggedAgentsGuardrailOnly` reaches it. The prose "refagent's, untagged, stays out of reach" (app.py comment above the statements; `rulings/pr2-security.md` R3) is wider than the policy. The narrow fix is to hold `TagResource` to `aws:ResourceTag/agentkeel:agent` non-null (an already-tagged resource; CloudFormation passes create-time tags in the create request) or to add a deny on `TagResource` where the ResourceTag is null. `tests/test_m09_platform.py::test_the_execution_role_makes_a_guardrail_only_with_the_tag_and_touches_only_a_tagged_one` passes on the current shape and would not catch this.
>
> **FINDING 4 — a reader test is wired to the real run file and will fail the suite on the PR that makes the run.** `tests/test_m09_readers.py::test_the_observer_writes_a_run_not_made_and_reads_nothing` calls `observer.main(["--read", "github,bucket,registry,guardrail", "--out", ...])` with no `--run`, so it reads `milestones/M09/runs/f9_3_plant_run.yaml`, and monkeypatches `gh` to raise `AssertionError`. When the owner fills `observed` (PR 3), `observe()` calls `read_github`, whose `except` catches `(URLError, KeyError, TimeoutError, OSError)` only; the AssertionError escapes, the test fails, and `evals.yml`'s pytest step (line 374, which produces the JUNIT the Makefile's F9 cases are read from) fails before the envelope. Give the test its own run file with `observed: null` (the sibling test already does this with `--run`).
>
> **FINDING 5 — `merge()` raises instead of refusing on a `messages:` that is not a mapping.** `src/validate/agent_rules.py`, `merge()`: `"messages": {**(baseline.get("messages") or {}), **(agent.get("messages") or {})}`. An agent file with `messages: some string` or a list makes `{**"..."}` raise `TypeError`; `merge_errors` calls `merge` on its last line, so `rules_errors` and `evaluate()` crash rather than name the refusal. The check run errors (so the head is not admitted; no bypass), but the stated rule "every refusal named" (agent.py docstring, line ~80) is not met for this input, and the two message values are not checked to be strings before the construct passes them to `CfnGuardrail`. Add the shape check to `merge_errors` beside the `denied_topics`/`pii` ones.
>
> **NOTE 1.** `src/verdict/__init__.py`: `M09_READERS: str | None = "9d2f3a7356d5"` and `required_checks` guards with `M09_READERS and descends_from(...)`, unlike M05–M08's plain strings. Harmless; the guard is dead.
>
> **NOTE 2.** `_check()` returns `runs[-1]`. GitHub's check-runs list is not guaranteed newest-last; a head with several `platform-check` runs (the five-minute schedule re-posts) may be read from the oldest. The observer writes `completed_at`; the reader could take the latest.
>
> **NOTE 3.** `scripts/observe_rules.py`, `baseline_on_main()` falls back `origin/main` → `main` → `HEAD` and records `read_from`. `evals.yml` checks out with `fetch-depth: 0` (lines 220, 272), so `origin/main` is there in CI; the fallback is visible on the envelope if it ever fires.
>
> **NOTE 4.** `docs/developer/quickstart.md` §5a: "The platform builds it from your rules on the baseline when it deploys your first merge" and `template-README.md`: "the platform builds a guardrail for your agent ... and puts your agent's calls through it" are stated flat; no deploy of an agent with `rules/` has happened (the first is PR 3's run, as `deploy.yml`'s header says in its last line). `docs/milestones/M09.md` hedges ("whether this holds here is read at PR 3"); the developer pages do not. Product's call; not one of the three forbidden words.
>
> **NOTE 5.** Checked and consistent, for the record: the digest recipe is the same in all three places (`agent_rules.digest`: baseline first, then `guardrail.yaml`, then `redteam.yaml` if present, CRLF→LF; the construct `_agent_guardrail` and the observer's `read_github` use the same file order and presence rule); the version description `rules sha256 <digest>` is written by the construct and compared exactly by `guardrail()`; the observer's `REFUSED` regex matches `scripts/platform_check.py:630`'s summary line shape; `src.validate.agent` returns 1 on a refusal, so the deploy's `--held-guardrail` step under `set -euo pipefail` does stop the deploy; `check_from_cases` matches by test name across the whole JUNIT, so `F9_1_CASES` mixing `test_m09_seeds.py` and `test_m09_readers.py` works; row 9's "PRs used" stays `1 / 4` at PR 2 as row 8's did at M08 PR 2.
>
> **Draft ruling line.** DRAFT — clear as the measure: the plant goes RED on this PR's own envelope by the reader this PR builds, nothing in the diff makes it pass, P5 and the owned paths hold. Findings 2, 4 and 5 are in this seat's paths and fit in this PR; Finding 1 needs a sentence (or a one-line reader change) before PR 3's run is counted; Finding 3 is Security's and goes to `rulings/pr2-security.md`'s Unsure. The Engineering seat rules; this file does not.
>
> BLOCK: 0 · FINDING: 5 · NOTE: 5
