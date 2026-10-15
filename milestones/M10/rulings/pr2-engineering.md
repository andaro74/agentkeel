---
# M10 PR 2 (#55), Engineering's key over the Engineering paths this PR
# touches: the two readers, the platform check's call, the schema, build,
# the gate, the ledger, the plants listing, the gates' field table, entry 7,
# run.py, the Makefile, the observer, the tests and the fixtures. The cold
# review (engineering-cold-reviewer) ran on this PR's diff before it opened
# (R9); its report is below. The two manifests' `callers: []` are the Tool
# Owner's field under pr2-tool-owner.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/verdict/caller.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - src/verdict/schema.json
  - src/verdict/__init__.py
  - src/verdict/plants.py
  - src/ledger.py
  - src/gates/two_key.py
  - src/gates/__init__.py
  - src/validate/callers.py
  - src/validate/agent.py
  - src/validate/semver.py
  - src/manifest/schema.json
  - src/agent/run.py
  - scripts/observe_caller.py
  - Makefile
  - tests/**
evidence:
  - SPEC/10-public-caller.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M10/feasibility.md
  - milestones/M10/rulings/pr1-engineering.md
  - milestones/M10/rulings/pr2.md
pr: 55
---

# Ruling: M10 PR 2, Engineering

DRAFT. Ruled by: pending.

## What this covers

The readers SPEC/10 §6 names, by the names the seed tests fixed:

- **`src/verdict/caller.py`**: `from_raw(record)` for both raw shapes (the
  access-log line, the data event), refusing a credential by key words and
  value shapes and dropping `DROPPED_KEYS` before anything is recorded;
  `calls(records, stated, callers, max_seconds)` returning `{read, held,
  admitted, refused, expected_admitted, expected_refused, reasons, steps}`
  with the strings S1 reads; `guardrail_through_the_door(answer)`;
  `record(observation, max_seconds)` for `build`. S1 read.
- **`src/validate/callers.py`**: `callers_errors(manifest)`, called from
  `evaluate()` under its own named check. S2 read. **`src/manifest/schema.json`**:
  the `callers` key in SPEC/10 §2's shape. S2's schema case read.
- **`src/gates/two_key.py`**: entry 7, `caller_relaxations`, under ADR-0016;
  **`src/gates/__init__.py`** attributes `callers` to the Tool Owner. S3 read.
- **`src/verdict/build.py`**: `--caller` into `caller`, recorded, never
  gated. **`gate.py`**: `CLAIM_10_CHECKS`, held from `M10_READERS`
  (`5e2cf70`, named in `2898100`); `READ_THE_CALLER`, `caller_misses`,
  `caller_reading`; `measured(caller=...)`. **`ledger.py`** prints row 10's
  reading. **`src/verdict/schema.json`**: `caller`.
- **`scripts/observe_caller.py`**: raw records only; stepped by the request
  ids the owner wrote; `stated` from the run file; a credential never
  copied; `DROPPED_KEYS` dropped and named; a line naming another agent
  not copied. **`src/agent/run.py`**: the door path.
- **Tests**: `test_m10_seeds.py` (five markers off, the run's on, S4's
  first guard rewritten, `with_nobody_admitted` for the older guards),
  `test_m10_readers.py`, `test_m10_platform.py` (the door's code run with a
  key made for the test; the doored fixture's own cdk-nag report read),
  four P5 cases, the required-checks list, the M02 seed patch's context,
  the M09 deploy-layout copy.

`tests/test_m10_seeds.py`: 9 passed, 1 xfailed; `--runxfail` 9 passed, 1
failed (the run not made). The full suite passes on the committed tree.
`make validate` twenty-one ok; `make ledger` exit 0 and row 10's reading of
the latest envelope RED on `caller not read`.

## From the other three reads

- `security-reviewer` (0 BLOCK, 7 FINDING, 10 NOTE; verbatim in the PR
  body and `pr2-security.md`): on this seat's paths, the observer refuses a
  line naming another agent and `build` names one (F1); the authoriser's
  tests for a malformed payload and the clipped context (F2); the doored
  fixture's cdk-nag report read in a test (F4). **Repaired.**
- `tool-owner` (0 BLOCK, 3 FINDING, 14 NOTE; `pr2-tool-owner.md`): entry
  7's one refusal string (F3); the semver docstring. **Repaired.**
- `data-owner` (0 BLOCK, 3 FINDING, 9 NOTE; `pr2-data-owner.md`): the drop
  list, the credential match, the no-token reading, the schema's reason
  enum, the placeholder table, the fixture's comment, the HIDDEN test.
  **Repaired.**

## Cold review

`engineering-cold-reviewer`, on the diff `a67de63...afd7f31` (59 files),
without the PR body: **0 BLOCK, 2 FINDING, 6 NOTE**. Shape, plant, P5 and
owned paths held. Each item's disposition, then the report verbatim. The
repairs are the commit after `afd7f31`, before the PR opened; the
measurement is of the tree that ships.

| # | Disposition | Seat |
|---|---|---|
| F1 | **Repaired.** `from_raw` raises `Unreadable` on a wrapper whose `raw` the observer refused to copy, with the observer's error; stepped, it is F10.3's and no record; a test feeds `record()` the stripped shape with `step: admitted` | Engineering |
| F2 | **Repaired by Security** (`pr2-security.md`): the deploy step's comment says the token is written to the step's output on the runner, masked, and nowhere else | Security |
| N1 | The five ruling files exist now, each `pr: 55` | Product; Security; Tool Owner; Data Owner; Engineering |
| N2 | The run file's `door:` comment stays as the record of what was proposed; the plant is untouched | Product |
| N3 | Recorded in the observer's docstring: it refuses what `build` refuses, by the same code | Engineering |
| N4 | **Taken by Security**: the docstring says "is expected never to reach this code" | Security |
| N5 | Recorded: the `platform` branch in `calls` is reached by a direct call only; a comment at PR 3 | Engineering |
| N6 | Recorded: the F10_2 case synthesises two stacks, as M09's did | Engineering |

### The report, verbatim

> Read: the diff a67de63...afd7f31 (59 files), the thirteen commits `git log a67de63..HEAD` (file stats and the `tests/test_m10_seeds.py` hunks per commit, not the message bodies), `milestones/README.md` row 10 and the "M10 PR 1 (no tag)" / "M10 PR 2 (no tag)" header rows (lines 53, 54, 70), and `C:\Users\andar\code\agentkeel\milestones\M10\README.md`. No PR body, no ruling file (none for this PR exists yet in `milestones/M10/rulings/`; only `pr1.md` and `pr1-engineering.md` are there, as the brief said).
>
> Runs (all free): `uv run pytest tests/test_m10_seeds.py -q` → 9 passed, 1 xfailed; `--runxfail` → 9 passed, 1 failed, `tests/test_m10_seeds.py:290 AssertionError: seed run: the run has not been made`; `uv run pytest tests/test_m10_readers.py tests/test_m10_platform.py tests/test_p5_disagree.py -q` → 66 passed; `make validate` → 21 ok; `make ledger` → exit 0, "as row M10 reads it" ends `caller not read: the envelope records no call; RED; envelope 8bb9b47a…` (that envelope's commit is behind a67de63, its file authored by `github-actions[bot]`); `make plants` → S1–S4 and the run all "in the tree"; `git diff a67de63...HEAD --stat -- evals/goldens thresholds.yaml src/baseline rules data/ tests/fixtures/m09` → empty.
>
> Draft ruling file, full text, for `C:\Users\andar\code\agentkeel\milestones\M10\rulings\pr2-engineering.md`:
>
> ---
> ruling: DRAFT
> seat: Engineering
> authorises:
>   - src/verdict/caller.py
>   - src/verdict/build.py
>   - src/verdict/gate.py
>   - src/verdict/schema.json
>   - src/verdict/__init__.py
>   - src/verdict/plants.py
>   - src/ledger.py
>   - src/gates/two_key.py
>   - src/gates/__init__.py
>   - src/validate/callers.py
>   - src/validate/agent.py
>   - src/manifest/schema.json
>   - src/agent/run.py
>   - scripts/observe_caller.py
>   - Makefile
>   - tests/**
> evidence:
>   - git diff a67de63...afd7f31 (59 files); git log a67de63..HEAD (13 commits)
>   - uv run pytest tests/test_m10_seeds.py -q → 9 passed, 1 xfailed; --runxfail → 1 failed at tests/test_m10_seeds.py:290 "seed run: the run has not been made"
>   - uv run pytest tests/test_m10_readers.py tests/test_m10_platform.py tests/test_p5_disagree.py -q → 66 passed
>   - make validate → 21 ok; make ledger → exit 0, row M10 reads "caller not read: the envelope records no call; RED" on envelope 8bb9b47 (github-actions[bot], behind a67de63); make plants → every M10 reader "in the tree"
>   - git diff a67de63...HEAD --stat -- evals/goldens thresholds.yaml src/baseline rules data/ tests/fixtures/m09 → empty
> pr: 55
> ---
>
> # M10 PR 2 — Engineering's cold review (the measure)
>
> ## 1. Shape (PR 2 of 4)
>
> Holds. Every reader SPEC/10 §6 names is in the diff and nothing makes the plant pass:
>
> - `src/verdict/caller.py` (new, 365 lines), `build.py:745-753` `caller_record` and `:957-960` writing `one_subject["caller"]`, `gate.py:167-172` `CLAIM_10_CHECKS`, `:231-238` `READ_THE_CALLER`, `:1162-1211` `caller_misses`/`caller_reading`, `src/ledger.py:142` adding `gate.READ_THE_CALLER` to the row loop; `src/validate/callers.py` (new) called from `src/validate/agent.py:217`; `src/manifest/schema.json:78-91` the `callers` key; `src/gates/two_key.py:266-281` `caller_relaxations` wired at `:343-345`; `scripts/observe_caller.py` (new) with its two `evals.yml` steps (`.github/workflows/evals.yml:89-91, 100-106`); the door in `infra/construct/governed_agent.py:285-440` and `infra/construct/door.py`; the delivery in `infra/security/app.py:317-382`; the documents (`SPEC/10`, `SPEC/00 §8 M10 item 2`, ADR-0016, quickstart §5b, template README, `docs/milestones/M10.md`, ledger row 54).
> - The run file `milestones/M10/runs/f10_x_caller_run.yaml` is not in the diff (`git diff --name-only`), its `observed: null` stands, and the one marker left is `tests/test_m10_seeds.py:290`.
> - Each seed's marker came off in the commit that landed its reader: `7ba474f` (schema `callers`; S2's schema case, one `-@expected_failure`), `a9ffab3` (`src/validate/callers.py`; S2's missing-key case), `7100808` (`two_key.py` entry 7 + ADR-0016; S3), `5e2cf70` (`caller.py`, `build`, `gate`, Makefile `F10_*_CASES`; S1). `3a929b6` is the raw fixture alone, no reader. `2898100` names `M10_READERS = "5e2cf705886c"` (`src/verdict/__init__.py:219`), which is `git rev-parse 5e2cf70` = `5e2cf705886cec47…`, the commit that put `F10_1`–`F10_5` into `Makefile:135-139, 148-152`.
>
> ## 2. The plant goes RED here
>
> Holds. `make ledger` on this tree prints, for row M10, every F0–F9 check passing and then `caller not read: the envelope records no call; RED` on envelope `8bb9b47…` (a CI-written envelope, `github-actions[bot]`, commit behind the base ref). `gate.caller_misses` (`src/verdict/gate.py:1162-1195`) returns that line for an envelope with no `caller` (`:1174-1175`) and, once `evals.yml` runs the observer on a run file whose `observed` is null, `the run has not been made…` plus `F10_1`–`F10_4 unread` (`:1181-1186`; shown by `tests/test_m10_readers.py::test_a_run_not_made_reads_every_falsifier_unread_and_row_10_reads_red`). Rows 0–9 are unchanged (`make ledger` exit 0; `caller=` is passed only for `milestone in READ_THE_CALLER`, `gate.py:1297-1298`).
>
> ## 3. P5
>
> Holds. `scripts/observe_caller.py` writes raw records, keys and errors only (`wrap`, `:240-246`; `blank`, `:283-290`; `observe`, `:293-304`); it computes no `held`. `src/verdict/build.py` alone writes `caller` (`:957-960`), through `caller.record` (`caller.py:304-365`). `src/verdict/gate.py` alone rules on it (`caller_misses`); `src/ledger.py:142` reads the gate. `tests/test_p5_disagree.py:377-421` has four new cases: observer-claims-vs-build-reads (`:377-389`), build GREEN without the five checks and the gate RED (`:392-401`), row 10 re-holding counts/N/plants (`:404-416`), and the readers anchor (`:419-421`). `tests/test_m10_readers.py:271-278` validates a held reading against `schema.json#/properties/caller`.
>
> ## 4. Frozen and owned paths
>
> Holds. `src/baseline/` untouched; no file under `evals/goldens/`, `thresholds.yaml`, `rules/`, `data/`, `tests/fixtures/m09/` (the stat is empty). The three `goldens/g-0*.yaml` and `rules/guardrail.yaml` in the diff are under `tests/fixtures/m10/s4-festival-desk-door/` (Engineering, `/tests/` in CODEOWNERS:80), byte-identical copies of M09's fixture (`diff -r tests/fixtures/m09/s1-festival-desk tests/fixtures/m10/s4-festival-desk-door` differs in `manifest.yaml` only: the header comment and `callers:` with `lantern-desk`, `box-office`). Seat-owned paths touched, each needing a ruling file this PR has not yet written: `agents/refagent/manifest.yaml:101-106` and `agents/ratings-helper/manifest.yaml:64-67` cite `milestones/M10/rulings/pr2-tool-owner.md`; `infra/bootstrap/app.py:363, 858, 934`, `infra/security/app.py`, `infra/construct/*`, `.github/workflows/deploy.yml:633`, `infra/workflows.sha256:173-177` cite `pr2-security.md`; `SPEC/10:10-11`, `SPEC/00`, ADR-0016, `docs/**`, `milestones/**` are Product's (`pr2.md`); ADR-0016 says it is keyed by the Tool Owner and "any second seat" (`docs/adr/ADR-0016…:13-16`). None of the five exists in the tree yet (see NOTE 1). `scripts/observe_caller.py` is taken by `/scripts/observe_*.py` (CODEOWNERS:69), `infra/construct/door.py` by `/infra/` (:52).
>
> ## 5. Does it work
>
> **FINDING 1 (Engineering; repair in PR 3).** `src/verdict/caller.py:165-178` `from_raw` reads an observer wrapper whose `raw` was stripped as if it were an access-log line, so the "unreadable record names no caller" path in `record()` (`:328-336`) is dead for the one shape the observer actually writes. `scripts/observe_caller.py:240-246` `wrap()` replaces a credential-bearing line with `{"source": "access-log", …, "raw": None, "error": …}`. In `from_raw`, `raw = record.get("raw") if isinstance(record.get("raw"), dict) else record` (`:170`) makes `raw` the wrapper itself, and `raw.get("source") == "access-log"` (`:175`) is true for the wrapper, so `_read_access_log` returns `{"subject": None, "outcome": "refused", "reason": "no identity", "time": None, …}` instead of raising `Unreadable`. Reproduced: `caller.from_raw({"source": "access-log", "raw": None, "step": "admitted", …})` → a refused record, no exception; the same wrapper with `source: "data-event"` → `Unreadable`. Effect on a live run where the admitted call's line carried a header: `calls()` reads it as a refusal of the `admitted` step with no event time; `record()` files `F10_4 not held: the admitted refusal's record has no event time…` and `calls admitted 0 of 1`, and `F10_3` reads **held** (`F10_3 True True []` in the repro), while the record also lands in `caller.records` with `raw: None` and passes the envelope schema. It fails safe (row 10 RED, never a false GREEN), but the Measured cell would name the wrong falsifier and the wrong reason, and `tests/test_m10_readers.py:294-301` `test_a_credential_in_an_observed_record_is_filed_under_f10_3…` exercises a wrapper *with* its `raw` present, a shape `observe_caller.py` never writes; `:384-391` writes the stripped shape but gives it `step: None`, so `calls()` never sees it. What settles it: in `from_raw`, raise `Unreadable(record.get("error") or "the observer copied no raw record")` when `"raw" in record and record["raw"] is None` before the source check, and a test feeding `record()` the stripped wrapper with `step: "admitted"` asserting `F10_3 held is False` and `records == []`.
>
> **FINDING 2 (Security; prose against code).** `.github/workflows/deploy.yml:637` says of the door token "nothing here writes it anywhere", and `:660` is `echo "token=$token" >> "$GITHUB_OUTPUT"`. The token is masked (`:658`) and lives one hour, and a step output on the runner is how the next step gets it, but the sentence is false as written and the file is Security's under `ruling-cited`. What settles it: either the comment says "written to the step's output on the runner, masked, and nowhere else" or the goldens step mints the token itself; `infra/workflows.sha256:181` moves with either. The Security ruling file for this PR should name it.
>
> Else read for the bug and not found: `caller_relaxations` (`two_key.py:266-281`) compares subjects not bytes, treats absent→`[]` and a removal as no relaxation, reads a non-list as removed, and reaches a first-written manifest because `relaxations()` loads `base.text(path)` through `_load` (`:319-320`); `callers_errors` (`validate/callers.py:36-70`) refuses the missing key, a non-list, extra keys, `platform`, a bad issuer and a duplicate, each naming the field; `caller_misses` flips a GREEN verdict on any miss and re-holds N and `plants_fired == plants_expected` (`gate.py:1189-1194`); `caller.calls` matches a stepped record by `step` before subject (`:200-208`); the authoriser (`door.py:106-148`) checks `alg`, `iss`, full PKCS#1 v1.5 padding, `token_use`, `exp`, then client+username, with `authorizer_result_ttl_in_seconds=0` (`governed_agent.py:421`) so every call's line has its own context; the proxy never forwards the caller's header (`tests/test_m10_platform.py:409`); `run.py:487-494` refuses a door URL for refagent and a door with no token; both inline sources are held under 4096 bytes (`governed_agent.py:369-371`, `tests/test_m10_platform.py:174`).
>
> ## 6. Claims in prose
>
> No "governed", "secure" or "proven" added (grep of the `+` lines, `GovernedAgent` excluded). `docs/developer/quickstart.md:356-357` and `template-README.md:389-393` describe what the door does in the present tense and then say at `:363-366` / `:395-396` that no door is deployed and the reading is at the first deploy; acceptable.
>
> ## Notes
>
> - **NOTE 1 (Product, Security, Tool Owner).** `milestones/README.md:54` says `ruling front matter` "reads the five draft rulings of this PR" and `milestones/M10/README.md:104-108` says they are "written as this PR's five ruling files"; `milestones/M10/rulings/` holds only `pr1.md` and `pr1-engineering.md`. The brief says they are written after this read with `pr: 55`; `make validate` passes today because it reads what exists. The code cites them by name (`SPEC/10:10-11`, `agents/*/manifest.yaml`, `infra/bootstrap/app.py:363`, `infra/workflows.sha256:173-177`), so `ruling-cited` and `cold-review-ruling` will block the merge until all five are on `main`.
> - **NOTE 2 (Product).** `milestones/M10/runs/f10_x_caller_run.yaml:17` still reads `door: as Security rules at SPEC/10 §11 R2   # proposed: the runtime's JWT authoriser on the agent's own pool` after R2 ruled door 2 (hybrid). Correctly left alone as the plant (`SPEC/10:112-114` "the seeds were not touched"); `observe_caller.py` reads only `observed` and `steps[].caller` (`:112-127`), so no reading moves. Product may amend the comment at PR 3 or leave it as the record of what was proposed.
> - **NOTE 3 (Engineering).** `scripts/observe_caller.py:68` imports `src.verdict.caller` for `refuse_credential` and `iso_of_epoch_ms`. The observer decides nothing with them (a refused line is written with its key and error, `:245`), but the raw-record writer now shares code with the module that rules; if `caller.py`'s credential test changes, the observer's copy rule moves with it unseen by the schema. Acceptable at M10; worth a line in `tests/fixtures/README.md` or the script's docstring.
> - **NOTE 4 (Security).** `infra/construct/door.py:81-83` states "A missing header never reaches this code: API Gateway refuses it first and logs the 401", while `SPEC/10 §7` (diff lines 166-173) names exactly this (the 401 line with its request id, and delivery within N) as the risk read only at festival-desk's deploy and PR 3's run. The docstring could say "is expected to", as the SPEC does.
> - **NOTE 5 (Engineering).** The `platform` branch in `caller.calls` (`caller.py:221-224`) is unreachable from `record()`, which filters `stepped` to `STEPS` (`:344`) before calling it; `tests/test_m10_readers.py:243-249` reaches it only by calling `calls()` directly. Harmless; a comment or a removal at PR 3.
> - **NOTE 6.** `tests/test_m10_platform.py:63-82` and `tests/test_m10_seeds.py:334-338` synthesise two CDK stacks (the doored fixture and refagent) per module; the F10_2 case in `Makefile:136` therefore depends on `cdk` being present in the evals runner, as M09's did. Not new.
>
> ## Ruling
>
> DRAFT — proposed: the plant holds and goes RED under this PR's own reading; Engineering's paths are clear to merge once FINDING 1 is carried into PR 3's list and the five ruling files exist with `pr: 55` (NOTE 1). FINDING 2 is Security's to rule in its own file.
>
> BLOCK: 0 · FINDING: 2 · NOTE: 6

## Unsure, for this seat

- The observer imports `refuse_credential`, `redact` and `iso_of_epoch_ms`
  from `src/verdict/caller.py` (cold review N3): it refuses and drops what
  `build` refuses and drops, by the same code, and rules nothing. Named in
  its docstring; a reader who wants the observer wholly apart from the
  verdict chain would copy the three functions, and that is PR 3's call.
- The M02 seed test (`test_s1_one_key_on_a_relaxation_is_refused`) still
  diffs the working tree against a worktree of HEAD and fails locally while
  seat-owned files are uncommitted (M09 PR 2's Unsure); it passes on the
  committed tree.
