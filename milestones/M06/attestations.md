# M06 — attestations

Four lines, signed before `git tag m06`. Every seat is one human (R1), so
one person signs all four. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong. The Rule Owner's, the Data Owner's and the Tool Owner's files did
not change in M06 (`git diff --stat m05 HEAD` over `rules/`,
`agents/refagent/rules/`, `evals/goldens/`, `data/`, `tools/` and
`agents/refagent/tools/` is empty), so none of those seats signs a line.
The seats in both manifests changed (`agents/refagent/manifest.yaml`,
`agents/ratings-helper/manifest.yaml`, PR 2), and line 2 covers them.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch, pushed before the merge. An unsigned line is not
a failed attestation; it is a milestone that is not tagged. Nothing reads
this file, so the close checks it on the pushed head before any merge
command (`milestones/M05/open.md` row 44).

The ledger row is not waiting on these. Row 6's State is RED because the
ledger's reading of the envelope its Measured cell names says so, and
`make ledger` holds the cell to that line. What these four gate is
`git tag m06`.

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json`
and its control card were written by `src/verdict/build.py` and
`src/baseline/run.py` inside CI run 36886530498, with `template` read
from GitHub, Grafana, the registry and the audit bucket by
`scripts/observe_template.py` in the same run, and committed by
`github-actions[bot]` in `3ca05dd`. No human edited any of them after CI
wrote them. Every commit under `evals/history/` from `m05` to this close's
reading is `github-actions[bot]`'s (four: `67d94ac`, `f73e152`, `a39d4d6`,
`3ca05dd`); a later run on this branch adds its own, by the same bot. That
authorship can still be claimed by anyone with write. `src/baseline/` is
unchanged since tag `m00`. No reader changed in PR 4: S2's marker came off
when its run file was filled (`245eb9b`), and the observer, `template.py`
and the platform check are as PR 3 merged them. The stated reading of S2
was wrong ("unstable"; the run read "blocked"), and no reader was changed
to make it right. At the close the seed tests read 7 passed and 1 xfailed
(S3, not attempted).

Signed: andaro74  Date: 2026-10-02

---

**2. Security — what was granted and listed at the close, and what was
not compared.**

Each read below was made once, on 2026-10-01, by the owner's `gh` or the
agent account's AWS CLI, as the command beside it; the output is not
committed, so each is the owner's read, not a record. The platform's
GitHub App (`agentkeel-platform`, 5144253) had Administration: read when
read (`gh api orgs/agentkeel-studio/installations`: administration,
contents, metadata and pull requests read, checks write), and that is why
it cannot see `bypass_actors` (finding 1). One read shows the grant on
that day, not that it was unchanged through PR 3 and PR 4. owner-check's
one ruleset is 24310403, `bypass_actors: []` as the owner reads it, its
required check `platform-check` bound to `integration_id` 5144253
(`gh api repos/agentkeel-studio/owner-check/rulesets/24310403`). `floresinnovations` (id 336113686) is a write-only outside
collaborator on `agentkeel-studio/owner-check` alone
(`gh api orgs/agentkeel-studio/outside_collaborators`; the organisation's
two repositories, and `agent-template`'s one collaborator, `andaro74`, from
`gh api .../collaborators`); it made S2 in the browser, with no personal
access token on the human's word. The temporary Grafana admin account `setup-temp` was deleted during
PR 2: read at 2026-10-01T15:45Z, the workspace `g-745446386a` has one
service account, `agentkeel-observer` (Viewer), with one token, which
expires 2026-10-31T07:00:01Z (`aws grafana list-workspace-service-accounts`
and `list-workspace-service-account-tokens`; `milestones/M07/open.md` row
9). The agent
account's stacks, as `aws cloudformation describe-stacks` lists them at
the close, **listed, not compared** with the commit each came from or the
tree:
`AgentkeelBootstrap` (updated 2026-10-01T03:44:35Z), `AgentkeelGrafana`
(11:20:46Z), `agentkeel-refagent` (12:15:28Z, the deploy role from
`main`), `AgentkeelAudit` and `AgentkeelIngest` unchanged since M05; the
registry holds refagent alone (`aws dynamodb scan`). The bootstrap's
update at 03:44:35Z (the deploy roles) is not traced to a commit here. Not
attested: that the security account's
deploy removed the stand-in's Allow (the human's word, read by nothing:
`milestones/M07/open.md` row 16); that the tag-keyed audit prefix works
for a template agent (none was deployed); and any control in SPEC/06 §8
that no seed attempted.

Signed: andaro74  Date: 2026-10-02

---

**3. Threshold Owner — the bar was set before its reader and not moved.**

`quickstart.max_seconds: 28800`, `relaxes: up`, was added to
`thresholds.yaml` in PR 2, before S3 was timed and before any reading of
it. It was not moved. No elapsed time was measured against it: S3 was not
attempted, so `F6_3` reads unread and the bar has never been compared with
a quickstart. Whether eight hours is the right bar is unread.

Signed: andaro74  Date: 2026-10-02

---

**4. Product — the close says what was read and nothing more.**

Row 6's Measured cell is `make ledger`'s line for the envelope it names,
copied, and the State is the verdict in it. The explainer's "What
happened" uses that envelope's readings and the run files' records, and
does not call the template, the platform check or the panel "governed",
"secure" or "proven". F6.1's live half and F6.3 were unread; F6.2 held,
while the App refused every head (`milestones/M07/open.md` row 5).
S3 was not attempted, by Product's ruling of 2026-10-01 (option 1), so the
second developer's one clean attempt is kept for M07. Every finding and
every Unsure item of #34 to #37 is ruled in M06 or carried to
`milestones/M07/open.md` with a seat and a milestone (`rulings/pr4.md`).

Signed: andaro74  Date: 2026-10-02
