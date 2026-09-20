# M01 feasibility note

Milestone M01, claim 1: *An unsigned or tampered bundle never loads;
refagent runs inside the construct.* SPEC/01 is `SPEC/01-signed-bundle.md`.
Opened at M01 PR 1 (#7), 2026-09-19, through `/open-milestone`.

This note names the commit and inputs that make the claim false (§3), the
code that reads the answer (§4), the falsifiers (§5), and what happened to
every item M00 carried in (`milestones/M01/open.md`, §6).

## 1. `product-spec-reviewer` report (pasted verbatim, 2026-09-19)

Run against SPEC/01 as first drafted, before anything else in PR 1 was
written. SPEC/01 was revised once afterwards, on the rulings in §2; the
report is of the first draft and is not edited to match.

---

product-spec-reviewer — SPEC/01-signed-bundle.md (M01), before PR 1

Read: SPEC/01 (untracked draft), SPEC/00 §3–§10.3, milestones/README.md, milestones/M01/open.md. There is no milestones/M01/README.md yet. I also checked docs/adr/ and thresholds.yaml, because SPEC/01 names them.

**1. BLOCK. The deploy runs only on `main`, so PR 2 cannot measure before it merges (checks 1, 2, 8).**
- §5 S2: "The signature over the recorded digest is made by CI, so it is PR 2's first commit, before the verifier".
- §6: "Deploy workflow … on `main` only".
- §2: "The certificate identity is the deploy workflow on `main` … and nothing else."
- What is wrong: a PR 2 branch cannot hold a signature from the `main` deploy identity, because that workflow is not on `main` until PR 2 merges. The same applies to S1/S2's "deploy workflow's verify step" and to refagent's first CI envelope, which needs refagent deployed. Any signature made on the branch is refused for its identity, not its digest, so S2 can pass for the wrong reason. The measurement then lands after PR 2, against P3.
- What would settle it: a ruling on which identity signs S2, and on which run, before PR 2 merges, produces refagent's first envelope.
- Seat: Product, with Security (cosign identity).

**2. BLOCK. False state 4 is already true for an admin (checks 1, 5).**
- §3.4: "A deploy of refagent's stack succeeds from a laptop, with credentials that are valid in the account but are not the deploy workflow's."
- §2: bootstrap is "Deployed once per account, by a human with admin".
- What is wrong: an admin on a laptop can run CloudFormation directly. The deploy role's trust policy (S4's reader) does not stop that. So the seed only passes if it picks a non-admin principal, and the plain sentence "a laptop, is refused" claims more than is measured.
- What would settle it: a ruling that names the principal in false state 4 and narrows the plain sentence to match.
- Seat: Product, with Security.

**3. BLOCK. F1.4 is redefined, so row 1 can be GREEN with refagent citing nothing (checks 3, 4, 8).**
- SPEC/00 §8: "F1.4 refagent answers an ordinary golden without `table_row` and `clause_id`."
- SPEC/01 §4 observation: "`kind: ordinary`, `cites: false` and `pass: true`".
- §8: "agent history is empty at the first run, so the checks decide it".
- What is wrong: under `pass = score and cites`, an uncited answer is `pass: false`. On empty history it lands in `never_passed` and does not gate (P7). F1.4 then fires only on a bug in `build`, never on refagent's behaviour, which is what SPEC/00 names.
- What would settle it: a ruling on whether an uncited refagent answer at the first run turns row 1 RED. It must come before PR 1, because the F1.4 rule lands in PR 1.
- Seat: Product. SPEC/00 wins.

**4. FINDING. Half of the claim has no false state (check 1).**
- §1: "refagent runs inside the construct".
- §2: "An agent exists on this platform only as an instance of it."
- What is wrong: none of false states 1–7 covers refagent deployed or synthesised outside `GovernedAgent`.
- What would settle it: an eighth false state, or a ruling that this half is covered by S3/S5.
- Seat: Product.

**5. FINDING. S4 and S6 evidence is hand-made, in a Product path (checks 1, 3; P5, P11).**
- §5: "`milestones/M01/runs/f1_1_laptop.yaml` … PR 2 (the attempt, made and recorded)".
- §8: "`AccessDenied`, recorded in their observation files by the run that made them".
- What is wrong, S4: the attempt is from a laptop by definition, so a human writes the observation that `checks.F1_1` rests on.
- What is wrong, S6: the spec does not say who can assume the agent role to call `kms:GetKeyPolicy`. That role is trusted by AgentCore, not by CI or a human.
- What is wrong, both: neither seed has a code reader, so the "`xfail(strict=True)` … cannot quietly start passing" rule in §5 cannot apply to them.
- What would settle it: a ruling on the principal and runner for each attempt, and on whether a human-written file under `milestones/` can feed `checks`.
- Seat: Product, with Security.

**6. FINDING. The reader for `checks.F1_1`–`F1_3` is not named (check 2).**
- §8: "refagent's envelope carries `checks.F1_1`, `F1_2`, `F1_3` (pass: the falsifier did not fire, with the run URL)".
- What is wrong: §6 lists no runner that writes these raw observations. It does not say how `build` gets a `deploy.yml` verify result, a pytest synth refusal, or a YAML file under `milestones/`. Without that, the instrument may end up deciding the verdict.
- What would settle it: one line per check naming the runner that writes the raw observation and the path `build` reads.
- Seat: Engineering.

**7. FINDING. Part of F1.1 cannot be seen in the repo (check 3).**
- §4 F1.1: "or a CloudFormation stack for a seed in the account".
- What is wrong: the account is not the repo, so a reader cannot check this without AWS access.
- What would settle it: drop that clause or name the file that records the stack listing.
- Seat: Product.

**8. FINDING. The expected output for refagent is not stated before the run (check 4).**
- §8: "S1 and S2 refused … F1.4 is read on its `goldens`."
- What is wrong: there is no expected count for refagent: ordinary x/9, traps x/3, guardrail `never_passed` 3, `plants_expected`.
- A second gap: "`make plants` lists S1–S7" puts infrastructure seeds under the word "plant". The plant rule in SPEC/00 §5 counts golden plants in `plants_expected`. Which count S1–S7 join is not said.
- What would settle it: numbers written into the ledger row at open, and one sentence on whether S1–S7 enter `plants_expected`.
- Seat: Product.

**9. FINDING. The load check verifies a digest, not a signature (checks 5, 8).**
- §6: "The agent's container entrypoint checks the bundle's digest against the digest the deploy recorded in the stack".
- SPEC/00 §6: "Runtime refuses an unsigned or mismatched digest".
- SPEC/00 §5 `signature`: "digest matches manifest".
- What is wrong, first: an unsigned bundle whose digest was recorded by a non-pipeline deploy passes the load check. The explainer title "Nothing runs unsigned" rests on this check.
- What is wrong, second: the two specs name different places for the digest, the stack and the manifest.
- What would settle it: a ruling on what the entrypoint verifies and where the digest lives.
- Seat: Security, with Product.

**10. FINDING. Two cited ADR amendments do not exist (check 8).**
- §2: "ADR-0003 amendment 1".
- §4 and §7: "ADR-0004 amendment 2".
- What is wrong: both ADRs have `amendments: 0` and `amendments: 1` in the tree. Amendment 2 would be ADR-0004's last. §7 also adds envelope fields that SPEC/00 §6 does not list: `control_card_ref`, `tokens_in`, and a one-subject envelope. The schema is `additionalProperties: false`.
- What would settle it: both amendments, and the SPEC/00 §6 field list, land in PR 1 before the F1.4 rule commit.
- Seat: Product. The ADRs' `authorises:` must name Engineering and Threshold Owner.

**11. FINDING. SPEC/01 rules items that belong to the Threshold Owner (checks 7, 8).**
- §7: "Cost is a recorded RED" (open.md #22), "The card's `region` is the request region" (#23), and the `m00` card hash "in `thresholds.yaml`" (#5).
- §6: "Sonnet 4.6 through `us.anthropic.claude-sonnet-4-6`".
- What is wrong: each of these belongs to the Threshold Owner. Item 22 is dated "before M01 PR 1".
- What would settle it: Threshold Owner ruling files cited from SPEC/01, not Product text.
- Seat: Threshold Owner.

**12. FINDING. Items due "before M01 PR 1" bear on this spec and are unruled (check 8).**
- §4: "F1.4 is read by `verdict.build` and, separately, by `verdict.gate`." open.md #6 says `build` and `gate` share code "so they cannot disagree".
- §5 S7: "fifteen raw replies, typed by hand". open.md #1 asks whether `tests/fixtures/` is exempt from the hand-written rule.
- What is wrong: both items are dated "before M01 PR 1", and both shape the F1.4 commit that lands in PR 1.
- What would settle it: rulings on #6 (Engineering) and #1 (Product) before PR 1's first commit.

**13. FINDING. `validate` grows less than SPEC/00 schedules (check 8).**
- SPEC/00 §5: "From M01 PR 1, when their inputs exist: manifest schema, seats assigned to real groups, CODEOWNERS ↔ manifest, edges two-sided, no cycles, ceilings within bounds, cdk-nag, workflow file hash unchanged".
- SPEC/01 §6 names only the manifest schema. §10 defers only CODEOWNERS and the gates.
- What is wrong: cdk-nag and the workflow hash have their inputs at M01 (open.md #29, #32), and SPEC/01 is silent on them.
- What would settle it: list each check as M01 or deferred, with its milestone.
- Seat: Product.

**14. FINDING. `platform-architect` is missing.**
- SPEC/00 §8 M01: "Adds `platform-architect` (R8)."
- What is wrong: SPEC/01 does not mention it. R8 says it is written in PR 1 and exercised on the milestone's seeded case.
- What would settle it: name it in SPEC/01 with the seed it is exercised on (S3 or S5).
- Seat: Product. The prompt's `seat:` is Security.

**15. FINDING. `agents/**` has no seat, and one file has several (check 7).**
- §2: "`agents/<name>/{manifest.yaml, prompt.txt, tools/, rules/}`".
- What is wrong, no seat: `agents/**` is in neither SPEC/00 §5 nor CLAUDE.md's table, so `agents/refagent/` agent code and `prompt.txt` have no seat.
- What is wrong, several seats: `manifest.yaml` carries fields owned by Rule Owner, Tool Owner and Threshold Owner.
- What is wrong, globs: it is unclear whether `rules/**` and `tools/**` match `agents/<name>/rules/` and `agents/<name>/tools/`.
- What would settle it: a SPEC/00 §5 amendment giving `agents/**` a seat and stating the glob scope.
- Seat: Product.

**16. FINDING. The eval role's name collides during PR 2 (check 8).**
- §6: "the eval role, absorbed from `infra/eval-role/` … The M00 stack `AgentkeelM00EvalRole` is deleted after PR 2 merges."
- open.md #20: "`agentkeel-m00-evals` is a fixed role name … Delete the M00 stack, or the names collide", due "at M01 PR 1".
- What is wrong: the bootstrap stack deploys in PR 2, while the M00 stack still holds the name.
- What would settle it: a ruling on the order: delete first, or rename the role.
- Seat: Security.

**17. FINDING. The cap is threatened by the core build, which the cut list cannot touch (check 6).**
- §9 cuts five items: ratings-helper, log delivery, knowledge base, HITL, inference profile. It is ordered and cuts no seed.
- §6 then leaves in PR 2 about 20 build items besides the five cuttable ones: 8 in bootstrap, the construct's 3 AgentCore services plus egress refusal, `deploy.yml`, `pack`/`verify`, the load check, the manifest schema, DynamoDB, the tool, the runner, the §7 envelope changes, and the S4/S6 live attempts. Every one of them is on the never-cut list or has no cut.
- The item I expect to break the cap: `GovernedAgent` with AgentCore Runtime, Gateway and Identity, together with the main-only deploy in finding 1. A repair then has only PR 3 left.
- What would settle it: a ruling on whether Gateway and Identity are never-cut at M01.
- Seat: Product.

**18. NOTE. False state 7 and F1.4 use different connectives.**
- §3.7: "no `table_row` or no `clause_id`".
- §4 F1.4: "without `table_row` and `clause_id`" (the SPEC/00 wording).
- The first says "or" and the second reads as "and". SPEC/00 §9 says "missing either". One word in F1.4 settles it. Seat: Product.

**19. NOTE. M01 is mapped to a threat SPEC/00 does not give it.**
- §1: "the negligent developer whose agent answers without citing the table".
- SPEC/00 §3 maps the negligent developer to M02 and M06, not M01. For the record. Seat: Product.

**20. NOTE. The F1.4 reader lands in PR 1.**
- §6: "None of it is in PR 1, except the F1.4 rule".
- CLAUDE.md, PR 1: "Nothing that makes it pass."
- The rule makes S7 go RED, not pass, so there is no conflict in effect. It is still a reader in the plant PR, which CLAUDE.md's PR shape does not describe. Record it in feasibility.md. Seat: Product.

**21. NOTE. The Budgets figure has no seat.**
- §6: "a Budgets action on the eval role at `daily_usd: 10`".
- The number is set in a Product spec. SPEC/00 §5 gives no seat for `daily_usd`, and open.md #34 names Security with Threshold Owner for the spend figure. Seat: Threshold Owner.

BLOCK: 3 · FINDING: 14 · NOTE: 4

---

## 2. Rulings

### 2.1 The seats' rulings for M01 PR 1 (2026-09-19, before the first commit)

The seats ruled on the 35 items of `milestones/M01/open.md` before this PR
was written. They bind this PR. Each is listed in §6 against its item, and
carried in `rulings/pr1.md`. Three are quoted here because this note is
where they were asked to be written.

- **Items 4 and 6, Engineering. Closed, no split.** "P5 separates
  judgment, not inputs. `replay_history` and `plants.plant_ids` are inputs
  both build and gate read; neither rules on anything. P5 requires that
  build's verdict and gate's verdict are computed separately from the same
  inputs, which `tests/test_p5_disagree.py` shows." The same sentence is in
  `src/verdict/__init__.py`'s docstring. F1.4 is computed twice, in
  `build.f1_4` and `gate.f1_4`, and `tests/test_gate.py`
  (`test_the_gate_reads_f1_4_for_itself`) shows them disagreeing.
- **Item 1, Product. Exempt, scoped.** CLAUDE.md gains: "The one exception
  is a seed under tests/fixtures/: a false state, never copied to
  evals/history/, named in tests/fixtures/README.md." S7 is a raw file,
  not an envelope, and is named there anyway.
- **PR 1's own run, Engineering with the Threshold Owner.** First ruled:
  with no agent under test, `make evals` writes the control card and no
  envelope. **Superseded by ruling A (§2.5):** a run always writes an
  envelope; with no agent it is the control's, in M00's form.

### 2.2 On the report: the three BLOCKs, ruled before PR 1 opened

| # | Ruling | Seat |
|---|---|---|
| BLOCK 1 | `verify` checks signature, identity and digest and reports **every** reason, so S2 is refused on its digest whoever signed it. PR 2 measures S1, S2, S3, S5 (and S7, S8) on the PR run, with the PR run's own identity accepted for that measurement only. When S4 and S6 are measured, as ruled before PR #7 merged (ruling 4; this replaces the draft first written here): The bootstrap stack is deployed to the agent account by the human with admin during PR 2, before PR 2's first CI run, as infra/eval-role was at M00. S4 and S6 are attempted by the human against that stack during PR 2; each attempt's request id, timestamp and AccessDenied text are written to milestones/M01/runs/f1_1_laptop.yaml and f1_3_key_policy.yaml, and a CloudTrail lookup in PR 2's CI run (scripts/observe_attempt.py, the F0.3 observer's pattern) confirms each request id was denied and writes checks.F1_1 and checks.F1_3. A human-written file feeds no check by itself; the check is the CI lookup of the request id. Refagent's first agent envelope is PR 2's. Nothing about claim 1 is first measured after PR 2 merges (P3). | Product, with Security |
| BLOCK 2 | The laptop principal of false state 4 is the developer role the bootstrap stack creates, boundary on. The admin who deploys the bootstrap stack is break-glass; stopping them needs a service control policy, which is landing-zone work (SPEC/00 §2, §12) and a deferred item. The explainer says so plainly. The §10.3 sentence stays. | Product, with Security |
| BLOCK 3 | `build` writes `checks.F1_4 = fail` when any agent ordinary result has `cites: false`; the gate works it out again from `goldens` and rejects any disagreement (P5). Row 1 goes RED on uncited answers whatever the history. It rides in ADR-0004 amendment 2 with rule (d). S7's envelope is RED. | Product |

SPEC/01 was revised on these three, once, before any other file in this
PR was committed.

### 2.3 On the report: FINDINGs and NOTEs

| # | What happened to it |
|---|---|
| 4 | Repaired. SPEC/01 §3 false state 8 and seed S8 (`tests/fixtures/construct/outside_construct.py`). |
| 5 | Partly repaired: S6 now grants `kms:GetKeyPolicy` in the role's own policy for the attempt, so only the key policy can refuse it, and records the request id. S4 is by definition from a laptop. Whether a human-written observation file can feed `checks.F1_1`/`F1_3`, and who runs each attempt, is **Unsure**: Security with Product, at M01 PR 2 open. |
| 6 | Repaired. SPEC/01 §4 names the source of each check; Engineering names the runner at PR 2 open. |
| 7 | Repaired. The clause is gone from F1.1. |
| 8 | Repaired. SPEC/01 §8 and the ledger row state what is expected, and that no count of refagent's passes is expected on empty history (P7). S1–S8 are seeded cases, not plants, and do not enter `plants_expected`; `make plants` lists them separately. |
| 9 | Repaired with `platform-architect` BLOCK 3: the load check verifies the signature, outside the bundle's own code, on a digest-pinned image. Where the digest lives (the stack or the manifest; SPEC/00 §5 says "digest matches manifest") is **Unsure**: Security with Product, at M01 PR 2 open. |
| 10 | Repaired. ADR-0003 amendment 1 and ADR-0004 amendment 2 are in this PR, with SPEC/00 §6's field list, in the commit before the F1.4 reader. |
| 11 | Repaired by citation. Items 5, 22 and 23 are the Threshold Owner's rulings (§2.1, §6), carried in `rulings/pr1.md` with the Threshold Owner's key; SPEC/01 §7 names them as such. The Sonnet 4.6 pin is the Threshold Owner's, from the M00 table, now in `agents/refagent/manifest.yaml`. |
| 12 | Repaired. Items 1 and 6 were ruled before PR 1's first commit (§2.1). |
| 13 | Repaired. SPEC/01 §6 lists each `validate` check with its milestone; the ledger header has the M01 PR 1 row. |
| 14 | Repaired. SPEC/01 §5 names `platform-architect`, exercised on S3, S5 and S8 at PR 2. Its prompt is in this PR and it was run once on SPEC/01's design; its report is in the PR body. |
| 15 | Repaired. ADR-0003 amendment 1 gives `agents/**` its seats and says `rules/**` and `tools/**` cover `agents/*/rules/**` and `agents/*/tools/**`. |
| 16 | Repaired. SPEC/01 §6: the bootstrap stack makes the eval role under a new name; order is deploy, repoint `AWS_EVAL_ROLE_ARN`, run, delete the M00 stack after PR 2 merges. Security confirms at PR 2 open. |
| 17 | Carried. Whether Gateway and Identity are never-cut at M01: Product, at M01 PR 2 open. |
| 18 | Repaired: "missing either fires it". |
| 19 | Repaired: the negligent-developer line is gone from §1. |
| 20 | Recorded here: the F1.4 reader is in PR 1, by the seats' ruling 5/11(d). It makes the seed go RED, not pass. |
| 21 | Recorded: `daily_usd: 10` is the Threshold Owner's number (item 34), named so in SPEC/01 §6. |

### 2.4 On the `platform-architect` report (in the PR body)

The report is a draft for Security and goes in the PR body, not here. Its
four BLOCKs:

- **BLOCK "S2 cannot be signed by the identity the verifier trusts"** and
  **BLOCK "S4 tests only the deploy role's trust policy"**: settled by the
  rulings on `product-spec-reviewer` BLOCKs 1 and 2.
- **BLOCK "the CloudFormation execution role is admin"**: repaired in
  SPEC/01 §6 as a PR 2 requirement (the execution role carries the
  boundary and may create a role only with it; the CDK bootstrap roles
  trust the deploy role only). Security confirms at PR 2 open.
- **BLOCK "the check at load does not check provenance"**: repaired in
  SPEC/01 §6 as a PR 2 requirement (signature verified at load, outside
  the bundle's code; image pinned by digest; tag-immutable repository).
  Security confirms at PR 2 open.

Its FINDINGs are PR 2 design for Security. The ones that cost only text
went into SPEC/01 now: the OIDC provider imported, the deploy role's four
trust conditions, the boundary stack-wide with a synth test, VPC mode
only, account-scoped endpoint policies, the egress check over the whole
stack (and S3's second form), the key policy's explicit denies, S6
isolating the key policy, and SPEC/01 §9's list of controls with no
seeded case. The rest go to Security at M01 PR 2 open, listed in
`milestones/M01/README.md`.

### 2.5 Rulings on the PR 1 Unsure items (2026-09-19, R1)

Added to the rulings above; they bind this PR.

| | Ruling | Seat |
|---|---|---|
| A | An envelope holds one subject: the agent when one ran, otherwise the control, in M00's form (`scope: control`, `control_card_ref: null`, `baseline_card_ref` this run's own card, commit-matched). A run always writes an envelope. `cost_cap --no-envelope` is removed; an over-cap control-only run is a recorded RED like any other (item 22). `gate.read` checks the `thresholds.yaml` `baseline_card` hash only when a result is `scope: agent`. In ADR-0004 amendment 2. | Engineering, with Threshold Owner |
| B | From this PR a two-key change cites two ruling files, each with one seat in `seat:`. This PR writes `rulings/pr1.md` (Product; the Product, Security and Engineering paths, seat named per path in the body) and `rulings/pr1-threshold-owner.md` (Threshold Owner; `thresholds.yaml` and the model-id fields of `agents/refagent/manifest.yaml`; Engineering's key for both is in `pr1.md`). Both carry `pr: 7`. M00's multi-seat files stand. Written into `.claude/skills/cold-review/SKILL.md`. | Product, with Threshold Owner |
| C | Item 19: the "OIDC claims the role trusts" step requests a token and prints claims; it never calls STS. The wording is now "no step assumes the role with a token of its own; the diagnostic step requests one and prints its claims." The step stays. | Security |
| D | Item 33: `s3:PutBucketPolicy` joins the Deny in this PR. Five actions, one deploy. "Exactly four" is superseded. | Security |
| E | `cold-review-ruling` accepting a PR-carried ruling is known and by design at M00 and is not R9's line. Carried to M02 PR 1 with `ruling-cited`: `milestones/M02/open.md` item 1, with R9's sentence quoted. | Security |
| F | S7: the PR body names its falsifier, its seed commit and the file that reads it here. If that reader is anything other than build.py's `pass = score and cites`, it moves out of this PR and S7 stays xfail strict. After the commits, the seed commit is checked out and `pytest` run; the failing tests and their reasons are pasted in §3. | Engineering |
| G | The manifest's model `version` stays null until Bedrock returns a version for `us.anthropic.claude-sonnet-4-6`; re-ruled at PR 2 with the cap. | Threshold Owner |

### 2.6 Rulings for M01 PR 2 open (2026-09-19, R1)

Written before PR 2's first commit. They settle the lists under "For
Security", "For Product" and the Threshold Owner's items in
`milestones/M01/README.md`, and `product-spec-reviewer` findings 5, 9 and
17. PR 2 is the measurement (P3).

**SCOPE (Product).** Cuts 1, 3 and 4 of SPEC/01 §10 are taken **now**, at
open, not when the cap is threatened: `ratings-helper` → M02; the
knowledge base over `data/corpus/` → M03; the HITL branch → M07. Gateway
and Identity are **not** never-cut at M01 (finding 17): the construct
declares both as props and wires neither. Identity's claim is M05's
(credentials only via Identity); Gateway's is M02's edge and M07's HITL
tool. Never-cut stays as written in §10. refagent at M01 is Sonnet 4.6
through `us.anthropic.claude-sonnet-4-6`, the rights table in DynamoDB, and
the `check_availability` tool with its strict schema, inside
`GovernedAgent`. F1.4 reads the table and the tool.

**Security**

| | Ruling |
|---|---|
| a′ | **Ruling a, amended 2026-09-20 (Security with the Threshold Owner).** AWS will not build what (a) asked for: a Budgets Action cannot hang off a daily budget — "AWS Budgets Actions don't support daily granularity budget for now" (Budgets, 400, on the deploy). So the two halves separate. `agentkeel-bedrock-daily` at `daily_usd: 10` **notifies** an address the human passes at deploy and stops nothing. `agentkeel-bedrock-monthly` carries the `APPLY_IAM_POLICY` Deny on `bedrock:Invoke*`, at 30 × the daily figure, which is the literal translation of what was ruled and not a number anybody chose. **The figure that was ruled and the figure that stops anything are no longer the same figure**, and the bound is a month, not a day: a run that spends the month's figure in an afternoon is stopped after it. The Threshold Owner re-rules the monthly number against measured spend — 54,250 tokens a run, about USD 0.23 on Sonnet 4.6's published rates (run 35532168520), so USD 300 is roughly 1,300 runs of headroom. `infra/bootstrap/README.md` and SPEC/01 §9 carry it as a control that has not fired. |
| a | **Budgets action:** one budget, service = Amazon Bedrock, whole account, `daily_usd: 10`, action = attach a Deny on `bedrock:Invoke*` to the eval role. No per-agent filter at M01; the per-agent profile stays, and the filter is M05 with cost tagging. `infra/eval-role/README.md` (then `infra/bootstrap/`) states the lag as AWS gives it — Budgets data refreshes up to three times a day — and the worst case as "up to one refresh interval at the account quota". No invented figure. |
| b | **Key policy:** agent roles are matched by path, `aws:PrincipalArn` `StringLike` `arn:aws:iam::<account>:role/agentkeel/agents/*`. Adding an agent is not a Security redeploy. Every role `GovernedAgent` makes is created under path `/agentkeel/agents/`. |
| c | **Gateway targets and Identity providers with no security group:** deferred to M05, and listed in SPEC/01 §9 as a control with no seeded case at M01. They are not wired at M01 (SCOPE). |
| d | **`endpoint_allowlist` at M01** holds AWS service names only, an enum in the manifest schema: `bedrock-runtime`, `dynamodb`, `kms`, `logs`, `s3`. Each maps to a VPC endpoint of the bootstrap VPC, and the agent security group's egress allows only those endpoints: interface endpoints by their security group, S3 and DynamoDB by gateway-endpoint prefix list. A hostname that is not one of the five is refused at synth. Arbitrary hostnames are M05. |
| e | **S3 and DynamoDB are gateway endpoints**, with endpoint policies scoped to the account. SPEC/00 §8 M01's "interface endpoints only" is amended by **ADR-0006** (Security, one sentence: interface endpoints, plus gateway endpoints for S3 and DynamoDB), written in PR 2. |
| f | **The new eval role** grants `bedrock-agentcore:InvokeAgentRuntime` on refagent's runtime ARN only, and keeps the two pinned profiles and the five-action Deny. Name: `agentkeel-evals`. Order: the human deploys `infra/bootstrap` with admin → points `AWS_EVAL_ROLE_ARN` at `agentkeel-evals` → attempts S4 and S6 → PR 2's first CI run → after PR 2 merges, the human runs `npx cdk destroy` in `infra/eval-role`. |
| g | **cosign verify:** `--certificate-oidc-issuer https://token.actions.githubusercontent.com`, `--certificate-identity andaro74/agentkeel/.github/workflows/deploy.yml@refs/heads/main` for a deploy; and `verify` additionally reads the certificate's Source Repository Identifier extension (Fulcio OID `1.3.6.1.4.1.57264.1.15`) and refuses unless it is `1376369685`. On the PR run, `verify` accepts the PR run's identity for the measurement of S1 and S2 only, and says so in its output. |
| h | **Where the signed digest lives** (finding 9, with Product): in the cosign bundle written beside the archive in CI (`agents/<name>/dist/`, not committed) and as a tag on the deployed runtime. The manifest carries no digest of itself. |
| i | **Finding 5** is ruled in §2.5's ruling 4: the human attempts, CI looks the request id up in CloudTrail through `scripts/observe_attempt.py`, and that lookup writes `checks.F1_1` and `checks.F1_3`. |
| j | **Redeploy record:** the `describe-stacks` line and the `simulate-principal-policy` table go in `infra/eval-role/README.md` under "Redeployed 2026-09-19 (items 14, 33)". One refused call on a denied action is the `evals.yml` probe step at PR 2 (item 18). |
| k | **The re-export** of `infra/ruleset/main.json`, with `evals` as a required check, is PR 2's first Security commit. If the live ruleset still lists one check, stop and say so. (At the M01 PR 1 merge the live ruleset already listed both; the export in the tree is from before that change.) |

| q | **The cdk-nag report is committed.** Both stacks' `NagReport` CSVs are committed beside their `app.py`, written by the same synth `make validate` runs; the check compares them and fails if they differ, so a suppression cannot be added without the report beside it changing in the same commit. |
| r | **A suppression names what it serves.** A suppression on an IAM wildcard, a boundary rule or a key-policy rule names the seeded case (S3, S4, S5, S6 or S8) or the SPEC/01 §6 line that requires it. One that names neither is a finding, not a suppression: it comes out and the rule fails until a seat rules on it. `make validate` fails on a suppression that names neither. |
| s | **Two boundaries, one per plane** (BLOCK B, `platform-architect` BLOCK 1 and `security-reviewer` on the same). `agentkeel-boundary` stays the **agent plane's allow-list** and is attached only to roles under `/agentkeel/agents/`. It is what S5 and S6 read. `agentkeel-deploy-boundary` is a new **deny-list** for the deploy plane — the CloudFormation execution role, the deploy role, the developer role, the eval role, the Budgets action role and the VPC flow-log role — `Allow *` with the escalation, erasure, key-policy and network-opening primitives denied. The bootstrap stack applies the deploy boundary stack-wide, because it creates no agent role; `GovernedAgent` attaches the agent boundary by ARN, from the Security-owned parameter. The execution role's `iam:PermissionsBoundary` condition keeps naming the **agent** boundary, so a role the deploy creates under the agent path is capped by the allow-list. Two corrections to the shape proposed: (1) the deny-list does **not** deny `iam:*`, which would cap the execution role's `iam:CreateRole` and the deploy role's `iam:PassRole` to nothing and leave BLOCK B exactly where it was; the escalation primitives are denied by name instead (`CreateUser`, `PutUserPolicy`, `AttachUserPolicy`, `CreateAccessKey`, `Put`/`DeleteRolePermissionsBoundary`, `CreatePolicyVersion`, `SetDefaultPolicyVersion`). (2) it does **not** deny `sts:AssumeRole`, because the developer role carries it and S4's first two attempts are the deploy role's **trust policy** refusing them; a boundary that refused the assume first would re-make the defect repaired in `c5bfdd1`, one level up. R4 holds through the key-policy denies (`kms:PutKeyPolicy`, `CreateGrant`, `ScheduleKeyDeletion`, `DisableKey`), which is what R4 names. |
| t | **The agent boundary allows `kms:GetKeyPolicy`** (S6). An allow-list caps by omission, so taking the action out of the Deny at `c5bfdd1` was not enough: the boundary would still have been what refused S6, and F1.3 still a check that could not fail. The action is in the Allow now. A boundary is a ceiling, not a grant: no agent role's own policy grants it, and the key policy denies it by role path (ruling b). The one principal that ever holds it is the role the human makes for S6's attempt, and the key policy is then the only thing left to refuse. |

**PR 2 mechanics (Product with Security).** The PR opens as a **draft**
right after the Security setup commit, so `sign-fixture.yml` can run on
the `pull_request` event. The S2 signature is the bot's commit and
precedes `src/bundle/`. Row 1's measurement is the CI run on the head
that is merged; earlier branch runs are recorded, not cited. Pushes are
batched: one for the Security setup, one for the build (step 2), one
after the human's attempts. The PR is undrafted only after the attempts
are observed and the cold review is done.

**Engineering**

| | Ruling |
|---|---|
| l | **The agent runner** is `src/agent/run.py`, as the Makefile expects. On a PR it runs refagent's code in the runner; on `main` after the deploy it calls the deployed runtime. It writes raw observations only; `build` and `gate` are unchanged in role (P5). |
| m | **The envelope does not record the cap** — no schema change, and ADR-0004 has no amendment left. Instead `gate` reads `thresholds.yaml` as it stood at the envelope's commit (`git show <commit>:thresholds.yaml`), so a later cap change cannot re-read an old envelope. Written into `gate.py`'s docstring and into `tests/test_gate.py`. |
| n | **S2's signature** is PR 2's first commit. A Security workflow `sign-fixture.yml`, run once on the PR, `cosign sign-blob` keyless over S1's archive bytes, writes the bundle into `tests/fixtures/bundles/altered/` and commits as `github-actions[bot]`, before `src/bundle/` exists. S1 stays unsigned. `infra/workflows.sha256` is updated in the same PR. |

**Threshold Owner**

| | Ruling |
|---|---|
| o | `cost_cap.tokens_per_run` stays 150,000 until PR 2's first agent envelope is recorded; re-ruled in `rulings/pr2-threshold-owner.md` against that envelope's `tokens_in + tokens_out`. |
| p | refagent's model `version` stays null; re-ruled with (o). |

## 3. The false state

SPEC/01 §3 names eight. This PR plants each as its own commit, first in
the PR and before any code that reads it. Each commit adds the seed and
its one test in `tests/test_m01_seeds.py`, marked `xfail(strict=True)`.
`git show <commit> --stat` lists the seed and the test and nothing else
(`tests/fixtures/README.md` rides with S8).

Ruling F: each seed commit checked out in a worktree and `pytest -q` run
on it (2026-09-19); then that seed's test run with `--runxfail` to show
why it fails.

| Seed | Falsifier | Commit | `pytest -q` at that commit | The seed's test, `--runxfail` |
|---|---|---|---|---|
| S1 `tests/fixtures/bundles/unsigned/` | F1.1 | `a7b088e` | 84 passed, 1 xfailed | `test_s1_an_unsigned_bundle_is_refused`: `ModuleNotFoundError: No module named 'src.bundle'` |
| S2 `tests/fixtures/bundles/altered/` | F1.1 | `df7c735` | 84 passed, 2 xfailed | `test_s2_a_bundle_changed_after_signing_is_refused`: `ModuleNotFoundError: No module named 'src.bundle'` |
| S3 `tests/fixtures/construct/extra_egress.py`, `extra_egress_standalone.py` | F1.1 | `48669ba` | 84 passed, 3 xfailed | `test_s3_egress_not_in_the_manifest_is_refused_at_synth`: `ModuleNotFoundError: No module named 'infra.construct'` |
| S4 `milestones/M01/runs/f1_1_laptop.yaml` | F1.1 | `1b4c2f6` | 84 passed, 4 xfailed | `test_s4_a_laptop_deploy_was_refused`: `AssertionError: the attempt has not been made` |
| S5 `tests/fixtures/construct/role_without_boundary.py` | F1.2 | `19131e9` | 84 passed, 5 xfailed | `test_s5_a_role_without_the_boundary_is_refused_at_synth`: `ModuleNotFoundError: No module named 'infra.construct'` |
| S6 `milestones/M01/runs/f1_3_key_policy.yaml` | F1.3 | `091cc45` | 84 passed, 6 xfailed | `test_s6_the_agent_role_cannot_read_its_key_policy`: `AssertionError: the attempt has not been made` |
| S7 `tests/fixtures/refagent_raw_uncited.json` | F1.4 | `2f4cacb` | 84 passed, 7 xfailed | `test_s7_an_answer_that_cites_nothing_is_not_a_pass`: `SystemExit: 2`, build's argument parser refusing `--control-card`: the F1.4 reader is not in the tree |
| S8 `tests/fixtures/construct/outside_construct.py` | F1.1 | `6b8b8cf` | 84 passed, 8 xfailed | `test_s8_an_agent_outside_the_construct_is_refused_at_synth`: `ModuleNotFoundError: No module named 'infra.construct'` |

What this PR cannot plant: S2's signature, which only CI can make. It is
PR 2's first commit, over S1's bytes, before `verify` exists.

## 4. The code that reads the answer

- **In this PR, S7's reader:** F1.4, and nothing else. `src/verdict/build.py`
  writes `pass = score and cites` for agent ordinary and trap results and
  `checks.F1_4` (ruling on BLOCK 3); `src/verdict/gate.py` works both out
  again from `score` and `cites` (P5). ADR-0004 amendment 2, item 4. The
  commit that lands them takes S7's `xfail` marker off; from then on S7
  shows 12 of 12 citing results `pass: false`, `checks.F1_4: fail`, and
  build and gate both RED. Whether ruling F admits the `checks.F1_4` half
  and the gate's reading is **Unsure** (Engineering, with Product; before
  this PR merges).
- **At PR 2:** everything else in SPEC/01 §6. None of it is in this PR.

## 5. Falsifiers, and what each would look like in the repo

SPEC/01 §4, unchanged here. In short: `checks.F1_1`, `F1_2`, `F1_3`,
`F1_4` of `fail` in an agent envelope under `evals/history/`, or a seed's
observation file under `milestones/M01/runs/` recording anything but the
expected refusal. At PR 1 none can fire: there is no agent envelope.

## 6. What M00 carried in (`milestones/M01/open.md`), item by item

Every item is answered here or moved on with a seat and a date. None is
dropped.

| # | Seat | Now |
|---|---|---|
| 1 | Product | Ruled: exempt, scoped. CLAUDE.md sentence; `tests/fixtures/README.md`. |
| 2 | Product | Ruled in ADR-0004 amendment 2, item 9: SPEC/00 §6 names the `$id` and the file. |
| 3 | Threshold Owner | Re-dated to **M05 open**. `cost_usd` stays null; a price table is `thresholds.yaml` `prices:`, keyed by pinned model id, added by the milestone that first needs USD on the envelope. |
| 4 | Engineering | Closed, no split (§2.1). |
| 5 | Engineering, Threshold Owner | Built: `thresholds.yaml` `baseline_card`, two keys; ADR-0004 amendment 2, item 1. |
| 6 | Engineering | Closed with item 4. |
| 7 | Engineering, Security | Closed on the ruleset export (item 31): `checks.F0_3`'s URL says what was observed, and `infra/ruleset/main.json` says `bypass_actors` at its date. |
| 8 | Engineering | Closed as written; real at M02 with `two-key`. |
| 9 | Engineering (Security's path) | Built: `evals.yml` exposes `gate_exit`; `record` runs only on 0 or 1. |
| 10 | Product | Ruled: a Seeded commit cell may hold several commits, each labelled. Row 0 edited in both ledger files. |
| 11 | Engineering | Ruled with item 5: one envelope per commit, one subject; ADR-0004 amendment 2, item 2. |
| 12 | Security | Signed: Security, 2026-09-19, on run 35412277571. `infra/eval-role/README.md`, `rulings/pr1.md`. "A second workflow file refused" carried: Security, **M01 PR 2**. |
| 13 | Security | Re-dated to **M01 PR 2**, with the bootstrap stack (Budgets action at `daily_usd: 10`). |
| 14 | Security | Built: `MODELS` gains `anthropic.claude-sonnet-5`. The human redeploys after this PR opens and before PR 2's first run. **Superseded at PR 2 (ruling p):** the account cannot call Sonnet 5, so `MODELS` names `anthropic.claude-sonnet-4-6` in both `infra/eval-role/` and `infra/bootstrap/`. |
| 15 | Security | Closed on the export (item 31). |
| 16 | Security | Built: `evals.yml`'s header sentence replaced, before the hashes were computed. |
| 17 | Security | Closed. The five `git ls-remote` results are in `rulings/pr1.md`. |
| 18 | Security | Re-dated to **M01 PR 2**: two `AccessDenied` probes as a step in `evals.yml`. |
| 19 | Security | Closed. 3600 stands; item 13 compensates. No step assumes the role with a token of its own; the diagnostic step requests one and prints its claims (ruling C). |
| 20 | Security | Re-dated to **M01 PR 2**: new role name in the bootstrap stack; the M00 stack is deleted after PR 2 merges (human). |
| 21 | Threshold Owner | Re-dated to **M01 PR 2**, after the first agent envelope. |
| 22 | Threshold Owner | Built: over the cap is a recorded RED; `cost_cap.tokens_per_run: 150000`, two keys. |
| 23 | Threshold Owner, Security | Ruled: the card's `region` is the request region; one sentence in SPEC/01 §7 and beside `baseline_card` in `thresholds.yaml`. |
| 24 | Data Owner | Re-dated to **M02 PR 1**: `g-012` stays through M01, `retired: null`, F0.1 recorded per run in the card's `traps_passed`. Retiring it is M02's two-key "merged properly" case. |
| 25 | Data Owner | Ruled: the replacement trap is `g-021`; `g-016` to `g-020` stay red-team at M03. Lands **M02 PR 1**. |
| 26 | Data Owner, Threshold Owner | Ruled: the frozen control cannot emit `sequel_no_inherit`; the replacement is a golden the control never passes, which P7 allows. **M02 PR 1**. |
| 27 | Product | Done in M00 PR 4 (#6, `8252763`). |
| 28 | Security | Re-dated to **M01 PR 2**: the permission boundary, in the bootstrap stack. |
| 29 | Security | Built: `validate`'s `workflow-hash`, `infra/workflows.sha256`. |
| 30 | Security, Product | Done by the human before this PR's first commit: `allowed_merge_methods: ["merge"]` on the `main` ruleset. ADR-0004 amendment 1's text unchanged; item 31's export is the evidence. |
| 31 | Security | Built: `infra/ruleset/main.json` and its README. The live-vs-export diff and `bypass_actors: []` in `validate` land at **M02 PR 1**. |
| 32 | Security | Built: the NagReport CSV from this PR's synth is committed under `infra/eval-role/`, dated in its README. cdk-nag joins `validate` at **M01 PR 2**. |
| 33 | Security | Built: the Deny statement in `app.py`, five actions with `s3:PutBucketPolicy` (ruling D); deployed with item 14. |
| 34 | Security, Threshold Owner | The figure is "unbounded at the account quota until PR 2", in the README. The Budgets action is **M01 PR 2**. |
| 35 | Security | Built: the `*` comment replaced in `app.py` and the README. |

## 7. What PR 1 does not do

- Nothing that makes claim 1 pass: no `src/bundle/`, no cosign, no
  bootstrap stack, no construct, no deploy workflow, no agent runner.
- No agent envelope. PR 1's run writes the control's envelope, in M00's
  form (ruling A); it does not measure claim 1.
- The manifest schema. `agents/refagent/manifest.yaml` carries the model
  ids only; the schema that validates it is PR 2.
