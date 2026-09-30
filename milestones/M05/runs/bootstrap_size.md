# The bootstrap template, measured before M05 PR 2 adds to it (`open.md` row 20)

Measured 2026-09-28 by local synth, nothing deployed, as compact JSON
(`json.dumps(template, separators=(",", ":"))`), the method M04 used. The
ceiling is CloudFormation's 51,200 bytes for a template passed inline: the
account is not CDK-bootstrapped, so there is no asset bucket to upload a
larger one to.

## The 66 bytes, accounted for

**Corrected at M05 PR 2 on the reviews, before the deploy.** This file's
first version (`30a04f5`) put the 66 bytes down to a difference between
M04 PR 1's scratch edit and the edit as committed. That was wrong. They are
the measuring script, not the template:

| At | Read as UTF-8 | Read with Windows' default (cp1252) |
|---|---|---|
| `5a5720e` (this PR's base) | **49,107** | **49,173** |
| head, after this PR's two statements | 49,613 | 49,685 |

`open()` without an encoding reads cp1252 on Windows. The template holds
eleven `§` characters, each two bytes in UTF-8; read as cp1252 each
becomes two characters, and `json.dumps` escapes each to six, so the
cp1252 reading counts 6 bytes more per `§`: 11 × 6 = 66. M04 PR 1 read
the file as UTF-8 (49,107); M04 PR 3 read it with the default (49,173).
The tree did not change between them.

Measured the same way throughout (cp1252), the history is: 47,601 at
M04 PR 1's merge and at `2870467^`; 49,173 at `2870467` (the swap
candidates, +1,572, all in `EvalRoleDefaultPolicy`); unchanged to
`5a5720e`.

## What this PR adds

The agent boundary's `s3:PutObject` statement and the S3 endpoint's
statement for the audit bucket (SPEC/05 §5.1, §6), and one sentence in the
boundary's cdk-nag reason: **+506 bytes**, 49,107 to 49,613 read as UTF-8,
**1,587 left** of 51,200. The UTF-8 reading is the one to use from here;
the bytes CloudFormation is sent are the UTF-8 encoding, fewer still
(49,565 with `ensure_ascii=False`).

    CDK_OUTDIR=.git/boot-out PYTHONPATH=. uv run python infra/bootstrap/app.py
    python -c "import json; t = json.load(open('.git/boot-out/AgentkeelBootstrap.template.json', encoding='utf-8')); print(len(json.dumps(t, separators=(',', ':'))))"
