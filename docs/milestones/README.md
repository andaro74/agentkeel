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
| [M07 — Upgrades come to you](M07.md) | A new platform version, a new model, or a retirement arrives as a PR; the team never edits the pipeline. | RED | [watch](../video/milestones/M07.mp4) |
| [M08 — We rehearsed the bad day](M08.md) | A hostile agent tried six things; all six were stopped, recorded, and recovered from. | RED | [watch](../video/milestones/M08.mp4) |
| [M09 — Every agent gets its own rules](M09.md) | A team writes the rules for its own agent on top of the platform's, each rule is shown to stop the question it was written for, and a team can add rules but cannot take the platform's away. | GREEN | not recorded |
| [M10 — Outsiders come in by the front door](M10.md) | Someone outside the team can only ask an agent a question through the platform's front door, under a name the agent's owners agreed to; every answer still carries the agent's rules, every question is recorded with who asked, and a stranger is turned away and the attempt written down. | GREEN | not recorded |
