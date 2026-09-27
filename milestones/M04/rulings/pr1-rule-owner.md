---
# M04 PR 1 (#23), the Rule Owner's key. Product's file is rulings/pr1.md.
ruling: pr1-rule-owner
seat: Rule Owner
authorises:
  - .claude/agents/red-teamer.md
evidence:
  - SPEC/00-overview.md#8-M04
  - milestones/M04/feasibility.md
  - milestones/M04/open.md
pr: 23
---

# Ruling: M04 PR 1, Rule Owner

The rulings below were made by andaro74 as the Rule Owner, on 2026-09-26
and 2026-09-27, each "as proposed". This file was drafted by the session
from them; the human signs it off before the PR opens. The `rule-owner`
reports (0/5/6 on the tree at `74fb9ed`; 0/3/8 on the diff at `688634c`)
are in the PR body verbatim.

**`.claude/agents/red-teamer.md`** reads the open milestone's SPEC, found
as the lowest-numbered row of `milestones/README.md` whose State is OPEN,
as well as SPEC/03 (`open.md` row 20; `70c2322`, `688634c`). Its tools
and its limits are unchanged. Not exercised at M04: no specialist is added
(R8) and it has no M04 seed.

**No rule changes.** Nothing under `rules/` or `agents/*/rules/`; the
guardrail pin stays `1088aw3ujhyd:5`. Nothing here is a relaxation.

**Held by this seat:**

| Item | When |
|---|---|
| ADR-0009's amendment on a definition's wording (two keys, read by `two_key.py`); until then this seat files a second key by hand for any change to a definition's wording (row 2) | M05 open, or the first change to `rules/**`, whichever comes first; it will be ADR-0009's last amendment |
| `guardrail.yaml`'s stale comments: "(M04)" at line 15, "until M04" at line 50, "at M04" at line 51, "a third party" at line 65 (row 17) | the next change to `rules/**` |
| `topics_apply_to: input` re-examined, and `g-014` blocked or masked (row 17) | M06, with retrieval |
| guardrail examples kept away from the attacks (row 21) | M05, with Promptfoo |
| PR 2's reader tests keep `CONTROLS` off or give the raws their named topics (note 7) | PR 2 |
