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
