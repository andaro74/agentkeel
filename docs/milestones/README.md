# Milestones

Generated from `milestones/README.md` by `make ledger-plain`. Do not edit.

| Milestone | In plain words | Result | Video |
|---|---|---|---|
| [M00 — Start from nothing](M00.md) | Before any guardrail, a plain model gets the trick questions wrong; every later number is measured against that. | GREEN | [watch](../video/milestones/M00.mp4) |
| [M01 — Nothing runs unsigned](M01.md) | An agent can only be deployed from a build the pipeline signed; a changed byte, or a laptop, is refused. | RED | [watch](../video/milestones/M01.mp4) |
| [M02 — Rules have owners](M02.md) | A rule, a test, or a threshold changes only when the person who owns it says so, and loosening one needs two owners. | OPEN | not recorded |
| M03 — It can't get worse quietly | A test that used to pass and now fails stops the deploy; the attacks we planted must all be caught; a fake contract never reaches the agent. | OPEN | not recorded |
| M04 — Changing the model is safe or it's blocked | A new model version is tried in the shadows first; if it breaks anything, the PR stays red. | OPEN | not recorded |
| M05 — The agent stays in its box | An agent can't reach the internet, other agents, secrets, or its own logs — and every attempt is recorded where it can't reach. | OPEN | not recorded |
| M06 — A team can do this in a day | Marketing creates a governed agent from the template, without touching the safety pipeline. | OPEN | not recorded |
| M07 — Upgrades come to you | A new platform version, a new model, or a retirement arrives as a PR; the team never edits the pipeline. | OPEN | not recorded |
| M08 — We rehearsed the bad day | A hostile agent tried six things; all six were stopped, recorded, and recovered from. | OPEN | not recorded |
