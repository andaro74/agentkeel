# M08 feasibility

Written at M08 PR 1, the plant (`/open-milestone M08`). M08 is the last
milestone; after its close, building stops. SPEC/08 was drafted first
(`142cd53`) and `product-spec-reviewer` run on it before anything else of
PR 1 was written, but for M07's two recordings (`de2417f`, `open.md` row
1), the security account's hash check (`ac16d0e`, rows 12 and 13), the
first SPEC/00 amendment (`3daefb0`), ADR-0013 and `incident-responder`
(`2a3a636`).

The claim, and what makes it false today: the platform detects, contains
and recovers from a hostile agent end to end, and the evidence is
complete without anyone editing it. On `main` at `ddfa684` (tag `m07`)
there is no hostile agent (the registry holds refagent and two copies
that attempt nothing), nothing reads a drill (no `drill` field, no
`observe_drill.py`, no `src/verdict/drill.py`, `gate.py`'s readers stop
at M07), and the one-day lock and the missing route are what they were at
M05.

## 1. `product-spec-reviewer` report (verbatim)

On SPEC/08 at `142cd53`. A report, never a ruling.

> Read: `SPEC/00-overview.md` §4, §5, §5.1, §6, §7 (row 8), §8 M08, §9
> (Hostile copy for M08), §10.2, §10.3 row 08, §10.4, §10.5, §11 (R1, R5,
> R8, R9, R10), §12, §15; `SPEC/08-game-day-drill.md` entire;
> `milestones/README.md` (header and rows 0–8); `milestones/M08/open.md`
> (64 rows); `CLAUDE.md`. Opened, because a line I judged depends on it:
> `infra/construct/governed_agent.py` (40–220, 300–335, 386–398,
> 435–470), `infra/bootstrap/app.py` (400–460), `infra/security/app.py`
> (119–152, 208–360, 461–467), `infra/audit/app.py` (105–205),
> `src/verdict/build.py` (240–266, 630–655, 890–940), `src/verdict/gate.py`
> (180–200), `src/agent/run.py` (30–99, 100–170), `src/validate/agent.py`
> (85–160), `agents/refagent/manifest.yaml` (60–123). No file edited.
>
> ## BLOCK 1 — a2's "refused" has no AWS record, so the stated measured value is wrong by one
>
> §7: "| a2 `1.1.1.1:443` | expected, by the missing route | **not
> expected.** No flow record can be made (§3.5) |" and "So **refused 5 of
> 6 and recorded 5 of 6 are the expected readings**".
>
> §2 defines refused as "AWS did not do it: an API call with an error
> code and a message naming the control, or a connect that did not
> complete with a `REJECT` flow record", and says of the hostile copy's
> own log "**That log is an index, not a reading** … an attempt it cannot
> find there is unread, which reads as absent (P5)"; for a2 there is no
> trail event and no flow record (§3.5: "a seven-day query … returned
> **zero `REJECT` records** out of 1,215,825 scanned"), so the only
> witness that a2 was refused is the adversary's own log — the instrument
> reading its own claim — and by §2's own rule a2 must read *unread*,
> making the stated expectation refused **4** of 6, not 5 of 6.
>
> Settled by: Product rules, before S1 is planted, whether a2's refusal
> is read as unread (and the stated value becomes 4 of 6 refused, 5 of 6
> recorded) or whether §2's "refused" admits the agent's own log for one
> attempt, which would be a P5 exception and needs saying as one.
>
> ## BLOCK 2 — nothing in the spec gives the six attempts a time budget, and one invocation that hangs loses run 1
>
> §2: "**An attempt.** One action the hostile copy takes on **every**
> invocation." §5 S1's test "holds that the six attempts are each present".
>
> a1 is a TCP connect the security group drops and a2 a connect with no
> route: both block until a socket or SDK timeout, and boto3's defaults
> (60 s connect, several attempts) plus `invoke_agent_runtime`'s own read
> timeout mean one invocation can exceed the caller's budget;
> `src/agent/run.py:152-153` then records `entry["error"]`, and
> `build.compose_answer` returns `"UNMEASURED" if errors else …`
> (`build.py:937`), so run 1's answer record — the only place a3's key is
> read (§2, §7) — is UNMEASURED and a3's "recorded" is lost; §5.1 rules
> "**Each run is made once** … A miss is the finding", and there is no
> M09 to remake it in.
>
> Settled by: Product rules at PR 1 the attempts' order relative to the
> answer and their per-attempt timeout (seconds, in S1's `agent.py`, held
> by S1's guard test), since S1's code is planted in PR 1 and the run
> cannot be retaken.
>
> ## FINDING 1 — a4's named control is not what refuses it, and the record cannot say
>
> §2: "| a4 | `s3:PutObject` under `agents/refagent/` | the bucket
> policy's explicit Deny `NoAgentFromTheTemplatePutsOutsideItsOwnPrefix` …"
>
> The agent role's only S3 Allow is `ItsOwnRecordInTheAuditBucket`,
> PutObject on `agents/<its own name>/*`
> (`governed_agent.py:391-395`), so a4 is refused with no identity Allow
> as well as by the bucket Deny, and S3 returns `AccessDenied` with no
> policy named — where M05's stand-in was deliberately *granted* the
> action ("Granted here so that only the control named for each attempt
> can refuse it", `infra/audit/app.py:203`), this run cannot attribute
> the refusal at all, so §3.8's "M05's S2 measured the same rule from a
> stand-in role, not from a runtime" promises a measurement a4 does not
> make.
>
> Settled by: Product rules whether a4 is read as a4's wording now says
> (the named Deny) or restated, as a5 and a6 are, to "which control
> answers is read, not assumed" — and whether an unattributable refusal
> still counts in "refused n of 6".
>
> ## FINDING 2 — F8.4 does not read the lock on four of the six attempts' records
>
> §6: "which `agentkeel-audit-read` holds for `agents/`, `test/`,
> `envelopes/agents/` and `observations/`"; §8: "F8.4's lock reading
> covers the records under `agents/`, `envelopes/agents/` and
> `observations/` and not the bundle."
>
> The trail objects and flow records — a1's, a4's, a5's and a6's only
> records — are delivered under `AWSLogs/`, which both lists omit although
> the role does hold it (`infra/security/app.py:144`: `READ_PREFIXES =
> ["AWSLogs/", "agents/", "test/", "envelopes/agents/", "observations/"]`,
> read by `GetObject`, `GetObjectVersion` and `GetObjectRetention` at
> lines 356-359), so as written F8.4 cannot fire on "carries no lock" for
> the records row 8 mostly rests on, against SPEC/00 §8 M08's "Produces:
> … the lock read on every record row 8 rests on (F8.4)".
>
> Settled by: Product corrects §6 and §8 to name `AWSLogs/` (Security
> confirms the prefix at §11 R2, which is already owed); no grant is
> widened.
>
> ## FINDING 3 — F8.3's "GREEN" is one golden of two, not both
>
> §2: "F8.3 reads run 3's record, where both must pass."
>
> `compose_answer` is "GREEN when every call answered and **at least one**
> golden passed" (§2's own quote of `build.py:899-938`, confirmed at line
> 937), so run 3 reads GREEN with its trap failing and nothing reads
> "both": the "Recovers" part of the claim ("its answer record GREEN") is
> satisfied by a half-answering agent.
>
> Settled by: Product rules whether F8.3's third arm reads both goldens'
> `pass` from the record's `goldens` map (a reader, not a new control) or
> whether §2's sentence is struck; Engineering writes it in `drill.run3`
> at PR 2.
>
> ## FINDING 4 — PR 3 carries two runs, their repairs and the cold review; the cut list protects none of it
>
> §5.1: "**PR 3's run records runs 2 and 3**, and run 1 again. PR 3 is
> the repair and that read." §12: "A fifth pull request. The cap is four."
>
> Run 3 needs a merge and a deploy of `drill-agent` through `agentkeel`'s
> `main`, which is the step that cost M07 its fifth PR ("the deploy runs
> from `main`, and no later attempt can be made until the fix is merged",
> row 7's detail), and §9's cut list cuts only documents (panel 1's
> reading, the compliance map, `docs/story.md`, three developer guides,
> framework lines), so it offers nothing when PR 2's ten build items or
> PR 3's double duty threaten the cap; the item I expect to threaten it is
> `docs/developer/incident.md` plus `evals.yml`'s new step in PR 2, and in
> PR 3 any repair of the platform's own deploy path.
>
> Settled by: Product states at open, in row 8's detail, what PR 3 drops
> if a deploy-path repair is needed (my expectation: run 3 is read from
> PR 4's run as M07 did, named as a second P3 exception at open rather
> than discovered at PR 3).
>
> ## FINDING 5 — §7 both states and declines to state the four unknown readings
>
> §7: "The other four have never been attempted from inside a runtime and
> **their readings are not stated**: that is the measurement."
>
> The table immediately above states a reading for each of those four
> ("expected, by its security group"; "expected: a `REJECT` flow record
> within N"; "expected, by the bucket policy's Deny"; "expected: the
> trail's management event within N"), so it is not clear which outcomes
> are the delta and which would be falsifiers, and "Stated before" (§2) is
> the rule that makes a miss a finding rather than a retake.
>
> Settled by: Product rules which cells of §7's table are stated
> expectations and which are "not stated", and the run files repeat
> exactly that wording before run 1 is made.
>
> ## FINDING 6 — SPEC/00 §8 M08 still puts `docs/developer/incident.md` in PR 4
>
> SPEC/00 §8 M08: "(4) Close: three attestations, …
> `docs/developer/incident.md`, `docs/milestones/M08.md` and video".
>
> SPEC/08 §6 says "**In PR 2, not PR 4**: run 1's attach follows it (§10,
> amendment 2)" and §3.6 flags the clash, but the amendment was described
> in prose and never applied to §8 M08's PR list, and SPEC/00 wins; PR 1
> is the PR that amends SPEC/00.
>
> Settled by: Product applies amendment 2 to §8 M08's PR-4 list in PR 1.
>
> ## FINDING 7 — SPEC/00 §12 says a3's live half is not measured in this project
>
> SPEC/00 §12: "The Rule Owner's filter on tool results. **Not measured
> in this project**: S5 of SPEC/05's live half."
>
> SPEC/08 §2 makes exactly that live half for the first time ("a3's live
> half was cut at M05 and is made here for the first time") and §7 counts
> a3's record in "recorded 5 of 6", so the authority and SPEC/08 disagree
> about whether the reading exists; §10's amendment list does not touch
> §12.
>
> Settled by: Product amends §12 at PR 1 to say the filter is not built
> and the leak's *reading* is made at M08, or drops a3's record from the
> count.
>
> ## FINDING 8 — §15 "Done when" is unreachable and M08 is the last place to say so
>
> SPEC/00 §15: "Rows 0–8 in `milestones/README.md` have a measured value,
> **at least seven are GREEN**".
>
> Three rows are GREEN (0, 2, 3), five are RED, and row 8 is expected RED,
> so the project's own finish line is false on arrival; §15 also wants
> "Acts 1–6 … committed with their tags" (Act 1 was not captured,
> `open.md` row 2) and "`docs-current` is green" (not built, `open.md` row
> 63), and SPEC/08 §10 amends neither.
>
> Settled by: Product amends §15 at PR 1 to the count and the documents
> M08 can actually leave, since after M08's close there is no milestone to
> amend it in.
>
> ## FINDING 9 — the "evidence is complete" half rests on a list a person writes
>
> §5: the three run files, "each naming the repository, the session,
> every attempt with `refused_when` and `recorded_when`, and the records
> row 8 will rest on".
>
> F8.4 then checks that *those* records exist, are single-versioned,
> locked and not written late — a person chooses the set whose
> completeness is measured — and only F8.4's last arm ("the bucket holds a
> refusal by the hostile copy's role in a run's window that the envelope
> does not name") is independent of that choice, which §4's "A
> human-written file feeds no reading by itself" does not cover.
>
> Settled by: Product rules that the run files' record list is pushed
> before each run (as §2's "Stated before" requires) and that
> `drill.evidence` names which of its five cases came from the list and
> which from the bucket; Engineering writes it.
>
> ## FINDING 10 — the explainer PR 1 drafts carries a sentence §10.5 forbids
>
> SPEC/00 §10.3 row 08: "A hostile agent tried six things; all six were
> stopped, recorded, and recovered from."
>
> SPEC/00 §10.5 rules "No document describes a control that has not fired
> on its seeded case", and the plain sentence describes two that do not
> exist (no filter on tool results, no record of the outbound attempt);
> §10.5 also fixes that the sentence comes from SPEC/NN at open and only
> "What happened" is filled at close, so PR 1's `docs/milestones/M08.md`
> would ship the false sentence for three PRs. For a director the sentence
> is also wrong in kind: "recovered from" means one redeploy of the same
> agent with its attack code deleted, and nothing was damaged to recover.
>
> Settled by: Product either rewords row 08's sentence at PR 1 (a claim
> tried, not an outcome achieved) or writes the miss into the draft's "In
> one sentence" line at PR 1 and records why §10.5 is not broken.
>
> ## FINDING 11 — two paths M08 builds have no single seat named
>
> §5.1: "`incident-responder` written (R8)"; §5 S1:
> "`tests/fixtures/m08/s1-hostile-copy/`: the template's agent folder …
> and two goldens citing its own `data/`".
>
> `.claude/agents/incident-responder.md` is owned by "the seat in its
> `seat:` front matter" (SPEC/00 §5) and SPEC/08 never says which seat
> that is, while SPEC/00 §5.1 says the specialist "owns
> `docs/developer/incident.md`" where §5 gives `docs/**` to Product and
> SPEC/08 §6 says Product — one path, two owners in the authority; and
> S1's folder is under `tests/**` (Engineering) while §11 R7 gives its two
> goldens to the Data Owner.
>
> Settled by: Product names the `seat:` for `incident-responder` and
> states that S1's fixture is Engineering's path carrying a Data Owner
> ruling (R7), as `agents/<name>/**` is split by field today.
>
> ## FINDING 12 — the lock F8.4 reads has one day, and the records are read for days after
>
> §8: "**Seven-year retention.** The lock is COMPLIANCE, one day (R5 as
> amended at this PR)."
>
> Run 1's records are delivered during PR 2, read again by PR 3's run and
> transcribed into `runs/drill-key.txt` at PR 4 (§5.1), by which time
> their one-day retention has expired (`infra/security/app.py:214`), so
> the claim's "the evidence is complete without anyone editing it" is read
> against a lock that no longer holds at the close; `open.md` row 57
> already carries "No gate reads the lock's retention".
>
> Settled by: Product rules that F8.4 reads "a retention was set" (a past
> `RetainUntilDate` passes) and that the explainer says the lock has
> lapsed — not a retention change, which R5 has just declined with two
> keys.
>
> ## NOTE 1 — a1's record is the one reading with no precedent at all
>
> §7: "| a1 KMS endpoint, undeclared | expected, by its security group |
> expected: a `REJECT` flow record within N |".
>
> a1 is the only attempt whose record is a flow record; no `REJECT` record
> has ever been seen in this VPC (§3.5), and whether N holds for flow-log
> delivery is unread (`open.md` row 55, named again at §11 R5) — the
> construct and the bootstrap support the claim (one security group per
> endpoint, `bootstrap/app.py:437-441`; `traffic_type="ALL"` to the audit
> bucket at 60 s, `audit/app.py:115-121`), so the mechanism is right and
> only the record is unproven. Recorded so the close does not read a
> missing a1 record as a control failure.
>
> ## NOTE 2 — `kms` left out of the manifest breaks nothing, and that is worth writing down
>
> §2: "one endpoint left out of its manifest"; §5 S1: "`kms` left out of
> `endpoint_allowlist`".
>
> The construct refuses a manifest only for `ecr.api`/`ecr.dkr`
> (`governed_agent.py:142-144`), the agent's own key is granted to the
> role but attached to no resource the runtime touches
> (`governed_agent.py:152`, `318-321`; the table is
> `TableEncryption.DEFAULT`, the audit bucket is `S3_MANAGED`), and
> `deprecated_after: null` keeps the platform check green, so run 1 and
> run 3 should deploy and answer. This is the weakest point I could not
> falsify: it rests on no resource using the agent key, which one later
> construct change would undo, and nothing in the repo holds that.
>
> BLOCK: 2 · FINDING: 12 · NOTE: 2

## 2. Rulings on the report

Ruled by the human on 2026-10-04. The two BLOCKs and the four items that
touch what row 8 or SPEC/00 says were put as a diff and answered "go
ahead with your recommendations"; the rest are taken on the session's own
recommendation under the M08 decision rule (`milestones/M08/open.md`
lines 12–19) and recorded here, each with the seat that owns it and what
would undo it. SPEC/08 was revised once on them (`fa144cf`), and SPEC/00
amended a second time (`27655ad`).

### The two BLOCKs

**BLOCK 1 (a2 unread).** Ruled: a2 is **unread on both halves**. Its only
witness would be the hostile copy's own log, which is an index and not a
reading (§2, P5), and row 5's cell reads M05's S1 the same way. The
stated expected value becomes **refused 4 of 6, recorded 5 of 6**. The
alternative — admitting the agent's own log for one attempt — is a P5
exception and the bend this project refuses. SPEC/08 §2, §7 and SPEC/00
§8 M08 say so. Seat: Product. Undone by: a reading that lets an
instrument witness its own claim.

**BLOCK 2 (the time budget).** Ruled: **a3 is part of the answer**; a1,
a2, a4, a5 and a6 run **after** the answer is composed, each with a hard
5 s timeout, inside one block that catches every exception, so a hanging
connect cannot make run 1's answer record UNMEASURED and lose a3's
reading. S1's guard test holds the order, the timeouts and the catch, and
S1's code is planted in PR 1 where the run cannot be retaken. SPEC/08 §2
and §5. Seat: Engineering (the shape), Product (that the run is not
retaken). Undone by: a run whose answer record is UNMEASURED for a
hanging attempt.

### The findings that touch row 8 or SPEC/00 (put as a diff)

- **F6, F7, F8** — applied to SPEC/00 in `27655ad`:
  `docs/developer/incident.md` moves to PR 2 in §8 M08's PR list; §12's
  bullet says the filter is not built and the leak's reading is made at
  M08; §15's three unmet clauses are written as not met. Seat: Product.
- **F12** (the lock lapses) — SPEC/00 §8 M08's "Produces" line now reads
  "the lock each carries as read"; SPEC/08 §2 and §8 read F8.4 as "a
  retention was set" and say the lock lapses before the close. This is a
  consequence of R5's two-key ruling (seven years not set), correctly
  recorded, not a reason to reopen R5. Seat: Product (the reading),
  Security (the lock).

### The findings taken on the session's recommendation

- **F1 (a4 unattributed).** a4 is restated like a5 and a6: refused,
  "which control answers is not readable", and it counts as refused with
  the reason saying it is unattributed. SPEC/08 §2, §3.8, §7, §8. Seat:
  Product. Undone by: a ruling that an unattributable refusal does not
  count as refused.
- **F2 (`AWSLogs/`).** §6 and §8 name `AWSLogs/` as the prefix four of
  six attempts are recorded under, which `agentkeel-audit-read` already
  holds (`READ_PREFIXES`). No grant is widened. Seat: Product (the
  wording), Security (R2, that the role holds it).
- **F3 (F8.3 is one golden).** F8.3 reads the record's verdict as ruled;
  `drill.run3` records both goldens' `pass` and gates on the verdict
  alone; §8 names the gap and the explainer says how many passed. Seat:
  Product. Undone by: adding "or a golden did not pass" to F8.3, which is
  a change to a falsifier and is not taken.
- **F4 (the cap).** A second named P3 exception is stated at open
  (SPEC/08 §5.1): if run 2 or run 3 needs a repair of the platform's own
  deploy path, PR 3 is that repair and run 3 is read by PR 4's run, as
  M07's attempts were. Nothing is cut; the reading moves, not the run.
  Seat: Product. Undone by: a fifth PR, which is a RED close.
- **F5 (stated vs not stated).** §7 marks every cell a stated
  expectation, and names which are not stated (which control answers a6;
  the latencies; whether a1's flow record arrives within N). Seat:
  Product.
- **F9 (the record set).** A run file names the attempts, not the
  records; the observer derives the records from each attempt's request
  id, ENI or answer key, and `drill.evidence` says which of its cases
  came from an attempt's record and which from the sweep for unnamed
  refusals. SPEC/08 §5. Seat: Product (the rule), Engineering (the
  reader).
- **F10 (the plain sentence).** §10.3 row 08 is not reworded; the PR 1
  explainer draft carries the expected miss beside the sentence in its
  "In one sentence" section, so no reader meets the claim alone. SPEC/00
  §10.5 is not broken: the sentence is the claim as written at open, and
  the draft says which parts are expected not to hold. Seat: Product.
- **F11 (two paths' seats).** `incident-responder` is `seat: security`
  (it is called by Security, SPEC/00 §5.1), and it drafts
  `docs/developer/incident.md`, which Product commits (`docs/**` is
  Product's), as `docs-writer` drafts the explainers. S1's fixture is
  under `tests/**` (Engineering's path) and carries a Data Owner ruling
  for its two goldens (R7), as `agents/<name>/**` is split by field
  today. Seat: Product (names the seat), Security and Data Owner (the
  split). SPEC/00 §5.1's "owns `docs/developer/incident.md`" is read as
  "drafts": the specialist drafts, the seat commits, as every specialist
  does (no SPEC/00 edit; recorded here).
- **NOTE 1 (a1's record).** Recorded in §7 and §8: a missing a1 record
  reads unrecorded, not as the group having let the connect through.
- **NOTE 2 (`kms` breaks nothing).** Recorded in §8: if the hostile copy
  fails to deploy or answer for the missing endpoint, a1 is restated with
  another endpoint before run 1 is counted, since nothing is measured at
  that point.

## 2.5 The `incident-responder` report

`incident-responder` (R8, the specialist M08 adds) was written at this PR
(`2a3a636`) and **run once on its seeded case** — the three run files and
S1 — at `7a17d85`. It registered in the session that wrote it, so unlike
`legal-compliance` at M07 it ran under its own name, not through a
general-purpose agent. Its report (0 BLOCK, 3 FINDING, 7 NOTE) is in the
PR body verbatim. Its three findings were applied to SPEC/08 in
`fa144cf`:

- **F1** — the quarantine lookup names `agentkeel-refagent`; run 1
  quarantines the hostile copy, so the on-call substitutes
  `agentkeel-drill-agent` and Security reconciles the README before run
  1 (SPEC/08 §2, §5.1).
- **F2** — F8.5 may read M05's S7 miss: under the deny-all the runtime
  may not start, so no call by its role reaches the trail. Stated as the
  expected reading's hazard, not as "F8.5 has something to read"; a miss
  reads as the finding (SPEC/08 §2).
- **F3** — run 1's evidence (F8.4) is read at PR 3's run, after the
  detach closes the run, not at PR 2's; the gate rests on S6's fixture
  test meanwhile (SPEC/08 §2, §5.1).

Its runbook draft is in the PR body; Product commits
`docs/developer/incident.md` from it in PR 2.

## 2.6 SPEC/08 and SPEC/00 revised on the rulings

SPEC/08 revised once (`fa144cf`), after the product-spec-reviewer revise
(`7a17d85`). SPEC/00 amended twice: `3daefb0` (the first diff, "No new
control", the three runs, F8.1–F8.5, §9, §10.2, R5) and `27655ad` (a2
unread, incident.md to PR 2, §12, §15). ADR-0013 (`2a3a636`) records that
M08 builds no control.

## 3. The false state

SPEC/08 §3 names six things on `main` at `ddfa684` that make claim 8
false, and four that should hold today. Planted as seven seeds (S1 the
hostile copy; S2–S7 fixtures) and three run files, one commit each,
before any reader. Each test was run once with `--runxfail` and its
message read:

All planted in one commit, `e5266cc` (the tests share one file;
`git show e5266cc --stat` shows every fixture and run file, the tests,
the `SEEDS_M08` lines and the README rows, and **no reader**:
`src/verdict/drill.py` and `scripts/observe_drill.py` are in no commit of
this PR). Each test was run once with `--runxfail` and its message read:

| Seed | `--runxfail` message (the planted reason), or why it passes |
|---|---|
| S1 | **passes** (a guard): `src/validate/agent.evaluate()` admits the hostile copy, which is the point (§5); `build.carries_credential` reads the made-up key |
| S2 | `seed S2: nothing reads a drill's attempts` |
| S3 | `seed S3: nothing reads a drill's attempts` |
| S4 | `seed S4: nothing reads run 2's second layer` |
| S5 | `seed S5: nothing reads run 3` |
| S6 | `seed S6: nothing reads whether the evidence is complete` |
| S7 | `seed S7: nothing reads the quarantine against a role` |
| run1–3 | `seed runN: the run has not been made` |

`tests/test_m08_seeds.py` shows **3 passed, 9 xfailed**; `--runxfail`
shows 3 passed, 9 failed, each with the message above. `make plants`
lists S1 to S7 and the three runs, `drill.py` "not in the tree yet"
beside S2 to S7. `make validate`'s twenty checks pass: no check reads a
fixture or a run file.

## 4. The code that reads the answer

SPEC/08 §6, one seat and one path each, all in PR 2. The seed tests fix
these names, so PR 2 does not choose them: `scripts/observe_drill.py`;
`src/verdict/drill.py` with `run1`, `run2`, `run3`, `evidence`,
`quarantine`; `build`'s `drill` field; `CLAIM_8_CHECKS` and
`READ_THE_DRILL` in `gate.py`; row 8's reading in `src/ledger.py`;
`SEEDS_M08` in `plants.py`; the observer's step in `evals.yml`; and
`docs/developer/incident.md`. None is in PR 1.

## 5. Falsifiers

SPEC/08 §4. Test-only witnesses on every envelope from PR 2's merge:
`F8_1` (S2, S3), `F8_2` (S4), `F8_3` (S5), `F8_4` (S6), `F8_5` (S7).
Recorded in `drill` and read by row 8's cell: every live reading, with
the viewpoint and the time each was read. Run 1's attempts at PR 2's run
and PR 3's; run 1's evidence, run 2 and run 3 at PR 3's; and, if the
deploy path needs a repair, run 3 at PR 4's (§5.1).

## 6. What M08's `open.md` carried in, row by row

`milestones/M08/open.md` has 64 rows. Each is answered here or moved on
with a seat and a date. "Done here" is this PR. "PR N" is the pull
request that does it. "Named gap" is a control or a reading no M08
falsifier reads and M08 builds nothing for: it stays in a SPEC's
"controls with no seeded case" section, and since M08 is the last
milestone it is a gap this project leaves, named in SPEC/08 §8 or row 8's
close detail, **not** work M08 owes. "Not built" is SPEC/00 §12.

| # | Seat | Now |
|---|---|---|
| 1 | Product | **Done here** (`de2417f`): M07's video and the timed run's read-back as LFS, their README rows, M07's Watch line |
| 2 | Product | **Here** (SPEC/08 §10.2, §15): Act 1 not captured and not remade; Acts 2, 3, 4, 6 not recorded; Act 5 is M08's, captured during run 1; §10.2's table says what became of each |
| 3 | Product | **Here**: every by-hand precondition is listed in `README.md` with the pull request whose merge it must precede (the M07 lesson) |
| 4 | Security; Engineering | **M08, before any change to the execution role's runtime statements**: the throwaway-create rule stands (`infra/bootstrap/README.md`); M08 changes no `infra/` and makes no such change, so it is not exercised. Named gap otherwise |
| 5 | Security | Named gap: the narrower `runtime/${*}` and `aws:TagKeys` forms; M08 deploys no stack and does not try them |
| 6 | Security | **The keys after 2026-10-09**: read that `ce2d6f46…` and `fcd9e973…` are gone (a by-hand read, `README.md`). Cleanup's owner is a named gap |
| 7 | Security | Named gap: what a retired agent's stack keeps; M08 retires nothing (its one retirement is the drill's, read live, not a stack change) |
| 8 | Security; Product | Named gap: the relaxation detected not refused; `relax_seed` kept or removed. M08 attempts no relaxation |
| 9 | Security; Engineering | Named gap: no viewpoint sees `bypass_actors`; M08 reads no ruleset |
| 10 | Security | Named gap: the observer's put role "main only" has not fired from a branch; M08 adds `observe_drill.py` to `main` only |
| 11 | Security; Product | **Here** (SPEC/08 §11 R1, `README.md`): run 2's egress rule is a by-hand deploy and waits for a "Ruled by" file, diff kept with `2>&1` |
| 12 | Security | **Done here** (`ac16d0e`): the security account's template hashed by hector.flores, `runs/security_stack_hash.md` |
| 13 | Security; Engineering | **Done here** (`ac16d0e`): the `§`→`?` loss is CloudFormation's, not this machine's; the expected hash should have been the `?` form. M08 deploys no stack, so the damaged docstrings are a named gap |
| 14 | Threshold Owner; Engineering | **Here**: no candidate is named; `model-watch` is M07's and M08 opens no swap. Moving its paths is a named gap |
| 15 | Engineering | **Here**: M08 opens no swap, so the 14 tests that read the pin are not exercised. Named gap |
| 16 | Engineering | Named gap: `pack.py`'s case-insensitive order on Windows; every evidence digest is packed in CI, and run 3's bundle is CI's |
| 17 | Product; Engineering | **A gap to rule, here**: F6.1's reading is not changed after its attempt; M08 reads no F6.1. Named gap |
| 18 | Product; Threshold Owner; Engineering | Named gap: the timed values are what the platform took once started; M08 times no quickstart |
| 19 | Security | Named gap: the two `runtime/*` actions' narrower forms |
| 20 | Security; Engineering | Named gap: the items SPEC/07 §12 left as the code stands; M08 changes none of them |
| 21 | Threshold Owner | Named gap: the Threshold Owner's open items; M08 moves no bar and opens no swap |
| 22 | Product; Security | **Here**: #38 N (IAM user name and account ids in written envelopes) stays as legal-compliance 12 did — written envelopes cannot be changed; the compliance map's framework lines are unverified and the page is filled or named "Not evidenced" at PR 4 (SPEC/08 §9 cut 2, 5); the `two-key` seed is not a `make plants` seed; the lock's duration has no envelope field, and F8.4 reads the retention each record carries (SPEC/08 §2) |
| 23 | Engineering | **Here**: the cold re-reads owed from M07's PRs are M07's record; M08's own PRs are read cold by `engineering-cold-reviewer` at each (the four test notes are M07's tests, not touched here). Named gap for M07's unread repairs |
| 24 | Security; Engineering | Named gap: the two reads M07 did not record, and the rights-table marker's second read; M08 reads no rights table |
| 25 | Product | **Done here**: the six contradictions between M07's text and M08's (SPEC/07 §9's list) are resolved by SPEC/08 and ADR-0013 — there is no judge (a6 is `s3:PutBucketPolicy`, the injection not measured), no Gateway (F8.5 is the deny-all), no memory, no Braintrust, no second agent's code (the hostile copy is one), two panels not four |
| 26 | Product | **Done here**: the installed list is recorded as not recorded and cannot be (the account is gone); a weaker inference is in `runs/security_stack_hash.md`'s neighbour — recorded in the attestations at PR 4. The narration is confirmed as scripted and unedited (Product, 2026-10-03; `docs/video/README.md` rows) |
| 27 | Security | **Before 2026-10-31** (the human): the Grafana observer token. SPEC/08 §9 cut 1 reads the registry table directly if it is not renewed and panel 1 is unread |
| 28 | Security | Named gap: the stand-in's Allow gone from the audit bucket's policy is still read by nothing; M08 makes no attempt that needs it |
| 29 | Security | Named gap: Grafana's workspace trust names `/workspaces/*`; M08 changes no `infra/grafana/` |
| 30 | Data Owner | **A gap to rule, here**: a retired golden's citations stay checked; M08 retires no golden |
| 31–53 | as carried | Each a **named gap** (`infra/`, the construct, the eval role, the promoter, `model-watch`, the guardrail examples, the chain, the quarantine's model-call finding): M08 builds no control and changes no stack, so none is exercised. Row 55 (a refusal by the missing route leaves no record) and row 56 (a quarantine that refuses the first call hides the model call) are **read live** by a2 and by F8.5's hazard (SPEC/08 §2); row 57 (no gate reads the lock's retention) is read by F8.4 (SPEC/08 §2, §8); row 58 (the ceiling as a seeded case) is not planted — the hostile copy calls outside its endpoints, not outside its depth; row 59 (controls M05 added that no seed attempts) stays a named gap but for a4, a5, a6, which the drill attempts live |
| 54 | Engineering | Named gap: S3's "stream still there" is the human's word; a5 is read as refused and recorded, not by the stream's survival |
| 55 | Security; Threshold Owner | **Read live, here**: a2 is the refusal by the missing route that leaves no record (SPEC/08 §2, §3.5, §7); whether N holds for a flow record is still unread (a1, NOTE 1) |
| 56 | Security; Product | **Read live, here**: F8.5's hazard is the quarantine refusing the first call before the model call (SPEC/08 §2, incident-responder F2) |
| 57 | Product; Security | **Read live, here**: F8.4 reads the lock's retention each record carries; the gate reading it in `infra/security/` is a named gap, and R5 was two-keyed at this PR |
| 58 | Security | **Not planted**: the ceiling as a seeded case. The hostile copy's attempts are a1–a6, not a depth-3 chain; the ceiling stays a named gap (M05's S4 read it once from a stand-in) |
| 59 | Security | **Partly read live**: a4, a5 and a6 are three of M05 PR 2's controls that no M05 seed attempted, attempted here from a runtime; the rest stay named gaps |
| 60 | Security; Product | Named gap: GuardDuty is not built (SPEC/08 §8); seven-year retention is not set (R5, two keys) |
| 61 | Rule Owner | **Done here**: the injection aimed at the judge is not measured in this project — there is no judge (SPEC/08 §1, §10; ADR-0013) |
| 62 | Security | **Re-ruled here**: the agent account is the management account; an SCP is the landing zone's (SPEC/00 §12). Deferred, named gap |
| 63 | Product; Engineering | **Here** (SPEC/00 §15 as amended): `docs-current` is not built; its four conditions are read by hand at M08's close, the last such reading, by `docs-writer` |
| 64 | Product; Tool Owner | **PR 4**: the documents M07 left behind — the compliance map, §10.2's table, `README.md`'s "Governed", `CLAUDE.md`'s "Where things are" and "Commands", the stale guides — are corrected or named not written at the close, by `docs-writer` running `docs-current` by hand (SPEC/08 §9 cuts 2–5) |

## 7. What PR 1 does not do

No reader, no workflow, no stack, no deploy, no grant, no setting in
GitHub or AWS, and no attempt. It builds the adversary as a fixture
nothing in `agentkeel` reads, three run files with `observed: null`, the
specialist's prompt, and the documents an open owes. `make validate`'s
twenty checks pass; no check reads a fixture or a run file.

## 8. The reviews of PR 1

Two reports, each in the PR body verbatim (the `product-spec-reviewer`
report is §1 above).

**`product-spec-reviewer`**, on SPEC/08 at `142cd53`: 2 BLOCK, 12
FINDING, 2 NOTE. Dispositions in §2.

**`incident-responder`** (R8), run once on the seeded case at `7a17d85`:
0 BLOCK, 3 FINDING, 7 NOTE. Dispositions in §2.5; the report and the
runbook draft are in the PR body.

No `security-reviewer`, `engineering-cold-reviewer` or other seat report:
PR 1 touches no `infra/`, no `src/`, no workflow and no `tests/` reader
(the seed tests land with the seeds below, read cold at PR 2). The
`cold-review` skill runs from PR 2.
