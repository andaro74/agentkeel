---
# M01 PR 3 (#9), the cold review. Ruling B: one seat per file. This file is
# Engineering's ("that it works"); the seats' own keys for the paths the
# repairs touch are in pr3.md (Security), pr3-engineering.md (Engineering),
# pr3-product.md (Product) and pr3-threshold-owner.md (Threshold Owner).
ruling: pr3-cold-review
seat: Engineering
authorises:
  - milestones/M01/rulings/pr3-cold-review.md
evidence:
  - SPEC/00-overview.md#8-M01
  - milestones/README.md
  - milestones/M01/rulings/pr3.md
  - milestones/M01/rulings/pr3-engineering.md
  - milestones/M01/rulings/pr3-product.md
  - milestones/M01/rulings/pr3-threshold-owner.md
  - evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json
pr: 9
---

# M01 PR 3 (#9) — the cold review, and what was done with it

Three reports, run on the tree at `e319528` and pasted verbatim into the PR
body:

| Reviewer | Read | BLOCK | FINDING | NOTE |
|---|---|---|---|---|
| `engineering-cold-reviewer` | the diff against `main` and ledger row 1, nothing else | 1 | 6 | 7 |
| `security-reviewer` | workflows, infra, IAM, the key policy | 0 | 8 | 9 |
| `threshold-owner` | how the model id, version and region are recorded and checked | 0 | 4 | 6 |

Each item's disposition is below. The seat that ruled it is named. Repairs
are their own commits, after `e319528`, and none is mixed into a commit the
reviewers read. Repair 2 touches a measured path (`src/verdict/gate.py`), so
**PR 3 measures again**: the envelope that counts is CI's for the head this
PR merges, not `b3a4969c`'s.

## The BLOCK

| # | Item | Disposition |
|---|---|---|
| B1 | Claim 1's second half had no reader that could go RED. Both version 2 envelopes in history say `mode: runner`, and the gate read them GREEN | **Repaired.** Ruled by Product and Engineering as option (a). `gate.measured_at()` shows a row in `READ_IN_THE_RUNTIME` (M01) as **UNMEASURED**, with `not read in the runtime (mode …)`, when its agent envelope is not `mode: runtime`. `src/ledger.py` passes the row's milestone, and its existing check refuses a GREEN state beside that cell. A pull request's own verdict is unchanged: option (b), UNMEASURED at the gate, would have deadlocked every PR that changes refagent. Held by `test_row_1_is_unmeasured_on_the_real_runner_envelope`, which runs on `b3a4969c` itself, and by `test_row_1_cannot_close_green_on_a_runner_envelope`. |

## FINDINGs

| # | Source | Finding | Disposition |
|---|---|---|---|
| 1 | cold F1 = threshold F1 | T2's region check compares the pin with the pin | **Ruled** (Threshold Owner): T2 reworded in `pr3-threshold-owner.md` and ADR-0007. The region is the request region the client was built with. The check guards against a changed runner or a hand edit, not against routing. Carried to M04. |
| 2 | cold F2 = threshold F3 | A version 1 agent envelope skipped every ADR-0007 check | **Repaired.** The gate REJECTs one unless its commit is at or before `7f8d0ae`, where ADR-0007 was accepted. All 23 version 1 envelopes in history are, which `test_the_version_1_envelopes_in_history_are_all_before_adr_0007` holds. |
| 3 | cold F3 | The S7 seed as committed now refuses at build, not RED | **Repaired.** `test_s7_as_committed_is_refused_at_build_since_adr_0007` holds the unmodified seed's exit 3, beside the overlaid reading. Row 1's Expected cell says so (Product). |
| 4 | cold F4 | pr3.md item 3 contradicted the ledger on when tenancy is read | **Repaired.** The row now says: the merge is the first deploy, and the reading is PR 4's run. |
| 5 | cold F5 | The read-back tables could not be re-run from the tree | **Repaired.** `scripts/read_back_grants.py`, committed, 50 rows, exits 1 on any mismatch. Re-run 2026-09-22: 0 mismatches. |
| 6 | cold F6 | ADR-0007 overclaimed: "the envelope says so", "`where`, mapped" | **Repaired.** Both lines corrected. |
| 7 | threshold F2 | The pin's `id` was never checked | **Repaired.** The gate refuses a pin whose `id` and `profile` disagree. |
| 8 | threshold F4 | `thresholds.yaml:13` named Sonnet 5 (PR 2 finding 30) | **Repaired**, one key (Threshold Owner): a comment only, no bar moves. |
| 9 | security F1 | A PR can make its own envelope say `mode: runtime` by editing the lookup code | **Recorded** (Security, Engineering). It is the known M02 gap, "the envelope is written by the PR's own code" (`pr3.md`, "What B2 does not close"), now reaching `mode` too. **Condition on the close:** M01 PR 4 touches nothing under `src/`, `scripts/`, `agents/` or `.github/workflows/`, and its cold review checks that before its envelope is read. |
| 10 | security F2 | The bytes can change mid-run | **Recorded.** PR 4 triggers no deploy (see 9). M02. |
| 11 | security F3 | A rerun of the same bundle cannot push; the image is not reproducible | **Repaired**, the rerun half: `deploy.yml` reuses the image already pushed under the bundle's tag, via `ecr:BatchGetImage`, which the deploy role holds. **Recorded**, the reproducibility half: the base image is by tag, the packages by range, and `agents/__init__.py` sits outside the bundle. The wording now says "bundle", not "bytes". M02. |
| 12 | security F4 | A failed first deploy is sticky; only an admin can recover | **Recorded** (Security). Recovery is the human with admin (R1). The deploy role is not widened with `DeleteStack`. |
| 13 | security F5 | Which principal resolves the SSM parameters | **Partly settled.** All ten `/agentkeel/security/*` parameters exist (read 2026-09-21). Which principal resolves them is read by the first deploy, and a failure there is clean: it happens at the change set, before any resource. |
| 14 | security F6 | The agent role's logs and KMS grants were on `*`, with a wrong cdk-nag reason | **Repaired.** Log streams are scoped to `/aws/bedrock-agentcore/runtimes/*`. KMS is on `key/*` conditioned on `kms:ResourceAliases` = `alias/agentkeel-refagent`. The reason is rewritten. `test_the_roles_logs_and_key_are_its_own_not_the_accounts`. |
| 15 | security F7 | cfn-exec's `vpc-lattice` actions are on `*` | **Recorded** (Security), as pr3.md Unsure 3. Scope from the first deploy's CloudTrail, at M02. |
| 16 | security F8 | A workflow and its hash can be edited together, by anyone with write | **Recorded.** The known M02 gap. |

## NOTEs kept, because they will matter later

- **cold N2.** `runtime_for_tree.py` exits 0 on every *lookup* failure. An
  import error fails the step. The docstring now says so.
- **cold N4.** `gate.manifest_at` falls back to the working tree when git
  cannot show the commit. CI checks out full history (`fetch-depth: 0`).
- **cold N5.** The refagent NagReport has two IAM5 rows under one reason.
- **cold N6.** The ruling that closes PR 3 cites CI's envelope for the head it
  merges.
- **cold N7.** The Makefile exit test skips where `make` is absent. CI's run
  is its evidence.
- **security N2.** The deploy role's `PassRole` has no `iam:PassedToService`.
  Tightening it is a bootstrap redeploy. M02, with F8.
- **security N3.** The agent boundary allows `bedrock-agentcore:*`. Not new.
- **security N5.** A change to `data/rights_table.json` does not trigger a
  deploy, so it does not reload the table.

Dropped because they will not matter: cold N1, and security N6 (stale prose,
repaired); cold N3 (repaired with F3); security N1, N4, N7 to N9 and the
threshold NOTEs (confirmations).

## What a reader can run to falsify this file

```bash
uv sync --frozen

# B1: row 1 is UNMEASURED on the real runner envelope; its own verdict is GREEN.
uv run python -c "
from pathlib import Path; from src.verdict import gate
p = Path('evals/history/b3a4969c76b013a4fcdad7ea572f05c7cdfca215.json')
print('own:  ', '; GREEN; ' in gate.measured_at(p))
print('row 1:', [x for x in gate.measured_at(p, milestone='M01').split('; ') if 'runtime' in x or x == 'UNMEASURED'])"

# F2: every version 1 envelope in history is at or before ADR-0007.
for f in evals/history/*.json; do case $f in *raw*|*card*) continue;; esac
  grep -q schema_version "$f" || git merge-base --is-ancestor "$(basename "$f" .json)" 7f8d0ae \
    || echo "AFTER ADR-0007: $f"; done

# The repairs, and the seeds they must not break.
uv run pytest tests/test_adr0007.py tests/test_m01_seeds.py tests/test_construct.py tests/test_bootstrap.py -q

# F5: the account read-back, from the tree (admin credentials, the agent account).
uv run python scripts/read_back_grants.py | tail -1     # mismatches: 0
```
