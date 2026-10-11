# M09 feasibility

Written at M09 PR 1, the plant (`/open-milestone M09`). M09 is a tenth
milestone, opened after M08 (which SPEC/00 §8 called the last) closed RED
and was tagged. SPEC/00 was amended and SPEC/09 drafted first
(`d848ea9`), and `product-spec-reviewer` run on it before anything else
of PR 1 was written. ADR-0014 and SPEC/09's revisions followed
(`2320218`), then the seeds (`02db54e`).

The claim, and what makes it false today: an agent made from the template
is guarded by its own rules on top of a platform baseline, and each of
its rules is shown to fire on a question planted for it. On `main` at
`0ba6d1d` (tag `m08`) an agent repository's `rules/` is read by nothing
(the template README says so), every template agent must pin refagent's
guardrail (`src/validate/agent.py:109-117`), an agent repository may hold
no guardrail or red-team golden (`agent_goldens.py:35`), there is no
`rules/baseline.yaml`, and nothing reads whether a template agent's rule
fired. The fixture agent is refused by the platform check on its pin and
on its planted golden's kind: that refusal is the plant.

## 1. `product-spec-reviewer` report (verbatim)

Run on SPEC/09 at `d848ea9`, 2026-10-11. A report, never a ruling.

> product-spec-reviewer report on SPEC/09 at d848ea9 (branch m09-pr1). Files read: C:\Users\andar\code\agentkeel\SPEC\09-per-agent-rules.md; C:\Users\andar\code\agentkeel\SPEC\00-overview.md §3, §4, §5, §6, §7 row 9, §8 preamble and M09, §10.3 row 09, §10.5, §15; C:\Users\andar\code\agentkeel\milestones\README.md; milestones/M08/open.md row 37; and the code lines SPEC/09 cites (src/validate/agent.py, agent_goldens.py, src/verdict/build.py, gate.py, governed_agent.py, deploy.yml, scripts/registry.py, agents/refagent/rules/guardrail.yaml, .github/CODEOWNERS). The five false states in §3 are live at 0ba6d1d as cited: `KINDS = ("ordinary", "trap")` (agent_goldens.py:35), `guardrail_errors` holds the pin to refagent's (agent.py:109), no `rules/` at the root, `READ_THE_DRILL = {"M08"}` is the last reader (gate.py:210). Every seed in §5 can be planted in PR 1 without a reader. No P5 breach: the observer writes raw, `build` rules, the gate reads, the ledger reads the gate.
>
> 1. FINDING — §2 "Platform baseline" / §1: "Proposed day-one content, for the Rule Owner to rule (§11 R1): the two PII entities, `PHONE` and `EMAIL`, both `ANONYMIZE`". Those two rules have never fired on a seeded case: refagent's only MASKED golden (`g-014`) reads `never_passed 1` in every cell from row 3 to row 8, and the membership reader (`build.py:311`) reads topic names only, so a PII anonymization cannot be read as "its named rule among `guardrail_topics`"; the claim's "on top of a platform baseline" therefore has no firing reading on the fixture agent, only a digest in a description (F9.1) and a read-back (F9.2) that cut 3 removes. Settled when Product and the Rule Owner rule whether the day-one baseline must hold a rule of a kind the reader can see fire, or §8 lists "a baseline rule firing on a template agent" as unseeded and PR 2's template README says so.
>
> 2. FINDING — §5.1: "opens its first pull request carrying S1's folder; the platform check reads its rules and admits its pin and its plant; it merges; the platform builds its guardrail and deploys it". S1's manifest pins `fest1va1desk:1`, which no guardrail answers to; the construct conditions the agent role's invoke on the manifest's pin ARN (`governed_agent.py:257`, `:409`) and passes that pin to the server (`:462`), so the first deploy either fails or guards the agent with an unresolvable ARN, and under R3's proposal the real id is known only after that deploy (§8 bullet 2, cut 2) — the sequence names no step where the manifest gets it. Settled when Security (R3) and Product state at which step the fixture's manifest carries the built guardrail's id and what the first deploy does with the placeholder; the feasibility note records it.
>
> 3. FINDING — §4 F9.2: "live, the platform check's result on the agent repository's head, and the read-back of the built guardrail against the baseline". §5.1's sequence opens one pull request in the fixture repository, a clean one, so the live reading of F9.2 is of a head that weakens nothing and witnesses no refusal; F9.2 is a test-only witness, and the row does not say so. Settled when Product either names a second pull request in `festival-desk` carrying S2's `weakened.yaml`, refused and read by the observer (M02's seed-PR pattern), or states F9.2 as test-only in the ledger row.
>
> 4. FINDING — §4 F9.4: "or admits a guardrail or red-team golden with no `blocks` entry, or one naming a rule the merged guardrail does not build | `checks.F9_4: fail` from S1's fixture test". S1 is the admitted case whose `blocks` entry agrees with its golden; no seed plants an unnamed plant or a plant naming a rule the merge does not build, so that refusal (§2 "The platform check refuses a plant with no named rule") is a control with no seeded case, and §8 does not list it. Settled when Product rules whether PR 1 adds the two refused files (under S1 or as S5) or §8 names the refusal as unseeded.
>
> 5. FINDING — §7 PR 1: "`tests/test_m09_seeds.py` shows 2 passed (S1's format guard, S4's guard) and 5 xfailed". §5 names S1 "Two planted tests", S2 two readings (refuse `weakened.yaml`, merge `empty_pii.yaml`), S3 three records, and the run file: at least 6 xfails, not 5. Settled when Product writes the exact count in the ledger row before the tests are written; the count is what `make plants` is compared with.
>
> 6. FINDING — SPEC/00 §8 M09 PRs (1) vs SPEC/09 §5 S1: SPEC/00 says "the fixture agent with `rules/guardrail.yaml`, one golden and one `blocks` entry"; SPEC/09 says "`goldens/g-030.yaml` ... `g-001` and `g-010` as the template's minimum". SPEC/00 wins, but a fixture with one golden is refused by `evaluate()` on M06's minimum (one ordinary, one trap), so S1 would fail for a reason other than its reader. Settled when Product amends SPEC/00 §8 M09's PR (1) line to "one guardrail golden" at this PR.
>
> 7. FINDING — SPEC/00 §15 vs §10.5: §15 reads "`docs/milestones/` holds nine explainers and nine videos (ten of each from M09 PR 1)"; §10.5 reads "M09's own video follows amendment 1 and rides M10's PR 1 if there is one". If M10 exists, M09's close commits nine videos and §15's video clause is unmet, and it is not among the three clauses §15 lets M09's close read as unmet. Settled when Product rules whether M09's close rules its own video as M08 did, or adds the video clause to §15's re-read list.
>
> 8. FINDING — §6 the observer row: "`scripts/observe_rules.py` ... Engineering (the script); Security (the workflow step and any read-back grant, §11 R4)". A new script needs its own CODEOWNERS line (ADR-0012; ledger M07 PR 3: "a script no line names now fails it"), which is Security's path and is not in the table, so PR 2 edits `.github/CODEOWNERS` with no row naming it. Settled when Security's line for the script is added to the §6 table.
>
> 9. NOTE — §4 F9.1: "a guardrail whose version description does not carry the digest of the baseline and the agent's files as the tree holds them". Nothing says who computes the tree digest; if the observer takes it from the same `guardrail_spec` that wrote the description, the comparison is a tautology. Settled when Engineering states in feasibility that the observer digests the agent repository's merge commit and `rules/baseline.yaml` on the platform's `main` itself, independently of the builder.
>
> 10. NOTE — §9 cut 3: "F9.1 reads the version's description digest as the deploy records it in the registry row". `scripts/registry.py` records no guardrail description today, so cut 3's fallback adds a `deploy.yml` and registry change (Security, Engineering) rather than removing work. Settled when Engineering says in feasibility whether the registry row carries the description before cut 3 is taken.
>
> 11. NOTE — §6: "`src/validate/agent.py` ... Engineering (the readings); Rule Owner (that a pin may be the agent's own)". One path under `src/**` with two seats in a table that says "One seat and one path each"; the Rule Owner's part is the re-ruling of M08 open.md row 37, which no §11 item carries. Settled when Product names it as an R10 for the Rule Owner or cites SPEC/00 §8 M09 item 3 as that ruling.
>
> 12. NOTE — cut list and cap: §6 lists nine build rows plus the schema, the P5 cases and the CODEOWNERS line, against a cut list of five. The never-cut item most likely to threaten the cap is the guardrail builder (R3: a construct change, the deploy role's deny at `app.py:134-136` narrowed, cdk-nag reports regenerated), since M07's deploy-path repair cost its fifth PR; §5.1's second exception covers a deploy failure, not a build-role refusal found on PR 2's own run. Settled by Security ruling R3 before PR 2 opens, as §11 says; recorded here so it is not found at PR 2.
>
> 13. NOTE — SPEC/00 §8 M09 F9.3: "blocked by a rule other than the one its `blocks` names" reads as exclusive; SPEC/09 §2 "Fired" reads membership ("another rule matching beside it is not a miss"). SPEC/00 §8 M09 item 4 cites `build`'s reading since M03 PR 3, which is membership, so the Falsifier sentence is the loose one. Settled when Product rewords the SPEC/00 line to "blocked with its named rule absent from the trace" at this PR.
>
> 14. NOTE — §10.3 row 09: "a team can add rules but cannot take the platform's away". A director reads "the platform's" as rules that stop something; at day one they are two PII entities whose only golden has never passed (item 1). No word needs the schema or a falsifier number; no "governed", "secure" or "proven" appears in SPEC/09 or the row. Flagged for the record only.
>
> 15. NOTE — SPEC/00 §6 "Bundle: manifest + prompt + tools + rules" and `src/bundle/pack.py:15` list rules in the signed bundle; §6's table has no row for `src/bundle/` or for `infra/construct/agent.Dockerfile`'s COPY list (which §3.1 cites as excluding `rules/`). Whether an agent repository's `rules/` enters the bundle digest, the image, or neither is not stated, and F9.1's "digest of the agent's files" would then be a second digest of the same files. Settled when Engineering states in feasibility where `rules/` goes and which digest F9.1 reads.
>
> BLOCK: 0 · FINDING: 8 · NOTE: 7

## 2. Rulings on the report

No BLOCK, so the PR may open. Every finding and note was taken on the
session's recommendation and is recorded here with its seat and what
would undo it; each is also a proposal until the seat's ruling file for
this PR reads "Ruled by". SPEC/09 was revised once on them and SPEC/00
three lines more (`2320218`).

| # | Disposition | Seat | Undone by |
|---|---|---|---|
| 1 | **Named as unseeded**, not planted. SPEC/09 §8's first bullet: the proposed baseline's two PII rules have no firing reading in this project (`g-014` never passed; the membership reader reads topic names), so M09 reads the baseline's presence (F9.1's digest and read-back) and the agent's own rule's firing. Whether day one's baseline must hold a rule the reader can see fire stays §11 R1's; the template README says this at PR 2; the explainer's first section says it now. | Rule Owner; Product | a baseline rule planted on the fixture agent at PR 2, which would be welcome and is not owed |
| 2 | **The placeholder pin, stated.** SPEC/09 §2 "The placeholder pin": proposed for Security and Product under R3, the construct builds the guardrail in the agent's own stack and conditions the invoke and the converse on the stack's own resource, reading the pin only to refuse null and refagent's; the deploy writes id, version and digest to the registry row; the manifest gets the id in the third pull request (§5.1); F9.1 reads the pin the answer record names, which is the stack's. The first deploy neither fails nor guards with an unresolvable ARN. | Security; Product | Security ruling the bootstrap alternative at R3, in which case the guardrail is built by hand before the first merge and the manifest pins it in the first pull request |
| 3 | **F9.2 given a live arm.** A second pull request in `festival-desk` carrying S2's `weakened.yaml`, which the platform check must refuse and the observer reads (M02's seed-PR pattern); the run file names it as its `second` step; SPEC/09 §4, §5, §5.1. | Product | nothing: the pull request is outside agentkeel's cap |
| 4 | **S5 added**: `tests/fixtures/m09/s5-unnamed-plant/` with `no_blocks.yaml` and `unbuilt_rule.yaml`, read by `rules_errors`; SPEC/09 §4 F9.4, §5. | Product (a seed); Engineering (its test) | nothing |
| 5 | **The count written before the tests**: 2 passed, 7 xfailed (SPEC/09 §7, the ledger row). The tests were then written and show that count. | Product | nothing |
| 6 | **SPEC/00 §8 M09 PR (1) amended** to "one guardrail golden beside the template's minimum of one ordinary and one trap". | Product | nothing |
| 7 | **M09's video at its own close**, as M08's (ADR-0005 amendment 2): SPEC/00 §10.5 as amended; §15's ten videos are met at M09's close. M10 is proposed, not planned. | Product | M10 opening before M09 closes, in which case amendment 1 applies and §15 is re-read then |
| 8 | **No CODEOWNERS edit is owed**: `.github/CODEOWNERS` already takes `scripts/observe_*.py` as Engineering's with no change (its own comment; security-reviewer 18 on M07 PR 3). SPEC/09 §6's observer row says so. The reviewer's reading of ADR-0012 was of a script outside that pattern. | Security (the file); Engineering | a script not named `observe_*.py` |
| 9 | **The observer digests independently**: SPEC/09 §4 F9.1 and the run file's `reads`: the agent repository's merge commit and `rules/baseline.yaml` on agentkeel's `main`, computed by the observer, never taken from the builder. | Engineering | nothing |
| 10 | **The registry row carries the guardrail's id, version and description digest** from PR 2, for an agent with its own rules (SPEC/09 §6, a new row): PR 2's work either way, so cut 3 removes the read-back only. | Engineering; Security (the deploy step) | nothing |
| 11 | **R10 added** (SPEC/09 §11): the Rule Owner's re-ruling of row 37, cited as SPEC/00 §8 M09 item 3, carried by the Rule Owner's ruling file at PR 2. | Rule Owner | nothing |
| 12 | **Recorded**: the guardrail builder is the item most likely to threaten the cap; R3 is ruled before PR 2 opens (`README.md`, "Read before PR 2"). A build-role refusal found on PR 2's own run is a repair inside PR 2, not a fifth PR. | Security; Product | nothing |
| 13 | **SPEC/00 §8 M09 F9.3 reworded** to "blocked with its named rule absent from the trace". | Product | nothing |
| 14 | Recorded. The explainer's first section says what "the platform's" rules are on day one and that their firing is not read. | Product | nothing |
| 15 | **Where `rules/` goes, stated** (SPEC/09 §2, a new bullet): into the signed bundle (`pack.py` packs the tree, no change), not into the image (the Dockerfile's list unchanged); F9.1's digest is the guardrail version description's, as `guardrail_spec` computes it, not the bundle's. | Engineering | nothing |

## 2.5 The `rule-owner` report (0 BLOCK, 7 FINDING, 5 NOTE)

Run on the committed diff at `106df54`, on the fixture's rules file and
SPEC/09's proposals. No relaxation: the diff touches no `rules/` path and
refagent's pin is unchanged. The report is in the PR body verbatim. Each
finding taken on the session's recommendation:

| # | Disposition | Seat |
|---|---|---|
| 1 | ADR-0009 entry 4 on the first pin change (refagent's id to the agent's own): **R10 says in words** whether it is a relaxation; a later id change inside an agent repository is unread at M09 (SPEC/09 §8, new bullet; §11 R10). Unsure L | Rule Owner; Threshold Owner |
| 2 | The placeholder's life: **stated as a proposal** in SPEC/09 §2 (admitted only while the registry row holds no guardrail for the agent; refused once it does), with the null-pin alternative for Security. Unsure C and K | Rule Owner (R10); Security (R3) |
| 3 | "an example" **struck** from the add list; a baseline topic's name in an agent file is refused, examples included (SPEC/09 §2) | Product (the line); Rule Owner (R1) |
| 4 | A `content_filters` key in an agent file is **refused** by the merge; the filters are the baseline's alone (SPEC/09 §2) | Rule Owner (R1) |
| 5 | The baseline carries `topics_apply_to: input`; the merge **takes the stricter** of the two values (SPEC/09 §2) | Rule Owner (R1) |
| 6 | A template agent's guardrail carries the baseline and its own rules only; refagent's six topics are refagent's; a topic for the template's shipped clause text is the agent's Rule Owner's to add: **R10 says so** (SPEC/09 §8, §11) | Rule Owner (R10) |
| 7 | The baseline's PII rule has no firing reading: **R11 added** for the Data Owner (a MASKED plant counted, or the firing unread through M09). Unsure M | Data Owner |
| N5 | `record_held.json` pins the placeholder; PR 2's test for `guardrail(record, read_back, tree_digest)` must not use it as F9.1's held case. Recorded for PR 2 | Engineering |

The report's drafts for R1, R2 and R10 and its list of what the merge
must refuse are carried into PR 2's Rule Owner ruling file as its
starting text; they are a report, never a ruling.

## 2.6 The `engineering-cold-reviewer` report (0 BLOCK, 3 FINDING, 7 NOTE)

Run on `origin/main...106df54` without the PR body. Shape, plant, P5 and
owned paths held; each seed fails for its planted reason and no other.
The report is in the PR body verbatim. The three findings are Product
prose and were applied in the last commit of this PR:

| # | Disposition | Seat |
|---|---|---|
| 1 | The explainer and SPEC/09 §2 now say the fixture is the template's agent (refagent's subject and data) with one festival rule added, not an agent on another subject | Product |
| 2 | The explainer's two present-tense sentences about a builder that does not exist ("checks the only way that counts", "cannot drift") reworded as what M09 is meant to build and what PR 3 reads | Product |
| 3 | F9.4 and F9.5 one wording: SPEC/00 §8 M09's falsifier line carries the unbuilt-rule arm and "read under 7 of 7"; `milestones/M09/README.md`'s Falsifiers cell is the ledger row's, verbatim | Product |
| N2 | `README.md`'s "What a reader can run" diff command lists `src/verdict/plants.py` on its own line | Product |
| N3 | `F9_5` is a guard's witness and cannot go RED at PR 2; the row's RED at PR 2 rests on `agent_rules` unread, as the row says. PR 2's review reads it as a guard | Engineering, PR 2 |
| N7 | The fixture's working-tree line endings are mixed (LF in the index); any digest the observer computes reads `git show`, never the working tree | Engineering, PR 2 |

## 3. The false state

SPEC/09 §3 names five things on `main` at `0ba6d1d` that make claim 9
false and one that holds today. Planted as five seeds and one run file in
one commit, `02db54e`, before any reader (`git show 02db54e --stat` shows
the fixture, the rule files, the records, the run file, the tests, the
`SEEDS_M09` lines and the README rows, and **no reader**:
`src/validate/agent_rules.py`, `src/verdict/agent_rules.py`,
`scripts/observe_rules.py` and `rules/baseline.yaml` are in no commit of
this PR). Each planted test was run once with `--runxfail` and its message
read:

| Seed | `--runxfail` message (the planted reason), or why it passes |
|---|---|
| S1 format | **passes** (a guard): the fixture is in refagent's format, within Bedrock's limits, its golden and `blocks` entry agree, its pin is its own, its goldens are guardrail, ordinary and trap |
| S1 admitted | `seed S1: the platform check refuses an agent's own pin and its guardrail golden: {"the platform's guardrail": ["manifest.yaml: guardrail {'id': 'fest1va1desk', 'version': '1'} is not the platform's {'id': '1088aw3ujhyd', 'version': '5'} (SPEC/06 section 6, item 6: one guardrail for every agent at M06)"], "an agent's goldens: one ordinary and one trap at least, citing its own data": ["agents/festival-desk/goldens/g-030.yaml: kind 'guardrail'; an agent's goldens are ordinary or trap"]}` |
| S1 rules read | `seed S1: nothing reads an agent repository's rules/guardrail.yaml` |
| S2 weakened | `seed S2: no platform baseline exists and nothing merges an agent's rules onto one` |
| S2 empty list | the same message |
| S3 | `seed S3: nothing reads an agent's plant from an answer record` |
| S4 | **passes** (a guard): refagent's six topics, two PII entities and seven plants as they stand |
| S5 | `seed S5: nothing reads a plant's named rule in an agent repository` |
| run | `seed run: the run has not been made` |

`tests/test_m09_seeds.py` shows **2 passed, 7 xfailed**; `--runxfail`
shows 2 passed, 7 failed, each with the message above. `make plants`
lists S1 to S5 and the run, the readers "not in the tree yet" beside S1,
S2, S3, S5 and the run, and `gate.py` "in the tree" beside S4. `make
validate`'s twenty checks pass: no check reads a fixture, a run file or a
`rules/` folder at the root.

**The platform check's two refusals of S1 are the plant made visible by
an existing reader.** They are not a seed passing by its reader: the
reader refuses, and PR 2 must change it to admit. S1's admitted test is
xfail on that refusal and comes off when `guardrail_errors` and
`agent_goldens.KINDS` change (SPEC/09 §6).

## 4. The code that reads the answer

SPEC/09 §6, one seat and one path each, all in PR 2. The seed tests fix
these names, so PR 2 does not choose them: `rules/baseline.yaml` (Rule
Owner); `src/validate/agent_rules.py` with `load`, `merge`,
`merge_errors`, `rules_errors(agent_dir, rules=None)`;
`src/verdict/agent_rules.py` with `plants(record, blocks)` returning
`{read, held, expected, fired, reasons}` and `guardrail(record,
read_back, tree_digest)`; `scripts/observe_rules.py`; `agent_rules` on
the envelope; `CLAIM_9_CHECKS` and `READ_THE_RULES` in `gate.py`; row 9's
reading in `src/ledger.py`; `SEEDS_M09` in `plants.py` (this PR); the
three changed readings in `src/validate/agent.py` and `agent_goldens.py`;
the registry row's guardrail fields; the guardrail builder as Security
rules. None is in PR 1.

## 5. Falsifiers

SPEC/09 §4. Test-only witnesses on every envelope from PR 2's merge:
`F9_1` (S1), `F9_2` (S2), `F9_3` (S3), `F9_4` (S1, S5), `F9_5` (S4).
Recorded in `agent_rules` and read by row 9's cell: the live reading of
the fixture agent's answer record, the read-back, and the platform
check's results on three heads, at PR 3's run (PR 4's if the deploy path
needs a repair).

## 6. What M08 carried in

M08 was the last milestone and left no `open.md` for M09: its close gave
every finding and Unsure item a standing home in
`milestones/M08/README.md`'s close detail, and those homes stand. M09's
inbox is one row of M08's own `open.md`, row 37 ("One guardrail for every
agent"; Rule Owner; "at M08 open: a named gap to re-rule, not work"),
which M08's open left as a named gap and this milestone takes as its
claim. Nothing else moves. Checked against M08's close detail:

| Item | Now |
|---|---|
| M08 finding 1 (a4/a6 unnamed in run 1's view), 3 (unnamed refusals), 4 (the overlay crash, tooling), 5 (the video over the ceiling) | Standing where M08's close put them; M09 touches none (ADR-0014: M09 repairs nothing M08 found) |
| M08 finding 2 (the drill-agent fixture's row defect) | Standing. M09's fixture is made by `make_template.py` with the full table, so the defect is not repeated here (SPEC/09 §11 R9); M08's fixture is not edited |
| M08's three ruled Unsure items (panel 1 for run 3, the orphan KMS keys, run 1's record set) | Ruled at M08's close; the keys are read as gone after 2026-10-09 by hand, a standing note, not M09's |
| M08 `open.md` row 37 | **Taken as claim 9** (SPEC/00 §8 M09; ADR-0014) |
| M08's video | Committed at M08's own close (ADR-0005 amendment 2); nothing to carry |

## 7. What PR 1 does not do

No reader, no baseline, no merge, no guardrail, no workflow, no stack, no
deploy, no grant, no setting in GitHub or AWS, no change to a bar, a rule
under `agents/refagent/rules/`, a golden under `evals/goldens/` or
`src/baseline/`. It changes `src/verdict/plants.py` by the `SEEDS_M09`
list only, which reads nothing and gates nothing, and
`tests/test_cost_cap_and_ledger.py` by the row count (nine to ten). The
template README still says a `rules/` folder is not read: that sentence
is the false state and is corrected at PR 2, after the reader exists.
`make validate`'s twenty checks pass.

## 8. The reviews of PR 1

**`product-spec-reviewer`**, on SPEC/09 at `d848ea9`: 0 BLOCK, 8
FINDING, 7 NOTE (§1). Dispositions in §2.

**`rule-owner`**, on the fixture's rules file and SPEC/09's proposals at
`106df54`: 0 BLOCK, 7 FINDING, 5 NOTE. No relaxation. Dispositions in
§2.5.

**`engineering-cold-reviewer`**, on `origin/main...106df54`: 0 BLOCK, 3
FINDING, 7 NOTE. Dispositions in §2.6.

Both reports are in the PR body verbatim. No `security-reviewer`,
`data-owner` or `threshold-owner` report: PR 1 touches no `infra/`, no
workflow, no `evals/goldens/`, no `data/` and no bar. The `cold-review`
skill runs from PR 2 (R9).
