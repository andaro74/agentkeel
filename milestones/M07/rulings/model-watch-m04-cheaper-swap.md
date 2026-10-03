---
# Drafted by model-watch on agentkeel's main, as the App agentkeel-upgrades.
# A seat rules it; the platform does not.
ruling: model-watch-m04-cheaper-swap
seat: Threshold Owner
authorises:
  - agents/refagent/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M07
  - SPEC/07-upgrade-retire-surfaces.md
  - milestones/M07/runs/f7_3_rollback.yaml
pr: 43
---

# Ruling: model-watch, the swap to pinned_roles.m04_cheaper_swap

Drafted by model-watch for the Threshold Owner (https://github.com/andaro74/agentkeel/actions/runs/37126101337). Not ruled: a seat replaces this line with its own.

## What this pull request changes

refagent's pin moves from `anthropic.claude-sonnet-4-6` to `anthropic.claude-haiku-4-5-20251001-v1:0` (`pinned_roles.m04_cheaper_swap`, the candidate named in `milestones/M07/runs/f7_3_rollback.yaml`). The whole pin is copied: id, version, profile, region.

Nothing else: no workflow, no bar, no golden, no other field of the manifest.

## What the seat is asked to rule

A model id change is measured by the gate, not two-keyed (SPEC/04 section 10): this pull request's own `evals` run is the shadow run, with A-vs-A, and M04's gate rules it (F4.1, F4.2, F4.4). Its verdict is not stated here. It is merged only if that envelope is GREEN and every required check is green. A swap never gets a second run.

This file is not a person's edit of the upgrade (SPEC/07 section 1, item 3): a seat ruling a change is the gate working.
