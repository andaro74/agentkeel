---
# M07 PR 2 (to open as #39), Engineering's key and the cold review, one
# file. Drafted from engineering-cold-reviewer's read of the diff
# a2c5a61...1b376a3 and row 7 only. The repairs after it (b3196d6,
# ccb2be8 and the documents' commit) were not read cold again.
# Product's file is rulings/pr2.md; Security's is rulings/pr2-security.md;
# the Threshold Owner's is rulings/pr2-threshold-owner.md.
ruling: pr2-engineering
seat: Engineering
authorises:
  - src/**
  - scripts/**
  - tests/**
  - Makefile
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/README.md
  - milestones/M07/README.md
  - milestones/M07/runs/pr2_expected.md
  - milestones/M07/runs/f7_0_dispatch_from_branch.json
pr: 39
---

# Ruling: M07 PR 2, Engineering, with the cold review

DRAFT for andaro74 as Engineering. Not ruled until this line reads "Ruled by".

## What this authorises

- **`src/verdict/`**: `upgrade.py`, build's readings of claim 7 (F7.0 to
  F7.5 and `taken`); the envelope's optional `upgrade` in `schema.json`;
  `build`'s `--upgrade`, `--surfaces` and `--app-observation`; the gate's
  `CLAIM_7_CHECKS` from `eed43f5`, and row 7's reading
  (`upgrade_misses`); `replay_history.verdicts` and `rows`;
  `plants.SURFACE_PLANTS`; `template.py`'s two inherited repairs.
- **`src/validate/`**: panel 2's check; **`src/manifest/schema.json`**:
  `rollout: retired` and `platform_version`'s pattern; **`src/ledger.py`**.
- **`scripts/`**: `platform_check.py` (the token for one repository and
  one named set, the reader of the grant, the seeded relaxation),
  `platform_upgrade.py`, `platform_pr.py`, `retire_agent.py`,
  `model_watch.py`, `observe_upgrade.py`, `envelope_rows.py`,
  `registry.py`'s `retiring` and `retire`, and the smaller changes to
  `make_template.py`, `observe_template.py`, `runtime_for_tree.py`.
- **`tests/`**: the S0 fixtures reshaped for three Apps; six new test
  files for M07; the seed tests' nine fixture markers off, four run-file
  markers kept.
- **`Makefile`**: `F7_*_CASES`, `UPGRADE_OBS`, `APP_OBS`, `make upgrade`.

Nothing under `src/baseline/`, `evals/history/`, `evals/goldens/`,
`rules/` or `data/`.

## The cold review

`engineering-cold-reviewer` read `git diff a2c5a61...1b376a3` (98 files)
and row 7, ran eight test files (310 passed, 4 expected failures) and
`make validate`, and probed `src/verdict/upgrade.py` in memory. BLOCK 2,
FINDING 15, NOTE 8. Its report is in the pull request's body, verbatim.

### BLOCK

| # | Block | Status |
|---|---|---|
| B1 | P5: `evals.yml`'s `archive` job opened each envelope with `jq` to write panel 2's table: a second reader of envelopes | **Repaired** (`b3196d6`). `replay_history.rows` reads them; `scripts/envelope_rows.py` writes the table from it; `evals.yml`'s new `envelope-rows` job runs it on `main`, apart from the job that holds the envelope put role. A test holds that the archive job names no table and the new job no `jq` |
| B2 | Seat-owned paths built on two ruling files that read DRAFT, and on item 13, which says it is not ruled | **Neither repaired nor ruled as the pull request opens. The seats'.** The human ruled items 1 to 12 and the Threshold Owner's four on 2026-10-02 and asked that each file's DRAFT line stay until the end of the PR, as in PR 1. `cold-review-ruling` holds the merge until then. Item 13 (13a to 13n) is put to Security in `pr2-security.md`: each is in the diff so that the `cdk diff` shows it, and none is deployed, granted or set. The reviewer's consequence is right and is the intent: while the Security file reads DRAFT, `load_grant` refuses and every keyed job on `main` stops at its first step |

### FINDING

| # | Finding | Status |
|---|---|---|
| F1 | The model upgrade cannot read as held: CI's own envelope commit on the swap pull request is "a person's edit" and a path "a model upgrade does not" change, so `taken` is at most 2 | **Stated, not repaired. Product's.** SPEC/07 §2 defines a person's edit as any commit on an upgrade pull request that is not the App's and touches anything but a ruling file; the reader keeps to it. Changing the reader changes what F7.1 says, which is not this seat's. A test holds the reading (`test_cis_own_envelope_commit_reads_as_a_persons_edit_as_the_spec_defines_one`); SPEC/07 §12 and `runs/pr2_expected.md` say it. To be ruled before the swap is opened |
| F2 | A relaxation read "refused" on any status of 400 or more | **Repaired** (`ccb2be8`): only 403. Anything else of 400 or more is unread |
| F3 | Five readings came out held with a record missing | **Repaired**, each with a test: an invocation with no time and answer records not listed are unread; a `post` job whose steps were not read is unread; a pull request that has not merged is unread unless a miss is already there; the owner's test refuses a deploy run that completed before the merge |
| F4 | A stale App observation overrode a fresher one, field by field | **Repaired**: where the run read a commit or a merge the stored record lacks, the run's own reading is ruled on and says `anonymous`. Nothing else compares their times; said in SPEC/07 §12 |
| F5 | "No person's edit" rests on a commit's author login | **Open. Engineering, PR 3.** The observer now writes each commit's committer and GitHub's verification beside its author. The rule on them waits for a commit made by `agentkeel-upgrades` to read: what GitHub records as the committer and the signer of an App's commit is not known from this tree. Before S1 |
| F6 | The observer compares records, which the module says is build's | **Part kept, part open.** The delete record is still matched by the observer (the runtime's id, no error, at or after the merge); build's "earlier than the merge" is a guard on a record from another source, and says so. `read_relaxation` still compares times for `passed_after_restore` and `merges_between`, and "after the restore" is any App success after the ask: **PR 3**, before the relaxation, which is the last attempt but one. Build does not read the bucket's `passed` |
| F7 | "Went live" is read from an image that exists | **Reworded**: the reason says no image of the agent carries the merged tree's digest, and the schema's description of `taken` says what live is read from. The observation's key stays `runtime` |
| F8 | Where the gate could not disagree with build | **Repaired**: the gate counts each taken kind again from F7_1's upgrades of it and from F7_2, holds F7_0 again to its four parts, holds each deploy's seconds to the bar, and refuses a count of no plants in the verdict and in row 7's reading |
| F9 | S0's installation test was reshaped; two reasons are no longer asked on the checking App | **Stands, and is said.** It follows from Security's item 3 ("all repositories"): for `agentkeel-platform` the grant bounds no repository of the organisation, so no fixture can make one a miss. `tests/fixtures/README.md` now says the reasons are kept by reason, not by App |
| F10 | S4's query seed test did not ask for the planted reason | **Repaired**: it asserts a computed verdict is what was refused |
| F11 | The grant reader minted a token with no repository on every installation | **Repaired** (`b3196d6`), as security-reviewer BLOCK 1. It still mints one metadata-only token with no repository on an installation the grant names, to list what it reaches, revoked after. Row 7's "no longer mints a token with no repository" is about `app_token()`; this one is said in `read_grant` and in `pr2-security.md` item 6 |
| F12 | The dispatch's refusal was inferred, and the run's workflow was not checked | **Repaired**: held only on GitHub's annotation on the `post` job, on a run of `platform-check.yml`. Run 36963543726 carries it |
| F13 | No envelope at this head | The pull request's own run. Cited here once CI has written it |
| F14 | SPEC/04 §2's second-run rule has no ADR | **Open. Product with the Threshold Owner.** The rule is the Threshold Owner's item 2, and no gate reads it. Recommended: an ADR in PR 3. This PR's own run does not qualify for a second run, so the rule is not used before then |
| F15 | A runner writes a file under `envelopes/` | **Open. Security's** (`pr2-security.md` item 13m). It is the retire job's record: no verdict, and the gate never reads it |

### NOTE

- **N2, kept because it bears on the order of the human's steps:** the
  schedules arm at merge. `model-watch.yml` runs daily and the candidate
  is already named, so the swap pull request opens with no further step
  once the role variable, the App's id and the "Ruled by" line all
  exist. The swap's statement must be pushed before the last of the
  three is made.
- **N5:** the prose is corrected in `upgrade.py`, `build.py`, the schema
  and `CLAUDE.md`.
- **N6:** a run's `updated_at` is read as its completion, and
  `required_on_head` reads the first 100 check runs. Kept; said here.
- **N7:** the content of `server.py` in a plan: `pr2-security.md` 13l.
- N1, N3, N4 and N8 need nothing.

## The other seats' reports that named this seat's paths

Each is in the pull request's body. What was done is in
`pr2-security.md` section 14 and `pr2-threshold-owner.md` section 5.
In `scripts/` and `src/`: the retire job's record (platform-architect
B1), the reader of the grant (security-reviewer 1, 2, 3, 6), the keyed
jobs' own text (4), the registry's one-way retirement (8),
`model_watch`'s date guard (threshold-owner F4), the gate holding the
deploy bar again (F6).

## What a reader can run

```
uv run pytest -q tests/test_m07_seeds.py                      # 9 passed, 4 xfailed
uv run pytest -q tests/test_m07_upgrade.py -k "refusal or unread or behind or persons_edit or wrong_run or never_started"
uv run pytest -q tests/test_m07_envelope.py tests/test_p5_disagree.py
uv run pytest -q tests/test_m07_workflows.py -k shared_reader
grep -n "jq" .github/workflows/evals.yml                      # the two panels' query bodies; no envelope is opened with it
gh api repos/andaro74/agentkeel/check-runs/110702392789/annotations --jq '.[].message'
make validate && make ledger
```
