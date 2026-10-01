# One question through refagent

The question is golden `g-001`: *Can we publish 'Pim and the Paper Whale'
on SVOD in the United States on 2026-12-25, and under what constraints?*
Every step below is code in this repository; the file is named at each.

## 1. The question reaches the agent

In CI, `make evals` asks every live golden. When the deployed runtime runs
the tree's own bytes, the runner calls it (`InvokeAgentRuntime`); when it
does not, refagent's code runs in the runner instead, and the envelope
says which (`mode`). Only the question is sent, never the golden's
expected answer (`src/agent/run.py`).

## 2. The guardrail reads the question

refagent sends the question to the model with the platform's guardrail
pinned by id and version (`agents/refagent/manifest.yaml`). The guardrail
is built from the Rule Owner's files (`agents/refagent/rules/`). On a
red-team question, such as `g-019`'s "ignore the holdback", the guardrail
blocks it before the model answers, and the envelope records which rule
blocked it. `g-001` passes through.

## 3. The model calls the tool once

The prompt (`agents/refagent/prompt.txt`) tells the model the rights table
is the truth, gives it the slate's title ids, and tells it to call
`check_availability` exactly once with the title, territory, platform and
date. Here: `t-005`, `US`, `SVOD`, `2026-12-25`.

## 4. The tool returns the row that governs

`check_availability` (`agents/refagent/agent.py`) finds the one row of the
rights table for that title, territory and platform: `r-019`. It returns
the row and the clauses it can be read under (`ML-2.1` among them). It does
not decide the answer. In the runtime the table is DynamoDB, loaded from
`data/rights_table.json` on deploy; the image holds no copy.

## 5. The model answers in fields

The reply is one JSON object: the row and clause it relied on, and the
answer's fields (`available: true`, `exclusive: true`, `constraints: []`).

## 6. build scores it; the gate rules on it

`src/verdict/build.py` compares each field with the golden's
`answer_fields`, checks that the cited row and clause exist and that the
tool call actually returned that row (an answer the tool did not ground is
wrong, however right it looks), and writes the envelope. A run over the
token cap is RED whatever it scored. `src/verdict/gate.py` rules on the
envelope again, from the files at that commit, and can disagree with
build. Only CI writes envelopes to `evals/history/`.

## What this walkthrough does not show

No judge reads the answer: fields are compared by code. No person
approves it. refagent does not read the licence text (no knowledge base).
No other agent is called. Each is M07's.
