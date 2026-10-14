---
adr: ADR-0015
title: The public caller; an eleventh milestone after the tenth; M10 records no video
status: Proposed
date: 2026-10-13
seat: Product
authorises:
  - Product  # SPEC/00 §3 a threat row, §7 row 10, §8's count and its M10 entry, §10.3 row 10, §10.5 (no recording), §15: a milestone after "the last", again
  - Tool Owner  # `callers`, a manifest field that says who may call an agent (SPEC/00 §5's Tool Owner row); a subject added is two keys with Security's (ADR-0009 amendment 2, at PR 2)
  - Security  # the door and the identity pool in the construct, the deploy step's token, the call record's delivery (SPEC/10 §11 R2, R3), ruled at PR 2
amendments: 0
---

# ADR-0015 — The public caller: an eleventh milestone after the tenth

Proposed by the session at M10 PR 1 and put to Product
(`milestones/M10/rulings/pr1.md`). Accepted when that ruling reads
"Ruled by", on `main` at the merge commit of M10 PR 1 (ADR-0008).

## Context

Four things stand in the tree at `833ab2b` (tag `m09`):

- **An agent is reached only by the platform.** Its runtime answers any
  IAM principal in the platform account that holds
  `bedrock-agentcore:InvokeAgentRuntime` on it: the deploy role for its
  goldens (`infra/bootstrap/app.py`, `CallTheRuntimeItJustDeployed`),
  the eval role for refagent's (`InvokeRefagentRuntimeOnly`), the owner
  by hand (M08's drill). `src/agent/run.py`'s `invoke_deployed` sends an
  ARN and a payload and nothing about who is calling. No principal
  outside the account is granted anything.
- **No record names who called.** The answer record `build` writes
  (`compose_answer`) has no caller field and is written once per deploy;
  the audit bucket's attempt records are CloudTrail's events for IAM
  principals.
- **No manifest field says who may call.** `may_call` and
  `may_be_called_by` are agent edges, empty everywhere;
  `src/manifest/schema.json` refuses any other key.
- **"The public caller" is named and never defined.** SPEC/05 S4 named
  it ("a caller lying about its depth: Identity, M07"); SPEC/00 §12
  shelved "credentials only via Identity" at M07 PR 1; SPEC/09 §11 R6
  ruled at M09 PR 2 that it is "M10, its own claim, opened only by a
  Product ruling, not folded into row 9"; SPEC/00 §10.5 said "SPEC/00
  plans no M10". Nothing was ever planted for it.

## Decision

1. **M10 is opened, after M09's close, by a Product ruling.** It is not
   a finding of M09 and reopens none of M09's rows; M09's close detail,
   its twenty findings' homes and its tag stand. SPEC/00's count becomes
   eleven milestones and at most 44 PRs. M10 takes the public caller and
   nothing else. **This ADR does not amend ADR-0014:** M09 built one
   control and that stays true of M09. M10 is a different milestone and
   builds one control, under its own claim, measured on its own seeded
   case before any document calls it working (SPEC/00 §10.5). A pull
   request of M10 that repairs an M09 finding under this ADR contradicts
   it; the ruling to cite for that does not exist.
2. **The public caller is defined** (SPEC/10 §2): a principal that is not
   the platform and not an agent, holding an identity the door issues and
   no AWS credential. A second IAM principal in the platform account is
   not outside. The owner's laptop principal is never presented as the
   caller.
3. **A manifest says who may call its agent**, in a field a seat owns:
   `callers` (Tool Owner), a list of `{subject, issuer}`; `callers: []`
   admits no outside caller and is the default; a manifest with no
   `callers` key is refused by the platform check from PR 2. A subject
   added, the key removed or the door widened is a relaxation: ADR-0009
   amendment 2, its last, at PR 2, keyed by the Tool Owner and Security.
   SPEC/00 §5's Tool Owner row carries the field from this PR.
4. **One door per agent, which the platform controls, and which Security
   rules** (SPEC/10 §11 R2). Proposed: the runtime's own JWT authoriser
   on an identity pool the agent's own stack deploys, so a call signed as
   an IAM principal no longer reaches a doored runtime and the only way
   in is a token the pool issued; the platform's own goldens caller
   presents a token too, as a `platform` client. The alternatives and
   their costs are SPEC/10 §2's. The guardrail stays where it is, on the
   agent role's model call inside the runtime (M03 PR 2, M09 PR 2); the
   door is in front of the runtime and cannot take it off.
5. **Every call leaves one record in the security account**, written by
   the door's delivery and never by the agent, the observer or a person;
   `build` reads it into the envelope's `caller` field; row 10's cell
   reads that field; the gate rules nothing on it. A refused call's
   record arrives within N, `detection.max_seconds` (600 s), reused from
   M05 and not moved. **A bypass, an answered stranger or an unrecorded
   refusal stops no merge at M10.**
6. **M10 records no video.** Product's ruling at M10 PR 1
   (`milestones/M10/rulings/pr1.md`), for the reason M09's close gave:
   no gate, no `validate` check, no envelope and no ledger cell reads a
   recording, and the evidence for row 10 is the CI-written envelope its
   Measured cell will name. ADR-0005 has no amendment left (its second,
   at M09 PR 4, was its last), so the rule lives here. SPEC/00 §10.5's
   sentence and §15's video clause ("nine videos; M09's and M10's ruled
   not recorded, not moved to fit") are written at this PR; the
   explainer's Watch line reads "No recording" from its draft;
   `docs/video/README.md` gets its M10 row at the close. SPEC/00 plans no
   M11.

## How this stands beside ADR-0014 and SPEC/00 §12

- **ADR-0014** opened a tenth milestone after "the last" by a Product
  ruling and said M09 builds one control. Both stay true of M09. M10 is
  opened the same way, for one item ADR-0014 itself named as M10's
  (decision 6: "the public caller is proposed as M10, with a claim of
  its own"). It repairs nothing M09 found: M09's standing items keep
  their homes, and the four Product housekeeping items M10 PR 1 carries
  (SPEC/06 §6's "selected repositories", ADR-0014's status line, the
  compliance map's M09 row and its stale claim-8 line) are M09's close
  detail's own instructions to "the next Product PR", not repairs of a
  falsifier.
- **SPEC/00 §12** names the AgentCore Gateway, "credentials only via
  Identity" and the per-agent Budgets filter as not built. The proposed
  door is none of them: the runtime's authoriser is a property of the
  runtime the construct already makes, and a Cognito pool is not
  AgentCore Identity's credential vault. §12 is not amended at PR 1. If
  Security rules door 3 (the Gateway) at R2, §12's gateway line is
  amended at PR 2 under that ruling and the cost is named there.
- **ADR-0009** gains its second and last amendment at PR 2, not here: the
  entry is read by `two_key.py` from PR 2, and its seeded case (S3) is
  planted at PR 1 before the reader.

## Consequences

- Row 10 is measured: the live run's calls, admitted n of n and refused
  m of m, each on the record within N, with F10.1 to F10.5 held. Expected
  admitted 1 of 1, refused 3 of 3 (SPEC/10 §7), with the record arm named
  as the risk most likely to close the row RED.
- refagent is not behind a door at M10; its `callers` is `[]` and its
  runtime keeps IAM authorisation, so `make evals` and the swap runs are
  unchanged. Its envelope's 7 of 7 is the guard that the construct change
  relaxed nothing (F10.2).
- Every agent with callers is one more Cognito user pool and two app
  clients in the platform account, in the agent's own stack, retained as
  the agent's guardrail is; a user's first credential is set by hand.
- `deploy.yml`'s goldens step presents a token for a doored agent
  (Security, PR 2); until it does, the first deploy of a doored agent
  fails its goldens step, which SPEC/10 §7 names so it is not found at
  the deploy.
- SPEC/00 §15's clauses M09's close read as not met are re-read at M10's
  close over eleven rows and moved to fit nothing (SPEC/00 §15 as amended
  at this PR). "At least seven are GREEN" is unreachable at M10 too.
