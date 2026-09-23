---
# Seed S1 (SPEC/02 §5), the two-files-one-seat form. Exists only inside
# tests/fixtures/m02/s1-two-files-one-seat.patch and on the seed's branch;
# never on main. `pr:` is set to the seed PR's number when it is opened.
ruling: seed-s1-threshold-owner-second
seat: Threshold Owner
authorises:
  - thresholds.yaml
evidence:
  - SPEC/02-seats-and-change-gates.md#5-the-seeded-cases
pr: 15
---

# Seed S1: a second file, the same seat

Two ruling files, both `seat: Threshold Owner`, both `pr:` this PR. Two
files are not two keys: SPEC/02 §2 says the two seats must be distinct.
`two-key` must count seats, not files, and refuse this.
