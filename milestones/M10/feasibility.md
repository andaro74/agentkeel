# M10 feasibility

Written at M10 PR 1, the plant (`/open-milestone M10`). M10 is an eleventh
milestone, opened after M09 (which SPEC/00 planned as the last, "SPEC/00
plans no M10") closed GREEN and was tagged. SPEC/00 was amended and SPEC/10
drafted first (`053ee19`), and `product-spec-reviewer` run on it before
anything else of PR 1 was written. SPEC/10's revision, SPEC/00's four more
lines, CLAUDE.md's seat table and ADR-0015 followed (`841178f`), then the
seeds (`fba41ad`).

The claim, and what makes it false today: a caller outside the platform
reaches an agent only through a door the platform controls, under an
identity the agent's manifest admits, with the agent's pinned guardrail on
every answer and the caller named in each call's record in the security
account; a caller with no identity, or one the manifest does not admit, is
refused and the refusal is in the security account within N. On `main` at
`833ab2b` (tag `m09`) the runtime answers any IAM principal in the platform
account that holds `InvokeAgentRuntime` and nothing else decides
(`src/agent/run.py` `invoke_deployed`); the answer record `build` writes
names no caller; the manifest schema refuses a `callers` key; `two-key`
passes a caller admitted with one key; nothing reads a call. The claim's
wording was ruled by Product at the session's stop, before SPEC/10 was
written (§2.4).

## 1. `product-spec-reviewer` report (verbatim)

Run on SPEC/10 at `053ee19`, 2026-10-13. A report, never a ruling.

> Read: C:\Users\andar\code\agentkeel\SPEC\10-public-caller.md; SPEC\00-overview.md (§3 row, §4, §5, §6, §7 row 10, §8 preamble and M10, §10.3, §10.5, §12, §15); milestones\README.md (header and rows 0–9); src\agent\run.py:60-110; src\verdict\build.py:990-1034; src\manifest\schema.json; src\gates\two_key.py (grep); infra\construct\governed_agent.py:284-298, 522-558 (and grep for `authorizer`: no match); infra\bootstrap\app.py (grep: `CallTheRuntimeItJustDeployed` l.937, `InvokeRefagentRuntimeOnly` l.1006); .github\workflows\deploy.yml:628-650; thresholds.yaml:78-89, 146; src\verdict\gate.py (grep: `READ_THE_RULES` l.223, `CLAIM_9_CHECKS` l.166); src\verdict\plants.py (grep: `SEEDS_M09`); docs\adr\ADR-0009 (amendment 1 only); tests\fixtures\m09\s1-festival-desk\ (exists); milestones\M10\ (absent, as expected); docs\adr\ADR-0015 (absent).
>
> **Check 1, false state.** SPEC/10 §3 items 1–5 are live at the cited lines: `invoke_deployed` (run.py:81-88) sends an ARN and a payload only; `compose_answer` (build.py:1005-1022) writes no caller; `schema.json` has `additionalProperties: false` and no `callers`; `two_key.relaxations` has entries for thresholds, goldens, rules, guardrail, budgets, memory, `deprecated_after` and nothing for `callers`; `_runtime` (governed_agent.py:528-558) sets no `authorizerConfiguration`; the two bootstrap sids and the deploy step exist as named. The fixtures are plantable in PR 1. The live false state (a stranger refused on a record) needs the door, which lands PR 2 and deploys after PR 2 merges; SPEC/10 §5.1 names that as a P3 exception and the cell cites PR 3's run. No BLOCK on this check.
>
> **Check 2, reader.** `src/verdict/caller.py` `calls(...)`, `build`, `gate.py` `READ_THE_CALLER`, `src/ledger.py`, all PR 2 (§6). The observer writes raw records. P5 holds on paper; finding 1 below is where it bends.
>
> ---
>
> **FINDING 1** — §2 "The call record": "`reason` for a refusal (`no identity`, `not admitted`, `not the door`) ... Written by the door's log delivery as AWS records it; never by the agent, the observer or a person." AWS writes none of those three strings, nor `outcome: admitted`, so some code maps a CloudTrail or runtime-log event onto §2's shape, and the spec names neither the module nor its seat, while S1's fixtures (§5) are already in the mapped shape, so `calls()` is tested on a shape no delivery produces. Settled by naming the mapper (proposed: `build`, from the raw event, with one S1 fixture in the raw shape) in feasibility.md; Engineering rules the module, Product the record shape under R5.
>
> **FINDING 2** — §2 "The call record": "`guardrail` as the trace carried it for an admitted call". The door's delivery (an `InvokeAgentRuntime` event or the runtime's log) cannot see the agent role's model call, and today's only record naming a guardrail is the answer record, whose `guardrail.source` is `"stack"` (build.py:1014; deploy.yml:647-648 passes `--guardrail "$PIN"` from the stack output), not a trace; so F10.2's per-call arm ("the admitted call's record carries a `guardrail` other than the agent's pin", §4) has no observable source for the owner's hand-made admitted call. Settled by Product ruling F10.2's live reading is the answer record's `g-030` arm and refagent's 7 of 7 only, and dropping `guardrail` from the per-call record or naming its source.
>
> **FINDING 3** — §4 F10.4: "each `outcome: refused` on a record whose `time` is within 600 s of the call's". The two timestamps are not named: for a no-token call the record's `time` is the only time of the call, so "within N" must be delivery (the object's `LastModified` against its `eventTime`, as M05's `alarm_latency_s` was, thresholds.yaml:78-82), yet §2 P5 says the observer records "the time each was read", which is not arrival. Settled by one sentence in §4 naming both timestamps; Threshold Owner (N's reading) with Engineering.
>
> **FINDING 4** — §2 door 1 unknowns: "(a) JWT mode refuses SigV4 outright" and §11 R2: "If (c) answers no, door 2." Only (c) has a ruled fallback; if (a) answers no, the bypass arm (an IAM principal with the grant, §4 F10.1) is answered and the run reads RED on F10.1 with no door change ruled. Settled by R2 stating the fallback for (a) no (narrow the bootstrap grants, or door 2); Security.
>
> **FINDING 5** — §5 S1: "`call_held.json` is the admitted user's call ... beside three refused records (`none`, `stranger`, `bypass`) each within N: held". F10.4's second arm ("refused with no record within N") and F10.3's "a caller other than the one that called" have no planted false state: no S1 fixture carries a record later than N or a wrong subject, so the reader's time and identity comparisons are not seeded. Settled by two more S1 records in PR 1 (a late refusal, a wrong subject) or Product naming the arms as live-only; Product.
>
> **FINDING 6** — §9 cut 4: "the runtime admits both the pool's tokens and the platform's IAM principals (door 1 in a mixed mode ...); F10.1's bypass arm then names the platform's roles as admitted by the construct". That cut changes the door and removes the bypass call's refusal, both of which §9's own first line forbids ("Never cut: the door, ... the four live calls"). Settled by Product striking cut 4 or moving the goldens step to the never-cut list.
>
> **FINDING 7** — §2 "`callers`. A manifest field (Tool Owner; ...)" and SPEC/00 §8 M10 item 1 "(Tool Owner)". SPEC/00 §5's Tool Owner row owns "`may_call`, `may_be_called_by`" and no `callers`; the status line lists §5 as not amended at M10 PR 1, and CLAUDE.md's table matches §5, so the field the milestone builds has no seat in §5. Settled by amending §5 (and CLAUDE.md) at PR 1 under `rulings/pr1.md`; Product.
>
> **FINDING 8** — SPEC/00 §8 M10 item 2: "the runtime's own JWT authoriser on an identity pool the bootstrap stack deploys" against SPEC/10 §2 "A Cognito user pool per agent, in the agent's own stack, made by the construct" and §6 "The door | the construct". Bootstrap and construct are different stacks, deploy paths and cdk-nag reports. SPEC/00 wins; settled by Product correcting one of the two at PR 1; Security rules which stack under R2.
>
> **FINDING 9** — SPEC/00 §10.3 row 10: title "Strangers come in by the front door" beside the sentence "a stranger is turned away and the attempt written down". "Stranger" means the admitted outsider in the title and the refused one in the sentence (and in SPEC/10 §5, the `stranger` arm is the refused call), so a director reads one word two ways in one row. Settled by Product renaming the title ("Outsiders come in by the front door") or the arm.
>
> **NOTE 10** — §3.2: "has `repository`, `agent`, `commit`, `platform_commit`, `runtime_arn`, `model_id`, `region`, `guardrail`, `goldens`, `observations`, `errors`, `tokens_in`, `tokens_out` and no caller". `compose_answer` also writes `what`, `run_url` and `verdict` (build.py:1006, 1020, 1021); S1's `record_no_caller.json` is to be "today's answer record shape", so the list it copies is short by three fields. Engineering, at the fixture.
>
> **NOTE 11** — SPEC/10 status line: "ADR-0015" and SPEC/00 §10.5 "ADR-0015, which carries the rule since ADR-0005 has no amendment left". No `docs/adr/ADR-0015*` exists at 053ee19; §10.5's no-recording rule and §8's eleventh milestone rest on a file PR 1 has still to write. Product, in PR 1.
>
> **NOTE 12** — §9 cut 3 against §10.3: "F10.3 reads the record's client against the admitted user's client" while the plain sentence says "every question is recorded with who asked". If cut 3 is taken, the record names a client, not a person's name, and the sentence overstates; the explainer's "What happened" must then say "which app, not who". Product, at the close.
>
> Expected output (check 4) is stated before the run: "admitted 1 of 1, refused 3 of 3" (§1, §7); PR 1 "2 passed, 5 xfailed"; PR 2 `caller` unread, row 10 RED. The delta is the four live calls; F10.1–F10.5 are the falsifiers. No "governed", "secure" or "proven" in SPEC/10 about the door.
>
> BLOCK: 0 · FINDING: 9 · NOTE: 3

## 2. Rulings on the report

No BLOCK, so the PR may open. Every finding and note was taken on the
session's recommendation (the decision rule since M08) and is recorded
here with its seat and what would undo it; each is also a proposal until
the seat's ruling file for this PR reads "Ruled by". SPEC/10 was revised
once on them, SPEC/00 four lines more and CLAUDE.md one row (`841178f`).

| # | Disposition | Seat | Undone by |
|---|---|---|---|
| 1 | **The mapper named.** SPEC/10 §2 "The call record" now has two shapes: the *raw* record AWS delivered, written by the delivery alone and copied by the observer with its `LastModified`; and the *read* record `build` maps it onto (`src/verdict/caller.py` `from_raw(event)`), whose field names are fixed in SPEC/10. S1's fixtures are read records, since the raw shape is known only after the probe; PR 2 plants one raw record from the probe's output as its own first commit, before `from_raw` exists (the `/open-milestone` step 4 allowance). | Engineering (the module); Data Owner (the read shape, R5) | a raw shape the probe shows that no mapper can read into §2's fields, which would be a finding for R5 |
| 2 | **No guardrail on a call record.** Struck from §2; F10.2's live reading is the answer record of the deploy that put the door on (the goldens asked through the door as `platform`, `g-030` 1 of 1, the pin named) and refagent's 7 of 7; SPEC/10 §1, §4, §5, §7 reworded. | Product | nothing |
| 3 | **The two timestamps named.** `time` is AWS's `eventTime` of the call; `delivered` is the object's `LastModified`; within N is their difference, as M05's `alarm_latency_s`; the observer's read time is recorded and is not arrival. SPEC/10 §2, §4 F10.4, §11 R6. | Threshold Owner (N's reading); Engineering | nothing |
| 4 | **A fallback for (a).** If JWT mode does not refuse SigV4, the bootstrap's `InvokeAgentRuntime` grants are narrowed by a condition on a runtime tag the construct sets for an agent with `callers` (`agentkeel:door=jwt`, proposed); failing that, door 2. SPEC/10 §2 door table, §11 R2. | Security | Security ruling otherwise at R2 |
| 5 | **Two more S1 records**: `call_wrong_subject.json` (a subject in `callers` that is not the stated caller) and `call_refused_late.json` (the stranger's refusal delivered 601 s after its event time). SPEC/10 §5; both planted in `fba41ad`. | Product (the seeds); Engineering (their test) | nothing |
| 6 | **Cut 4 struck**; the `platform` client through the door joins the never-cut list (without it the bypass arm has nothing to refuse). SPEC/10 §9. | Product | nothing |
| 7 | **SPEC/00 §5 amended**: the Tool Owner's row gains `callers`, with "admit a caller with one key" under May not; CLAUDE.md's seat table follows; SPEC/00's status line names §5. | Product | nothing |
| 8 | **SPEC/00 §8 M10 item 2 corrected** to "an identity pool the agent's own stack deploys (the construct, as the agent's guardrail is since M09)". Which stack is still Security's at R2; SPEC/00 and SPEC/10 now agree on the proposal. | Product (the line); Security (R2) | Security ruling the bootstrap at R2, in which case both lines change at PR 2 under that ruling |
| 9 | **The title is "Outsiders come in by the front door"** (SPEC/00 §10.3 row 10; the explainer's title). The refused arm keeps the name `stranger`. | Product | nothing |
| 10 | **The three fields added** to SPEC/10 §3.2's list (`run_url`, `verdict`, `what`); `record_no_caller.json` carries all sixteen. | Engineering (the fixture); Product (the line) | nothing |
| 11 | **ADR-0015 written** in `841178f`, proposed, carrying the eleventh milestone, the public caller's definition, `callers`, the door, the record and the no-recording ruling. | Product | nothing |
| 12 | Recorded. If cut 3 is taken, the explainer's "What happened" says the record names which app asked, not who; SPEC/10 §9 cut 3 says so. | Product | nothing |

### 2.4 The stop before SPEC/10 (Product, 2026-10-13)

The session stated the claim and the false state and stopped, as the brief
required, before SPEC/10 was written. Product ruled the claim **as
reworded** by the session, with four changes from the brief's proposal,
each with its reason, and **yes** to every proposal put at the same stop
(the door, the outside caller, the manifest field, the record, N, R7's
housekeeping), each recorded in SPEC/10 §11 as a proposal for its seat.
The four changes:

| Brief's words | Ruled words | Why |
|---|---|---|
| "the platform's one door" | "a door the platform controls" | two of the three door candidates are one door per agent; the claim should not presume R2's answer |
| "an identity the platform issued" | "an identity the agent's manifest admits" | the admission lives in a seat-owned file, which is what F10.4 reads; "issued" presumes a door that mints credentials |
| "named in the answer's record" | "named in each call's record" | the answer record is written once per deploy, not per call; the claim needs a per-call record, which PR 2 defines |
| "F10.1 a call that bypasses the door reaches the agent" | "a principal other than the door's reaches the agent, from outside or from a platform principal the construct does not name" | an outsider is refused today by IAM's default, so the outsider's bypass has no plantable false state; the platform's own principals are the live bypass |

### 2.5 The `tool-owner` report

Written into this section when the report arrives (§8); the report itself
is in the PR body verbatim. PR 1 proposes a manifest field (`callers`) and
changes no schema, so the read is of SPEC/10 §2 and §11 R4 and of seed S2's
`with_callers.yaml`.

### 2.6 The `engineering-cold-reviewer` report

Written into this section when the report arrives (§8); the report itself
is in the PR body verbatim.

## 3. The false state

SPEC/10 §3 names five things on `main` at `833ab2b` that make claim 10
false and one that holds today. Planted as four seeds and one run file in
one commit, `fba41ad`, before any reader (`git show fba41ad --stat` shows
the six call records, the two manifests, the two-key cases, the run file,
the tests, the `SEEDS_M10` lines and the README rows, and **no reader**:
`src/verdict/caller.py`, `src/validate/callers.py`, the schema's `callers`
key, `two_key.py`'s entry 7 and `scripts/observe_caller.py` are in no
commit of this PR). Each planted test was run once with `--runxfail` and
its message read:

| Seed | `--runxfail` message (the planted reason), or why it passes |
|---|---|
| S1 | `seed S1: nothing reads a call record` |
| S2 refused | `seed S2: nothing reads who may call an agent` |
| S2 admitted by the schema | `seed S2: the manifest schema refuses `callers`: ["<manifest>: Additional properties are not allowed ('callers' was unexpected)"]` |
| S3 a subject added | `seed S3 (a subject added): two-key passes a caller admitted with one key` |
| S3 the key removed | `seed S3 (the key removed): two-key passes a caller admitted with one key` |
| S3 left alone | **passes** (a guard): `callers: []` unchanged with one key passes before and after the reader |
| S4 the invoke condition | **passes** (a guard): the fixture agent's stack conditions both `InvokeModel` allows on its own guardrail at its version, and its runtime carries no authoriser yet |
| S4 refagent's plants | **passes** (a guard): the latest CI-written envelope reads `plants_expected` 7, `plants_fired` 7, GREEN |
| run | `seed run: the run has not been made` |

`tests/test_m10_seeds.py` shows **3 passed, 6 xfailed**; `--runxfail`
shows 3 passed, 6 failed, each with the message above. SPEC/10 §7 said "2
passed, 5 xfailed" at `053ee19`, written before the tests: the two-key
seed has two cases and a guard, as M07's has, so the count is 3 and 6.
Corrected in SPEC/10 §7 at the documents commit, with the first count left
in brackets there; the ledger row carries 3 and 6. `make plants` lists S1
to S4 and the run, the readers "not in the tree yet" beside S1, S2 and the
run, and "in the tree" beside S3 (`two_key.py`, which gains entry 7 at PR
2) and S4 (the construct and the gate). `make validate`'s twenty-one checks
pass: no check reads a fixture, a run file or a call.

**S3's "in the tree" is the file, not the entry.** `two_key.py` exists and
reads a manifest's guardrail, budgets and dates; it has no entry for
`callers`, which is why the gate passes the seed. The strict marker, not
the plants list, says the reader is not there.

## 4. The code that reads the answer

SPEC/10 §6, one seat and one path each, all in PR 2. The seed tests fix
these names, so PR 2 does not choose them: `src/verdict/caller.py` with
`from_raw(event)` and `calls(records, stated, callers, max_seconds)`
returning `{read, held, admitted, refused, expected_admitted,
expected_refused, reasons}`, whose reasons carry the strings the S1 test
reads ("names no caller", "does not admit", "without the door", "other
than the one that called", "later than"); `src/validate/callers.py` with
`callers_errors(manifest)`; `src/manifest/schema.json`'s `callers` key;
`two_key.py`'s entry 7 naming "ADR-0009 amendment 2"; `scripts/observe_caller.py`;
`caller` on the envelope; `CLAIM_10_CHECKS` and `READ_THE_CALLER` in
`gate.py`; row 10's reading in `src/ledger.py`; `SEEDS_M10` in `plants.py`
(this PR); the door, the pool and the deploy step's token as Security
rules. None is in PR 1.

## 5. Falsifiers

SPEC/10 §4. Test-only witnesses on every envelope from PR 2's merge:
`F10_1` (S1), `F10_2` (S4), `F10_3` (S1), `F10_4` (S1, S2), `F10_5` (S3).
Recorded in `caller` and read by row 10's cell: the live reading of the
four call records, festival-desk's answer record through the door and
refagent's envelope, at PR 3's run (PR 4's if the deploy path needs a
repair).

## 6. What M09 carried in

M09 wrote no `open.md`: its close gave every finding and Unsure item a
standing home in `milestones/M09/README.md`'s close detail, and those homes
stand. M10's inbox is that close detail's findings and Unsure tables and
nothing else. Checked against it:

| Item | Now |
|---|---|
| M09 finding 3 (the platform App on "selected repositories"; SPEC/06 §6 and the quickstart "at the next Product PR") | **Taken here under R7**: SPEC/06 §6 row 2 and the quickstart's step 0 corrected, naming the finding and Security's ruling that it stays "selected" |
| M09 finding 11 (the compliance map's stale "Claim 8 (M08): not opened" and no M09 row) | **Taken here under R7**: envelope E9 and row 35 added; the stale line replaced by two that name claims 7 to 10 as they stand |
| M09 finding 14 (ADR-0014's `status:` Proposed) | **Taken here under R7**: `Accepted`, 2026-10-11, the correction named on the line |
| M09 Unsure F (the public caller; R6) | **Taken as claim 10** (SPEC/00 §8 M10; ADR-0015) |
| M09 finding 12 (`docs/story.md` absent), finding 15 (the M08 header rows), finding 19 (the videos' ceilings) | Standing where M09's close put them; M10 touches none. SPEC/00 §15 as amended says `docs/story.md` stays absent unless Product writes it |
| M09 findings 1, 2, 4 to 10, 13, 16 to 18, 20 | Standing where M09's close put them; M10 repairs nothing M09 found (ADR-0015 decision 1). Finding 18 (festival-desk stays deployed) is what lets M10 reuse it as the agent the caller reaches |
| M09's video | Ruled not recorded at its close; nothing to carry. M10's is ruled not recorded here (SPEC/00 §10.5; ADR-0015 decision 6) |

## 7. What PR 1 does not do

No reader, no door, no pool, no workflow, no stack, no deploy, no grant,
no probe, no setting in GitHub or AWS, no change to a bar, a golden under
`evals/goldens/`, `src/baseline/`, any rule file, the manifest schema or
any manifest, and no change to `agentkeel-studio/festival-desk` from an
agentkeel session. It changes `src/verdict/plants.py` by the `SEEDS_M10`
list only, which reads nothing and gates nothing, and
`tests/test_cost_cap_and_ledger.py` by the row count (ten to eleven). Its
R7 housekeeping is four Product documents (SPEC/06 §6, the quickstart,
ADR-0014's status line, the compliance map), each a correction M09's close
named. `make validate`'s twenty-one checks pass.

## 8. The reviews of PR 1

**`product-spec-reviewer`**, on SPEC/10 at `053ee19`: 0 BLOCK, 9 FINDING,
3 NOTE (§1). Dispositions in §2.

**`tool-owner`** and **`engineering-cold-reviewer`**: run on the committed
diff before the PR opens; counts and dispositions in §2.5 and §2.6, the
reports in the PR body verbatim. No `security-reviewer`, `data-owner`,
`rule-owner` or `threshold-owner` report: PR 1 touches no `infra/`, no
workflow, no `evals/goldens/`, no `data/`, no rule file and no bar. The
`cold-review` skill runs from PR 2 (R9).
