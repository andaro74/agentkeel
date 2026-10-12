---
# The Rule Owner's key over the one path this pull request changes:
# refagent's guardrail pin, version 5 to version 6, the id unchanged. The
# by-hand step 2 of milestones/M09/README.md ("By-hand steps before PR 3's
# run"), after the bootstrap deploy of 2026-10-12 built version 6 and before
# PR 3's run, so refagent's envelope at that run carries the baseline's digest.
ruling: refagent-version-6
seat: Rule Owner
authorises:
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M09
  - SPEC/09-per-agent-rules.md
  - milestones/M09/rulings/pr2-rule-owner.md
  - milestones/M09/rulings/pr3-security.md
  - docs/adr/ADR-0009-the-closed-list-of-relaxations-amended.md
pr: 51
---

# Ruling: refagent's guardrail pin moves to version 6 (Rule Owner)

Ruled by andaro74 as Rule Owner, 2026-10-12, as written.

## What moves

`agents/refagent/manifest.yaml` pins guardrail `1088aw3ujhyd` at version
`6` in place of version `5`. One line. Nothing under
`agents/refagent/rules/` changes, and `rules/baseline.yaml` is as PR 2
left it.

## Why it is one key (R2)

The guardrail id is unchanged, so ADR-0009 entry 4 (a guardrail rebuilt
under a new id) does not fire; no entry leaves a list under
`agents/refagent/rules/`, so entry 5 does not fire. `pr2-rule-owner.md`
ruled the split one key on exactly this condition: refagent's PII entries
stay in its file beside the baseline's, the merge dedupes them, the
guardrail keeps its id and gains a version. This pull request is that
version.

## What version 6 is

Built by the bootstrap deploy of 2026-10-12 (stack `AgentkeelBootstrap`,
`UPDATE_COMPLETE` 01:19 UTC; the deploy under `pr3-security.md`), from
`rules/baseline.yaml` merged with `agents/refagent/rules/guardrail.yaml`
and `redteam.yaml`. Its description reads

    rules sha256 41a0265a2e37b7dd18d24704889bb607e2bba00a4793be6458a89d182c97cbd7

and that is the digest `src/validate/agent_rules.digest` computes over
those three files as the tree holds them at `f5ecb25`. The stack's
`GuardrailVersionForTheManifest` output reads `6` and
`GuardrailIdForTheManifest` reads `1088aw3ujhyd`.

The rules on the call do not change: the same six topics, PHONE and EMAIL
as ANONYMIZE, the prompt-attack filter off. Version 5's description
carried the digest of refagent's two files alone; version 6's carries the
baseline's too, which is what F9.1 reads on an agent's guardrail and what
lets a page say refagent's runtime carries the baseline. Until this merges,
refagent's runtime carries version 5, the same rules, and no page calls it
the baseline's (`#50` Unsure R2-a).

## What must hold after the merge (F9.5)

`deploy.yml` redeploys refagent with version 6 on the call. On the
CI-written envelope that follows, refagent's `plants_fired` must read
**7 of 7** (g-013, g-015, g-016 to g-020) and `guardrail` and `redteam`
their M08 values. Under 7 of 7 is F9.5 firing: the split relaxed refagent,
and the finding goes to row 9's cell, not to a rewording.

## What a reader can run

```
git diff f5ecb25...HEAD --stat                 # agents/refagent/manifest.yaml (one line) and this file, nothing else
git diff f5ecb25...HEAD -- agents/refagent/rules rules/baseline.yaml   # empty
aws bedrock list-guardrails --guardrail-identifier 1088aw3ujhyd --region us-west-2 --query 'guardrails[-1].[version,description]'
PYTHONPATH=. uv run python -c "from pathlib import Path; from src.validate import agent_rules; r=Path('agents/refagent/rules'); print(agent_rules.digest(Path('rules/baseline.yaml').read_bytes(), (r/'guardrail.yaml').read_bytes(), (r/'redteam.yaml').read_bytes()))"
aws cloudformation describe-stacks --stack-name AgentkeelBootstrap --region us-west-2 --query 'Stacks[0].Outputs[?starts_with(OutputKey,`Guardrail`)]'
make ledger                                     # after the merge: refagent's latest envelope reads plants 7/7
```

A version 6 whose description is not the digest above, an id other than
`1088aw3ujhyd`, a change under `agents/refagent/rules/` in this diff, or
`plants_fired` under 7 of 7 on the envelope after the merge, makes this
ruling wrong.
