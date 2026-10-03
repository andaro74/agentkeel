---
# The ids pull request (#42), Security's key: two ids in the grant file,
# each read back from GitHub as the grant block names it. No permission
# is widened; the Apps and their keys were made by the human by hand.
ruling: grant-ids-security
seat: Security
authorises:
  - infra/platform_grant.yaml
evidence:
  - SPEC/00-overview.md#8-M07
  - docs/adr/ADR-0012-the-reader-of-the-apps-grant-is-securitys.md
  - milestones/M07/rulings/pr3-security.md
  - milestones/M07/runs/pr2_by_hand.md
pr: 42
---

# Ruling: the ids pull request, Security

Ruled by andaro74 as Security, 2026-10-03, as written.

Dates in this file are UTC (cold review F3: the human's clock is UTC-7,
so "2026-10-02 evening" there is 2026-10-03 here).

## What this authorises

Two values in `infra/platform_grant.yaml`, `app_id` under
`agentkeel-upgrades` (5169860) and under `agentkeel-observer` (5169892).
Nothing else in the file moves: `ruled_in` still names
`rulings/pr3-security.md`, and the permissions, environments and
installations are as that ruling and `pr2-security.md` set them.

## What was read before this was written (2026-10-03, 00:10 to 00:30 UTC, by the human and the session)

```
gh api orgs/agentkeel-studio/installations \
  --jq '.installations[]|[.app_slug,.app_id,.repository_selection,(.permissions|tostring)]|@tsv'
```
gave three Apps on the organisation, each on `all`:
`agentkeel-platform 5144253` with `administration: write, checks: write,
contents: read, metadata: read, pull_requests: read`;
`agentkeel-upgrades 5169860` with `contents: write, metadata: read,
pull_requests: write`; `agentkeel-observer 5169892` with
`administration: read, checks: read, contents: read, metadata: read,
pull_requests: read`. The observer was first created with the writer's
two write permissions; the human corrected it and accepted the change on
the installation, and the read above is the one after. Each environment
(`platform-upgrades`, `platform-observer`) read `can_admins_bypass
false`, one policy `main` branch, one secret. That `agentkeel-upgrades`
is on `andaro74` with `agentkeel` alone is the human's browser read.

## What this does, and does not

**It is the switch** (security-reviewer F2 on this pull request). The
keys were in their environments before this, and the reader refused
every keyed job on `main` for the null id (`scripts/platform_check.py`,
`NoGrant`): no token was minted for either App. With the ids on `main`,
each keyed job proceeds past the grant step when GitHub's read of the
App is within its block, and mints the App's token for that job. The
permissions do not widen; what the platform may do with the two keys,
from `main` alone, begins here. The scheduled `observe.yml` runs between
PR 3's merge and this merge were each `REFUSED: agentkeel-observer: the
grant holds no app_id for it yet`: 37076288316, 37078369773,
37082494705, 37085985257, 37087576069, 37089300274 and the ones after,
until the merge.

After the merge the reader compares what GitHub says each App holds
with the grant block, on every keyed job, and stops on anything beyond
it. That comparison has not yet run live with a non-null id; the first
keyed run after the merge is its first, and its `grant-<slug>` artifact
is the evidence (security-reviewer N3).

`ruled_in` still names `pr3-security.md`: the reader takes it as a guard
against a draft and nothing more; the ruling that authorises these two
values is this file, named in the two lines' comments (N5). "One
secret" per environment above is the human's read in the browser; no
token a job holds may list an environment's secrets (N6).

## To falsify

```
gh api orgs/agentkeel-studio/installations --jq '.installations[]|[.app_slug,.app_id]|@tsv'
grep -n app_id infra/platform_grant.yaml
```
The two ids differ, or an installation holds a permission the grant
block does not name: this ruling is wrong.
