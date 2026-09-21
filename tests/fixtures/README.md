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
