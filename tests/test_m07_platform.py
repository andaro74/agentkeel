"""The platform's side of an upgrade: model-watch, the retirement, the registry and the construct (SPEC/07 §6).

`tests/test_m07_readers.py` holds the token, the grant and the platform upgrade. These hold what opens
the other two kinds of pull request and what retires an agent. Nothing here calls AWS, a model or
GitHub: Bedrock, DynamoDB and GitHub are stand-ins, and no pull request is opened.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts import model_watch, platform_check, registry, retire_agent
from src.verdict import ROOT

MANIFEST_TEXT = (ROOT / model_watch.MANIFEST).read_text(encoding="utf-8")
MANIFEST = yaml.safe_load(MANIFEST_TEXT)
PIN = MANIFEST["model"]["id"]
HAIKU = MANIFEST["pinned_roles"]["m04_cheaper_swap"]
BASE = "b" * 40
RUN = "https://github.com/andaro74/agentkeel/actions/runs/1"


def lifecycle(**models: dict[str, Any]) -> dict[str, Any]:
    seen = {PIN: {"status": "ACTIVE", "endOfLifeTime": None, "error": None},
            HAIKU["id"]: {"status": "ACTIVE", "endOfLifeTime": None, "error": None}}  # fmt: skip
    return {"read_at": "2026-10-02T11:12:00Z", "region": "us-west-2", "models": {**seen, **models}}


# --- model-watch: what it would open ----------------------------------------------------


def test_the_candidate_is_the_one_the_threshold_owner_named_in_the_run_file():
    assert model_watch.candidate_role() == "m04_cheaper_swap"
    assert MANIFEST["pinned_roles"]["m04_cheaper_swap"]["id"].startswith("anthropic.claude-haiku-4-5")


def test_today_model_watch_proposes_the_swap_to_haiku_4_5_and_writes_no_date():
    """As read on 2026-10-02: both models ACTIVE, neither with an end-of-life date."""
    dated, swap = model_watch.plan(MANIFEST_TEXT, lifecycle(), "m04_cheaper_swap", BASE, RUN)
    assert dated["open"] is False and "no end-of-life date; nothing is written" in dated["why"]
    assert swap["open"] is True and swap["branch"] == "model-watch/m04_cheaper_swap" and swap["base"] == BASE
    after = yaml.safe_load(swap["files"][model_watch.MANIFEST])
    assert after["model"] == {f: HAIKU[f] for f in model_watch.PIN_FIELDS}
    assert {k: v for k, v in after.items() if k != "model"} == {k: v for k, v in MANIFEST.items() if k != "model"}
    # Four lines move and every comment stays.
    before_lines, after_lines = MANIFEST_TEXT.splitlines(), swap["files"][model_watch.MANIFEST].splitlines()
    assert len(before_lines) == len(after_lines)
    assert sum(a != b for a, b in zip(before_lines, after_lines, strict=True)) == 3  # region is the same
    assert model_watch.entry_errors(swap, MANIFEST_TEXT, "m04_cheaper_swap") == []


@pytest.mark.parametrize("role, models, said", [
    (None, {}, "names no candidate"),
    ("m04_no_such_role", {}, "is not a whole pin"),
    ("baseline", {}, "is not a whole pin"),  # the control's pin has no version or region
    ("m04_cheaper_swap", {HAIKU["id"]: {"status": "LEGACY", "endOfLifeTime": None, "error": None}}, "does not call"),
    ("m04_cheaper_swap", {HAIKU["id"]: {"status": None, "endOfLifeTime": None, "error": "AccessDeniedException"}}, "AccessDeniedException"),
])  # fmt: skip
def test_no_swap_is_proposed_without_a_named_whole_active_candidate(role, models, said):
    _dated, swap = model_watch.plan(MANIFEST_TEXT, lifecycle(**models), role, BASE, RUN)
    assert swap["open"] is False and said in swap["why"] and "files" not in swap


def test_no_swap_is_proposed_to_the_pin_refagent_already_has():
    swapped = model_watch.plan(MANIFEST_TEXT, lifecycle(), "m04_cheaper_swap", BASE, RUN)[1]["files"][model_watch.MANIFEST]
    _dated, again = model_watch.plan(swapped, lifecycle(), "m04_cheaper_swap", BASE, RUN)
    assert again["open"] is False and "already pinned_roles.m04_cheaper_swap" in again["why"]


@pytest.mark.parametrize("stated, end, opens, said", [
    (None, "2027-03-01T08:00:00+00:00", True, "Bedrock's end-of-life"),  # a date where there was none
    ("2027-06-01", "2027-03-01T08:00:00+00:00", True, "Bedrock's end-of-life"),  # earlier: a tightening
    ("2027-03-01", "2027-03-01T08:00:00+00:00", False, "already says"),
    ("2027-01-01", "2027-03-01T08:00:00+00:00", False, "later than the manifest's"),  # later is two keys
    ("2027-01-01", None, False, "a person's to clear, with two keys"),  # clearing is two keys
    (None, None, False, "no end-of-life date; nothing is written"),  # a null to a null opens nothing
])  # fmt: skip
def test_deprecated_after_is_written_from_bedrock_and_never_relaxed_by_the_platform(stated, end, opens, said):
    text = MANIFEST_TEXT if stated is None else MANIFEST_TEXT.replace("deprecated_after: null", f'deprecated_after: "{stated}"')
    dated, _swap = model_watch.plan(text, lifecycle(**{PIN: {"status": "ACTIVE", "endOfLifeTime": end, "error": None}}),
                                    None, BASE, RUN)  # fmt: skip
    assert dated["open"] is opens and said in dated["why"], dated
    if opens:
        assert yaml.safe_load(dated["files"][model_watch.MANIFEST])["deprecated_after"] == "2027-03-01"
        assert dated["branch"] == "model-watch/deprecated-after-2027-03-01"
        assert model_watch.entry_errors(dated, text, None) == []


def test_a_lifecycle_that_was_not_read_writes_nothing():
    dated, _ = model_watch.plan(MANIFEST_TEXT, lifecycle(**{PIN: {"status": None, "endOfLifeTime": None, "error": "Throttled"}}),
                                None, BASE, RUN)  # fmt: skip
    assert dated["open"] is False and "was not read (Throttled)" in dated["why"]


def test_bedrock_is_asked_once_per_pinned_model_and_an_error_is_recorded_not_raised():
    class Bedrock:
        def __init__(self) -> None:
            self.asked: list[str] = []

        def get_foundation_model(self, modelIdentifier):  # noqa: N803 - boto3's name
            self.asked.append(modelIdentifier)
            if "llama" in modelIdentifier:
                raise RuntimeError("AccessDeniedException")
            return {"modelDetails": {"modelLifecycle": {"status": "ACTIVE", "endOfLifeTime": date(2027, 3, 1)}}}

    ids = model_watch.pinned_ids(MANIFEST)
    assert ids[0] == PIN and len(ids) == len(set(ids)) and HAIKU["id"] in ids
    client = Bedrock()
    seen = model_watch.read_lifecycle(ids, client)
    assert client.asked == ids
    assert seen["models"][PIN] == {"status": "ACTIVE", "endOfLifeTime": "2027-03-01", "error": None}
    assert seen["models"]["meta.llama3-1-8b-instruct-v1:0"]["error"].startswith("RuntimeError")


# --- model-watch: what the keyed job will not open -----------------------------------------


def swap_entry() -> dict[str, Any]:
    return model_watch.plan(MANIFEST_TEXT, lifecycle(), "m04_cheaper_swap", BASE, RUN)[1]


@pytest.mark.parametrize("change, said", [
    (lambda e: e.update(repository="agentkeel-studio/owner-check"), "is not andaro74/agentkeel"),
    (lambda e: e["files"].update({".github/workflows/evals.yml": "x"}), "and nothing else"),
    (lambda e: e.update(files={"thresholds.yaml": "x"}), "and nothing else"),
    (lambda e: e.update(role="m04_breaking_swap", branch="model-watch/m04_breaking_swap"), "is not the one"),
    (lambda e: e.update(kind="anything"), "is not one model-watch opens"),
    (lambda e: e["files"].update({model_watch.MANIFEST: e["files"][model_watch.MANIFEST].replace("daily_usd: 10", "daily_usd: 1000")}),
     "this moves daily_usd, model"),
    (lambda e: e["files"].update({model_watch.MANIFEST: MANIFEST_TEXT.replace(PIN, "meta.llama3-1-8b-instruct-v1:0")}),
     "sets `model` to pinned_roles.m04_cheaper_swap's pin"),
])  # fmt: skip
def test_the_keyed_job_holds_the_plan_to_mains_own_manifest_and_candidate(change, said):
    entry = swap_entry()
    change(entry)
    errors = model_watch.entry_errors(entry, MANIFEST_TEXT, "m04_cheaper_swap")
    assert any(said in e for e in errors), errors


def test_a_plan_that_delays_deprecated_after_is_refused_by_the_keyed_job():
    text = MANIFEST_TEXT.replace("deprecated_after: null", 'deprecated_after: "2027-01-01"')
    entry = {"kind": "deprecated_after", "repository": model_watch.REPOSITORY, "branch": "model-watch/deprecated-after-2027-06-01",
             "files": {model_watch.MANIFEST: text.replace("2027-01-01", "2027-06-01")}}  # fmt: skip
    assert any("two keys" in e for e in model_watch.entry_errors(entry, text, None))


def test_the_drafted_ruling_is_a_draft_a_gate_would_refuse_and_names_its_pull_request():
    from src.validate import checks

    entry = swap_entry()
    text = model_watch.draft_ruling(entry, 41)
    front = checks.front_matter(text)
    assert front == {"ruling": "model-watch-m04-cheaper-swap", "seat": "Threshold Owner", "authorises": [model_watch.MANIFEST],
                     "evidence": ["SPEC/00-overview.md#8-M07", "SPEC/07-upgrade-retire-surfaces.md", model_watch.CANDIDATE_FILE],
                     "pr": 41}  # fmt: skip
    body = text.split("---", 2)[2]
    assert not any(line.startswith("Ruled by") for line in text.splitlines())  # item 10; security-reviewer 8
    assert any(line.startswith("Drafted ") for line in body.splitlines())  # cold-review-ruling refuses it until a seat rules
    assert HAIKU["id"] in text and RUN in text
    assert model_watch.ruling_slug(entry) == "model-watch-m04-cheaper-swap"
    # A field that would smuggle a ruled line in is refused, not written.
    with pytest.raises(model_watch.Refused, match="a gate reads as ruled"):
        model_watch.draft_ruling({**entry, "run_url": "x).\nRuled by nobody"}, 41)


def test_model_watch_opens_the_swap_then_commits_the_ruling_draft_as_the_app(monkeypatch):
    from scripts import platform_pr

    calls: list[tuple[str, Any]] = []
    monkeypatch.setattr(platform_check, "load_grant", lambda root=None: {"agentkeel-upgrades": {"app_id": 5200001}})
    monkeypatch.setattr(platform_check, "app_token", lambda app, account, key, repository, named: calls.append(
        ("token", (app, account, repository, named))) or "t")  # fmt: skip
    monkeypatch.setattr(platform_check, "gh", lambda path, **k: {"default_branch": "main"})
    monkeypatch.setattr(platform_pr, "open_draft", lambda repository, base_branch, base, branch, files, **k: calls.append(
        ("open", (repository, base_branch, base, branch, sorted(files), k["title"]))) or {"number": 41})  # fmt: skip
    monkeypatch.setattr(platform_pr, "add_commit", lambda repository, branch, files, message: calls.append(
        ("ruling", (branch, sorted(files)))) or "c" * 40)  # fmt: skip
    results = model_watch.open_all(model_watch.plan(MANIFEST_TEXT, lifecycle(), "m04_cheaper_swap", BASE, RUN), "key")
    assert [name for name, _ in calls] == ["token", "open", "ruling"]
    assert calls[0][1] == (5200001, "andaro74", "andaro74/agentkeel", "open")  # this repository, the `open` set, no other
    assert calls[1][1] == ("andaro74/agentkeel", "main", BASE, "model-watch/m04_cheaper_swap", [model_watch.MANIFEST],
                           "model-watch: refagent's pin to pinned_roles.m04_cheaper_swap")  # fmt: skip
    assert calls[2][1] == ("model-watch/m04_cheaper_swap", ["milestones/M07/rulings/model-watch-m04-cheaper-swap.md"])
    assert results == [{"kind": "swap", "opened": True, "number": 41, "ruling": "c" * 40}]


# --- the retirement's pull request ------------------------------------------------------------

AGENT_MANIFEST = (ROOT / "tests/fixtures/m07/s1-platform-upgrade/agent/manifest.yaml").read_text(encoding="utf-8")
AGENT = {"repository": "agentkeel-studio/premiere-desk", "repository_id": "9", "commit": "c" * 40, "name": "premiere-desk",
         "rollout": "all-at-once"}  # fmt: skip


def manifest_reader(text: str = AGENT_MANIFEST):
    return lambda repository, commit: text


def test_a_dispatched_retirement_is_one_line_in_one_file():
    (entry,) = retire_agent.plan([AGENT], "premiere-desk", manifest_reader())
    assert entry["open"] is True and entry["branch"] == "platform-retire" and sorted(entry["files"]) == ["manifest.yaml"]
    before, after = AGENT_MANIFEST.splitlines(), entry["files"]["manifest.yaml"].splitlines()
    assert [(a, b) for a, b in zip(before, after, strict=True) if a != b] == [("rollout: all-at-once", "rollout: retired")]
    assert "It is one-way" in entry["body"] and "the owner dispatched" in entry["why"]
    assert retire_agent.entry_errors(entry, "agentkeel-studio", AGENT_MANIFEST) == []


@pytest.mark.parametrize("agents, name, said", [
    ([AGENT], "no-such-agent", "no agent named no-such-agent"),
    ([{**AGENT, "rollout": "retired"}], "premiere-desk", "already retired"),
    ([{**AGENT, "name": "refagent"}], "refagent", "never retired by this path"),
])  # fmt: skip
def test_no_retirement_is_opened_for_an_agent_that_is_not_there_is_retired_or_is_refagent(agents, name, said):
    (entry,) = retire_agent.plan(agents, name, manifest_reader(AGENT_MANIFEST.replace("premiere-desk", name)))
    assert entry["open"] is False and said in entry["why"]


def test_a_pin_within_30_days_of_its_end_is_due_and_one_further_off_is_not():
    today = date(2026, 10, 2)
    due = AGENT_MANIFEST + "deprecated_after: 2026-10-14\n"
    (entry,) = retire_agent.plan([AGENT], None, manifest_reader(due), today)
    assert entry["open"] is True and "`deprecated_after` is 2026-10-14" in entry["why"]
    assert retire_agent.plan([AGENT], None, manifest_reader(AGENT_MANIFEST + "deprecated_after: 2027-10-14\n"), today) == []
    assert retire_agent.plan([AGENT], None, manifest_reader(), today) == []  # no date: not due
    assert retire_agent.deprecating({"deprecated_after": "soon"}, today) is None


@pytest.mark.parametrize("change, said", [
    (lambda e: e.update(repository="andaro74/agentkeel"), "not an agent repository"),
    (lambda e: e.update(repository="agentkeel-studio/agent-template"), "not an agent repository"),
    (lambda e: e.update(name="refagent"), "is not one the platform retires"),
    (lambda e: e["files"].update({"agent.py": "x"}), "manifest.yaml and nothing else"),
    (lambda e: e.update(branch="main"), "is not platform-retire"),
    (lambda e: e["files"].update({"manifest.yaml": e["files"]["manifest.yaml"].replace("security: andaro74", "security: x")}),
     "this moves rollout, seats"),
    (lambda e: e["files"].update({"manifest.yaml": AGENT_MANIFEST}), "this moves nothing"),
])  # fmt: skip
def test_the_keyed_job_opens_a_retirement_only_for_rollout_retired_and_nothing_else(change, said):
    (entry,) = retire_agent.plan([AGENT], "premiere-desk", manifest_reader())
    change(entry)
    errors = retire_agent.entry_errors(entry, "agentkeel-studio", AGENT_MANIFEST)
    assert any(said in e for e in errors), errors


# --- after the deletion ----------------------------------------------------------------------------


class Gone(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class Runtime:
    def __init__(self, raises: Exception | None = None) -> None:
        self.raises, self.asked = raises, []

    def invoke_agent_runtime(self, agentRuntimeArn, payload):  # noqa: N803 - boto3's names
        self.asked.append(agentRuntimeArn)
        if self.raises:
            raise self.raises
        return {"response": b'{"text": "still here"}'}


def test_the_one_invocation_after_the_deletion_is_written_raw_and_never_raises():
    arn = "arn:aws:bedrock-agentcore:us-west-2:1:runtime/agentkeel_premiere_desk-x"
    gone = retire_agent.invoke(arn, Runtime(Gone("ResourceNotFoundException")))
    assert gone["answered"] is False and gone["error"] == "ResourceNotFoundException" and gone["arn"] == arn
    denied = retire_agent.invoke(arn, Runtime(Gone("AccessDeniedException")))
    assert denied["answered"] is False and denied["error"] == "AccessDeniedException"
    answered = retire_agent.invoke(arn, Runtime())
    assert answered["answered"] is True and answered["error"] is None
    assert retire_agent.invoke(arn, Runtime(TimeoutError("slow")))["error"] == "TimeoutError"
    document = retire_agent.record("premiere-desk", AGENT["repository"], AGENT["commit"], arn, RUN, gone)
    assert document["what"] == "agent retired" and document["invocation"] == gone and "its key and alias" in document["kept"]
    with pytest.raises(retire_agent.Refused):
        retire_agent.record("refagent", "andaro74/agentkeel", "c" * 40, arn, RUN, gone)


# --- the registry ------------------------------------------------------------------------------------


class Table:
    """DynamoDB's get_item and conditional put_item on one key, as the registry uses them from M07 PR 2."""

    def __init__(self) -> None:
        self.items: dict[str, dict[str, Any]] = {}

    def get_item(self, TableName, Key, ConsistentRead):  # noqa: N803 - boto3's names
        item = self.items.get(Key["name"]["S"])
        return {"Item": item} if item else {}

    def put_item(self, TableName, Item, ConditionExpression, ExpressionAttributeValues=None,  # noqa: N803
                 ExpressionAttributeNames=None):  # noqa: N803
        from botocore.exceptions import ClientError

        # DynamoDB refuses a name the expression does not use; so does this.
        assert (ExpressionAttributeNames is None) == ("#n" not in ConditionExpression), ConditionExpression
        held = self.items.get(Item["name"]["S"])
        same = ExpressionAttributeValues is not None and held and held["repository_id"] == ExpressionAttributeValues[":id"]
        if (held and not same) or (not held and "attribute_not_exists" not in ConditionExpression):
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "PutItem")
        self.items[Item["name"]["S"]] = Item


ARN = "arn:aws:bedrock-agentcore:us-west-2:1:runtime/agentkeel_premiere_desk-x"


def deployed_table() -> Table:
    table = Table()
    assert registry.claim(table, "premiere-desk", "org/a", "111")[0] == 0
    assert registry.write(table, "premiere-desk", "org/a", "111", "a" * 40, "7", "first")[0] == 0
    return table


def test_a_retirement_keeps_the_arn_then_writes_retired_at_on_a_row_that_stays():
    table = deployed_table()
    assert registry.retiring(table, "premiere-desk", "111", ARN) == (0, ARN)
    # A rerun after a failure: the stack no longer gives the ARN, and the row still does.
    assert registry.retiring(table, "premiere-desk", "111", None) == (0, ARN)
    code, said = registry.retire(table, "premiere-desk", "111", "c" * 40, "9")
    row = table.items["premiere-desk"]
    assert code == 0 and row["retired_at"]["S"] in said and row["retired_commit"]["S"] == "c" * 40
    assert row["commit_sha"]["S"] == "a" * 40 and row["repository"]["S"] == "org/a"  # the row stays as it was
    assert registry.retiring(table, "premiere-desk", "111", None)[0] == 4  # nothing left to do
    assert registry.retire(table, "premiere-desk", "111", "c" * 40, "9")[0] == 0  # and saying so twice changes nothing
    assert table.items["premiere-desk"]["retired_at"] == row["retired_at"]


@pytest.mark.parametrize("name, repository_id, said", [
    ("refagent", "111", "never retired by this path"),
    ("premiere-desk", "222", "held by repository 111"),
    ("never-deployed", "111", "no registry row"),
])  # fmt: skip
def test_refagent_another_repositorys_agent_and_a_name_never_deployed_are_not_retired(name, repository_id, said):
    table = deployed_table()
    table.items["refagent"] = {"name": {"S": "refagent"}, "repository_id": {"S": "111"}}
    for code, why in (registry.retiring(table, name, repository_id, ARN), registry.retire(table, name, repository_id, "c" * 40, "9")):
        assert code == 3 and said in why
    assert "retired_at" not in table.items["premiere-desk"] and "retiring_arn" not in table.items["premiere-desk"]


def test_a_retirement_with_no_arn_anywhere_is_refused_before_anything_is_removed():
    code, why = registry.retiring(deployed_table(), "premiere-desk", "111", None)
    assert code == 3 and "ARN is not known" in why


def test_the_row_says_whose_answer_record_stands():
    """Re-read of 52ebd57 (M07 PR 1): on a 412 the row named this run against a record another run wrote."""
    table = deployed_table()
    assert table.items["premiere-desk"]["answer_put"]["S"] == "first"
    assert registry.write(table, "premiere-desk", "org/a", "111", "a" * 40, "8", "stood")[0] == 0
    assert table.items["premiere-desk"]["answer_put"]["S"] == "stood" and table.items["premiere-desk"]["deploy_run_id"]["S"] == "8"
    assert registry.write(table, "premiere-desk", "org/a", "111", "a" * 40, "9")[0] == 0  # refagent's row says nothing of it
    assert "answer_put" not in table.items["premiere-desk"]


# --- deployable: a retired head is retired, not deployed -------------------------------------------


def test_a_head_that_says_retired_is_in_the_list_to_retire_and_never_in_the_list_to_deploy(monkeypatch, tmp_path):
    heads = [{"repository": "org/a", "repository_id": "111", "commit": "a" * 40, "name": "premiere-desk", "rollout": "retired"},
             {"repository": "org/b", "repository_id": "222", "commit": "b" * 40, "name": "second-desk", "rollout": "all-at-once"},
             {"repository": "org/c", "repository_id": "333", "commit": "c" * 40, "name": "never-deployed", "rollout": "retired"}]  # fmt: skip
    monkeypatch.setattr(platform_check, "identity", lambda: ("org", 5144253))
    monkeypatch.setattr(platform_check, "deployable", lambda org, app: [dict(h) for h in heads])
    table = deployed_table()
    monkeypatch.setattr(registry, "client", lambda: table)
    out, retiring = tmp_path / "agents.json", tmp_path / "retiring.json"
    assert platform_check.main(["deployable", "--skip-deployed", "--out", str(out), "--retiring", str(retiring)]) == 0
    assert [a["name"] for a in json.loads(out.read_text(encoding="utf-8"))] == ["second-desk"]
    assert [a["name"] for a in json.loads(retiring.read_text(encoding="utf-8"))] == ["premiere-desk"]  # no row: nothing to retire
    # Once the row says retired_at, there is nothing left to retire either.
    registry.retiring(table, "premiere-desk", "111", ARN)
    registry.retire(table, "premiere-desk", "111", "a" * 40, "9")
    assert platform_check.main(["deployable", "--skip-deployed", "--out", str(out), "--retiring", str(retiring)]) == 0
    assert json.loads(retiring.read_text(encoding="utf-8")) == []
    # Without the registry (no --skip-deployed) a retired head is still not in the list that is deployed.
    assert platform_check.main(["deployable", "--out", str(out)]) == 0
    assert [a["name"] for a in json.loads(out.read_text(encoding="utf-8"))] == ["second-desk"]


# --- the template's version, and the manifest's two new values -------------------------------------


def test_the_templates_version_is_the_tag_head_carries_else_the_short_commit(tmp_path, monkeypatch):
    import subprocess

    from scripts import make_template

    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q")
    (tmp_path / "f").write_text("x", encoding="utf-8")
    git("add", "f")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "one")
    short = make_template.platform_version(tmp_path)
    assert short == git("rev-parse", "--short=12", "HEAD") and len(short) == 12
    git("tag", "not-a-milestone")
    assert make_template.platform_version(tmp_path) == short
    git("tag", "m07")
    assert make_template.platform_version(tmp_path) == "m07"
    doc = yaml.safe_load(make_template.manifest("example-agent", "m07"))
    assert doc["platform_version"] == "m07" and doc["rollout"] == "all-at-once"


@pytest.mark.parametrize("field, value, valid", [
    ("platform_version", "m07", True), ("platform_version", "16d9f84", True), ("platform_version", "16d9f84aaa57", True),
    ("platform_version", "main", False), ("platform_version", "M07", False), ("platform_version", "abc", False),
    ("rollout", "retired", True), ("rollout", "all-at-once", True), ("rollout", "paused", False),
])  # fmt: skip
def test_the_manifest_schema_takes_a_tag_or_a_commit_and_a_retired_rollout(field, value, valid):
    from src import manifest as manifest_module

    errors = manifest_module.schema_errors({**MANIFEST, field: value})
    assert (errors == []) is valid, errors


# --- the construct: a retired agent's stack has no runtime ---------------------------------------------


def synth(tmp_path: Path, rollout: str, name: str = "premiere-desk") -> dict[str, Any]:
    import aws_cdk as cdk
    from aws_cdk.assertions import Template

    from infra.construct import governed_agent
    from infra.construct.governed_agent import GovernedAgent

    bundle = tmp_path / "agents" / name
    bundle.mkdir(parents=True)
    doc = {**MANIFEST, "name": name, "rollout": rollout}
    doc.pop("pinned_roles", None)
    (bundle / "manifest.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    old = governed_agent.ROOT
    governed_agent.ROOT = tmp_path
    try:
        app = cdk.App(outdir=str(tmp_path / "cdk.out"))
        stack = cdk.Stack(app, "T", env=cdk.Environment(account="111111111111", region="us-west-2"),
                          synthesizer=cdk.LegacyStackSynthesizer())  # fmt: skip
        agent = GovernedAgent(stack, "Agent", bundle=f"agents/{name}")
        template = Template.from_stack(stack).to_json()
    finally:
        governed_agent.ROOT = old
    return {"template": template, "agent": agent}


def types(template: dict[str, Any]) -> list[str]:
    return sorted({resource["Type"] for resource in template["Resources"].values()})


def test_a_retired_agents_stack_is_the_same_stack_without_its_runtime(tmp_path):
    live = synth(tmp_path / "live", "all-at-once")
    retired = synth(tmp_path / "retired", "retired")
    runtime = "AWS::BedrockAgentCore::Runtime"
    assert runtime in types(live["template"]) and live["agent"].runtime is not None
    assert runtime not in types(retired["template"]) and retired["agent"].runtime is None and retired["agent"].retired
    assert [t for t in types(live["template"]) if t != runtime] == types(retired["template"])  # nothing else goes
    assert not any(t.startswith("AWS::IAM::") and t not in types(live["template"]) for t in types(retired["template"]))  # no new IAM
