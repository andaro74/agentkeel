---
# M07 PR 1 (#38), Security's key. One Security path is in the diff: the
# CODEOWNERS line for the specialist M07 adds. Drafted from
# security-reviewer's read of the diff 57b9bf6...01e8ff8. This file makes
# no grant and authorises none.
ruling: pr1-security
seat: Security
authorises:
  - .github/CODEOWNERS
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/open.md
  - milestones/M07/runs/platform_app_read.md
  - milestones/M07/runs/platform_app_environment.json
  - milestones/M07/runs/platform_app_branch_policies.json
pr: 38
---

# Ruling: M07 PR 1, Security

DRAFT for andaro74 as Security. Not ruled until this line reads "Ruled by".

## What this authorises

- **`.github/CODEOWNERS`**: one line, `/.claude/agents/legal-compliance.md
  @andaro74`, under `# seat: Product`, equal to the file's own `seat:
  product` (`make validate`'s CODEOWNERS check holds the two equal).
  SPEC/00 §5.1 adds `legal-compliance` at M07 (R8). Its tools are Read,
  Grep and Glob: it cannot write, run or fetch.

Nothing else. **No grant is made or authorised by this file**: not
Administration: write, not a second App, not a token, not an environment
or ruleset change. Those are ruled in `rulings/pr2-security.md`, before
PR 2's first commit, and made by hand after PR 2 merges.

## What was read

`security-reviewer` read the diff `57b9bf6...01e8ff8` (39 files) from a
file, and for context `scripts/platform_check.py`,
`.github/workflows/platform-check.yml`, `infra/ruleset/agent.json` and
`milestones/M07/open.md`. BLOCK 0, FINDING 14, NOTE 9. The report is
verbatim in the PR body. The diff changes no workflow, no `infra/**`, no
IAM and no key policy; the findings are on SPEC/07's plan for the grant
and on the run files.

## What was read back, by hand (not a check; nothing has fired)

`milestones/M07/runs/platform_app_read.md`: the `platform-app` environment
has one deployment branch policy, `main`, type branch;
`can_admins_bypass: true`; `PLATFORM_APP_PRIVATE_KEY` is a secret of the
environment and not of the repository. The App's installation cannot be
read with a user's token.

## Dispositions

| # | Finding | Status |
|---|---|---|
| 1, 2 | One key behind every permission set; R3 would put the same key on `agentkeel` | SPEC/07 §6 and §8 now say the split binds nothing with one key, and put three Apps to Security under R2; 5144253 is never installed on `andaro74/agentkeel`. **To rule before PR 2** (`rulings/pr1.md`, Unsure A). A grant |
| 3 | The dispatch from a branch came after the grant | Repaired (`8337ad8`): SPEC/07 §5.1, §11 R1 and S0's run file. It is made and read as refused before any grant |
| 4 | The new mint points beside agent data | Repaired in SPEC/07 §6: two jobs, as `platform-check.yml` has |
| 5, 8 | Who can change the keyed job; a ruling line's author is not read | Named in SPEC/07 §8. Each fix is a SPEC/00 §5 amendment: Unsure F |
| 6 | `selected` or `all`; the timed run's repository; `agent-template` | SPEC/07 §11 R2; Unsure C |
| 7, 9, 10 | Two mints in `post`; R4's store writable from `main` only; R7's three points | SPEC/07 §11, to rule before PR 2 |
| 11, 12 | Where the key is stored; the read's time, command and login | Read and committed (`runs/platform_app_read.md`) |
| 13 | S0's second attempt could read a skip as a refusal | Repaired in the run file: an unchecked head must exist, and only the environment's rejection counts |
| 14 | The seeded relaxation missed its place, a new head, the restore, and where its token is minted | Repaired in the run file but for the last, which is Unsure D |
| 15 | What the retirement deletes, and what the deleted key encrypts | The run file waits for R7's list, committed before the dispatch; Unsure H |
| 16 | No path back if the revert is not green | The run file: named before the swap is merged; Unsure G |
| 18, 21 | One flat grant in S0's fixture; not one endpoint's answer | Stands until R2 is ruled; PR 2 changes the fixtures' shape before the reader if it must |
| 19, 20 | No raised level or widened scope; `app_token`'s test read a default | Repaired (`4240d9e`, Engineering) |
| 17, 22, 23 | Notes | No change needed |

## What a reader can run

```
git diff 57b9bf6...HEAD -- .github infra   # one line, in .github/CODEOWNERS
make validate                              # "CODEOWNERS complete, single-owner, logins real": ok
gh api repos/andaro74/agentkeel/environments/platform-app/deployment-branch-policies --jq '.branch_policies[]|[.name,.type]'
gh api repos/andaro74/agentkeel/actions/secrets --jq '.secrets[].name'   # no PLATFORM_APP_PRIVATE_KEY
```
