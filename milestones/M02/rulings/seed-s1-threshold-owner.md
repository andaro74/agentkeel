---
# Seed S1 (SPEC/02 §5), the one-key form. This file exists only inside
# tests/fixtures/m02/s1-one-key.patch and on the seed's branch; it is never
# on main. `pr:` is set to the seed PR's number when the human opens it.
ruling: seed-s1-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/02-seats-and-change-gates.md#5-the-seeded-cases
pr: 0
---

# Seed S1: one key on a relaxation

`cost_cap.tokens_per_run` moves from 150000 to 300000. Upward relaxes it
(`thresholds.yaml`, "Relaxes upward"). This file is the Threshold Owner's
key and it is the only one: no second file from a second seat exists on
this branch. `ruling-cited` is satisfied by this file. Only `two-key` can
refuse the change, and it must.
