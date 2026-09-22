---
# M01 PR 3 (#9), the Threshold Owner's key. Ruling B: one seat per ruling
# file; `pr3.md`, `pr3-engineering.md` and `pr3-product.md` carry the same
# `pr`. The seat owns the agent model id + version + region (SPEC/00 §5);
# this file rules how an envelope records them (ADR-0007, T1 to T3).
ruling: pr3-threshold-owner
seat: Threshold Owner
authorises:
  - thresholds.yaml
  - milestones/M01/rulings/pr3-threshold-owner.md
evidence:
  - docs/adr/ADR-0007-the-envelope-says-where-the-agent-ran.md
  - milestones/M01/rulings/pr2-cold-review.md
pr: 9
---

# M01 PR 3 — the Threshold Owner's rulings on ADR-0007

Cold review findings 35 and 39 (PR 2) were carried here:
- **35:** nothing compares the model a run used with the manifest's pin;
- **39:** the envelope carries neither region nor model version, though
  A-vs-A (M04) compares the pair.

**T1 — `model_version` comes from the manifest's pin.** Bedrock returns no
version for `us.anthropic.claude-sonnet-4-6` (ruling p), so the pin is
`null`, and `agents/refagent/manifest.yaml` says why. A version read from a
response would be a second source that can disagree with the first, and
there would be nothing to settle which one is right.

**T2 — `region` is recorded per run,** from the raw file's request region,
and compared with the pin.

*Reworded after the PR 3 cold review* (threshold-owner F1 = cold F1). The
first wording said "the run says what did", and that overstated it. The
region recorded is **the request region the client was built with**. The
runner takes it from the pin (`src/agent/run.py`), and Converse reports no
region that served the call, so a run routed elsewhere by Bedrock is not
seen. So the check guards against a changed runner or a hand-edited raw file
or envelope. It does not guard against routing. That limit is the Threshold
Owner's to carry into M04, where A-vs-A compares the pair.

**T3 — a run off the pin is REJECTED, not RED.** A run on another model or
another region did not measure the pinned subject, so it is not a result
about that subject. RED would enter it in history as one, and every later
reading of the regression bar would count it. The gate compares all three
fields (model id, region, version) with the manifest as it stood at the
envelope's commit, the same way the cap is read (ruling m).

**What this does not rule:**
- the cap re-rule against measured spend (finding 31), which is for the
  M01 close;
- `judge_model_id`, which is M03's (finding 37);
- what a model swap should do. That is M04's claim, and it reads these
  fields.

**What holds it:** `tests/test_adr0007.py`. A run off the pin in each of the
three fields is REJECTED. build writes a region off the pin, and the gate
refuses it: the two disagree, which is P5.

**Finding 30 (PR 2 cold review), closed here.** `thresholds.yaml`'s comment
named "refagent on Sonnet 5", but the pin is Sonnet 4.6 (ruling p). The
comment is corrected. It is prose only: no bar moves, so it takes one key,
this one.

**The pin's `id`** (threshold-owner F2). The envelope carries the profile, so
the gate now also refuses a pin whose `id` and `profile` disagree.
