---
# M06 PR 4 (#37), Engineering's key and the cold review, one file. Drafted
# from engineering-cold-reviewer's read of the diff. Product's file is
# pr4.md.
ruling: pr4-engineering
seat: Engineering
authorises:
  - tests/test_m06_seeds.py
evidence:
  - SPEC/00-overview.md#8-M06
  - milestones/README.md
  - milestones/M06/README.md
  - evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json
pr: 37
---

# Ruling: M06 PR 4, Engineering, with the cold review

Ruled by andaro74 as Engineering, 2026-10-02, as written.

## What this authorises

- **`tests/test_m06_seeds.py`**: S2's strict `xfail` marker removed, in the
  commit that filled S2's run file (`245eb9b`). With `observed` filled the
  test passes, and a strict marker would fail it as XPASS. The test reads
  that the attempt was recorded, not F6.2: F6.2 is `build`'s, from the
  observer's lookup (`pr1-engineering.md` NOTE 1). S3's marker stays: S3
  was not attempted.

## What was read

`engineering-cold-reviewer` read the diff `c7ef180...8a3754c` (15 files)
and row 6, not the PR body or commit bodies. It ran `src.ledger` (exit 0)
and `src.validate` (exit 0, 19 checks). It did not run pytest, because a
full run was in progress: that run read 773 passed, 1 skipped, 3 xfailed.
BLOCK 0, FINDING 3, NOTE 5. The report is verbatim in the PR body. The
repairs after it (one commit, prose only) were not read cold again.

## What holds (the reviewer's "Verified")

1. **Shape.** A close: the cell, the close detail, the explainer, the
   attestations, SPEC/00's amendments, `M07/open.md`, two run files and one
   marker. No reader built in the last PR.
2. **P5.** The only `evals/history/` files are `3ca05dd`'s, by
   `github-actions[bot]`; `245eb9b`, the stated reading, is its parent and
   `f6_2_standin.yaml` is not touched after it.
3. **The cell** equals `src.ledger`'s line character for character; State
   RED; 4 / 4. `src/baseline/` unchanged since `m00`.
4. **"blocked"** is a valid inference: `template.py` gives `F6_2` no
   reasons only on that state.

## Dispositions

| # | Finding | Status |
|---|---|---|
| F1 | `attestations.md` line 4 said F6.2 did not hold live | Repaired: "F6.1's live half and F6.3 were unread; F6.2 held, while the App refused every head" |
| F2 | `M07/open.md` row 8 said F6.2 did not read as held | Repaired to match rows 3 and 5 |
| F3 | SPEC/06 §5.1 not amended with SPEC/00 §10.5 | Repaired: an amendment note in §5.1 (Product, `pr4.md` §4 item 2); the full restatement is `M07/open.md` row 31 |
| N1 | The F6.2 table cites apps and times the envelope does not carry | Repaired: the close detail says which part is the envelope's and which is GitHub's check runs as the owner read them. The explainer gives GitHub's times without the source, in its plain register; kept |
| N2 | A RED condition without a verdict | Repaired: "holds, as at M05", with why S2's test passing is not a reader |
| N3 | Rows 9 and 31 name no milestone | Repaired: "M07, before 2026-10-31"; "M07, before S3" |
| N4 | SPEC/00 §8 M07 not amended | Recorded: `M07/open.md` row 31, for SPEC/07 |
| N5 | Seed-test counts not run by the review | Read by the full run: 773 passed, 1 skipped, 3 xfailed; `tests/test_m06_seeds.py` 7 passed, 1 xfailed |

`security-reviewer` (no Security path in the diff; read for the Security
claims, verbatim in the PR body), BLOCK 0, FINDING 8, NOTE 6:

| # | Finding | Status |
|---|---|---|
| S-F1 | Line 2's reads cite no record | Repaired: each read names its command; line 2 says the outputs are not committed, so each is the owner's read, not a record |
| S-F2 | "No permission was changed in PR 3 or PR 4" from one read | Repaired: "one read shows the grant on that day" |
| S-F3 | Stacks listed, not compared | Repaired: the heading and the line say "listed, not compared"; the bootstrap's update is not traced to a commit |
| S-F4 | Line 4 and row 8 against the envelope | Repaired (cold review F1, F2) |
| S-F5 | Row 2 names the risk but no bound | Repaired: row 2 lists what must be ruled before the grant |
| S-F6 | The App key's environment unread, not a precondition | Repaired: row 20 says it, and row 2's When waits for it |
| S-F7 | Rows 2 and 3 put a stronger key beside pull-request code | Repaired: row 3 says the key never enters a job that runs PR code |
| S-F8 | Nothing reads the App's permissions back | Repaired: in row 2, a reader that fails on a permission change no ruling covers (folded into row 2, so the row count stays 75) |
| S-N1 | "no token" | Repaired: "no personal access token, on the human's word" |
| S-N2 | `app_token()` with no repository mints every permission | In row 2 |
| S-N5 | Row 9 does not say who renews | Repaired: "Security (renews)" |
| S-N3, N4, N6 | The words; the "not attested" list; no subject for checks 1, 3 to 6 | No change needed |

## What a reader can run

```
uv run pytest tests/test_m06_seeds.py -q        # 7 passed, 1 xfailed (S3)
git show 245eb9b --stat                          # the run file and the one marker, before 3ca05dd
git diff c7ef180...HEAD -- src scripts infra .github agents thresholds.yaml   # empty
grep -n "F6.2" milestones/M06/attestations.md milestones/M07/open.md
```
