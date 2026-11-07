---
# Maintenance PR #58. Security's key over the two Security paths it touches:
# infra/bootstrap/app.py (the five interface endpoints in one subnet) and
# infra/bootstrap/README.md (the paragraph, the kms proposal, the deploy
# record). Engineering's file is endpoints-one-subnet-engineering.md,
# Product's endpoints-one-subnet-product.md.
ruling: endpoints-one-subnet
seat: Security
authorises:
  - infra/bootstrap/app.py
  - infra/bootstrap/README.md
  - milestones/maintenance/rulings/endpoints-one-subnet.md
evidence:
  - SPEC/01-signed-bundle.md#6-the-code-that-reads-the-answer-pr-2-except-f14
  - infra/bootstrap/README.md#deploy-record-2026-11-02-the-interface-endpoints-in-one-subnet
  - https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html
  - https://github.com/andaro74/agentkeel/pull/58
pr: 58
---

# Ruling: maintenance PR #58, Security

Ruled by andaro74 as Security, 2026-11-07, as written.

## What is ruled

The five interface endpoints (bedrock-runtime, kms, logs, ecr.api,
ecr.dkr) are placed in the first isolated subnet alone. Ten ENIs were
$74.40 for October 2026, the largest line in the account; five are $36.50
a month expected. No control SPEC/01 §6 or SPEC/05 names moves: no
internet gateway, no NAT, every endpoint policy still scoped to the
account, the deploy boundary's denies on gateway creation unchanged, both
flow logs on the VPC. The egress rule the construct renders is a
security-group reference, VPC-wide, so a runtime in the other subnet
matches the same rule and leaves the same flow record. Not a relaxation
and not two-keyed: the AZ count is not a bar, a rule, a golden or
retention. A NAT gateway was not taken: no cheaper, and SPEC/01 §6 says
no NAT.

The change was deployed by hand on 2026-11-02 before this file was ruled
(README, "Deploy record"): the change set read five Modify and no
replacement, every endpoint id, security group id and parameter is the
same after as before, and the runtime answered g-001 the same way. That
record is a read, not evidence; the envelope for the first `main` commit
after the merge is what measures the runtime after the change.

## What is given up, stated

The endpoints' second Availability Zone. An impairment of us-west-2a now
takes every interface endpoint from a runtime in us-west-2b.

## The kms proposal

The README's paragraph on the kms endpoint is a proposal with its unknowns
named, not a change; this ruling does not authorise it.

## The security-reviewer's read of this PR

0 BLOCK, 2 FINDING, 11 NOTE. F1 (no ruling file): this file and its two
companions. F2 (present tense before the deploy): the prose now states
the template, the expected figure and the deploy record. N4 and N8 taken
(the subnet id named, the Cost Explorer read named, the test pins index
0). N6 taken (the kms paragraph marked a proposal, its source and unknowns
named). N7 taken (deploy when nothing is in flight; the second ENI is
deleted live). N2's cross-AZ cost stated. The report is in the PR body.
