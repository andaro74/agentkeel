# M07 — attestations

Four lines, signed before the close merges. Every seat is one human (R1),
so one person signs all four. They are separate because they attest to
different things, and a later reader should be able to see which one was
wrong. The Rule Owner's, the Data Owner's and the Tool Owner's files did
not change in M07 (`git diff --stat m06 HEAD` over `rules/`,
`agents/refagent/rules/`, `evals/goldens/`, `data/`, `tools/` and
`agents/refagent/tools/` is empty), so none of those seats signs a line.

Sign by writing your name and the date at the end of the line, in a commit
on the close PR's branch, pushed before the merge. An unsigned line is not
a failed attestation; it is a milestone that is not closed. Nothing reads
this file, so the close checks it on the pushed head before any merge
command (`milestones/M05/open.md` row 44).

The ledger row is not waiting on these. Row 7's State is RED because the
ledger's reading of the envelope its Measured cell names says so, and
`make ledger` holds the cell to that line. What these four gate is the
merge, and `git tag m07` if Product places it (`rulings/pr4.md`).

---

**1. Engineering — the evidence is CI-written and unedited.**

The envelope `evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json`
and its control card were written by `src/verdict/build.py` and
`src/baseline/run.py` inside CI run 37149475766, with `upgrade` and
`template` read from GitHub, AWS and Grafana by
`scripts/observe_upgrade.py` and `scripts/observe_template.py` in the
same run, and committed by `github-actions[bot]` in `45bac6a`. No human
edited any of them after CI wrote them. Every commit under
`evals/history/` from `m06` to this close's reading is
`github-actions[bot]`'s (seven: `1302b67`, `6f84d1c`, `a00b80e`,
`10f4eb4`, `3326dd1`, `7b29d10`, `45bac6a`). That authorship can still be
claimed by anyone with write. `src/baseline/` is unchanged since tag
`m00`. No reader changed in PR 4: nothing under `src/`, and of
`scripts/` only a docstring in `platform_check.py`. The close's first
run (37147871497) failed two jobs on a test the session had not updated
and pushed without reading the suite's result; the envelope the cell
cites is the second run's, with every job green. Two commits were
authored as `floresinnovations` by the session's checkout; one was
amended (`78aac19`) and the other never merged (#41). At the close the
seed tests read 13 passed (`tests/test_m07_seeds.py`) and 8 passed
(`tests/test_m06_seeds.py`).

Signed:

---

**2. Security — what was granted, deployed and read at the close, and
what was not compared.**

Three Apps are installed on `agentkeel-studio`, each on all repositories,
as `gh api orgs/agentkeel-studio/installations` gave them on
2026-10-03: `agentkeel-platform` (5144253) with Administration: write,
checks write, contents, metadata and pull requests read;
`agentkeel-upgrades` (5169860) with contents and pull requests write;
`agentkeel-observer` (5169892) with administration, checks, contents and
pull requests read. The grant's reader compared each with
`infra/platform_grant.yaml` live on keyed runs of `platform-upgrade.yml`,
`model-watch.yml`, `deploy.yml` and `observe.yml` after #42 merged, and
stopped none. **Three deploys were made by hand before any ruling**, from
`m07-pr4`: the bootstrap stack twice (two actions on `runtime/*` for the
execution role) and the security account's stack once (the observer's
put role's trust), the last by `hector.flores` in the console
(`rulings/pr4-security.md` item 1). The bootstrap's stored template was
compared with the tree's synth by a script whose two hashes are recorded
(`runs/b2_cdk_diff.md`); the security account's was hashed by nobody.
The App's token relaxed `owner-check`'s ruleset when asked, once, and
the owner restored it 7 min 21 s later; it reads back equal to the
export as the owner read it. **Not attested:** that the execution role
is refused on a runtime outside the two prefixes (no attempt); that the
observer's put role refuses a branch (no attempt); that the two orphan
keys are gone (pending deletion until 2026-10-09); that nothing else
changed in the security account (one person's word); and any control in
SPEC/07 §8 or §12 that no seed attempted.

Signed:

---

**3. Threshold Owner — the bars were set before their readers and not
moved, and the candidate was measured once.**

`upgrade.arrive_max_seconds: 4500`, `upgrade.deploy_max_seconds: 3600`
and `upgrade.retire_max_seconds: 3600`, each `relaxes: up`, were added
to `thresholds.yaml` in PR 2, before any attempt, and not moved.
`quickstart.max_seconds: 28800` is as M06 set it. The owner's test
missed `deploy_max_seconds` and the bar was not moved to meet it. The
candidate named on 2026-10-01, Haiku 4.5, was run against the goldens
once, on #43: RED, `g-004` regressed, p95 3,258 ms, not merged; no second
run was made and none was owed (the rule allows one after a p95 miss
only). refagent's pin on `main` is unchanged. No candidate is named now.

Signed:

---

**4. Product — the close says what was read and nothing more.**

Row 7's Measured cell is `make ledger`'s line for the envelope it names,
copied, and the State is the verdict in it. The explainer's "What
happened" uses that envelope's readings and the run files' records, and
does not call the upgrade path, the grant or the check "governed",
"secure" or "proven". M07 took five pull requests against a cap of four;
the row is RED for that, for F7.0 and for `taken` 2 of 3, and no cap
raise was proposed. Each attempt was stated and pushed before it was
made; one statement was edited after its attempt began, and the owner's
dispatches went beyond what the statements allowed, and both are said in
`runs/pr4_expected.md`. Act 1 was not captured, and nothing filmed
afterwards is filed as it. Every finding and every Unsure item of #38,
#39, #40, #42 and #44 is ruled in M07 or carried to
`milestones/M08/open.md` with a seat and a milestone (`rulings/pr4.md`).

Signed:
