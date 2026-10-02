# Milestones

Generated from `milestones/README.md` by `make ledger-plain`. Do not edit.

| Milestone | In plain words | Result | Video |
|---|---|---|---|
| [M00 — Start from nothing](M00.md) | Before any guardrail, a plain model gets the trick questions wrong; every later number is measured against that. | GREEN | [watch](../video/milestones/M00.mp4) |
| [M01 — Nothing runs unsigned](M01.md) | An agent can only be deployed from a build the pipeline signed; a changed byte, or a laptop, is refused. | RED | [watch](../video/milestones/M01.mp4) |
| [M02 — Rules have owners](M02.md) | A rule, a test, or a threshold changes only when the person who owns it says so, and loosening one needs two owners. | GREEN | [watch](../video/milestones/M02.mp4) |
| [M03 — It can't get worse quietly](M03.md) | A test that used to pass and now fails stops the change from merging; every attack we planted must be caught, or the change stops; a contract nobody signed never reaches the documents the agent will be given to read. | GREEN | [watch](../video/milestones/M03.mp4) |
| [M04 — Changing the model is tested, or it's blocked](M04.md) | When a team switches the agent to a different model, the switch is tested on its own proposal before it can go in; if a test that used to pass now fails, or answers get much slower, it can't go in. | RED | [watch](../video/milestones/M04.mp4) |
| [M05 — The agent stays in its box](M05.md) | An agent is stopped from reaching the internet, writing to another agent's files, or deleting its own logs, and each attempt is recorded in a separate account it cannot change. | RED | [watch](../video/milestones/M05.mp4) |
| [M06 — A team can do this in a day](M06.md) | One developer creates an agent from the template and ships it in a day, without touching the safety pipeline. | RED | [watch](../video/milestones/M06.mp4) |
| [M07 — Upgrades come to you](M07.md) | A new platform version, a new model, or a retirement arrives as a PR; the team never edits the pipeline. | OPEN | not recorded |
| M08 — We rehearsed the bad day | A hostile agent tried six things; all six were stopped, recorded, and recovered from. | OPEN | not recorded |
