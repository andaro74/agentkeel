# M02 — Seats and change gates

## Ledger row

Written at M02 PR 1 open. The row in `milestones/README.md` is the one
`make ledger` reads; this is the same row with the open detail.

| Field | Row 2 |
|---|---|
| Claim | Seat-owned files change only with a ruling; relaxations need two keys |
| Falsifiers | F2.1 any of the five seeded changes merges: a threshold relaxed with one key or with two files from one seat, a golden edited to green a build, an edge declared on one side, the owner merging past a red required check, a golden id renamed. F2.2 the three doors (Door 1 blocked by the gate, Door 2 merged with two keys, Door 3 blocked by two gates) are not reproducible from the PR record. |
| Seeded commit | `6ff333a` (S1, both forms); `74a38be` (S2); `d8fbdb1` (S3); `9eb539c` (S4, the attempt to make, `observed: null`); `479abb9` (S5), each its own commit (SPEC/02 §5) |
| Expected gate output | PR 1: refagent's envelope in runner mode, gated and recorded as at M01; it says nothing about claim 2. `make plants` lists S1–S5 with no reader in the tree; `tests/test_m02_seeds.py` shows 6 expected failures. PR 2, on the PR: S1 (both forms), S2, S3 and S5 refused by `src/gates/` and `validate` in a copy of the tree, each with its planted reason; `checks.F2_1` fails on PR 2's own run, because S4's `observed` is null; `two-key` green on PR 2's own two files for `g-012`, which is Door 2. After PR 2 merges and before PR 3's first CI run: the human makes `ruling-cited` and `two-key` required, opens the seed PRs from `main`, and makes S4's two attempts; PR 3's run looks each up (`scripts/observe_pr.py`) and writes `checks.F2_1` (both halves) and `checks.F2_2` pass. **A named P3 exception (SPEC/02 §5.1): a PR refused by a gate on `main` cannot exist before the gate is on `main`; the machinery is PR 2's, the reading is PR 3's, whether PR 3 is the repair or the close.** RED if any seed PR's check is green, if `--admin` merges, if `validate` stays green with `bypass_actors` non-empty, or if PR 3's run reads anything else. No count of refagent's passes is expected to change; the checks decide the row. |
| Measured | — |
| PRs used / cap | 1 / 4 |
| State | OPEN |

### Open detail (PR 1, #11, 2026-09-22)

- Opened through `/open-milestone`. SPEC/02 was written first and
  `product-spec-reviewer` run on it (1 BLOCK, 8 FINDING, 6 NOTE), pasted
  verbatim in `feasibility.md` §1; every item is ruled in §2 and SPEC/02
  was revised once on them, before any seed was committed. This time the
  order of commits is the order of writing: SPEC/02 lands in `bc35c39`,
  before the first seed (`6ff333a`). The M01 cold review's F5 does not
  recur.
- **Planted** in five commits, one per seed, `6ff333a` to `479abb9`,
  each with its test in `tests/test_m02_seeds.py`, before any code that
  reads them. At `479abb9` all six tests (S1 has two forms) are expected
  failures. A seed is a diff to a seat-owned path under
  `tests/fixtures/m02/`, applied to a throwaway worktree by its test;
  S4 is an attempt against the `main` ruleset, `observed: null`.
- **Read in this PR:** nothing. No `src/gates/`, no CODEOWNERS, no
  `validate` growth. `make plants` lists S1–S5 with "not in the tree
  yet" beside each reader.
- **The BLOCK, and what it changed.** The reviewer found that a seed
  with no ruling is refused by `ruling-cited` and by any `two-key`, so
  nothing planted told the two apart and "one key" had no false state.
  S1 now carries exactly one Threshold Owner ruling, so only `two-key`
  can refuse it, and a second form carries two files from that one seat.
  The one-key case is what M01's second half lacked: a seeded case for
  the half of the claim that costs the most to get wrong.
- **Door 2 is PR 2's own merge** (`g-012` retired with two keys, `g-021`
  added), not a PR of its own: a PR merged properly through a gate
  cannot exist before the gate does, and the cap has no PR to spare for
  a demonstration. The seed PRs are opened from `main` after PR 2 merges
  and read by PR 3's run; SPEC/02 §5.1 names that as a P3 exception, as
  ADR-0007 named M01's. If PR 3 is the close, the reading rides in it.
- **Carried work, with its seats' rulings** (`feasibility.md` §6): row 9,
  the construct's rights table on `TableEncryption.DEFAULT` after a test
  that fails on the collision (`25b2743` fails, `9ea6405` passes; the
  rendered template differs from `main` by one line, `SSEEnabled` true
  to false); row 8, the cold-review skill's diff-or-tree line; row 22,
  ADR-0006 amendment 1 and the S6 note; row 1, ADR-0008; row 21, ruled
  in SPEC/02 §2. Rows 3 and 4 move to PR 2 as Door 2. Row 2, M01's
  video, lands in this PR when the recording is given.
- **This PR's run** writes refagent's envelope in runner mode, gated and
  recorded as at M01. It does not measure claim 2. Its merge triggers
  `deploy.yml` on `main`: the first agent deploy since the failed one,
  read at PR 2 (row 10).

### For the seats, at M02 PR 2 open

- **Security:** make `ruling-cited` and `two-key` required after PR 2
  merges, not before (SPEC/02 §5.1); whether `GITHUB_TOKEN` on a PR run
  can read the live ruleset for `validate`'s diff, or a token with
  `administration:read` is needed; whether `gates.yml` has what it needs
  on a fork PR (row 11); whether the rule-suites API records a refused
  `--admin` merge (finding 3), read at the attempt; destroy
  `AgentkeelM00EvalRole` so PR 2 can remove `infra/eval-role/` (row 16);
  read the first successful deploy (row 10).
- **Threshold Owner:** `relaxes:` on every bar in `thresholds.yaml`; the
  cap against 54,156 measured; `max_tokens_per_session` and `daily_usd`
  (row 18); and, before the seed PRs are opened, that five seed PRs each
  trigger an `evals` run at about 54,000 tokens.
- **Data Owner, Threshold Owner:** the two ruling files for `g-012`'s
  retirement and `g-021`, both `pr:` 12 (rows 3, 4).
- **Tool Owner:** the `ratings-helper` manifest stub and computed semver
  (row 20).
- **Engineering:** `src/gates/`, `scripts/observe_pr.py`, the `validate`
  checks, `two-key`'s human-commit case (row 6), the instruments (row
  12), the smaller items (row 13).
