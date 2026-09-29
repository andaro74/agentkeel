---
# M05 PR 2, the measure. Product's key. One seat per file: Security's is
# pr2-security.md, Engineering's pr2-engineering.md (with the cold review),
# the Threshold Owner's pr2-threshold-owner.md. The PR touches no Rule
# Owner, Data Owner or Tool Owner path.
ruling: pr2
seat: Product
authorises:
  - SPEC/05-containment-and-evidence.md
  - milestones/README.md
  - milestones/M05/README.md
  - milestones/M05/runs/f5_4_chain.yaml
  - milestones/M05/runs/f5_7_quarantine.yaml
  - milestones/M05/rulings/**
evidence:
  - SPEC/00-overview.md#8-M05
  - SPEC/05-containment-and-evidence.md
  - milestones/M05/feasibility.md
  - milestones/M05/rulings/pr1.md
  - evals/history/36a86b1527fe2d49a2ed15f83242268ccd691a00.json
pr: 31
---

# Ruling: M05 PR 2, Product

Drafted by the session; the human rules as Product before the merge.

## What this PR is

PR 2 of M05, the measure: 2 / 4. Every reader SPEC/05 §6 names, in its
order, and nothing that decides the row: the row is read at PR 3's run,
after S3, S4 and S7 are attempted against the merge deploy (SPEC/05 §5.1,
the named P3 exception ruled at PR 1).

## Rulings

1. **The Rule Owner's filter on tool results does not land in M05.**
   SPEC/05 §6 let it ride "if the cap allows"; it would move the guardrail
   pin, redeploy the bootstrap and re-measure every count, for a live half
   that is already cut (§9 cut 1). It goes to M06 with cut 1, and
   `feasibility.md` §6 rows 2 and 3 go with it, as that row said they
   would. S5's reader is `build`'s, and it lands.
2. **S4's and S7's run files name the session id** (amended before
   either attempt is made). CloudTrail records `InvokeAgentRuntime` with
   its `runtimeSessionId`, and the runtime is handed the same id; the CLI
   prints no request id for the call. The run files' commands pass
   `--runtime-session-id`, and each entry records it.
3. **The stand-in carries refagent's boundary and explicit denies, not
   refagent's grants.** SPEC/05 §2 says "the agent role's grants"; neither
   S2 nor S3 uses one, and copying them would make a second principal
   able to call refagent's model. SPEC/05 §8 already says a stand-in is
   not the agent; this is one more way it is not.
4. **Stated before PR 2's run.** S4 and S5 refused by their readers
   (`F5_1: pass`). refagent otherwise as at M04: ordinary 9/9, traps 2/2,
   guardrail 2/3, red team 5/5, golden plants 7/7, A-vs-A not run. Row 5,
   as the ledger reads PR 2's envelope: S1, S2 and S6 each refused by the
   control named for it and recorded within N if they were attempted
   before the run; S3, S4 and S7 **not made**, so row 5 reads RED on that
   envelope. That is expected and is not the row's measurement: PR 3's run
   is. A row 5 reading RED gates nothing, so this PR can merge with it.
5. **Unsure D stays named** in SPEC/05 §8, as ruled at PR 1.
6. **SPEC/05 amended on the reviews** (platform-architect F1, F4 to F6;
   security-reviewer): §2 says the stand-in carries the denies, not the
   grants (ruling 3); §6's "every role in that account" is every role
   `infra/security/` makes; §8 names the organization's reach over the
   security account and the controls this PR adds that no seed attempts.
   None of them is described as working.
7. **SPEC/05 §6 amended on the second Security read** (its F1): S6's
   `test/` grant names the agent account, not the admin alone, and lists
   the put and the retention read beside the two actions; the lock's IAM
   action is named. S2's and S6's run files say the phrase the reader
   requires, "explicit deny in a resource-based policy", before either
   attempt is made (second cold read, F2).
8. **S1's origin is a Lambda in the platform VPC, not a CloudShell VPC
   environment** (ruled by the human as Product, with Security,
   2026-09-29, on the evidence recorded in `runs/f5_1_curl.yaml`). The
   CloudShell environment's curl to 1.1.1.1 at 12:56:42Z timed out, and no
   flow record of it exists: its ENI read NODATA in every window through
   13:15:41, while its connection to the Bedrock endpoint at 13:15:47Z was
   recorded as ACCEPT on the same ENI. CloudShell drops outside traffic
   before its ENI, so the security group never refused it and no record
   could exist. `agentkeel-seed-s1` (`infra/audit/`) sends from its own ENI
   behind refagent's security group. SPEC/05 §5 and §8 amended. Neither
   origin is the runtime (§8).

## What a reader can run

```
uv run pytest tests/test_m05_seeds.py tests/test_m05_readers.py tests/test_observe_containment.py -q
make validate      # sixteen checks; cdk-nag reads the two new stacks
make ledger        # exits 0; "as row M05 reads it" names each seed
make plants        # S1 to S7, every reader in the tree
```
