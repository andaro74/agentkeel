# Carried into M04

Written at M03's close (PR 4, 2026-09-26). `/open-milestone` reads this
file first. An item dated "before M04 PR 1" is answered before that PR's
first commit; "at M04 open" is in M04 PR 1; a later milestone is where the
item's claim is measured, and it waits there. Sources: the M03 cold
reviews (`milestones/M03/rulings/pr1-engineering.md`, `pr2-engineering.md`,
`pr3-engineering.md`), the seat rulings, the PR bodies' Unsure lists (#19,
#20, #21), their first comments, and `milestones/M03/open.md` rows that M03
did not close (`feasibility.md` §6).

Read at M04 PR 1 before anything else: row 3 of `milestones/README.md` and
the envelope `cb06c0d`, not this file's prose. That envelope is in
`mode: runner`. **No envelope reads the runtime at guardrail version 5**
(row 10).

| # | Item | Source | Seat | When |
|---|---|---|---|---|
| 1 | **SPEC/00 §9's "8–10 invented documents".** Its own list comes to seven with both amendments; six are admitted and the seventh is seed S5, never admitted. Five of the six are under a page. Amend the count, or the corpus grows. | #20 Unsure A; `pr2-data-owner.md` | Product | at M04 open |
| 2 | **ADR-0009 reads a rule file's examples, not its definitions.** A definition narrowed under the same name is one key. An ADR-0009 amendment, or a line that says it stays one key. | #20 Unsure B; `pr2-rule-owner.md` F4 | Product (the Rule Owner proposes) | at M04 open |
| 3 | **`g-010`'s answer is mostly in the corpus** once refagent reads it (the answer-side overlap). | #20 Unsure E; `data-owner` F1 on PR 2 | Data Owner | at M04 open |
| 4 | **`g-015.yaml` line 1 is stale**: "deal terms requested for a third party" and "no guardrail exists before M03". A comment; the id and the question are unchanged. | #21 Unsure A; `pr3-rule-owner.md` NOTE | Data Owner | at M04 open |
| 5 | **`g-021` has never passed.** How an absence trap cites; retire it with two keys and re-add under a new id, or keep it. | #21 Unsure F; `pr3.md` ruling A; `pr1.md` (`data-owner` F6); M03 `open.md` row 5 | Data Owner, Tool Owner | at M04 open |
| 6 | **Whether the deployed bootstrap template reads `§`** where it read `?` (metadata only). | #21 Unsure D | Security | at M04 open, read from the first bootstrap `cdk diff --strict` |
| 7 | **N16: the bootstrap template is 47,601 of CloudFormation's 51,200 inline bytes.** Roughly two more topics with examples. | `pr3-security.md` (ruled) | Security | at M04 open, before any addition to that stack |
| 8 | **The promoter's record keeps no guardrail version.** S5's scan is version 4's only by `admitted_at`. | `pr3-security.md` NOTE (ruled) | Security, Engineering | at M04 open, when refagent first reads the corpus |
| 9 | **The promoter records assessment keys, `invocationMetrics` among them, as policies.** Recorded at PR 2 with no date; changing it is an ingest redeploy. | `pr2-engineering.md` N7 | Engineering, Security | at M04 open, in the same ingest redeploy as row 8 |
| 10 | **The first envelope in `mode: runtime` at `1088aw3ujhyd:5`.** None exists at M03's close: PR 3's envelope `cb06c0d` is in the runner, `main`'s run 36272077628 reused it, and M03 PR 4 changed only paths `evals.yml` does not measure. The runtime at `:5` is read only by deploy run 36272077619's load check (20 observations, 0 errors, the seven plants `guardrail_intervened`), a deploy log that prints no topics and no version. No page says the runtime blocks the plants by their named rules until an envelope shows it. | #21 Unsure B, C; `pr3-security.md` | Product, Security | at M04 open: the first measured run in `mode: runtime` |
| 11 | **The rights-table marker is read once, before the run** (`scripts/runtime_for_tree.py:76`). A load mid-run changes the table under a `runtime` envelope; re-read the marker and the image tags after the last call. Raised on `606bece` in #20 (first comment, `security-reviewer` F1) with no disposition. | #20 first comment | Engineering, Security | at M04 open |
| 12 | **The Threshold Owner's re-rule of the cap** (150,000) against the first envelope with retrieval; the stale `thresholds.yaml` comment ("about 6,000", "not measured yet"); the control's fairness (M02 §8); `check_model_access`. | `pr3-threshold-owner.md` §4 | Threshold Owner | at M04 open |
| 13 | **`delta_max`, the relative regression bar.** At M03 the bar is P7 and R2 as `judge` holds them: any regressed golden blocks. | SPEC/03 §10; `feasibility.md` F11, §6 row 4 | Threshold Owner | at M04 open |
| 14 | **`pinned_roles` carry region, version and the T2 limit; the stub's model fields move with the swap.** | M03 `open.md` row 12 | Threshold Owner | at M04 open |
| 15 | **`agent.py` keeps `cacheReadInputTokens`**, so `build`'s prompt-cache refusal can fire; the cached-answer seed SPEC/00 §8 named for M03. Until then `cache_state: disabled` is a constant, not a reading. | `feasibility.md` B2 and §6 | Engineering (the reader); Product (the seed) | at M04 open |
| 16 | **The knowledge base over the production bucket, and refagent retrieving from it** (SPEC/03 cut 6, taken at M03 open). With it: F3.5's second half, "or changes an answer"; `g-014` (MASKED) counted as a plant. | SPEC/03 §8, §9 | Product (the SPEC); Security (the stack) | at M04 open |
| 17 | **`topics_apply_to: input`**: the six topics do not block on the answer. M03 had nothing on the answer side to catch; re-examine with retrieval. And `g-014` could be blocked rather than masked (`red-teamer` on the guardrail draft, #20). | `pr2-rule-owner.md`; #20 first comment | Rule Owner | at M04 open |
| 18 | **Fourteen corpus clauses are outside `data/clause_index.json`** (ML-2.2, ML-4.1, ML-5.1, ML-6.1, ML-15.1, AM1-1, AM1-3, HS-1, HS-3, HS-5, MC-1, MC-2, MC-5, EM-3). An answer citing one fails F1.4 until a ruling adds it. | `pr2-data-owner.md` | Data Owner | at M04 open |
| 19 | **SPEC/03 cuts 1 to 4 were never built, and no ruling took them at the time**: the Braintrust mirror with its divergence check and redaction before upload (cut 1), the Bedrock Evaluations judge pinned in the manifest with its rubric (cut 2), `admitted_false_fails.json` (cut 3), the FRAGILE state (cut 4). SPEC/03 §9 allowed each "only if the cap is threatened"; recorded as taken at M03's close (`rulings/pr4.md`), each to the milestone §9 names. Until the judge exists, "correct" is the deterministic comparison of answer fields. | SPEC/03 §9; found at the close | Product; Threshold Owner (the judge); Data Owner (FRAGILE, false fails) | at M04 open |
| 20 | **`red-teamer` reads the open milestone's SPEC**, not SPEC/03 only. | `pr1-rule-owner.md` N5 | Rule Owner | at M04 open |
| 21 | **Nothing keeps the guardrail's examples away from the attacks.** At most 4 shared words at M03; no check reads it. Recorded at PR 2 with no date. | `pr2-engineering.md` N9 | Rule Owner | at M04 open |
| 22 | **M02 `open.md` row 11, items f, h and i**: `server.py`'s profile default and docstring; the gate takes `build`'s token sums as given; Makefile paths that write no envelope. | `feasibility.md` §6, row 11 | Engineering | at M04 open |
| 23 | **SPEC/00 §3 says the poisoned-corpus threat "lands in the knowledge base"**, which M03 cut; the explainer says "reading pile" and "bucket". | `docs-writer` on #19 | Product | at M04 open |
| 24 | **M03's video**, recorded on `main` at tag `m03`, ≤ 5 minutes and ≤ 40 MiB, committed in M04 PR 1 as an LFS object with its row in `docs/video/README.md` (ADR-0005 amendment 1). What it shows is in that row. | ADR-0005 amendment 1 | Product | before M04 PR 1 (recorded); at M04 open (committed) |
| 25 | **Cut 5, Promptfoo as the red-team runner**; until then the five attacks run as goldens. `red-teamer.md` names Promptfoo when it lands. | SPEC/03 §9; `pr1-rule-owner.md` N4 | Rule Owner | M05 |
| 26 | **N8 / F4: the eval role's invoke is not conditioned on the guardrail.** The plants (F3_2) catch a dropped `guardrailConfig`; IAM does not. | `pr2-security.md`; `pr3-security.md` (ruled) | Security | M05 |
| 27 | **N10: `<arn>:*` lets the eval role, the agent role and the promoter apply DRAFT and versions 1 to 5**; only the runtime's invoke is pinned. | `pr3-security.md` (ruled) | Security | M05 |
| 28 | **R10's N** is not in `thresholds.yaml`; dated to M03 PR 2 and slipped. | `pr3-threshold-owner.md` §5 (ruled); #21 Unsure E | Threshold Owner | M05 |
| 29 | **The promoter's egress outside the platform VPC.** Not an agent; M05's per-agent egress does not cover it. | `pr2-security.md` F4; #20 Unsure G | Security | M05 |
| 30 | **The reader is the PR's own code**: anyone with write can edit `src/verdict/`, `src/gates/`, the Makefile or `runtime_for_tree` so its own envelope or gate says GREEN. Take the reader from `main`. | `pr1-security.md` NOTE 3; #19 Unsure D; SPEC/03 §8; `security-reviewer` F2 on `606bece` | Security, Engineering | M05 |
| 31 | **S3 data events on the production bucket.** | `pr1-security.md` NOTE 6 | Security | M05 |
| 32 | **Nothing mechanical compares deployed pins with the tree**: the guardrail version's description against the rule files' digest, the promoter's `GUARDRAIL_VERSION` against the manifest. Read by hand at each deploy. | `pr3-security.md`; `pr3-rule-owner.md` F4; `pr3-engineering.md` N5 | Security, Engineering | M05 |
| 33 | **The ingest record is write-once by code, not IAM (N11); none of the ingest stack's own refusals has been attempted in AWS (N13)**: the put, delete, replication, hold and re-lock denials, Object Lock's day, the promoter's five grants. No page calls them working. | `pr2-security.md`; SPEC/03 §8 | Security | M05 |
| 34 | **SPEC/01 §9's ceiling, a seeded case**; M02 `open.md` row 11 items a, b, c, d and k; M03 `open.md` row 14 (M02's M05 items). | `feasibility.md` §6 | Security, Engineering | M05 open |
| 35 | **N14: an admin can remove the production bucket's policy, or change the promoter or its admitted list.** An SCP, deferred with the landing zone (SPEC/00 §2, §12). | `pr2-security.md`; SPEC/03 §8 | Security | M05 open |
| 36 | **Ceilings computed from the org graph; the rest of `ratings-helper`'s tool work.** | M03 `open.md` row 13 | Tool Owner | M06; M07 |
| 37 | **Injection aimed at the judge.** | SPEC/03 §8 | Rule Owner | M08 |
