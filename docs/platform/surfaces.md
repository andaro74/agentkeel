# The surfaces: what each panel shows, and what it does not

Written at M07 PR 2 (Product). For an engineer or a seat holder. A
surface is a place a person looks: a Grafana panel. This page says what
each one reads, how the platform checks that it shows what is recorded,
and what has not been built.

Two panels exist. Two more are described here and not built.

## Panel 1: the registry

One row per agent the platform has deployed: its name, its repository,
the commit deployed and when. It reads the registry table and nothing
else.

- **What checks the query:** `make validate` refuses a panel 1 query that
  reads any other table or a second source.
- **What checks the rows:** each `evals` run asks Grafana for panel 1's
  rows and compares them with a scan of the registry. A row for an agent
  the registry does not hold is a miss (F6.4).
- **Fired on its planted case:** yes, in a copy of the tree (M06 PR 2).
  The live comparison read as held at M06's close (row 6's cell).

## Panel 2: the verdict history

One row per run recorded on `main`: the commit, the verdict the run
stored, and where the agent ran.

- **What checks the query:** `make validate` refuses a panel 2 query that
  computes a column, filters on the verdict, or reads any table but the
  one the rows are written to.
- **What checks the rows:** each `evals` run asks Grafana for panel 2's
  rows and compares them, commit by commit, with the envelopes in
  `evals/history/`. A row that says GREEN for a run whose envelope says
  anything else is a miss (F7.4).
- **Fired on its planted case:** in a copy of the tree only (M07 PR 2).
  The live panel was deployed on 2026-10-03 and read at M07's close: 55
  rows, each equal to its envelope's verdict. That is a reading of
  agreement; the live panel has not been made to show a wrong GREEN.

### A GREEN on panel 2 is not a GREEN milestone

This is the one thing to know before reading panel 2.

Panel 2 shows **the run's own verdict**: did the agent's answers get
worse, did a planted attack get through, did a check fail. It does not
show whether a milestone's claim held.

A milestone's row in the ledger can be RED over a GREEN run. The run for
commit `245eb9b` stored GREEN: the agent answered as well as before and
every planted case fired. Row 6 of the ledger, which cites that same run,
is RED: the claim was that a developer ships an agent in a day, and that
day's records could not be read. Both are right. They answer different
questions.

So: for "is this change safe to merge", read the run's verdict. For "did
the platform do what it said", read the ledger (`milestones/README.md`,
or `make ledger`).

### Where panel 2's rows come from

When a change lands on `main`, a job copies three fields from each
recorded run (the commit, the verdict, the mode) into a table that panel
2 reads. A row is written once and not changed by the workflow that writes it: each
put carries the condition that the commit is not there. The role itself
could replace a row; nothing in IAM stops that. The table is a copy for
a person to look at. It is not the evidence: the envelope in the
repository and its copy in the security account are. The comparison
above is what holds the copy to them.

A run made on a pull request that never reached `main` has no row.

## Panels 3 and 4: described, not built

Cut from M07 at its open (SPEC/07 section 9, cut d). No falsifier reads
them. What each would show, and where that information is today:

| Panel | Would show | Where to read it today |
|---|---|---|
| 3, the call graph | Which agent called which, and how deep | Nowhere as a picture. One agent has code; the depth limit is enforced in the agent's own server and was tested at M05 |
| 4, containment | Each hostile attempt, whether it was refused, and how long until its record reached the security account | Row 5 of the ledger and the `containment` section of each run's envelope |

## The surfaces' own plants

A check that stops running looks the same as a check that passes. So each
panel has a planted fault its checks must refuse on every run:

| Panel | Planted fault |
|---|---|
| 1 | A query with a second source, and a row for an agent that is not in the registry |
| 2 | A query that shows GREEN for everything, and a GREEN row for a run recorded RED |

Every run counts them: two expected, and two refused. If a check did not
run, or passed what it should refuse, the run is RED (F7.5). The count is
in the envelope beside the other numbers (`upgrade.surfaces`).

## What no surface checks

- **What a person sees on the page.** The platform reads the same data
  the panel is drawn from, through Grafana's query interface. It does not
  look at the rendered page.
- **The workspace's settings.** A data source pointed somewhere else
  under the same name would pass `validate`; the row comparison is what
  would notice.
- **Who can edit the table panel 2 reads.** An admin of the account can.
  The comparison with the envelopes would notice a changed verdict.
