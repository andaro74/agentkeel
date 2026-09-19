# CLAUDE.md — agentkeel

AgentCore proves the agent obeyed the policy tonight; agentkeel proves the
policy could only have been changed by the seat that owns it, and that a
model swap cannot relax it unnoticed.

SPEC/00-overview.md is the authority. If this file and SPEC/00 disagree,
SPEC/00 wins and this file gets a PR.

## How a session starts

1. Read `milestones/README.md` (the ledger) and the open milestone's
   `milestones/MNN/README.md` (its row plus open/close detail).
2. State back, in two sentences: the claim, and the commit or input that
   makes it false. If you cannot, stop and say so. Do not touch code.
3. Say which PR of the milestone this session is (1–4) and what that PR
   is allowed to contain (below).
4. One milestone per session. A session that drifts to the next milestone
   ends.

## The PR shape (cap four, no spare)

- **PR 1 — plant.** SPEC/NN, `milestones/MNN/feasibility.md` (with the
  `product-spec-reviewer` report pasted in), ledger row on open in
  `milestones/README.md` and `milestones/MNN/README.md`, explainer draft
  (`docs/milestones/MNN.md`, "What happened" empty), the seeded false
  state committed. Nothing that makes it pass.
- **PR 2 — measure.** The gate that reads the plant. The plant must go
  RED here. This PR is the measurement; later PRs do not decide the row.
- **PR 3 — repair.** Whatever the cold review of PR 2 found. If it found
  nothing, PR 3 is skipped and the milestone closes at PR 3 as the close
  PR.
- **PR 4 — close.** Ledger "measured" cell, explainer "What happened",
  video README entry, attestations, `git tag mNN`. M00 only: the three
  skills, written from by-hand PRs 1–3.
- A milestone may close in three PRs; never in five. A fifth PR is a RED
  close with the finding as the result. Do not propose a cap raise; write
  the finding.

A PR lands on `main` as a merge commit, never a rebase or a squash
(ADR-0004 amendment 1): envelopes are keyed to the commit they measured,
and `github-actions[bot]` authorship under `evals/history/` is part of
what makes them evidence.

Every PR ends with a ruling file at `milestones/MNN/rulings/<slug>.md`
(front matter: `ruling`, `seat`, `authorises`, `evidence`, `pr`), not
with a merge. `cold-review-ruling` enforces this from M00 PR 2 and blocks
the merge until the ruling is on `main`. A PR touching a milestone's
build paths cites `SPEC/00-overview.md#8-MNN` as its ruling. You write
the diff; you do not merge.

## Never (these are what turned beaconpave's milestones RED)

- Never write a claim whose false state is not already in the repo.
- Never build the machinery that reads a claim in the last PR.
- Never let the corpus that judges an answer also supply the answer.
  (`validate` checks golden/retrieval overlap; do not route around it.)
- Never edit `src/baseline/` after tag `m00`. It is the control.
- Never write an envelope by hand or from a runner. Only
  `src/verdict/build.py` writes envelopes; only `src/verdict/gate.py`
  reads them; a test proves they can disagree.
- Never touch `evals/goldens/`, `thresholds.yaml`, `rules/`,
  `data/corpus/` or the guardrail/judge/model ids in `manifest.yaml`
  without naming the seat that owns the path and the ruling that
  authorises it. Propose the diff; the seat's PR carries it.
- Never rename a golden id. Retire it.
- Never treat a local run (`evals/local/`) as evidence.
- Never hand-edit `docs/milestones/README.md`; `make ledger-plain`
  writes it from the ledger.
- Never write "governed", "secure" or "proven" in prose about a control
  that has not fired on its seeded case.
- Never summarise the project's state from its own prose. Read the
  ledger and the envelopes; the prose has been wrong before.
- Never add a subagent before the milestone that first needs it (R8).
- Never put real film titles, real contracts or real studio workflow
  detail anywhere. The slate is fictional.

## Seats and paths (SPEC/00 §5)

| Path | Seat | Gate |
|---|---|---|
| `SPEC/**`, `milestones/**`, `CLAUDE.md`, `.claude/skills/**`, `docs/**`, `README.md`, `LICENSE` | Product | `ruling-cited` |
| `rules/**`, guardrail id/version | Rule Owner | `ruling-cited`, `two-key` on relaxation |
| `evals/goldens/**`, `data/**` | Data Owner | `ruling-cited`, `two-key` on retire |
| `tools/**`, `may_call`, `may_be_called_by` | Tool Owner | `ruling-cited`, computed semver |
| `thresholds.yaml`, judge rubric, judge model id, agent model id + version + region | Threshold Owner | `two-key` on any downward move |
| `.github/workflows/**`, `infra/**`, key policy, cosign identity | Security | `ruling-cited`, `security-reviewer` |
| `src/**`, `scripts/**`, `tests/**`, `Makefile`, `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `evals/history/**` (CI-written only), `evals/local/**` (gitignored, no gate) | Engineering | `cold-review-ruling`; `two-key` on a human commit to `evals/history/**` |
| `.claude/agents/<name>.md` | the seat in its `seat:` front matter | `ruling-cited` |

Every seat is one human (R1). No gate waits for a human approval; all
gates are mechanical and the list in SPEC/00 §5 is exhaustive. If a task
seems to need a new gate, that is a SPEC/00 amendment, not a workflow
edit. Each ADR's `authorises:` names the seat whose rule it changes.
Every file on `main` has a seat; a file no seat owns is deleted.

## Subagents (`.claude/agents/`)

Call the seat subagent for the path you are changing before you open the
PR; paste its report into the PR body. The `product-spec-reviewer` report
goes into `milestones/MNN/feasibility.md` instead. Reports are drafts,
never rulings. Specialists (`platform-architect`, `red-teamer`,
`docs-writer`, `legal-compliance`, `incident-responder`) exist only from
the milestone that added them; do not invoke one that is not in the tree.

M00 only: PR 1 creates the seven seat subagents, so the "call before
opening" rule is waived for the six it cannot yet call.
`product-spec-reviewer` is written first and run against SPEC/00 before
the rest of PR 1 is written.

Skills: `/open-milestone`, `/close-milestone`, `/cold-review`. From M01
on, a milestone opens and closes only through them.

## Where things are

```
SPEC/                 specs, SPEC/00 first
docs/adr/             one ADR per rule change, max two amendments (Product)
docs/milestones/      explainers MNN.md; README.md is generated, never hand-edited
docs/video/           README.md carries each recording's commit and tag
.claude/skills/       open-milestone, close-milestone, cold-review (Product)
milestones/README.md  the ledger (one file; make ledger and docs-current read it)
milestones/MNN/       README.md (row + open/close detail), feasibility.md,
                      rulings/<slug>.md, attestations.md, open.md (carried
                      into MNN at the last close), runs/
src/baseline/         frozen control
src/verdict/          schema.json, build.py, gate.py, replay_history
agents/refagent/      the reference agent (title availability)
agents/ratings-helper/
evals/goldens/v1/     g-NNN.yaml, immutable ids
evals/history/        CI-written envelopes (evidence)
evals/local/          your runs (not evidence)
data/                 slate.json, rights_table.json, clause_index.json (M00);
                      corpus/ (M01)
infra/                CDK: bootstrap stack, GovernedAgent construct
scripts/seed_slate.py writes data/slate.json and data/rights_table.json
tests/
Makefile              Engineering; all five targets exist from M00 PR 1
```

## Commands

```
make evals            baseline, plus refagent from M01, against goldens, CI-equivalent
make evals-local      same, your credentials, writes evals/local/ only
make validate         grows by milestone; the ledger header says what it
                      checked at each tag. M00: golden and ruling front
                      matter. M01+: schema, seats, edges, semver, cdk-nag
make plants           list plants and whether each fired on last run
make ledger           print the ledger with measured values; exits 1 if a
                      Measured cell differs from its envelope
make ledger-plain     the same, and writes docs/milestones/README.md
```

Until M00 PR 2, `evals`, `plants` and `ledger` exit 1 with
"not until M00 PR 2".

## Writing

Plain. Short sentences. Name the shortcoming. Numbers over adjectives.
The explainer pages and the README are read by directors; if a sentence
needs the envelope schema to be understood, it belongs in `docs/platform/`
not in an explainer.

## When unsure

Say so in the PR body under **Unsure**, name the seat whose ruling would
settle it, and stop. An unstated assumption that later proves wrong costs
a milestone; a stated one costs a sentence.
