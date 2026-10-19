---
# M10 PR 4 (#57), the close. Engineering's key over the two Engineering
# paths this PR touches: the run test's marker in tests/test_m10_seeds.py,
# committed with the owner's observed block so the branch's CI envelope
# reads the run made; and tests/test_containment_stacks.py, following the
# destination policy back to PR 2's (Security's pr4-security.md). The cold
# review of the close is pasted below. Product's file is pr4.md, the Data
# Owner's pr4-data-owner.md, Security's pr4-security.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m10_seeds.py
  - tests/test_containment_stacks.py
evidence:
  - SPEC/10-public-caller.md#5-the-seeded-cases
  - evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json
  - https://github.com/andaro74/agentkeel/actions/runs/39143365127
  - milestones/M10/rulings/pr2-engineering.md
  - milestones/M10/rulings/pr3-engineering.md
pr: 57
---

# Ruling: M10 PR 4, Engineering

Ruled by andaro74 as Engineering, 2026-10-18, as written.

## The marker

`test_the_caller_run_was_made` in `tests/test_m10_seeds.py` loses its
`xfail(strict=True)` marker (`14ab792`): the run is made, `observed` is a
mapping in the same commit, and the test passes by its reader, the run
file. The file now shows 10 passed; `--runxfail` has nothing left to show.
The `expected_failure` marker object stays defined, unused, as the other
milestones' seed files leave theirs; the pre-existing `noqa: F401` import
stays. No other line of the test changes.

## The destination test

`tests/test_containment_stacks.py` asserts the destination policy's one
statement by equality (`Sid: ThePlatformAccountsDoorsSubscribe`, the
platform account as principal, `logs:PutSubscriptionFilter`, the one
destination ARN) and, on the real synth, the account and no condition
(`e05095c`, `0ebfdbd`), following `infra/security/app.py` back to PR 2's
policy for the reason Security gives. The test holds the template, not a
seeded case: no refused subscription from another account has been made,
and the comment says "stands", not "held" (security-reviewer N5).

## The envelope's provenance

The owner's `observed` block and the marker were committed and pushed
together, and the PR opened, before any document was written, so the CI
bot's envelope is of a tree whose only difference from `main` is that
commit and the destination policy with its test. `evals.yml` (run
39143365127) ran `scripts/observe_caller.py` twice, as `agentkeel-audit-read`
for the bucket (the five access-log and trail records, the answer record)
and as the eval role for GitHub (`#4` and the manifest at its merge), and
`build` composed `caller` from the file (`looked_up_at` 16:13:11Z); the
gate ruled GREEN on refagent's own run (`plants 7/7`); `record` committed
`evals/history/14ab792….json` as `github-actions[bot]` (`4de0fab`,
16:14:52Z). The `checks` job's pytest passed. Nothing under `src/`,
`scripts/`, `evals/goldens/`, `thresholds.yaml` or `src/baseline/` changed
in PR 4. No later commit of this PR touches a measured path; the fixtures
README under `tests/` was left unchanged for that reason (finding 17).

## Standing, this seat

| From | Item | Disposition |
|---|---|---|
| pr3 H | `time_epoch_ms` carries seconds on an HTTP API; the field keeps its name | Standing. The reader reads either unit by its size; the live lines read as 2026-10-18 on the envelope (the Data Owner's epoch check) |
| pr3 I | The quota test measures the template's rendered length; an intrinsic that renders longer could pass it and be refused | Standing. 1,106 characters of room in the execution role's default policy |
| pr3-engineering N4 | No test reads the observer's time window | Standing |
| pr3-engineering N5 | The action lists are the guide's; a deploy is the only reader of completeness | Standing; the door deployed |
| security-reviewer N4 (this PR) | Neither destination test asserts `RoleArn` is the subscriber role or `TargetArn` the stream | One line each at the next Engineering PR that touches the file; not in a close |
| data-owner D (this PR) | `_step_of`'s fallbacks pair a record to a step by its subject when no request id matches; a line with an unmatched request id and the right subject would hold F10.3 by construction. Not on this evidence: all five live records carried the observer's step | A test at the next Engineering PR: a line whose request id is in no `observed` entry is not held for the step its subject names |
| data-owner C (this PR) | The `PLATFORM` branch in `calls` is reached by a test only; `record()` filters the platform record by its null step first | Recorded; a comment at the next Engineering PR |
| pr2 F | `make plants` reads file presence; the run's marker, now off, was what said the run was not made | Closed by the marker |
| pr2-engineering (its two Unsure) | The observer imports three functions from `src/verdict/caller.py`; the M02 seed test fails on a dirty checkout | Standing, as at PR 2 and PR 3 |
| finding 17 | `tests/fixtures/README.md`'s run rows for M09 and M10 still read `observed: null` | The next Engineering PR; not changed at a close because `tests/` is a measured path and the change would write a second envelope for prose |

## Cold review of the close (verbatim)

Dispositions: F1 repaired in the close's last commit (the `m10` header row
names `infra/security/app.py` and says `cdk-nag, every stack` synthesises
the security stack with its report unchanged); N1 repaired (step 7 cites
GitHub's `mergedAt` and the commit's stamp, one second apart); N2 stands as
finding 25 and `pr4.md` Unsure 6; N3 recorded: the four claims that rest on
the owner's word are named as such in the close and are no cell's or gate's
input; N4 Product's (the seat files list themselves as M09's did, the key
given in words; `pr4.md` Unsure 8); N5 recorded for a `docs-current` that
is not built. The repairs touch `milestones/**` only, no measured path, so
the envelope the cell names is of the tree that ships.

> Read: the diff f05405f...a0c2fbf (20 files), `git log f05405f..HEAD` (e05095c, 0ebfdbd, 14ab792 andaro74; 4de0fab github-actions[bot]; a0c2fbf andaro74, linear on f05405f), milestones/README.md row `| 10 | M10 |` and the `m10` header row (line 55), milestones/M10/README.md's row table and close detail, the envelope's `caller` field. Not read: the PR body, commit bodies, feasibility.md.
>
> Ran (all read-only, nothing in AWS): `make ledger` exit 0; `make validate` 21 ok, exit 0; `uv run pytest tests/test_m10_seeds.py tests/test_m10_readers.py tests/test_containment_stacks.py -q` 61 passed; `tests/test_m10_seeds.py` alone 10 passed; `make plants` every reader "in the tree"; `git diff f05405f...HEAD --stat -- src scripts .github infra/bootstrap infra/construct evals/goldens thresholds.yaml rules data` empty; `git diff --stat m00 HEAD -- src/baseline` empty.
>
> **Checks that held (each falsifiable as stated)**
>
> 1. Measured cell. milestones/README.md row 10 field 7 == `make ledger` "as row M10 reads it" for `14ab792…`, byte-equal (3,336 chars). milestones/M10/README.md:18 `| Measured |` cell byte-equal to the same line. PRs used 4 / 4, State GREEN in both; docs/milestones/README.md:17 reads GREEN.
> 2. Numbers against the envelope `evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json` `caller`: admitted 1/1, refused 3/3; delivered minus time per step = admitted 96 s, none 78 s, stranger 107 s, bypass 235 s, platform test call 92 s (`step: null`); F10_2 pin `at8e36cosq1r:1`, plant `g-030`, blocked true; plants 7/7; F10_1..F10_4 read and held; `looked_up_at` 16:13:11Z. docs/milestones/M10.md:85-87 ("96, 78, 107 and 235 seconds ... in that order"), :91-93, milestones/M10/README.md close detail table (F10.1 to F10.5), step 6's four call times (03:32:31, 03:32:49, 03:33:16, 03:33:47) and record times (03:34:07, 03:35:03, 03:37:42), the map's "78 s to 235 s" (docs/compliance/map.md:43) all match. Request ids and bypass principal in milestones/M10/runs/f10_x_caller_run.yaml:119-122 equal the envelope's. 14ab792 touches only the run file and the marker; 4de0fab (bot) only evals/history; 16:04:18Z and 16:14:52Z as the close detail states. "F10_5 pass on every envelope since 917601d": the three envelopes carrying F10_5 all read pass, plants 7/7. PR 2's policy Sid `ThePlatformAccountsDoorsSubscribe` is at 917601d:infra/security/app.py:495, as "What a reader can run" says. GREEN rows 0, 2, 3, 9, 10 = five of eleven, as the §15 re-read says.
> 3. Rulings. Four files, each `pr: 57`, each with a body line "DRAFT, written by the session on 2026-10-18 ..." (pr4.md:47, pr4-engineering.md:25, pr4-security.md:30, pr4-data-owner.md:26); no body line starts "Drafted ". `authorises` union = all 17 non-evals/history paths in the diff; no path listed that the diff does not touch. Only `@@` in the diff is `@@COLD@@` at pr4-engineering.md:83.
> 4. Attestations: five numbered lines, five `_Signed: _` (lines 44, 64, 78, 93, 107). Line 1's claims checked: bot authorship of 4de0fab, run 39143365127 in every F-check URL, baseline unchanged since m00, code changes = 14ab792 + e05095c/0ebfdbd.
> 5. Shape: no reader, rule, bar, golden, workflow or grant change; one infra file, infra/security/app.py:96-102, with its two tests following it (tests/test_containment_stacks.py:266, :327). No new writer or reader of envelopes (P5 clean).
> 6. Forbidden words: "governed"/"secure"/"proven" appear in the diff only inside negations or quotations (attestations.md:99-100, pr4.md:1103); "forgery-proof" only negated (attestations.md:59-60). The explainer's "What GREEN does not mean" names the shared-account forgery path, the one-key agent half, the unrecorded no-token edge call, the single-issuer door, and that the caller was the owner.
>
> **FINDING 1** — milestones/README.md:55 (`m10` header row): "PR 4's code changes are the run test's marker in `tests/test_m10_seeds.py` and the destination test ... neither read by `validate`". PR 4 also changes infra/security/app.py (the destination policy, e05095c + 0ebfdbd), and `cdk-nag, every stack` does synthesise that stack (src/validate/checks.py:297 `"AgentkeelSecurity": "infra/security"`). The row's claim that validate reads none of PR 4's changes is wrong by one file; the check still passes (ran it). Settle: Product adds the file to the sentence, or states that the nag report for it is unchanged.
>
> **NOTE 1** — milestones/M10/README.md close detail step 7: "PR 3 merged (`#56`, `f05405f`, 05:37:56)". The merge commit's committer time is 2026-10-17T22:37:55-07:00 = 05:37:55Z. One second; likely GitHub's `mergedAt` vs the commit stamp. Settle: `gh pr view 56 --json mergedAt`, or cite the commit stamp.
>
> **NOTE 2** — docs/milestones/M10.md:98-100: "The door's own records are told from a forgery by the request numbers the owner wrote down." The run file says those ids were read from the door's access log (f10_x_caller_run.yaml:114-115), so the sentence rests on the owner's reading of a platform-account log group, which is the same account the forgery path sits in. Already homed as finding 25 / pr4.md Unsure 6; recorded here only so the ruling says the wording was seen.
>
> **NOTE 3** — Claims in this PR that the repository cannot falsify and that rest on the owner's word: the two refused security-stack deploys and their rollbacks (infra/security/app.py:92-93, pr4-security.md), 55 orphan pools (M10.md:109, README finding 3), the synthesised template equalling the deployed one (finding 26), "the `checks` job's pytest passed" (pr4-engineering.md:58). Each is named as such in the close; none is a cell or a gate input.
>
> **NOTE 4** — pr4.md `authorises` lists pr4-security.md and pr4-data-owner.md, and each of those files also lists itself. Double-keying a milestones/** path by a non-Product seat is harmless for `ruling-cited` (validate passed) but is a Product path under a Security/Data Owner `authorises`; the front-matter comments say the key is "given in words". Settle: Product's call whether a seat file may list itself.
>
> **NOTE 5** — docs/adr/ADR-0015…md:4 and ADR-0016…md:4 carry a YAML inline comment on `status: Accepted`. validate's ruling/ADR readers parse it (21 ok); if `docs-current` is ever built it should expect the comment.
>
> BLOCK: 0 · FINDING: 1 · NOTE: 5
