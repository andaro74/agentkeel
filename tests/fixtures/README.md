# tests/fixtures

Every file here is a false state, not evidence. None is ever copied to
`evals/history/`. CLAUDE.md's "never write an envelope by hand" has one
exception, and it is this folder: a seed under `tests/fixtures/`, named
in this file (M01 open item 1, Product).

## M00

`hand_written_envelope_no_baseline_card_ref.json` is M00's second seed: a
run without a baseline card. It was typed by hand from the numbers of the
PR 1 plant run (`22b5499`, feasibility.md §6.2). It has every envelope
field except `baseline_card_ref`, and it says GREEN.

Edited once, by hand, at ADR-0004: each result gained `scope: control`
when the schema began to require it. Without that the file would be
rejected for two reasons, and the test needs it rejected for one.

It was committed before `src/verdict/` existed, with the test that
expects the gate to reject it. Do not add the missing field here;
`tests/test_f0_2.py` adds it in memory to show the file is rejected for
that reason and no other.

## M01 (SPEC/01 §5)

Committed at M01 PR 1, one commit per seed (`a7b088e` S1 to `6b8b8cf`
S8), each with its test in `tests/test_m01_seeds.py`, before any code that
reads them. Each test was `xfail(strict=True)` until its reader landed.

**Every marker is off as of M01 PR 2.** `tests/test_m01_seeds.py` carries
none, because every reader landed in that PR: `src/bundle/verify.py` for S1
and S2, `infra/construct/` for S3, S5 and S8, `scripts/observe_attempt.py`
with `--check-attempt` for S4 and S6. A marker comes off in the commit that
lands its reader, and `strict=True` is what stopped one coming off early —
an xpass would have failed the run. This paragraph still said every test was
xfail until the cold review of PR 2 found it.

| Seed | File | What is wrong with it |
|---|---|---|
| S1 | `bundles/unsigned/` | a bundle with no signature |
| S2 | `bundles/altered/`, and `bundles/altered/bundle.cosign.json` | S1's bundle with one byte of `prompt.txt` changed (`0.7` to `0.1`, the HITL threshold). It carries S1's signature, which CI makes in M01 PR 2's first commit, over S1's bytes. `manifest.yaml` is S1's, byte for byte, including the comment that says S1 |
| S3 | `construct/extra_egress.py`, `construct/extra_egress_standalone.py` | refagent's `GovernedAgent` plus an egress rule to `0.0.0.0/0:443` that the manifest does not list: once through the construct's security group, once as a separate resource the construct never sees |
| S5 | `construct/role_without_boundary.py` | `GovernedAgent` handed a role with no permission boundary |
| S8 | `construct/outside_construct.py` | an AgentCore runtime resource made directly, with no `GovernedAgent` |
| S7 | `refagent_raw_uncited.json` | fifteen raw replies, written from the goldens' `answer_fields`: every ordinary and trap answer right, and none cites a `table_row` or a `clause_id`. Raw observations, not an envelope; `verdict.build` scores them |

S4 and S6 are attempts against AWS, not files that can be read here. They
are described in `milestones/M01/runs/f1_1_laptop.yaml` and
`f1_3_key_policy.yaml`, and were **made by the human on 2026-09-20, during
M01 PR 2**, against the deployed bootstrap stack. Both run files carry the
`observed:` entries; CI looks each request id up in CloudTrail and that
lookup is what writes `checks.F1_1` and `checks.F1_3`. This paragraph said
they were made on the first `main` run after PR 2 merges, which was the plan
at PR 1 and was superseded by ruling 4 before PR #7 merged.

The four `construct/` files import `infra.construct`, which does not exist
until M01 PR 2. `pytest` does not collect them. If the construct's API
names differ when it lands, PR 2 changes the call and never what is added
or handed in.

## M02 (SPEC/02 §5)

Committed at M02 PR 1, one commit per seed, each with its test in
`tests/test_m02_seeds.py`, before any code that reads them. Each test was
`xfail(strict=True)` until its reader landed at PR 2, and `strict` is what
made a marker come off in the commit that landed the reader.

**Five markers are off as of M02 PR 2**: S1 (both forms) and S2 in the
commit that landed `src/gates/two_key.py`, S3 and S5 in the commit that
landed `validate`'s edge and golden-id checks. S4's marker stayed on at
PR 2: its reader, `scripts/observe_pr.py`, landed there, but the test
reads `f2_1_bypass.yaml`, whose `observed:` was null until the human made
the attempts after PR 2 merged (SPEC/02 §5.1), and a strict marker taken
off early would have failed every run until then. **All six are off as of
M02 PR 3**: S4's came off in the commit that wired `evals.yml` to look the
attempts up, after the human filled the run file on 2026-09-23; the strict
marker had refused the filled file on the branch's run before that
(35874322479, `XPASS(strict)`), which is what strict is for.

A seed here is a **diff**, not a file: a unified patch against the tree
at PR 1's base, under `m02/`, applied to a throwaway worktree by the test
and, after PR 2 merges, to a branch by the human to open the seed PR
(`milestones/M02/runs/f2_1_seed_prs.yaml`). The patches are `-text` in
`.gitattributes` so a Windows checkout keeps them LF and `git apply`
matches. If a base file changes before PR 2 so a patch no longer applies,
PR 2's first commit re-plants it, still before its reader.

| Seed | File | What is wrong with it |
|---|---|---|
| S1 | `m02/s1-one-key.patch` | `thresholds.yaml` `cost_cap.tokens_per_run` 150000 → 300000, an upward move, with **one** ruling file (`seat: Threshold Owner`, `pr: 0`) covering the path. `ruling-cited` is satisfied; only `two-key` can refuse it |
| S1 | `m02/s1-two-files-one-seat.patch` | the same move with two ruling files, both Threshold Owner. Two files are not two seats |
| S2 | `m02/s2-golden-greened.patch` | `g-010`'s `expected.answer_fields.available` false → true and `constraints` emptied, so the trap rewards the answer it was written to catch. No ruling. `g-010` has passed in agent history |
| S3 | `m02/s3-one-sided-edge.patch` | `may_call: [ratings-helper@v1]` in refagent's manifest; nothing says `ratings-helper` may be called by refagent. No ruling |
| S5 | `m02/s5-golden-renamed.patch` | `g-005.yaml` deleted, `g-099.yaml` added with the same content and `id: g-099`; `retired` untouched. No ruling. Passes today's `validate` |

The two ruling files inside S1's patches carry `pr: 0`; the human sets the
seed PR's number when opening it, and the run file records that edit.
They exist only in the patches and on the seed branches, never on `main`.
**`g-099` is burned**: no golden ever gets that id (R11).

S4 is an attempt against GitHub, not a file that can be read here. It is
described in `milestones/M02/runs/f2_1_bypass.yaml` and is made by the
human, as the repository owner, after M02 PR 2 merges and before PR 3's
first CI run; PR 3's run looks it up (`scripts/observe_pr.py`). Its
`observed:` is null at PR 1 and filled at PR 3.

## M03 (SPEC/03 §5)

Committed at M03 PR 1, one commit per seed, each with its test in
`tests/test_m03_seeds.py`, before any code that reads them. Each test is
`xfail(strict=True)` until its reader lands at PR 2, and asserts the
planted reason, not only the verdict. The two guards in the same file
carry no marker and are not seeds (SPEC/03 §5.2).

The patches are `-text` in `.gitattributes`, as M02's are. The ruling
file inside S1's patch carries `pr: 0` and exists only in the patch;
no seed PR is opened at M03 (SPEC/03 §4).

| Seed | File | What is wrong with it |
|---|---|---|
| S1 | `m03/s1-table-regresses.patch` | `r-003` (`t-001`, DE, SVOD) `exclusive` false → true in `data/rights_table.json`, with one Data Owner ruling. `g-011` reads `r-003` and expects false. `ruling-cited` passes and nothing is a relaxation; in `mode: runtime` the run answers from `main`'s table and `g-011` passes |
| S2 | `m03/s2-g-016.yaml`, `m03/s2-g-016-result.json` | the first red-team attack (the embargoed synopsis through role-play) as a golden, and its result as the runner writes it when the attack gets through. The test adds the result to row 2's envelope in memory with a red-team control in a copy of the tree; `CONTROLS` is empty, so it lands in `never_passed` and the gate says GREEN. Not a golden: `g-016` lands under `evals/goldens/v1/` at PR 2 |
| S3 | `m03/s3-overlap.patch` | `data/corpus/holdback-schedule.md`, whose worked example is `g-010`'s question word for word (38 words) with its answer (`available: false`, holdback, `r-009`, `HS-4`), and a Data Owner ruling on the path. Today's golden, citation and ruling checks pass on it |
| S4 | none | the false state is already in `evals/history/`: row 2's envelope, `8033c2a`, says `corpus_fingerprint: null`, as every envelope does. The test puts S3's document and an `admitted.yaml` naming it in a copy of the tree and asks the gate to rule the envelope beside it. Nothing is copied or edited |
| S5 | `m03/s5-unsigned-amendment.md` | "Amendment No. 2", its signature lines blank, granting `t-001` exclusive SVOD in DE against `r-003` and `ML-5.2`. Uploaded once to the quarantine bucket by the human during PR 2 (`milestones/M03/runs/f3_5_amendment.yaml`, `observed: null` until then); never under `data/corpus/`, never named in `admitted.yaml`. `-text` in `.gitattributes`, so the sha256 the run file records is the same on every checkout |
