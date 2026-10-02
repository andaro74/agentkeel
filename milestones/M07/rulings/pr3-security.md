---
# M07 PR 3 (to open as #40), Security's key. It makes no grant: each is
# made by the human, by hand. infra/platform_grant.yaml names this file
# as the ruling that rules it; until this file reads as ruled on main,
# every keyed job stops at its first step.
ruling: pr3-security
seat: Security
authorises:
  - .github/CODEOWNERS
  - .github/workflows/deploy.yml
  - .github/workflows/observe.yml
  - .github/workflows/platform-check.yml
  - .github/workflows/platform-upgrade.yml
  - infra/workflows.sha256
  - infra/platform_grant.yaml
  - infra/bootstrap/app.py
  - infra/construct/governed_agent.py
  - infra/security/README.md
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - docs/adr/ADR-0012-the-reader-of-the-apps-grant-is-securitys.md
  - milestones/M07/rulings/pr2-security.md
  - milestones/M07/runs/pr2_by_hand.md
  - https://github.com/andaro74/agentkeel/actions/runs/37023118799
  - https://github.com/andaro74/agentkeel/actions/runs/37047341001
  - evals/history/af8835fad82709e2385bf4eff97a175e069bf855.json
pr: 40
---

# Ruling: M07 PR 3, Security

Ruled by andaro74 as Security, 2026-10-02, as written.

Each item is a recommendation with its alternative. Nothing here has
fired on a seeded case or run live. No document may say otherwise.

## 1. The workflow fix (`f5d2f6c`)

`deploy.yml`'s `sign-agent` staged nothing: it uploaded three paths under
two roots, GitHub rooted the artifact at their common parent, and
`deploy-agent` did not find `bundle.cosign.json` (run 37023118799). The
fix stages the three files under one folder and uploads it whole.
`deploy-agent` is unchanged. Two tests hold the layout. **It has not run
on `main`**: the first deploy run after the merge is its measurement.

## 2. Item 13 of `pr2-security.md`, as it stands

That file's first line rules it "as written", and as written it carries
13a to 13n, each with a recommended option, under a heading that says
"not ruled". The seat said in the session on 2026-10-02 that item 13
(13a to 13n) is ruled as written. Ruled here by item, for the ones PR 3
builds:

| Item | As built in PR 3 |
|---|---|
| 13h | `agentkeel-model-watch` and `agentkeel-envelope-row-put` named in the construct's `PLATFORM_ROLES` and in refagent's key policy (`530bf98`). A Deny made wider; no Allow changes. refagent's key takes it at B2, by hand |
| 13i | `deploy.yml`'s `retire-agent` holds the retired head's manifest to the one at the registry row's commit, before the registry or the stack is touched (`eea5508`) |
| 13j | The grant is `infra/platform_grant.yaml`; `scripts/platform_check.py` is Security's (ADR-0012). The CODEOWNERS diff was shown to the seat and agreed before it was committed (`54a4f66`). It binds from the next pull request |
| 13l | The keyed `open` job reads the template itself, refuses a plan made from another commit, and holds each proposed file to the template's text and the guardrail to `main`'s (`fe0431a`) |
| 13k, 13m | Accepted as PR 2 left them; nothing built |
| 13n | PR 4's, after the relaxation is made |

## 3. The observer's keyed job (security-reviewer 12 on PR 2)

Tokens minted first, read-only, one per repository the run files on
`main` name; the key let go before any read; no agent repository's tree
packed beside them; an artifact fetched from GitHub's storage with no
credential; each token revoked when the observation is written
(`e83ef7f`, `127d7fc`). No separate keyless job: the App's reading is
what the key is for.

## 4. To rule: when B2 and B3 are deployed

`runs/pr2_by_hand.md` first said "from the branch `m07-pr3`". Three
reports named it (security-reviewer 5, platform-architect 2, cold review
F2): refagent's key policy would be changed from a head no ruling
covers.

- **Recommended: after this file is ruled, from one named commit of
  `m07-pr3`, with the `cdk diff --strict` output kept**, and the commit
  written in the table in `runs/pr2_by_hand.md`. One deploy; the two
  roles exist before the merge.
- **Alternative: after the merge, from `main`.** The cleaner record.
  Nothing before the merge needs the two roles.

Either way `AWS_MODEL_WATCH_ROLE_ARN` is set last, after the swap's
statement is pushed.

## 5. The two App ids

`infra/platform_grant.yaml` holds `app_id: null` twice at the head the
seats reviewed. The ids go in a commit of their own when the seat gives
them. **That commit is after the reviewed head** (security-reviewer 4,
cold review N5): it changes two values the block marked "filled when the
App exists" at PR 2, and nothing else. If the ids are not in before the
merge, the next pull request that can carry them is PR 4, the close, and
S1 and the observer's keyed run wait for it.

## 6. The seat reviews, and what was done

`security-reviewer` and `platform-architect` read the diff
`3bfd074...936eb17` (38 files) from `.git/cold-review.patch`. Both
reports are in the pull request's body, verbatim.

**security-reviewer: BLOCK 0, FINDING 5, NOTE 19.**

| # | Finding | Status |
|---|---|---|
| 1 | The grant names a ruling file that was not in the tree | **This file.** A test holds that the file the grant names exists and is a Security ruling (`tests/test_m07_readers.py`). Whether it is ruled is the seat's line, and `cold-review-ruling` holds the merge to it |
| 2 | `ruled_in` ties the grant to a ruling by name, not by content | **Said**, in the file's header and SPEC/07 §12. Not repaired: a hash in the ruling would have to change with the ids' commit. `ruling-cited` on `/infra/` holds a later change. The seat's to rule if it wants the hash |
| 3 | The files that hold PR 3's new checks stay Engineering's | **Open, the seat's.** Named in ADR-0012 and SPEC/07 §12. A path move is an ADR. To M08's open list |
| 4 | Two `app_id` are null at the reviewed head | Item 5 above |
| 5 | B2 from the unmerged branch | Item 4 above. `runs/pr2_by_hand.md` corrected: the guard sentence restored, the choice put to the seat, a table for the commit deployed |
| 9, 10 | "Byte for byte" was a text compare; a template file that is not UTF-8 crashed the job | **Repaired** (`4fd46f8`) |
| 14 | The observer's tokens were never revoked | **Repaired** (`127d7fc`) |
| 15 | "To `api.github.com` and nowhere else" was not checked | **Repaired** (`127d7fc`): any other first address is refused |
| 18 | CODEOWNERS' comment said a new script matches no line; `observe_*.py` is a pattern | **Comment and ADR corrected** (`62c7bce`). The lines are as the seat agreed them |
| 6 to 8, 11 to 13, 16, 17, 19 to 24 | Notes | Need nothing, or are said where they stand. 17: `seeded_repository()` reads the grant file without the ruled check; the `grant` step runs first and does check. 24 is cold BLOCK 1 |

**platform-architect: BLOCK 0, FINDING 6, NOTE 7.**

| # | Finding | Status |
|---|---|---|
| 1 | The diff cited Security rulings the tree did not hold; "ruled" against a heading that says "not ruled" | Item 2 above, and this file |
| 2 | B2 by hand from an unmerged branch | Item 4 above |
| 3 | What is deployed in the security account rests on one person's statement | **Owed, by hand**: the sha256 of the template synthesised at the commit, and the same hash of the template CloudFormation stores, read by `hector.flores`. A row in `runs/pr2_by_hand.md`'s table. Said in SPEC/07 §12 |
| 4 | A platform role added after an agent's key exists fails that agent's stack updates, its retirement included | **Open, the seat's.** No key exists yet, and PR 3's two names land before the first. Said in SPEC/07 §12. PR 4 must not change `PLATFORM_ROLES`. To M08's open list |
| 5 | "No role the platform creates" is wider than the list | **Reworded** on a template agent's key (`740de6e`). refagent's key says the same sentence and is left: changing a live key's description is a change to that key. The seat's to rule; to M08's open list |
| 6 | The Deny for the two new roles has no seeded case | **Said**: "named in both lists", never that it works |
| N7 | `same_errors` reads a field null when deployed and removed at the retired head as unmoved | Left: the construct reads both alike. Said here |
| N9 | The bundle put under `bundles/` is the artifact's file; nothing compares its digest with the verified one | **Open, the seat's.** Not repaired in PR 3: it is a new step on the deploy path the fix has not yet run on, and a fault in it would have no pull request left. Said in SPEC/07 §12; to M08's open list |

## What a reader can run

```
uv run pytest -q tests/test_m07_workflows.py tests/test_validate_workflow_hash.py
uv run pytest -q tests/test_m07_readers.py -k "grant or relaxation or template or proposed"
uv run pytest -q tests/test_m07_platform.py -k "retired_head or deployed_commit"
uv run pytest -q tests/test_m07_observer.py -k "mints_first or storage_host or tree_is_fetched"
uv run pytest -q tests/test_bootstrap.py tests/test_construct.py -k "administer or key"
make validate                                   # workflow-hash, CODEOWNERS complete, cdk-nag
gh api orgs/agentkeel-studio/installations --jq '.installations[]|[.app_slug,.app_id,(.permissions|tostring)]|@tsv'
gh api repos/andaro74/agentkeel/actions/runs/37023118799/jobs --jq '.jobs[]|[.name,.conclusion]|@tsv'
```
