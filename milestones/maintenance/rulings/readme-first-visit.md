---
# Maintenance PR #61. Product's key over the README, the six files under
# docs/assets/ and the maintenance README's row. Every path is Product's
# (SPEC/00 §5: README.md, docs/**, milestones/**); no other seat's path
# is touched.
ruling: readme-first-visit
seat: Product
authorises:
  - README.md
  - docs/assets/readme-header.html
  - docs/assets/readme-header.png
  - docs/assets/architecture.svg
  - docs/assets/workflow-template-to-agent.svg
  - docs/assets/workflow-planted-and-measured.svg
  - docs/assets/workflow-who-owns-what.svg
  - milestones/maintenance/README.md
  - milestones/maintenance/rulings/readme-first-visit.md
evidence:
  - CLAUDE.md
  - SPEC/00-overview.md
  - milestones/README.md
  - docs/milestones/README.md
  - milestones/maintenance/README.md
  - docs/developer/quickstart.md
  - infra/ruleset/main.json
  - infra/construct/governed_agent.py
  - infra/construct/door.py
  - infra/bootstrap/app.py
  - infra/security/app.py
  - infra/audit/app.py
  - infra/grafana/app.py
  - infra/ingest/app.py
  - .github/workflows/deploy.yml
  - https://github.com/andaro74/pharmadelta/blob/c2d45c3/README.md
  - https://github.com/andaro74/pharmadelta/blob/c2d45c3/milestones/adoption/rulings/readme.md
  - https://github.com/andaro74/pharmadelta/blob/c2d45c3/milestones/adoption/rulings/exec-overview.md
pr: 61
---

# Ruling: maintenance PR #61, Product: the README a first-time visitor reads

Drafted by Claude Fable 5.2 for Product, 2026-11-14; not yet ruled. The seat replaces this line with `Ruled by <login> as Product, <date>, as written` (or with the changes it made named) before the merge; `cold-review-ruling` fails while it reads Drafted.

A maintenance PR (`milestones/maintenance/README.md`): no ledger row, no
explainer, no claim, no plant, no measurement. It rewrites `README.md`,
which was two lines, adds six files under `docs/assets/`, adds one row to
the maintenance README and adds this file. No gate, workflow, stack,
golden, bar, rule or envelope is touched, and no call to an agent or to
AWS was made. The owner asked on 2026-11-14 for a README that says, as
soon as the repository opens, what agentkeel solves and how, as was done
for `andaro74/pharmadelta` the same day (its #43, #45, #46).

## Rulings in this PR

1. **The word "Governed" is gone from the README's first line.** CLAUDE.md
   restricts "governed", "secure" and "proven" to a control that has fired
   on its seeded case. The old line applied the first to the whole
   platform, and six of eleven rows are RED. None of the three words is in
   the README or in any image. The construct's class name is not written;
   the README says "the platform's construct". **Not done here:** the
   GitHub repository description still opens with "Governed". Changing it
   is a repository setting, the owner's. Proposed text is in the PR body.
2. **SPEC/00 §1's one sentence is kept word for word**, as a quotation,
   because §1 fixes it as the README's. It says "proves". The two lines
   under it say it is the aim and not the result, give the count, and say
   that the model-swap half is row 4 and row 4 is RED.
3. **Every state and number is a ledger cell.** The count (five GREEN,
   six RED) is the State column. Each number in the table under "What the
   platform refuses" and in two of the images is in that row's cells
   (Measured; the 600 seconds is row 5's Falsifiers cell and the cap of
   four is row 7's "PRs used / cap"), and each row links its envelope
   under `evals/history/` and the CI run that wrote it. `make ledger`
   exited 0 on this tree, a local run and not evidence; CI's `checks` job
   is the reading. The one date
   that is not a cell is the read-back of 2026-11-07, which is the
   maintenance README's, made by hand; the README says "read-back" and
   links it.
4. **RED rows are drawn RED.** The owner's brief asked for "the planted
   failures it caught, one per milestone". In rows 1, 4, 5, 6, 7 and 8
   part of what was planted was not caught or not measured. The third
   image has one card per row, eleven, with what was caught and what was
   not. The second image (template to running agent) sits on rows 6 and
   7 and says both are RED in its footer.
5. **Enforced and routed (R1).** SPEC/00 §5 says the README states which
   gates are enforced and which are routed. The README lists the five
   required checks as `infra/ruleset/main.json` names them (`checks`,
   `evals`, `ruling-cited`, `two-key`, `cold-review-ruling`), says the
   bypass list is empty, says the signature is checked in the deploy
   workflow and not on a pull request, and says everything else is routed
   by CODEOWNERS and enforced by nothing.
6. **The services.** Each AWS service named is a CDK module imported
   under `infra/` at `3962809` (`aws_bedrock`, `aws_bedrockagentcore`,
   `aws_dynamodb`, `aws_apigatewayv2`, `aws_lambda`, `aws_cognito`,
   `aws_kms`, `aws_ecr`, `aws_ec2`, `aws_logs`, `aws_cloudtrail`,
   `aws_s3`, `aws_ssm`, `aws_budgets`, `aws_athena`, `aws_iam`,
   `aws_kinesisfirehose`) or is used in `deploy.yml` (cosign, the two
   OIDC uses, the ECR login). Glue and SAM are imported by the Grafana
   stack and are left out as not main ones.
7. **No identifier.** No account id, host, ARN, pool id, API id or key id
   is in the README or in an image. Grep for a twelve-digit number,
   `execute-api`, `us-west-2`, `amazonaws` and `arn:aws` over the seven
   files: the one match is inside an envelope's commit hash. The hero
   does not carry the owner's site name, which pharmadelta's does.
8. **The images.** `docs/assets/readme-header.png` is rendered from
   `docs/assets/readme-header.html` by headless Chrome (1200 by 630 at
   scale 2), the command in the file's comment. The four diagrams are
   SVG files, each rendered and read as a picture before it was
   committed. Each box has a plain sentence and the service or file name.
   Each image has alt text that says what it shows. None is an
   illustration of something unmeasured presented as measured: the first
   and fourth show the design and say so in the text beside them; the
   second and third carry ledger cells.
9. **The tenant.** The README points at `andaro74/pharmadelta` and
   `agentkeel-studio/label-impact` and says that what pharmadelta claims
   is measured in its own ledger, not here. That label-impact was made
   from the template is its `.template-source.json`; that it runs on the
   platform is the maintenance README's read-back.

## Cold review

`engineering-cold-reviewer` read the diff `origin/main...c315c63` (nine
files) and the ledger, and nothing else. BLOCK 0, FINDING 7, NOTE 10. Its
report is in the PR body, verbatim. Engineering owns no path in this
diff, so its findings are recorded here and not in a file of its own.
Each finding was checked against the file it cites and repaired in the
commit after `c315c63`:

| # | Finding | Repair |
|---|---|---|
| F1 | "the planted key reached the answer": the run file says not refused, reached the tool result | reads "was not refused" |
| F2 | "One Grafana panel": the tree has two | reads two panels, the registry and the stored verdicts |
| F3 | "of six recordings, one was made": `docs/video/README.md` and SPEC/00 §15 disagree | the sentence is removed; Unsure F |
| F4 | "ledger written by CI": CI writes envelopes, Product writes cells | the hero and its alt text read "held to CI's runs" |
| F5 | row 5 "from inside the agent's network"; row 10 "a borrowed name" | row 5 reads "each expected to be refused"; row 10 reads "one the manifest does not name" |
| F6 | row 7's "F6_1 not held" left out beside the timed run | added to the README's list and the second image's footer |
| F7 | row 3 "No regression merged" reads as if a pull request carried one | reads "refused in a copy of the tree; no pull request carried it" |

Notes N1, N2, N3 and N5 were taken as wording changes. N6 is Unsure G.

## What a reader can falsify

- `git diff 3962809..<head> --stat` touches the nine files this ruling
  authorises and no other.
- `grep -i -w -E "governed|secure|proven" README.md docs/assets/*.svg docs/assets/*.html`
  prints nothing.
- Each number in the README's row table is in that row's Measured cell
  in `milestones/README.md`.
- Rendering `docs/assets/readme-header.html` with the command in its
  comment gives the committed PNG's picture.
- Each envelope link is a file under `evals/history/`.
- `docs/milestones/README.md` is unchanged; `make ledger-plain` was not
  needed.

## Unsure

- **A. SPEC/00 §1's sentence in a README where row 4 is RED.** Kept, with
  the result under it. If Product would rather the README not quote it,
  that is a SPEC/00 amendment, since §1 names it as the README's.
- **B. The hero carries a count** (eleven claims, five green, six red).
  pharmadelta's ruling kept every measured number out of its hero. Kept
  here because the count is the first thing a visitor should not be
  misled about. Product's.
- **C. The architecture picture draws the guardrail after the agent.**
  The brief's order was door, guardrail, agent. The guardrail is on the
  agent role's model call inside the runtime (SPEC/00 §8 M09 item 6), so
  the picture draws it there.
- **D. Row 5's count.** The claim says five attempts; the Measured cell
  reads six (S1, S2, S3, S4, S6, S7). The README and the image say six,
  with the cell.
- **E. `docs/platform/overview.md` is not touched.** It was written at
  M02 and says so. The README now overlaps it.
- **F. How many walkthrough recordings exist.** SPEC/00 §15 says one act
  is committed; `docs/video/README.md` says none recorded. The README
  says nothing about the acts. Which file is right is Product's.
- **G. The README links to files that hold identifiers** (cold review
  N6): `milestones/maintenance/README.md` (an account id, security group
  and pool ids) and envelope `dee74c3` (an IAM user ARN with a person's
  name). Both were on `main` before this PR and neither is changed by
  it. Whether they stay is Security's.

## What will go stale

- The services tables, when `infra/` changes. Nothing reads them.
- "The two agents running on the platform", at the next agent made or
  retired.
- The four diagrams, if a row is re-measured or a milestone is added.
  They are redrawn by hand; the third is written by a script that is not
  committed.
