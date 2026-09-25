---
# M03 PR 1 (#19), Security's key. Product's file is rulings/pr1.md.
ruling: pr1-security
seat: Security
authorises:
  - .github/CODEOWNERS
evidence:
  - SPEC/00-overview.md#8-M03
  - SPEC/03-evals-regression-redteam-corpus.md
pr: 19
---

# Ruling: M03 PR 1, Security

Ruled by andaro74 as Security, 2026-09-25.
The `security-reviewer` report (1 BLOCK, 7 FINDING, 8 NOTE) is in the PR
body verbatim; it read the diff.

**`.github/CODEOWNERS`**: two lines, `/.claude/agents/docs-writer.md`
under `# seat: Product` and `/.claude/agents/red-teamer.md` under
`# seat: Rule Owner`, one login (R1). `make validate` holds each line
equal to the prompt's front matter.

**BLOCK 1, ruled before the PR opened.** `ruling-cited` reads the owner
table from the base, where no line names a prompt this PR adds, so no
ruling could have covered either file. The human ruled the gate's fix
(`10452f9`, Engineering): a `.claude/agents/*.md` is owned by the `seat:`
in its own front matter, read from the base when the file is there and
from the PR when it is new, as ruling files already were. Not `--admin`,
not a bypass. **This PR changes the gate that judges it** (NOTE 3): the
`ruling-cited` run on #19 is the PR's own `src/gates/`. That is the known
gap SPEC/03 §8 now names for `src/gates/` as well as `src/verdict/`;
taking the reader from `main` is Security's at M05.

**No workflow, infra or ruleset change.** Nothing touches AWS. The human
runs every deploy and every ruleset change.

**What Security holds for PR 2** (`pr1.md` has each row): the
`bedrock:*Guardrail*` deny narrowed for `ApplyGuardrail` in the agent
boundary, the eval role and the deploy boundary, one key, read back with
`simulate-principal-policy` before and after (F1); a
`bedrock:GuardrailIdentifier` condition on the agent's invoke grant (F2);
the promoter principal, its trust, the deploying role and the
bucket-policy route, named in SPEC/03 §6 before the ingest stack (F3);
the Object Lock mode and period (F4); `DeleteItem` and `Scan` for the
deploy role on the rights table (F5); read access to the runtime's table
marker (F6); `deploy.yml` on `data/rights_table.json`, with
`infra/workflows.sha256` in the same commit (NOTE 5); cdk-nag over the
ingest stack (NOTE 7). The human reads `cdk diff` before anything
touches AWS. At M05: S3 data events on the production bucket (NOTE 6),
the reader taken from `main` (NOTE 3).
