"""M04's seeded cases S1-S5 (SPEC/04 §5), committed before the code that reads them.

Each test asks the reader to refuse its seed, and asserts the planted
reason, not only the verdict. Until the reader is in the tree the test
fails, and it is marked `xfail(strict=True, raises=...)` with the one
exception class its planted reason raises, so an exception of any other
class (a patch that no longer applies, a fixture that moved) is a failure,
not an expected one. Each was run once with `--runxfail` and its message
read (M03 PR 1's second cold read), and the marker comes off in the commit
that lands the reader.

The readers, none of which exist at M04 PR 1 (SPEC/04 §6): tool grounding
in `verdict.build.score_one` (S1); the eval role's candidate list in the
bootstrap stack (S2); A-vs-A in `build` (S3); the `delta_max` bars in
`thresholds.yaml` and the gate reading them (S4); `validate` reading
`deprecated_after` (S5). The API names below are what PR 2 must provide;
if they land under other names, PR 2 changes the call and never what the
seed adds.

Every envelope here is built by `verdict.build` in a temporary folder and
ruled by `verdict.gate`; none is written by hand and none reaches
`evals/history/`. Nothing here calls a model.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import PIN_FIELDS, ROOT, build, gate, plants

from .conftest import (
    AGENT_TOP,
    COMMIT,
    REFAGENT_PIN,
    URL,
    claim_1_checks,
    claim_2_checks,
    make_raw,
)

FIXTURES = Path(__file__).parent / "fixtures" / "m04"
# The pin on main at M04 open, which every seed's fixture and patch was planted against. Not the
# working tree's pin: a swap PR, branched from M04 PR 2's head, moves that, and its own checks ran
# these seeds and failed them for it (#25, #26). The seeds are read against the tree they were
# planted in: the working tree with this pin (`planted_tree`).
PLANTED = {"id": "anthropic.claude-sonnet-4-6", "version": None, "profile": "us.anthropic.claude-sonnet-4-6",
           "region": "us-west-2"}  # fmt: skip
INCUMBENT = PLANTED["profile"]
PLANTED_TOP = {**AGENT_TOP, "model_id": PLANTED["profile"], "region": PLANTED["region"]}
MOVED = any(REFAGENT_PIN.get(field) != PLANTED[field] for field in PIN_FIELDS)
LLAMA = "meta.llama3-1-8b-instruct-v1:0"


class SeedBroken(Exception):
    """A seed's own precondition failed: its fixture, its patch, the synth, or the table it reads.

    Not AssertionError, which the strict markers expect of the planted
    failure: a broken seed must fail the run, not pass as an expected failure
    (cold review F3 and data-owner F3 on M04 PR 1). Only the planted assertions
    at the end of each test are `assert`s."""


def holds(condition: bool, message: str) -> None:
    if not condition:
        raise SeedBroken(message)


def fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def with_planted_pin(tree: Path) -> None:
    """Put the planted pin back in `tree`'s manifest: the four lines of `model:`, nothing else."""
    path = tree / "agents" / "refagent" / "manifest.yaml"
    text = path.read_bytes().decode("utf-8")  # as checked out: a Windows checkout has CRLF
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    start = lines.index("model:")
    for i in range(start + 1, start + 1 + len(PIN_FIELDS)):
        key = lines[i].strip().partition(":")[0]
        holds(key in PLANTED, f"the manifest's model block: {lines[i]!r}")
        lines[i] = f"  {key}: {'null' if PLANTED[key] is None else PLANTED[key]}"
    path.write_bytes(newline.join(lines).encode("utf-8"))
    holds(yaml.safe_load(path.read_text(encoding="utf-8"))["model"] == PLANTED, "the planted pin is back")


@pytest.fixture(scope="module")
def planted_tree(tmp_path_factory) -> Path | None:
    """None where the working tree pins the planted pin. Elsewhere, refagent's manifest with it put back."""
    if not MOVED:
        return None
    tree = tmp_path_factory.mktemp("planted")
    (tree / "agents" / "refagent").mkdir(parents=True)
    source = (ROOT / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8")
    (tree / "agents" / "refagent" / "manifest.yaml").write_text(source, encoding="utf-8")
    with_planted_pin(tree)
    return tree


@pytest.fixture(autouse=True)
def at_the_planted_pin(planted_tree, monkeypatch):
    """Where the pin moved, a made-up commit's incumbent is the planted pin, not the working tree's."""
    if planted_tree is None:
        return
    for module in (build, gate):
        monkeypatch.setattr(module, "incumbent_at", lambda commit, bundle="agents/refagent", root=ROOT:
                            (dict(PLANTED), "the pin the seeds were planted against"))  # fmt: skip


@pytest.fixture
def seeded():
    """A detached worktree of HEAD with one seed's patch applied. Removed after the test."""
    trees: list[Path] = []

    def apply(patch: str) -> Path:
        tree = Path(tempfile.mkdtemp()) / "tree"
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), "HEAD"],
                       cwd=ROOT, check=True, capture_output=True)  # fmt: skip
        trees.append(tree)  # before apply, so a patch that no longer applies is still cleaned up
        if MOVED:  # a swap PR's head: the patch's context is the planted pin
            with_planted_pin(tree)
        subprocess.run(["git", "apply", str(FIXTURES / patch)], cwd=tree, check=True, capture_output=True)
        return tree

    yield apply
    for tree in trees:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False,
                       capture_output=True)  # fmt: skip


def pin_of(tree: Path) -> dict[str, Any]:
    return yaml.safe_load((tree / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))["model"]


TABLE = "data/rights_table.json"


def the_call(golden: dict[str, Any]) -> dict[str, Any]:
    """The `check_availability` call the question asks for, made on the real tool with the real table.

    The title is the slate title the question names (the longest match), the
    territory and platform are those of the golden's expected row, and the
    date is the date the question asks about, the last ISO date in it: only
    `g-010` has two, and its first is the lure (data-owner F1 on M04 PR 1). The tool validates both the
    arguments and its result against its contract, so every call here is one
    the tool can make. For `g-021`, the sequel with no US row, it answers
    `found: false` (data-owner F9 on M04 PR 1): the incumbent's answer to it
    is not grounded, as it is not in any run on record. `g-021` is retired at
    M04 PR 2 (open.md row 5); the raw runs still answer it, as the planted
    runs did, and build drops that answer unscored."""
    import re

    from agents.refagent import agent

    rows = json.loads((ROOT / TABLE).read_text(encoding="utf-8"))
    titles = json.loads((ROOT / "data" / "slate.json").read_text(encoding="utf-8"))["titles"]
    named = max((t for t in titles if t["title"] in golden["question"]), key=lambda t: len(t["title"]))
    row = next(r for r in rows if r["table_row"] == golden["expected"]["table_row"])
    date = re.findall(r"\d{4}-\d{2}-\d{2}", golden["question"])[-1]
    arguments = {"title_id": named["title_id"], "territory": row["territory"], "platform": row["platform"],
                 "date": date}  # fmt: skip
    return {"name": "check_availability", "input": arguments, "status": "success",
            "output": agent.check_availability(arguments, rows, TABLE)}


def grounded(golden: dict[str, Any], latency: int = 500, tokens: int = 300) -> dict[str, Any]:
    """An answer as the incumbent gives it: right and cited, after the call its question asks for.

    Grounded (SPEC/04 §2) wherever the tool's row is the golden's row, which
    is every live ordinary and trap golden (`g-021`, which it is not, is retired
    at M04 PR 2)."""
    base = {"id": golden["id"], "kind": golden["kind"], "question": golden["question"],
            "usage": {"inputTokens": tokens * 2 // 3, "outputTokens": tokens // 3, "totalTokens": tokens},
            "latency_ms": latency, "source": TABLE}  # fmt: skip
    if golden["kind"] not in build.CITING_KINDS:
        return {**base, "text": "", "parsed": None, "stop_reason": "guardrail_intervened",
                "guardrail_topics": [], "tool_calls": []}  # fmt: skip
    expected = golden["expected"]
    parsed = {**expected["answer_fields"], "table_row": expected["table_row"], "clause_id": expected["clause_id"]}
    return {**base, "text": json.dumps(parsed), "parsed": parsed, "stop_reason": "end_turn",
            "guardrail_topics": [], "tool_calls": [the_call(golden)]}  # fmt: skip


@pytest.fixture
def measured(tmp_path: Path, goldens, monkeypatch, planted_tree):
    """Build an agent envelope from a raw run through build's command line, as `chain` does.

    With no controls and no corpus, as `chain` has them: these seeds are about
    the model, not the plants or the fingerprint. `tree`, when given, is a
    worktree with a seed's pin in it: build reads the pin's version there, and
    the gate reads the pin there instead of at the made-up commit.
    """
    monkeypatch.setattr(plants, "CONTROLS", {})
    monkeypatch.setattr(build, "fingerprint_at", lambda commit, root=ROOT: (None, "no corpus in the fixture"))
    monkeypatch.setattr(gate, "fingerprint_at", lambda commit, root=ROOT: (None, "no corpus in the fixture"))
    runs = iter(range(1000))

    def envelope(raw: dict[str, Any], *, commit: str = COMMIT, history: Path | None = None,
                 tree: Path | None = None, out: Path | None = None, extra: tuple[str, ...] = ()) -> Path:  # fmt: skip
        work = tmp_path / f"run-{next(runs)}"
        work.mkdir()
        control_raw = work / f"{commit}.baseline-raw.json"
        control_raw.write_text(json.dumps(make_raw(goldens, commit=commit)), encoding="utf-8")
        card = work / f"{commit}.baseline-card.json"
        holds(build.main(["card", "--raw", str(control_raw), "--out", str(card)]) == 0, "build refused the control card")
        top = {**raw, "commit": commit}
        tree = tree or planted_tree
        if tree is not None:
            top["bundle"] = str(tree / "agents" / "refagent")
            pinned = yaml.safe_load((tree / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
            monkeypatch.setattr(gate, "manifest_at", lambda c, bundle, root=ROOT: (pinned, "the seed's tree"))
        agent_raw = work / f"{commit}.agent-raw.json"
        agent_raw.write_text(json.dumps(top), encoding="utf-8")
        out = out or work / f"{commit}.json"
        history = history or tmp_path / "no-history"
        code = build.main(["envelope", "--raw", str(agent_raw), "--control-card", str(card), "--out", str(out),
                           "--history-dir", str(history), "--run-url", URL,
                           *claim_1_checks(work), *claim_2_checks(work), *extra])  # fmt: skip
        holds(code == 0, f"build refused the envelope (exit {code})")
        return out

    return envelope


@pytest.fixture
def incumbent_history(tmp_path: Path, goldens, measured):
    """Three envelopes of the incumbent on its pin, in the runner, every citing golden passed and grounded.

    Built by build, into a temporary history folder the gate is then given.
    Three, so a median has something to be the middle of (S4)."""
    history = tmp_path / "history"
    history.mkdir()
    live = [g for g in goldens.values() if not g.get("retired")]
    raw = {**make_raw(goldens), **PLANTED_TOP, "observations": [grounded(g) for g in live]}
    for commit in ("b" * 40, "c" * 40, "d" * 40):
        measured(raw, commit=commit, history=history, out=history / f"{commit}.json")
    return history


# --- S1: a breaking swap -----------------------------------------------------


def test_s1_a_breaking_swap_whose_answers_the_tool_never_grounded_is_red(seeded, measured, incumbent_history, goldens):
    """The pin moved to Llama 3.1 8B. Every ordinary and trap answer has the expected fields and a
    real row and clause, and none came from a successful `check_availability` call: the call was
    printed as text, or refused by the schema. The incumbent passed eleven of them grounded; g-021,
    the sequel with no US row, it never grounds (the_call), and g-021 is retired at M04 PR 2, so its
    answer in the seed is dropped unscored and the eleven live ones are what is read.
    SPEC/00 §9: the rights table is the truth, never inferred. So each is a golden that passed and
    now fails, and the swap is RED for that reason (F4.1; SPEC/04 §2, §7)."""
    tree = seeded("s1-breaking-pin.patch")
    pin = pin_of(tree)
    holds(pin["id"] == LLAMA and pin["profile"] == f"us.{LLAMA}", "the seed moves the pin")
    seed = fixture("s1-breaking-raw.json")
    holds(seed["model_id"] == pin["profile"], "the raw run is the swap's")
    live = {g for g, golden in goldens.items() if not golden.get("retired")}
    citing = [o for o in seed["observations"] if o["kind"] in build.CITING_KINDS and o["id"] in live]
    holds(len(citing) == 11, "every live ordinary and trap golden")
    holds(not any(call["status"] == "success" for o in citing for call in o["tool_calls"]),
          "no answer is grounded: the seed is what it says")

    out = measured(seed, tree=tree, history=incumbent_history)
    results = gate.read(out)["goldens"]
    verdict, reasons = gate.rule(out, incumbent_history)

    ungrounded = sorted(o["id"] for o in citing if results[o["id"]]["pass"])
    assert ungrounded == [], f"answers the tool did not ground passed: {ungrounded}"
    assert verdict == "RED", reasons
    assert any("regressed" in reason for reason in reasons), reasons


# --- S2: an equivalent swap the eval role cannot call ------------------------

SONNET_45 = "anthropic.claude-sonnet-4-5-20250929-v1:0"


def eval_role_invokes(tmp_path: Path) -> list[dict[str, Any]]:
    """The eval role's Allow statements that grant bedrock:InvokeModel, from the synthesised bootstrap template.

    Synthesised as tests/test_bootstrap.py does: the rendered template is what
    the human deploys, so it is what IAM will say."""
    import os
    import sys

    done = subprocess.run([sys.executable, str(ROOT / "infra" / "bootstrap" / "app.py")], cwd=ROOT,
                          capture_output=True, text=True, check=False,
                          env={**os.environ, "PYTHONPATH": str(ROOT), "CDK_OUTDIR": str(tmp_path)})  # fmt: skip
    holds(done.returncode == 0, done.stderr)
    template = json.loads((tmp_path / "AgentkeelBootstrap.template.json").read_text(encoding="utf-8"))
    for logical, resource in template["Resources"].items():
        if resource["Type"] == "AWS::IAM::Policy" and "EvalRole" in logical:
            statements = resource["Properties"]["PolicyDocument"]["Statement"]
            return [s for s in statements if s["Effect"] == "Allow"
                    and "bedrock:InvokeModel" in ([s["Action"]] if isinstance(s["Action"], str) else s["Action"])]
    raise SeedBroken("no policy on the eval role")


def test_s2_the_equivalent_swaps_pin_is_one_the_eval_role_may_invoke(seeded, tmp_path):
    """The pin moved to Sonnet 4.5, the Threshold Owner's equivalent, and nothing else changed. The
    swap PR's run calls it through the eval role; if the role may not invoke it, every call is
    AccessDeniedException, every golden fails and the swap is RED for a reason that is IAM's, not the
    model's (F4.2; SPEC/04 §3 item 2). Read from the template the human deploys."""
    tree = seeded("s2-equivalent-pin.patch")
    pin = pin_of(tree)
    holds(pin["id"] == SONNET_45 and pin["profile"] == f"us.{SONNET_45}", "the seed moves the pin")
    holds(pin["region"] == "us-west-2", "and nothing else")

    invokes = json.dumps(eval_role_invokes(tmp_path))
    holds(f"inference-profile/{INCUMBENT}" in invokes, "the incumbent's profile is there: the read is the right one")
    assert f"inference-profile/{pin['profile']}" in invokes, \
        f"the eval role may not invoke the equivalent swap's profile {pin['profile']}"  # fmt: skip
    assert f"foundation-model/{pin['id']}" in invokes, \
        f"the eval role may not invoke the equivalent swap's model {pin['id']}"  # fmt: skip


# --- S3: A-vs-A with a diff -------------------------------------------------


def test_s3_two_runs_of_one_pin_that_differ_are_a_failed_a_vs_a(measured, incumbent_history, tmp_path):
    """Two runs of the incumbent pin on one tree, identical but for g-006, which passes in one and
    fails in the other. Ruled against the incumbent's history (cold review F4 on M04 PR 1: with no
    incumbent, PR 2's bars would rule the single runs RED for that), the first alone is GREEN and
    the second alone is RED for one reason, g-006 regressed: a flaky golden, blamed on whatever the
    diff was, because nothing compares two runs of one pin. Given both, build writes F4_3 fail and
    names g-006 in the envelope's `a_vs_a` (F4.3; SPEC/04 §4, §6). Today build's command line has no
    second raw, and argparse refuses the flag."""
    a, b = fixture("s3-a.json"), fixture("s3-b.json")
    holds((a["model_id"], a["region"]) == (b["model_id"], b["region"]) == (INCUMBENT, "us-west-2"), "one pin")
    differ = [x["id"] for x, y in zip(a["observations"], b["observations"], strict=True) if x != y]
    holds(differ == ["g-006"], "the seed is what it says")
    verdict, reasons = gate.rule(measured(a, history=incumbent_history), incumbent_history)
    holds(verdict == "GREEN", f"the first run alone is a clean run: {reasons}")
    verdict, reasons = gate.rule(measured(b, history=incumbent_history), incumbent_history)
    holds(verdict == "RED" and len(reasons) == 1 and "regressed" in reasons[0] and "g-006" in reasons[0],
          f"the second run alone reads as g-006 regressed, and nothing else: {verdict} {reasons}")

    second = tmp_path / f"{COMMIT}.agent-raw-b.json"
    second.write_text(json.dumps({**b, "commit": COMMIT}), encoding="utf-8")
    out = measured(a, history=incumbent_history, extra=("--a-vs-a", str(second)))
    envelope = gate.read(out)
    assert envelope["checks"]["F4_3"]["status"] == "fail", envelope["checks"]
    assert envelope["a_vs_a"]["agent"] == ["g-006"], envelope.get("a_vs_a")
    verdict, reasons = gate.rule(out, incumbent_history)
    assert verdict == "RED" and any("F4_3" in reason for reason in reasons), reasons


# --- S4: over the delta_max bars --------------------------------------------


@pytest.mark.parametrize(("seed", "bar", "field", "times"), [
    ("s4-slow-raw.json", "p95", "latency_ms", 3),  # p95 at 3x; the bar is 2.0x (SPEC/04 section 2)
    ("s4-heavy-raw.json", "tokens", "usage", 2),  # the agent's tokens at 2x; the bar is 1.5x
])  # fmt: skip
# The ids stay as planted: the Makefile's F4_4 cases name them.
def test_s4_a_run_over_the_incumbents_bar_is_red(seed, bar, field, times, measured, incumbent_history, goldens):
    """The incumbent's answers, every one grounded and right, three times as slow (p95) or with
    twice the tokens. The incumbent's history is three runs on the same pin, in the same mode. No
    golden regresses, so today the gate rules GREEN; `delta_max` (SPEC/04 section 2: p95 at most
    2.0x the incumbent's median, the agent's tokens at most 1.5x) makes it RED for that reason
    (F4.4)."""
    run = fixture(seed)
    holds(run["model_id"] == INCUMBENT and run["mode"] == "runner", "the incumbent's pin, in the history's mode")
    live = {g["id"]: g for g in goldens.values() if not g.get("retired")}
    for observation in run["observations"]:
        if observation["id"] not in live:  # g-021, retired at M04 PR 2: build drops its answer unscored
            continue
        incumbent = grounded(live[observation["id"]])
        if field == "latency_ms":
            holds(observation["latency_ms"] == times * incumbent["latency_ms"], observation["id"])
        else:
            holds(observation["usage"]["totalTokens"] == times * incumbent["usage"]["totalTokens"], observation["id"])
        holds({k: v for k, v in observation.items() if k not in ("latency_ms", "usage")}
              == {k: v for k, v in incumbent.items() if k not in ("latency_ms", "usage")},
              f"{observation['id']}: the same answers as the incumbent's, on today's table")

    out = measured(run, history=incumbent_history)
    verdict, reasons = gate.rule(out, incumbent_history)
    assert verdict == "RED", f"{bar} {times}x the incumbent's ruled {verdict}: {reasons}"
    # The bar's own reason, by name: `gate.spend`'s "tokens:" reason is not it (cold review of PR 2, F5).
    named = {"p95": "p95_ms", "tokens": "agent_tokens"}[bar]
    assert any(reason.startswith("F4_4: ") and named in reason for reason in reasons), reasons


# --- S5: a pin past, or within 30 days of, its end of life -------------------

SONNET_4 = "anthropic.claude-sonnet-4-20250514-v1:0"


def test_s5_a_pin_within_30_days_of_its_end_of_life_fails_validate(seeded):
    """The pin moved to Sonnet 4 with `deprecated_after: '2026-10-14'`, Bedrock's `endOfLifeTime`
    for it (read 2026-09-26, milestones/M04/runs/model_access_2026-09-26.md). Today's manifest
    check takes the date, and nothing else in validate reads it. From M04 PR 2 a pin whose date is
    within 30 days of the run, or past, fails; null passes (SPEC/04 section 5). Read before
    2026-10-14 the seed is "30 days before"; after, "already past". The same check refuses both."""
    import datetime

    from src.validate import checks

    tree = seeded("s5-deprecated-pin.patch")
    manifest = yaml.safe_load((tree / "agents" / "refagent" / "manifest.yaml").read_text(encoding="utf-8"))
    holds(manifest["model"]["id"] == SONNET_4 and manifest["deprecated_after"] == "2026-10-14", "the seed")
    holds(checks.check_manifests(tree) == [], "the schema takes the date: only its reader can refuse it")

    from src.validate import lifecycle

    errors = lifecycle.check(tree, today=datetime.date.today())
    assert any("deprecated_after" in e and "2026-10-14" in e for e in errors), errors
