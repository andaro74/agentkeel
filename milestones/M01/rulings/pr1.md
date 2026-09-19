---
# M01 PR 1 (#7), the plant. Ruling B: one seat per file; the seat per path
# is named in the body. The Threshold Owner's key is in
# rulings/pr1-threshold-owner.md; Engineering's key on the same two
# thresholds.yaml changes is given here.
ruling: pr1
seat: Product
authorises:
  # Product
  - SPEC/00-overview.md
  - SPEC/01-signed-bundle.md
  - CLAUDE.md
  - .claude/skills/cold-review/SKILL.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - docs/adr/ADR-0004-measurement-fields.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - docs/milestones/M01.md
  - docs/milestones/README.md
  - docs/video/README.md
  - milestones/README.md
  - milestones/M00/README.md
  - milestones/M01/**
  - milestones/M02/open.md
  # Security (and platform-architect, whose seat is Security)
  - .claude/agents/platform-architect.md
  - .github/workflows/evals.yml
  - infra/eval-role/app.py
  - infra/eval-role/README.md
  - infra/eval-role/AwsSolutions--AgentkeelM00EvalRole-NagReport.csv
  - infra/ruleset/main.json
  - infra/ruleset/README.md
  - infra/workflows.sha256
  # Engineering
  - .gitattributes
  - Makefile
  - src/cost_cap.py
  - src/validate/checks.py
  - src/verdict/**
  - tests/**
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M01
  - SPEC/01-signed-bundle.md
  - milestones/M01/feasibility.md
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - docs/adr/ADR-0004-measurement-fields.md
  - docs/adr/ADR-0005-video-follows-the-tag.md
  - https://github.com/andaro74/agentkeel/actions/runs/35412277571
pr: 7
---

# Ruling: M01 PR 1 (plant)

Cites `SPEC/00-overview.md#8-M01` for M01's build paths, and the seats'
rulings in `milestones/M01/feasibility.md` §2 (the 35 carried items,
§2.1 and §6; the three `product-spec-reviewer` BLOCKs, §2.2; the Unsure
items A to G, §2.5). Nothing here makes claim 1 pass: no `src/bundle/`,
`src/agent/`, `infra/construct/` or `infra/bootstrap/`.

## Seat per path

| Seat | Paths | Ruling |
|---|---|---|
| Product | `SPEC/00-overview.md`, `SPEC/01-signed-bundle.md`, `CLAUDE.md`, `.claude/skills/cold-review/SKILL.md`, `docs/adr/ADR-0003…`, `ADR-0004…`, `ADR-0005…`, `docs/milestones/M01.md`, `docs/milestones/README.md` (by `make ledger-plain`), `docs/video/README.md`, `milestones/README.md`, `milestones/M00/README.md`, `milestones/M01/**`, `milestones/M02/open.md` | SPEC/00 §8 M01; items 1, 2, 10, 27, 30; ADR-0003 amendment 1, ADR-0004 amendment 2, ADR-0005 amendment 1; rulings B, E |
| Security | `.claude/agents/platform-architect.md` (`seat: security`, R8), `.github/workflows/evals.yml`, `infra/eval-role/**`, `infra/ruleset/**`, `infra/workflows.sha256` | items 9, 12, 14, 16, 17, 19, 29, 30, 31, 32, 33, 34, 35; rulings C, D |
| Engineering | `.gitattributes`, `Makefile`, `src/cost_cap.py`, `src/validate/checks.py`, `src/verdict/**`, `tests/**`, `agents/refagent/manifest.yaml` (all but its model-id fields) | items 4, 5, 6, 9, 11, 22, 29; ADR-0003 amendment 1; rulings A, F |
| Threshold Owner | `thresholds.yaml`; the model-id fields of `agents/refagent/manifest.yaml` | `rulings/pr1-threshold-owner.md` |
| Rule Owner | `guardrail: null` in the manifest; unchanged, M03 | none needed |

**Engineering's key** (ruling B) on the two `thresholds.yaml` changes is
given here: `cost_cap.tokens_per_run` 20,000 → 150,000, and
`baseline_card` pinning the card at tag `m00` by hash `b0219756…`. The
Threshold Owner's key is `rulings/pr1-threshold-owner.md`.

`.gitattributes` holds `docs/video/**/*.mp4 filter=lfs diff=lfs merge=lfs
-text`, not the ruled `docs/video/** …`: the ruled line made
`docs/video/README.md` an LFS pointer in `fa21d9d`, and Engineering
narrowed it before the PR opened (`8f4faa2`). A second line,
`docs/video/milestones/M00.mp4 -filter -diff -merge`, keeps the filter off
M00.mp4: with it on, every fresh checkout read M00.mp4 as modified and this
PR's first `evals` run refused as a dirty tree (run 35469006669). M00.mp4's
blob is unchanged, `5c5413c`.

## Item 12, Security

Signed: Security, 2026-09-19, on run 35412277571

The narrowed eval role was assumed with `job_workflow_ref =
andaro74/agentkeel/.github/workflows/evals.yml@refs/pull/5/merge`
(commit `c547f4f`). "A second workflow file refused" stays unobserved:
carried, Security, M01 PR 2.

## Item 17, Security: the five pins, re-run 2026-09-19

```
$ git ls-remote https://github.com/actions/checkout refs/tags/v4.2.2 refs/tags/v4.2.2^{}
11bd71901bbe5b1630ceea73d27597364c9af683	refs/tags/v4.2.2
$ git ls-remote https://github.com/astral-sh/setup-uv refs/tags/v10.1.0 refs/tags/v10.1.0^{}
bec219d24cd3e171d82865faccec33120bb574f4	refs/tags/v10.1.0
$ git ls-remote https://github.com/aws-actions/configure-aws-credentials refs/tags/v6.3.0 refs/tags/v6.3.0^{}
e1253824e5c10ff9df46874f81ed3ec929e19cfd	refs/tags/v6.3.0
$ git ls-remote https://github.com/actions/upload-artifact refs/tags/v7.0.1 refs/tags/v7.0.1^{}
043fb46d1a93c77aae656e7c1c64a875d1fc6a0a	refs/tags/v7.0.1
$ git ls-remote https://github.com/actions/download-artifact refs/tags/v8.0.1 refs/tags/v8.0.1^{}
3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c	refs/tags/v8.0.1
```

All five equal the SHAs pinned in `evals.yml` (lightweight tags; no
`^{}` line).

## Cold review (`engineering-cold-reviewer`, verbatim; read at `8f4faa2`)

# M01 PR 1 (#7): cold review, Engineering seat

Read cold: the diff `main...m01-pr1` at `8f4faa2`, the commit list, ledger row 1
(`milestones/README.md:29`) and `milestones/M01/README.md`. Not read: the PR
body, commit message bodies, the argument in `feasibility.md`. Nothing was run
except read-only git.

## Shape and seed order

The commit order, from `git log --reverse main..m01-pr1`:

- The seeds come first: S1 `a7b088e`, S2 `df7c735`, S3 `48669ba`, S4 `1b4c2f6`, S5 `19131e9`, S6 `091cc45`, S7 `2f4cacb`, S8 `6b8b8cf`. Each is its own commit and touches only fixtures, `milestones/M01/runs/*.yaml` and `tests/test_m01_seeds.py`.
- Then `4a254da` (the thresholds pin).
- Then `f42a200`, the only reader in the PR. It reads S7.
- Then the Security, SPEC, ADR and docs commits.

Every seed that has a reader went in before its reader. Nothing in the tree makes claim 1 pass: `git ls-tree -r m01-pr1` lists none of `src/bundle/`, `src/agent/`, `infra/construct/` or `infra/bootstrap/`.

Nothing changed under the protected paths: `git diff --stat main...m01-pr1 -- src/baseline evals/goldens data rules tools evals/history` is empty.

On P5 (separate writer and reader), nothing new writes or reads an envelope:
- only `build.emit` writes one;
- only `src/verdict/gate.py` reads one (`read`, `measured_at`, `control_against_base`);
- `src/cost_cap.py` reads raw runner output only;
- `.github/workflows/evals.yml` reads the gate's exit code, not the envelope.

## BLOCK

**B1. S2's false state is not in the repo at the commit the ledger names for it.**
- `milestones/README.md:29` gives S2 as `df7c735`, "a bundle altered after signing".
- `tests/fixtures/bundles/altered/` has only `manifest.yaml`, `prompt.txt` and two `.gitkeep` files. There is no signature and no signed digest.
- `tests/fixtures/README.md:34` says: "It carries S1's signature, which CI makes in M01 PR 2's first commit".
- So at PR 1, S2 is a second unsigned bundle. `verify` can only refuse it for the same reason as S1, yet `tests/test_m01_seeds.py` expects `match="digest"`.
- The seed is finished in the same PR that lands its reader. CLAUDE.md says: "Never write a claim whose false state is not already in the repo."
- **To clear:** either commit a signature over S1's bytes in this PR, or have Product change the row's Seeded-commit cell to say S2 is completed in PR 2, at a named commit that comes before `src/bundle/verify.py`. Then S2 is recorded as a two-part seed and not claimed as `df7c735`.

**B2. Seat-owned paths cite ruling files that are not in the tree.**
- `thresholds.yaml:20` raises `cost_cap.tokens_per_run` from 20000 to 150000. `thresholds.yaml:10` itself says "Relaxes upward: a higher number needs two keys".
- Its keys are cited as `milestones/M01/rulings/pr1-threshold-owner.md` and `milestones/M01/rulings/pr1.md` (`thresholds.yaml:6-7`).
- `.github/workflows/evals.yml:4` and `infra/eval-role/README.md:4,101` (Security) cite `rulings/pr1.md` too.
- `git ls-tree -r --name-only m01-pr1 milestones/M01` lists no `rulings/` folder at all.
- `milestones/M01/README.md:42` and `feasibility.md` items 12 and 17 say evidence is "in `rulings/pr1.md`". That file does not exist.
- `make validate` checks only that ruling front matter is well formed, so it cannot catch a citation that points at a missing file.
- **To clear:** both files are on the branch before merge. Each has one seat and `pr: 7`, and their `authorises` lists cover `thresholds.yaml`, the model-id fields of `agents/refagent/manifest.yaml`, `.github/workflows/evals.yml`, `infra/**` and the Product paths.

## FINDING

**F1. PR 1 carries PR 2's measurement for S7, and S7's RED is not recorded as evidence.**
- CLAUDE.md, "The PR shape", gives the reader of a plant to PR 2. Here the F1.4 reader lands in PR 1: `src/verdict/build.py:305` (`checks = {**checks, "F1_4": ...}`) and `src/verdict/gate.py:132,180-185`.
- PR 1 also carries other work outside its list: the schema, the Makefile chain, the cost-cap change, the `workflow-hash` check in `validate`, and the workflow and `infra/` edits.
- None of it makes claim 1 pass.
- Row 1 expects at PR 1: "`checks.F1_4` fail; build and gate RED". But this PR's CI envelope is the control's, and build adds F1_4 only on the agent path (`build.py:429`). So S7's RED exists only as a pytest result (`tests/test_m01_seeds.py`, `test_s7_...`), never as a recorded envelope.
- The seat should say where the S7 RED is recorded, for example the junit result under this PR's run URL.

**F2. S7's "red before its reader" was satisfied by a command-line error, not by the missing rule.**
- At `2f4cacb`, the S7 test was `@pytest.mark.xfail(strict=True, reason="S7: the F1.4 rule is not in verdict.build or verdict.gate yet")` (`tests/test_m01_seeds.py:76` at `2f4cacb`), with no `raises=`.
- It calls `build.main([... "--control-card", ...])`. At `2f4cacb`, build accepts only `--baseline-card` (`src/verdict/build.py:321` at `2f4cacb`).
- So argparse exits with an error, and any failure counts as an expected failure.
- `milestones/M01/README.md:33` ("At `6b8b8cf` all eight tests are expected failures") is true, but not for the reason the row claims.
- To falsify: `git show 2f4cacb:src/verdict/build.py | grep -- --control-card` returns nothing.
- The other seeds use `raises=ModuleNotFoundError` or `raises=AssertionError`. S7 did not.

**F3. The S4 and S6 tests pass on empty input.**
- `tests/test_m01_seeds.py:57-58` and `:71-72` use `assert observed is not None` and then `all(attempt["result"] == "AccessDenied" for attempt in observed)`.
- `observed: []` would pass, and would count as "refused".
- Nothing checks that every attempt listed in `milestones/M01/runs/f1_1_laptop.yaml` (three attempts) or `f1_3_key_policy.yaml` (one) was actually made, or that each result carries a request id.
- Both files are filled in by a human. Whether a human-written observation can feed a check is `product-spec-reviewer` finding 5, still open (`milestones/M01/README.md`, "For Security").

**F4. A control envelope can carry F1 checks that nobody verifies.**
- On the control path (`build.py:429`), any `--check-junit F1_x ...` passes straight into `checks` (`build.py:425`).
- `gate.py:179-185` works out F1_4 again only when an agent result is present. It never rejects `F1_*` on a control envelope.
- `Makefile:22,39` chooses the agent chain by whether the file `src/agent/run.py` exists. If the runner is missing, the run silently becomes a control envelope, which can be GREEN and can carry `F1_* pass` into a Measured cell.
- Row 1 says PR 1's envelope "says nothing about claim 1". Nothing mechanical enforces that.

**F5. The prose about commit order is contradicted by the log.**
- `milestones/M01/README.md:20-23` says: "SPEC/01 first ... The seats ruled the three BLOCKs before anything else was committed".
- In fact SPEC/01, `feasibility.md` and the ledger row land in `9a4e750`, the 13th of 15 commits.
- `f42a200` builds ADR-0004 amendment 2 (one subject, `control_card_ref`, `tokens_in`), but the amendment itself lands later, in `28137f2`.
- If "first" means written first, the repo cannot show it. Either reword the prose or cite where the order is evidenced.

**F6. A closed GREEN row was edited after tag `m00`, with no cited ruling.**
- `milestones/README.md` row 0's Seeded-commit cell changes from `` `22b5499` `` to `` `22b5499` (F0.1 plant); `f9f1342` (F0.2 seed) ``. `milestones/M00/README.md:44` changes the same way.
- `make ledger` checks only the Measured cell, so this edit passes with no mechanical check.
- The change may well be a correction. It still needs a Product ruling naming it.

## NOTE

**N1. The cost cap is weaker in the gate than in build.**
- `gate.py:272` reads the cap. If the cap is missing, it is `None` and `gate.py:193` skips the cap check. Build refuses in the same case (`token_cap`).
- If the cap is not an integer, `>` raises `TypeError`. Python then exits 1, which is the same code as RED. The workflow's `record` job keeps exit 1 as RED.
- `"tokens_in" in envelope` means a control envelope with `tokens_in` deleted skips the gate's cap check, and the schema allows that.
- The gate takes build's token sums as given. It does not work them out again from the card and the raw usage.

**N2. The `make plants` line "reader ... in the tree" only checks that a file exists (`gate.py:320`).**
- S7's reader is `src/verdict/build.py` (`plants.py:28`), which has existed since M00. So the line would have read "in the tree" before F1.4 was written.
- S3, S5 and S8 share `infra/construct/`, so one new directory flips all three.

**N3. `Makefile:15` says "A run always writes an envelope". Two paths break this.**
- On the agent chain (`Makefile:43-44`, not live in PR 1): if `src.agent.run` writes nothing, `cost_cap` raises `FileNotFoundError`. Its `except ValueError` does not catch that, so the chain stops with no envelope.
- On either chain: `cost_cap` exits 1 when there is no cap, and no envelope is written.

**N4. `src/verdict/schema.json` is reformatted wholesale.**
- It changes by 206 lines. The real changes are `control_card_ref`, `tokens_in` and `$defs.card_ref`; the rest is whitespace, which makes the reader's job harder.

**N5. Prose claims check out.**
- No "governed", "secure" or "proven" appears about a control that has not fired. `GovernedAgent` is a class name.
- `.github/workflows/evals.yml` says of the REJECTED path "Not yet fired on a seeded REJECTED run in CI", which is honest.

## What a reader can run to falsify this ruling

    git ls-tree -r --name-only 8f4faa2 tests/fixtures/bundles/altered   # B1: no signature
    git ls-tree -r --name-only 8f4faa2 milestones/M01                    # B2: no rulings/
    git show 2f4cacb:src/verdict/build.py | grep -n -- "-card"            # F2: only --baseline-card
    git show 2f4cacb:tests/test_m01_seeds.py | grep -n "xfail(strict=True, reason"   # F2: no raises=
    git log --reverse --oneline main..8f4faa2                            # F5 and seed order
    git diff main...8f4faa2 -- milestones/README.md                      # F6: row 0 edited
    git diff --stat main...8f4faa2 -- src/baseline evals/goldens data rules tools evals/history   # empty

BLOCK: 2 · FINDING: 6 · NOTE: 5

## What happened to the cold review's items

The draft asked for a file named `pr1-engineering.md` with `seat:
Engineering`. Ruling B names this file `pr1.md` with `seat: Product` and
the seat per path in the body; the draft's text is committed here as its
body.

| # | Status |
|---|---|
| B1 | Repaired in `5359229`: row 1's Seeded cell records S2 as a two-part seed, its content at `df7c735` and its signature over S1's bytes as M01 PR 2's first commit, before `src/bundle/verify.py` (the seats' ruling on BLOCK 1; a keyless signature can only be made by CI). |
| B2 | Repaired: this file and `rulings/pr1-threshold-owner.md`, both `pr: 7`, one seat each (ruling B). |
| F1 | Stands, ruled. The F1.4 reader is in PR 1 by the seats' rulings 5/11(d) and BLOCK 3 (`checks.F1_4` with rule (d)). S7's RED in this PR is recorded as the junit result of `tests/test_m01_seeds.py::test_s7_an_answer_that_cites_nothing_is_not_a_pass` under this PR's `evals` run URL, not as an envelope; no agent ran. Whether ruling F admits the `checks.F1_4` half and the gate's reading is Unsure: Engineering with Product, before merge. |
| F2 | Stands, recorded. `milestones/M01/feasibility.md` §3 already names S7's failure at `2f4cacb` as `SystemExit: 2` from build's argument parser. The seed commit is not rewritten. |
| F3 | Repaired in `4733a9a`: every listed attempt must be made, each with a request id. |
| F4 | Repaired in `4733a9a`: `verdict.gate` rejects a control envelope that carries an `F1_*` check. |
| F5 | Repaired in `5359229`: the M01 README says the SPEC-first order is of writing; the commits follow the seats' ruling on commit order. |
| F6 | Ruled: item 10 (Product), `milestones/M01/open.md`, ruled at M01 PR 1: a Seeded commit cell may hold several commits, each labelled; row 0 edited in both ledger files. `make ledger` still exits 0 on row 0. |
| N1 | Repaired in `2515d19` and `188c357` (from the `threshold-owner` re-read): the gate rejects a missing or invalid cap. The gate taking build's token sums is carried: Engineering, M01 PR 2. |
| N2 | Kept: the `make plants` line lists a reader path; it does not claim the reader works. |
| N3 | Carried: Engineering, M01 PR 2, with the agent runner. |
| N4 | Kept: the schema was rewritten by `json.dumps(indent=2)`; the content diff is the three named additions. |
| N5 | Kept. |

## What a reader can falsify at this PR's head

- `git log --reverse --oneline main..m01-pr1`: the eight seed commits
  come first; `f42a200` is the first reader.
- For each seed commit: `git show <sha> --stat` lists the seed and its
  test only; `feasibility.md` §3 has each commit's `pytest -q` result.
- `uv run pytest -q`: 107 passed, 7 xfailed (S1–S6, S8), no XPASS, no
  failure.
- `make validate`, `make plants`, `make ledger` exit 0; row 0 differs from
  `main` in its Seeded cell only.
- `git ls-tree HEAD docs/video/milestones/M00.mp4` is blob `5c5413c`, as
  on `main`; `git lfs ls-files` lists nothing.
- `sha256sum` of `git show HEAD:.github/workflows/<file>` equals the line
  in `infra/workflows.sha256`.
- `infra/ruleset/main.json`: `allowed_merge_methods` `["merge"]`,
  `bypass_actors` `[]`.
