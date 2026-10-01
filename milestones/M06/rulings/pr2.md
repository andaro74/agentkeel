---
# M06 PR 2 (#35), the measure. Product's key. One seat per file:
# Security's is pr2-security.md, the Threshold Owner's pr2-threshold-owner.md,
# Engineering's pr2-engineering.md (with the cold review). The Data Owner's
# R5 and the Rule Owner's report touch no path of theirs (feasibility.md §8).
ruling: pr2
seat: Product
authorises:
  - SPEC/06-developer-template.md
  - milestones/README.md
  - milestones/M06/**
  - docs/milestones/M06.md
  - docs/milestones/README.md
  - docs/developer/quickstart.md
  - docs/developer/template-README.md
  - docs/refagent/README.md
  - docs/refagent/walkthrough.md
evidence:
  - SPEC/00-overview.md#8-M06
  - SPEC/06-developer-template.md
  - milestones/M06/feasibility.md
  - evals/history/827ee8bc014b28f588e9b8f3e1d4a947be885f26.json
pr: 35
---

# Ruling: M06 PR 2, Product

Ruled by andaro74 as Product, 2026-10-01, as written.

## What this PR is

PR 2 of M06, the measure: 2 / 4. It lands the readers of S1a, S1b and S4,
each marker off in its reader's commit; `F6_1` and `F6_4` on every agent
envelope from `M06_READERS` (`c2a15d0`); the envelope's `template`, read by
row 6; the observer; the platform check, the agent deploy, the registry and
Grafana panel 1; the bar; both manifests' seats; the template's source
script; the documents. S2 and S3 are not made (SPEC/06 §5.1, the P3
exception): PR 3 reads them. PR 1's envelope (`827ee8b`: GREEN, runtime,
ordinary 9/9, traps 2/2, guardrail 2/3, red team 5/5, plants 7/7, 48,667
tokens) is cited here, and first in `86eb01a`.

## Rulings

1. **R1 to R9** (`feasibility.md` §8), ruled by andaro74 on 2026-09-30, "go
   ahead with your recommendations", in the seats named there. R4 rows 5
   and 8, offered without a recommendation, were taken as the automatic
   option (each agent's own key in its stack; one tag-keyed audit
   statement). SPEC/06 §2, §6, §8 and §11 are written from them.
2. **S2 carries one null seat** (from R2). Row 6's expected output, SPEC/06
   §4 and §7 and S2's run file are amended in this PR, inside the PR that
   measures (`623c75b`); the falsifier's wording is unchanged. Reason: the
   App reaches every pull request, so S2 as planted would be passed and
   would test nothing. PR 3's run reads S2's `mergeable_state` and its
   repository's live required check with the App's id, so the refusal is
   read as the binding's (cold review F3, F6).
3. **A seat is held by a login that administers the repository**
   (security-reviewer F11): SPEC/06 §2 amended. Under R1 the author holds
   every seat; the write developer holds none, and the check now says so.
4. **Cut 3 taken** (SPEC/06 §9): `docs/developer/manifest.md`, `goldens.md`
   and `edges.md` move to M07. The quickstart carries what a first agent
   needs of both. SPEC/00 §8 still lists them at M06 (data-owner N10): the
   amendment rides PR 4's close.
5. **An agent from the template's image is `agentkeel/<name>`** (ECR's
   creation templates match a namespace): SPEC/06 §6 row 4.
6. **SPEC/06 §8** names what the five seat reviews and the cold review
   found unseeded or unread at M06.

## What a reader can run

```
git log ef7e48e..HEAD --format='%h %s' -- SPEC milestones docs
uv run python -m src.ledger                      # exit 0; row 6 OPEN; "as row M06 reads it" ends RED: template not read
grep -n "amended at PR 2" milestones/README.md   # row 6's S2 sentence
```
