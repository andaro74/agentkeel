# The platform, in one page

Written at M02 PR 2 by hand (Product; `docs-writer` is M03). For an
engineer who has the repository open. What each thing is, who owns it,
and which of it has fired on a planted case. SPEC/00 is the authority.

## What runs

- **An agent** is a folder under `agents/<name>/`: a manifest, a prompt,
  tool schemas, rules. `refagent` answers one question, whether a title
  can be published somewhere on a date, from a rights table it reads
  through a tool. `ratings-helper` is a manifest with no code (M07).
- **The control** is `src/baseline/`, frozen at tag `m00`. Every number
  the platform reports is a delta against it.
- **The goldens** are `evals/goldens/v1/g-NNN.yaml`: a question, the
  expected answer, and the row and clause a right answer reads. A trap's
  or an ordinary golden's answer passes only if it also cites a row and a
  clause that exist; the citation is not yet compared to the golden's own
  (M03). An id is never renamed or reused; a golden is retired by setting
  `retired:`, and its file stays.
- **A run** is `make evals` in CI: the control and the agent answer every
  live golden, `src/verdict/build.py` scores them into an envelope under
  `evals/history/<commit>.json`, and `src/verdict/gate.py` rules on the
  envelope and nothing else. The gate's exit code is the required check
  `evals`.

## Who owns what

SPEC/00 §5 gives every path a seat. From M02 the table is machine-readable
as `.github/CODEOWNERS`, one login per seat, and every seat is one person
(R1). A change to a seat-owned path merges only with a ruling file under
`milestones/*/rulings/` whose `seat:` is that seat, whose `authorises:`
names the path and whose `pr:` is the PR. A relaxation (a bar loosened, a
golden retired or edited to pass, a rule deleted, retention shortened, a
hand-written envelope) needs two such files from two distinct seats.

Nobody approves anything by hand. The gates read files.

## The gates, and what each has refused

| Gate | Where | Reads | Refused its planted case |
|---|---|---|---|
| `validate` | `src/validate/`, run by `evals.yml`'s `checks` job | the tree; `origin/main` for golden ids and semver; the API for the live ruleset and the logins | S3 (one-sided edge) and S5 (renamed golden id), in a copy of the tree, M02 PR 2; on real PRs 17 and 18, read by M02 PR 3's run |
| `ruling-cited` | `src/gates/ruling_cited.py`, run by `gates.yml` | the diff against the base; CODEOWNERS from the base | S2 (golden edited with no ruling) and S5, in a copy of the tree, M02 PR 2; on real PRs 16 and 18, and on M02 PR 3 itself before its rulings were written (job 107181506184), read by M02 PR 3's run |
| `two-key` | `src/gates/two_key.py`, run by `gates.yml` | the diff, the history, `thresholds.yaml`'s `relaxes:` | S1 (one key; two files from one seat) and S2, in a copy of the tree, M02 PR 2; on real PRs 14, 15 and 16, read by M02 PR 3's run; green on PR 12's keyed retirement (Door 2) |
| `evals` | `evals.yml`, the gate's exit code | the envelope | F0.2 (an envelope with no baseline ref), M00; F1.4 (an uncited answer), M01 |
| `signature` | `src/bundle/verify.py`, `deploy.yml` | the bundle and its cosign bundle | S1 and S2 of M01 (unsigned; altered after signing) |
| the construct | `infra/construct/` | the manifest | S3, S5, S8 of M01 at synth (egress not in the manifest; a role without the boundary; an agent outside the construct) |
| the `main` ruleset | GitHub, exported to `infra/ruleset/main.json` | the required checks; `bypass_actors: []` | the owner's `gh pr merge 14 --admin`, refused by GitHub (rule suite 4192991324); the owner listed in `bypass_actors`, refused by `validate` (job 107206831180); both read by M02 PR 3's run, envelope `8033c2a` |

"Refused its planted case in a copy of the tree" means a test applied the
seed and the gate refused it. It does not mean a real pull request was
refused on GitHub; for M02 that reading comes after PR 2 merges and the
two checks are made required (SPEC/02 §5.1).

## What is not enforced at M02

- A person holding every seat can write both keys. The gate records that
  the change was named and under which seat; it does not record that a
  second person looked. A ruling file is read for its seat, its globs
  and its number, never for what it says.
- The bot's exemption under `evals/history/` reads a commit's author
  name, which anyone can set with `git config`. Until M05 reads something
  a committer cannot set (the push actor from the API, or a signature), a
  hand-written envelope committed under the bot's name passes both gates.
- The gates run the pull request's own copy of `src/gates/`; a PR can
  edit the gate it is gated by (M05).
- A PR that edits a workflow can edit `src/`, `scripts/` and the
  `Makefile` it runs; only the workflow's text is hashed (M05).
- The envelope is written by the PR's own code; nothing signs it (M05).
- `ratings-helper` has no code, no edge and no ceiling in force (M07).
- The ledger is read by `make ledger`, which holds each Measured cell to
  its envelope; the prose around it is held by nobody but the reader.

## Where to look

- `milestones/README.md`: the ledger. What `validate` checked at each tag
  is in its header; the rows say what each milestone claimed, planted,
  expected and measured.
- `milestones/MNN/`: the feasibility note, the rulings, the run files.
- `docs/milestones/MNN.md`: the explainer for a director.
- `docs/adr/`: one file per rule change.
