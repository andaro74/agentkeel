---
# M07 PR 4 (#44), the close. Product's key. PR 4 by name, the fifth pull
# request by count: a RED close by the cap's rule (rulings/grant-ids.md).
# Security's file is pr4-security.md (three repairs deployed before any
# ruling, and item 13n); Engineering's is pr4-engineering.md (the cold
# review and the tests).
ruling: pr4
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/07-upgrade-retire-surfaces.md
  - CLAUDE.md
  - milestones/README.md
  - milestones/M06/runs/f6_3_quickstart.yaml
  - milestones/M07/README.md
  - milestones/M07/attestations.md
  - milestones/M07/runs/b2_cdk_diff.md
  - milestones/M07/runs/f7_0_owner_test.yaml
  - milestones/M07/runs/f7_1_platform_upgrade.yaml
  - milestones/M07/runs/f7_2_removed_and_kept.md
  - milestones/M07/runs/f7_2_retire.yaml
  - milestones/M07/runs/f7_3_rollback.yaml
  - milestones/M07/runs/pr2_by_hand.md
  - milestones/M07/runs/pr4_expected.md
  - milestones/M07/rulings/pr4.md
  - milestones/M07/rulings/pr4-security.md
  - milestones/M07/rulings/pr4-engineering.md
  - milestones/M08/open.md
  - docs/milestones/M07.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/developer/quickstart.md
  - docs/developer/template-README.md
  - docs/developer/upgrade.md
  - docs/platform/overview.md
  - docs/platform/surfaces.md
  - docs/compliance/map.md
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - https://github.com/andaro74/agentkeel/actions/runs/37149475766
  - evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json
  - https://github.com/andaro74/agentkeel/actions/runs/37147871497
  - evals/history/84dc913b996815b9bf8f7a6ebff45b272a211bdd.json
  - milestones/M07/feasibility.md
  - milestones/M07/rulings/pr1.md
  - milestones/M07/rulings/pr2.md
  - milestones/M07/rulings/pr3.md
  - milestones/M07/rulings/grant-ids.md
  - milestones/M07/runs/pr4_expected.md
  - milestones/M06/runs/f6_3_quickstart.yaml
  - milestones/M07/runs/f7_0_owner_test.yaml
  - milestones/M07/runs/f7_1_platform_upgrade.yaml
  - milestones/M07/runs/f7_2_retire.yaml
  - milestones/M07/runs/f7_3_rollback.yaml
pr: 44
---

# Ruling: M07 PR 4, Product

Ruled by andaro74 as Product, 2026-10-03, as written.

Dates and times are UTC.

## 1. What this PR is

The close of M07. PR 4 by name and **the fifth pull request by count**
(#38, #39, #40, #42, then this): a RED close by the cap's rule, as
`rulings/grant-ids.md` ruled, with no cap raise. Row 7 was already
expected RED on F7.0 (`rulings/pr3.md`).

It carries: the `observed` entry of every attempt but the owner's test
(the timed run, the platform upgrade, the relaxation, the swap, the
rollback, the retirement), each stated in `runs/pr4_expected.md` and
pushed before it was made; the five run-file markers off; **three
repairs deployed by hand during the attempts** (two IAM actions on
`runtime/*`, the observer's trust subject: `pr4-security.md`) and item
13n; row 7's Measured cell from `make ledger`'s reading of this pull
request's envelope, its State, `5 / 4`; the close detail; the
explainer's "What happened"; the read-back's entry in the video README;
`attestations.md`; SPEC/07 §12's records; `milestones/M08/open.md`; this
file, Security's and Engineering's.

It builds no reader. Nothing under `src/`, `agents/`, `thresholds.yaml`,
`evals/goldens/`, `data/` or the `Makefile` changes.

## 2. The reading

The cell is `make ledger`'s line for the envelope for
`dee74c3cf4102bfb6d4315faafb161c154618ed9` (CI run 37149475766, bot commit `45bac6a`), copied.
`make ledger` exits 0.

refagent GREEN in `mode: runtime`, ordinary 9/9, traps 2/2, guardrail
2/3, red team 5/5, plants 7/7, `regressed` 0, p95 5,740 ms. `upgrade`:
`taken` **2 of 3** (platform and retirement; model unread). `F7_0` read
and **not held**: "owner_test: deployed 32264 s after the merge, over
upgrade.deploy_max_seconds 3600"; its other three parts held, the
relaxation as `detected`. `F7_1` **unread**: "model andaro74/agentkeel#43:
unread: the pull request has not merged". `F7_2` held, 368 s. `F7_3`
held, on `window-check`. `F7_4` held, 55 rows. `F7_5` held. `template`:
`F6_1` read and **not held**; `F6_3` held, 3,615 s; `F6_2` not held,
"behind"; `F6_4` held. Row 7: **RED**.

**Against what was stated.** The statements that count are
`runs/pr4_expected.md`'s, each pushed before its attempt. Of what they
expected of this run: one was wrong (`template.F6_1` expected held; it
reads not held) and one number was off by four seconds (32,260 for
32,264). The rest read as expected. An expected reading of this run as a
whole was also written in #44's body when it opened: after every
attempt, before the run, and not in the tree (cold review 2, N17). It
read as written there, with `F7_4`, given as "held or unread", held; and
with the platform pull requests' times as 139 s and 144 s to arrive and
518 s and 511 s to deploy, not the session's hand counts.

**The close ran twice.** The first run (37147871497, `84dc913`, envelope
kept) read the same and its `evals` and `checks` jobs failed on one test
the session had not updated (`pr4-engineering.md`). The cell is the
second run's. If a later run on this branch reads differently, that is
recorded beside it and the cell stays on `dee74c3`.

**"Unread" for the model, and "not taken".** The envelope says the
model's pull request is unread because it did not merge
(`rulings/pr2-engineering.md` ruled that reading). Its own envelope, on
its own branch, is RED on `g-004`. The row is RED on `taken` under 3
either way; the close's prose says "not taken" for the upgrade and
"unread" for the envelope's field, and does not use one for the other.

## 3. What Product ruled during the attempts, each in the conversation and recorded here

| When | Ruling | Where it is recorded |
|---|---|---|
| 2026-10-03, before the timed run | The owner's test's miss on time does not stop the timed run; the path held end to end | SPEC/07 §12, "the restatements R9 owes" |
| the same | SPEC/06's "five records" and "four" are read against the reader's count; the run file's comment restated; the agent named `window-check` | the same; `milestones/M06/runs/f6_3_quickstart.yaml` |
| during the timed run | The first pull request is continued after its first commit was refused for a typo, not replaced by a second | `runs/pr4_expected.md` attempt 1 |
| 2026-10-03 | The ids go to `main` in a pull request of their own; the close is a fifth and RED | `rulings/grant-ids.md` (ruled, on `main`) |
| before the rollback | The fallback is read on `window-check`, not `owner-check`: one envelope cannot read a rollback and a retirement on one agent | `runs/f7_3_rollback.yaml`; `runs/pr4_expected.md` attempt 5 |
| at the close | Act 1 was not captured and is not re-made; a read-back from the records is filmed and filed as that | `docs/video/README.md`; `milestones/M08/open.md` rows 1, 2 |

The dispatches of the platform's jobs by the owner were the session's
instruction, taken by the owner; they were not ruled, and attempt 1's
statement did not allow them (`runs/pr4_expected.md`, "After the cold
review", item 2).

## 4. Row 7's amendment at the close

Row 7's text says F7.3 is read on `owner-check`'s platform upgrade
reverted when the swap is not merged. It was read on `window-check`'s
(item 3; cold review F6). The row gets one dated sentence, shown to the
seat before it is written, and nothing else in the row's claim,
falsifiers or expected output is reworded:

> **Amended at the close (Product, `rulings/pr4.md`): the swap read RED
> and was not merged, and the rollback was read on `window-check`'s
> platform upgrade reverted, not `owner-check`'s: `owner-check` is
> retired before the closing run, which deletes the runtime F7.3 reads.**

## 5. Every Unsure item of #38, #39, #40, #42 and #44

Rows of `milestones/M08/open.md` are "M08 row n".

| Item | Where it ended |
|---|---|
| #38 A, B, C, D, E, H, J (panel 2's source) | Ruled: `rulings/pr2-security.md` (three Apps; admin bypass off; installations on all repositories; the relaxation from `main` by a dispatch input; `observations/` and the cell's envelope; what a retirement removes; 13d) |
| #38 F: `platform_check.py` to Security | Done: ADR-0012, `rulings/pr3.md`. Reading a ruling commit's author: **open**, M08 row 22 |
| #38 G: the revert not green; the candidate's access | Ruled by the Threshold Owner (`rulings/pr2-threshold-owner.md` item 3, `pr3-threshold-owner.md`). Moot: the swap was not merged |
| #38 I, Q; #39 T1, T2, T5 | Ruled or done: the three bars (`a34bcfa`); ADR-0011; `two-key` on `deprecated_after` (`rulings/pr3-threshold-owner.md`) |
| #38 J: the Grafana token | **Open**, the human's: M08 row 27 |
| #38 K: a retired golden's citations | **Open**: no Data Owner ruling in M07. M08 row 30 |
| #38 L, M | Ruled and done: `rulings/pr1.md`, `rulings/pr2.md` |
| #38 N: an IAM user name and account ids in envelopes | **Open**: M08 row 22 |
| #38 O; #39 P5; #40 L: the compliance map | The page says it is unverified. Its redraft was owed at this close and **is not made**: M08 row 22 |
| #38 P: PR 1's repairs not read cold | **Open**: M08 row 23 |
| #39 P1, P2 | Done: SPEC/07 §2's amendment (`rulings/pr3.md`); ADR-0011 |
| #39 P3, P4 | Ruled as written: SPEC/07 §12 ("live" from the deploy run and the image; no idle trigger) |
| #39 P6; #40 A | Replaced by `rulings/pr3.md`: PR 4 carries every attempt but the owner's test, read from the pull request's own viewpoint |
| #39 13a to 13m | Ruled: `rulings/pr2-security.md` as written, `rulings/pr3-security.md` by item; 13h, 13i, 13j, 13l done in PR 3 |
| #39 13n | **Done here**: `pr4-security.md` item 4 |
| #39, the three unlabelled Security bullets | Ruled or done: `rulings/pr2-security.md`, `pr3-security.md` |
| #39 T3, T4 | **Open**: M08 row 21 |
| #39 E1 to E5; #40 B, C | Ruled: `rulings/pr2-engineering.md`, `pr3-engineering.md`, `pr3.md`. Read live: the App's commits are verified, committer `web-flow` |
| #40 D, E, G, M | Ruled: ADR-0012; `rulings/pr3-security.md`; #42 |
| #40 F: when B2 and B3 are deployed | Ruled in `rulings/pr3-security.md`, and **not followed**: `pr4-security.md` item 1; M08 row 11 |
| #40 H, I, J | **Open**: M08 row 20 |
| #40 K: the `two-key` seed and `make plants` | **Open**: M08 row 22 |
| #40 N: B1's template hash | **Open**, by hand: `pr4-security.md` item 8; M08 row 12 |
| #42: `ruled_in` not moved; the cap cell's form | Ruled: `rulings/grant-ids-security.md`, `grant-ids.md` |
| #44 | Section 7 below: each with its seat and what is taken; ruled by this file's first line and the other two files' |

## 6. Every Finding

Collected from `feasibility.md`, every ruling file of M07, the seat
reports in #38 to #44 and the attempts' records. Those with no complete
home before the close, and where they went:

| Finding | Home |
|---|---|
| F7.0 fired: the owner's test deployed 32,264 s after its merge; three faults of the platform's own | recorded: SPEC/07 §12; M08 row 4 (Security; Engineering) |
| The model upgrade not taken: Haiku 4.5 regressed `g-004` | recorded; M08 row 14 (Threshold Owner; Engineering) |
| Five pull requests; the by-hand precondition that missed its pull request | recorded: `rulings/grant-ids.md`; M08 row 3 (Product) |
| F6.1's live half not held on the first commit | M08 row 17 (Product; Engineering) |
| Act 1 not captured; Act 2 not recorded; cuts 2 to 4 unrecorded | M08 rows 1, 2 (Product) |
| The timed values are not the schedules' latency | M08 row 18 (Product; Threshold Owner; Engineering) |
| The relaxation accepted and detected; no viewpoint sees `bypass_actors` | M08 rows 8, 9 (Security; Product; Engineering) |
| Two actions on `runtime/*`; narrower forms untried | M08 row 5 (Security) |
| A failed create needs the admin; two keys pending deletion | M08 row 6 (Security) |
| A retired agent's stack keeps a role, and two network interfaces stayed | M08 row 7 (Security) |
| The observer's put role: "main only" has not fired | M08 row 10 (Security) |
| Three deploys before any ruling; a session's part in them | `pr4-security.md` item 1; M08 rows 11, 12 (Security; Product) |
| The sign stored as `?`; the stored reason is the old text | M08 row 13 (Security; Engineering) |
| Fourteen tests red on a moved pin | M08 row 15 (Engineering) |
| The packer's order on Windows | M08 row 16 (Engineering) |
| S2 never read on a new head; pull requests and branches left open | M08 row 19 (Product; Engineering) |
| PR 3's items left as the code stands | M08 row 20 (Security; Engineering) |
| The Threshold Owner's open items | M08 row 21 |
| Two reads not recorded under `runs/`; the marker read once | M08 row 24 (Security; Engineering) |
| Six contradictions with M08's text | M08 row 25 (Product) |
| The profile's list; the narration | M08 row 26 (Product) |
| The statement for PR 3 was wrong on `template.F6_2` | closed: recorded in `runs/pr3_expected.md` and `rulings/pr3.md` |
| Two commits were authored as `floresinnovations` by the session's checkout | closed: #41 closed unmerged, #42 in its place; `d79915c` amended to `78aac19`. `milestones/M07/README.md` |
| A sentence that said the App's viewpoint sees `bypass_actors` | closed: corrected in SPEC/07 §12 and the README |
| The first bootstrap deploy's diff not kept | closed as lost; `runs/b2_cdk_diff.md` says so and gives the stored template's comparison |

`milestones/M07/open.md`'s rows that M07 did not close are copied into
`milestones/M08/open.md` as rows 27 to 62, each with its M07 row number (rows 63 and 64 were added after the second review);
the rows ruled "not built" at M07's open are named in that file's
header and not copied.

## 7. #44's own Unsure items

Each was taken as its recommended option. The seat named rules it by
ruling its file as written, or writes otherwise beside the item.

| # | What | Taken | Seat |
|---|---|---|---|
| A | Whether `m07` is tagged | Section 8 | Product |
| B | The three deploys made before any ruling: keep, narrow or revert | Keep; the narrowing is `milestones/M08/open.md` row 5 (`pr4-security.md` items 1, 2) | Security |
| C | The read-back is filed under its own heading and not as Act 1; its file is committed in M08 PR 1, like a milestone video; it is held to an act's ceilings (eight minutes, 64 MiB), since none is ruled for a read-back | As written | Product |
| D | The fourteen tests that fail on a moved pin, and four notes on tests from the second read, are carried and not repaired here | M08 rows 15, 23 | Engineering |
| E | `relax_seed()` stays in `scripts/platform_check.py` with no caller | Kept as the record, with its tests; M08 row 8 | Security |
| F | The owner's dispatches in the timed run were not allowed by its statement | Recorded as that. F6.3's elapsed time is GitHub's and AWS's own whatever started the jobs; the bar was not moved | Product; Threshold Owner |
| G | Row 7's amendment sentence (section 4) | Written into the row only on the seat's word | Product |
| H | The compliance map's redraft, owed at this close, is not made; a note on the page says so | M08 row 22 | Product |
| I | The explainer runs to about three screens; SPEC/00 §10.3 says one | Left: the page is M06's length; M08 row 64 | Product |
| J | SPEC/00 is amended at the close (§8 M07, one paragraph) | As written; the other stale sentences of SPEC/00 are M08 row 64 | Product |
| K | `docs-current` is not built, so "runs `docs-current` before a close" was a read by hand | M08 row 63 | Product; Engineering |
| L | The session's AWS reads were made as the agent account's admin user | Said where each is recorded; M08 row 12 | Security |

## 8. The tag

`/close-milestone` lists "the PR count would be five" among its refusals
to tag. CLAUDE.md says a fifth pull request is "a RED close with the
finding as the result". `rulings/grant-ids.md` ruled the fifth and the
RED and did not speak of the tag (cold review 2, F4).

**Recommended: `m07` is tagged**, on `main`, at this pull request's merge
commit, by the human, after the merge, as `m01`, `m04`, `m05` and `m06`
were on RED closes. A tag names the commit a closed milestone's evidence
is at, and later files cite it: the ledger header's `validate` row,
ADR-0005's "recorded at tag", M08's open. What the refusal guards, that
five pull requests are not passed off as an ordinary close, is met by
the row: RED, `5 / 4`, with the finding written. **Alternative: no
tag**; each of those then cites the merge commit, as
`milestones/M08/open.md` row 3 says.

Ruled as recommended by this file's first line, unless the seat writes
the alternative here. No session places the tag.

## 9. The docs-writer's read of `d653c7d`, and what was done

`docs-current` is not in the tree (item K), so its conditions were read
by hand by `docs-writer`. Its report is in a comment on #44.

| What it found | Status |
|---|---|
| `docs/developer/upgrade.md`: "no upgrade has run"; a retired agent redeployed "at a new address"; "no retirement has run"; the check "has not run on a real repository"; no rollback section | **Repaired**: what has run, with the envelope's numbers; setting `rollout` back deploys nothing; a section on undoing an upgrade |
| `docs/developer/quickstart.md`, `template-README.md`: "M06's timed run"; "read again at M07"; the schedules | **Repaired**. The template repository's own README keeps the old sentence until the template is next re-made (M08 row 64) |
| `docs/platform/surfaces.md`: panel 2 "not deployed" | **Repaired**: read live at the close, 55 rows |
| `docs/platform/overview.md`, `CLAUDE.md`: `ratings-helper` "(M07)" | **Repaired**: its code is not built in this project |
| `docs/compliance/map.md`: every M07 row behind | **A note**, not a redraft: item H |
| `docs/video/README.md`: "two kinds"; two names for the read-back's file | **Repaired** |
| SPEC/00 §8 M07 has no close amendment | **Repaired**: one paragraph (item J). §8 M08, §10.2's table and §12's rollback sentence: M08 row 64 |
| The explainer: ten rewordings (who started the platform's jobs; the model is proposed for the reference agent only; 368 s is to the delete; one change failed, not "every"; three wrong statements, not one; the dispatches counted; "none did" overreached; one person holds every seat; "almost nine hours"; "four and a half hours") | **All ten taken** |
| The explainer names the deploy role (also cold review 2, F5) | **Repaired** |
| `README.md` says "Governed" with five rows RED; `CLAUDE.md`'s two omissions; the quickstart's "until M07" | M08 row 64 |

## What a reader can run

```
make ledger                                    # exit 0; row 7 RED, 5 / 4, its cell the envelope's line
uv run pytest -q tests/test_m07_seeds.py tests/test_m06_seeds.py
git log --format='%h %cI %s' origin/main..HEAD -- milestones/M07/runs/pr4_expected.md   # each statement before its record
gh api repos/agentkeel-studio/window-check --jq .created_at
gh api repos/agentkeel-studio/owner-check/rulesets/24310403 --jq .updated_at
aws dynamodb get-item --table-name agentkeel-registry --key '{"name":{"S":"owner-check"}}' --query Item.retired_at
grep -c "^| [0-9]" milestones/M08/open.md        # 64
grep -n "governed\|secure\|proven" docs/milestones/M07.md   # nothing but the claim's own word, if it is quoted
```
