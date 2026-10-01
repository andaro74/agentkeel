---
# M06 PR 4 (#37), the close. Product's key. Engineering's file is
# pr4-engineering.md (the cold review, and S2's marker in
# tests/test_m06_seeds.py).
ruling: pr4
seat: Product
authorises:
  - SPEC/00-overview.md
  - milestones/README.md
  - milestones/M06/README.md
  - milestones/M06/attestations.md
  - milestones/M06/runs/f6_0_owner_test.yaml
  - milestones/M06/runs/f6_2_standin.yaml
  - milestones/M06/rulings/pr4.md
  - milestones/M06/rulings/pr4-engineering.md
  - milestones/M07/open.md
  - docs/milestones/M06.md
  - docs/milestones/README.md
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md#51-when-each-is-measured
  - SPEC/06-developer-template.md#7-expected-on-the-plant-row-6
  - https://github.com/andaro74/agentkeel/actions/runs/36886530498
  - evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json
  - milestones/M06/feasibility.md
  - milestones/M06/rulings/pr1.md
  - milestones/M06/rulings/pr2.md
  - milestones/M06/rulings/pr3.md
  - milestones/M06/rulings/pr3-security.md
  - milestones/M06/runs/f6_0_owner_test.yaml
  - milestones/M06/runs/f6_2_standin.yaml
pr: 37
---

# Ruling: M06 PR 4, Product

DRAFT for andaro74 as Product. Not ruled until this line reads "Ruled by".

## 1. What this PR is

PR 4 of M06, the close, and the last: 4 / 4. Product ruled option 1 on
2026-10-01: M06 closes RED at PR 4; S2 is attempted, S3 is not, and
`floresinnovations`' one clean attempt is kept for M07. This PR has S2's
`observed` entry and the reading stated before the run (`245eb9b`, pushed
first); the owner test's step 2 miss; row 6's Measured cell from `make
ledger`'s reading of the envelope for `245eb9b` (CI run 36886530498, bot
commit `3ca05dd`), State RED, 4 / 4; `validate` at `m06` in the ledger
header; `make ledger-plain`; the close detail; the explainer's "What
happened"; `attestations.md`; SPEC/00's amendments; this file and
Engineering's; and `milestones/M07/open.md`. It builds no reader and
changes nothing under `agents/`, `src/`, `infra/`, `scripts/`,
`.github/`, `thresholds.yaml`, `evals/goldens/` or `data/`. Its one
Engineering path is S2's strict marker, removed because the run file is
filled (`pr4-engineering.md`).

## 2. The reading

refagent GREEN in `mode: runtime`, ordinary 9/9, traps 2/2, guardrail
2/3, red team 5/5, plants 7/7, `regressed` 0. `template` at 15:48:23Z:
`F6_1` unread, `F6_2` held, `F6_3` unread, `F6_4` held. Row 6: **RED**,
because F6.1's live half and F6.3 are unread. `make ledger` exits 0.

**The statement before the run was wrong.** `runs/f6_2_standin.yaml`, pushed
before the run, said the observer would read owner-check #2 as
"unstable" (the anonymous reading at 15:40Z) and F6.2 as not held. The run
read "blocked", and F6.2 held. Nothing was changed after the run to agree
with either. The cell is the envelope's reading. The wrong statement is
recorded here and in the close detail, and the dependence on the token is
finding 2 (`milestones/M07/open.md` row 3).

**What F6.2 holding shows.** The App's failure on #2 carried "bypass_actors
is not shown to the App's token", which refuses every head. So the hold
shows that a stand-in's success does not satisfy a check bound to the App
by `integration_id`. It does not show the App refusing S2 for S2's own
fault. S2 also set no seat: its branch came from `main`, where all seven
were null (`milestones/M07/open.md` row 5).

The run is the reading for row 6 even if a later run on this branch reads
it differently. If one does, that is recorded beside it, and the cell
stays on `245eb9b`.

## 3. The owner's test, as S3's precondition (`pr3.md`)

Recorded in `runs/f6_0_owner_test.yaml`, not evidence for the cell. Step 1
missed at PR 3 (the ruleset differed from PR 2's export; repaired).
**Step 2 missed at PR 4**: owner-check #1 was failed at 14:24:31Z on the
seats, the goldens and the hidden `bypass_actors`. Steps 3 and 4 were never
possible. S3 therefore had no precondition met, which is why Product kept
the attempt for M07 instead of spending it.

## 4. What this PR rules (Product's paths), each a draft for the seat

1. **SPEC/00 §10.5**: "by the author" and row 6's `floresinnovations` are
   one person (`feasibility.md` §2, NOTE 23). §10.5 now names both, and
   says the quickstart is timed at M07 (`pr3.md`, "Stands, for later";
   cold review N3 on PR 3). `milestones/M07/open.md` row 7 for the ruling.
2. **SPEC/00 §8 M06, §10.1, §10.2**: cut 3's three guides to M07 (owed
   since `pr2.md` ruling 4, data-owner N10); Acts 1 and 2 to M07, moved
   with S3 and not cut; Act 3 to M07 as cut 2; cuts 1 and 2 recorded as
   taken (neither was built in M06). Act 2 was due at this close and was
   not recorded: a finding, `milestones/M07/open.md` row 30.
3. **"Governed"**: row 6's claim keeps its wording, since a claim is not
   rewritten at its close. The close, the explainer and the attestations
   do not repeat the word, or "secure" or "proven", about F6.1 to F6.3
   (cold review N4 on PR 3). `milestones/M07/open.md` row 8.
4. **No video row.** Nothing was recorded during M06, so no row is written
   in `docs/video/README.md`. M05's close wrote its row as a plan; this one
   does not, and the plan is `milestones/M07/open.md` row 1.
5. **PR 3's "no margin" (pr3-engineering N2)** ended as feared: the read at
   PR 4 missed, and the row closes RED with the finding, with no fifth PR.

## 5. Every Unsure item of #34, #35, #36 and #37

| Item | Where it ended |
|---|---|
| #34: the App check taken from the docs | The ruleset was read back at PR 3; the App's id read. The App's token is finding 1: `M07/open.md` row 2 (Security; Engineering) |
| #34: how an agent repository asks for the check; forgeable | Ruled R2 (`feasibility.md` §8) |
| #34: where Grafana runs; per-agent changes automatic or timed | Ruled R1, R4 (`feasibility.md` §8) |
| #34: goldens for a new agent, which checks, item 4's envelope | Ruled R5 to R7 (`feasibility.md` §8) |
| #34: PR 2's size | Cut 3 taken (`pr2.md` ruling 4) |
| #34: the second account suspended before S3; `andaro74` on Pro until M06 closes | `M07/open.md` row 11 (Product; Security), at M07 open |
| #35: S2's expected reading changed inside the measuring PR; a seat needs admin; R4 rows 5 and 8 | Ruled (`pr2.md` rulings 1 to 3) |
| #35: the seeded refusal for a tagged role | `M07/open.md` row 18 (Security) |
| #35: `TagResource`; the Metadata read; an owner as `admin` | `M07/open.md` row 13 (Security), at the owner test |
| #35: the schedule's delay in S3's clock | `M07/open.md` row 14 (Product; Threshold Owner) |
| #35: PR 2's last repairs not read cold | `M07/open.md` row 15 (Engineering), at M07 open |
| #35: the security account's update on the human's word | `M07/open.md` row 16 (Security) |
| #35: panel 1's columns in Glue `default` | `M07/open.md` row 10 (Security) |
| #36: `require_extra_approval_for_unattributed_changes` | `M07/open.md` row 12 (Security), at the owner test's step 3 |
| #36: PR 4 carries the read and the close | §4 item 5 above |
| #36: `b19db9a`, `cf92716` not read cold | `M07/open.md` row 15 (Engineering) |
| #37: the items in its body's **Unsure** | Each names its seat there; each is in this table's rows above or in `M07/open.md` |

## 6. Every Finding

Collected from `feasibility.md`, every ruling file of M06 and its
dispositions table, the seat reports in #34 to #36, and this PR's run.
Each is closed in M06 (the ruling that says where) or carried to
`milestones/M07/open.md` with a seat and a milestone. Those with no
complete home before the close, and where they went:

| Finding | Home |
|---|---|
| Finding 1: the App cannot read `bypass_actors` (the RED) | row 2 (Security; Engineering) |
| Finding 2: the observer's reading depends on the token; the stated reading was wrong | row 3 (Engineering; Security) |
| S3 not attempted; F6.1 live and F6.3 unread; Act 1 not recorded | rows 4, 30 (Product; Threshold Owner) |
| S2 set no seat; F6.2's hold made while the App refused every head | row 5 (Product; Engineering) |
| The owner test, steps 2 to 4 | row 6 (Product; Security) |
| F18 deploy widening; delta F1 private repository | row 17 (Security) |
| S-F6 tagged role; S-F8 workspace trust; S-F12 key environment; platform-architect N13 to N15 | rows 18 to 20 (Security) |
| pr3-security N5 (a ruleset relaxed after a success) | row 21 (Security) |
| pr2-engineering N1, N4 to N7 | row 22 (Engineering) |
| threshold-owner N6 (no two-key test on the new bar) | row 23 (Engineering; Threshold Owner) |
| data-owner N5, N7 | rows 24, 25 (Data Owner) |
| rule-owner: one guardrail, the agent's own code | row 26 (Rule Owner) |
| SPEC/06 §8's items without a milestone | rows 27, 28 |
| The knowledge base's fourth move; FRAGILE | row 32, with the carried rows |
| SPEC/06 §7's "five records" against four elsewhere | row 31 |
| The Grafana token's expiry, 2026-10-31 | row 9 (Security) |
| data-owner N9 (item 4 GREEN on any one pass) | closed: the explainer's last paragraph of "What happened" |
| threshold-owner N7 (a shallow clone reads today's bar) | closed: `evals.yml` checks out with `fetch-depth: 0`, which PR 4's run used |
| pr2-security delta N5 (`setup-temp`) | closed: `attestations.md` line 2, from the workspace's service-account list read 2026-10-01T15:45Z |
| pr1-engineering NOTE 1 (an XPASS is not F6.2) | closed: S2's marker off in `245eb9b`; the close detail says the test passing is not F6.2 |

`milestones/M06/open.md`'s rows that M06 did not close (4, 6 to 16, 18 to
48, by `feasibility.md` §6) are copied into `milestones/M07/open.md` as rows
33 to 75, each with its M06 row number.

## What a reader can run

```
make ledger                                   # exit 0; row 6 RED, 4 / 4, cell = the envelope for 245eb9b
python -c "import json;print(json.load(open('evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json'))['template'])"
git log --format='%h %an %s' c7ef180..HEAD    # 245eb9b (S2 and its stated reading) before 3ca05dd (the bot's envelope)
git show 245eb9b -- milestones/M06/runs/f6_2_standin.yaml   # "unstable" stated, before the run
uv run pytest tests/test_m06_seeds.py -q      # 7 passed, 1 xfailed (S3)
gh api repos/agentkeel-studio/owner-check/commits/e3a8083/check-runs --jq '.check_runs[]|[.app.id,.conclusion]'
grep -c "^| [0-9]" milestones/M07/open.md      # 75
grep -n "governed\|secure\|proven" docs/milestones/M06.md   # nothing
```
