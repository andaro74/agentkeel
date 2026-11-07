---
# Maintenance PR #58. Engineering's key over tests/test_bootstrap.py; the
# cold review is pasted in the PR body. Security's file is
# endpoints-one-subnet.md, Product's endpoints-one-subnet-product.md.
ruling: endpoints-one-subnet-engineering
seat: Engineering
authorises:
  - tests/test_bootstrap.py
  - milestones/maintenance/rulings/endpoints-one-subnet-engineering.md
evidence:
  - tests/test_bootstrap.py
  - https://github.com/andaro74/agentkeel/pull/58
pr: 58
---

# Ruling: maintenance PR #58, Engineering

Ruled by andaro74 as Engineering, 2026-11-07, as written.

`test_each_interface_endpoint_is_in_one_subnet` holds the five interface
endpoints in one subnet, the same for all five, the subnet whose
AvailabilityZone is index 0 of the region's AZ list. It fails on `main`:
there the synthesised template gives each endpoint two SubnetIds (the cold
review synthesised both). The endpoint, security-group and parameter
logical ids are identical in both templates, so the construct's reads of
`/agentkeel/security/endpoint/<name>` and `/agentkeel/security/subnet-ids`
are untouched. What this ruling does not cover: that the deployed runtime
still answers after the bootstrap deploy, which only the CI-written
envelope for the first `main` commit after the merge can show (the
by-hand read is in the bootstrap README); and the `infra/bootstrap/`
paths, which are Security's.

The cold review: 0 BLOCK, 3 FINDING, 4 NOTE. F1 (seat of the path): a
Security ruling, written. F2 (half the claim not in the diff): stated
above, and the README's deploy record says its runtime call is a read,
not evidence. F3 (an AZ the code does not pin): the prose names the
subnet index and the deployed subnet id; the test pins index 0. N1 taken
(`len == 5` in the test). N2 taken (cross-AZ transfer named in the README).
