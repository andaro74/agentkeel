# M10 — The public caller

An eleventh milestone, opened after M09's close by a Product ruling
(ADR-0015). It takes one named item, "the public caller" (SPEC/09 §11 R6,
ruled at M09 PR 2 as M10's own claim), and reopens none of M09's rows.

## Ledger row

Written at M10 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 10 |
|---|---|
| Claim | A caller outside the platform reaches an agent only through a door the platform controls, under an identity the agent's manifest admits, with the agent's pinned guardrail on every answer and the caller named in each call's record in the security account; a caller with no identity, or one the manifest does not admit, is refused and the refusal is in the security account within N |
| Falsifiers | F10.1 a call that does not pass the door reaches the agent: from the outside caller directly on `InvokeAgentRuntime`, or from a platform principal the construct does not name. F10.2 a call through the door loses the guardrail: festival-desk's answer record through the door names a guardrail other than its pin or reads `g-030` other than 1 of 1, or refagent's plants read under 7 of 7 on the first envelope after the door's construct change. F10.3 a call's record names no caller, or a caller other than the one that called. F10.4 a caller with no identity, or one the manifest does not admit, is answered; or is refused with no record in the security account within N (`detection.max_seconds`, 600 s: the object's `LastModified` against AWS's `eventTime`). F10.5 a caller is admitted, or the field removed from a value, with one key (ADR-0016, entry 7; measured in agentkeel: an agent repository has no `two-key`, and the construct's authoriser widened is unread by it, SPEC/10 §8). |
| Seeded commit | `fba41ad`: S1 the call records (today's answer record naming no caller; a stranger answered; a bypass; a wrong subject; a late refusal; the held four); S2 festival-desk's manifest with no `callers`, and the same with it; S3 refagent's manifest gaining a caller with one key; S4 two guards, no fixture; the run file `f10_x_caller_run.yaml` with `observed: null`. One commit, before any reader |
| Expected gate output | PR 1: refagent's envelope as at M09; it says nothing about claim 10. `tests/test_m10_seeds.py` 4 passed, 6 xfailed. From PR 2's merge the gate requires `F10_1` to `F10_5`, test-only witnesses. The live reading is recorded in `caller` and read by this row's cell, not gated (SPEC/10 §4); on PR 2's own envelope it reads unread, so the row reads RED there. Named P3 exception: the door is deployed and the four calls made after PR 2 merges, read by PR 3's run (PR 4's if the deploy path needs a repair). Security probes door 1's three unknowns before PR 2 opens. **Stated at open: admitted 1 of 1, refused 3 of 3, F10.1 to F10.5 held, row 10 expected GREEN**, with SPEC/10 §7's risks named, the refusal's record first. |
| Measured | agent: traps 2/2 (g-010, g-011); ordinary 9/9; guardrail 2/3; redteam 5/5; control: traps 0/2; ordinary 0/9; guardrail 0/3; redteam 0/5; mode runtime; never_passed 1; regressed 0; plants 7/7; F0_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F0_3 pass https://github.com/andaro74/agentkeel/actions/runs/35401176820/job/105781176255; F10_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F10_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F10_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F10_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F10_5 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F1_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F1_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F1_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F1_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F2_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F2_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F3_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F3_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F3_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F3_5 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F3_6 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F4_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F4_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F4_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F5_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F6_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F6_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_0 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F7_5 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F8_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F8_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F8_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F8_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F8_5 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F9_1 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F9_2 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F9_3 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F9_4 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; F9_5 pass https://github.com/andaro74/agentkeel/actions/runs/39143365127; callers admitted 1 of 1, refused 3 of 3; F10_1 held; F10_2 held; F10_3 held; F10_4 held; GREEN; envelope `14ab792156f585c9010275e6b6be3f687cee22c6`; base b0219756 |
| PRs used / cap | 4 / 4 |
| State | GREEN |

### Open detail (PR 1, 2026-10-13)

- **Opened through `/open-milestone`.** M09 is closed (GREEN, tag `m09`
  on `833ab2b`, 2026-10-13). SPEC/00 planned no M10 and said so in
  §10.5; it was amended first (`053ee19`: §3 a threat row, §7 row 10, §8's
  count and its M10 entry, §10.3 row 10, §10.5, §15), SPEC/10 written in
  the same commit, and `product-spec-reviewer` run on it before anything
  else of PR 1 (0 BLOCK, 9 FINDING, 3 NOTE; pasted verbatim in
  `feasibility.md` §1). Every finding was taken on the session's
  recommendation and recorded in `feasibility.md` §2 with its seat;
  SPEC/10 was revised once on them, SPEC/00 four lines more (§5's Tool
  Owner row, §8 M10 item 2, the §10.3 title, the status line) and
  CLAUDE.md's seat table followed §5 (`841178f`). ADR-0015 is proposed in
  the same commit. The seeds are `fba41ad`. Every ruling file of this PR
  is a **draft** until Product and Engineering rule.
- **The claim's wording was ruled before SPEC/10 was written** (Product,
  2026-10-13, at the session's stop): the brief's proposal with four
  changes, each recorded in `rulings/pr1.md` ruling 2. The same stop ruled
  yes to the proposals for the door, the outside caller, the manifest
  field, the record's shape, N and R7's housekeeping, each still a
  proposal for its seat's ruling before PR 2 (SPEC/10 §11).
- **M10 builds one control** (ADR-0015): a door in front of an agent that
  admits a caller by an identity the agent's manifest names and refuses
  every other, with each call's record in the security account. It is not
  described as working until it has refused its seeded case. The reading
  of it (the call records, `caller` on the envelope, row 10's cell) is the
  instrument; the gate rules nothing on `caller`, so a bypass, an answered
  stranger or an unrecorded refusal stops no merge at M10.
- **What is live today, in the tree at `833ab2b`:** the runtime answers
  any IAM principal in the platform account with the grant
  (`src/agent/run.py` `invoke_deployed`; the bootstrap's two
  `InvokeAgentRuntime` statements); the answer record `build` writes names
  no caller; the manifest schema refuses a `callers` key; `two-key` passes
  a caller admitted with one key; nothing reads a call. An outsider is
  refused today by IAM's default, with no record the platform reads: the
  platform has no outside caller, admitted or refused.
- **Expected GREEN, with the risks named.** Admitted 1 of 1, refused 3 of
  3 is stated at open (SPEC/10 §7). Whether a call refused at the
  service's edge leaves a record the security account can hold within N
  is unknown and is the probe's question (c), answered before PR 2 opens;
  if neither door records it, row 10 closes RED on the record arm. The
  subject on the admitted record, the runtime's authoriser update and the
  deploy's goldens step presenting a token are the other three.
- **M09 left no `open.md` for M10.** Its close gave every finding and
  Unsure item a standing home (`milestones/M09/README.md`, close detail);
  M10 takes four of them as Product housekeeping under R7 (SPEC/06 §6 and
  the quickstart's step 0 on the platform App's "selected repositories",
  finding 3; ADR-0014's status line, finding 14; the compliance map's M09
  row and its stale claim-8 line, finding 11) and nothing else. M09's
  video was ruled not recorded, so this PR carries no recording; M10's is
  ruled not recorded here too (SPEC/00 §10.5 as amended; ADR-0015
  decision 6).
- **The fixture is fictional.** festival-desk is M09's agent; the subjects
  `lantern-desk`, `box-office` and `stranger` are made-up staff of a
  made-up festival; the pool ids, the role and the account in the
  records are made up. No real person, title, contract or studio
  workflow detail (SPEC/00 §9).

### Measure detail (PR 2, 2026-10-15)

- **PR 2 of 4, the measure.** Every reader SPEC/10 §6 names landed, each
  in the commit that took its seed's marker off: the raw record fixture
  from the probe first and alone (`3a929b6`); the schema's `callers` and
  the two manifests' `callers: []` (`7ba474f`; S2's schema case read);
  `src/validate/callers.py` from `evaluate()` (`a9ffab3`; S2's missing-key
  case read); `two-key` entry 7 under ADR-0016 (`7100808`; S3's two cases
  read, its two guards still passing); `src/verdict/caller.py`, `caller`
  on the envelope, `CLAIM_10_CHECKS` wired and row 10's reading
  (`5e2cf70`; S1 read), named as `M10_READERS` in the commit after it
  (`2898100`); the observer and its two `evals.yml` steps (`7a0ff78`);
  the door in the construct, the bootstrap's grants, the doored fixture
  and S4's first guard rewritten (`1734656`); the deploy's door step and
  `run.py`'s door path (`1c5b71f`); the call records' delivery in the
  security account (`e9d915d`). The run file's marker stays on:
  `observed` is null until the owner makes the run.
- **The plant goes RED here.** On PR 2's own envelope `caller` is unread:
  no door is deployed and no call has been made, so row 10's reading is
  RED ("caller not read: the envelope records no call", or, once
  `evals.yml` runs the observer, "the run has not been made", every
  falsifier unread) whatever refagent's own verdict. `F10_1` to `F10_5`
  are test-only witnesses on every envelope from the merge; the gate rules
  nothing on `caller`.
- **The rulings decided before PR 2 opened** (2026-10-15, after the
  probe, each as the brief put them, with one correction from the probe's
  files): R2 door 2 in the hybrid form; R3 as proposed with the bypass arm
  an assumed role; R4, R5, R6 and ADR-0016 as proposed. Written as this
  PR's five ruling files, each a draft until it reads "Ruled by". The
  correction: the brief read the probe's (b) as NO; the data event of an
  admitted call does carry the token's `sub` and `iss`, so (b) is PARTLY
  (`runs/door_probe.md`). The decision R2 reaches is the same.
- **The four seat reads before the PR opened** (each verbatim in its
  ruling file and the PR body): `engineering-cold-reviewer` 0 BLOCK, 2
  FINDING, 6 NOTE; `security-reviewer` 0 BLOCK, 7 FINDING, 10 NOTE;
  `tool-owner` 0 BLOCK, 3 FINDING, 14 NOTE; `data-owner` 0 BLOCK, 3
  FINDING, 9 NOTE. Every finding in a path of this PR's was repaired in one
  commit after the reads (`1a3e336`), the measurement being of the tree
  that ships: a record the observer refused to copy reads as no record; the
  caller's address, user agent, key id, principal id, session context and
  TLS details are dropped before any record reaches an envelope, each drop
  named; the credential match reads a key by its words and a value by its
  shape; a line with no authoriser context that is not the API's own 401
  reads as the door failing; a line naming another agent under this
  agent's prefix is not copied; the authoriser clips what it writes and
  survives a malformed payload; the pool's execution-role grants are held
  to the agent tag; the dead stream suppression is gone; the subscriber
  role's trust is this account's. What stands is in `rulings/pr2.md`'s
  Unsure table, A to Q.
- **What this PR does not do.** No live call; no festival-desk pull
  request; no pool user's credential; no golden under `evals/goldens/`,
  no bar, nothing under `src/baseline/`, no rule file; refagent stays
  outside the door; no recording; no fifth pull request.

### By-hand steps before PR 3's run, each with what it must precede

1. **Security deploys the security stack** (`infra/security/`, by hand,
   in the security account): the Logs destination the doors subscribe to,
   the Firehose that writes under `calls/agents/<name>/`, the bucket's
   `calls/` statements, the read role's `calls/` prefix. Before
   festival-desk's deploy: the construct's subscription names the
   destination's ARN, and a deploy whose subscription has no destination
   fails on it, which is a PR 3 repair, not a finding of the claim.
2. **Security deploys the bootstrap stack** (`infra/bootstrap/`, by
   hand): the execution role's door grants, the deploy role's read of a
   door client's secret, the agent ceiling's one new action. Before
   festival-desk's deploy, for the same reason. The first deploy, from
   PR 2's merge on 2026-10-16, was refused and rolled back (Repair
   detail, below); the second is from PR 3's branch.
3. **The owner opens festival-desk's `callers` pull request** (one
   subject, `lantern-desk`, `issuer: self`), states it in the run file
   first, and merges it once the platform check admits it; the scheduled
   deploy puts the door on and asks the three goldens through it as
   `platform`.
4. **The owner sets lantern-desk's first credential** by hand
   (`admin-set-user-password`, permanent), outside the repository.
5. **The owner makes the four calls** in the run file's order, each
   stated first: admitted (lantern-desk's token at the door), none (no
   token at the door), stranger (a throwaway pool's user's token at the
   door; the pool made and deleted outside the repository), bypass (an
   assumed role holding the grant, straight at the runtime; its request
   id and the role's ARN under `observed.bypass`). The owner fills
   `observed` and nothing else.
6. PR 3's run reads the records; if the platform's own deploy path needs
   a repair first, PR 3 is that repair and PR 4's run reads them (SPEC/10
   §5.1).

### Repair detail (PR 3, 2026-10-16)

The platform's own deploy path needed a repair before any call could be
made, so PR 3 is that repair and PR 4's run reads the records (step 6
above; SPEC/10 §5.1).

1. **The bootstrap deploy was refused on an IAM quota.** From PR 2's
   merge (`917601d`), `cdk deploy` of `AgentkeelBootstrap` on 2026-10-16
   failed on `DoorGrants` with "Maximum policy size of 10240 bytes
   exceeded for role agentkeel-cfn-exec" and rolled back
   (`UPDATE_ROLLBACK_COMPLETE`); nothing of PR 2's bootstrap diff
   landed, and the platform account stands as at M09. IAM holds a
   role's inline policies to 10,240 characters in all; the execution
   role's default policy is 9,134 and PR 2 made the door's grants a
   second inline policy of 2,937 (12,071). PR 2's Unsure I named the
   wrong ceiling: not the size CloudFormation takes for one document,
   but IAM's for all of a role's inline documents. Neither cdk-nag nor
   any test here measured it.
2. **The repair**: `DoorGrants` is a customer managed policy attached to
   the execution role (`agentkeel-cfn-exec-door`, its own ceiling 6,144,
   counted against the role's ten attached policies and not its inline
   total); its six statements are PR 2's, unchanged, under the same
   cdk-nag path and reasons. `tests/test_bootstrap.py` now holds IAM's
   three quotas on every role the stack makes, measured as IAM counts
   (whitespace out) on the template's longer form; on PR 2's bootstrap
   it fails with 12,071. `tests/test_m10_platform.py` reads the
   execution role's grants from both policy kinds and holds that
   nothing of the door is inline.
3. **Standing**: the default policy has 1,106 characters of room before
   CDK splits it into a second inline document, which the role cannot
   hold either; the quota test is what says so before a deploy does.
4. **The security stack** was deployed on 2026-10-16 by Security from
   CloudShell in the security account, as a plain template synthesised
   from this branch (the stack has no assets; the `agentkeel-security`
   profile has had no role to assume since M05). The change set's Modify
   rows on every role, the OIDC provider and the bucket were CDK path
   metadata only; the property changes were PR 2's four. The destination
   `agentkeel-calls` stands.
5. **festival-desk's first door deploy was refused**, after its
   `callers` pull request (#4) merged on 2026-10-17. Run 38997315544:
   `logs:DescribeLogGroups` takes no resource-level permission, so PR 2's
   grant on two log-group patterns never applied and the stage could not
   read its log group's ARN; and `logs:PutSubscriptionFilter` is
   authorised against the security account's destination as well as the
   log group, which PR 2 did not grant. The rollback kept what it had
   made as Retain: the three log groups and the pool. Every later run
   (38998599409, 38999504064, 39000157276, and every scheduled run until
   the next repair) was refused on "log group already exists", and each
   left one more pool: 55 in all, deleted by hand on 2026-10-18. PR 2's test read the
   action names the handlers call and not the resources they are
   granted on.
6. **The repair**: `DescribeLogGroups` on `*`, `PutSubscriptionFilter`
   on the one destination's ARN, both in `DoorGrants`; the pool and its
   users `RetainExceptOnCreate`, so a failed first deploy deletes the
   pool it made. The log groups stay `Retain`: the deploy boundary denies
   the delete a rollback would need, so a failed first door deploy's log
   groups are deleted by hand. The bootstrap is redeployed from this
   branch; the orphan pools and log groups are deleted by hand.
7. **The second door deploy was refused at the stage** (run 39052047504,
   2026-10-17T17:05Z, after the bootstrap redeploy and the log groups
   deleted): the subscription and the log-group lookup passed; an HTTP
   API stage with access logging needs CloudWatch Logs' vended log
   delivery from its creator (`logs:CreateLogDelivery` and five more,
   on `*`, as API Gateway's guide lists them). Granted in `DoorGrants`.
   The guide's eighth, `logs:DeleteLogDelivery`, is denied by the
   deploy boundary's flat `logs:Delete*` and is not granted: a stage's
   delete or a change of its log destination may be refused.
8. **The door stood, and its records did not arrive** (deploy run
   39076739413, 2026-10-17T22:51Z): the stack built the door, the
   run's goldens step reports asking through it as `platform` (its log,
   not an envelope: F10.2 is read by PR 4's run), and the
   access log holds three lines naming `platform`. None reached
   `calls/agents/festival-desk/`: the subscription counted one delivery
   error. CloudWatch Logs hands a subscribed event to the destination's
   role on the sender's behalf, and PR 2's role trusted Logs on the
   security account's behalf only, which is the destination's own test
   message (the one object under `calls/errors/`). The trust now names
   both accounts; the security stack is redeployed from CloudShell.
9. **The reader read the access log's epoch as milliseconds**: an HTTP
   API writes `$context.requestTimeEpoch` in seconds (`1792277674` on
   the live lines), so every call dated to 1970. Either unit is read by
   its size now, with a test on the live line's shape (PR 2's Unsure G).

### Read before PR 2, each with the pull request whose merge it must precede

SPEC/10 §11, and the **Unsure** list in PR 1's body. A step is attempted
only when the readings it needs have been ruled; a by-hand deploy waits
for a ruling file that reads "Ruled by" (M09 finding 4).

**Before PR 2 opens** (rulings and one probe, not grants):
1. R2 (Security): the door. Proposed door 1, the runtime's own JWT
   authoriser on a Cognito user pool per agent in the agent's stack; the
   three unknowns (SigV4 refused in JWT mode; the subject readable where
   the record is written; a refusal at the edge recorded within N) probed
   with throwaway names outside the repository, the outputs committed in
   PR 2 as `runs/door_probe.md`. If (c) is no, door 2 (API Gateway with a
   Lambda authoriser); if (a) is no, the bootstrap's grants narrowed by a
   runtime tag, failing which door 2.
2. R3 (Security, Product): the outside caller. Proposed: a user in the
   agent's pool for the admitted arm; a user of a throwaway pool for the
   stranger; no token; the laptop's IAM principal for the bypass arm only,
   never presented as outside.
3. R4 (Tool Owner): `callers`, a list of `{subject, issuer}`; not an edge,
   not a rule; `[]` the default; `subject` a name, never `platform`;
   `issuer` the symbol `self` at M10; optional in the schema, required by
   `callers_errors`; no semver bump; refagent's and `ratings-helper`'s gain
   `callers: []` at PR 2 under a Tool Owner ruling file (`tool-owner`
   findings 1, 2, 3, 6).
4. R5 (Data Owner): the read record's shape (`subject`, `issuer`, `agent`,
   `outcome`, `reason`, `request_id`, `time`, `delivered`), mapped by
   `build` from the raw record AWS delivered; no guardrail on a call
   record; the raw record carries no credential.
5. R6 (Threshold Owner): N is `detection.max_seconds`, 600 s, reused and
   read as M05 read it.
6. ADR-0016 (Product; keyed at PR 2 by the Tool Owner and any second
   seat): entry 7 of the closed list, a caller admitted or the field
   removed from a value; absent to `[]` not one; a new ADR, since
   ADR-0009's last amendment is the Rule Owner's (`tool-owner` note 4).
   Written at PR 2 after S3 is planted here.

**After PR 2 merges, before PR 3's run** (the owner, each stated in
`runs/f10_x_caller_run.yaml` first):
7. festival-desk's `callers` pull request, one subject; the platform
   check must admit it; it merges; the scheduled deploy puts the door on
   and asks the goldens through it as `platform`.
8. The admitted user's first credential, set by hand outside the
   repository.
9. The four calls in the run file's order: admitted, none, stranger,
   bypass. The owner fills `observed` with the pull request number, the
   deploy run id, the answer record's key and each call's request id, and
   nothing else.
10. If the platform's own deploy path needs a repair, PR 3 is that repair
    and the run is read by PR 4's run (M08's second exception).

### Close detail (PR 4, 2026-10-18)

Opened and closed through `/open-milestone` and `/close-milestone`. **Row
10 closes GREEN**, as stated at open (SPEC/10 §7): callers admitted 1 of 1,
refused 3 of 3, F10.1 to F10.4 held on the live run, F10.5 held on every
envelope since PR 2's merge. The Measured cell is copied from `make
ledger`'s "as row M10 reads it" line for the envelope for
`14ab792156f585c9010275e6b6be3f687cee22c6`, written by CI run 39143365127
on this PR's branch (the owner's `observed` block and the run test's
marker, `14ab792`) and committed by `github-actions[bot]` (`4de0fab`).
`make ledger` exits 0 against it. Nothing in this PR touches a golden, a
bar, `src/baseline/`, a reader, a workflow, a grant, the run file after
`14ab792`, or `agentkeel-studio/festival-desk`. One infra file changes:
the calls destination's policy is PR 2's again (`e05095c`, `0ebfdbd`;
finding 7).

**The measurement.** The owner made the four calls on 2026-10-18 between
03:32 and 03:34 UTC and wrote their keys, and nothing else, in
`runs/f10_x_caller_run.yaml` (`14ab792`). `scripts/observe_caller.py` read
the access-log objects under `calls/agents/festival-desk/` and the bypass's
data event in the platform trail's objects from the audit bucket in the
security account (as `agentkeel-audit-read`), the answer record of deploy
run 39076739413 by its key, and festival-desk's pull request `#4` with its
manifest at the merge commit from GitHub (as the eval role), at 16:13:11Z;
`build` ruled on them into `caller`.

| Falsifier | Read | Held | What the envelope says |
|---|---|---|---|
| F10.1 | yes | yes | the bypass, `arn:aws:sts::581208540944:assumed-role/m10-bypass/m10-bypass` on `InvokeAgentRuntime` straight at the runtime: `errorCode AccessDenied` ("Authorization method mismatch"), read `refused`, `not the door`; request id `2d07b741…`; no call that did not pass the door was answered |
| F10.2 | yes | yes | the deploy's answer record through the door names `at8e36cosq1r:1`, festival-desk's pin, and `g-030` `blocked: true`: **1 of 1**; refagent `plants 7/7` on this envelope and every one since the construct changed |
| F10.3 | yes | yes | the admitted record names `lantern-desk`, the stated caller and the manifest's one entry; the no-token record names no one; the stranger's names `stranger` with its issuer `us-west-2_rXaZjWjO5`, another pool; the bypass names the role. None names no caller or the wrong one |
| F10.4 | yes | yes | no identity: `401`, record delivered 78 s after the call; the stranger: `403`, `not admitted`, 107 s; the bypass: 235 s; the admitted call's record 96 s. Each under `detection.max_seconds` 600. The manifest at `#4`'s merge admits `lantern-desk` alone |
| F10.5 | the gate | yes | `F10_5 pass` on every envelope since `917601d`; no caller admitted in agentkeel with one key (ADR-0016 entry 7). The agent-repository half is unread, as SPEC/10 §8 says (finding 19) |

Beside the four, the platform's own test call of 03:13:30Z (`platform`,
`200`, delivered in 92 s) is in the bucket and on the envelope with
`step: null`; `calls` counts it for nothing (finding 18). The risk SPEC/10
§7 named first, whether the door's front records a refused stranger with
her name and a no-token call with its request id, did not happen: both
lines are there (pr2.md Unsure A, answered yes). The bypass's record
arrived in 235 s against the fifteen minutes AWS allows itself (pr2.md Q).

**What each step showed, in order** (times UTC; the deploy-path repairs
are PR 3's "Repair detail" above).

1. **The security stack** (Security, by hand, CloudShell, 2026-10-16):
   PR 2's delivery, the destination `agentkeel-calls`.
2. **The bootstrap** (Security, by hand): refused from PR 2's merge on
   IAM's inline ceiling (finding 1); deployed from `m10-pr3` 2026-10-16
   04:26 with the door grants as a managed policy; redeployed 2026-10-17
   16:58 and once more after the log-delivery grant (findings 2, 4). Each
   on a draft of `pr3-security.md` (finding 8).
3. **festival-desk's `callers` pull request** (`#4`, one subject,
   `lantern-desk`, `issuer: self`): admitted by the platform check, merged
   2026-10-17 02:47. The first door deploy (run 38997315544) was refused
   on two grants, and every scheduled run until the repair was refused on
   the log groups it left, each leaving a pool: 55, deleted by hand
   (finding 3). Run 39052047504 (17:05) was refused at the stage on the
   vended log delivery. Run 39076739413 (22:51) deployed the door:
   `UPDATE_COMPLETE`, the pool `us-west-2_f8kyzKF0P`, the two clients,
   the API `ohw3eeegoa`, the three goldens asked through the door as
   `platform`, `g-030` blocked, the answer record put at
   `envelopes/agents/festival-desk/747c836b….json`. Its three access-log
   lines did not arrive (finding 5).
4. **The security stack again** (2026-10-18, CloudShell): the subscriber
   role's trust names both accounts. The platform test call at 03:13:30
   arrived at 03:15:02.
5. **The credential**, set by hand outside the repository.
6. **The four calls**: admitted 03:32:31 (`Fa6YgjvJvHcEJQw=`, `200`), none
   03:32:49 (`Fa6bTjdkvHcEJ_Q=`, `401`), stranger 03:33:16
   (`Fa6fghRCPHcEJxw=`, `403`, a token from the owner's throwaway pool),
   bypass 03:33:47 (`2d07b741…`, `AccessDenied`, as `m10-bypass`). Their
   records: 03:34:07 (two lines in one object), 03:35:03, 03:37:42.
7. **PR 3 merged** (`#56`, `f05405f`, 05:37:56 by GitHub's record; the
   merge commit's own stamp reads 05:37:55), its three rulings ruled
   2026-10-17.
8. **The narrowing refused** (Security, by hand, CloudShell, 2026-10-18):
   PR 3's destination principal (the execution role's ARN) refused by
   CloudWatch Logs, rolled back; the account id with an `aws:PrincipalArn`
   condition refused, rolled back (finding 7). The tree now says what is
   deployed; no deploy in PR 4.
9. **The observed block** (`14ab792`, 16:04): the pull request number, the
   deploy run id and the answer record's key, the four request ids, the
   bypass principal, nothing else. The envelope followed at 16:14:52.

**Shortcomings, named.** The platform's own deploy path was refused three
times (in four places) and failed silently once before the door stood with
its records arriving, the first door deploy's failure repeating on the
ten-minute timer until its repair landed, so the run moved from PR 3 to PR 4 (SPEC/10 §5.1's second
exception, stated at open). 55 identity pools were left by the failed
first deploys and deleted by hand. Seven account changes were made before
the ruling file that carries them was ruled (five in PR 3, two refused
attempts in PR 4). The narrowing of the calls destination that Security
asked for after PR 3's review cannot be deployed, and would not have closed
the path it was for: any principal in the platform's shared account that
can subscribe a log group can file a line under an agent's name. None of
these is a falsifier of claim 10; each is a finding below.

**SPEC/00 §15, re-read over rows 0 to 10** (as amended at M10 PR 1, the
same way M09's close read it). "At least seven are GREEN": rows 0, 2, 3, 9
and 10 are GREEN, five of eleven; not met, as stated unreachable.
`docs-current`: not built; its four conditions read by hand at this close
by `docs-writer` (report in the PR body). Acts 1 to 6: one act, unchanged
since M08. Eleven explainers: met. Videos: nine of eleven, M09's and
M10's ruled not recorded (ADR-0005 amendment 2; ADR-0015 decision 6), not
moved to fit. `git tag m10`: after this PR merges. `docs/story.md`: does
not exist (finding 24). Every RED row carries a ruling file; every PR
since M00 PR 1 has one; the ledger page is generated. The compliance page
gains claim 10's row at this close (finding 24 names rows 7 and 8, still
not drafted).

**Findings, each with a standing home.** SPEC/00 plans no M11 (ADR-0015),
so there is no `open.md` to carry an item to; each stands here, as M08's
and M09's did.

| # | Finding | Home / seat |
|---|---|---|
| 1 | The bootstrap deploy was refused on IAM's ceiling for a role's inline policies in all (12,071 of 10,240); PR 2's Unsure I named the wrong ceiling; no test measured it. | `rulings/pr3-security.md`, `rulings/pr3-engineering.md`: the door grants a managed policy; `tests/test_bootstrap.py` holds IAM's three quotas. Repaired; closed. The test's measure is the template's (pr3 I, Engineering, standing) |
| 2 | The first door deploy was refused: `logs:DescribeLogGroups` takes no resource and `logs:PutSubscriptionFilter` is authorised against the destination too; PR 2's test read action names, not resources. | `rulings/pr3-security.md` rows 2, 3. Repaired; closed |
| 3 | 55 orphan identity pools, one per refused scheduled deploy between 2026-10-17 02:47 and the repair, deleted by hand; `RetainExceptOnCreate` has not fired on a failed first deploy since. | `rulings/pr4-security.md` (pr3 D). Security; Engineering. Standing, not described as working |
| 4 | An HTTP API stage with access logging needs CloudWatch Logs' vended delivery from its creator: six actions on `*`, account-wide and uncapped by the deploy boundary; `logs:DeleteLogDelivery` is not granted, so a stage's delete or a doored agent's retirement may be refused. | `rulings/pr3-security.md` (accepted by name), `rulings/pr4-security.md` (pr3 B, C). Security. Standing; read at the first retirement of a doored agent |
| 5 | The door's records did not arrive: the subscriber role trusted Logs on the security account's behalf only, and Logs assumes it on the sender's. One delivery error, one object under `calls/errors/`. | `rulings/pr3-security.md` row 5. Repaired; closed |
| 6 | The reader read the access log's epoch as milliseconds; an HTTP API writes seconds, so every live call dated to 1970 on the first read. Either unit is read by its size now; the field keeps its name. | `rulings/pr3-engineering.md`, `rulings/pr4-engineering.md` (pr3 H). Repaired; the name standing |
| 7 | **Security F3 stands.** The calls destination's policy cannot name the execution role: CloudWatch Logs takes an account id, or an organisation condition, and nothing narrower (two refused deploys, 2026-10-18); and the narrowing would have been partial, since the role's own grant reaches the door Lambdas' log groups. Any principal in the shared platform account holding `logs:PutSubscriptionFilter` can file a line under an agent's prefix; no seeded case shows one refused. The tree is PR 2's policy again, equal to what is deployed. | `rulings/pr4-security.md`: accepted by name with four routes (a dedicated account; partition by source log group; an SCP; a detective read of the subscription filters). Security; the Data Owner on the record's shape if route 2 is taken. **Standing** |
| 8 | Account changes before their ruling file was ruled: the bootstrap three times and the security stack twice in PR 3; the security stack twice more in PR 4, each refused and rolled back. M09 finding 4 again. | `rulings/pr3-security.md` (top), `rulings/pr4-security.md`. Security: no by-hand deploy before the file reads "Ruled by". Standing lesson, recorded three milestones running |
| 9 | PR 3 wrote no "What `make validate` checked" header row in the ledger; the `m10` row covers PR 3 and PR 4. | `milestones/README.md`, this close. Product. Closed |
| 10 | `logs:PutResourcePolicy` takes an optional log-group `resourceArn` (read at the close in the API reference; pr3 J); the DoorGrants reason's "none of which takes a resource" is not exact, though API Gateway's delivery writes the account-level policy the grant on `*` is for. | `rulings/pr4-security.md`. Security: the sentence at the next bootstrap PR. Standing |
| 11 | A subject removed from `callers` keeps its user and credential in the pool; re-admitting it is refused until the user is deleted by hand. | `rulings/pr4-security.md` (pr3 E). Tool Owner; Security. Standing |
| 12 | The door's subscription filter can be repointed by a template or deleted by an account admin from the platform account; the records then stop and row 10 reads the run unread, not held; nothing reads that the filter is present. | `rulings/pr4-security.md`, accepted by name (security-reviewer N6); route 4 is the read. Security. Standing |
| 13 | Neither destination test asserts the destination's `RoleArn` or `TargetArn`. | `rulings/pr4-engineering.md`. Engineering, the next PR that touches the file. Standing |
| 14 | An assumed-role ARN's session name is free text and reaches the envelope by design on the bypass record; tonight's names nobody, and no file says it must not. | `rulings/pr4-data-owner.md` (data-owner F1). Product, with Security: a sentence in SPEC/10 §2. Standing |
| 15 | Two raw shapes were not produced by the run and are unmeasured by `redact`: an admitted SigV4 data event with request parameters, and a token call straight at the runtime with its claims. | `rulings/pr4-data-owner.md`. Product: a line in SPEC/10 §8. Standing |
| 16 | ADR-0015 and ADR-0016 read `Proposed` after their ruling files read "Ruled by" (2026-10-13, 2026-10-15): M09 finding 14 again. | Both lines read `Accepted` at this close, the correction named on each. Product. Closed |
| 17 | `tests/fixtures/README.md`'s run rows for M09 and M10 still read `observed: null`; not changed here because `tests/` is a measured path and a prose change would write a second envelope (M09 finding 20). | `rulings/pr4-engineering.md`. Engineering, the next Engineering PR. Standing |
| 18 | The platform's own test call (03:13:30Z) and the deploy's three goldens through the door leave records under the agent's prefix with subject `platform`; the observer steps none of them and `calls` counts them for nothing. The first is on the envelope with `step: null`. | This close; SPEC/10 §2 (`platform` never a subject). Recorded; nothing to act |
| 19 | F10.5's agent-repository half is unread: festival-desk's `callers` admission (`#4`) took one commit, since an agent repository has no `two-key` (pr1 K; SPEC/10 §8). | The ledger row, the explainer. Product. Standing, named not measured |
| 20 | A call with no token made straight at the runtime's edge leaves no record anywhere (SPEC/10 §8, from the probe's (c)); the run's `none` step went to the door. | SPEC/10 §8. Product; Security. Standing |
| 21 | `_step_of`'s fallbacks pair a record to a step by its subject when no request id matches; untested on a line with an unmatched request id (data-owner D). All five live records carried the observer's step. | `rulings/pr4-engineering.md`. Engineering, a test at the next PR. Standing |
| 22 | The stranger's throwaway pool (`us-west-2_rXaZjWjO5`) and the bypass role (`m10-bypass`) were made outside the repository and no observer reads their deletion (pr1 L). | `rulings/pr4.md` Unsure 3: the owner's word, written there if given. Security; Product |
| 23 | The run moved from PR 3 to PR 4 (SPEC/10 §5.1's second exception, stated at open), the third milestone running to use it. | The ledger row, `rulings/pr3.md`, `rulings/pr4.md` ruling 2. Closed |
| 24 | M09's standing items untouched by M10: `docs/story.md` absent (SPEC/00 §15); the ledger's M08 PR 2 to PR 4 header rows; the videos' ceilings (M01, M02, M08); the compliance map's rows for claims 7 and 8 not drafted. | Where M09's close put them. Product. Standing |
| 25 | The explainer tells the door's records from a forgery by the request ids the owner wrote in the run file; whether that sentence is enough, or should read "provenance unproven", is wording. | `rulings/pr4.md` Unsure 6. Product |
| 26 | The synthesised security template equals the deployed one by the owner's read in CloudShell; the diff is not in the tree. | `rulings/pr4.md` Unsure 2, `rulings/pr4-security.md`. Security. Recorded |

**Unsure items, every PR body of this milestone, each ruled or with a
named seat.**

| # | From | Item | Ruled |
|---|---|---|---|
| A | `#54` | The door (R2) | Ruled at PR 2 on the probe (`runs/door_probe.md`): door 2 in the hybrid form; `rulings/pr2-security.md`. Deployed at run 39076739413; the four calls read through it |
| B | `#54` | Who the outside caller is (R3) | Ruled at PR 2: a pool user, a throwaway pool's user, no token, an assumed role for the bypass; the run was made so (`rulings/pr2.md`) |
| C | `#54` | The manifest field (R4) | `rulings/pr2-tool-owner.md`; festival-desk's `#4` admitted on it |
| D | `#54` | The read record's shape (R5) | `rulings/pr2-data-owner.md`; re-read on the first live records at this close, `rulings/pr4-data-owner.md`: the drop list whole on five records |
| E | `#54` | N (R6) | Threshold Owner before PR 2: 600 s reused, not moved; the slowest record, the bypass, 235 s |
| F | `#54` | ADR-0016 | Written at PR 2, keyed by two seats; `Accepted` at this close (finding 16) |
| G | `#54` | Where the raw record comes from | The probe's (b): the access log for the door's calls, the trail's data event for the bypass; `calls/agents/<name>/` and the trail's prefix (`rulings/pr2-security.md`) |
| H | `#54` | The runtime's authoriser update in place or replaced | The probe's (d): in place; the registry row at run 39076739413 says so (`rulings/pr2.md`) |
| I | `#54` | The `platform` client's credential | pr2.md E: the deploy mints the token itself; stored nowhere |
| J | `#54` | Cut 3's wording at the close | Cut 3 not taken (pr2.md H); the explainer reads "who asked", the record names the subject |
| K | `#54` | F10.5's agent-repository half unread | Finding 19; standing, Product |
| L | `#54` | The throwaway pool outside the repository | Finding 22; `rulings/pr4.md` Unsure 3 |
| A | `#55` | Whether the access log records the refused stranger with her name and the no-token 401 with its id | **Answered yes by the run**: both lines are on the envelope (the measurement table) |
| B | `#55` | Whether the delivery lands under `calls/agents/<name>/` within N | Answered after PR 3's trust repair (finding 5): 78 to 235 s |
| C, O | `#55` | The door's functions outside the platform VPC | `rulings/pr4-security.md`: standing, accepted by name |
| D, E, H, J, K, L, P | `#55` | Recorded at PR 2 | Stand as recorded |
| F | `#55` | `make plants` reads file presence | Closed by the marker (`rulings/pr4-engineering.md`) |
| G | `#55` | The hand-written fixture against the live line | The epoch's unit (finding 6), repaired at PR 3 as G said |
| I | `#55` | The execution role's door policy | Superseded by PR 3's managed policy (finding 1) |
| M | `#55` | `DROPPED_KEYS` on the first live record | `rulings/pr4-data-owner.md`, `rulings/pr4-security.md`: whole on these five records; finding 14 and 15 name what the run did not produce |
| N | `#55` | Cognito and the agent tag | Answered by the deploy: no refusal at Cognito |
| Q | `#55` | The bypass arm rests on CloudTrail's delivery | 235 s on this run; the risk stands as named; not a reason to move N. Threshold Owner; Product |
| A–D | `#55` (Security's own) | The access log's two lines; the delivery; Cognito's tag; the quote-and-newline probe | A, B, C answered as above; D not made, standing (`rulings/pr4-security.md`) |
| two | `#55` (Engineering's own) | The observer's three imports; the M02 seed test on a dirty checkout | Standing as at PR 2 |
| three | `#54` (Engineering's own) | `STATED`'s derivation; the S4 synth guard's sharing; the `noqa` import | The derivation held (data-owner D); the guard as PR 2 left it; the import stays. Engineering |
| A | `#56` | PR 2's A, read by PR 4's run | Answered yes |
| B, C, D, E | `#56` | The account-wide grants; `DeleteLogDelivery`; `RetainExceptOnCreate`; the retained user | Findings 4, 3, 11; `rulings/pr4-security.md`. Standing |
| F | `#56` | The destination admits the execution role alone | **Not held, standing**: finding 7 |
| G | `#56` | The by-hand deploys before their ruling | Finding 8; this PR's two recorded in `rulings/pr4-security.md` |
| H, I | `#56` | The epoch field's name; the quota test's measure | Findings 6, 1; Engineering, standing |
| J | `#56` | `PutResourcePolicy`'s resource type | Read at the close: finding 10 |
| 1–7 | `#57` | `rulings/pr4.md` Unsure | Each with its seat there: the video row; the template's equality; the pool's and role's deletion; a second envelope; the map's framework lines; the forgery sentence; F10.5's half |

**The by-hand steps of the close** (the owner): rule the four `pr4*.md`
files and sign the five lines of `attestations.md` on this branch, each
pushed; merge with a merge commit; `git tag m10` on the merge commit and
push the tag. No recording is made (ADR-0015 decision 6). Delete nothing
in AWS: festival-desk's door, pool, log groups and subscription, the
security account's destination and stream, and the failed deploy runs'
artifacts stand as the envelope read them (`rulings/pr4-security.md`).
The bypass role and the throwaway pool are the owner's to confirm
(finding 22).

### What a reader can run, at the close

```
make ledger            # row 10 GREEN, 4 / 4; the cell equals "as row M10 reads it" for 14ab792; exit 0
make validate          # twenty-one checks, ok
uv run pytest tests/test_m10_seeds.py -q   # 10 passed: the run test has no marker
git log --format='%h %an %s' e05095c^..4de0fab   # the destination policy (andaro74, two commits), the observed block and the marker (andaro74), the envelope (github-actions[bot])
git diff f05405f...HEAD --stat -- evals/goldens thresholds.yaml src/baseline rules data agents src scripts .github infra/bootstrap infra/construct   # empty: the close changes no reader, rule, bar, golden, workflow or grant
git diff f05405f...HEAD --stat -- infra/security tests   # the destination policy, its test, the run test's marker
python -c "import json; c=json.load(open('evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json'))['caller']; print(c['admitted'], c['refused'], c['F10_2']['pin'], c['F10_2']['blocked']); [print(r['step'], r['read']['subject'], r['read']['outcome'], r['read']['reason'], r['read']['time'], r['read']['delivered']) for r in c['records']]"
git show 917601d:infra/security/app.py | grep -n ThePlatformAccountsDoorsSubscribe   # PR 2's policy, the one deployed and the one on this branch
gh pr view 4 -R agentkeel-studio/festival-desk --json state,mergedAt   # MERGED, 2026-10-17
gh run view 39076739413 --json conclusion -q .conclusion   # success: the deploy that put the door on and asked the three goldens through it
```

A Measured cell that differs from the envelope, a reader or a golden
changed in this PR, a run file changed after `14ab792`, a deploy made in
PR 4, or a fifth pull request, makes this close wrong.

### What a reader can run

```
git log 833ab2b..HEAD --format=%h     # PR 1's commits: 053ee19, 841178f, fba41ad, then the documents and the rulings
uv run pytest tests/test_m10_seeds.py -q              # 4 passed, 6 xfailed
uv run pytest tests/test_m10_seeds.py -q --runxfail   # 4 passed, 6 failed, each with its planted message
make plants     # S1 to S4 and the run; S1, S2 and the run "not in the tree yet"
make validate   # twenty-one checks, ok
make ledger     # exits 0; row 10 OPEN, Measured empty
git show fba41ad --stat   # the seeds, the tests, the README rows, SEEDS_M10, the run file; no reader
git diff 833ab2b...HEAD --stat -- evals/goldens thresholds.yaml src/baseline rules agents infra .github scripts src/verdict/caller.py src/validate/callers.py   # empty
```

Any reader of a call record, a `callers` field or a two-key entry for it
in this PR, a door, a workflow or `infra/` change, a golden, a bar, or a
change to festival-desk from an agentkeel session, makes the plant wrong.

### What a reader can run, at PR 2

```
git log a67de63..HEAD --format=%h     # PR 2's commits: the raw fixture first, then one reader per commit
uv run pytest tests/test_m10_seeds.py -q              # 9 passed, 1 xfailed (the run, not made)
uv run pytest tests/test_m10_seeds.py -q --runxfail   # 9 passed, 1 failed: "seed run: the run has not been made"
uv run pytest tests/test_m10_readers.py tests/test_m10_platform.py tests/test_p5_disagree.py -q
make plants     # S1 to S4 and the run; every reader "in the tree" (the run's marker stays on)
make validate   # twenty-one checks, ok
make ledger     # exits 0; "as row M10 reads it" ends "caller not read: the envelope records no call; RED"
git diff a67de63...HEAD --stat -- evals/goldens thresholds.yaml src/baseline rules data/ tests/fixtures/m09   # empty
PYTHONPATH=. CDK_OUTDIR=/tmp/door AGENTKEEL_BUNDLE=tests/fixtures/m10/s4-festival-desk-door uv run python infra/construct/app.py   # the doored stack, cdk-nag clean
```
