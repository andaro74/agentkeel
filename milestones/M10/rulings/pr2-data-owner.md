---
# M10 PR 2 (#55), the Data Owner's key: R5, the call record's read shape and
# what a raw record may carry onto an envelope, read on the raw fixtures that
# carry both shapes. Those fixtures are Engineering's paths under CODEOWNERS
# (tests/); this file names them as the record of the shape this seat ruled
# on, and pr2-engineering.md covers them.
ruling: pr2-data-owner
seat: Data Owner
authorises:
  - tests/fixtures/m10/s1-call-records/raw/data_events.json
  - tests/fixtures/m10/s1-call-records/raw/access_log.json
  - tests/fixtures/m10/s1-call-records/raw/credential_leak.json
evidence:
  - SPEC/10-public-caller.md
  - milestones/M10/runs/door_probe.md
  - milestones/M10/rulings/pr1.md
  - tests/fixtures/README.md
pr: 55
---

# Ruling: M10 PR 2, Data Owner

Ruled by andaro74 as Data Owner, 2026-10-15, as written.

## R5. The call record's read shape

As proposed at PR 1: `subject`, `issuer`, `agent`, `outcome`, `reason`,
`request_id`, `time` (AWS's time of the call: the data event's `eventTime`,
the access-log line's `requestTimeEpoch`) and `delivered` (the object's
`LastModified`, never the observer's read time); no guardrail on a call
record. `reason` is one of four: `no identity`, `not admitted`, `not the
door`, and from this PR `the door failed` (a line with no authoriser
context that is not the API's own 401), or null. `outcome` is the door's:
admitted means the authoriser let the caller in, whether or not the agent
then answered. `src/verdict/caller.from_raw` maps each of the two raw
shapes (the access-log line; the data event) onto exactly those eight
fields; the raw record stays beside the read one on the envelope.

**What a raw record may carry onto an envelope** (this seat with Security,
on this PR's finding 1). `evals/history/` is public evidence. A record that
carries a credential is refused and never copied: a key is a credential's by
its words (`authorization`, `token`, `secret`, `password`, `cookie`,
`credential`, an API key, a signature, `x-amz-security`), but for the benign
few (`token_use`, `sessionCredentialFromConsole`), and a value by its shape
(a JWT, `Bearer`, `Basic`, `AWS4-HMAC-SHA256`); CloudTrail's own redaction is
not one. And the caller's address, user agent, key id, principal id,
session context and TLS details are **dropped** before a record is copied
by the observer and again before `build` records it, each drop named in the
wrapper (`DROPPED_KEYS`), so what reaches the envelope is what AWS delivered
less the named keys. The read shape needs none of them.

## From this seat's read of the PR (0 BLOCK, 3 FINDING, 9 NOTE)

| # | Disposition | Seat |
|---|---|---|
| F1 | **Repaired**: the drop list above, in the observer and in `build`, each drop named; held by `tests/test_m10_readers.py` | Security; Data Owner; Engineering |
| F2 | **Repaired**: the credential match by words and shapes, with the benign keys named; held by a test with a non-JWT value under an unlisted key | Data Owner; Engineering |
| F3 | **Repaired**: `no identity` only on the API's own 401 (its error set, no authoriser error); any other line with no authoriser context reads `the door failed`, which no stated call holds | Data Owner; Engineering |
| N (placeholder table) | **Repaired**: the table says what the fixture holds, and what is kept as the probe wrote it | Engineering |
| N (access_log.json's comment) | **Repaired**: names `door.py` and says the outer shape is the fixture's own | Engineering |
| N (reason enum) | **Repaired**: the schema's `read.reason` is the four values or null | Data Owner; Engineering |
| N (HIDDEN under a credential key) | **Repaired**: the test puts the redaction under `token` too | Engineering |
| N (outcome is the authoriser's) | **Repaired**: a sentence in SPEC/10 §2 and the module's docstring | Product; Data Owner |
| N (the bypass arm's N rests on CloudTrail's delivery, up to fifteen minutes) | **Recorded** in SPEC/10 §7 as a risk, not a reason to move N | Threshold Owner; Product |
| N (the answer record copied whole) | Recorded: `build` reads its pin, plant and block only | — |

### The report, verbatim

> Read: the diff a67de63...afd7f31 (the record's paths): `src/verdict/caller.py`, `src/verdict/schema.json` (the `caller` field), `scripts/observe_caller.py`, `tests/fixtures/m10/s1-call-records/raw/{access_log,credential_leak,data_events}.json`; and SPEC/10 §2 and §11 R5, `infra/construct/door.py` (ACCESS_LOG_FORMAT, the authoriser), `infra/security/app.py` (`_calls_delivery`), `tests/fixtures/README.md` (M10 section and placeholder table), `tests/test_m10_readers.py`, `tests/fixtures/m10/s1-call-records/calls_held.json`, `milestones/M10/runs/door_probe.md`.
>
> The prompt's golden and corpus checks (ids, weakening, checkable, overlap, traps, corpus admission): nothing under `evals/goldens/` or `data/` changes in this PR; nothing to read. Real IP: every name in the fixtures is fictional (`festival-desk`, `lantern-desk`, `box-office`, `probe-door`); nothing found.
>
> **Findings, one per line.**
>
> - FINDING. The raw record on the envelope carries what the fixture policy scrubbed. `caller.py:704-705` copies `wrapper.get("raw")` whole into `records[].raw`, and `schema.json` `raw` is `object|null` with no shape. The access-log line carries `ip` (`door.py:44`, `$context.identity.sourceIp`); the data event carries `sourceIPAddress`, `userAgent` (the laptop's OS, arch and Python versions), `userIdentity.accessKeyId`, `principalId`, `sessionContext`, `tlsDetails`. `tests/fixtures/README.md:412-423` replaced the account, the address and the key ids "before it reaches the repository"; `evals/history/` is in the repository and SPEC/10 §2 line 172 calls it public evidence. The first live envelope (PR 3's run) would carry the owner's real address and key id unscrubbed. Settle: a ruling naming the raw keys the observer drops before copying (propose `ip`, `sourceIPAddress`, `userAgent`, `userIdentity.accessKeyId`, `tlsDetails`, listed in the wrapper as `dropped: [...]` so "what AWS delivered less the named keys" stays checkable), or a ruling that they stay and why, before PR 3's run. Rules: Security (public evidence) with Data Owner (the record); Engineering carries.
> - FINDING. The credential refusal is narrower than R5 says. `caller.py:470` matches a key only when `str(key).lower()` is exactly one of `CREDENTIAL_KEYS` (line 421-422): `accessKeyId`, `sessionToken`, `secretAccessKey`, `x-api-key`, `apikey`, `userToken`, `bearer` all pass the key check, and the value check (line 476) catches only a JWT-shaped string. A SigV4 `Authorization` value (`AWS4-HMAC-SHA256 Credential=...Signature=...`) is caught by its key; an opaque Cognito refresh token or an API key under an unlisted key is not. Settle: substring match on `token`, `secret`, `authorization`, `password`, `cookie`, `credential`, `signature`, plus a test with a non-JWT value under an unlisted key. Rules: Data Owner (R5's definition); Engineering carries.
> - FINDING. The access-log reading cannot tell the no-token 401 from an authoriser failure. `caller.py:521-526`: `outcome` absent and status not 2xx reads `refused`; `reason` absent and `subject` None reads `no identity`. An authoriser crash (JWKS fetch timeout, a 500, `$context.authorizer.error` set) writes the same `-` in `subject`, `issuer`, `outcome`, `reason`, and reads as the no-identity refusal; `auth_error` and `error` are in the line and not read. In the live run the `none` step would hold on a broken door. Settle: `no identity` only when status is 401 and `auth_error` is absent; otherwise the record's reason reads the API's `error`, which `calls()` line 622 then does not hold. Rules: Data Owner (the read shape); Engineering carries.
> - NOTE. Worked by hand, check 3 holds. Access-log admitted line: `time_epoch_ms` 1792490400000 = 2026-10-20T10:00:00Z (1767225600 + 292 days + 10 h), `delivered` 10:04:20 = 260 s; the no-token line 10:01:00 = 200 s (test line 192); the stranger line 10:02:00 = 140 s. Data-event stranger: `eventTime` 14:21:49, `last_modified` 14:26:47 = 298 s (test line 171). `time` is `eventTime` (`caller.py:509`) or `requestTimeEpoch` (line 529); `delivered` is the wrapper's `last_modified`, which `observe_caller.py:211` writes from S3 `LastModified`; `looked_up_at` (`observe_caller.py:331`) never feeds `delivered`. Held.
> - NOTE. Check 1 holds: `_read_data_event` (`caller.py:507-509`) and `_read_access_log` (lines 527-529) each write exactly the eight fields; `schema.json` `read` is `additionalProperties: false` with the eight required; no guardrail field on a call record. Check 2's HIDDEN case holds: `caller.py:470` and `476` exempt `HIDDEN_DUE_TO_SECURITY_REASONS`; `observe_caller.py:246-252` writes `raw: null` and the key path, never the value.
> - NOTE. The placeholder table and the fixture do not match. The table (`README.md:424-426`) lists `us-west-2_0therp00l`, `ca11ersc1ient…`, `wr0ngc1ient…` and `…b0b1` as "In the fixture"; none appears there (the stranger's and wrong-client's events carry no claims, `door_probe.md:61-65`). The fixture carries values not in the table: the role name `probe-door-bypass`, the runtime name `probe_door_agent`, the trail object suffix `bndt3mMSZpEcbfrN` and stamp `20261014T1425Z`, the two user agents. None looks real; the account, address, key ids, pool, client, subs, request and event ids are all placeholders as the table says. Settle: the table corrected to what the fixture holds. Rules: Engineering (`tests/fixtures/`).
> - NOTE. `access_log.json` `_comment` names `infra/construct/governed_agent.py` for ACCESS_LOG_FORMAT; the constant is `infra/construct/door.py:42`. The line's fifteen keys match the format's fifteen in order; the `-` for absent values, the 401 with `error: Unauthorized` and the stranger's claimed subject and issuer match the authoriser (`door.py:69-91`) and API Gateway's behaviour as `door.py:25-27` describes it. What a reader could mistake it for: the file's outer `{key, last_modified, lines}` is the test's wrapper, not the object's bytes (newline-delimited lines, `infra/security/app.py:436-439`, as the test builds them at line 381) and not the observer's per-line wrapper (`source, key, last_modified, step, raw, error`). The comment says hand-written before any door is deployed and that PR 3's first live object shows the shape; it should also say the outer shape is the test's. Rules: Engineering.
> - NOTE. `schema.json` `read.reason` is any string or null; SPEC/10 §2 line 180-181 fixes three values (`no identity`, `not admitted`, `not the door`). The authoriser writes only those or `-`. Tighten to the enum so a future authoriser edit that changes the vocabulary fails validation rather than reading as a new reason. Rules: Data Owner proposes; Engineering carries.
> - NOTE. The HIDDEN test (`test_m10_readers.py:209`) puts `HIDDEN_DUE_TO_SECURITY_REASONS` under `userToken`, which is not in `CREDENTIAL_KEYS`, so it proves the value exemption, not the key exemption at `caller.py:470`. Add `token: HIDDEN` to the case. Rules: Engineering.
> - NOTE. `outcome: admitted` is the authoriser's, not the integration's: a call admitted and then failed at the proxy (status 502, `integration_status` 5xx) reads `admitted` (`caller.py:521`). Right for F10.1, F10.3 and F10.4, which read who was let in, not whether the agent answered; one sentence in SPEC/10 §2 or the docstring would stop a reader expecting otherwise. Rules: Product (SPEC) with Data Owner.
> - NOTE. The bypass arm is held to N by CloudTrail's delivery: 296-299 s in the probe, half of N; AWS documents up to 15 min. `calls()` lines 607-614 read a bypass refusal delivered after 600 s as not held (F10.4). A risk of the design, not a defect of the shape; SPEC/10 §7 should name it if it does not. Rules: Threshold Owner (N) and Product.
> - NOTE. `observe_caller.py:302-304` copies the deploy's answer record whole with no `refuse_credential`; `record()` reads only its pin, plant and blocked (`caller.py:639-660`), so nothing of it reaches the envelope. Stated; nothing to settle.
>
> BLOCK: 0 · FINDING: 3 · NOTE: 9
