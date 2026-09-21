# Carried into M02

Started at M01 PR 1, because some items already had M02 as their date
when M01 opened. The M01 close adds whatever else M01 leaves, and
`/open-milestone` reads this file first. An item dated "before M02 PR 1"
is answered before that PR's first commit.

| # | Item | Seat | When |
|---|---|---|---|
| 1 | `cold-review-ruling` passes on a ruling the PR carries itself: its checkout is the PR's merge ref, so a ruling the PR adds counts. Known and by design at M00; the workflow header says so. It is not R9's line, which reads: "No PR in this repo merges before its ruling file is on `main`." Carried with `ruling-cited` (Security ruling E, M01 PR 1; raised by the `security-reviewer` report on M01 PR 1). | Security | M02 PR 1 |
| 2 | M01's video. From M01 a milestone's video is committed in the next milestone's PR 1 (ADR-0005 amendment 1). Recorded on `main` at tag `m01`, ≤ 5 minutes and ≤ 40 MiB, committed as an LFS object in M02 PR 1 with its entry in `docs/video/README.md`. | Product | M02 PR 1 |
| 3 | Retire `g-012` (Finding F0.1): `retired: M02`, never renamed. The two-key "merged properly" case of SPEC/00 §8 M02, Door 2. M01 open item 24. | Data Owner | M02 PR 1 |
| 4 | The replacement trap is `g-021`, a sequel that does not inherit the original's rights (`sequel_no_inherit`). The frozen control cannot emit that code, so it never passes; P7 allows that. `g-016` to `g-020` stay red-team at M03. M01 open items 25, 26. | Data Owner, with Threshold Owner | M02 PR 1 |
| 5 | `validate` diffs the live `main` ruleset against `infra/ruleset/main.json`, and fails unless `bypass_actors` is `[]`. M01 open item 31. | Security | M02 PR 1 |
| 6 | "CI-written" becomes real with `two-key` (`GITHUB_ACTIONS == "true"` is an environment variable). M01 open item 8. | Engineering | M02 |
| 7 | The workflow-hash check can be edited in the same PR as the workflow it guards, and it hashes the workflow's text only, not the `Makefile`, `src/` or `scripts/` it runs (`infra/ruleset/README.md`). `ruling-cited` on `infra/**` closes the first. M01 open item 29. | Security | M02 |

## Carried from M01 PR 2's cold review (Product, `.claude/skills/**`)

**A cold review read the tree, not the diff, and nothing would have caught
it.** Of the four seat subagents `/cold-review` called on M01 PR 2, three
reported that Bash was unavailable to them, so they reviewed the tree at
HEAD instead of `git diff main...HEAD`. Their findings therefore cannot say
which of them this PR caused and which predate it, and every one had to be
re-checked by hand before it could be triaged.

The skill names which subagent to call per path and says nothing about the
tools each needs. `make validate` does not read subagent definitions. The
only reason this was noticed is that three of the reports opened by
admitting it — had they not, the review would have read as four seats
agreeing on the state of a diff none of them had seen.

Settle at M02 by one of: granting Bash in each `.claude/agents/*.md` whose
seat reviews a diff; or a line in `.claude/skills/cold-review` requiring
each report to state whether it read the diff or the tree, so a report that
read the tree is visibly a weaker witness. M02 is the milestone whose claim
is that seat-owned files change only with a ruling, and a review that cannot
see the change is that claim's blind spot.
