# The bootstrap template, measured before M05 PR 2 adds to it (`open.md` row 20)

Measured 2026-09-28 by local synth, nothing deployed, compact JSON
(`json.dumps(template, separators=(",", ":"))`), the method M04 used.
The ceiling is CloudFormation's 51,200 bytes for a template passed inline:
the account is not CDK-bootstrapped, so there is no asset bucket to upload
a larger one to.

| At | Bytes | What |
|---|---|---|
| `8e438d1` (M04 PR 1's merge) | 47,601 | the base |
| `2870467^` | 47,601 | unchanged |
| `2870467` (M04 PR 2, the swap candidates) | 49,173 | +1,572, all of it in `EvalRoleDefaultPolicy` (4,499 to 6,071 bytes) |
| `5a5720e` (M05 PR 1's merge, this PR's base) | 49,173 | unchanged; no bootstrap input changed since |

**The 66 bytes, accounted for.** M04 PR 1 measured 49,107 in a scratch
worktree with the candidates added (M04 `feasibility.md` §6 row 7); the
edit as committed at `2870467` measures 49,173. The base is the same at
both points (47,601), so the 66 bytes are the difference between the
scratch edit and the committed one, both in the eval role's policy. They
were never in the tree at any merge. The scratch worktree was removed, so
its exact bytes cannot be re-read.

**Left for M05 PR 2:** 51,200 − 49,173 = **2,027 bytes**, for the agent
boundary's `s3:PutObject` statement and the S3 endpoint's statement for the
audit bucket (SPEC/05 §5.1, §6). The size after them is in
`rulings/pr2-security.md`.

    CDK_OUTDIR=.git/boot-out PYTHONPATH=. uv run python infra/bootstrap/app.py
    python -c "import json; t = json.load(open('.git/boot-out/AgentkeelBootstrap.template.json')); print(len(json.dumps(t, separators=(',', ':'))))"
