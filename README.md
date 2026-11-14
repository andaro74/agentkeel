# agentkeel
A platform on Amazon Bedrock and AgentCore that controls change to an AI agent: who may alter its rules, tests, thresholds or model, what is measured first, and what record is kept. Eleven claims, each planted false first and measured in CI: five GREEN, six RED.

![AgentKeel: who may change an AI agent's rules, tests and model, and what is measured before the change ships, each claim tested with a planted failure. A change (a rule, a test, a threshold, a model) enters the platform, needs its owning seat's ruling, passes gates that ask for two keys to loosen anything, and reaches an agent that is signed, deployed and listed, held by a door for named callers, a guardrail with pinned rules, and an audit record in a second account. Below the platform, a ledger written by CI: planted, measured, ruled. Eleven claims measured: five green, six red. A proof of concept; the film slate is fictional.](docs/assets/readme-header.png)

> AgentCore proves the agent obeyed the policy tonight; this platform proves the policy could only have been changed by the seat that owns it, and that a model swap cannot relax it unnoticed.

That sentence is the aim, as [SPEC/00 §1](SPEC/00-overview.md) states it. It is not the result. The result is the [ledger](milestones/README.md): eleven claims, five GREEN and six RED. The model-swap half of the sentence is row 4, and row 4 is RED.

The authority for what agentkeel claims is [SPEC/00-overview.md](SPEC/00-overview.md). What was measured is in [milestones/README.md](milestones/README.md). The same ledger in plain words, one line per milestone, is [docs/milestones/README.md](docs/milestones/README.md).

agentkeel is a proof of concept built by one person. The reference agent answers questions about film title availability. Its slate, contracts and titles are invented.

## What it solves for the business

A company puts an AI agent in front of a real question. Amazon Bedrock AgentCore enforces the agent's rules while it runs. That leaves three things open:

- **Who may change the rules.** A rule, a test, a threshold or the model itself can be edited by anyone who can edit the repository.
- **What is measured before the change ships.** A model swap or a loosened bar can make the agent worse with no one seeing it.
- **What record survives.** If the agent's own account holds the evidence, the agent's own account can lose it.

agentkeel answers those three for every agent built on it:

| The question | What agentkeel does | Measured at |
|---|---|---|
| Who may change a rule, a test or a bar? | Each file has one owning seat. A change merges only with that seat's ruling file. Loosening anything needs rulings from two seats. | Row 2, GREEN |
| Can a change make the agent worse quietly? | A test that used to pass and now fails stops the merge. Every planted attack must be blocked, or the run goes RED. | Row 3, GREEN |
| Is a model swap tested first? | The swap runs against the tests on its own pull request. A breaking swap went RED. So did the one named equivalent. | Row 4, **RED** |
| Is what runs what was reviewed? | CI signs the bundle. The deploy checks the signature. An unsigned or altered bundle was refused. The agent inside the platform's construct was not measured at this row. | Row 1, **RED** |
| Can the agent reach out, or erase its tracks? | Its network has no route out, and its role is denied the calls. Four of six attempts were refused and recorded. Two left no record. | Row 5, **RED** |
| Who may ask the agent a question? | Only a caller the agent's manifest names, through a door the platform builds. | Row 10, GREEN |

Each row, with its numbers and its CI run, is in the table under [What the platform refuses, and what it has caught](#what-the-platform-refuses-and-what-it-has-caught).

## How it works

1. **An agent is a folder with a manifest.** The manifest pins the model, the guardrail, the seven seats, the AWS endpoints the agent may reach and the callers it admits.
2. **Every file has a seat.** [`.github/CODEOWNERS`](.github/CODEOWNERS) maps each path to one of seven seats. A change to a seat's file needs a ruling file from that seat.
3. **Gates read the change.** Required checks in GitHub Actions refuse a change with no ruling, a loosening with one key, a regressed test or a silent plant. The owner has no bypass.
4. **CI signs, and only CI deploys.** The bundle is signed with cosign. The deploy role is assumed through GitHub OIDC, on `main` only.
5. **A question goes through the door.** An HTTP API with an authoriser admits only the callers the manifest names. The runtime answers the door and nothing else.
6. **The agent answers from a table.** It runs in AgentCore Runtime, in a VPC with no route out. Its one tool returns a table row. Every call to the model carries the agent's pinned guardrail.
7. **The record leaves the account.** Calls, refusals and network flows are delivered to a bucket in a separate security account, which the agent account cannot edit.

![How a question is answered, and what surrounds it. A question (can we publish this title in this territory, on this platform, on this date?) is asked by a caller the agent's manifest names, or by the platform's own test run. Inside agentkeel's agent account on AWS: 1, the door (Amazon API Gateway, AWS Lambda, Amazon Cognito) admits only a caller the manifest names; 2, the agent (Bedrock AgentCore Runtime, in a VPC with no route out) looks up one row of its table through its one tool; 3, the guardrail (Bedrock Guardrails, built from rules/baseline.yaml and the agent's own rules) is on every model call; 4, the answer cites one table row and one contract clause. Beside the path: seven seats (a rule, test or bar changes only with its owner's ruling), a signed deploy (cosign, GitHub OIDC, AWS CDK), the agent's table (Amazon DynamoDB, one KMS key per agent) and the registry (DynamoDB, Athena, Grafana). In a separate security account: 5, the record (AWS CloudTrail, VPC flow logs, the door's access log) goes to an audit bucket (Amazon S3 with Object Lock, one day) that the agent account cannot edit. Notes: the door is built for an agent whose manifest names callers, and the reference agent has none; a request to the internet is dropped and leaves no record, ledger rows 5 and 8, RED.](docs/assets/architecture.svg)

The picture shows the design. It is not a measurement. The reference agent, `refagent`, names no callers and has no door. The door was measured on a second agent at row 10.

## From template to running agent

A team does not build any of the above. It creates a repository from [`agentkeel-studio/agent-template`](https://github.com/agentkeel-studio/agent-template), fills in a manifest, and opens a pull request. The steps are in the [quickstart](docs/developer/quickstart.md).

![From template to running agent, in five steps. 1, create: a team makes a repository from the platform's template and names its agent (agent-template, manifest.yaml). 2, fill the seats: seven owners are named, and the team writes its tests, its rules and who may call the agent (seats, callers, goldens, rules/guardrail.yaml). 3, pass the check: every pull request is read by the platform, and with an empty seat or no tests it cannot merge (platform-check.yml, a GitHub App's check required by a ruleset). 4, signed: after the merge the platform builds the agent and signs what it built; the team does nothing here (deploy.yml, cosign, Amazon ECR). 5, deployed: the agent runs in the platform's network, is asked its own tests and is listed in the registry (infra/construct, AgentCore Runtime, DynamoDB). What was measured, ledger rows 6 and 7, both RED: timed once, 3,615 seconds from a new repository to an agent deployed and listed; the first agent from the template took 32,264 seconds to deploy after its merge, against a bar of 3,600; at row 6 the check refused every change, a correct one too, and no agent shipped.](docs/assets/workflow-template-to-agent.svg)

What was measured, from [row 7's envelope](evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json), written by [CI run 37149475766](https://github.com/andaro74/agentkeel/actions/runs/37149475766):

- The path was timed once: 3,615 seconds from a new repository to an agent deployed and listed. The bar is one working day. One run is not a rate.
- The first agent made from the template took 32,264 seconds to deploy after its merge. The bar is 3,600. Faults in the platform's own deploy caused it.
- At row 6 the platform check refused every change, a correct one included. No agent shipped at that milestone.

Rows 6 and 7 are both RED.

## What the platform refuses, and what it has caught

Every claim was planted false before any code that could catch it was written. CI then measured what happened. A GREEN row means the claim held on its planted case. A RED row means part of it did not, and the row says which part.

![What was planted and what happened, one card per ledger row. Row 0, M00, GREEN, start from nothing: planted a result with no baseline behind it; refused. Row 1, M01, RED, nothing runs unsigned: planted an unsigned bundle, a changed byte, a deploy from a laptop; each was refused; not measured: the agent running inside the platform's construct. Row 2, M02, GREEN, rules have owners: planted a bar loosened with one key, a test edited to pass, the owner's bypass; none merged. Row 3, M03, GREEN, it can't get worse quietly: planted seven attack questions and an unsigned contract amendment; 7 of 7 blocked, the amendment not admitted. Row 4, M04, RED, a model swap is tested: the breaking swap went RED, caught; the equivalent one went RED too, on one question. Row 5, M05, RED, the agent stays in its box: six hostile attempts; 4 refused and recorded, the slowest in 307 seconds; 2 left no record of a refusal. Row 6, M06, RED, a team ships in a day: a fake copy of the platform's check did not count, but the check refused every change and no agent shipped. Row 7, M07, RED, upgrades arrive as a pull request: 2 of 3 taken; the first agent took 32,264 seconds to deploy against a bar of 3,600; five pull requests against a cap of four. Row 8, M08, RED, the bad day rehearsed: a hostile agent making six attempts; 2 of 6 refused, 3 of 6 recorded; the emergency stop held once attached by hand. Row 9, M09, GREEN, each agent its own rules: 1 of 1 planted question stopped by the team's own rule. Row 10, M10, GREEN, in by the front door: 3 of 3 wrong callers refused, 1 of 1 admitted, each on the record. Five GREEN, six RED.](docs/assets/workflow-planted-and-measured.svg)

Every number below is the row's Measured cell in the [ledger](milestones/README.md). `make ledger` fails if a cell differs from its envelope. Each envelope was written by the CI run linked beside it.

| Row | What was planted | What was measured | State | Evidence |
|---|---|---|---|---|
| 0 | A result with no baseline behind it. | Refused. The frozen plain model, the control, passed 1 of 3 trick questions and 0 of 9 ordinary ones. | GREEN | [envelope](evals/history/9407615dcde09308490f6699c21a18100bfedcd2.json), [run](https://github.com/andaro74/agentkeel/actions/runs/35406351135) |
| 1 | An unsigned bundle; one changed after signing; egress the manifest does not list; a deploy from a laptop. | Each was refused. The agent was measured on the test runner only, not inside the construct, so the row is RED. | **RED** | [envelope](evals/history/e97125e970ccfc6d044612eb006cdbdbcdb99337.json), [run](https://github.com/andaro74/agentkeel/actions/runs/35680056132) |
| 2 | A bar loosened with one key; a test edited to pass; a one-sided edge; a renamed test id; the owner's bypass. | None of the five merged. | GREEN | [envelope](evals/history/8033c2a7a0588e557df577464c190e64a435e88a.json), [run](https://github.com/andaro74/agentkeel/actions/runs/35951008874) |
| 3 | A regressed test; seven attack questions; an unsigned contract amendment. | Plants fired 7 of 7. No regression merged. The amendment was not admitted. | GREEN | [envelope](evals/history/cb06c0dbf0019088c664c6df1ce7d67cc64f7d58.json), [run](https://github.com/andaro74/agentkeel/actions/runs/36270471757) |
| 4 | A model swap known to break the agent; a swap named equivalent. | The breaking swap went RED with 11 tests regressed. The equivalent swap went RED too, with 1 regressed, where GREEN was expected. | **RED** | [envelope](evals/history/05bd718feb0cc72ab78df13fccf47c3efb8a9314.json), [run](https://github.com/andaro74/agentkeel/actions/runs/36362949356) |
| 5 | Six hostile attempts, each expected in the security account within 600 seconds. | Four refused and recorded, in 199 to 307 seconds. The request to the internet and the call after the quarantine were not shown refused and left no record. | **RED** | [envelope](evals/history/28634e9a1405b034a3efbe898cc7675ebfab3587.json), [run](https://github.com/andaro74/agentkeel/actions/runs/36666223908) |
| 6 | A first pull request with an empty seat; a fake copy of the platform's check; a timed first agent. | The fake check did not count. The empty-seat case and the timed run were not read: the check refused every change. | **RED** | [envelope](evals/history/245eb9baf796cd9ceed652abe3805825208358c9.json), [run](https://github.com/andaro74/agentkeel/actions/runs/36886530498) |
| 7 | A platform upgrade, a model upgrade and a retirement, each arriving as a pull request. | 2 of 3 taken; the model upgrade was not merged. The first agent deployed 32,264 seconds after its merge, against a bar of 3,600. Five pull requests against a cap of four. | **RED** | [envelope](evals/history/dee74c3cf4102bfb6d4315faafb161c154618ed9.json), [run](https://github.com/andaro74/agentkeel/actions/runs/37149475766) |
| 8 | A hostile copy of the reference agent making six attempts on every call. | 2 of 6 refused and 3 of 6 recorded. The quarantine held once a person attached it. The recovery run was RED. | **RED** | [envelope](evals/history/e930e4da1e528fdfee77e62c52154970873add79.json), [run](https://github.com/andaro74/agentkeel/actions/runs/37402273717) |
| 9 | A question that a second agent's own rule must stop; a baseline rule weakened. | Planted rules fired 1 of 1. The weakened baseline was refused. | GREEN | [envelope](evals/history/c503324bac926e4a3295ee7e7f68a98cf254bc42.json), [run](https://github.com/andaro74/agentkeel/actions/runs/38400685274) |
| 10 | A caller with no identity; one the manifest does not name; a call around the door. | Refused 3 of 3 and admitted 1 of 1, each on the record. | GREEN | [envelope](evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json), [run](https://github.com/andaro74/agentkeel/actions/runs/39143365127) |

Each milestone has a one-page explainer under [docs/milestones/](docs/milestones/README.md), with what was planted and what happened in plain words.

**What is enforced, and what is only routed.** Five checks are required on `main`, and the ruleset's bypass list is empty:

| Required check | What it refuses |
|---|---|
| `checks` | `make validate` and the tests: a manifest outside its schema, an unowned file, a one-sided edge, a renamed test id, an edited workflow whose hash is not listed, a ruleset that differs from its export. |
| `evals` | A regressed test, a silent plant, a run over the token cap. |
| `ruling-cited` | A change to a seat's file with no ruling from that seat. |
| `two-key` | A loosening with rulings from fewer than two seats. |
| `cold-review-ruling` | A pull request with no ruling file, or one still a draft. |

The bundle's signature is checked in the deploy workflow, not on a pull request. Everything else is routed by CODEOWNERS and enforced by nothing.

## Who owns what

Seven seats. Each owns one decision and the files that hold it. The table is [SPEC/00 §5](SPEC/00-overview.md).

![Who owns what: seven seats, one decision each. Product: what to build, and when it is acceptable (SPEC, milestones, docs, README.md). Rule Owner: what the agent may say and do (rules, the guardrail id and version). Data Owner: what a correct answer is (evals/goldens, data). Threshold Owner: the bars the agent must clear, and which model is pinned (thresholds.yaml, the model pin in a manifest). Tool Owner: what a tool returns, and who may call an agent (tools, callers in a manifest). Security: what tooling and infrastructure may do (.github/workflows, infra). Engineering: that it works (src, scripts, tests, an agent's code). How a change gets in: a change to a seat's file needs that seat's ruling file; loosening a bar or retiring a test needs two seats' rulings. The gates read files, not people. In this project one person holds all seven seats, so a person holding every seat can write both keys.](docs/assets/workflow-who-owns-what.svg)

A seat is a responsibility and a route, not a reviewer. No gate waits for a person to approve. A gate reads a ruling file for its seat, its paths and its pull request number, and never for what it says. In this project one person holds all seven seats, so that person can write both keys.

## Main AWS services and technologies

Read from [`infra/`](infra/) and [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) at `3962809`.

**Built for each agent**

| Service | What it does here |
|---|---|
| Amazon Bedrock | Runs the model the agent's manifest pins, through one inference profile per agent. |
| Amazon Bedrock AgentCore Runtime | Runs the agent's container, inside the platform's VPC. |
| Amazon Bedrock Guardrails | One guardrail per agent, built from the platform's baseline rules and the agent's own. |
| Amazon DynamoDB | The table the agent's tool reads. |
| Amazon API Gateway and AWS Lambda | The door: an HTTP API whose authoriser admits only the callers the manifest names. |
| Amazon Cognito | Issues a caller's token. |
| AWS KMS | One key per agent. |
| Amazon ECR | Holds the agent's container image. |
| Amazon CloudWatch Logs | The door's access log: who asked, and whether they were admitted. |

**Platform-wide**

| Service or tool | What it does |
|---|---|
| Amazon VPC endpoints | The only way out of the agents' network. An agent reaches the AWS endpoints its manifest lists and nothing else. |
| AWS IAM with GitHub OIDC | CI assumes a deploy role. No AWS key is stored in GitHub. Permission boundaries cap every role the platform makes. |
| AWS CDK and AWS CloudFormation | Every stack is code, checked with cdk-nag. |
| AWS Systems Manager Parameter Store | Settings the Security seat owns. |
| AWS Budgets | A spend ceiling on model calls. |
| AWS CloudTrail and VPC flow logs | The record of calls, refusals and network flows. |
| Amazon Data Firehose | Delivers the door's call records to the security account. |
| Amazon S3 with Object Lock | The audit bucket in the security account, and the corpus buckets. |
| Amazon DynamoDB, Amazon Athena and Grafana | The registry of deployed agents, and a panel over it. |
| Sigstore cosign | Signs each bundle, keyless. The deploy checks the signature. |
| GitHub Actions, a ruleset and a GitHub App | The gates, the deploy, and the platform check on an agent repository's pull requests. |
| Python and `uv` | The gates, the verdict builder and the observers. |

## What it is not

- **Not an agent framework.** An agent is plain code inside the platform's construct.
- **Not a production landing zone.** It runs in two accounts: one for agents, one for evidence. An account per team is a named follow-on.
- **Not a dashboard product.** One Grafana panel over the registry.
- **Not a compliance certification.** The [compliance map](docs/compliance/map.md) links controls to evidence paths. It certifies nothing.

## Shortcomings

- **Six of eleven claims are RED.** SPEC/00 asked for at least seven GREEN. That bar was not met and was not moved.
- **One person holds all seven seats.** The gates show that a change was named and under which seat. They do not show that a second person looked.
- **Each row was measured once.** One run is not a rate.
- **A request to the internet leaves no record.** The network drops it before any rule sees it. Rows 5 and 8.
- **A credential in a tool result is not stopped.** No filter on tool results was built. At row 8 the planted key reached the answer.
- **The quarantine is attached by hand.** Nothing attaches it by itself.
- **The audit bucket's lock is one day.** SPEC/00 first asked for seven years.
- **The model-upgrade pull request was opened and not merged.** Its own run was RED.
- **An agent two platform versions behind can neither upgrade nor retire through the platform.** Found after the last milestone, in [milestones/maintenance/README.md](milestones/maintenance/README.md), and not repaired.

**Not built, so not measured:** retrieval from a knowledge base; a model that judges answers (correct means the answer's fields match, compared by code); the AgentCore Gateway and Identity's credential vault; a human-approval step; a second agent's code and the edge to it; canary rollout; per-caller limits; the `docs-current` check. The full list is [SPEC/00 §12](SPEC/00-overview.md).

**Not recorded:** videos for M09 and M10, by ruling. Of six planned walkthrough recordings, one was made.

## A worked tenant: pharmadelta

[`andaro74/pharmadelta`](https://github.com/andaro74/pharmadelta) is a demo built on agentkeel. Its agent, [`agentkeel-studio/label-impact`](https://github.com/agentkeel-studio/label-impact), was made from the template. At the last read-back, on 2026-11-07, it and the reference agent were the two agents running on the platform ([milestones/maintenance/README.md](milestones/maintenance/README.md)).

pharmadelta has its own spec, its own ledger and its own pages. What it claims about its agent is measured there, not here.

| Repository | Holds |
|---|---|
| `andaro74/agentkeel` (this one) | The platform: gates, signing, deploy, guardrail, door, registry, audit. |
| [`agentkeel-studio/agent-template`](https://github.com/agentkeel-studio/agent-template) | What a new agent repository starts from. |
| [`agentkeel-studio/label-impact`](https://github.com/agentkeel-studio/label-impact) | A tenant's agent: manifest, code, prompt, tool, data, rules, tests. |
| [`andaro74/pharmadelta`](https://github.com/andaro74/pharmadelta) | The tenant's demo: its ledger, its test questions, its pages. |

## How it was built

With Claude Code, one milestone at a time. Each milestone has one claim, one planted failure and one measured verdict, in at most four pull requests:

1. **Plant.** The spec, the ledger row and the false state. Nothing that makes it pass.
2. **Measure.** The gate that reads the plant. The plant must go RED here.
3. **Repair.** Whatever a cold review of the measurement found.
4. **Close.** The measured cell, the explainer, the tag.

A milestone that needs a fifth pull request closes RED. Only a result written by CI counts; a local run is not evidence. Every pull request ends with a ruling file, and the person who writes the diff does not merge it.

The rules a session works under are in [CLAUDE.md](CLAUDE.md). Each rule change is an [ADR](docs/adr/). The seat subagents and the three skills that open, review and close a milestone are under [`.claude/`](.claude/).

```
make validate       the repository's own checks
make evals          the control and the reference agent against the tests, as CI runs them
make ledger         the ledger with measured values; fails if a cell differs from its envelope
make plants         the planted cases, and whether each fired on the last run
```
