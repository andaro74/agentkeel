# Carried into M05

Written at M04's close (PR 4, 2026-09-27). `/open-milestone` reads this
file first. An item dated "before M05 PR 1" is answered before that PR's
first commit; "at M05 open" is in M05 PR 1; a later milestone is where the
item's claim is measured, and it waits there. Sources: the M04 cold
reviews (`milestones/M04/rulings/pr1-engineering.md`, `pr2-engineering.md`,
`pr3-engineering.md`), the seat rulings, the PR bodies' Unsure lists (#23,
#24, #27), SPEC/04 §8 to §10, and `milestones/M04/open.md` rows that M04
did not close (`feasibility.md` §6). A seat marked *(proposed at the
close)* was named by no source; Product proposed it in `rulings/pr4.md`.

Read at M05 PR 1 before anything else: row 4 of `milestones/README.md`
and the envelope its Measured cell names, not this file's prose. Row 4 is
**RED on F4.2**: the equivalent swap (#26, Sonnet 4.5) regressed `g-005`
on its first run (`9ff21d5`) and again on its re-run (`a86262e`).

| # | Item | Source | Seat | When |
|---|---|---|---|---|
| 1 | **Every `evals` run still reads M04's two swap PRs** through `milestones/M04/runs/f4_swaps.yaml`, and prints them in every envelope's `swaps`. They are closed unmerged after M04 PR 4's run. Stop reading them, or say why a closed swap stays in every envelope. `READ_THE_SWAPS` keys the reading to row 4 alone, so no later row's cell turns on them. | M04 PR 4 (`rulings/pr4.md`) | Engineering, Product | at M05 open |
| 2 | **ADR-0009's last amendment: a change to a definition's wording takes two keys**, read by `two_key.py`. Until it lands, the Rule Owner files the second key by hand. | M04 `open.md` row 2; `pr1-rule-owner.md`; #23 Unsure G | Rule Owner proposes; Product rules | at M05 open, or the first `rules/**` change, whichever is first |
| 3 | **Stale comments in `agents/refagent/rules/guardrail.yaml`**: lines 15 "(M04)", 50 "until M04", 51 "at M04", 65 "a third party". | M04 `open.md` row 17; `pr1-rule-owner.md` | Rule Owner | at M05 open, or the first `rules/**` change, whichever is first |
| 4 | **The rights-table marker is read once, before the run** (`scripts/runtime_for_tree.py:76`); re-read it and the image tags after the last call. SPEC/04 §9 cut 2 was taken because PR 2's run was in the runner. | M04 `open.md` row 11; `pr2.md` §4 | Engineering, Security | M05 |
| 5 | **Makefile paths that write no envelope** (M03 `open.md` row 11 item i). Items f and h were done at M04 PR 2. | M04 `open.md` row 22 | Engineering | M05 |
| 6 | **Nothing keeps the guardrail's examples away from the attacks.** At most 4 shared words at M03; no check reads it. | M04 `open.md` row 21 | Rule Owner | M05, with Promptfoo (row 7) |
| 7 | **Cut 5, Promptfoo as the red-team runner**; until then the five attacks run as goldens. | M04 `open.md` row 25 | Rule Owner | M05 |
| 8 | **The eval role's invoke is not conditioned on the guardrail**, and from M04 PR 2 it covers three more models (Sonnet 4.5, Llama 3.1 8B, Haiku 4.5). With it, SPEC/04 §8's seeded refusal of a model call made without the pinned guardrail, or around the agent's own profile: nothing has attempted it in AWS. | M04 `open.md` row 26, new row 40; `pr2-security.md` §3; #24 security F1 | Security | M05 |
| 9 | **`<arn>:*` lets the eval role, the agent role and the promoter apply DRAFT and versions 1 to 5**; only the runtime's invoke is pinned. | M04 `open.md` row 27 | Security | M05 |
| 10 | **R10's N** is not in `thresholds.yaml`, and `threshold-owner` flags it with no gate reading it. | M04 `open.md` row 28; #23 Unsure F | Threshold Owner, Product | M05 |
| 11 | **The promoter's egress outside the platform VPC.** | M04 `open.md` row 29 | Security | M05 |
| 12 | **The reader is the PR's own code**: anyone with write can edit `src/verdict/`, `src/gates/`, the Makefile or `runtime_for_tree`. From M04: a swap PR that also edits `src/verdict/` can switch off its own A-vs-A and `F4_3` (`pin_moved` is the PR's own). Take the reader from `main`. | M04 `open.md` row 30; `pr2-security.md` §3; #24 security F3 | Security, Engineering | M05 |
| 13 | **S3 data events on the production bucket.** | M04 `open.md` row 31 | Security | M05 |
| 14 | **Nothing mechanical compares deployed pins with the tree**: the guardrail version's description against the rule files' digest, the promoter's `GUARDRAIL_VERSION` against the manifest. | M04 `open.md` row 32 | Security, Engineering | M05 |
| 15 | **The ingest record is write-once by code, not IAM (N11); none of the ingest stack's own refusals has been attempted in AWS (N13).** | M04 `open.md` row 33 | Security | M05 |
| 16 | **SPEC/01 §9's ceiling, a seeded case**; M03 `open.md` row 11 items a, b, c, d and k; M03 `open.md` row 14. | M04 `open.md` row 34 | Security, Engineering | at M05 open |
| 17 | **N14: an admin can remove the production bucket's policy, or change the promoter or its admitted list.** An SCP, deferred with the landing zone. | M04 `open.md` row 35 | Security | at M05 open |
| 18 | **A commit claiming the bot's email is attributed to the bot.** Swap branches are outside the ruleset, so anyone with write can push a hand-made envelope there; `evals_on_measured` is the independent record, and `verification.verified` cannot be required. | #27 Unsure C; `pr3-security.md` §1, §2 F2; `pr2-engineering.md` F4 | Security, Product | at M05 open |
| 19 | **Scripts run under the eval role's session are Engineering's path, not Security's.** Whether they need the Security seat is a SPEC/00 §5 amendment. | #27 Unsure D; `pr3-security.md` §2 F4 | Product (SPEC/00 §5) | at M05 open |
| 20 | **The bootstrap template is 49,173 of 51,200 bytes at M04 PR 3**, against 49,107 measured at PR 1; the 66 bytes between are not accounted for. | #27 Unsure F; `pr3-security.md` §3 item 4 | Security | at M05 open, before any addition to that stack |
| 21 | **A merged swap's first envelope in a mode the swap never ran in fails `F4_4`** for having no incumbent. | #24 Unsure E; `pr2-threshold-owner.md` note 9; `pr2-engineering.md` N4 | Threshold Owner | at M05 open |
| 22 | **The gateway decision**: the pin for every caller and every version, what CloudTrail records, the refusing statement. Direct Converse stays until it is ruled. | M04 `feasibility.md` §6 row 39; SPEC/04 §10 | Product, Security, Threshold Owner | at M05 open |
| 23 | **k6** (SPEC/04 §9 cut e). Until it lands, `p95_ms` is the per-answer latency, not a load reading. | SPEC/04 §9; `pr1.md` ruling 3 | Engineering; Threshold Owner (the bar it reads) *(proposed at the close)* | M05 |
| 24 | **The second read of M04 PR 3's repairs** (`70a979b`, `63712c7`, `12ebb54`) had no third cold read before #27 merged. M04 PR 4's cold review reads them (`rulings/pr4-engineering.md`); anything it finds lands here. | #27 Unsure B | Engineering, Security | before M05 PR 1 |
| 25 | **`g-010`'s answer is mostly in the corpus** once refagent reads it. The first row of M06's `open.md`, ruled before retrieval lands. | M04 `open.md` row 3 | Data Owner | M06 |
| 26 | **A trap where no row governs** needs an absence form in SPEC/00 §6 and a reader that grounds a `found: false` call (`g-021` retired at `fe70686`); with the Tool Owner's question whether a not-found result offers `ML-2.3`. | M04 `open.md` row 5; `pr2-data-owner.md` §1 | Data Owner, Tool Owner; Product (SPEC/00 §6) | M06 |
| 27 | **The promoter's record keeps no guardrail version, and records assessment keys such as `invocationMetrics` as policies.** One ingest redeploy. | M04 `open.md` rows 8, 9 | Security, Engineering | M06 |
| 28 | **`agent.py` keeps `cacheReadInputTokens`, and the cached-answer seed.** | M04 `open.md` row 15; SPEC/04 §9 cut f | Engineering; Product (the seed) | M06 |
| 29 | **The knowledge base over the production bucket, and refagent retrieving from it**; F3.5's second half; `g-014` counted as a plant. The second move; a third needs a SPEC/00 amendment. | M04 `open.md` row 16; SPEC/04 §9 cut f | Product; Security | M06 |
| 30 | **`topics_apply_to: input` re-examined, and `g-014` blocked or masked.** Until then a swap's plants fire before the candidate model is called, so "plants 7 of 7" on a swap PR says nothing about the new model. | M04 `open.md` row 17; SPEC/04 §8 | Rule Owner | M06 |
| 31 | **Fourteen corpus clauses are outside `data/clause_index.json`.** | M04 `open.md` row 18 | Data Owner | M06 |
| 32 | **FRAGILE**, with `docs/developer/goldens.md`. | SPEC/04 §9 cut d | Data Owner | M06 |
| 33 | **A second agent's model** (`ratings-helper`'s pin). | SPEC/04 §10 | Threshold Owner *(proposed at the close)* | M06 |
| 34 | **Ceilings computed from the org graph; the rest of `ratings-helper`'s tool work.** | M04 `open.md` row 36 | Tool Owner | M06; M07 |
| 35 | **`model-watch`**, which also catches the model changing under an unchanged pin; its shadow run needs a GitHub App or a token. | SPEC/04 §9 cut a; §8 | Engineering (the code); Security (the App or token) *(proposed at the close)* | M07 |
| 36 | **The judge**: the Bedrock Evaluations judge pinned in the manifest, its rubric, graded examples, `admitted_false_fails.json`, and `model-watch` on the judge. | SPEC/04 §9 cut b; M04 `open.md` row 19 | Threshold Owner (the judge); Data Owner (false fails) | M07 |
| 37 | **The Braintrust mirror**, its divergence check, redaction before upload. | SPEC/04 §9 cut c; M04 `open.md` row 19 | Engineering; Security (redaction) *(proposed at the close)* | M07 |
| 38 | **`deprecated_after` set from Bedrock by code.** Until then the Threshold Owner reads `modelLifecycle` on each swap PR. | SPEC/04 §9 cut g | Threshold Owner | M07 |
| 39 | **The cheaper swap's run (Haiku 4.5), reported, not ruled, was never made.** SPEC/04 §9 cut 1 allowed it "only if the cap is threatened", and the cap was not (97,635 of 150,000); no ruling took the cut at the time. Recorded as taken at M04's close (`rulings/pr4.md`). | SPEC/04 §9 cut 1; found at the close | Threshold Owner *(proposed at the close)* | M07 |
| 40 | **Sonnet 4.5 is not equivalent on `g-005`** (a local-time embargo: 01:30 UTC on 14 May is still 13 May in São Paulo). Any M07 upgrade candidate list starts from this finding; the label "equivalent" was not moved (SPEC/04 §2). | row 4; `pr3.md` §3 | Threshold Owner | M07 |
| 41 | **Injection aimed at the judge.** | M04 `open.md` row 37 | Rule Owner | M08 |
| 42 | **M04's video**, recorded on `main` at tag `m04`, ≤ 5 minutes and ≤ 40 MiB, committed in M05 PR 1 as an LFS object with its row in `docs/video/README.md` (ADR-0005 amendment 1). What it must show is in that row; Product confirms it against the recording. | SPEC/00 §10.5; ADR-0005 amendment 1 | Product | before M05 PR 1 (recorded); at M05 open (committed) |
