---
# M10 PR 2 (#55), the measure. Product's key over the Product paths this PR
# touches: SPEC/00 section 8's M10 item 2, SPEC/10's amendments on the probe,
# ADR-0016, the two developer documents, the explainer's engineer rows, the
# ledger's header row, the plain ledger, this milestone's README, the probe's
# record and the five ruling files. Security's file is pr2-security.md (R2,
# R3); the Tool Owner's is pr2-tool-owner.md (R4, ADR-0016's key, the two
# manifests); the Data Owner's is pr2-data-owner.md (R5); Engineering's (with
# the cold review) is pr2-engineering.md. R6 is ruled here: it touches no
# path.
ruling: pr2
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/10-public-caller.md
  - docs/adr/ADR-0016-two-keys-on-a-caller-admitted.md
  - docs/developer/quickstart.md
  - docs/developer/template-README.md
  - docs/milestones/M10.md
  - docs/milestones/README.md
  - milestones/README.md
  - milestones/M10/**
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/runs/door_probe.md
  - milestones/M10/feasibility.md
  - milestones/M10/rulings/pr1.md
  - docs/adr/ADR-0015-the-public-caller-an-eleventh-milestone.md
  - docs/adr/ADR-0016-two-keys-on-a-caller-admitted.md
pr: 55
---

# Ruling: M10 PR 2, Product

DRAFT. Ruled by: pending.

## What this PR is

PR 2 of M10, the measure: 2 of 4. The gate that reads the plant. Every
reader SPEC/10 §6 names is in the tree, each landed in the commit that
took its seed's marker off (`milestones/M10/README.md`, "Measure detail"),
and on this PR's own envelope `caller` reads unread, so row 10's reading
is RED: the plant going RED under the measurement, which PR 2 is for. The
rulings decided before it opened (R2 to R6 and ADR-0016, 2026-10-15, after
Security's probe) are written as this PR's five ruling files; each is a
draft until it reads "Ruled by".

## Rulings put to Product

1. **R2 is door 2 in the hybrid form, and SPEC/10 and SPEC/00 say so.**
   Security's probe answered door 1's unknowns (`runs/door_probe.md`): a
   SigV4 call is refused in JWT mode (a, yes); an admitted call's data
   event names the token's `sub` and a refused call's names no one (b,
   partly); the stranger's refusal is recorded in 298 s naming no caller
   and the no-token refusal is recorded nowhere (c, partly). Door 1 alone
   fails F10.3 on the stranger and F10.4's record arm on the no-token
   call. The ruling is Security's (`pr2-security.md`); Product's part is
   the amendment: SPEC/10's status line, §2's door table, §4 F10.1 and
   F10.4, §5.1, §6 rows 3, 4, 5, 7 and 8, §7's risks, §8 and §11 R2 and R3;
   SPEC/00 §8 M10 item 2 says the same, and SPEC/00 wins.
2. **The brief's reading of (b) is corrected, not the decision.** The
   session's brief read (b) as "written nowhere"; the probe's own file
   shows the admitted call's claims on the data event. `door_probe.md`
   says PARTLY with the claims listed, and the fixture carries them.
3. **ADR-0016, entry 7 of the closed list**, proposed: a subject added to
   `callers` or the key removed from a value is two keys; absent to `[]`
   and a subject removed are not; the Tool Owner's file covers and any
   second seat names; the construct's authoriser widened stays Security's
   under `ruling-cited`. Keyed at this PR by the Tool Owner
   (`pr2-tool-owner.md`). A new ADR, since ADR-0009's last amendment is the
   Rule Owner's.
4. **R6: N is `detection.max_seconds`, 600 s, reused.** No bar is added
   and none moved; `thresholds.yaml` is not in the diff. `build` reads it
   at the run, the gate reads it again at the envelope's commit, and a
   mismatch is a miss (`gate.caller_misses`). The Threshold Owner's ruling,
   recorded here because it touches no path.
5. **The quickstart and the template README say what `callers` is**, that
   `[]` is the default, how a caller gets in, and that the first door has
   not been deployed for any agent yet: what the door is meant to do, not
   what it has done.
6. **The ledger's header row for M10 PR 2**: twenty-one checks, none new,
   two reading more, with what `validate` still does not read. Written as
   the brief asked.
7. **The explainer's engineer rows** say the check landed; "What
   happened" stays empty until the close. The Watch line is unchanged: no
   recording, by ruling 6 of PR 1.
8. **The by-hand steps before PR 3's run** are named in this milestone's
   README with the pull request each must precede: the security stack and
   the bootstrap deployed before festival-desk's deploy, since the
   construct's subscription names a destination that must exist; the
   callers pull request; the credential; the four calls, each stated in
   the run file first.

## Unsure, each with its seat and when

| # | Item | Seat | By |
|---|---|---|---|
| A | Whether the HTTP API's access log records a request its authoriser refused with the authoriser's context (the stranger named), and a request with no token (the API's own 401 with its request id). Unprobed: door 1 had no API. If the stranger's line names no subject, F10.3 fires; if the no-token line is missing or late, F10.4 fires on the record arm; row 10 closes RED on whichever. Named first in SPEC/10 §7 | Security; Product (the cell's wording) | festival-desk's deploy and PR 3's run |
| B | Whether the Logs subscription's delivery (the destination, the Firehose with decompression, message extraction and dynamic partitioning on `agent`) lands under `calls/agents/<name>/` within N. The observer reads both the partitioned shape and a batch left whole; a line under `calls/errors/` is a miss the cell names | Security | the security stack's deploy, before festival-desk's |
| C | The door's two Lambdas run outside the platform VPC: the pool's token endpoint and the runtime's bearer endpoint are public service endpoints the VPC has no way to. Stated in the construct; whether that is the shape Security keeps, or a VPC with endpoints for both | Security | before PR 3, or standing |
| D | The brief said REST "for access logging to Firehose"; the API is an HTTP API, since the delivery goes by a Logs subscription (no account-level CloudWatch role, no Firehose in the platform account, fewer resources). Recorded as a departure from the brief's parenthesis with its reason | Security | this PR |
| E | The deploy's goldens step mints the door client's token itself and presents it at the API, admitted as `platform` by the authoriser; the secret is read from Cognito and stored nowhere (Unsure I of PR 1 answered as proposed at the stop of 2026-10-15) | Security | this PR |
| F | `make plants` says "in the tree" beside the run too, since `scripts/observe_caller.py` exists; the run's marker stays on and `--runxfail` names it. The brief expected "not in the tree yet" for the run; the listing reads file presence, as it did at M09 PR 2 | Engineering | recorded |
| G | The access-log fixture is hand-written in the construct's format before any door is deployed; PR 3's first live object is what shows the shape. A line that differs is a reader repair in PR 3, not a finding of the claim | Data Owner; Engineering | PR 3 |
| H | The data event's `sub` is a pool user's UUID, not a name; under the hybrid the admitted record is the access-log line (the username the authoriser verified), and the data event is read for the bypass arm only. Cut 3 (the record names the client) is not taken | Product; Data Owner | recorded |
| I | The bootstrap's execution role gains a policy of its own for the door's grants (`agentkeel-cfn-exec-door`): its default policy was at the size CloudFormation takes for one document, and the overflow document CDK makes cannot carry a cdk-nag reason by path. The pool's id is the service's, so its grants are on `userpool/*`; CreateUserPool takes no resource and is held to the agent tag | Security | this PR |
| J | The agent ceiling gains one action, `cognito-idp:DescribeUserPoolClient`, so the proxy may read the door client's secret on its own pool; the construct grants it on that pool alone, and no agent role's own policy allows it. A ceiling widened, as M05's put was | Security | this PR |
| K | The three log groups and the subscription are retained (the deploy boundary denies `logs:Delete*` flat), so a retired agent's stack keeps them; the construct never calls a delete | Security | recorded |
| L | A test and a seed patch of earlier milestones read refagent's manifest's shape (M02 S3's patch context, the M09 deploy-layout test); each follows the manifest as it now stands, and neither seed changed | Engineering | this PR |

## What a reader can run

See `milestones/M10/README.md`, "What a reader can run, at PR 2".
