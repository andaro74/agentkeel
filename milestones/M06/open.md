# Carried into M06

Written at M05's close (PR 4, 2026-09-30). `/open-milestone` reads this
file first. An item dated "before M06 PR 1" is answered before that PR's
first commit; "at M06 open" is in M06 PR 1; a later milestone is where the
item's claim is measured, and it waits there. Sources: the M05 cold
reviews (`milestones/M05/rulings/pr2-engineering.md`,
`pr3-engineering.md`), the seat rulings, the PR bodies' Unsure lists (#30,
#31, #32), SPEC/05 §8 to §10, and the rows of `milestones/M05/open.md` that
M05 did not close (`milestones/M05/feasibility.md` §6). A seat marked
*(proposed at the close)* was named by no source; Product proposed it in
`rulings/pr4.md`.

Read at M06 PR 1 before anything else: row 5 of `milestones/README.md`
and the envelope its Measured cell names, not this file's prose. Row 5 is
**RED on S1 and S7**: S1 refused by the missing route, which no flow record
can show (`rulings/pr2.md` ruling 9); S7 refused at the rights-table read
before any model call, so no model call is recorded (`rulings/pr3.md`
ruling 1). S2, S3, S4 and S6 refused and recorded within N, the slowest
307 s.

| # | Item | Source | Seat | When |
|---|---|---|---|---|
| 1 | **M05's video**, recorded on `main` at tag `m05`, ≤ 5 minutes and ≤ 40 MiB, committed in M06 PR 1 as an LFS object with its row in `docs/video/README.md` (ADR-0005 amendment 1). What it must show is in that row; Product confirms it against the recording. | SPEC/00 §10.5; ADR-0005 amendment 1 | Product | before M06 PR 1 (recorded); at M06 open (committed) |
| 2 | **The stand-in's grant, by name, in the security account's bucket policy.** `agentkeel-refagent-standin` was deleted on 2026-09-30 at 03:58:11Z (`NoSuchEntity` at 03:58:19Z, `milestones/M05/runs/security_account.md`), but the policy still **allows** its ARN a put under `agents/refagent/standin/*`, matched by name. A role recreated with that name and path (by the agent account's admin, or by `agentkeel-cfn-exec` from `main`) gets the grant back. Its reach: that one prefix; the Deny on `events/` stands; a write adds a version and modifies nothing. Remove the Allow in the next hand deploy of `infra/security/`; keep the two Denies that name it. | `milestones/M05/rulings/pr3-security.md` F2; `pr3-engineering.md` N7 | Security | at M06 open |
| 3 | **`ecsTaskExecutionRole` in the security account**, left from before the cleanup; trusted by `ecs-tasks` only, read by nothing. Delete it or say why it stays. | #31 and #32 Unsure N; `pr2-security.md` §7 (platform F4) | Security | at M06 open |
| 4 | **The other stacks' cdk-nag suppressions have no `appliesTo`**, so each suppresses every finding of its rule on its resource (the defect repaired on refagent's role at `ca0d07d`). | `pr2-security.md` §7, second read N3; #32 | Security | M06 |
| 5 | **`agents/refagent/manifest.yaml`'s `s3` comment still says image layers only**; the endpoint also lets the audit put out from M05 PR 2. A comment there moves the bundle digest, so it rides the first change to refagent that redeploys anyway. | `pr2-security.md` §7 (platform NOTE 5); #32 | Engineering (the path); Security (the note) | M06 |
| 6 | **S3's "stream still there" is the human's word.** No reader looks the log stream up after the refusal; the run file says it. | `pr3-engineering.md` N2; #32 | Engineering | M06 |
| 7 | **The Rule Owner's filter on tool results, and S5's live half** (SPEC/05 §9 cut 1): a deployed tool result carrying a key, and the filter measured live. With it, M05 `open.md` row 2 (a change to a definition's wording takes two keys, read by `two_key.py`; until then the Rule Owner files the second key by hand) and row 3 (`guardrail.yaml`'s stale comments at lines 15, 50, 51, 65), which ride the first `rules/**` change. | SPEC/05 §9 cut 1; `rulings/pr2.md` ruling 1; M05 `open.md` rows 2, 3 | Rule Owner; Data Owner and Engineering (the live half) | M06 |
| 8 | **The reader is the PR's own code** (M05 `open.md` row 12): anyone with write can edit `src/verdict/`, `src/gates/`, the Makefile or `runtime_for_tree`. From M05 also: any same-repository PR's code can read `AWSLogs/` in the audit bucket through `agentkeel-audit-read` (read-only; both accounts' management events). Take the reader from `main`, with the required workflows the template ships. | M05 `open.md` row 12; `pr2-security.md` §7 (security NOTE, platform NOTE 4) | Security, Engineering | M06 |
| 9 | **The rights-table marker is read once, before the run** (`scripts/runtime_for_tree.py`); re-read it and the image tags after the last call. | M05 `open.md` row 4 | Engineering, Security | M06 |
| 10 | **Makefile paths that write no envelope** (M03 `open.md` row 11 item i). | M05 `open.md` row 5 | Engineering | M06 |
| 11 | **Nothing keeps the guardrail's examples away from the attacks** (at most 4 shared words at M03; no check reads it); and **Promptfoo as the red-team runner** (M04 cut 5). Both with row 23, the guardrail re-examined with retrieval. | M05 `open.md` rows 6, 7 | Rule Owner | M06 |
| 12 | **The eval role's invoke is not conditioned on the guardrail**, over four models; SPEC/04 §8's seeded refusal of a model call without the pinned guardrail has not been attempted in AWS. With it, the eval role's Deny recorded as a refusal (M03 `open.md` row 14). | M05 `open.md` rows 8, 16; SPEC/05 §8 | Security | M06 |
| 13 | **`<arn>:*` lets the eval role, the agent role and the promoter apply DRAFT and versions 1 to 5**; only the runtime's invoke is pinned. | M05 `open.md` row 9 | Security | M06 |
| 14 | **The promoter's egress outside the platform VPC; the ingest record write-once by code, not IAM (N11); none of the ingest stack's refusals attempted in AWS (N13).** With row 20's ingest redeploy. | M05 `open.md` rows 11, 15 | Security | M06 |
| 15 | **The agent's raw output committed** (M03 `open.md` row 11 item b). | M05 `open.md` row 16; `feasibility.md` §6 | Security, Engineering | M06 |
| 16 | **Three notes on M04's swap read**: `--strict-cards` accepts any 40-hex card in the history folder (N3); `card_at` raises `KeyError` on a reference without `path` or `sha256` (N4); the own-PR `note` decodes `§` twice (N5). | M05 `open.md` row 43 | Engineering | M06 |
| 17 | **"Stated before the attempt" rests on a local commit time.** S7's expected reading (`e1a6bb2`) was committed 91 s before the attach, but nothing outside the machine dated it until its push. Push a stated-before commit before the attempt it states. | `pr3-engineering.md` N3 | Product *(proposed at the close)* | at M06 open |
| 18 | **`g-010`'s answer is mostly in the corpus** once refagent reads it. Ruled before retrieval lands, whatever its row here. | M05 `open.md` row 25 | Data Owner | M06 |
| 19 | **A trap where no row governs** needs an absence form in SPEC/00 §6 and a reader that grounds a `found: false` call; with the Tool Owner's question whether a not-found result offers `ML-2.3`. | M05 `open.md` row 26 | Data Owner, Tool Owner; Product (SPEC/00 §6) | M06 |
| 20 | **The promoter's record keeps no guardrail version, and records assessment keys such as `invocationMetrics` as policies.** One ingest redeploy. | M05 `open.md` row 27 | Security, Engineering | M06 |
| 21 | **`agent.py` keeps `cacheReadInputTokens`, and the cached-answer seed.** | M05 `open.md` row 28 | Engineering; Product (the seed) | M06 |
| 22 | **The knowledge base over the production bucket, and refagent retrieving from it**; F3.5's second half; `g-014` counted as a plant. | M05 `open.md` row 29 | Product; Security | M06 |
| 23 | **`topics_apply_to: input` re-examined, and `g-014` blocked or masked.** Until then a swap's plants fire before the candidate model is called. | M05 `open.md` row 30 | Rule Owner | M06 |
| 24 | **Fourteen corpus clauses are outside `data/clause_index.json`.** | M05 `open.md` row 31 | Data Owner | M06 |
| 25 | **FRAGILE**, with `docs/developer/goldens.md`. | M05 `open.md` row 32 | Data Owner | M06 |
| 26 | **A second agent's model** (`ratings-helper`'s pin). | M05 `open.md` row 33 | Threshold Owner | M06 |
| 27 | **Ceilings computed from the org graph; the rest of `ratings-helper`'s tool work.** | M05 `open.md` row 34 | Tool Owner | M06; M07 |
| 28 | **The chain reached refagent unchanged: inferred, not read** (Unsure F). AgentCore handed refagent the session id (the refusal event is keyed by it); that the chain arrived as sent rests on the 403, since only a chain deeper than 2 or a malformed one is refused, and the envelope keeps no event body. A caller can lie about its depth until Identity carries the chain. | #30, #31, #32 Unsure F; `rulings/pr3.md` ruling 4; SPEC/05 §8 | Engineering; Security (Identity) *(proposed at the close)* | M07 |
| 29 | **The audit bucket's policy names refagent only**; a second agent's prefix and principal come with its code. | `pr2-security.md` §7 (platform NOTE 6) | Security | M07 |
| 30 | **Nothing mechanical compares deployed pins with the tree** (the guardrail version's description against the rule files' digest; the promoter's `GUARDRAIL_VERSION` against the manifest). | M05 `open.md` row 14 | Security, Engineering | M07 |
| 31 | **A merged swap's first envelope in a mode the swap never ran in fails `F4_4`.** Stands as SPEC/04 §2 wrote it until an upgrade moves a pin. | M05 `open.md` row 21 | Threshold Owner | M07 |
| 32 | **The gateway**, with the Gateway tool form; direct Converse until then (ruled 2026-09-27). | M05 `open.md` row 22; SPEC/05 §10 | Product, Security, Threshold Owner | M07 |
| 33 | **k6**: fan-out at the ceiling, and p95 as a load reading (SPEC/05 §9 cut d). | M05 `open.md` row 23 | Engineering; Threshold Owner (the bar it reads) | M07 |
| 34 | **Credentials only via Identity; the per-agent Budgets filter; the nightly declared-vs-observed graph diff** (SPEC/05 §9 cuts b, c). | SPEC/05 §9 | Security; Engineering (the diff) *(proposed at the close)* | M07 |
| 35 | **`model-watch`**, which also catches the model changing under an unchanged pin; its shadow run needs a GitHub App or a token. | M05 `open.md` row 35 | Engineering; Security (the App or token) | M07 |
| 36 | **The judge**: the Bedrock Evaluations judge pinned in the manifest, its rubric, graded examples, `admitted_false_fails.json`, and `model-watch` on the judge. | M05 `open.md` row 36 | Threshold Owner (the judge); Data Owner (false fails) | M07 |
| 37 | **The Braintrust mirror**, its divergence check, redaction before upload. | M05 `open.md` row 37 | Engineering; Security (redaction) | M07 |
| 38 | **`deprecated_after` set from Bedrock by code.** Until then the Threshold Owner reads `modelLifecycle` on each swap PR. | M05 `open.md` row 38 | Threshold Owner | M07 |
| 39 | **The cheaper swap's run (Haiku 4.5), never made**; recorded as taken at M04's close. | M05 `open.md` row 39 | Threshold Owner | M07 |
| 40 | **Sonnet 4.5 is not equivalent on `g-005`.** Any M07 upgrade candidate list starts from this finding. | M05 `open.md` row 40 | Threshold Owner | M07 |
| 41 | **A refusal by the missing route leaves no record** (S1's finding, `rulings/pr2.md` ruling 9). Routing drops a packet for an outside address before any security group or network ACL sees it, so no flow record is made, from any origin in the VPC. Recording the attempt needs something that sees it before the drop; no other kind of record stands in for the flow record. With it, **Unsure C for flow logs**: 600 s held for every attempt recorded at M05 (worst 307 s, a CloudTrail record, `alarm_latency_s` 307), but no flow record was ever made for S1, so whether N holds for flow logs is unread. | `rulings/pr2.md` ruling 9; SPEC/05 §8; #30, #31, #32 Unsure C | Security; Threshold Owner (N) | M08, with the hostile copy |
| 42 | **A quarantine that refuses the agent's first call hides the model call F5.4 reads** (S7's finding, `rulings/pr3.md` ruling 1). Under the deny-all, refagent's rights-table Scan is refused before Converse, so no model call is made or recorded; the caller's answer (the Scan refused by `agentkeel-quarantine`) is the only sign the quarantine held on the right role, and it feeds no reading (`pr3-engineering.md` N4). The full kill switch is F8.5's. | `rulings/pr3.md` ruling 1; `pr3-engineering.md` N4; SPEC/05 §9 cut f | Security, Product | M08 |
| 43 | **No gate reads the lock's retention in `infra/security/`**: a later pull request could shorten the default for new objects with one ruling. Closing it is a SPEC/00 §5 amendment (Unsure D). | #30, #31 Unsure D; SPEC/05 §8 | Product, Security | M08, where F8.4 measures seven years |
| 44 | **SPEC/01 §9's ceiling as a seeded case**, with the hostile copy that calls outside the ceiling from the runtime (Unsure A). | #30, #31 Unsure A; `feasibility.md` §6 row 16 | Security | M08 |
| 45 | **The controls M05 PR 2 added that no seed attempts** (SPEC/05 §8): the envelope-put role refusing a pull request's token; the read role outside its three prefixes; the S3 endpoint refusing another account's bucket; the stand-in refused without MFA; the Deny on `events/`; a put under `envelopes/` without If-None-Match; refagent's own explicit denies (`iam:*`, `sts:AssumeRole`, `s3:PutBucketPolicy`, the guardrail verbs); the quarantine started by the Budgets alarm. None is described as working. | SPEC/05 §8; `pr2-security.md` §7 (platform F5, F6) | Security | M08 |
| 46 | **GuardDuty Runtime Monitoring; R5's seven-year retention** (SPEC/05 §9 cuts a, e). | SPEC/05 §9 | Security; Product and Security (the retention's two keys) | M08 |
| 47 | **Injection aimed at the judge.** | M05 `open.md` row 41 | Rule Owner | M08 |
| 48 | **The agent account is the organization's management account.** No SCP binds it (M05 `open.md` row 17, N14: an admin can remove the production bucket's policy or change the promoter), and it can enable centralized root access and `sts:AssumeRoot` into the security account (read 2026-09-28: not enabled; nothing stops it). The landing zone's (SPEC/00 §12); the OIDC provider's origin with it. Rule at M06 open whether it stays deferred past M08. | M05 `open.md` rows 16, 17; `pr2-security.md` §1, §7 (platform F1); SPEC/05 §8 | Security | at M06 open |
