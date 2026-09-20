---
# M01 PR 2 (#8), the measurement. Ruling B: one seat per file; the seat
# per path is named in the body. The Threshold Owner re-rules the cap and
# refagent's model version against this PR's first agent envelope, in
# rulings/pr2-threshold-owner.md, which carries the same `pr`.
ruling: pr2
seat: Product
authorises:
  # Product
  - SPEC/00-overview.md
  - SPEC/01-signed-bundle.md
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
  - milestones/README.md
  - milestones/M01/README.md
  - milestones/M01/feasibility.md
  - milestones/M01/pr2-body-draft.md
  - milestones/M01/rulings/pr2.md
  - milestones/M01/runs/f1_1_laptop.yaml
  - milestones/M01/runs/f1_3_key_policy.yaml
  # Security
  - .github/workflows/deploy.yml
  - .github/workflows/evals.yml
  - .github/workflows/sign-fixture.yml
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - infra/bootstrap/AwsSolutions--AgentkeelBootstrap-NagReport.csv
  - infra/construct/__init__.py
  - infra/construct/governed_agent.py
  - infra/construct/app.py
  - infra/construct/cdk.json
  - infra/construct/AwsSolutions--AgentkeelRefagent-NagReport.csv
  - infra/bootstrap/cdk.json
  - infra/ruleset/main.json
  - infra/ruleset/README.md
  - infra/workflows.sha256
  # Tool Owner
  - agents/refagent/tools/check_availability.json
  # Threshold Owner and Tool Owner, in one file, one field at a time
  # (ADR-0003 amendment 1). The model fields are re-ruled in
  # pr2-threshold-owner.md against this PR's first agent envelope.
  - agents/refagent/manifest.yaml
  # Engineering
  - .gitignore
  - uv.lock
  - Makefile
  - pyproject.toml
  - agents/__init__.py
  - agents/refagent/__init__.py
  - agents/refagent/agent.py
  - agents/refagent/server.py
  - agents/refagent/prompt.txt
  - agents/refagent/Dockerfile
  - scripts/load_rights_table.py
  - scripts/observe_attempt.py
  - src/agent/**
  - src/bundle/**
  - src/manifest/**
  - src/validate/checks.py
  - src/verdict/build.py
  - src/verdict/gate.py
  - tests/**
evidence:
  - SPEC/00-overview.md#8-M01
  - SPEC/01-signed-bundle.md
  - milestones/M01/feasibility.md
  - docs/adr/ADR-0006-gateway-endpoints-for-s3-and-dynamodb.md
pr: 8
---

# M01 PR 2 — the measurement

This is the PR that reads the plants (P3). Row 1 is decided by the CI run
on the head that merges; earlier runs on this branch are recorded and not
cited (PR 2 mechanics, `feasibility.md` §2.6).

## The seat for each group

| Paths | Seat | What authorises them |
|---|---|---|
| `SPEC/**`, `milestones/**`, `docs/adr/ADR-0006` | Product | `SPEC/00-overview.md#8-M01`; ADR-0006 is Security's rule and Product's folder |
| `.github/workflows/**`, `infra/**` | Security | `SPEC/00-overview.md#8-M01`, SPEC/01 §6, `feasibility.md` §2.6 a, b, d, e, f, g, k, n, q, r |
| `agents/refagent/tools/check_availability.json` | Tool Owner | SPEC/01 §6 (`check_availability` with a strict schema both ways), ruling SCOPE |
| `src/**`, `scripts/**`, `tests/**`, `Makefile`, `pyproject.toml`, `.gitignore`, `agents/refagent/**` but for the rows above | Engineering | `SPEC/00-overview.md#8-M01`, `feasibility.md` §2.6 l, m |

`agents/refagent/manifest.yaml` is changed in this PR, and each field it
gains has its own seat (ADR-0003 amendment 1): `endpoint_allowlist` and
`seats` are Security's (ruling d), `may_call`, `may_be_called_by` and
`ceilings` the Tool Owner's, `max_tokens_per_session` and `daily_usd` the
Threshold Owner's. The model id, version and region do not move; they are
re-ruled with the cap (rulings o and p) in `pr2-threshold-owner.md`.

S4 and S6 fail on this head, and that is the row RED for the stated
reason: the attempts have not been made. Their markers are off because
their reader — `scripts/observe_attempt.py` and `--check-attempt` — landed
in this PR, which is the rule (a marker comes off in the commit that lands
the reader). Leaving `xfail(strict=True)` on would have failed the
measuring run the moment the human recorded the attempts.

## What went in, and what reads what

| Seed | Planted | Read by | State at this PR |
|---|---|---|---|
| S1 | `tests/fixtures/bundles/unsigned/` | `src/bundle/verify.py` | marker off; refused for its missing signature |
| S2 | `tests/fixtures/bundles/altered/` | `src/bundle/verify.py` | marker off; refused for its digest |
| S3 | `tests/fixtures/construct/extra_egress*.py` | the stack validation in `infra/construct/` | marker off; both forms refused at synth |
| S4 | `milestones/M01/runs/f1_1_laptop.yaml` | the deploy role's trust policy, read through CloudTrail | marker off; **failing**, because the attempt has not been made |
| S5 | `tests/fixtures/construct/role_without_boundary.py` | the stack validation | marker off; refused at synth |
| S6 | `milestones/M01/runs/f1_3_key_policy.yaml` | the key policy, read through CloudTrail | marker off; **failing**, because the attempt has not been made |
| S7 | `tests/fixtures/refagent_raw_uncited.json` | `verdict.build` and `verdict.gate` | marker came off at PR 1 |
| S8 | `tests/fixtures/construct/outside_construct.py` | the stack validation | marker off; refused at synth |

## ADR-0006

SPEC/00 §8 M01 said "VPC with interface endpoints only". S3 and DynamoDB
are reached from a VPC through gateway endpoints, which have no security
group. The rule is amended, and the difference is carried into the
construct: three egress rules to security groups, two to prefix lists, and
the S3 check accepts both shapes and nothing else.

## What the cold review found, and what was done

Five seats read this PR before it was undrafted: `security-reviewer`,
`platform-architect` (on S3, S5 and S8), `threshold-owner`, `tool-owner`
and `engineering-cold-reviewer`. Every report is in the PR body verbatim.
Counts: 6 BLOCK, 39 FINDING, 43 NOTE. Two BLOCKs are ruled here (B, repaired; E, ruled in `pr2-threshold-owner.md`); three stand.

**Repaired in this PR.** Each of these was a control that could not fail,
or a check that could not see:

| # | What | Where |
|---|---|---|
| 1 | The boundary denied `kms:GetKeyPolicy`, so S6 could never show the **key policy** was what refused. F1.3 could not fail. | `infra/bootstrap/app.py` |
| 2 | S4's attempts were refused by the developer role's own Deny, so the deploy role's trust conditions were never the thing that refused. The assume is now allowed on the developer role, exactly as S6 grants itself `kms:GetKeyPolicy`. | `infra/bootstrap/app.py` |
| 3 | `F1_3` passed on any `AccessDenied`, including one from the role's own policy — the case the run file says does not count. It now reads CloudTrail's `errorMessage` against `message_must_contain`. | `src/verdict/build.py`, `runs/f1_3_key_policy.yaml` |
| 4 | An agent envelope could omit `F1_1`, `F1_2` and `F1_3` and still go GREEN: the Makefile builds the flags conditionally. The gate now refuses an agent envelope missing any of the four. | `src/verdict/gate.py` |
| 5 | `verify()` passed a bundle whose certificate it could not read, and skipped the signature silently when cosign was absent. Both are now reasons. A regression test forges exactly that bundle. | `src/bundle/verify.py` |
| 6 | S3's second form was matched by Python class, so the same rule written as a raw `CfnResource` was missed. Now matched by CloudFormation type. | `infra/construct/governed_agent.py` |
| 7 | A runtime added inside a `GovernedAgent`'s scope passed S8's check. Now the check is identity, not a place in the tree. | `infra/construct/governed_agent.py` |
| 8 | `fromPort` was in the message and not in the test: `tcp 1-443` to an approved endpoint was accepted. | `infra/construct/governed_agent.py` |
| 9 | S4's and S6's markers were still `xfail(strict=True)` although their reader landed here. The moment the attempts were recorded, strict xpass would have failed the measuring run. | `tests/test_m01_seeds.py` |
| 10 | S2's assertion matched `digest`, which also matches "carries no signed digest" — it would have passed with the comparison never run. | `tests/test_m01_seeds.py` |
| 11 | Two construct tests read a gitignored `cdk.out`, so they could pass on an older template. They synthesise their own now. | `tests/test_construct.py` |
| 12 | The tool chose silently between two rows on one key; `date` was required and never read; the prompt's field names were bound to nothing. | `agents/refagent/` |
| 13 | A run that spent and then failed reported less than it spent — the case the cap exists for. | `agents/refagent/agent.py`, `src/cost_cap.py` |
| 14 | `deploy.yml` set an output from every line of `pack`'s stdout and interpolated it into a shell in the credentialed job. | `.github/workflows/deploy.yml` |
| 15 | The construct read the two gateway endpoints under a parameter name nothing writes: refagent's stack could not have deployed. | `infra/construct/governed_agent.py` |
| 16 | `make validate`'s ruling-r check matched `S3` the AWS service as if it were seed S3. | `src/validate/checks.py` |
| 17 | **BLOCK B, ruled and repaired** (rulings s and t). One allow-list boundary was on every role the bootstrap stack makes, so the execution role could create nothing and the Budgets stop could not attach. Split per plane: the agent allow-list on agent-path roles only, a deploy-plane deny-list on the rest. The deny-list denies neither `iam:*` nor `sts:AssumeRole`, because either would be the wrong control firing. | `infra/bootstrap/app.py`, `tests/test_bootstrap.py` |
| 18 | The agent boundary did not **allow** `kms:GetKeyPolicy`. An allow-list caps by omission, so taking it out of the Deny at repair 1 was not enough: the boundary, not the key policy, would still have refused S6. | `infra/bootstrap/app.py` |

**Not repaired; for a seat, before this PR is undrafted.** Each is in the
PR body under **Unsure** with the seat and the milestone.

| # | BLOCK | Seat |
|---|---|---|
| A | The tool's return shape is not the one SPEC/00 §9 publishes. SPEC/00 is the authority, so either §9 is amended or the tool returns its fields. | Product |
| C | A fork PR skips the `evals` job, and a skipped required check counts as success on GitHub, so a fork PR merges with no `validate` and no pytest. | Security |
| D | S8's check is installed by the stack under test. A stack that never imports `infra.construct` is not checked, so what fired is narrower than false state 8. | Security |

## What refagent's first agent envelope found (run 35529132275)

`aadc735` records the first envelope of `scope: agent` this repo has ever
written. It is **UNMEASURED**, and the reason is not in the repo:

```
AccessDeniedException ... anthropic.claude-sonnet-5 is not available for this account
```

Fifteen goldens, fifteen identical refusals, and the control beside them
answering normally on Nova Micro. The account has never had model access
for Sonnet 5 enabled, and nothing before this run would have said so.

**Ruled, in `rulings/pr2-threshold-owner.md` (o and p).** The model was
pinned on `list-foundation-models` reporting `modelLifecycle: ACTIVE` in
us-west-2. ACTIVE says the model exists in the region; it does not say
this account may call it, and the two were read as one. refagent's model
is now `anthropic.claude-sonnet-4-6`, verified by a call rather than by a
listing, and `scripts/check_model_access.py` is what makes that check
repeatable. It is a script and not a `validate` check because it spends.
The cap stays at 150,000 as a **pre-run** number: ruling m makes an
over-cap envelope RED at its commit forever, so the cap has to be right
before the run, not calibrated after it.

What the envelope does show, and it is the first time any of it has been
in CI evidence: `F1_2` **pass** — S5's role without a boundary refused at
synth; `F1_1` and `F1_3` **fail** — S4's and S6's attempts have not been
made; `F1_4` **fail** — refagent cited nothing, because it answered
nothing. The cost-cap read 5,534 tokens against 150,000, all of it the
control's.

## What a reader can run to falsify this PR's own claims

```bash
uv sync --frozen

# Each seed, refused for its own reason and no other.
uv run pytest tests/test_m01_seeds.py -q          # S4 and S6 xfail: not yet attempted
uv run python -m src.bundle.verify tests/fixtures/bundles/unsigned   # exit 4, signature
uv run python -m src.bundle.verify tests/fixtures/bundles/altered    # exit 4, digest
uv run python -c "from pathlib import Path; from infra.construct import synth_refusal; \
  print(synth_refusal(Path('tests/fixtures/construct/extra_egress.py')))"

# The archive recipe is the one CI signed: this re-packs S1 and compares
# the digest with the one inside the bot's signature.
uv run pytest tests/test_bundle.py -q

# Both stacks, cdk-nag, and the committed reports held to this synth.
uv run make validate

# The gate reads the cap that stood at the envelope's commit, not today's.
uv run python -c "from src.verdict import gate; \
  print(gate.cap_at('55dadb2f221e60036bdba0b01fdb6eff025d74bc'))"   # 20000, not 150000
```

To falsify the construct's claim, add an egress rule to
`infra/construct/app.py` — any destination, any port — and run
`uv run make validate`. If it synthesises, the S3 check does not read what
it says it reads.

## What this PR does not show

- **No deploy has run.** `deploy.yml` is written and has never executed.
  The signature it would make, the image it would push and the load check
  it would run are all untested. Row 1 does not rest on any of them.
- **The rights table is read from the file, not DynamoDB**, in this PR's
  measurement. refagent's stack is deployed from `main` after this PR
  merges, so on a PR run there is no table; every observation records
  which source it read (`agent.rights_rows`, `rights_table` in the raw).
- **F1.4 reads existence, not correctness.** An answer passes the citation
  half if its `table_row` and `clause_id` exist in `data/`; it is not
  compared with the golden's expected pair. That is SPEC/01 §4 as written,
  and it is the weaker of the two things a reader might assume it means.
