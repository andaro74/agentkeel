---
# M10 PR 2 (#55), the Tool Owner's key over its field: `callers` in the two
# manifests (absent to [], one key, ADR-0016 decision 2), and the key the ADR
# asks of this seat at entry 7. The schema file and src/validate/callers.py
# are Engineering's paths (pr2-engineering.md); the field's shape, its
# refusals and the ADR's rule are this seat's to rule (SPEC/10 §11 R4).
ruling: pr2-tool-owner
seat: Tool Owner
authorises:
  - agents/refagent/manifest.yaml
  - agents/ratings-helper/manifest.yaml
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - docs/adr/ADR-0016-two-keys-on-a-caller-admitted.md
  - milestones/M10/feasibility.md
  - milestones/M10/rulings/pr1.md
pr: 55
---

# Ruling: M10 PR 2, Tool Owner

Ruled by andaro74 as Tool Owner, 2026-10-15, as written.

## R4. The manifest field

`callers`, in the shape SPEC/10 §2 fixed at PR 1 and `src/manifest/schema.json`
carries from this PR: a list of `{subject, issuer}`, both required, no other
key, no two entries alike; `subject` a name (`^[a-z][a-z0-9-]{2,30}$`) and
never `platform`, which the schema's pattern excludes and `callers_errors`
refuses by name (the seat's reading on this PR's finding 1: both, since a
manifest read by the schema alone must not admit the platform's own name
either; SPEC/10 §2's line now says so); `issuer` the symbol `self`, the
agent's own pool, the one issuer at M10. Optional in the schema and required
by `src/validate/callers.py`, so a manifest with no key fails for its named
reader (S2). Not an edge: `semver.py` reads `may_call` and
`may_be_called_by` only and computes no bump for it; `version` stays. Not a
rule. `[]` is the default and admits no one.

## The two manifests: absent to `[]`, one key

`agents/refagent/manifest.yaml` and `agents/ratings-helper/manifest.yaml`
each gain `callers: []`. Absent to `[]` is not a relaxation (ADR-0016
decision 2; S3's guard case "absent to an empty list" is this diff), so this
file is the one key, and this file is the one the two manifests' comments
name. refagent is not behind a door at M10 (SPEC/10 §8): the construct
refuses a refagent manifest with a caller at synth, and its runtime keeps IAM
authorisation. The line moves refagent's bundle digest, so the first deploy
after the merge re-signs and redeploys refagent (`tool-owner` note 8 on PR 1);
S4's second guard reads its plants whole on the envelope after.

## ADR-0016, entry 7: this seat's key

A subject added to `callers`, or the key removed from a value, is two keys
from this PR: this seat's file covers the path and any second seat names it.
Absent to `[]` and a subject removed are not. A `callers` that stops being a
list is read as removed, with the same refusal string (this PR's finding 3,
repaired). The construct's authoriser widened is Security's under
`ruling-cited`, unread by `two-key` (SPEC/10 §8).

## From this seat's read of the PR (0 BLOCK, 3 FINDING, 14 NOTE)

| # | Disposition | Seat |
|---|---|---|
| F1 | **Both readers keep the `platform` exclusion**: the schema's pattern and `callers_errors` by name. SPEC/10 §2's sentence is amended to say the pattern excludes it | Tool Owner; Product (the line) |
| F2 | **Repaired**: this file, which the two manifests' comments name | Tool Owner |
| F3 | **Repaired**: a `callers` that stops being a list is refused as `callers removed from a value (ADR-0016 entry 7)`, decision 1's own words; the test pins it | Engineering (the gate); Tool Owner (the text) |
| N (semver docstring) | **Repaired**: `src/validate/semver.py`'s reason for refagent carrying no `version` no longer says the digest does not move | Engineering |
| N (uniqueItems with a second issuer) | Recorded for the milestone that adds a second issuer: `callers_errors` alone catches a duplicate subject then | Tool Owner |
| the rest | Recorded; nothing to settle | — |

### The report, verbatim

> Read: the diff a67de63...afd7f31 (Tool Owner paths): `src/manifest/schema.json`, `agents/refagent/manifest.yaml`, `agents/ratings-helper/manifest.yaml`, `src/validate/callers.py` (new), `src/gates/two_key.py`, `src/gates/__init__.py`, `docs/adr/ADR-0016-two-keys-on-a-caller-admitted.md` (new). Also read: SPEC/00 §5 (Tool Owner row, line 119), §6 Manifest (line 243), R7 (line 1176); SPEC/10 §2 "`callers`" (lines 134-161) and §11 R4 (lines 635-644); `src/validate/semver.py` whole; `src/validate/agent.py` `evaluate()` (lines 176-225); `tests/test_m10_seeds.py` S2, S3 and `tests/fixtures/m10/s3-caller-added/cases.json`; `tests/test_m10_readers.py` (callers_errors and entry 7 tests); `milestones/M10/rulings/` listing. No edge is named by the diff: both manifests keep `may_call: []` and `may_be_called_by: []`, so there is no second manifest to read on an edge.
>
> **1. Closed schemas**
> - NOTE. The new `callers` items object is closed: `"additionalProperties": false` at `src/manifest/schema.json` line 84 (`"items": {"type": "object", "additionalProperties": false, "required": ["subject", "issuer"], ...}`); the root is closed at line 6. The array itself is `"type": "array", "uniqueItems": true`. No object level in the diff is open. No tool input/output schema (`agents/*/tools/*.json`) is touched. Nothing to settle.
>
> **2. Semver preview**
> - NOTE. Computed bump: none. `semver.py` reads only `input`/`output` of a tool schema (line 81, `contract_changed = any(before.get(k) != after.get(k) for k in ("input", "output"))`) and the two edge keys of a manifest (line 114, `for k in ("may_call", "may_be_called_by")`). `callers` is read nowhere in it; `grep callers src/validate/semver.py` is empty. Neither manifest carries `version`, so both stay at the default `1.0.0` (line 113, `parse_version(before.get("version")) or (1, 0, 0)`), and the diff asserts no version, so nothing disagrees with the computed bump. The `version` description's new sentence (schema.json line 193, "`callers` is not an edge and computes no bump") matches the code. `src/manifest/schema.json` is not a tool schema under R7's "schema" (the TOOL regex at semver.py line 29 is `agents/<name>/tools/*.json`), so widening it computes no bump either. Consistent with SPEC/10 §2 line 146-148 and R4.
>
> **3. Both sides**
> - NOTE. No edge changes; `callers` is not an edge (SPEC/10 §2 line 154: "Not an edge: a caller is not an agent, so `may_be_called_by`'s two-sided check does not apply"). The only second side a caller has is `issuer: self` (the agent's own pool), which the enum of one fixes at schema.json line 88 (`"issuer": {"enum": ["self"]}`) and `callers.py` line 255 (`ISSUERS = ("self",)`). Nothing to settle.
>
> **4. Ceilings**
> - NOTE. Unchanged. Depth, fan-out, rps and concurrency are read by `edges.check` only when an edge exists; none does. No cycle: the graph after the diff has no edges. SPEC/10 §2 line 160 says `ceilings` binds no caller; the diff adds no ceiling for callers, which matches.
>
> **5. Results**
> - NOTE. No tool result or output schema is on the diff. `callers.py` line 270-293 reads the manifest it is given and nothing else (its docstring, line 240-244: "no pool, no door, no record"), so no credential can reach a result from this path. Nothing to settle.
>
> **The shape against SPEC/10 §2 as fixed at PR 1**
> - FINDING. The schema's `subject` pattern is `^(?!platform$)[a-z][a-z0-9-]{2,30}$` (schema.json line 87). SPEC/10 §2 line 139-140 fixes it as "`subject` matches `^[a-z][a-z0-9-]{2,30}$` and is never `platform`, which `callers_errors` refuses by name", and the same section argues the key is "optional in the schema and required by `callers_errors`, so S2's manifest fails for its named reader and not for the schema". The diff puts the `platform` exclusion in both places: the schema refuses a `platform` subject as an unnamed pattern error, and `callers_errors` refuses it again by name (callers.py line 284-286). `evaluate()` does not short-circuit (agent.py lines 203 and 217 both run), so the named refusal still appears beside the schema's; the shape is wider than the one §2 says PR 2 copies. What settles it: the Tool Owner rules whether the exclusion lives in the schema too (then Product amends §2 line 139 to carry the lookahead) or in `callers_errors` alone (then the pattern reverts to `^[a-z][a-z0-9-]{2,30}$`). Either reading keeps the refusal; the ruling fixes which reader names it. Tool Owner rules; Product carries the §2 line if the first.
> - NOTE. `uniqueItems: true` compares whole entries. With one issuer in the enum, two entries with one subject are byte-identical, so the schema refuses them too; `callers_errors` refuses by name at line 288-289 ("subject ... is already callers[N]'s; one entry per subject"). When a second issuer comes (SPEC/10 §2 line 143, "a later milestone's"), `uniqueItems` stops catching a duplicate subject and only `callers_errors` will. Nothing to settle now; the later milestone's Tool Owner report should re-read it.
> - NOTE. The issuer refusal at callers.py line 292 reads `issuer {issuer!r} is not 'self' (the agent's own pool, the one issuer at M10)`; SPEC/10 §9 cut-list item 4 named the issuer check as cuttable. It is kept and tested (`test_m10_readers.py` line 56). Nothing to settle.
>
> **The two manifests' change, and the ADR**
> - NOTE. Each manifest's diff is one key: `+callers: []` (refagent line 30, ratings-helper line 12), both after `may_be_called_by: []`. ADR-0016 decision 2 (line 87-90) says "Absent to `[]`, and a subject removed: both admit no one new. The two manifests M10 PR 2 gives `callers: []` are exactly that diff, under the Tool Owner's one key". `caller_relaxations({}, {"callers": []})` returns `[]` (two_key.py line 159-168; pinned at `test_m10_readers.py` line 118 and by S3's guard "absent to an empty list"). Consistent.
> - FINDING. Both manifest comments cite `milestones/M10/rulings/pr2-tool-owner.md` (refagent line 25, ratings-helper line 9), and `src/gates/__init__.py` line 124 now attributes `callers` to the Tool Owner, so `ruling-cited` will look for a Tool Owner ruling with `pr: 55` whose `authorises:` covers both manifest paths. At head afd7f31 `milestones/M10/rulings/` holds `pr1.md` and `pr1-engineering.md` only; the file the comments name is not in the tree. What settles it: the Tool Owner writes `pr2-tool-owner.md` (`seat: Tool Owner`, `pr: 55`, `authorises:` both manifest paths and, as the field's owner, the ADR's decision 1-3 as its evidence) before the merge, or the comments stop naming a file that does not exist. Tool Owner rules (the file is its); Product carries the ADR's "Accepted" line (ADR-0016 line 54-57 says acceptance waits on that ruling reading "Ruled by").
> - NOTE. SPEC/00 §6 line 250 makes the bundle "manifest + prompt + tools + rules", so one line added to `agents/refagent/manifest.yaml` moves refagent's bundle digest; `semver.py`'s docstring (line 9-10) still gives "so that its bundle digest does not move for a field nothing reads yet" as the reason refagent has no `version`. The reason is now stale by one line, and the merge re-signs and redeploys refagent. No contract changes; Engineering may trim the docstring, and the deploy on merge is Security's to watch. Not this seat's to settle.
>
> **Entry 7: subjects, not bytes, and the refusal text**
> - NOTE. Entry 7 reads subjects: `subjects(after) - subjects(before)` over `{e.get("subject") for e in listed if isinstance(e, dict)}` (two_key.py line 159-164). A reorder (`test_m10_readers.py` line 120, `one[::-1]`), a subject removed (line 119) and absent-to-`[]` (line 118) each return `[]`; a first write naming a subject (line 121) and a subject added (line 122) each return one line. Held by S3's four cases (`cases.json` lines 4-17) and the five readers tests. Matches ADR-0016 decision 1 ("Read against the base ref, on subjects").
> - NOTE. The refusal text matches the ADR for the two strings it names. The gate prints `f"{r.path}: {r.what}; two keys ... {count}"` (two_key.py line 371-373) with `what` = `callers: subject 'lantern-desk' admitted (ADR-0016 entry 7)` or `callers removed from a value (ADR-0016 entry 7)`, which is ADR-0016 decision 3's `<path>: callers: subject '<name>' admitted (ADR-0016 entry 7)` and `<path>: callers removed from a value (ADR-0016 entry 7)`. S3 asserts `"{path}: callers"`, `"one seat holds a key"` and `"ADR-0016"` (test_m10_seeds.py line 202-204).
> - FINDING. The code emits a third string the ADR does not name: `callers no longer a list from a value (ADR-0016 entry 7)` (two_key.py line 166-167, pinned at `test_m10_readers.py` line 125). ADR-0016 decision 1 says "A `callers` that stops being a list is read as removed", and decision 3 lists two refusal strings only. The behaviour is right (refused, two keys); the text diverges from the ADR, and "no longer a list from a value" reads badly. What settles it: either the code emits `callers removed from a value` for that case too (one word, decision 1's own reading), or the ADR's decision 3 names the third string. Tool Owner rules on the gate's text for its field; Product carries the ADR line.
> - NOTE. A manifest deleted from the tree reads as `callers removed from a value` under entry 7, since `_load(None)` returns `{}` (two_key.py line 95-97) and `isinstance(before.get("callers"), list) and not isinstance(after.get("callers"), list)` then holds. Entries 3 and 4 already behave this way on a deleted manifest (line 326, 336), so entry 7 is consistent with the list; ADR-0016 does not say it. Nothing to settle unless `retire_agent.py` deletes a manifest with one key; then the Tool Owner's key is the second one it needs.
> - NOTE. A subject that is not a string (`{"subject": 123, "issuer": "self"}`) is dropped by entry 7 (`if isinstance(s, str)`, line 164) and so counts as no admission; the schema refuses it on `"type": "string"` (line 87) and `callers_errors` at line 282-283, so `validate` is RED before `two-key` matters. Nothing to settle.
> - NOTE. `src/gates/__init__.py` line 124 adds `"callers": "Tool Owner"` beside `may_call`, `may_be_called_by`, `ceilings`, `version`; matches SPEC/00 §5 line 119 as amended at M10 PR 1. `test_m10_readers.py` line 504-508 holds it. Nothing to settle.
> - NOTE. ADR-0016 is a new ADR, not ADR-0009 amendment 2 (ADR-0016 line 57-59 gives the reason: the last amendment is reserved for the Rule Owner, my note 4 on PR 1). `authorises: - Tool Owner` (line 48). Consistent with SPEC/00 §6 "at most two amendments; a third amendment is a new ADR" and with SPEC/10 §6 line 395.
>
> **What the seat should rule differently**
> - Nothing in the contract. The three findings are a reader split (where the `platform` exclusion lives), a missing ruling file the diff already names, and one refusal string the ADR does not list. None changes what the gate admits or refuses.
>
> BLOCK: 0 · FINDING: 3 · NOTE: 14
