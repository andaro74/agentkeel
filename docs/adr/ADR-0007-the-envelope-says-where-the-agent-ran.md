---
adr: ADR-0007
title: The envelope says where the agent ran, in which region, and on which model version
status: Accepted
date: 2026-09-21
seat: Product
authorises:
  - Product  # SPEC/00 §4 P3: the exception M01 PR 2 named, made readable from the envelope
  - Threshold Owner  # the agent model id + version + region, which A-vs-A compares as a pair
amendments: 0
---

# ADR-0007 — The envelope says where the agent ran

## Context

Three gaps, each found by M01 PR 2's cold review and ruling. Each is
already named in a ruling file.

1. **Mode.** `src/agent/run.py` runs refagent in the runner when
   `AGENTKEEL_RUNTIME_ARN` is unset, and in the deployed runtime when it is
   set. The raw file says which (`where`), but the runner that chose the
   mode wrote it, and `verdict.build` drops it. An envelope from the runner
   and an envelope from the construct look the same. That is why M01 PR 2
   had to name a P3 exception (`pr2.md`, "What runner mode means for
   claim 1").
2. **Region and model version.** The envelope carries `model_id` and
   nothing else about the model. A-vs-A (M04) compares the id, version and
   region as a pair (cold review, finding 39).
3. **Nothing compares the model with the pin.** `build.py` takes `model_id`
   from the runner's raw file. No reader checks it against the manifest's
   pin (finding 35, "M04 needs this").

Two facts about the current tree limit what can be decided.

- **`replay_history` validates every past envelope against the current
  schema**, and raises on the first failure. `evals/history/` holds 23
  envelopes, and they are evidence and are not rewritten. A new field that
  is simply *required* would make all 23 invalid and stop every later build.
- **Nothing on `main` measures, and nothing calls the deployed runtime
  except `deploy.yml`'s load check.**
  - `evals.yml` on `main` finds the merge commit's tree already measured,
    because it is the tree the pull request's run measured. So it re-gates
    the recorded envelope and runs nothing.
  - `record` commits only on pull requests.
  - `AGENTKEEL_RUNTIME_ARN` is set nowhere but in `deploy.yml`, whose load
    check writes a raw file and no envelope.

## Decision

### 1. A versioned envelope, so history stays valid

- The schema gains an optional top-level `schema_version`. An envelope
  without one is version 1: everything in `evals/history/` today.
  `verdict.build` writes `schema_version: 2` from this ADR on.
- **For version 2, four fields are required**, enforced in the schema with
  `if`/`then`:

| Field | Values | Written from |
|---|---|---|
| `mode` | `control`, `runner`, `runtime` | the raw file's `mode`, which `run.py` writes beside `where`. A control-only envelope, M00's form, is `control` |
| `runtime_arn` | the runtime's ARN, or `null` | the raw file. Non-null exactly when `mode` is `runtime` |
| `region` | a region name | the raw file's request region (see T2) |
| `model_version` | a string, or `null` | see T1 |

- `verdict.gate` refuses (REJECTED) a version 2 envelope that breaks the
  pairing: `runtime` without an ARN, or an ARN without `runtime`.
- A test proves `verdict.build` and `verdict.gate` can disagree on these
  fields, as CLAUDE.md requires of every envelope field.

### 2. The run is compared with the pin (finding 35)

`verdict.gate` reads the manifest of the agent under test as it stood at
the envelope's commit, and compares the envelope's `model_id`, `region` and
`model_version` with the pin. A mismatch is REJECTED (T3). `verdict.build`
writes them as the run reported them and does not compare.

### 3. Where claim 1's second half is first read — P1: Option B

The fields only record the mode; something has to run in `runtime` mode.
Two ways to do that, and they are exclusive:

- **Option A: the deploy's load check writes the envelope.** After the
  deploy, `deploy.yml` runs the same chain `make evals` runs, in `runtime`
  mode, and `verdict.build` writes the envelope.
  - *For:* it measures the bytes just deployed, at the merge commit of the
    PR that deployed them, which is closest to "PR 3's measurement".
  - *Against:* the envelope cannot be recorded. `evals/history/` is written
    by `record` on pull requests, and a push to `main` from CI is refused by
    the ruleset. It would be evidence only as a workflow artifact, and that
    is a second evidence path.
- **Option B: a pull request's run uses the runtime when the bytes match.**
  `evals.yml` packs the tree's refagent bundle. If the deployed runtime's
  image carries the same bundle digest, the run sets `AGENTKEEL_RUNTIME_ARN`
  and measures in `runtime` mode. Otherwise it stays in `runner` mode and
  says so. The image tag is already the bundle digest (`deploy.yml`).
  - *For:* one evidence path. The envelope is written by `build.py`,
    recorded by `record`, and replayed like every other.
  - *Against:* the first runtime-mode envelope is the first pull request
    after PR 3 merges, which is M01 PR 4, the close. That moves the P3
    exception from "PR 3" to "PR 4's run". The machinery still lands in
    PR 3, so no machinery is built in the last PR. But the ledger's Expected
    cell has to say PR 4's run, not PR 3's.
  - *Needs:* three read grants for the eval role, and a bootstrap
    redeploy. The runtime pins the *image* digest, and the bundle digest is
    the image's *tag*, so matching them takes all three reads (the draft
    said two; the runtime's ARN has to be found first):
    - `cloudformation:DescribeStacks` on `stack/agentkeel-refagent/*`, for
      the runtime's ARN;
    - `bedrock-agentcore:GetAgentRuntime` on `runtime/refagent*`, for the
      image digest the runtime runs;
    - `ecr:DescribeImages` on `repository/agentkeel-refagent`, for that
      image's tags.

## Rulings (2026-09-21)

All five were ruled as recommended below: T1 to T3 by the Threshold Owner
(`milestones/M01/rulings/pr3-threshold-owner.md`), P1 and P2 by Product,
with Security for the workflow (`pr3-product.md`, `pr3.md`). One condition
came with P1: **the fallback is never silent.** If the digest match cannot
run, the envelope says `mode: runner`, the run's job summary says why, and
a reader at the close meets an unmeasured half, not a false GREEN. The
envelope has no field for the reason, and this ADR adds none.

Where the code differs from the text above, the code is the ruling's:

- **The pin check is the gate's, not build's.** build writes the model, the
  region and the mode as the run reports them, and the gate REJECTs a
  version 2 agent envelope that is off the pin. That split is what lets the
  two disagree (P5), and a test holds each disagreement.
- **The gate knows the agent's bundle by a constant**, `agents/refagent`,
  because the envelope names none and this ADR adds no field for it. The
  second agent (M02) replaces the constant.
- `gate.measured()` adds `mode <mode>` after the tallies, and only for a
  version 2 envelope. Row 0's cell is unchanged, byte for byte.

## Questions that were ruled

| # | Seat | Question | Recommendation |
|---|---|---|---|
| T1 | Threshold Owner | Where `model_version` comes from | **The manifest's pin.** Bedrock returns no version for `us.anthropic.claude-sonnet-4-6` (ruling p), so the pin is `null`, and the manifest already says why. A version read from a response would be a second source that can disagree with the first. |
| T2 | Threshold Owner | `region` per run, or from the manifest | **Per run, from the raw file**, and compared with the pin (T3). The pin says what should have happened; the raw file says what did. |
| T3 | Threshold Owner | What a mismatch with the pin does | **REJECTED, not RED.** The run did not measure the pinned subject, so it is not evidence of anything about it. RED would record it as a result. |
| P1 | Product, with Security for the workflow | Option A or B | **B.** One evidence path, and the envelope a reader meets in `evals/history/` says `runtime`. A second, artifact-only path would be the "prose about a control" this milestone has caught seven times. |
| P2 | Product | The ledger's Expected cell for row 1, after P1 | If B: "construct tenancy is read by the first run whose bundle digest matches the deployed runtime: M01 PR 4's". The Expected cell is Product's and not a falsifier, so it may be clarified. The falsifiers do not change. |

## Consequences

- Version 1 envelopes are read as they are. Nothing in `evals/history/`
  changes.
- `make ledger` compares the Measured cell with `gate.measured()`. If
  `measured()` starts printing the mode, row 0's cell (M00) must still match
  its version 1 envelope, so `measured()` prints the mode only for version 2.
- If B: when an envelope is in `runner` mode although a runtime exists, it
  is because the bytes differ or the lookup failed. The envelope says
  `runner`; the job summary says which, since the envelope has no field for
  why. It does not fail the pull request:
  a pull request that changes refagent cannot be measured on the runtime
  until it is deployed.

## Amended by the PR 3 cold review (before merge; not an amendment)

- **B1.** Recording the mode was not a reading of claim 1. From this repair,
  `gate.measured_at()` shows a row in `READ_IN_THE_RUNTIME` (M01) as
  **UNMEASURED** when its agent envelope is not `mode: runtime`, and
  `src/ledger.py` refuses a GREEN state beside that cell. A pull request's
  own verdict is unchanged.
- **F2.** A version 1 agent envelope is REJECTED unless its commit is at or
  before this ADR's (`7f8d0ae`). All 23 in history are.
- **The pin's id.** The gate also refuses a pin whose `id` and `profile`
  disagree.
- **T2.** The region recorded "per run" is the request region the client was
  built with. Converse does not report the region that served the call, so
  the check guards against a changed runner or a hand-edited file. It does
  not guard against routing.

## Not decided here

- `judge_model_id` is still a constant `null` in `build.py` (finding 37).
  M03.
- `cost_usd` stays `null`. The cap re-rule is the Threshold Owner's at the
  M01 close (finding 31).
