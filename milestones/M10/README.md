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
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

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
   (38998599409, 38999504064, 39000157276) was refused on "log group
   already exists", and each left one more pool. PR 2's test read the
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
   goldens went through it as `platform` (GREEN, g-030 blocked), and the
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
