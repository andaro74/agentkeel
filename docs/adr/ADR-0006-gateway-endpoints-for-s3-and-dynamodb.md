---
adr: ADR-0006
title: The platform VPC has gateway endpoints for S3 and DynamoDB, as well as interface endpoints
status: Accepted
date: 2026-09-19
seat: Security
authorises:
  - Security  # SPEC/00 §8 M01, the bootstrap stack's "VPC with interface endpoints only"
amendments: 1
---

# ADR-0006 — Gateway endpoints for S3 and DynamoDB

## Context

SPEC/00 §8 M01 describes the bootstrap stack as a "VPC with interface
endpoints only". The VPC has no internet gateway and no NAT gateway, so
every AWS call the agent makes has to leave through an endpoint or not
leave at all. That is the point of the line, and it stands.

refagent reads the rights table from DynamoDB (SPEC/01 §6), and the
runtime pulls its image layers from S3. AWS does not offer an interface
endpoint for either service in the form this needs: S3 and DynamoDB are
reached from inside a VPC through **gateway** endpoints, which are route
table entries, not elastic network interfaces. Writing the rule as
"interface endpoints only" would leave M01 with two services the agent
must reach and no way in the VPC to reach them.

There is a real difference between the two kinds, and it is why this is
an ADR and not a note. An interface endpoint has a security group, so the
agent's egress can name it. A gateway endpoint has none: egress to it is
written against the service's managed **prefix list**. Both are policy
points — an endpoint policy scoped to this account applies to either —
but only one of them can be reached by a security group id.

## Decision

The platform VPC has:

- **interface endpoints** for `bedrock-runtime`, `kms` and `logs`, each
  with an endpoint policy scoped to this account;
- **gateway endpoints** for `s3` and `dynamodb`, each with an endpoint
  policy scoped to this account.

SPEC/00 §8 M01's "VPC with interface endpoints only" is amended to read:
**VPC with interface endpoints, and gateway endpoints for S3 and
DynamoDB.** No other service is reachable, and no route leaves the VPC.

The five names are the manifest's `endpoint_allowlist` enum (ruling d,
`milestones/M01/feasibility.md` §2.6): `bedrock-runtime`, `dynamodb`,
`kms`, `logs`, `s3`. A manifest that names anything else is refused by
the schema, and an egress rule to anything else is refused at synth
(seed S3, both forms).

## Consequences

- `GovernedAgent` writes two shapes of egress rule: to a security group
  for the three interface endpoints, to a prefix list for the two
  gateway ones. The check that reads S3 accepts both and nothing else.
- A managed prefix list id has no CloudFormation attribute, so the
  bootstrap stack cannot publish those two ids the way it publishes the
  three security group ids. The human who deploys the bootstrap stack
  writes `/agentkeel/security/prefix-list/s3` and
  `…/dynamodb` with one command each (`infra/bootstrap/README.md`).
  Until they exist, an agent stack does not deploy. That is a gap in
  automation, not in the control: a wrong value there widens nothing,
  because the endpoint policy and the boundary still apply.
- Arbitrary hostnames remain M05 (ruling d). The enum is five AWS
  service names, and the reason it is an enum is that a hostname is not
  something the VPC can refuse at synth.

## Amendment 1 (M02 PR 1, 2026-09-22): seven names, not five

Security.

"The five names" above was true at M01 PR 1. Ruling d was amended at M01
PR 3 (`milestones/M01/rulings/pr3.md`): the runtime pulls its image
through `ecr.api` and `ecr.dkr`, both interface endpoints, and the
construct refuses a manifest that omits them. The enum is therefore
**seven** names: `bedrock-runtime`, `dynamodb`, `ecr.api`, `ecr.dkr`,
`kms`, `logs`, `s3`. Five are interface endpoints and two are gateway
endpoints; the shapes of egress rule in "Consequences" are unchanged.
The sentence above is left as written, dated by this amendment
(`milestones/M02/open.md` row 22).

This is ADR-0006's first amendment. One is left.
