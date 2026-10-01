# Quickstart: ship an agent from the template

For a developer with **write** access to one agent repository and nothing
else: no admin on the repository, no cloud credentials. This page is what
M06's timed run follows (SPEC/06 section 1). The clock starts when the
repository is created and stops at the last of four records: your first
pull request merged, the platform's deploy, your agent answering one of its
own tests, and your agent listed in the registry. The bar is one working
day, 28,800 seconds, breaks included.

What is not built, so do not look for it: no judge (answers are checked by
code, field by field), no human-in-the-loop step, no knowledge base, no
calls between agents, no FRAGILE marking. Each is M07's.

## 0. Before you start (the owner, not you)

The organisation's owner creates your repository from the template, applies
the platform's ruleset to it, and gives you write. That moment is the
repository's `created_at`, and the clock starts there. You cannot create
the repository yourself: member repository creation is off.

## 1. Clone it

```sh
git clone https://github.com/<org>/<your-repo>.git
cd <your-repo>
git switch -c first-agent
```

## 2. Name your agent

In `manifest.yaml`, set `name`: lower-case letters, digits and hyphens, 3
to 31 long, fictional, and not `refagent` or `ratings-helper`. A name
another repository already deployed under is refused at deploy.

Leave `guardrail` as it is. Leave `model` as it is unless the model's owner
has said otherwise.

## 3. Open your pull request now

Commit, push and open a pull request to the default branch. Within about
five minutes (sometimes longer at the top of the hour) agentkeel posts a
check named `platform-check` on it. On the template as shipped it **fails**,
and says why:

- `seats assigned, each a login with access`: all seven seats are empty;
- `an agent's goldens`: you have no tests.

That is the platform doing its job. The pull request cannot merge until
the check passes.

## 4. Fill the seats

Each of the seven seats in `manifest.yaml` (`product`, `rule-owner`,
`data-owner`, `tool-owner`, `threshold-owner`, `security`, `engineering`)
names the GitHub login of the person who owns that kind of decision for
this agent. Each must have access to this repository. On this project one
person holds every seat, so ask the owner which login to use. Your own
login is not one of them.

## 5. Write your tests (goldens)

At least **one ordinary** question and **one trap**, each a file
`goldens/g-NNN.yaml`:

```yaml
id: g-001
kind: ordinary          # or: trap
question: Can we publish ... on SVOD in the United States on 2026-12-25?
expected:
  table_row: r-019      # a row in data/table.json
  clause_id: ML-2.1     # a key in data/clauses.json
  answer_fields:
    available: true     # what the answer must say, field by field
seat: Data Owner
added: M06
retired: null
```

An ordinary golden asks something the table answers plainly. A trap asks
something that looks like yes and is no, because of a row's detail (a
holdback, an embargo, a window that ends the day before). The file name
is the id. A test that has never passed does not block anything; it is
reported.

You may change `data/table.json` and `data/clauses.json` to your agent's
own rows and clauses. Every golden must cite a row and a clause that are
there.
If you change the titles, change the slate in `prompt.txt` too: the
agent finds a title's id there, and the tool finds the row by that id.

## 6. Push, wait for the check, merge

Push. When `platform-check` passes, merge with a **merge commit** (the
only kind the ruleset allows). A job in your own workflow called
`platform-check` does not count: GitHub accepts the check only from
agentkeel's App.

## 7. The platform deploys it

Within about ten minutes of the merge, agentkeel's `deploy` workflow finds
your merged commit, builds the image from its own Dockerfile, signs it,
deploys your agent into the platform's network, and asks it each of your
goldens. You do nothing here, and you can watch it in agentkeel's Actions
tab:
<https://github.com/andaro74/agentkeel/actions/workflows/deploy.yml>

The run's summary says whether your agent answered. The answers are
written once to the platform's audit account, which this project's
workflows can add to and cannot overwrite.

## 8. Find it in the registry

Grafana panel 1 lists every deployed agent, one row each, from the
registry. Ask the owner for the link. When your agent's row is there, you
have shipped.

## If something fails

| What you see | What it means |
|---|---|
| No `platform-check` after 30 minutes | agentkeel's schedule has not reached it. Push an empty commit, or tell the owner. |
| `the agent's name` | The name is malformed, agentkeel's own, or taken. |
| `the platform's guardrail` | `guardrail` was changed. Put it back. |
| `the repository's ruleset is the export` | The repository's settings were changed. Only the owner can fix this. |
| The deploy run fails at the registry | Another repository already deployed under your agent's name. Rename it. |
