---
adr: ADR-0012
title: The grant of the platform's Apps, and the script that reads it back, are Security's
status: Accepted
date: 2026-10-02
seat: Product
authorises:
  - Security     # SPEC/00 §5 Security row: `scripts/platform_check.py`; `infra/platform_grant.yaml` under `infra/**`
  - Engineering  # SPEC/00 §5 Engineering row: `scripts/**` but for that one file
amendments: 0
---

# ADR-0012 — The Apps' grant, and the script that reads it back, are Security's

Raised by `security-reviewer` on M07 PR 2 (finding 5) and put to the
Security seat as item 13j of `milestones/M07/rulings/pr2-security.md`,
ruled as written on 2026-10-02. Ruled by Product at M07 PR 3
(`milestones/M07/rulings/pr3.md`), accepted on `main` at that PR's merge
commit (ADR-0008). ADR-0003 has used both its amendments, so a change to
path ownership is a new ADR.

## Context

From M07 PR 2 every job that holds an App's key first reads the App's
grant back from GitHub and stops on anything beyond what Security ruled
(`scripts/platform_check.py grant`). Three things decided what "beyond"
means, and none was on a Security path:

- the `grant:` block, in `milestones/M07/rulings/pr2-security.md`, under
  `milestones/**`, which is Product's;
- the repository the seeded relaxation may be pointed at, in
  `milestones/M07/runs/f7_0_owner_test.yaml`, Product's too;
- the reader itself, `scripts/platform_check.py`, under `scripts/**`,
  which is Engineering's. The same file holds the table of permission
  sets a token may be minted for, and `app_token()`.

So a pull request that widened the grant, or weakened the reader of it,
met `ruling-cited` for Product or `cold-review-ruling` for Engineering,
and no Security gate.

## Decision

1. **`infra/platform_grant.yaml` holds the grant**, and the repository
   the seeded relaxation may be pointed at. It is under `infra/**`,
   which is Security's already. It names, in `ruled_in`, the ruling file
   that rules it; the reader refuses it unless that file is a Security
   ruling on the checkout that carries a line starting "Ruled by".
2. **`scripts/platform_check.py` is Security's.** SPEC/00 §5's Security
   row names it; the Engineering row reads "`scripts/**` but for
   `scripts/platform_check.py`".
3. **`.github/CODEOWNERS` lists Engineering's scripts one by one**
   (`observe_*.py` as one pattern), because `validate` refuses a file
   that lines from two seats match. A script no line names matches none,
   and `validate` fails until it is listed.

## Consequences

- From the pull request after M07 PR 3, a change to
  `scripts/platform_check.py` or to the grant needs a Security ruling.
  The gates read CODEOWNERS from the base ref, so M07 PR 3 itself is
  read under the table as it stood: its change to the script is covered
  by Engineering's ruling, and says so.
- The block in `rulings/pr2-security.md` is left as the record of what
  Security ruled on 2026-10-02. Nothing reads it. A test holds the grant
  file to it, word for word but for ids filled in since.
- Still Engineering's, and still able to change what a keyed job does:
  `src/validate/agent.py`, `scripts/platform_pr.py`,
  `scripts/platform_upgrade.py`, `scripts/retire_agent.py`,
  `scripts/model_watch.py`, `scripts/observe_upgrade.py`, and whatever
  `uv.lock` installs (SPEC/07 §8). This ADR moves the reader of the
  grant and the mint, not every line a keyed job runs.
- A new script needs a CODEOWNERS line in the pull request that adds it.
  CODEOWNERS is Security's, so that pull request needs a Security
  ruling: a cost, taken knowingly.
- One person holds every seat (R1). This names whose ruling a diff
  cites; it does not add a reviewer.
