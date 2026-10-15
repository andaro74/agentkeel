"""M10's seeded cases (SPEC/10 §5), committed before the code that reads them.

Four kinds. **S1, the call records** (`tests/fixtures/m10/s1-call-records/`): today's
answer record, which names no caller, and five read records in the shape SPEC/10 §2
fixes (a stranger answered, a bypass, a wrong subject, a late refusal, and the held
four). Their reader is `src.verdict.caller.calls`, not in the tree. **S2, a manifest
with no `callers`** (`s2-manifest-no-callers/`): festival-desk's manifest as its
repository holds it, which `src.validate.callers.callers_errors` must refuse naming
the field, and the same manifest with `callers`, which the manifest schema must
admit; today the module is absent and the schema refuses the key. **S3, a caller
admitted with one key** (`s3-caller-added/cases.json`): refagent's manifest gaining a
`callers` entry with the Tool Owner's ruling alone, which `two-key` must refuse under
ADR-0016 (entry 7 of the closed list); today it passes. **S4** is two guards, no fixture: the fixture
agent's stack conditions the agent role's invoke on its own guardrail, and refagent's
latest envelope reads its plants whole; both pass today and must pass after the door
is added to the construct. **The run** is `milestones/M10/runs/f10_x_caller_run.yaml`,
`observed: null`, read by `scripts/observe_caller.py` after PR 2 merges.

Each planted test is marked `xfail(strict=True, raises=AssertionError)`, so an
exception of any other class (a moved fixture, a file that no longer parses) is a
failure, not an expected one. Preconditions raise `SeedBroken`. Each was run once
with `--runxfail` and its message read, and a marker comes off in the commit that
lands its reader (fixtures, PR 2) or records the run (PR 3). Nothing here calls AWS,
a model or GitHub.

M10 builds one control, the door, and the reading of it (ADR-0015); these readers
are the platform check's, the gate's and the envelope's. P5 holds: the observer
writes raw records, `build` rules, the gate reads the envelope, the ledger reads
the gate. The agent writes nothing about its callers.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.verdict import ROOT, gate
from tests.test_gates import Repo, git, ruling
from tests.test_m06_seeds import SeedBroken, holds  # noqa: F401 - SeedBroken is the class `holds` raises
from tests.test_m09_platform import FIXTURE as M09_AGENT
from tests.test_m09_platform import actions, of_type, synth, the_one

RUNS = ROOT / "milestones" / "M10" / "runs"
FIXTURES = Path(__file__).parent / "fixtures" / "m10"
RECORDS = FIXTURES / "s1-call-records"
MANIFESTS = FIXTURES / "s2-manifest-no-callers"
CASES = json.loads((FIXTURES / "s3-caller-added" / "cases.json").read_text(encoding="utf-8"))
REFAGENT_MANIFEST = "agents/refagent/manifest.yaml"
MAX_SECONDS = 600  # detection.max_seconds, reused (SPEC/10 §11 R6)

expected_failure = pytest.mark.xfail(strict=True, raises=AssertionError, reason="planted at M10 PR 1 (SPEC/10 §5)")

# The run file's four steps and the caller each states (SPEC/10 §5): what `calls` compares each record with. At
# PR 2 the observer derives it from the run file's `steps[].caller` and `observed.bypass.principal` (cold review
# F3 on PR 1); this dict stands for that derivation, the bypass principal being what the owner would write.
STATED = {
    "admitted": {"subject": "lantern-desk", "outcome": "admitted"},
    "none": {"subject": None, "outcome": "refused", "reason": "no identity"},
    "stranger": {"subject": "stranger", "outcome": "refused", "reason": "not admitted"},
    "bypass": {"subject": "arn:aws:sts::000000000000:assumed-role/agentkeel-fixture-laptop/owner", "outcome": "refused",
               "reason": "not the door"},
}  # fmt: skip
# The manifest's issuer is the symbol `self` at M10 (the agent's own pool; tool-owner F1): the pool's URL is known
# only after the construct makes it, and the reader learns it from the observer, not from the manifest.
CALLERS = [{"subject": "lantern-desk", "issuer": "self"}, {"subject": "box-office", "issuer": "self"}]


def load_yaml(path: Path) -> Any:
    holds(path.is_file(), f"{path.relative_to(ROOT).as_posix()} is in the tree")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def record(name: str) -> dict[str, Any]:
    path = RECORDS / name
    holds(path.is_file(), f"{name} is in tests/fixtures/m10/s1-call-records/")
    return json.loads(path.read_text(encoding="utf-8"))


def reader(module: str, name: str, seed: str, what: str) -> Any:
    """A function PR 2 adds to `module`; the planted failure is that the module is not there."""
    assert importlib.util.find_spec(module) is not None, f"seed {seed}: {what}"
    found = getattr(importlib.import_module(module), name, None)
    assert found is not None, f"seed {seed}: {what}"
    return found


# --- S1: the call records, read by caller.calls --------------------------------------------------

CALLS_WHAT = "nothing reads a call record"


@expected_failure
def test_s1_a_call_record_names_its_caller_and_the_door_refused_the_rest():
    """`src.verdict.caller.calls(records, stated, callers, max_seconds)` over six fixtures (F10.1, F10.3, F10.4).
    Today's answer record names no caller: not held. A stranger answered: not held, naming the subject. A
    bypass: not held. A subject in callers that is not the stated caller: not held. A refusal delivered 601 s
    after its event time: not held, later than N. The four as stated, each refusal within N: held, admitted
    1 of 1, refused 3 of 3. Today nothing reads a call record (SPEC/10 §3.5)."""
    today = record("record_no_caller.json")
    holds("subject" not in today and "outcome" not in today and today.get("what") == "agent answer",
          "record_no_caller.json is today's answer record shape")  # fmt: skip
    late = record("call_refused_late.json")
    holds(late["delivered"] == "2026-10-20T10:12:01Z" and late["time"] == "2026-10-20T10:02:00Z", "the late refusal is 601 s late")
    calls = reader("src.verdict.caller", "calls", "S1", CALLS_WHAT)

    no_caller = calls([today], STATED, CALLERS, MAX_SECONDS)
    assert no_caller["read"] is True and no_caller["held"] is False, no_caller
    assert "names no caller" in " ".join(no_caller["reasons"]), no_caller["reasons"]
    stranger = calls([record("call_stranger_answered.json")], STATED, CALLERS, MAX_SECONDS)
    assert stranger["held"] is False and "stranger" in " ".join(stranger["reasons"]), stranger
    assert "does not admit" in " ".join(stranger["reasons"]), stranger["reasons"]
    bypass = calls([record("call_bypass.json")], STATED, CALLERS, MAX_SECONDS)
    assert bypass["held"] is False and "without the door" in " ".join(bypass["reasons"]), bypass
    wrong = calls([record("call_wrong_subject.json")], STATED, CALLERS, MAX_SECONDS)
    assert wrong["held"] is False and "box-office" in " ".join(wrong["reasons"]), wrong
    assert "other than the one that called" in " ".join(wrong["reasons"]), wrong["reasons"]
    overdue = calls([late], STATED, CALLERS, MAX_SECONDS)
    assert overdue["held"] is False and "later than" in " ".join(overdue["reasons"]), overdue
    held = calls(record("calls_held.json")["records"], STATED, CALLERS, MAX_SECONDS)
    assert held["read"] is True and held["held"] is True and held["reasons"] == [], held
    assert (held["admitted"], held["expected_admitted"], held["refused"], held["expected_refused"]) == (1, 1, 3, 3), held


# --- S2: a manifest with no callers, read by validate.callers and the schema ------------------------


def test_s2_a_manifest_that_does_not_say_who_may_call_is_refused():
    """festival-desk's manifest at 19864419 has no `callers`. `src.validate.callers.callers_errors(manifest)` must
    refuse it naming the field (F10.4). Today nothing reads such a field (SPEC/10 §3.3)."""
    manifest = load_yaml(MANIFESTS / "manifest.yaml")
    holds("callers" not in manifest and manifest["name"] == "festival-desk", "S2's manifest has no callers field")
    callers_errors = reader("src.validate.callers", "callers_errors", "S2", "nothing reads who may call an agent")
    errors = callers_errors(manifest)
    assert errors and any("callers" in e for e in errors), errors


def test_s2_a_manifest_with_callers_passes_the_schema():
    """The same manifest with one `callers` entry must pass `src/manifest/schema.json` (F10.4: a manifest can say).
    Today the schema's `additionalProperties: false` refuses the key (SPEC/10 §3.3)."""
    from src import manifest as manifest_module

    with_callers = load_yaml(MANIFESTS / "with_callers.yaml")
    holds(with_callers.get("callers") == [{"subject": "lantern-desk", "issuer": "self"}], "with_callers.yaml names one subject")
    errors = manifest_module.schema_errors(with_callers)
    assert errors == [], f"seed S2: the manifest schema refuses `callers`: {errors}"


# --- S3: a caller admitted with one key, read by two-key ---------------------------------------------

LINE = "may_be_called_by: []\n"
EMPTY = "callers: []\n"  # what M10 PR 2 wrote into refagent's manifest (SPEC/10 §2: `[]` the default)


def manifest_with(callers: str) -> str:
    """refagent's manifest as the tree holds it, its `callers: []` line taken out and the case's block put after
    `may_be_called_by`. Until PR 2 the tree had no `callers` key and the block was simply added (PR 1)."""
    text = (ROOT / REFAGENT_MANIFEST).read_text(encoding="utf-8").replace("\r\n", "\n")
    holds(text.count(LINE) == 1 and text.count("\ncallers:") == text.count(EMPTY) == 1,
          "refagent's manifest has may_be_called_by once and one `callers: []` key (M10 PR 2)")  # fmt: skip
    text = text.replace(EMPTY, "")
    block = "" if callers == "<the line deleted>" else callers
    return text.replace(LINE, LINE + block)


def manifest_repo(tmp_path: Path, base: str) -> Repo:
    """A repository whose base ref holds refagent's manifest with `base` as its callers block, and this tree's
    CODEOWNERS. The caller removes the worktree."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    repo = Repo(root)
    repo.write(".github/CODEOWNERS", (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8"))
    repo.write(REFAGENT_MANIFEST, manifest_with(base))
    (root / "evals" / "history").mkdir(parents=True)
    (root / "evals" / "history" / ".keep").write_text("", encoding="utf-8")
    repo.commit_base()
    return repo


@pytest.fixture
def with_empty_callers(tmp_path: Path):
    """The planted cases' base: refagent's manifest with `callers: []`."""
    repo = manifest_repo(tmp_path, CASES["base"])
    yield repo
    git(repo.root, "worktree", "remove", "--force", str(repo.base))


@pytest.mark.parametrize("case", sorted(CASES["relaxed_with_one_key"]))
def test_s3_a_caller_admitted_with_one_key_is_refused(with_empty_callers, case):
    """A subject added to `callers`, or the key removed, with the Tool Owner's ruling alone: `two-key` must refuse it
    naming the path and ADR-0016 (F10.5), and pass the same diff with Security's key. Today the
    closed list has no entry for `callers` and the gate passes it (SPEC/10 §3.4)."""
    with_empty_callers.write(REFAGENT_MANIFEST, manifest_with(CASES["relaxed_with_one_key"][case]))
    with_empty_callers.write("milestones/M10/rulings/a.md", ruling("Tool Owner", [REFAGENT_MANIFEST]))
    refused = with_empty_callers.keys() or ""
    assert f"{REFAGENT_MANIFEST}: callers" in refused and "one seat holds a key" in refused, \
        f"seed S3 ({case}): two-key passes a caller admitted with one key"  # fmt: skip
    assert "ADR-0016" in refused
    with_empty_callers.write("milestones/M10/rulings/b.md", ruling("Security", ["infra/**"], keys=[REFAGENT_MANIFEST]))
    assert with_empty_callers.keys() is None


@pytest.mark.parametrize("case", sorted(CASES["not_a_relaxation"]))
def test_s3_guard_a_narrowing_or_a_first_empty_list_needs_no_second_key(tmp_path, case):
    """Guards, not seeds, each a real diff to the manifest with one ruling: a subject removed from two (a
    narrowing), and the key first written as `[]` (what PR 2 does to refagent's and ratings-helper's). Each
    passes before the reader and must still pass after entry 7 (SPEC/10 §2: absent to `[]` is not a
    relaxation). A byte-identical manifest would be no guard: two-key never sees an unchanged path (cold
    review F2 on PR 1)."""
    guard = CASES["not_a_relaxation"][case]
    repo = manifest_repo(tmp_path, guard["base"])
    try:
        repo.write(REFAGENT_MANIFEST, manifest_with(guard["change"]))
        repo.write("milestones/M10/rulings/a.md", ruling("Tool Owner", [REFAGENT_MANIFEST]))
        assert repo.keys() is None, f"guard ({case}): two-key read a narrowing or a first empty list as a relaxation"
    finally:
        git(repo.root, "worktree", "remove", "--force", str(repo.base))


# --- S4: the guardrail stays on the call (two guards, not seeds; they pass) -------------------------------


@pytest.fixture(scope="module")
def fixture_template(tmp_path_factory) -> dict[str, Any]:
    """M09's fixture agent's stack as the construct synthesises it today (the agent the door goes on)."""
    code, said, template = synth(M09_AGENT.relative_to(ROOT), tmp_path_factory.mktemp("festival-desk-m10"))
    assert code == 0, said
    return template


def test_s4_guard_the_invoke_is_conditioned_on_the_agents_own_guardrail(fixture_template):
    """F10.2's first guard: every Allow on `bedrock:InvokeModel` in the fixture agent's stack carries the
    `bedrock:GuardrailIdentifier` condition on the stack's own guardrail at its version, and the runtime
    carries no authoriser yet (the door is PR 2's; this line is rewritten there, not deleted). Passes today and
    must pass after the door is added to the construct. No marker."""
    guardrail, _ = the_one(fixture_template, "AWS::Bedrock::Guardrail")
    version, _ = the_one(fixture_template, "AWS::Bedrock::GuardrailVersion")
    invokes = [s for policy in of_type(fixture_template, "AWS::IAM::Policy").values()
               for s in policy["Properties"]["PolicyDocument"]["Statement"]
               if s["Effect"] == "Allow" and "bedrock:InvokeModel" in actions(s)]  # fmt: skip
    assert len(invokes) == 2
    for statement in invokes:
        identifier = statement["Condition"]["StringEquals"]["bedrock:GuardrailIdentifier"]
        assert identifier == {"Fn::Join": ["", [{"Fn::GetAtt": [guardrail, "GuardrailArn"]}, ":", {"Fn::GetAtt": [version, "Version"]}]]}
    runtime = next(iter(of_type(fixture_template, "AWS::BedrockAgentCore::Runtime").values()))["Properties"]
    assert "AuthorizerConfiguration" not in runtime, "the door is not in the tree yet (SPEC/10 §3.1)"


def test_s4_guard_refagents_plants_are_whole_on_the_latest_envelope():
    """F10.2's second guard: the latest CI-written envelope reads refagent's plants fired equal to expected, 7 of
    7. Passes today and must pass on the first envelope after the construct change. The verdict is not read
    here: a main envelope RED for a reason that is not the door's is not F10.2's (cold review N4). No marker."""
    path = gate.latest()
    holds(path is not None, "a CI-written envelope is under evals/history/")
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert envelope["plants_expected"] == envelope["plants_fired"] == 7, (envelope["plants_expected"], envelope["plants_fired"])


# --- the run file (made after PR 2 merges; observed filled by the owner) -----------------------------------


@expected_failure
def test_the_caller_run_was_made():
    run = load_yaml(RUNS / "f10_x_caller_run.yaml")
    holds(isinstance(run, dict) and run.get("seed") == "run", "f10_x_caller_run.yaml is the run file")
    holds([s["id"] for s in run["steps"]] == ["admitted", "none", "stranger", "bypass"], "the run names its four calls")
    holds([s["id"] for s in run["before_the_calls"]] == ["callers", "deploy", "credential"], "the run names its three preconditions")
    assert run["observed"] is not None, "seed run: the run has not been made"
