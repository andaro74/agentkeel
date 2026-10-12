---
# M09 PR 3 (#52), the repair. Engineering's key over the Engineering paths
# this PR touches: the platform check's name reading and the tests that read
# both repairs. Security's file is pr3-security.md (the bootstrap), Product's
# pr3.md (this milestone's README and the run file, unchanged).
ruling: pr3-engineering
seat: Engineering
authorises:
  - src/validate/agent.py
  - tests/test_bootstrap.py
  - tests/test_m09_platform.py
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/rulings/pr2-engineering.md
  - milestones/M09/rulings/pr3-security.md
pr: 52
---

# Ruling: M09 PR 3, Engineering

DRAFT until it reads "Ruled by". Drafted by the session 2026-10-12.

## What this PR is

PR 3 of 4, the repair, under SPEC/09 §5.1's second named exception: the
platform's own deploy path needed repairing before an agent with `rules/`
could deploy, so PR 3 is the repair and the plant run is read by PR 4's
run, which the cell cites. Nothing here changes the claim, a seed, a
golden, a bar, `src/baseline/`, the run file, or `agent_rules`'s reading.
On this PR's own envelope `agent_rules` still reads not made, and row 9
still reads RED, as at PR 2.

## Repair 2: the held-pin check over the deploy's own copy

Deploy run 38259465892 (`agentkeel-studio/festival-desk` at `cd0ad604`,
2026-10-12 13:58 UTC), the first deploy of an agent with `rules/`, was
refused by `deploy-agent`'s held-pin check, which PR 2 added and which had
never run:

    FAIL the agent's name
         manifest.yaml: name festival-desk is held by agents/festival-desk/ in agentkeel

`deploy.yml` places the signed bundle at `agents/<name>/` in agentkeel's
checkout (the construct reads it there) and runs `src.validate.agent
evaluate --agent agents/<name>` with the registry row's pin.
`name_errors` refuses a name for which `agents/<name>/` exists in
agentkeel, to keep an agent repository from taking a platform agent's
name; in the deploy job the folder it found was the candidate itself. The
pull-request check never reads this: `platform-check.yml` checks the head
out to `agent-src` beside a clean checkout of `main`, and that is where a
name agentkeel holds is refused.

Changed, `src/validate/agent.py`: `name_errors(name, root, agent=None)`
takes the folder being checked and does not count it as the holder;
`evaluate` passes its `agent`. A caller that names no folder reads exactly
as before. The platform-check job is unchanged: at a pull request the
candidate is at `agent-src`, never under `agents/`, so a real platform
agent's folder is still a collision there. `deploy.yml` is not touched:
the alternative, a second copy of the bundle for the check, changes a
workflow and its hash under Security for the same reading.

Tests, `tests/test_m09_platform.py`: the three cases of the name check (the
candidate's own folder admitted; no folder named, or another folder with
that name, refused as before; a name nothing holds admitted either way),
and the call site (`evaluate` over a copy of the fixture at
`<tmp>/agents/festival-desk` hands `name_errors` that folder and refuses
nothing).

## Repair 1's tests (the bootstrap, Security's path)

`tests/test_m09_platform.py` reads the execution role's three guardrail
statements by Sid (the create on `Resource *` held to the request tag,
`TagResource` at create on `guardrail/*` held to the request tag, the
resource-tag statement unchanged), the deploy boundary's two tag denies
(the conditioned one on an untagged guardrail; refagent's by ARN in both
forms, flat), and that every action the `AWS::Bedrock::Guardrail` and
`GuardrailVersion` handlers hold in their permission lists is granted and
denied by no flat deny on `Resource *`. `tests/test_bootstrap.py`'s
collision test reads flat denies on `Resource *` only: a deny on one named
resource fires on that resource, not on the action, as a conditioned one
fires on its condition (`security-reviewer` NOTE 3 on this PR records the
narrowing).

## What this PR does not do

- No change to `deploy.yml`, `platform-check.yml`, the construct, any
  golden, bar, seed fixture or the run file. `observed` stays `null`; the
  run test's marker stays on. The run is PR 4's.
- No change to what the platform check refuses at a pull request.

## Cold review

Filled when `/cold-review` runs on this diff before the PR opens.

## What a reader can run

```
git diff f5ecb25...HEAD --stat                                  # the five files of repair 1, src/validate/agent.py, the tests, this milestone's documents and rulings
git diff f5ecb25...HEAD -- .github/workflows infra/construct evals/goldens thresholds.yaml src/baseline milestones/M09/runs   # empty
uv run pytest tests/test_m09_platform.py tests/test_bootstrap.py tests/test_m06_readers.py -q   # the two new tests among them
uv run pytest tests/test_m09_seeds.py -q                         # 8 passed, 1 xfailed: the run, not made
make validate                                                    # twenty-one ok
gh run view 38259465892 --log-failed | grep -m2 "the agent's name\|is held by"   # the refusal this repairs
```

A `name_errors` that admits a name a platform agent holds at a pull
request, a `deploy-agent` that still refuses the agent's own folder, or a
change under `.github/workflows/` in this PR, makes this ruling wrong.
