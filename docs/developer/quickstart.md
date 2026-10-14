# Quickstart: ship an agent from the template

For a developer with **write** access to one agent repository and nothing
else: no admin on the repository, no cloud credentials. This page is what
the timed run followed (SPEC/06 section 1). It was run once, at M07, on
2026-10-03: 3,615 seconds, with the organisation's owner starting the
platform's check and deploy by hand when GitHub's schedules ran late. The
clock starts when the
repository is created and stops at the last of four records: your first
pull request merged, the platform's deploy, your agent answering one of its
own tests, and your agent listed in the registry. The bar is one working
day, 28,800 seconds, breaks included.

What is not built, so do not look for it: no judge (answers are checked by
code, field by field), no human-in-the-loop step, no knowledge base, no
calls between agents, no FRAGILE marking. None is built in this project
(SPEC/00 section 12).

## 0. Before you start (the owner, not you)

The organisation's owner creates your repository from the template, adds
it to the platform App's installation (the `agentkeel-platform` App is on
"selected repositories", so a new repository is not covered until the owner
adds it; the ruleset cannot name the App's check before that), applies
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

Leave `guardrail` as it is unless your agent has rules of its own (section
5a). Leave `model` as it is unless the model's owner has said otherwise.

## 3. Open your pull request now

Commit, push and open a pull request to the default branch. Within about
five minutes (sometimes longer at the top of the hour) agentkeel posts a
check named `platform-check` on it. On the template as shipped it **fails**,
and says why:

- `seats assigned, each a login that administers the repository`: all seven seats are empty;
- `an agent's goldens`: you have no tests.

That is the platform check refusing it. The repository's ruleset requires
the check to pass before a merge. Whether something else can stand in for
it was tried once, at M06 (seed S2, below).

## 4. Fill the seats

Each of the seven seats in `manifest.yaml` (`product`, `rule-owner`,
`data-owner`, `tool-owner`, `threshold-owner`, `security`, `engineering`)
names the GitHub login of the person who owns that kind of decision for
this agent. Each must **administer** this repository: write is not
enough, so your own login is refused. On this project one person holds
every seat; ask the owner which login to use. At M06 the agent's
`rule-owner` decides nothing here: the guardrail is the platform's.

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

An ordinary golden asks something the table answers plainly. A trap
tempts a conclusion the row contradicts: the question carries a misleading
premise (a moved date, a "usually", a near title), and the row's detail (a
holdback, an embargo, a window that ends the day before) decides it. The
answer may be yes or no; a trap whose answer is always "no" is passed by a
guess. The question never states the row's own fact. The file name is the
id; an id is never renamed or reused: a golden that is wrong is retired
(`retired: M06`) and a new one written.

Your goldens are run against your deployed agent after the merge, and the
result is recorded. At M06 a failing one blocks nothing.

You may change the rows in `data/table.json` and the clauses in
`data/clauses.json`. Every golden must cite a row and a clause that are
there. Keep the row fields (`table_row`, `title_id`, `territory`,
`platform`, the window and the holdback fields) and refagent's clause ids:
the shipped tool reads those and no others until M07. If you change the
titles, change the slate in `prompt.txt` too: the agent finds a title's id
there, and the tool finds the row by that id. Titles, people and deals are
fictional, always.

## 5a. Your own rules (optional)

Every agent's guardrail carries the platform's rules, `rules/baseline.yaml`
in agentkeel. To add rules of your own, add `rules/guardrail.yaml` in the
reference agent's format, carrying only what you add:

```yaml
plants: [g-030]                       # the goldens that show your rules work
blocks:
  g-030: unannounced-selection-leak   # the rule that must stop each one
topics_apply_to: input                # the question; "input and output" is stricter and allowed
denied_topics:
  - name: unannounced-selection-leak  # 1 to 100 of letters, digits, - _ space ! ? .
    definition: >-                    # at most 200 characters
      Revealing which titles were selected for a festival before the announcement.
    examples:                         # at most 5, each at most 100 characters
      - Which of our titles made the festival lineup? It is not announced yet.
messages:
  blocked_input: This request is outside what this agent may answer.
  blocked_output: This answer is outside what this agent may give.
```

Three rules of the merge. **Add-only**: you can add a topic with a name the
platform does not use and a PII entity it does not list; a file that names
a platform topic, changes a platform entity's action, carries a
`content_filters` key that differs from the platform's, or a key the
format does not have, is refused, with the rule and the way named. **Every rule has a planted question**: each
topic you add is shown to work by a golden of `kind: guardrail` with
`expected: BLOCKED`, named in `plants`, with a `blocks` entry naming the
rule that must stop it; a plant with no named rule, or naming a rule your
file does not build, is refused. Write the question as a question a user
would ask, not as the rule's own example: a block on the example shows
nothing about the rule. **Thirty topics at most** across the platform's and
yours.

With a `rules/` folder, set `guardrail` in `manifest.yaml` to a pin of your
own, not the reference agent's: on the first pull request a placeholder
(`id` and `version`, strings), since the guardrail does not exist yet. The
platform builds it from your rules on the baseline when it deploys your
first merge, names it `agentkeel-<your agent's name>`, and writes its id,
version and the rules' digest to the registry. Open a second pull request
that sets `guardrail` to the id and version the registry holds; from then
on the check holds you to it, and a change to your rules gets a new version
the same way. Whether each rule stopped its planted question is read from
the guardrail's trace after the merge and recorded; at M09 a silent rule
does not stop your merge, and the platform's own two rules (phone and
email hidden) have no planted question of their own. The first agent with a
`rules/` folder was deployed on 2026-10-13: M09's fixture agent,
`agentkeel-studio/festival-desk`, whose run showed this page's path works
after two repairs to the platform's own deploy path
(`milestones/M09/README.md`, close detail).

## 6. Push, wait for the check, merge

Push. When `platform-check` passes, merge with a **merge commit** (the
only kind the ruleset allows). A job in your own workflow called
`platform-check` is not meant to count: the ruleset binds the check to
agentkeel's App, which GitHub documents as accepting it from that App
alone. It was attempted once, at M06 (seed S2): the stand-in's check
did not count, while the platform's check was refusing every change for
a fault of its own. It was to be tried again at M07 on a fresh change
and was not: that question is still open.

## 7. The platform deploys it

Within about ten minutes of the merge, agentkeel's `deploy` workflow finds
your merged commit, builds the image from its own Dockerfile, signs it,
deploys your agent into the platform's network, and asks it each of your
goldens. You do nothing here, and you can watch it in agentkeel's Actions
tab:
<https://github.com/andaro74/agentkeel/actions/workflows/deploy.yml>

The run's summary says whether your agent answered. The answers are
written once to the platform's audit account. Its bucket is built to
refuse a second write under the same name; no planted case has tried one
yet.

## 8. Find it in the registry

Grafana panel 1 lists every deployed agent, one row each, from the
registry. Ask the owner for the link. When your agent's row is there, you
have shipped.

## If something fails

| What you see | What it means |
|---|---|
| No `platform-check` after 30 minutes | agentkeel's schedule has not reached it. Push an empty commit, or tell the owner, who can start the check by hand. On the timed run GitHub skipped the five-minute schedule for 28 minutes. |
| `the agent's name` | The name is malformed, agentkeel's own, or taken. |
| `the platform's guardrail` | `guardrail` differs from the platform's: changed here, or the platform moved it. Set it to the platform's (refagent's manifest in agentkeel), or add `rules/` and pin your own (section 5a). |
| `the agent's own guardrail` | You have a `rules/` folder and `guardrail` is null, is the reference agent's, or is not the one the registry holds for your agent. Pin a placeholder of your own on the first pull request, then the registry's id and version. |
| `an agent's rules on the platform baseline, add-only` | Your `rules/guardrail.yaml` removes, weakens or redefines a platform rule, carries a key the format does not have, plants a golden with no named rule or names a rule it does not build; the message names the rule and the way. |
| `an agent's goldens` names a guardrail golden | A `kind: guardrail` golden that `rules/guardrail.yaml` does not name in `plants` with a `blocks` entry. Name it, or make it ordinary or trap. |
| `the files the platform's image copies` | A file the image needs is missing: `__init__.py`, `agent.py`, `server.py`, `prompt.txt`, `manifest.yaml` or `tools/`. |
| `the repository's ruleset is the export` | The repository's settings were changed. Only the owner can fix this. |
| The deploy run fails at the registry | Another repository already deployed under your agent's name. Rename it. |
