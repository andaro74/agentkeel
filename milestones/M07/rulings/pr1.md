---
# M07 PR 1 (#38), the plant. Product's key. One seat per file:
# Engineering's is pr1-engineering.md (with the cold review); Security's is
# pr1-security.md (the CODEOWNERS line). The rulings made at open in the
# other seats (Threshold Owner on the swap candidate; Security on the
# grant's timing) are recorded in feasibility.md section 2 and below, on
# Product paths; the PR touches no Rule Owner, Data Owner, Tool Owner or
# Threshold Owner path.
ruling: pr1
seat: Product
authorises:
  - SPEC/00-overview.md
  - SPEC/07-upgrade-retire-surfaces.md
  - .claude/agents/legal-compliance.md
  - docs/developer/quickstart.md
  - docs/milestones/M06.md
  - docs/milestones/M07.md
  - docs/milestones/README.md
  - docs/video/README.md
  - docs/video/milestones/M06.mp4
  - milestones/README.md
  - milestones/M07/**
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/feasibility.md
  - milestones/M07/open.md
  - milestones/M07/runs/platform_app_read.md
  - milestones/M06/rulings/pr4.md
  - evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json
  - docs/adr/ADR-0005-video-follows-the-tag.md
pr: 38
---

# Ruling: M07 PR 1, Product

DRAFT for andaro74 as Product. Not ruled until this line reads "Ruled by".

The rulings in section "Rulings" were made by andaro74 on 2026-10-01, in
the seats named, with the words "as proposed", before any seed; they are
recorded here, not made here. What this file still asks Product to rule
is everything after them: the placements in `feasibility.md` §6, the
dispositions in its §8, and the Unsure items below.

## What this PR is

PR 1 of M07, the plant: 1 / 4. M06 is closed (RED, tag `m06` on
`57b9bf6`). SPEC/07 first (`83eb558`), reviewed by `product-spec-reviewer`
(3 BLOCK, 26 FINDING, 12 NOTE; `feasibility.md` §1), every item ruled
(`66e6c0f`), SPEC/07 revised once (`addd8cc`), SPEC/00 amended
(`956fdc2`). M06's video (`1d18c2d`). Six seeds, one commit each, before
any reader: `c870bca` S0, `ef3d88a` S1, `3872c13` S2, `ea53ef4` S3 (its
run file made to parse in `a46c98f`), `e814efe` S4, `f36adee` S5.
`legal-compliance` and its CODEOWNERS line (`340a034`). Row 7, its README
and the explainer draft (`60a873f`). `feasibility.md` §2.5 to §7
(`01e8ff8`). Then the PR's own review repaired: the seeds' fixtures and
tests (`4240d9e`), SPEC/07, the run files and `feasibility.md` §8
(`8337ad8`), and this commit. It builds no reader, changes no workflow,
stack, bar, golden, rule or manifest, and makes no grant.

## Rulings

1. **BLOCK 1** (retirement; option a). A retirement arrives as a pull
   request the platform opens, setting `rollout: retired`; the agent's
   seats merge it; the deploy path retires instead of deploying.
   Archiving a repository is not the trigger. SPEC/00 §10.3 row 07 stands.
2. **BLOCK 2** (option a). A ruling file under `milestones/*/rulings/` is
   not "a person's edit". F7.1 reads every other path on an upgrade pull
   request.
3. **BLOCK 3** (option a). Taken at open and **not built in this
   project**, recorded in SPEC/00 §12: the knowledge base (its fifth
   move), the judge and FRAGILE, the Braintrust mirror, HITL as a Gateway
   tool with `ratings-helper`'s code, the gateway, Identity-only
   credentials, the Budgets filter, the graph diff, k6, Promptfoo and the
   CLI. Panels 3 and 4 are doc-only. **Not measured in this project**: the
   cached-answer seed, F3.5's second half, `g-014` as a plant, S5 of
   SPEC/05's live half. Six contradictions with M08's text, R6 and §15 are
   recorded in SPEC/00 §8 M07, ruled at M08 open, and owed to M08's
   `open.md` at M07's close. Rows 1, 4, 5 and 6 are RED, so §15's "at
   least seven are GREEN" cannot be met.
4. **The seeded cases and falsifiers** (SPEC/00 §8 M07 as amended): S0,
   the template's repair read by CI, and SPEC/06's S3 with Act 1,
   received; neither is ever cut. F7.0 is new and reads "exists" only
   (item 14): a quickstart over its bar does not fire it. F7.1 is
   reworded. F7.4 is read through Grafana's query API; Playwright is not
   used. "Platform major bump" reads "a platform bump; major recorded".
5. **Claim 6's later reading** (item 14). SPEC/06's F6.1 live half and
   F6.3 are read by `template` on M07's envelopes and quoted in row 7's
   cell. Row 6's cell stays on `245eb9b` and row 6 stays RED.
6. **SPEC/06's S2** (items 12, 13). A new head on `s2-standin` by the
   owner's one empty commit, read before owner-check #1 merges.
   `floresinnovations` is not touched.
7. **The swap candidate** (Threshold Owner; item 16). Haiku 4.5,
   `pinned_roles.m04_cheaper_swap`; its verdict is not stated. The
   fallback, named before any run: if its envelope is RED it is not
   merged and F7.3 is read on owner-check's platform upgrade reverted;
   `upgrade.taken` then stays under 3.
8. **One invocation after a retirement** (with Security; item 4), by the
   retire job, recorded raw.
9. **The steps and the cap** (item 30). Chained only where one needs
   another. `model-watch`'s swap and its revert are pull requests on
   `main` outside M07's cap of four, by a line in the ledger when they
   exist. If PR 2 slips, panel 2 with S4's and S5's readers lands in PR 3.
10. **The grant's timing** (Security; items 33, 36). After PR 2 merges,
    never before; the mint points and permission sets ruled in
    `rulings/pr2-security.md` first. After the security review of this
    PR: the dispatch from a branch is made and read as refused before any
    grant.
11. **`open.md` rows 7, 8 and 11** (items 4 and 5 of SPEC/07 §10):
    SPEC/00 §10.5 stands; row 6's claim keeps its wording, and no M07
    prose uses "governed", "secure" or "proven" of F6.1 to F6.3, F7.0 to
    F7.5 or the grant; NOTE 23 extends to S3's attempt at M07.
12. **The other findings and notes** of `product-spec-reviewer`, as
    proposed, one by one in `feasibility.md` §2's last table.
13. **M06's video** (`open.md` row 1). Product confirmed that it shows
    everything `docs/video/README.md`'s Shows cell lists, with no
    deviation from the script; the row gives the date as 2026-10-02, as
    the human gave it. 3:13 (192.6 s), 2,862,360 bytes, under both
    ceilings; recorded at tag `m06` (`57b9bf6`); committed as an LFS
    object whose oid is the file's sha256 (`d165a15b…`).

## The two runs of this PR

Read from the envelopes, not from this prose.

| Run | Commit | Verdict | p95 | Counts |
|---|---|---|---|---|
| First (36960565903) | `9f2ce07` | **RED**, on `F4_4` alone | 14,281 ms, 2.06 times the incumbent's median of 6,946 ms over 15 runtime envelopes; the bar is 2.0 | ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5, plants 7/7, regressed 0, `never_passed` `g-014`; 49,615 tokens |
| Second (36961169742) | `0f4b72a` | **GREEN**, 19 checks pass | 5,830 ms | the same counts; 48,676 tokens |

Nothing was stated about p95 before the first run. The second was stated
before it was made, in `runs/pr1_second_run.yaml`, pushed first (`0f4b72a`):
GREEN at or under 13,892 ms. It read as stated. The PR changes nothing
refagent runs, so the two runs measured the same bytes 30 minutes apart.
Both envelopes stay; the first is RED in `evals/history/` for good. The
run file's `observed` is left null: filling it would change a measured
path and spend a third run. `template` on both: `F6_1` unread, `F6_2`
held, `F6_3` unread, `F6_4` held, as at `245eb9b`. Neither says anything
about claim 7.

**The finding, for the Threshold Owner.** The last eight runtime
envelopes read 10,679; 11,434; 7,338; 8,927; 12,277; 8,423; 14,281 and
5,830 ms against a median of 6,946: seven of eight over it, one over the
bar. One run's p95 over about nineteen answers is close to its slowest
single call. A pull request that changes no code can go RED on it, and a
second run can clear it. The bar is not moved here (a move upward is two
keys); what to do about it is Unsure Q.

## For Product to rule with this file

- **`open.md` rows placed** (`feasibility.md` §6). The placements not
  ruled above are proposed there. "Named gap" rows are carried to M08's
  `open.md` at the close as gaps to re-rule, not as work.
- **The reviews' dispositions** (`feasibility.md` §8).
- **`legal-compliance`** (R8): written in this PR and run once, on the
  slate, the corpus, the goldens and S2 (0 BLOCK, 6 FINDING, 11 NOTE;
  nothing recognised as real). Its draft rows for `docs/compliance/map.md`
  are in the PR body; no page is committed here.

## Unsure, each with its seat and when

| # | Item | Seat | By |
|---|---|---|---|
| A | One App or three (SPEC/07 §6): with one key the permission split binds nothing. Proposed: three, each key in its own environment limited to `main`; 5144253 never installed on `andaro74/agentkeel`. Every App and permission is a grant | Security | before PR 2 (R2, R3) |
| B | `can_admins_bypass: true` on `platform-app`: inside the bound, or switched off before the dispatch from a branch | Security | before the dispatch (R1) |
| C | How a new agent repository enters the grant (`selected` or `all`), its effect on S3's clock, and whether `agent-template` is in it | Security; Product | before PR 2 (R2) |
| D | Where S0's third attempt mints its token: a dispatch input on `post`, or the attempt is not made | Security | before that attempt |
| E | Which run's envelope the cell cites, and where `main`'s observer stores what it read (writable from `main` only) | Security; Engineering | before PR 2 (R4) |
| F | Moving `scripts/platform_check.py` to Security's row, and reading a ruling commit's author: each a SPEC/00 §5 amendment | Product; Security proposes | before PR 2 |
| G | What is done if the swap's revert does not go green; whether the candidate's access stays | Threshold Owner; Security | before the swap is merged (R6) |
| H | What retirement deletes and keeps, what the key encrypts, and whether the retirement is also written to the audit bucket | Security | before PR 2 (R7) |
| I | The three limits as bars under `upgrade:` (4,500 s, 3,600 s, 3,600 s) | Threshold Owner | PR 2, before any attempt |
| J | Panel 2's source; the Grafana observer token's renewal before 2026-10-31 | Security | before PR 2 (R8) |
| K | A retired golden's citations stay checked (`open.md` row 25) | Data Owner | by PR 2 |
| L | The video row's date (2026-10-02, the human's) beside this session's local dates (2026-10-01) | Product | with this file |
| M | `legal-compliance` ran through a general-purpose agent given its prompt; its first run under its own name is owed | Product | PR 2 |
| N | A person's IAM user name and two account ids in written envelopes (legal-compliance 12) | Security | M08 open |
| O | The framework lines in the draft map are from the specialist's memory, unverified | Product | before the page is committed |
| Q | `F4_4`'s p95 bar went RED on a pull request that changes no code and GREEN 30 minutes later. Taking one stated second run was Engineering's choice here; whether a second run is allowed at all, and whether p95 is read over more calls or the bar restated, is the Threshold Owner's | Threshold Owner; Engineering | M07 PR 2, before its run |
| P | The repairs after the reviews (`4240d9e`, `8337ad8` and this commit) were not read cold again | Engineering | M07 PR 2 |

## What a reader can run

```
git show c870bca --stat   # and each seed: the seed, its tests, one README row, one SEEDS_M07 line, no reader
uv run pytest tests/test_m07_seeds.py -q              # 13 xfailed
uv run pytest tests/test_m07_seeds.py -q --runxfail   # 13 failed, each with feasibility.md section 3's message
uv run pytest tests/test_m06_seeds.py -q              # 7 passed, 1 xfailed (S3)
make plants     # S0 to S5, each reader "not in the tree yet"
make validate   # nineteen checks, ok
make ledger     # exits 0; row 7 OPEN, Measured empty, 1 / 4
git lfs ls-files | grep M06.mp4
gh api repos/andaro74/agentkeel/environments/platform-app/secrets --jq '.secrets[].name'   # PLATFORM_APP_PRIVATE_KEY
gh api repos/agentkeel-studio/owner-check/commits/0c596c1/check-runs --jq '.check_runs[]|[.app.id,.conclusion]'   # the false state, live
git diff 57b9bf6...HEAD -- src/validate src/verdict/build.py scripts .github/workflows infra agents thresholds.yaml evals data rules   # empty
```

Any seed test that passes, or fails for another reason, makes this PR's
plant wrong.
