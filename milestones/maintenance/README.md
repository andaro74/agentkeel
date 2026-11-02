# Maintenance

Pull requests after the `m10` close (M10 was the last milestone; building
stopped at its close). A maintenance PR carries no ledger row, no
explainer and no video entry, and is not PR 1 to 4 of anything. It still
ends with a ruling file here, under `rulings/`, one per seat whose path it
touches, so `ruling-cited` and `cold-review-ruling` hold as they did; and
a change to the account is still made by hand by the human, recorded in
the README of the stack it changed.

| Ruling | PR | What |
|---|---|---|
| `endpoints-one-subnet` (Security), `endpoints-one-subnet-engineering`, `endpoints-one-subnet-product` | #58 | the five interface VPC endpoints in one subnet: ten ENIs to five, $74.40 a month to $36.50 expected |
