---
# M10 PR 3 (#56), the repair. Product's key over the Product paths this PR
# touches: this milestone's README (the repair detail, the by-hand step it
# changes) and the three ruling files. Security's file is pr3-security.md;
# Engineering's (with the cold review) is pr3-engineering.md.
ruling: pr3
seat: Product
authorises:
  - milestones/M10/**
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/README.md
  - milestones/M10/rulings/pr2.md
pr: 56
---

# Ruling: M10 PR 3, Product

DRAFT. Ruled by: pending.

## Which PR this is, and why

PR 2's merge (`917601d`) could not put the door on: the platform's own
deploy path was refused five times, in five places, before festival-desk's
door stood on 2026-10-17 (deploy run 39076739413), and its records did not
reach the security account until the sixth repair. SPEC/10 §5.1 and this
milestone's README say what follows: PR 3 is that repair, and PR 4's run
reads the calls. PR 4 is the close. A further deploy-path repair after this
PR merges would be a fifth PR and a RED close; none is known.

The four calls were made on 2026-10-18 after the repairs stood, each as the
run file states it. Their request ids, the callers pull request (#4), the
deploy run and its answer record's key enter the run file's `observed` in
PR 4, and nothing about their outcome is written here: the run is read by
the observer and `build`, not by this file.

## Unsure

| | What | Seat | When |
|---|---|---|---|
| A | PR 2's Unsure A (whether the access log names a refused stranger and records a no-token 401) is read by PR 4's run, not here | Product | PR 4 |
| B | `logs:PutResourcePolicy` and the log-delivery grants reach the whole shared account; accepted by name; the `aws:ViaAWSService` condition untried | Security | PR 4, or standing |
| C | `DeleteLogDelivery` not granted: a stage's delete, its log destination's change, or a doored agent's retirement may be refused | Security | the first retirement of a doored agent |
| D | `RetainExceptOnCreate` on the pool has not fired on a failed first deploy; the 55 orphans were deleted by hand | Security; Engineering | standing |
| E | A subject removed from `callers` leaves its user and credential in the pool; re-admitting it is refused until the user is deleted by hand | Tool Owner; Security | standing |
| F | The destination admits the execution role alone (security F3); no seeded case shows another principal refused | Security | PR 4, or standing |
| G | The by-hand deploys preceded their ruling (cold F1; M09's carry): the bootstrap three times, the security stack twice; the narrowed destination policy is deployed after this file is ruled | Security | this PR |
| H | `time_epoch_ms` carries seconds on an HTTP API; the field keeps its name (cold N1) | Engineering | standing |
| I | The quota test's measure is the template's; an intrinsic that renders longer could pass it and be refused (cold N2). The default policy has 1,106 characters of room | Engineering | standing |
| J | Whether `logs:PutResourcePolicy` takes a resource is unread in the Service Authorization Reference (security N9) | Security | PR 4 |
