---
# M04 PR 4 (#28), Engineering's key: the code, with the cold review.
# Product's file is rulings/pr4.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - src/verdict/gate.py
  - src/ledger.py
  - tests/test_cost_cap_and_ledger.py
evidence:
  - SPEC/00-overview.md#8-M04
  - SPEC/04-model-swap.md#51-when-each-is-measured
  - SPEC/04-model-swap.md#7-expected-on-the-plant-row-4
  - milestones/M04/rulings/pr4.md
  - https://github.com/andaro74/agentkeel/actions/runs/36362949356
  - evals/history/05bd718feb0cc72ab78df13fccf47c3efb8a9314.json
  - evals/history/12ebb54ca3fb3a13e8807f8f5bca37a83b0e4df1.json
  - evals/history/9e4b559bf7ff8241482ed89bb350a2f6249e8c5c.json
pr: 28
---

# M04 PR 4, the close: Engineering's cold review

Drafted by the session; the human rules as Engineering before the merge.

Read cold by `engineering-cold-reviewer`: `git diff 960d6db...5fb17b5`
and ledger row 4 only, with a third read of M04 PR 3's second-round
repairs (`70a979b`, `63712c7`, `12ebb54`; #27 Unsure B). 1 BLOCK,
3 FINDING, 5 NOTE. `docs-writer` read the prose (nine findings, all
repaired in `5fb17b5`).

## What the code does

Row 4's claim is read from the swap PRs, which gate no pull request
(M04 PR 3). Before this PR the Measured cell carried refagent's own
verdict, GREEN, and `src/ledger.py` refused State RED beside it, so the
RED SPEC/04 §7 names could not be written. `READ_THE_SWAPS = {"M04"}` in
`src/verdict/gate.py` keys a reading to row 4, as `READ_IN_THE_RUNTIME`
does row 1: `swap_misses` names each swap that misses its falsifier's
verdict or was not read, and a GREEN run's cell reads RED. `rule()` is
unchanged; no pull request's gate moves; the cell can only turn RED.

## Dispositions

| # | Item | Disposition |
|---|---|---|
| B1 | The machinery that reads the claim lands in the last PR (CLAUDE.md; SPEC/04 §5.1) | **Ruled** (Product, `pr4.md` §2): a second named P3 exception, written into SPEC/04 §5.1 and row 4's Expected cell before the reading run (`05bd718`). Withdrawing it would have left row 4 closable only as "—" RED, the measurement thrown away |
| F1 | F4.1: a RED on the cost cap, or with only a redteam or guardrail golden regressed, read as no miss | **Repaired** (`b8a2e5e`): the breaking swap needs a regressed ordinary or trap golden, no `cost-cap:` reason, and a reason list not cut short; each case a test |
| F2 | F4.2 read from the recorded verdict alone, not the checks recorded beside it | **Repaired** (`b8a2e5e`): the equivalent swap's GREEN needs `evals_on_measured` and every `required_on_head` value `success`, and a head read; each case a test. The first run still decides F4.2 (`pr3.md` §3) |
| F3 | The close files are not in the diff | **Done** after the reading run: the Measured cell (`ed5961d`), `ledger-plain` (`411ba60`), the close detail, `attestations.md`, this file and `pr4.md` |
| N1 | The explainer and video row predicted the reading before it existed | **Recorded**: the reading run wrote exactly what they said ("swap #26 equivalent missed: RED, expected GREEN; RED") |
| N2 | "every other check green" was ambiguous against `d61af92`'s `F1_4: fail` | **Repaired** (`05bd718`) |
| N3 | `--strict-cards` accepts any card in the history folder, not only the envelope's own | **Carried**: `milestones/M05/open.md` row 43, Engineering, M05 |
| N4 | `card_at` raises `KeyError` on a malformed reference instead of REJECTED | **Carried**: row 43 |
| N5 | The own-PR `note` in `d61af92` and `a86262e` is double-decoded (`Â§`) | **Carried**: row 43 |
| Third read | `70a979b`, `63712c7`, `12ebb54` | **Recorded**: no way found for a swap branch to run its own code in the read; the data path (a hand-made envelope under the bot's email) is `M05/open.md` row 18 |

## Checks at the close

- `uv run pytest -q`: 595 passed, 1 skipped (the cosign signature check), at `05bd718`.
- `uv run python -m src.validate`: 16 of 16 ok.
- `make ledger`: exit 0; rows 0 to 3 unchanged; row 4 RED, equal to the
  gate's reading of the envelope for `05bd718` (run 36362949356, bot
  commit `a3bae6b`).
- `src/baseline/` unchanged since tag `m00`.

## The cold review, verbatim (draft ruling file as the reviewer wrote it)

> ## Cold read: M04 PR 4 (m04-pr4 at 5fb17b5; base 960d6db)
>
> HEAD moved while I was reading. Commit `5fb17b5` (Product, docs-writer fixes) landed, so this read covers `960d6db...5fb17b5`: six commits. I read the diff, row 4, `milestones/M04/README.md`, SPEC/04 §5.1 and §7, and the envelopes. I did not read commit bodies or the PR description, and I edited nothing.
>
> **Checks I ran:**
> - `uv run pytest -q`: 589 passed, 1 skipped (the cosign signature check).
> - `uv run python -m src.validate`: 16 of 16 ok.
> - `make ledger`: exit 0. Rows 0–3 are byte-identical to their envelopes. Row 4 is "—", 3/4, OPEN.
> - "As row M04 reads it" on `12ebb54`: `...; swap #26 equivalent missed: RED, expected GREEN; RED; envelope 12ebb54…`.
>
> **PR number:** I could not confirm 28. `gh pr list` shows #27 as the newest PR and there are no issues, so 28 is likely but not certain.
>
> **Direct answers:**
> - **Can rows 0–3 change?** No. `measured_at` passes `read_the_swaps=milestone in {"M04"}` (gate.py:740), and `make ledger` confirms the four cells still match.
> - **Can a later row go RED?** No, unless someone adds to `READ_THE_SWAPS`. The test asserts M05 gives the same output as no milestone.
> - **Does it change `rule()` or any PR's gating?** No. The diff touches only `measured`, `measured_at`, `swap_misses` and two constants. `measured_at` is called only from src/ledger.py:60, 129 and 135.
> - **Does P5 hold?** Yes. The ledger still reads envelopes only through `gate`.
> - **Is `src/baseline/` touched?** No.
> - **Explainer numbers:** each matches the envelopes.
>   - `9e4b559`: agent ordinary 9/9, traps 2/2, `a_vs_a.agent []`; control A-vs-A disagreed on `g-001`; tokens_in 87,344 + tokens_out 10,291 = 97,635 (5fb17b5 now correctly says "whole test job").
>   - `d61af92`: 0/9, 0/2, 11 regressed, A-vs-A zero diff.
>   - `a86262e`: 8/9, 2/2, `g-005` regressed with cites true and score false; the first run `9ff21d5` shows the same. S4 at 3x and 2x and S5 at 17 days match.
> - **Prose claims:** the diff adds none of "governed", "secure" or "proven".
>
> **B1. The PR that closes the milestone adds code that reads the claim.**
> Before this PR, row 4's verdict was not computed anywhere; it is now computed by `swap_misses` and its use in `measured()` (src/verdict/gate.py:641-658 and 609-611). CLAUDE.md says: "Never build the machinery that reads a claim in the last PR." SPEC/04 §5.1 says: "The machinery is not built in the last PR: it lands and runs at PR 3."
>
> The need was known at PR 3. §7's "row 4 closes RED on F4.2 either way" was written at PR 3. src/ledger.py:72 already refused State RED beside a GREEN cell.
>
> The harm this rule guards against is absent here:
> - the code can only turn a GREEN cell RED, never the reverse;
> - rule() and PR gating are untouched;
> - it fired on a real false state in its own test (12ebb54 with #26 RED, tests/test_cost_cap_and_ledger.py:135).
>
> The letter of the rule is still broken. To resolve: Product names this as a P3 exception in SPEC/04 §5.1 and in row 4's Expected cell before the reading run, cited from rulings/pr4.md. That is how M01 and M02 recorded theirs. Withdrawing the code is worse: row 4 could then close only as "—" RED (src/ledger.py:53-55), which throws the measurement away.
>
> **F1. For the breaking swap, `swap_misses` checks less than §7 requires.**
> gate.py:656 accepts any RED that has one reason starting `regressed: `. §7 requires "at least one *citing* golden regressed … and none of these: REJECTED, access errors, the cost cap". Two cases get through:
> - a RED with `cost-cap: N over 150000` (gate.py:538) plus one regression counts as no miss;
> - a regression of a guardrail or redteam golden also passes, because gate.py:496 does not filter by kind.
>
> No test covers either case (the parametrize at test lines 157-165). The outcome today is unaffected: d61af92 has 11 regressions, all ordinary or trap, and no cost-cap reason. Fix: treat any `cost-cap:` reason as a miss, and require a regressed id whose kind is ordinary or trap.
>
> **F2. The equivalent swap is read from the latest recorded verdict alone.**
> §7 says #26's first run (`9ff21d5`) decides F4.2 and "row 4 closes RED on F4.2 either way". `swap_misses` instead reads whatever the reading run recorded: the last commit on the PR that GitHub attributes to the bot (scripts/observe_pr.py:439-443). It ignores `required_on_head` and `evals_on_measured`, which are recorded beside that verdict.
>
> Three routes lead to a recorded GREEN:
> - a verdict that differs between jobs;
> - an envelope pushed by hand under the bot's email (M05 open.md row 18);
> - a swap branch that edits `build` (row 12).
>
> Any of them makes the cell GREEN, and ledger.py:72 would then demand State GREEN, which contradicts §7. The outcome today is unaffected (a86262e is RED), and the reading run's envelope fixes the result once written. Fix before the reading run: count the equivalent swap as a miss when `evals_on_measured != "success"` or any `required_on_head` value is not `"success"`, or pin F4.2 to 9ff21d5.
>
> **F3. The close is not complete in this diff.**
> - milestones/README.md:44 still reads "—", 3 / 4, OPEN, and milestones/M04/README.md matches it.
> - There is no milestones/M04/attestations.md.
> - There is no rulings/pr4.md, although milestones/M05/open.md row 39 cites it.
>
> This ruling covers 5fb17b5 only. The Measured cell must be re-checked by `make ledger` after the reading run.
>
> **N1. The explainer and video row predict the reading run before it exists.** docs/milestones/M04.md:63 says "Red", and the M04 row in docs/video/README.md names the cell text. "Red" is supported by 9ff21d5 under §7. The cell text is a prediction until PR 4's envelope exists.
>
> **N2. "The re-runs … have every other check green" (5fb17b5) is ambiguous.** It is true of the required PR checks. It is false of the envelope's `checks`: d61af92 has `F1_4: fail`. That failure is the model's (wrong fields), so the conclusion stands; the wording does not.
>
> **N3. The `--strict-cards` path check accepts any card in the history folder.** gate.py:355 accepts any 40-hex sha, not only the envelope's own. A swap envelope can name another run's card that is in HEAD's tree, and spend() then holds its tokens to the wrong card. The card is data, not code.
>
> **N4. `card_at` crashes instead of rejecting on a malformed reference.** It reads `ref["path"]` and `ref["sha256"]` without checking them. A dict without those keys raises KeyError instead of REJECTED. rule_swaps turns the crash into an unread swap, which reads RED, so the failure is safe.
>
> **N5. The swap notes in both re-run envelopes are garbled.** d61af92 and a86262e store `SPEC/04 Â§4` (displays as "Â§") in the own-PR `note`. The source bytes are correct (C2 A7 in scripts/rule_swaps.py). The note is not read by any verdict.
>
> **Third read of 70a979b, 63712c7, 12ebb54.** I found no way for a swap branch to run its own code in the read: the gate runs from a fresh worktree of HEAD with PYTHONPATH set to that tree; only two fixed paths are taken, at the bot's commit; no credentials are passed; the whole read has a 240 s budget; every exception makes the swap unread, which swap_misses reads as RED. The data path stays open. The gate trusts an envelope's `pass` fields, and the bot attribution can be claimed (observe_pr.py:432-441). That is F2's route to a changed recorded verdict, and N3 and N4 above.
>
> BLOCK: 1 · FINDING: 3 · NOTE: 5
