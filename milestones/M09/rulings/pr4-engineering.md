---
# M09 PR 4 (#53), the close. Engineering's key over the one Engineering
# path this PR touches: the run test's marker in tests/test_m09_seeds.py,
# first and alone, so the branch's CI envelope reads agent_rules made. The
# cold review of the close is pasted below. Product's file is pr4.md, the
# Data Owner's pr4-data-owner.md, Security's pr4-security.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m09_seeds.py
evidence:
  - SPEC/09-per-agent-rules.md#5-the-seeded-cases
  - evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json
  - https://github.com/andaro74/agentkeel/actions/runs/38400685274
  - milestones/M09/rulings/pr2-engineering.md
  - milestones/M09/rulings/pr3-engineering.md
pr: 53
---

# Ruling: M09 PR 4, Engineering

Ruled by andaro74 as Engineering, 2026-10-13, as written.

## The marker

`test_the_plant_run_was_made` in `tests/test_m09_seeds.py` loses its
`xfail(strict=True)` marker (`c503324`): the run is made, `observed` is a
mapping (`bfa4c19`), and the test passes by its reader, the run file. The
file now shows 9 passed; `--runxfail` has nothing left to show. The
`expected_failure` marker object stays defined, unused, as the other
milestones' seed files leave theirs. No other line changes. The
pre-existing unused import `SeedBroken` (ruff F401; no workflow runs ruff)
stays: no code beyond the marker in a close (finding 17).

## The envelope's provenance

The marker was committed and pushed alone, and the PR opened, before any
document was written, so the CI bot's envelope is of a tree whose only
difference from `main` is the owner's `observed` block and the marker.
`evals.yml` (run 38400685274) ran `scripts/observe_rules.py` twice, as
`agentkeel-audit-read` for the bucket and as the eval role for GitHub, the
registry and `GetGuardrail` (`made True` both times), and `build` composed
`agent_rules` from the file; the gate ruled GREEN; `record` committed
`evals/history/c503324….json` as `github-actions[bot]` (`1ebd907`). The
`checks` job's pytest passed. Nothing under `src/`, `scripts/`,
`evals/history/` (but for the bot's commit) or `infra/` is in this PR.

## Read on the envelope, by the readers PR 2 built

- `F9_1`: `source: read_back`, so R4's grant was deployed and the eval
  role read the guardrail; `digest_read == digest_expected`
  (`1245e65b…a122`). The registry fallback (SPEC/09 §9 cut 3) was not
  needed.
- `F9_2`: `refused_on` is the rules check alone; `baseline_in_guardrail:
  true` from the read-back's PII entities.
- `F9_3`: `fired_by: {g-030: [unannounced-selection-leak]}`, one topic, the
  named one; membership, not "only", and here they coincide.
- `F9_4`: `heads: {first: admitted, second: refused, third: admitted}`,
  each the platform App's run (5144253) by `_check`'s app-id hold (cold
  review F2 on PR 2).
- `gate.rules_misses` returns `[]`; `rules_reading` prints the cell's
  tail.

## Cold review

Run before the documents were asked for ruling, on the diff
`79ba804...b011c25` (the close's documents commit; the two commits after
it, `54f84e6` and this one, are the repairs it and the `docs-writer` asked
for, each touching the documents alone). **0 BLOCK, 2 FINDING, 5 NOTE.**
The `docs-writer` read (the explainer against the envelope, and
`docs-current` by hand: pass) is in the PR body with its five
corrections, all taken in `54f84e6`. Dispositions, then the report
verbatim.

| # | Finding | Status |
|---|---|---|
| F1 | The close plans a video pull request after the tag while two lines say "a fifth pull request makes this close wrong"; the uncounted precedents (`#1`, `#29`) did not edit a closed milestone's files | Product's, `pr4.md` ruling 3 and Unsure 1: the two lines now read "counted against the cap", and ruling 3 records that the after-the-tag form is a rule Product writes, not a precedent it follows, with M08's form as the alternative. Product chooses before ruling. |
| F2 | "The numbers below are the envelope's" covered the cost paragraph's numbers, which are the record's; "one every ten minutes" does not reconcile with 50 runs in 791 minutes | Repaired: the explainer says which paragraphs are the envelope's and which the record's; the rate reads "on a ten-minute schedule" (`54f84e6`), and the close detail and `pr4-security.md` say 50 runs in 79 slots. Product, Security. |
| N1 | "The two ordinary questions" named the trap as ordinary | Repaired in `54f84e6` (the `docs-writer` read it too). Product. |
| N2 | A stale comment in `tests/test_m09_seeds.py` ("made at PR 3; observed: null today") | Repaired: one comment line, no code. Engineering, this file's path. |
| N3 | This section was empty | This table and the report. |
| N4 | The bot's three envelope files are in no ruling's `authorises` | Recorded: `gates` (`ruling-cited`) passed on the pushed head `b011c25` (run 38405490865), so the gate reads the bot's commit as covered, as at every close before. Nothing to act. |
| N5 | `54f84e6` landed after the briefed head | Read by this seat as part of the PR: nine lines of the explainer, the five `docs-writer` corrections, no other file. Not re-reviewed. |

### `engineering-cold-reviewer`

> Read: the diff 79ba804...b011c25 (17 files)
>
> (The stat reads 16 files, 2246+/15-: the brief's 17 counts the diff file itself or the run file twice; every path below is from `git diff 79ba804...b011c25 --name-status`.)
>
> Proposed file: C:\Users\andar\code\agentkeel\milestones\M09\rulings\pr4-cold-review.md (or paste the body into the empty "Cold review" section of C:\Users\andar\code\agentkeel\milestones\M09\rulings\pr4-engineering.md, lines 64-71, which says a draft with that section empty is not ruled).
>
> ---
> ```
> ---
> # M09 PR 4 (#53), the close. The cold review of the diff 79ba804...b011c25,
> # read without the PR body, the feasibility note's argument or any commit
> # message body. Read-only: make ledger, make validate, pytest, git.
> ruling: DRAFT
> seat: Engineering
> authorises:
>   - tests/test_m09_seeds.py
> evidence:
>   - evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json
>   - https://github.com/andaro74/agentkeel/actions/runs/38400685274
>   - milestones/README.md
>   - milestones/M09/README.md
>   - milestones/M09/rulings/pr4.md
>   - milestones/M09/rulings/pr4-engineering.md
>   - milestones/M09/rulings/pr4-security.md
>   - milestones/M09/rulings/pr4-data-owner.md
> pr: 53
> ---
>
> # Cold review: M09 PR 4 (#53), the close
>
> Diff `79ba804...b011c25`, four commits: `bfa4c19` (andaro74, the run
> file alone, 5+/1-), `c503324` (andaro74, `tests/test_m09_seeds.py`, one
> deletion), `1ebd907` (`github-actions[bot]`, the three `evals/history/`
> files), `b011c25` (andaro74, the documents and the four rulings).
>
> ## What held (each checked, not read)
>
> - **Shape.** Nothing under `src/`, `scripts/`, `infra/`, `.github/`,
>   `rules/`, `evals/goldens/`, `thresholds.yaml`, `data/`, `agents/`,
>   `src/baseline/` is in the diff (`--name-status`). The one code change
>   is `tests/test_m09_seeds.py:224`, the `@expected_failure` line removed.
>   The last PR builds nothing that reads the plant.
> - **The plant and its reading.** `milestones/M09/runs/f9_3_plant_run.yaml:49-53`
>   carries four keys and no result; `agent_rules.commit` in the envelope
>   is `cd0ad60490ad66a55e201eacda9e09b732a99a7c`, the commit the
>   `answer_key` names. The row read RED at PR 2 (ledger row 9, "Expected
>   gate output"), and GREEN here on the envelope.
> - **P5.** The only commit touching `evals/history/` in the range is
>   `1ebd907` by `github-actions[bot]` (`git log --format='%h %an'
>   79ba804..HEAD -- evals/history`). The run file's `observed` block is a
>   raw record (ids and a key), the named P3 exception (SPEC/09 §5.1).
> - **Frozen and owned paths.** `src/baseline/` untouched. Every path in
>   the diff has a CODEOWNERS line at the base ref (`/milestones/`,
>   `/docs/`, `/tests/`, `/evals/history/`, lines 27, 30, 80, 92) and is
>   named in a `pr: 53` ruling's `authorises` (`pr4.md:16-27`,
>   `pr4-engineering.md:10`), except the bot's three files (NOTE 4).
> - **The Measured cell.** `make ledger` exits 0; its "as row M09 reads it"
>   line for `c503324…` equals the cell in `milestones/README.md:91` and
>   `milestones/M09/README.md:95` byte for byte (the ledger holds it).
> - **The envelope against the close detail's table**
>   (`milestones/M09/README.md:127-133`): `agent_rules.pin at8e36cosq1r:1`;
>   `F9_1.source read_back`, `digest_read == digest_expected ==
>   1245e65b…a122`; `F9_2.baseline_in_guardrail true`, `refused_on` the
>   rules check alone; `F9_3.fired_by {g-030: [unannounced-selection-leak]}`,
>   `fired 1 expected 1`; `F9_4.heads {first: admitted, second: refused,
>   third: admitted}`; `guardrail_version 1088aw3ujhyd:6`; `plants_fired 7
>   of 7`; `checks.F9_1..F9_5 pass` at run 38400685274; `verdict GREEN`;
>   `never_passed ['g-014']` (the cell's `never_passed 1`). All as written.
> - **The test can fail.** `tests/test_m09_seeds.py:225-228` asserts
>   `run["observed"] is not None`; `observed: null` (the state before
>   `bfa4c19`) fails it. `uv run pytest tests/test_m09_seeds.py -q`: 9
>   passed. `uv run pytest -q`: 1233 passed, 1 skipped, 2 xfailed, as
>   `pr4.md:148` states. `make validate`: 21 `ok`, exit 0, as the `m09`
>   header row (`milestones/README.md:82`) states.
> - **Prose words.** `grep -iE 'governed|secure|proven'` over the added
>   lines (envelopes excluded) hits `GovernedAgent` (the construct's name,
>   `milestones/M09/README.md:220`, `pr4-security.md:52`) and the
>   attestation that quotes the rule (`attestations.md:83`). No claim.
> - **Drafts.** All four `pr4*.md` carry `DRAFT until it reads "Ruled by"`
>   (`pr4.md:41`, `pr4-engineering.md:22`, `pr4-security.md:25`,
>   `pr4-data-owner.md:24`); no body line starts `Drafted `.
> - **The record's arithmetic.** 13:28Z merge to 13:58Z first deploy = 30
>   min; 03:16:43Z `#52` merge to 03:35Z deploy = 18-19 min
>   (`milestones/M09/README.md:157-163`; explainer lines 48-49). Holds.
>
> ## FINDING 1 — the close plans a fifth pull request on this milestone's paths while saying a fifth makes it wrong
>
> `docs/video/README.md:55` (row M09): "committed in M09's video pull
> request, uncounted as `#29` was". `milestones/M09/rulings/pr4.md:66-81`
> (ruling 3) and `:113-116` (Unsure 1): the video pull request carries the
> LFS object, the README row, "the explainer's Watch line, the re-signed
> attestation 6, and the second amendment to ADR-0005". `attestations.md:91-96`
> is written for that form. Against it, the same diff writes
> `milestones/M09/README.md:282-284`: "or a fifth pull request, makes this
> close wrong", and `pr4.md:156` the same; and the explainer text this PR
> removes (`docs/milestones/M09.md`, old lines 76-77) read "M09's video is
> committed at M09's close, as M08's was (ADR-0005 amendment 2; SPEC/00
> §10.5 as amended at M09 PR 1)", citing the same amendment for the
> opposite form. The ledger's uncounted precedents (`milestones/README.md:8-12`)
> are the adoption PR (#1) and M04's sign-off (#29), neither a PR that
> edits a closed milestone's attestations and explainer after its tag.
> CLAUDE.md: "never in five. A fifth PR is a RED close with the finding as
> the result." Product settles Unsure 1 before `pr4.md` reads "Ruled by":
> either M08's form (record on this branch, commit before the merge, README
> row and attestation 6 rewritten to the hash) or a written rule that the
> video PR is outside the count, with the two "fifth pull request" lines
> reworded so the close does not contradict itself. Not a BLOCK: the diff
> as it stands has four PRs and the decision is Product's, named in the file.
>
> ## FINDING 2 — "The numbers below are the envelope's" covers numbers that are the record's, and one of them does not reconcile with the count
>
> `docs/milestones/M09.md:9-12`: "The numbers below are the envelope's
> (`c503324…`)". The cost paragraph (`:43-56`) carries fifty failed
> deploys, thirty and nineteen minutes, two repairs, two fixtures, one
> repository, one account change: none is in the envelope (`agent_rules`
> holds `fired`, `expected`, the pin, the digest, the heads); they are the
> close detail's (`milestones/M09/README.md:157-173, 183-193`), read from
> GitHub and AWS by hand. `pr4.md:60-62` ("No number in the explainer
> differs from the envelope's") rests on the same sentence. And `:47`
> "Fifty failed deploy attempts ... one every ten minutes": the window the
> close detail gives (13:58Z to 03:09Z, `milestones/M09/README.md:160-161`)
> is 791 minutes, 79 ten-minute slots, so fifty runs is one every ~16
> minutes, not ten; `pr4-security.md:93-94` ("finds the same admitted head
> every ten minutes") says the same. The schedule is `*/10`; the count says
> the scheduler skipped about a third. Reword the source sentence (the
> envelope's for the reading, the record's for the cost) and the rate
> (a ten-minute schedule, fifty runs in thirteen hours). Product, one
> paragraph; the count itself (50) is not checked here (`gh run list`,
> `pr4-security.md:121`, is the reader's).
>
> ## NOTE 1 — "The two ordinary questions" names a trap as ordinary
>
> `docs/milestones/M09.md:21-23`: `g-010` is a trap (the cell: `traps 2/2
> (g-010, g-011)`; the close detail `:136-137` records its holdback
> answer). One ordinary question and one trap were answered. Product.
>
> ## NOTE 2 — a stale comment in the one code file
>
> `tests/test_m09_seeds.py:221`: `# --- the run file (made at PR 3;
> observed: null today)`. The run was made at PR 4 and `observed` is
> filled. One comment line, Engineering; the marker commit left it.
>
> ## NOTE 3 — `pr4-engineering.md`'s "Cold review" section is empty
>
> `milestones/M09/rulings/pr4-engineering.md:64-71` says the report is
> pasted after the review runs and "a draft ruling with this section empty
> is not ruled". This report, with its dispositions, goes there before
> "Ruled by".
>
> ## NOTE 4 — the three envelope files are in no ruling's `authorises`
>
> `evals/history/c503324….json`, `.baseline-card.json`, `.baseline-raw.json`
> are in the diff and in neither `pr4.md:16-27` nor `pr4-engineering.md:10`.
> They are the bot's commit (`1ebd907`), Engineering's path, no human
> commit so no two-key. Whether `ruling-cited` exempts a bot commit is not
> in this diff; earlier closes shipped the same shape. Recorded, nothing
> to act unless the gate says otherwise on the PR.
>
> ## NOTE 5 — the branch moved past the briefed head during the review
>
> `54f84e6` (andaro74, 2026-10-13T06:35:45-07:00, "the explainer's five
> sentences the docs-writer read as wrong or stale") landed on `m09-pr4`
> after `b011c25`, the head this review was given. It changes
> `docs/milestones/M09.md` only (9+/10-): it rewords NOTE 1's sentence
> ("The ordinary question and the trap were answered"), FINDING 2's rate
> ("on a ten-minute schedule"), the F9.2 sentence (the refusal's naming
> moved to "the pull request's own record"), and two "at the close"
> forward references. It leaves FINDING 2's source sentence (`:9-12`) and
> FINDING 1 as they were. This report is of `79ba804...b011c25`; the
> Engineering seat reads `54f84e6` as part of the PR or re-runs the review
> on the merged head.
>
> ## What a reader can run
>
> ```
> make ledger; echo $?                                   # row 9 GREEN, 4 / 4; 0
> make validate | grep -c '^ok '                         # 21
> uv run pytest tests/test_m09_seeds.py -q               # 9 passed
> git log --format='%h %an' 79ba804..b011c25 -- evals/history    # 1ebd907 github-actions[bot]
> git diff 79ba804...b011c25 --stat -- src scripts infra .github rules evals/goldens thresholds.yaml data agents   # empty
> git diff 79ba804...b011c25 -- . ':!evals/history' | grep '^+' | grep -iE 'governed|secure|proven'   # GovernedAgent, and the attestation quoting the rule
> grep -n '^Drafted ' milestones/M09/rulings/pr4*.md    # nothing
> python -c "from datetime import datetime as d; print((d(2026,10,13,3,9)-d(2026,10,12,13,58)).total_seconds()/600)"   # 79.1 ten-minute slots for 50 runs
> git diff b011c25 54f84e6 --stat                        # docs/milestones/M09.md alone
> ```
>
> BLOCK: 0 · FINDING: 2 · NOTE: 5
> ```
> ---
>
> Summary for the caller: nothing blocks. The Measured cell is the envelope's line (`make ledger` exit 0), the close changes no reader, the envelope is the bot's, the test can fail and passes by the run file, all four rulings are drafts with no "Drafted " body line, and no "governed/secure/proven" claim is written. Two findings for Product to settle before ruling: the planned video pull request versus the diff's own "a fifth pull request makes this close wrong" (`docs/video/README.md:55`, `pr4.md:66-81,156`, `milestones/M09/README.md:282-284`), and the explainer's "numbers are the envelope's" sentence covering record numbers, with "one every ten minutes" not matching fifty runs in 791 minutes (`docs/milestones/M09.md:9-12,47`). Note that `54f84e6` landed on the branch after the briefed head and already rewords two of the sentences; it was not in the reviewed range.
>
> BLOCK: 0 · FINDING: 2 · NOTE: 5

## What a reader can run

```
git show c503324 --stat                                  # tests/test_m09_seeds.py, one deletion
git diff c503324^ c503324                                # the marker line and nothing else
uv run pytest tests/test_m09_seeds.py -q                 # 9 passed
git log --format='%h %an' 1ebd907 -1                     # github-actions[bot]
uv run python -m src.verdict.gate evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json   # exit 0
git diff 79ba804...HEAD --stat -- src scripts infra .github rules evals/goldens thresholds.yaml   # empty
```

A reader changed in this PR, an envelope committed by a person, a marker
left on, or a test that passes for a reason other than the run file's
`observed` block, makes this ruling wrong.
