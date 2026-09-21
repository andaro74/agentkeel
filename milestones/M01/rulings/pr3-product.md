---
# M01 PR 3 (#9), Product's key. Ruling B: one seat per ruling file.
# `pr3.md` is Security's and `pr3-engineering.md` Engineering's; all three
# carry the same `pr`. This file keys the Product paths that carry BLOCK D's
# narrowing, which Security ruled at PR 2 (`pr2.md`, "BLOCK D").
ruling: pr3-product
seat: Product
authorises:
  - SPEC/01-signed-bundle.md
  - docs/milestones/M01.md
  - milestones/M01/rulings/pr3-product.md
evidence:
  - SPEC/00-overview.md#8-M01
  - milestones/M01/rulings/pr2.md
  - milestones/M01/rulings/pr3.md
pr: 9
---

# M01 PR 3 — Product's key: BLOCK D's narrowing, written down

**What was ruled, and by whom.** Security ruled BLOCK D at PR 2
(`pr2.md`):
- **What S8 proves.** A stack that installs the platform's checks and makes
  a bare AgentCore runtime is refused at synth.
- **What it does not prove.** A stack that never imports `infra.construct`
  is not read. Nothing at synth binds code that does not call it.
- **Where that goes.** An author who skips the import is **M05's**, through a
  CloudFormation Hook or a service control policy.

PR 2 ruled that PR 3 writes the narrowing into SPEC/01 §5 and keeps the
explainer from overclaiming. Those are Product's paths, so the key is here.
`pr3.md` lists item 5 under Security because Security made the ruling. This
file is where the text is keyed.

**What changed:**

| Where | Before | After |
|---|---|---|
| SPEC/01 §2, "The construct" | "An agent exists on this platform only as an instance of it." | Every agent is *meant* to be an instance of it; at M01 that is checked at synth on a stack that installs the checks, and no further |
| SPEC/01 §5, S8's row | "Read by: a check over the whole synthesised stack" | "…on a stack that installs it", with a pointer to the paragraph below |
| SPEC/01 §5, new paragraph | — | what S8 shows, what it does not, what else stands in the way at M01 and what does not, and who closes the rest (M05) |
| `docs/milestones/M01.md`, "For the business user" | — | one paragraph: the wrapper check refuses a build that asks to be checked; a build that never asks is M05's |

**Not changed, and why:**
- **Claim 1 and its falsifiers**, in the ledger row. The claim is about
  refagent ("refagent runs inside the construct"), and S8 never widened it.
  F1.1's "an agent built outside the construct … synthesises" is read by S8
  as narrowed here. A falsifier is not reworded after its plant, so the
  narrowing lives in the SPEC that says how the falsifier is read.
- **The explainer's "What happened".** It stays empty until the close.
- **The construct's own wording** is Security's, not keyed here. Security
  reworded it in the same PR: the refusal message in `governed_agent.py`,
  and `infra/construct/__init__.py`'s docstring (`pr3.md`, item 5).
- **The S8 fixture's docstring** still quotes the old §2 sentence. It is a
  planted seed, and it quotes the SPEC as it read when the seed was planted.

**One thing PR 3 added that bears on D**, and it is written into SPEC/01 so
it is not mistaken for more than it is. BLOCK F's repair holds the deploy
plane's `CreateAgentRuntime` to the platform VPC's subnets. That limits
*where* a runtime can be made, not *who* built it. `pr2.md` warned that D's
narrowing must not lean on the deploy plane's old inability to make a
runtime. It leans on this new condition only for what the condition says.
