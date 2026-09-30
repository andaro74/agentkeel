# M06 feasibility note

Claim 6: a developer ships a governed agent from the template in under
one day (SPEC/06 §1). The false state, the falsifiers and the seeds are
SPEC/06 §3 to §5. This note carries the `product-spec-reviewer` report
(§1), the seats' rulings on it (§2), and, after those, the rest of
`/open-milestone`'s record.

SPEC/06 was drafted first in PR 1 (`69721b6`), before anything else, and
reviewed as committed there. Nothing else in PR 1 is written until §2 is
ruled; no seed is planted before then.

## 1. `product-spec-reviewer` report (verbatim)

product-spec-reviewer report on SPEC/06 (DRAFT, 69721b6), M06, before PR 1. Written 2026-09-30. A report, not a ruling.

Files read: SPEC/06-developer-template.md; SPEC/00-overview.md §4, §5, §6, §7, §8 M05 to M07, §10.1 to §10.5, §11, §12, §13; milestones/README.md (validate header, rows 5 and 6); milestones/M06/open.md; infra/ruleset/main.json; infra/bootstrap/app.py (grep); src/bundle/verify.py (grep); agents/refagent/manifest.yaml; agents/ratings-helper/manifest.yaml; milestones/M05/feasibility.md §1 (form only).

Facts the SPEC cites, checked: `main.json` requires the five contexts, none with an `integration_id`, `bypass_actors: []` (holds). `SUBJECT = "repo:andaro74@3157440/agentkeel@1376369685"` at app.py:85, deploy trust on `{SUBJECT}:ref:refs/heads/main` with the workflow exact (holds). `DEPLOY_IDENTITY` is the one identity in verify.py:48, and a `REPOSITORY_ID` check (holds). Both manifests have all seven seats `null` (holds). Not read: `gh api user/orgs`, `is_template`.

The four human rulings of 2026-09-30 are stated as ruled, with one gap. "Timed once the template works" is not carried (item 9).

**BLOCK 1. The required workflow cannot live where Q1 leaves it** (checks 2, 8; §11 Q1, SPEC/00 §12)
- §11 Q1: "`agentkeel` itself stays where it is: moving it would change the deploy role's `sub` and the signing identity (§3.5)."
- SPEC/00 §12: "required workflows assume the same GitHub org".
- Q1 puts the agent repositories in a new organization and keeps the platform's workflows in a user-owned repository outside it. An organization ruleset's `workflows` rule picks its workflow from a repository in that organization. So F6.2's named reader cannot point at `agentkeel`'s workflow as written.
- Q1 also leaves two things unread: whether the rule exists on the Free plan at all, and what M06 does if it does not. "That is the finding" leaves S2's seed and §7's PR 3 line with nothing to state.
- To settle: before PR 1, Security reads where a `workflows` rule can source its file and on which plan. Product then rules one of three things: move `agentkeel` (re-key claim 1), keep a copy in the organization (name its seat and its hash check), or accept F6.2 as having no reader, with the row's expected output written that way.

**BLOCK 2. S2's expected refusal has no reason** (checks 1, 3, 4; §4 F6.2, §7)
- §4 F6.2: "a pull request … that removes the caller's `uses:` line, or replaces the job with one of the same name … and is mergeable".
- §7: "S2 refused by the required workflow, the pull request not mergeable".
- A required workflow runs whatever the caller file says. Removing `uses:` removes nothing it enforces. If the platform's checks pass on S2's content (it changes only the caller), the pull request is mergeable, and by §4's own wording F6.2 fires on a working control.
- No §6 item refuses an edit to the caller file, for example a hash of the agent repository's `.github/workflows/` held by the required workflow.
- To settle: Security and Product rule what refuses S2 and for which planted reason, or restate F6.2 as "merged without the platform's workflow having run and passed".

**BLOCK 3. S4's instrument decides its own verdict** (check 2, P5; §4, §5 S4)
- §5 S4, "Read by": "`scripts/observe_template.py`'s panel reading: panel 1's rows equal to a registry scan, by agent name".
- §4 P5: "Observers write raw observations; `verdict.build` writes the checks and `template`".
- The observer reads both sources and rules them equal. `F6_4` is then that comparison's result, taken from the seed test.
- To settle: Engineering names `build` (or the ledger) as the comparer, with the observer writing the two raw lists. Product rules it in §4.

**FINDING 4. The developer who "creates" the repository cannot be write-only** (checks 1, 7; §1 item 1, §2)
- §2: "The developer has **write** on it and nothing more: no admin". §1 item 1: "The repository was created from the template". §10.1 quickstart: "create from template → …".
- On GitHub the creator of an organization repository is its admin. If the second account creates it, the write-only ruling does not hold. If the owner creates it, the start record `created_at` is the owner's act, not the developer's.
- An admin can also delete and recreate a botched repository. That resets `created_at`, which is the start of F6.3, and the observer would read the shorter attempt.
- To settle: Security rules who creates the repository and the organization's member repo-creation setting. Product rules that a deleted attempt is recorded, not replaced.

**FINDING 5. Onboarding a second agent needs platform changes that §6 does not list** (checks 2, 6; §6, §1 items 3 and 4)
- §6 lists "The deploy role's trust and the signing identity". §1 item 4: "The deployed agent answered one of its own goldens in the runtime."
- Not listed:
  - The eval role's trust, which is `[f"{SUBJECT}:pull_request", f"{SUBJECT}:ref:refs/heads/main"]` (app.py:778), `agentkeel` only.
  - Where verify's accepted "caller repository by id" list lives, and who adds a new id.
  - The construct's per-agent resources for an agent that is not refagent, including its own rights table (M05: no shared surfaces).
  - The audit bucket policy, which "names refagent only" (`open.md` row 29, dated M07).
- If any of these needs a platform PR per new agent, that PR falls inside the timed run and is made by a seat holder, not the developer. The plain sentence's "without touching the safety pipeline" then fails.
- To settle: Security lists every per-agent platform change in §6 and states whether each is automatic or a PR, before PR 2.

**FINDING 6. F6.1's live half has no reader, and its wording fires on a correct refusal** (check 3; §4, §5 S3)
- §4 F6.1 live: "the timed run's first pull request … with any required check green while a seat is null or the goldens are empty".
- "Any required check green" is true of a correctly refused PR (for example `ruling-cited` green, `validate` red).
- "Where each reading comes from" names live readings for F6.2, F6.3 and F6.4 only. S3's "Read by" lists `created_at`, the deploy run, the answer, the registry row and panel 1, not the first pull request's refusal. §1 item 2 says that refusal is read.
- To settle: Product rewrites F6.1 as "mergeable while …", and Engineering names the observer field that reads the first PR's checks.

**FINDING 7. "Its own goldens" have no envelope, and the citation check cannot pass outside this repository** (check 3; §1 item 4, §2 Goldens, §5 S1)
- §5 S1: "The same checks run in an agent repository through the required workflow". §2: goldens "in SPEC/00 §6's shape".
- §6's shape requires `table_row` and `clause_id`. `validate` checks them against `data/rights_table.json` and `data/clause_index.json` (ledger, M00 PR 1), which an agent repository does not have. Also unsaid: which of the sixteen checks run there (CODEOWNERS completeness, ruling front matter, workflow hash).
- Item 4's answer has no named envelope. Only `build` writes envelopes, `evals/history/` is `agentkeel`'s, and P11 makes only CI-written ones evidence.
- To settle: Engineering names the checks that run in an agent repository and where item 4's record is written. The Data Owner rules the golden shape for an agent that is not refagent (Q4).

**FINDING 8. F6.3's end record leaves two of the five items outside the clock** (check 3; §1 "Under one day")
- §1: "the new repository's `created_at`, and the completion of the deploy run that satisfies item 3".
- Items 4 (answer) and 5 (registry and panel) come after that deploy, so a run can be "under one day" by the bar and still not "ships" within it.
- Work done before `created_at` (manifest, goldens drafted from the quickstart) is not counted.
- To settle: the Threshold Owner rules the end record as the last of the five items' records, and Product states in §1 that preparation before creation is not timed, or forbids it.

**FINDING 9. "Timed once the template works" is not carried** (check 3; §5.1)
- The ruling: "timed once the template works". §5.1: "S3 is made once … the first is the measured value."
- The SPEC does not say what shows the template works before S3. A rehearsal of the quickstart by the author would be an uncounted first attempt.
- To settle: Product states the reading that shows "the template works" and that it is not a run of the quickstart, or records any rehearsal as an attempt.

**FINDING 10. S1 plants two reasons in one fixture** (checks 3, 4; §5 S1)
- §5 S1: "`manifest.yaml` with all seven seats `null` and an empty `goldens/`". §5: "`xfail(strict=True, raises=...)` naming the one exception its planted reason raises".
- With both reasons in one fixture, a reader that catches only one still refuses S1, and the seed test passes with the other reader missing.
- To settle: Engineering either splits S1 into two fixtures or makes the test require both refusals by message. Product rules which.

**FINDING 11. S4 seeds the comparison, not the panel's source** (check 3; §5 S4)
- §5 S4, "Read by": "the dashboard's panel 1 query names the registry as its only source".
- The fixture is two JSON files. No seed plants a dashboard whose panel 1 query names a second source. That control has no seeded case, and §8 does not list it.
- To settle: Engineering adds a dashboard-JSON seed, or Product lists the query check in §8.

**FINDING 12. ratings-helper's null seats turn PR 2's `validate` red** (check 4; §7 PR 2)
- §7: "refagent's own seats assigned in the same PR, since S1's reader reads every manifest".
- `agents/ratings-helper/manifest.yaml` has seven `null` seats too. S1's reader refuses it, and PR 2 cannot merge.
- To settle: Security assigns ratings-helper's seats in PR 2 as well, and §7 says so.

**FINDING 13. The plain sentence still says what §1 says it must not** (check 5; §1, SPEC/00 §10.3 row 06)
- §1: "The table's word 'Marketing' is dropped here: the developer who is timed is the author (§2), not a marketing team, and the sentence must not say otherwise."
- The replacement: "*a team creates a governed agent from the template*". "A team" says otherwise too; the timed person is the author alone. The title "A team can do this in a day" repeats it.
- "Governed" is used about controls none of which has fired: the required workflow, seat checks, registry and panel all land at PR 2 or later.
- §10.3 is SPEC/00. The SPEC does not say it is amended in this PR, as it says for §8.
- To settle: Product amends §10.3 row 06 in PR 1 with a sentence naming one developer and without "governed".

**FINDING 14. The cap has no relief** (check 6; §6, §9)
- §9: "None cuts S1 to S4, their readers, the template, the organization ruleset, the registry, panel 1, Acts 1–2 or `docs/refagent/`."
- §6 has 11 bullets and about 22 build items once split, all in PR 2. Examples: organization plus ruleset plus export check; three reusable workflows plus hashes; deploy trust; verify; template; two `validate` checks; table plus write step; Grafana workspace plus dashboard; observer; `template` field, `CLAIM_6_CHECKS`, ledger reading, `evals.yml` step; six documents; seat assignments.
- Add FINDING 5's unlisted items, Acts 1 and 2 (no PR is named for either), and 24 `open.md` rows dated M06.
- Items I expect to threaten the cap: the deploy chain from another repository (item 3) and Grafana (FINDING 19). The two numbered cuts (panel 2, Act 3) remove neither.
- To settle: Product names which PR records Acts 1–2 and whether Act 1 is S3's own run, and adds a cut that relieves PR 2.

**FINDING 15. The cut list is out of order and cuts received scope** (checks 6, 8; §9)
- §9 row 2: Act 3 "**Proposed as taken at open**". SPEC/00 §8 M06: "Grafana panel 2 → M07; Act 3 → M07", in order. Taking cut 2 at open while cut 1 stands inverts that order.
- §9 row "a" cuts FRAGILE. SPEC/00 §8 M06 received FRAGILE as build ("Received at M04 PR 1 … the FRAGILE state"). By the same paragraph's logic as the knowledge base, moving it is an amendment, not a cut.
- Rows numbered "1, 2, a" do not say where "a" falls in the order.
- To settle: Product records FRAGILE as a §8 amendment. Act 3 is either taken in order after panel 2 or amended at open. The Data Owner rules on FRAGILE.

**FINDING 16. Seat gaps and doubles** (check 7; §6)
- "The registry (`infra/`, Security; the write step, Engineering): … the step in the reusable deploy workflow". The step lives in `.github/workflows/`, which is Security's path.
- "The deploy role's trust and the signing identity (`infra/bootstrap/`, `src/bundle/verify.py`; Security, Engineering)". The cosign identity is Security's (§5, R4), but the constant sits in an Engineering path. That is two seats on one control.
- "Engineering for the dashboard JSON": no path is named.
- "The template †": no seat until Q2 is ruled.
- To settle: Product names one path and one seat for each, amending SPEC/00 §5 for the template path.

**FINDING 17. Row 8 is cited as a false state but closed only for agent repositories** (check 8; §3 item 2, `open.md` row 8)
- §3 item 2: "both are files the same pull request can carry (`open.md` row 8: the reader is the PR's own code)".
- Row 8: "Take the reader from `main`, with the required workflows the template ships" (Security, Engineering, M06).
- §6 builds the organization rule for agent repositories only. `agentkeel` keeps its repository ruleset, so a same-named `evals` job still answers there, and §8 does not list it.
- To settle: Security rules whether row 8 closes for `agentkeel` at M06 or carries, and §8 or `feasibility.md` §6 says which.

**FINDING 18. Claim 1's controls are widened with no seeded refusal** (checks 3, 8; §6, §8)
- §6: "`sub` scoped to the organization's repositories; `verify` accepting the reusable workflow as the build signer and the caller repository by id".
- This moves the deploy trust from one exact `sub` to an organization pattern (`StringLike`; app.py:23–24 records the lesson against patterns) and gives verify a second identity.
- No M06 seed attempts a deploy from a repository outside the organization or a caller not on the list. §8 does not name the widening.
- To settle: Security adds a seeded refusal for each widening, or lists both in §8 as controls with no seeded case.

**FINDING 19. Panel 1 is never-cut, but its platform is unruled** (checks 2, 6; §11 Q6)
- Q6: "Amazon Managed Grafana needs IAM Identity Center or SAML; the agent account is the organization's management account (`open.md` row 48)."
- Unread:
  - Whether Identity Center in the management account conflicts with row 48's deferral.
  - Whether the workspace has a DynamoDB data source without a custom plugin (SPEC/00 §13: Grafana's job excludes "anything custom").
  - The per-editor cost against §14's $250.
- If any answer is no, F6.4's live half has no reader and panel 1 cannot be cut.
- To settle: Security answers Q6 before PR 2, and Product says what the row reads if the answer is no.

**NOTE 20. SPEC/00 promises a seat check that was never built** (check 8; SPEC/00 §5 R1)
- R1: "From M01 PR 1, when their inputs exist: manifest schema, seats assigned to real groups". The ledger header never lists a seat check, and §3 item 3 says "No check reads a seat's value."
- S1's false state exists because of that gap. SPEC/00 §6 still says "seats → IdP groups", which Q3 replaces without an amendment.
- For the record. Product amends R1's list and §6 with Q3.

**NOTE 21. The knowledge-base amendment's text and the rows that ride it** (check 8; §10, SPEC/00 §8 M06)
- SPEC/00 §8 M06 reads "The knowledge base has moved twice (M01, M03 open, M04 open)". It lists three moves; SPEC/06 counts this as the fourth. The amendment is not yet in 69721b6.
- §10: "The `open.md` rows that ride it (18, 22, 23, 24)". Row 21 carries "the cached-answer seed", which §10 moves. Row 11 says "Both with row 23". Neither is listed.
- Product corrects the count in the amendment and lists rows 11 and 21.

**NOTE 22. PR 3 cannot be skipped at M06** (check 8; §5.1, CLAUDE.md)
- §5.1: "PR 3 is the repair and that read." CLAUDE.md: "If it found nothing, PR 3 is skipped and the milestone closes at PR 3 as the close PR."
- If PR 2's cold review finds nothing, S2 and S3 are still read at PR 3, so PR 3 is a read PR, not a close. §5.1 should say so. Product.

**NOTE 23. The second account and GitHub's terms** (for the record; §2)
- §2: "a second GitHub account with write access only (ruled by the human, 2026-09-30)".
- GitHub's Terms of Service, as I recall them, allow one free personal account per person, with machine accounts allowed only for automation. The ruling stands. If the account is suspended before the timed run, F6.3 goes unread. Product and Security note the risk.

BLOCK: 3 · FINDING: 16 · NOTE: 4

## 2. Rulings on the report

The three BLOCKs and NOTE 23 are ruled; the findings are pending. Each BLOCK is ruled, with its
seat, before the PR opens and before any seed.

- **BLOCK 1, Security's read (2026-09-30), ruling pending.** The human
  ruled "as proposed": option (b), a hash-pinned copy of the platform
  workflow in a repository of the organisation, falling back to (c), F6.2
  with no reader, if the free organisation plan has no `workflows` rule.
  The read: GitHub's rules page for Free, Pro and Team
  (`docs.github.com/en/repositories/.../available-rules-for-rulesets`)
  has no section on requiring workflows; the Enterprise Cloud version of
  the same page (`docs.github.com/en/enterprise-cloud@latest/...`) has
  one: "Ruleset workflows can be configured at the organization or
  enterprise level to require workflows to pass before merging pull
  requests", with the workflow in a repository whose visibility matches,
  on `pull_request`, `pull_request_target` or `merge_group` only. Read as:
  not on a free organisation. This is the documentation, not an attempt;
  the organisation's ruleset API answering for a `workflows` rule would
  settle it. Before (c) is written, a fourth option is put to the human,
  since (c) leaves F6.2 unmeasured and row 6 cannot then be GREEN.
  **Ruled by the human as Security and Product, 2026-09-30: option (d).**
  Neither (b) nor (c), and no paid plan: a personal plan does not change
  what an organisation can do, and Enterprise Cloud, the one plan the
  rule is documented on, is a monthly cost against SPEC/00 §14's target
  for as long as the control must hold (to M08). (d): each agent
  repository's default branch carries a ruleset whose required status
  check names an `integration_id`, a GitHub App the platform owns, so a
  check of that name posted by the GitHub Actions app (any job in the
  pull request's own workflow files) does not satisfy it. The check is
  posted by a workflow in `agentkeel` that runs from `main`, evaluates the
  pull request's head, and holds the App's key (Security). If the run is
  never asked for, no check arrives and the pull request stays blocked.
  Only an organisation owner edits the ruleset; the developer has write.
  **Security's read of (d), 2026-09-30:** GitHub's REST reference for
  repository rules (`docs.github.com/en/rest/repos/rules`) gives each
  required status check an `integration_id`, "The optional integration
  ID that this status check must originate from"; rulesets are available
  "in public repositories with GitHub Free and GitHub Free for
  organizations" (`about-rulesets`). The documentation, not an attempt:
  the first ruleset made in PR 2 is exported and read back by `validate`,
  as `main`'s is. What (d) adds to PR 2 (FINDING 14): the App, its key
  in `agentkeel`'s secrets, and the trigger from an agent repository's
  pull request to `agentkeel`'s workflow. It answers `open.md` row 8 for
  agent repositories (the reader runs from `agentkeel`'s `main`), not for
  `agentkeel` itself (FINDING 17).
- **BLOCK 2, ruled by the human as Security and Product, 2026-09-30, as
  proposed.** F6.2 reads: a pull request in an agent repository merged
  without the platform's workflow having run on it and passed. S2's
  planted reason is a job of the required check's name, defined in the
  pull request's own workflow file, standing in for the platform's.
  Deleting the `uses:` line alone is not the attack: it refuses nothing.
- **BLOCK 3, ruled by the human as Engineering and Product,
  2026-09-30, as proposed.** `scripts/observe_template.py` writes two raw
  lists, panel 1's rows as Grafana's API returns them and a registry
  scan, with the time each was read; `verdict.build` compares them by
  agent name and writes `checks.F6_4`. The observer rules nothing (P5).

- **NOTE 23, ruled by the human as Product and Security, 2026-09-30.** The
  risk is accepted: the second developer's account is a second free
  personal account held by the author, and GitHub may suspend it. If it is
  suspended before S3 is made, F6.3 is unread and row 6 goes RED on it; no
  other account is substituted without a new ruling. The account is
  `floresinnovations`, id 336113686, `created_at` 2026-09-30T14:09:05Z,
  created on the fresh Windows profile. Read from GitHub on 2026-09-30
  (`gh api users/floresinnovations`): 0 public repositories, 0 gists, 0
  public organisations, 0 public events. The human states, and GitHub's
  public record cannot show, that the account has two-factor on, a private
  email with command-line pushes that expose it blocked, and no token,
  SSH key or authorised app. Both go into S3's run file as preparation
  when S3 is planted.
  **Amended the same day:** the human upgraded `andaro74` to GitHub Pro
  on 2026-09-30, so the author holds one free account and one paid one,
  which the terms' limit ("One person or legal entity may maintain no
  more than one free Account", section B) does not forbid. The plan is
  the human's word: `gh api user` returns no plan field to this token.
  It must stay paid until M06 closes. The rest of the risk stands:
  GitHub may still suspend an account under its other terms, with the
  consequence above.

**Findings ruled by the human, 2026-09-30, "as proposed"** (the numbers are
the report's):

- **FINDING 4 (Security, Product).** The organisation owner (`andaro74`)
  creates each agent repository from the template; member repository
  creation is off. The second developer is given write on it and nothing
  more. F6.3's clock starts at that repository's `created_at`. A
  repository deleted during an attempt is recorded in the run file, never
  replaced by a later one's `created_at`.
- **FINDING 5 (Security).** Every per-agent platform change is automatic,
  made from `main` by the platform's own workflow when an agent
  repository first calls it, or it is a Security pull request inside the
  timed run and counts against the clock. Security lists all of them in
  SPEC/06 §6 before PR 2: the eval role's trust, `verify`'s accepted
  caller repositories, the construct's per-agent resources (with the
  agent's own table, M05: no shared surfaces) and the audit bucket's
  policy (`open.md` row 29).
- **FINDING 8 (Threshold Owner, Product).** F6.3's clock stops at the
  last of the five records of SPEC/06 §1 (merge refusal read, deploy run
  completed, the answer, the registry row, panel 1's row), not at the
  deploy. The bar is 28,800 s wall clock, breaks not subtracted
  (`quickstart.max_seconds`, `relaxes: up`, SPEC/06 §11 Q5). Nothing is
  prepared before `created_at` beyond the account set-up recorded under
  NOTE 23.
- **FINDING 9 (Product).** "The template works" is read from PR 2's own
  run: the template's example agent deployed from a test repository the
  owner creates and owns, through the same App check and deploy path.
  That run is not a quickstart run, is not timed and is made by
  `andaro74`, never by `floresinnovations`. Any run of the quickstart by
  the second developer is an attempt and is recorded.
- **FINDING 10 (Engineering, Product).** S1 is split: **S1a** a manifest
  with every seat null and valid goldens; **S1b** assigned seats and an
  empty goldens folder. Each has its own test and its own planted reason.
  Five seeds: S1a, S1b, S2, S3, S4.
- **FINDING 7 / Q4 (Data Owner; Engineering).** An agent's goldens are at
  least one ordinary and one trap, in SPEC/00 §6's shape. For an agent
  that is not refagent, `table_row` and `clause_id` name a row and a
  clause in that agent's own data, carried in its repository; the Data
  Owner rules the files at PR 2. Engineering names in SPEC/06 which of the
  sixteen `validate` checks run in an agent repository and where the
  answer's envelope (SPEC/06 §1 item 4) is written.
- **NOTE 20 / Q3 (Security; Product).** A seat is assigned to a GitHub
  login with access to the repository, checked as M02 checks CODEOWNERS
  logins. SPEC/00 R1's `validate` list ("seats assigned to real groups")
  and §6 ("seats → IdP groups") are amended in this PR to say so. Under
  R1 every seat is `andaro74`; the second developer's login holds none.
- **FINDING 19 / Q6 (Security).** Security reads, before PR 2, whether
  Amazon Managed Grafana can run in the agent account (IAM Identity
  Center in the management account, against `open.md` row 48's
  deferral), read the registry with a data source that is not a custom
  plugin, and at what cost against SPEC/00 §14. If any answer is no, F6.4's
  live half is recorded as unread and row 6 says so; panel 1 is not cut.

**The remaining items, ruled by the human, 2026-09-30, "as proposed":**

- **FINDING 6 (Product; Engineering).** F6.1 reads: the first pull request
  in an agent repository is mergeable while a seat is unassigned or its
  goldens are under the minimum. The observer records that pull request's
  required checks and `mergeable_state`; `build` rules on them.
- **FINDING 11 (Engineering).** S4 plants the panel's source as well: its
  fixture carries a dashboard JSON whose panel 1 query names a second
  source beside the registry. `validate` refuses a panel 1 query that
  names anything but the registry (PR 2).
- **FINDING 12 (Security).** PR 2 assigns the seats in both manifests,
  refagent's and ratings-helper's; SPEC/06 §7 says so.
- **FINDING 13 (Product).** SPEC/00 §10.3 row 06 is amended in this PR:
  "One developer creates an agent from the template and ships it in a
  day, without touching the safety pipeline." The title stays.
- **FINDING 14 (Product).** Act 1 is recorded during S3's timed run; Act
  2 at the close, against M02's pull requests. A third cut, after panel
  2: the three `docs/developer/` pages other than the quickstart
  (`manifest.md`, `goldens.md`, `edges.md`) to M07. `docs/refagent/` stays
  never-cut.
- **FINDING 15 (Product; Data Owner).** FRAGILE moves to M07 by a SPEC/00
  §8 amendment in this PR, not a cut. Act 3 stays second in the order and
  is taken only if the cap is threatened.
- **FINDING 16 (Product; Security; Engineering).** The registry's write
  step is Security's (`.github/workflows/`). The signing identity's
  constant moves from `src/bundle/verify.py` to a Security-owned file
  under `infra/` at PR 2. The dashboard is Security's, at
  `infra/grafana/panel1.json` (`infra/**` is Security's in SPEC/00 §5).
  The template's source lives in the template repository only; nothing
  under a path with no seat in `agentkeel`.
- **FINDING 17 (Security).** `open.md` row 8 closes for agent repositories
  through BLOCK 1's App check and carries to M07 for `agentkeel` itself,
  named in SPEC/06 §8 as a gap.
- **FINDING 18 (Security).** The organisation-wide deploy trust and
  `verify`'s second identity are listed in SPEC/06 §8 as controls with no
  seeded case at M06; no seed is added (the cap, FINDING 14).
- **NOTE 21 (Product).** The SPEC/00 §8 amendment counts the knowledge
  base's moves correctly (four) and moves `open.md` rows 11, 18, 21, 22,
  23 and 24 with it.
- **NOTE 22 (Product).** SPEC/06 §5.1: PR 3 is the read of S2, S3 and S4's
  live half and cannot be skipped, whatever PR 2's cold review finds.

Every BLOCK, FINDING and NOTE of §1 is ruled. SPEC/06 is revised once on
all of them (§2.5).
