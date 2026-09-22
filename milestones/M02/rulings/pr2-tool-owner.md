---
# M02 PR 2 (#12), the Tool Owner's key. Product's file is rulings/pr2.md.
ruling: pr2-tool-owner
seat: Tool Owner
authorises:
  # the may_call, may_be_called_by, ceilings and version fields only
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M02
  - SPEC/02-seats-and-change-gates.md#6-the-code-that-reads-the-answer-pr-2
  - milestones/M02/open.md
  - agents/refagent/tools/check_availability.json
pr: 12
---

# Ruling: M02 PR 2, Tool Owner

Drafted by the session; the human rules as Tool Owner before the merge.

## The stub's edge fields (open.md row 20)

`agents/ratings-helper/manifest.yaml`: `may_call: []`,
`may_be_called_by: []`, ceilings at the platform's bounds, `version:
1.0.0`. **No edge is declared on either side at M02**, on purpose: a stub
that named refagent would itself be one-sided on `main`, and an edge
declared on both sides would have made seed S3's patch stop applying.
The seed is never edited. The M07 PR that brings the code declares both
sides, with a major bump on both manifests, and that is computed
semver's first real case.

## Computed semver (SPEC/00 §5, R7)

`validate` computes the bump the diff needs and fails a smaller
assertion: a change to a tool schema's `input` or `output` is a major
bump of that schema's own `version`; a change to `may_call` or
`may_be_called_by`, or a major bump of any of its schemas, is a major
bump of the manifest's `version`; an edge `<agent>@vN` names the callee
manifest's major. A manifest with no `version` is at `1.0.0`: refagent's
carries none, so that its bundle digest does not move for a field
nothing reads. `check_availability.json` is unchanged at `1.0.0`, with
`additionalProperties: false` at every object level.

## The rest of row 20

The not-found branch deciding the clause, nested `row`, `pinned_roles`
typing, `territory` and `platform` typing: none is a reader of claim 2,
and none is in this PR. Re-dated to M07 with the helper's code, where
the schema is next opened.

## What a reader can falsify

```
uv run pytest tests/test_validate_m02.py -k "semver or edge or cycle or ceilings"
uv run pytest tests/test_m02_seeds.py -k s3
git apply --check tests/fixtures/m02/s3-one-sided-edge.patch
```
