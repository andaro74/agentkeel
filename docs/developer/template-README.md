# An agent from the agentkeel template

This repository holds one agent. It starts as a copy of agentkeel's
reference agent, `refagent`, which answers title-availability questions
from a rights table. You make it yours, and agentkeel ships it.

Start with the quickstart:
<https://github.com/andaro74/agentkeel/blob/main/docs/developer/quickstart.md>

What is here:

| File | What it is |
|---|---|
| `manifest.yaml` | The agent's name, model, guardrail and owners (seats). Every seat starts empty. |
| `goldens/` | The agent's own tests. Starts empty. You add at least one ordinary question and one trap. |
| `data/table.json`, `data/clauses.json` | The rows and clauses the agent answers from. Each test cites one of each. |
| `rules/guardrail.yaml` (optional) | Your agent's own rules, on top of the platform's. Not shipped by the template; add the folder when your agent needs a rule of its own. See "Your own rules" in the quickstart. |
| `agent.py`, `server.py`, `prompt.txt`, `tools/` | The agent itself. |

What you cannot change from here:

- **The platform check.** Every pull request needs a passing check named
  `platform-check`, posted by agentkeel's GitHub App. A workflow in this
  repository can post a check with that name; GitHub documents that a
  check bound to an App is accepted from that App only. It was attempted
  once, as M06's seed S2: the stand-in's check did not let the pull
  request merge. At that time the platform's own check was refusing every
  head for a fault of its own. It was to be tried again at M07 and was
  not, so that question is still open.
- **The deploy.** agentkeel deploys this agent from its own pipeline after
  a merge. Nothing in this repository holds a cloud credential.
- **The platform's rules.** Every agent's guardrail carries agentkeel's
  `rules/baseline.yaml` (on day one: phone numbers and email addresses
  hidden in any answer). A `rules/guardrail.yaml` here is **read**, and
  merged onto that baseline **add-only**: you can add a denied topic or a
  PII entity, and you cannot remove, weaken or redefine one of the
  platform's, turn a content filter on or off, or use a key the format
  does not have. A file that tries is refused by the platform check, with
  the rule and the way named. Without a `rules/` folder your agent is
  guarded by the reference agent's rules, as before.
- **Every rule you write carries a planted question.** A denied topic in
  your `rules/guardrail.yaml` is shown to work by a golden of
  `kind: guardrail` (`expected: BLOCKED`) that the file names in `plants`,
  with a `blocks` entry naming the rule that must stop it. A rule nobody
  planted a question for, or a plant naming a rule the file does not
  build, is refused. Whether the rule stopped the question is read from
  the guardrail's trace after your merge and recorded; at M09 a silent
  rule does not stop your merge.
- **The guardrail itself.** With a `rules/` folder, the platform builds a
  guardrail for your agent from the merged rules when it deploys, named
  `agentkeel-<your agent's name>`, and puts your agent's calls through it.
  Your `manifest.yaml` pins it: on the first pull request, before it
  exists, a placeholder of your own (not the reference agent's); after the
  first deploy, the id and version the platform wrote to the registry,
  which the platform check holds you to from then on.
