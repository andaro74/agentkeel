---
adr: ADR-0002
title: The baseline is frozen at tag m00
status: Accepted
date: 2026-09-18
seat: Product
authorises:
  - Engineering      # src/baseline/** is closed after tag m00; tests/test_baseline_frozen.py is the guard
  - Threshold Owner  # the baseline's model id, region and inference parameters, confirmed before the tag
  - Product          # SPEC/00 §8 M00: the freeze lands at the close PR, not at a fourth PR
amendments: 0
---

# ADR-0002 — The baseline is frozen at tag m00

Reserved at ADR-0001 and held open through ADR-0003 and ADR-0004. This
is the M00 close PR, so it is written now.

## Context

Claim 0 is that every later number is a delta against a frozen naive
baseline. A delta is only a delta if its base does not move. Two things
could move it:

1. Someone edits `src/baseline/` — the prompt, the parse, the call — and
   the control gets better or worse. Every earlier number then compares
   against something that no longer exists.
2. Someone changes the model id, the region or the inference parameters.
   Same effect, with nothing in the diff under `src/baseline/` to show
   it, because `MODEL_ID`, `REGION` and `INFERENCE_CONFIG` live in
   `src/baseline/agent.py` and a reader could take them for code.

CLAUDE.md already says "never edit `src/baseline/` after tag `m00`". That
is a sentence. Nothing read it.

The base moves for a third reason this ADR does not fix: the control is
not deterministic at temperature 0 (Finding F0.4, ADR-0004,
`milestones/M00/feasibility.md` §6.5). Freezing the code does not freeze
the answers. What is frozen here is the thing under test, not its output.

## Decision

1. **`src/baseline/` is closed from tag `m00`.** Four files, no more and
   no fewer, with the content hashes below. Nothing is added to the
   folder either: a new file anywhere under it, including in a
   sub-package, is a change to the control. The test walks the folder
   recursively and ignores only `__pycache__`.

2. **The frozen content.** sha256 of each file's text, read as text, so a
   CRLF checkout hashes the same as CI (the same rule as
   `canonical_sha256`).

   | File | sha256 |
   |---|---|
   | `src/baseline/__init__.py` | `cbb26eec2d2181a42954125f22b4f7b5d0f9ba6ffc847ce2b34e3d974d0b9147` |
   | `src/baseline/agent.py` | `70d9fc4561dfa423027cc51e241dcc8b8f977c98406bd7550874da943cb3dfd3` |
   | `src/baseline/prompt.txt` | `2c3d9b754f8c285e95c3590cea61cafb1f59e5c5af64a1ea7b776c6c383684ab` |
   | `src/baseline/run.py` | `625183fd3ca5f7b3014218d7b043e3a5268b3f8b3f3d56a74992f1a2db549e22` |

   The prompt's hash is the one in every baseline card in
   `evals/history/`, including the card the row 0 measurement rests on
   (`9407615…baseline-card.json`, `prompt_sha256` `2c3d9b75…`). The
   measurement and the freeze name the same prompt.

3. **The frozen parameters.** Threshold Owner, confirmed before this tag
   and recorded in `milestones/M00/README.md`: `us.amazon.nova-micro-v1:0`,
   `us-west-2`, Converse, `temperature` 0, `maxTokens` 512, one system
   prompt, no tools, no guardrail, no retrieval. They are in
   `src/baseline/agent.py`, so item 2's hash covers them; the test states
   them separately anyway, because a reader looking for the numbers
   should find them named, not inside a hash.

4. **The test.** `tests/test_baseline_frozen.py`. It fails on any diff to
   `src/baseline/` or to the prompt hash:
   - the file set and each file's hash against the table above;
   - the model id, region and inference config against item 3;
   - the table above against the same constants, so the ADR and the test
     cannot drift apart;
   - `git diff m00 HEAD -- src/baseline`, when tag `m00` is in the
     checkout.

   The first three run everywhere and fail today on any edit. The fourth
   is the one that reads the tag itself; it skips where the tag is not
   fetched, and says so rather than passing quietly. The `evals` workflow
   checks out with `fetch-depth: 0`, so it runs there from the tag on.

5. **After the tag, `src/baseline/` changes only by retiring the
   control.** Not by editing it. A new control is a new folder, a new
   card and a new ADR, and every row measured against the old one keeps
   the old one as its base. Engineering and Threshold Owner, two keys,
   from M02.

## Consequences

- SPEC/00 §8 M00 said this ADR lands "at PR 4". The milestone closes at
  PR 3 (ruling F, `milestones/M00/feasibility.md` §2 fourth round), so
  §8 M00 is amended in this PR to say the close PR.
- A change to `src/baseline/` now fails four ways before it reaches
  review: three hash assertions and, from the tag, the diff against it.
  None of them is a gate a seat waits on; they are tests, and `pytest`
  runs in `evals`.
- The freeze is on content, not on behaviour. Run 4 and run 5 of the
  control differ with these exact hashes (§6.5). Anyone reading a later
  delta has to read F0.4 with it.
- `g-012` stays as it is, under ADR-0003. If the Data Owner retires it at
  M01, the control is not touched: a retired golden is not a changed
  baseline. The new golden's expected `constraints` may name a code the
  frozen prompt cannot produce; who resolves that is
  `milestones/M01/open.md`, not this ADR.
