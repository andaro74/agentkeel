---
# M02 PR 2 (#12), Security's key. Product's file is rulings/pr2.md.
ruling: pr2-security
seat: Security
authorises:
  - .github/CODEOWNERS
  - .github/workflows/gates.yml
  - .github/workflows/evals.yml
  - .github/workflows/deploy.yml
  - infra/workflows.sha256
  - infra/bootstrap/app.py
  # the seats and endpoint_allowlist fields only
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M02/runs/api_probes.yaml
  - milestones/M02/runs/row16_second_workflow.yaml
  - milestones/M02/runs/row10_first_deploy.yaml
  - https://github.com/andaro74/agentkeel/actions/runs/35734541276
  - docs/adr/ADR-0003-remaining-path-ownership.md
  - docs/adr/ADR-0008-a-ruling-is-on-main-at-the-merge-commit.md
pr: 12
---

# Ruling: M02 PR 2, Security

Drafted by the session; the human rules as Security before the merge.
Each item below is a decision `milestones/M02/README.md` ("For the
seats") asked Security to make at PR 2 open, with what was read by the
call (`runs/api_probes.yaml`) and what is still read on this PR's first
run.

## 1. `.github/CODEOWNERS` (ADR-0003 amendment 2)

The SPEC/00 §5 table as owner lines, one login per seat, the seat in a
`# seat:` line above each block. GitHub reads the login for routing only;
`require_code_owner_review` is false on the `main` ruleset and stays
false (R1). The gates read the seat, **from the base ref**, so a PR
cannot move a path to a seat whose ruling it carries; the PR that adds
the file, this one, is read against its own table and the gate's output
says so. A manifest is attributed field by field (ADR-0003 amendment 1).
`validate` holds the table complete and single-owner over every tracked
file, each `.claude/agents/*.md` under the seat its front matter names,
and each login answered by the API.

## 2. `gates.yml`: which job, which token, no fork condition

Two jobs, `ruling-cited` and `two-key`, one per required context; both
`permissions: contents: read`, no secret, no OIDC, **no `if:`**, so a
fork's PR runs them (a skipped required check counts as satisfied,
evals.yml BLOCK C). The checkout is the merge ref with full history; the
base sha comes from the event. Neither job reads the live ruleset.

**The live compare runs in `evals.yml`'s `checks` job**, inside `make
validate`, with `GITHUB_TOKEN` (`contents: read`) passed to that step and
to the `evals` job's copy. Read by the call: unauthenticated, the ruleset
endpoint answers 200 **without** `bypass_actors`; with a token GitHub
can name, it answers `[]`. So `validate` sends the token and treats an
absent list as "not shown to this caller", an error naming the token,
never a pass. **Still unread**: whether an Actions token is shown the
list. It is read on this PR's first `checks` run. If it is not, the
compare needs a token that is; a fine-grained PAT (`administration:read`
on this repository) as a secret is the only shape, a fork cannot read a
secret, and Security rules then whether the compare moves to the `evals`
job (which a fork already skips) with the fork's `checks` left with the
eleven other checks. That is a PR 3 repair, not a re-plant.

## 3. Which ruleset fields the compare reads (Unsure H, a)

`name`, `target`, `enforcement`, `conditions`, `rules`, `bypass_actors`.
Not `updated_at`, `created_at`, `node_id`, `current_user_can_bypass` or
`_links`: they say when and by whom the ruleset was read, not what it
does. S4 attempt 2 therefore leaves the compare green once
`bypass_actors` is restored, whatever `updated_at` says. Both the export
and the live ruleset must say `bypass_actors: []`.

## 4. The order of the ruleset edit and the export (Unsure H, b)

Ruled as follows, for the human to carry out after this PR merges:

1. Make `ruling-cited` and `two-key` required on the live `main` ruleset
   (`strict_required_status_checks_policy` stays true). Not before the
   merge: a required context nothing reports pins every open PR at
   "Expected".
2. Export the ruleset at once, the same day, to a fresh branch, `m02-pr3`, as its first
   commit, and open PR 3 from it before any seed PR (security-reviewer on PR 2, F3: the window is bounded by that opening) (`gh api repos/andaro74/agentkeel/rulesets/23685206 >
   infra/ruleset/main.json`). Until PR 3 merges that export, `checks` is
   red on every branch off `main` for "live differs from export" as well
   as for any seed. That window is accepted: `scripts/observe_pr.py`
   reads the job log for the line that names the seed's path and never
   the `checks` conclusion alone, so S3's and S5's red `checks` still
   prove what they should, and S1's and S2's expected checks are the
   gates, which do not read the ruleset.
3. Open the five seed PRs from `main`, then make S4's two attempts.
   Attempt 2's `make validate` is run on the `m02-pr3` branch, whose
   export matches live but for the actor, so the RED is the actor's.

## 5. The rule-suites API and `administration:read`

Read by the call: 401 unauthenticated, 200 with the human's token, three
evaluations, all `pass` (the merges of #9, #10, #11). A workflow's
`permissions:` block has no key that grants it, so `observe_pr.py` takes
`RULE_SUITES_TOKEN` when the environment has one and records the status
it got when it does not. **Whether a refused `--admin` merge appears
there at all is read at attempt 1** (SPEC/02 §5.1). If it does not, Door
3's first gate rests on S1's PR being unmerged and the human's own
output, `build.check_from_bypass` says which witness it read, and the
attestations say so at the close. Security decides at the attempt
whether to add the PAT as a secret for PR 3's `evals` job.

## 6. `AgentkeelM00EvalRole` and `infra/eval-role/` (Unsure E)

The stack was `UPDATE_COMPLETE` in the account on 2026-09-22 (this PR's
`describe-stacks`). This PR removes nothing. The human destroys the
stack (`npx aws-cdk@2 destroy AgentkeelM00EvalRole` from
`infra/eval-role/`), confirms `AWS_EVAL_ROLE_ARN` points at the
bootstrap stack's role and not this one, and PR 3 deletes the directory
under this seat.

## 7. `deploy.yml`, the Dockerfile pin and `infra/bootstrap/app.py` (row 10)

The five commits at the branch's base, made by the human before this
session: the deploy role's `GetTemplateSummary` and `DeleteChangeSet`
(the CloudFormation update path; deployed by hand, bootstrap stack
`UPDATE_COMPLETE` at 14:21:58Z), the deploy job on `ubuntu-24.04-arm`,
the build step refusing any image that is not arm64, the Dockerfile
pinned to `linux/arm64`, and `tests/test_deploy_image_architecture.py`
before the fix. AgentCore Runtime runs arm64 only; run 35734541276 shows
the four failures. **Read at PR 2**: the reuse branch's refusal by name
of `822fe2b5` will not fire at this PR's merge, because the Dockerfile is
in the bundle and the pin moved the digest (`runs/row10_first_deploy.yaml`,
the three digests). The merge builds fresh on arm64 under a new tag.
Security decides whether to delete `822fe2b5` before the merge or leave
it for a rerun. `observed_at_pr2_merge` is filled by the human from that
run: the load check's answer, cfn-exec's `vpc-lattice` actions from
CloudTrail, whether the arm64 runner image carries `docker` and `aws`.

## 8. `infra/workflows.sha256` and row 16

`gates.yml` and the changed `evals.yml` were committed unlisted (`0e78ef8`)
so that `workflow-hash` refusing a second workflow file could be
observed once (`runs/row16_second_workflow.yaml`), then listed. From this
PR, a workflow and this file edited together need this seat's ruling:
`ruling-cited` on `infra/**` (open.md row 7, first half). The second
half, hashing what a workflow runs, stays M05.

## 9. The stub's Security fields

`agents/ratings-helper/manifest.yaml`: `seats` all null (no IdP groups
exist), `endpoint_allowlist` the four names a runtime would need to pull
its image and call the model, and nothing reaches the rights table. No
runtime is built from it before M07.

## 10. The bot's exemption reads a name anyone can set (security-reviewer F1, cold review F4)

`bot_only` reads `git log --format=%an` for `github-actions[bot]`, which
`git config user.name` sets. A hand-written envelope committed under
that name is exempt from `ruling-cited` and is not a relaxation for
`two-key`. Ruled: the exemption stands until M05, when the reader
becomes something a committer cannot set (the push actor from the API,
or the envelope's signature); `docs/platform/overview.md` names it now
under "What is not enforced", beside the unsigned envelope it is one
face of. No seeded case at M02 (SPEC/02 §8).

## What a reader can falsify

```
curl -s https://api.github.com/repos/andaro74/agentkeel/rulesets/23685206 | grep -c bypass_actors   # 0: omitted
gh api repos/andaro74/agentkeel/rulesets/23685206 | grep -o '"bypass_actors":\[\]'                   # shown with a token
uv run pytest tests/test_validate_m02.py -k "ruleset or codeowners"
grep -n "if:" .github/workflows/gates.yml         # none
git checkout 0e78ef8 && make validate             # FAIL workflow-hash on gates.yml
MSYS_NO_PATHCONV=1 aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelM00EvalRole --query 'Stacks[0].StackStatus'
```
