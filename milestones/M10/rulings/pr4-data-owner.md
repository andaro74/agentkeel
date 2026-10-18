---
# M10 PR 4 (#57), the close. The Data Owner's key, in words, over the
# rulings put to this seat and carried to the first live records: R5 (the
# read record's shape and what a raw record may carry onto an envelope,
# pr1.md D, pr2.md M, pr2-data-owner.md F1), the access-log fixture against
# the live line (pr2.md G), and the goldens untouched. This seat owns no
# path in this diff: nothing under evals/goldens/ or data/ changed in M10.
# The one path listed is this file, which Product's pr4.md carries for the
# gate; the key is given here.
ruling: pr4-data-owner
seat: Data Owner
authorises:
  - milestones/M10/rulings/pr4-data-owner.md
evidence:
  - SPEC/10-public-caller.md#2-words-used-here
  - SPEC/10-public-caller.md#11-read-before-PR-2
  - evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json
  - https://github.com/andaro74/agentkeel/actions/runs/39143365127
  - milestones/M10/rulings/pr2-data-owner.md
  - milestones/M10/rulings/pr2.md
pr: 57
---

# Ruling: M10 PR 4, Data Owner

DRAFT, written by the session on 2026-10-18 for the owner to rule as the
Data Owner.

## R5 on the first live records: what reached the envelope

The envelope for `14ab792` carries five raw records and their read shapes,
mapped by `build`'s `from_raw` after the observer's drop (`DROPPED_KEYS`,
PR 2's F1): the four stated steps and the platform's own test call of
03:13Z (`step: null`, counted for nothing by `calls`).

| Record | Source | Dropped | What stayed, and whether it belongs on public evidence |
|---|---|---|---|
| platform (03:13:30Z), admitted (03:32:31Z), none (03:32:49Z), stranger (03:33:16Z) | the door's access log, one line each | `ip` | fourteen fixed fields: `source`, `agent`, `request_id`, `time_epoch_ms`, `status`, `method`, `path` (`POST /invocations`, the route, no query), `error`, `auth_error`, `subject`, `issuer`, `outcome`, `reason`, `integration_status`. No credential, address, user agent, key id, principal id, session or TLS detail. Each belongs |
| bypass (03:33:47Z) | the runtime's `InvokeAgentRuntime` data event in the platform trail | `sourceIPAddress`, `tlsDetails`, `userAgent`, `userIdentity.accessKeyId`, `userIdentity.principalId`, `userIdentity.sessionContext` (which took `sessionIssuer.arn`, `creationDate`, `mfaAuthenticated` with it) | `userIdentity.{type, arn, accountId}`, `eventTime`, `eventSource`, `eventName`, `awsRegion`, `errorCode` (`AccessDenied`), `errorMessage` (AWS's text), `requestParameters` and `responseElements` (null), `requestID`, `eventID`, `readOnly`, `resources[]` (the runtime ARN, from which `agent` is derived), `eventType`, `managementEvent`, `recipientAccountId`, `eventCategory`. The role ARN is the stated bypass principal, on the envelope by design (the run file names it). Each belongs |

The two issuer URLs carry two pool ids, the agent's (`us-west-2_f8kyzKF0P`)
and the stranger's throwaway (`us-west-2_rXaZjWjO5`); a pool id is an
identifier whose key set is public by design, and `issuer` is a field of
R5's shape. **On these five records the drop list is whole**: the access
log's one field in R5's category (`ip`) was dropped, and the data event's six
dropped keys are the whole of R5's list present in it. Nothing joins
`DROPPED_KEYS` on this evidence, and nothing dropped need have stayed.

**One finding, standing (data-owner F1 on this PR).** The bypass's
`userIdentity.arn` is kept by design, and an assumed-role ARN's session name
is free text: a federated or SSO principal writes a person's name or
address there. Tonight's `assumed-role/m10-bypass/m10-bypass` names nobody,
so nothing leaked; the design rests on the owner choosing a neutral session
name, which no file states. The sentence belongs in SPEC/10 §2 "The call
record" (Product, with Security): the bypass principal's session name names
no person, and a record naming one is the owner's to re-run, not the
observer's to copy. Not written at a close.

**Two shapes this run did not produce** are unmeasured (data-owner note):
an admitted SigV4 data event with non-null `requestParameters` and
`responseElements`, and a token call made straight at the runtime whose
`additionalEventData.jwt.claims` carries the whole claim set. `redact`
matches key names exactly, so a renamed field would pass it. A line for
SPEC/10 §8, Product; nothing for the close.

## The read shape, record by record

Each live record maps onto R5's shape as `from_raw` was written to map it,
checked by hand from the epochs (2026-10-18T00:00:00Z is 1792281600):
`1792294351` is 03:32:31Z (admitted), `1792294369` 03:32:49Z (none),
`1792294396` 03:33:16Z (stranger), each equal to the record's `time`; the
reader reads the HTTP API's seconds by their size (PR 3's repair, pr3.md
Unsure H). Delivered minus time: admitted 96 s, none 78 s, stranger 107 s,
bypass 235 s (03:33:47Z to 03:37:42Z), the platform call 92 s; each under
600. The no-token line (`status 401`, `error Unauthorized`, no authoriser
context) reads `no identity`, PR 2's F3 rule; the stranger's line is the
authoriser's own `refused`, `not admitted`, issuer the other pool; the
bypass reads subject the role ARN, issuer null, `refused`, `not the door`
from `errorCode AccessDenied`, agent `festival-desk` from the runtime ARN
`agentkeel_festival_desk-379Sz3GgxZ`; the admitted line's subject
`lantern-desk` is the run file's stated subject and the manifest's one
caller at `#4`'s merge (`F10_4.manifest_callers`).

**pr2.md G, the hand-written fixture against the live line.** The live
line's shape matched the fixture's but for the epoch's unit, repaired at
PR 3 as a reader repair, not a finding of the claim, as G said it would be.

## Where the stated caller comes from (cold review F3 on PR 1, held)

The observer derives `stated` from the run file's `steps[].caller` and
`observed.bypass.principal` and nothing else; `calls` compares each
record's subject with the stated one; the step of each record is set by the
owner's request id. All five live records carried the observer's step, so
the pairing fallbacks by subject in `_step_of` did not run. A test that a
line with a request id in no `observed` entry is not held for the step its
subject names is Engineering's, after the close (data-owner note; `pr4-engineering.md`).

## Goldens and data

`git diff --stat m09 HEAD -- evals/goldens data thresholds.yaml src/baseline
rules agents/refagent/rules` is empty (run by the session on 2026-10-18;
pasted in the PR body). `g-030` is as `02db54e` planted it and was blocked
through the door on deploy run 39076739413's answer record (`F10_2`:
`at8e36cosq1r:1`, `blocked: true`). No golden id was renamed or retired;
nothing entered the corpus in M10. The names on the records
(`festival-desk`, `lantern-desk`, `stranger`, `platform`, `m10-bypass`) are
made up; no real person.

## Seat report: data-owner on PR 4 (verbatim)

Dispositions: F1 standing, named above (SPEC/10 §2, Product with
Security); the throwaway pool's deletion is `pr4.md`'s Unsure (the owner's
word); the two unproduced shapes are SPEC/10 §8's line, Product; the
`_step_of` fallback test is Engineering's; the goldens diff was run and is
empty.

> Data Owner read, M10 PR 4 (the close), branch m10-pr4. A report, never a ruling.
>
> Read: `evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json` lines 593-828 (`caller`, five records); `src/verdict/caller.py` (DROPPED_KEYS 71, redact 142-160, refuse_credential 122-134, from_raw 224-239, _read_access_log 195-221, _read_data_event 174-192, _step_of 245-255, calls 258-328, record 366-436); `scripts/observe_caller.py` (stated_from 112-128, wrap 240-251, read_bucket 254-300); `SPEC/10-public-caller.md` §2 lines 165-199 and §11 R5 lines 659-668; `milestones/M10/rulings/pr2-data-owner.md`; `milestones/M10/runs/f10_x_caller_run.yaml`; `src/verdict/schema.json` lines 902-1004; `milestones/M10/README.md` lines 304-330.
>
> **A. What reached the envelope.**
> - NOTE. Access-log `raw` (four records) keeps exactly fourteen keys: source, agent, request_id, time_epoch_ms, status, method, path, error, auth_error, subject, issuer, outcome, reason, integration_status; `ip` dropped. None is a credential, address, user agent, key id, principal id, session or TLS detail. `path` is `POST /invocations` (route only, no query string); `error`/`auth_error` are `Unauthorized`/`Forbidden`/`-`; `integration_status` is `200`/`-`; request ids are API Gateway's opaque ids and already in the run file lines 76-78. All belong on public evidence.
> - NOTE. Bypass `raw` keeps: eventVersion, userIdentity{type, arn, accountId}, eventTime, eventSource, eventName, awsRegion, errorCode, errorMessage, requestParameters null, responseElements null, requestID, eventID, readOnly, resources[{accountId, type, ARN}], eventType, managementEvent, recipientAccountId, eventCategory; six keys dropped (envelope lines 789-796). `userIdentity.arn` is the stated bypass principal (run file line 79), the read `subject` F10.3 is held on; it belongs. The runtime ARN is what `agent_of` (caller.py 166-171) derives `agent` from, so the read is checkable from it; runtime ARNs are already an envelope field (`runtime_arn`, schema line 245). The account id 581208540944 is on 99 files already (`agents/refagent/manifest.yaml`, every runtime envelope). `eventID` is CloudTrail's event uuid, an identifier with no reading use; harmless. `errorMessage` is AWS's text. Nothing is a credential.
> - NOTE. Issuer URLs carry two pool ids: `us-west-2_f8kyzKF0P` (the agent's pool) and `us-west-2_rXaZjWjO5` (the stranger's throwaway). A pool id is an identifier whose JWKS is public by design and `issuer` is a field of R5's read shape; it belongs. Run file line 43 says the throwaway pool is deleted after the run; `observed` records no deletion. Settle: one line in the PR body or the run file's observed saying the pool `us-west-2_rXaZjWjO5` was deleted and when. Security rules; Product's file.
> - FINDING. The bypass's `userIdentity.arn` is kept by design, and an assumed-role ARN's session name is free text: an SSO or federated principal writes a person's name or email there (`assumed-role/<role>/user@domain`). Tonight's `m10-bypass/m10-bypass` names nobody, so nothing leaked; the design rests on the owner choosing a neutral session name, which no file states. Settle: a sentence in SPEC/10 §2 "The call record" (or the run file's bypass step comment) that the bypass principal's session name names no person, and that a record naming one is the owner's to re-run, not the observer's to copy. Product (SPEC) with Security; Data Owner concurs. Not a BLOCK: no live field carries a person.
>
> **B. Is the drop list whole?**
> - NOTE. On these five records, yes for the two shapes as deployed: the access-log format is fifteen fixed fields (`door.py` ACCESS_LOG_FORMAT) and the only one in R5's category, `ip`, was dropped; the data event's six dropped keys are the whole of R5's list present in it (`sessionContext` took `sessionIssuer.arn`, `creationDate`, `mfaAuthenticated` with it). Nothing should join DROPPED_KEYS on this evidence; nothing dropped need have stayed, each is in R5's named list (pr2-data-owner.md lines 46-50).
> - NOTE. Two shapes this run did not produce are unmeasured: an admitted SigV4 data event with non-null `requestParameters`/`responseElements`, and a token call straight at the runtime whose `additionalEventData.jwt.claims` carries the whole claim set. `redact` matches key names exactly (caller.py 151), so a renamed field (`sourceIpAddress`) would pass. Settle: none for the close; a line in SPEC/10 §8 (controls with no seeded case) naming the two unproduced shapes. Product.
>
> **C. The read shape.** Worked by hand; each record maps faithfully.
> - NOTE. Epoch check: 2026-10-18T00:00:00Z = 1792281600 (1767225600 + 290 d). `1792293210` = +11610 s = 03:13:30Z (platform); `1792294351` = 03:32:31Z (admitted); `1792294369` = 03:32:49Z (none); `1792294396` = 03:33:16Z (stranger); each equals the record's `time`. Latencies to `delivered`: 92, 96, 78, 107 s; bypass 03:33:47Z to 03:37:42Z = 235 s. All under 600.
> - NOTE. none: status 401, `error: Unauthorized`, `auth_error: -`, `subject: -` reads `no identity` by caller.py 212-214 as PR 2 F3 required; stated subject null (stated_from 125-126) equals read null. stranger: the authoriser's own `outcome refused`, `reason not admitted`, issuer the other pool. bypass: AssumedRole branch (182-183) gives subject the ARN and issuer null; `errorCode AccessDenied` gives `refused`, `not the door`; `agentkeel_festival_desk-379Sz3GgxZ` → `festival-desk`. admitted: subject lantern-desk is the stated subject (run file line 35) and the manifest's one caller (envelope lines 821-826).
> - NOTE. The platform record has `step: null`, so `record()` line 412 filters it out before `calls`; the `PLATFORM` branch at 279-282 never sees observer input and is reached only by a test. Counted for nothing either way. Nothing to settle; Engineering may note the dead branch.
>
> **D. Where the stated caller comes from.**
> - NOTE. One source held: `stated_from` (observe_caller.py 112-128) reads `steps[].caller` and `observed.bypass.principal`; `calls` compares the record's subject to `expected.subject` (caller.py 294, 313). The step of each record is set by the observer from `observed.<step>.request_id` (259, 268, 292), the owner's keys. All five live records carried the observer's step, so `_step_of`'s fallbacks (250-255) did not run.
> - NOTE. Those fallbacks pair a record to a step by the record's own subject when its request id matched none; the name still comes from the run file, but a record of an unmatched request id with the right subject would then hold F10.3 by construction. Not on this evidence. Settle: a test that an access-log line with a request id in no `observed` entry is not held for the step its subject names. Engineering, after the close.
>
> **E. Goldens and data.**
> - NOTE. This seat had no shell in this run and did not execute `git diff --stat m09 HEAD -- evals/goldens data`. README lines 311 and 328 and pr2-engineering.md line 145 record the diff empty at PR 1 and PR 2; the branch's git status shows nothing under `evals/goldens/` or `data/`; g-001 to g-021 are all present (no id missing or renamed); the envelope's `goldens` block is M09's set. Settle: the caller runs the command and pastes its (empty) output into the PR body. Data Owner rules.
> - NOTE. Real IP: `festival-desk`, `lantern-desk`, `stranger`, `platform`, `m10-bypass`; none real. Corpus admission: nothing enters the corpus in M10.
>
> BLOCK: 0 · FINDING: 1 · NOTE: 12
