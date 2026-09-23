"""validate's M02 PR 2 checks (SPEC/02 §6): CODEOWNERS, relaxes, edges, golden ids, semver, the live ruleset."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from src.validate import checks, codeowners, edges, golden_ids, ruleset, semver
from src.verdict import ROOT

REFAGENT = ROOT / "agents" / "refagent" / "manifest.yaml"
HELPER = ROOT / "agents" / "ratings-helper" / "manifest.yaml"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A repository holding this tree's manifests, thresholds, goldens and CODEOWNERS, committed once."""
    root = tmp_path / "tree"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    for rel in ("thresholds.yaml", ".github/CODEOWNERS", "agents/refagent/manifest.yaml", "agents/ratings-helper/manifest.yaml"):
        write(root, rel, (ROOT / rel).read_text(encoding="utf-8"))
    shutil.copytree(ROOT / "agents" / "refagent" / "tools", root / "agents" / "refagent" / "tools")
    shutil.copytree(ROOT / "evals" / "goldens", root / "evals" / "goldens")
    for rel in sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / ".claude" / "agents").glob("*.md")):
        write(root, rel, (ROOT / rel).read_text(encoding="utf-8"))
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    git(root, "branch", "-q", "-M", "main")
    git(root, "remote", "add", "origin", str(root))
    git(root, "fetch", "-q", "origin")
    return root


def real(login: str) -> tuple[bool, str]:
    return True, "200"


# --- CODEOWNERS ----------------------------------------------------------------


def test_this_repository_passes_with_the_login_taken_as_read():
    assert codeowners.check(ROOT, lookup=real) == []


def test_a_file_no_line_matches_fails(tree):
    write(tree, "stray/x.txt", "x\n")
    git(tree, "add", "-A")
    assert any("stray/x.txt: matches no line" in e for e in codeowners.check(tree, lookup=real))


def test_a_file_matching_two_seats_fails(tree):
    path = tree / ".github" / "CODEOWNERS"
    path.write_text(path.read_text(encoding="utf-8") + "\n# seat: Product\n/thresholds.yaml @andaro74\n", encoding="utf-8")
    assert any("thresholds.yaml: matches lines from 2 seats" in e for e in codeowners.check(tree, lookup=real))


def test_an_agent_prompt_under_the_wrong_seat_fails(tree):
    path = tree / ".github" / "CODEOWNERS"
    text = path.read_text(encoding="utf-8").replace("# seat: Tool Owner\n/.claude/agents/tool-owner.md", "# seat: Product\n/.claude/agents/tool-owner.md")
    path.write_text(text, encoding="utf-8")
    assert any("tool-owner.md: front matter says seat Tool Owner" in e for e in codeowners.check(tree, lookup=real))


def test_a_login_the_api_does_not_answer_for_fails(tree):
    errors = codeowners.check(tree, lookup=lambda login: (False, "404"))
    assert errors == [".github/CODEOWNERS: @andaro74 is not a GitHub login the API answers for (GET /users/andaro74: 404)"]


def test_the_seat_table_needs_every_seat(tree):
    path = tree / ".github" / "CODEOWNERS"
    text = path.read_text(encoding="utf-8").replace("# seat: Rule Owner\n/rules/ @andaro74\n/agents/*/rules/ @andaro74\n", "")
    path.write_text(text.replace("# seat: Rule Owner\n/.claude/agents/rule-owner.md @andaro74\n", ""), encoding="utf-8")
    assert any("no line for ['Rule Owner']" in e for e in codeowners.check(tree, lookup=real))


# --- relaxes: on every bar -------------------------------------------------------


def test_this_repository_has_relaxes_on_every_bar():
    assert checks.check_relaxes(ROOT) == []


def test_a_bar_without_an_entry_and_an_entry_without_a_bar_fail(tree):
    thresholds = yaml.safe_load((tree / "thresholds.yaml").read_text(encoding="utf-8"))
    thresholds["cost_cap"]["seconds_per_run"] = 60
    thresholds["relaxes"]["floor.min_pass"] = "sideways"
    (tree / "thresholds.yaml").write_text(yaml.safe_dump(thresholds), encoding="utf-8")
    errors = checks.check_relaxes(tree)
    assert "thresholds.yaml: bar cost_cap.seconds_per_run has no relaxes: entry" in errors
    assert "thresholds.yaml: relaxes: names floor.min_pass, which is not a bar" in errors
    assert "thresholds.yaml: relaxes.floor.min_pass is 'sideways', not up or down" in errors


# --- edges, cycles, ceilings ----------------------------------------------------


def manifest(tree: Path, name: str, **fields) -> None:
    path = tree / "agents" / name / "manifest.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else yaml.safe_load(REFAGENT.read_text(encoding="utf-8")) | {"name": name}
    doc.update(fields)
    write(tree, f"agents/{name}/manifest.yaml", yaml.safe_dump(doc))


def test_this_repository_has_no_edge_and_passes():
    assert edges.check(ROOT) == []


def test_the_callers_side_alone_is_one_sided(tree):
    manifest(tree, "refagent", may_call=["ratings-helper@v1"])
    errors = edges.check(tree)
    assert any("may_call ratings-helper@v1" in e and "may_be_called_by does not name refagent" in e for e in errors), errors


def test_the_callees_side_alone_is_one_sided(tree):
    manifest(tree, "ratings-helper", may_be_called_by=["refagent@v1"])
    errors = edges.check(tree)
    assert any("may_be_called_by refagent@v1" in e and "may_call does not name ratings-helper" in e for e in errors), errors


def test_a_callee_that_does_not_exist_is_one_sided(tree):
    manifest(tree, "refagent", may_call=["nobody@v1"])
    assert any("no agents/nobody/manifest.yaml exists" in e for e in edges.check(tree))


def test_both_sides_pass_and_a_cycle_fails(tree):
    manifest(tree, "refagent", may_call=["ratings-helper@v1"])
    manifest(tree, "ratings-helper", may_be_called_by=["refagent@v1"])
    assert edges.check(tree) == []
    manifest(tree, "ratings-helper", may_call=["refagent@v1"])
    manifest(tree, "refagent", may_be_called_by=["ratings-helper@v1"])
    assert any("closes a cycle" in e and "refagent -> ratings-helper" in e for e in edges.check(tree))


def test_ceilings_over_the_bounds_fail_and_an_edge_without_ceilings_fails(tree):
    manifest(tree, "refagent", ceilings={"concurrency": 2, "rps_per_edge": 1, "depth": 2, "fan_out": 4})
    assert any("ceilings.fan_out 4 is over the bound 3" in e for e in edges.check(tree))
    manifest(tree, "refagent", may_call=["ratings-helper@v1"], ceilings=None)
    manifest(tree, "ratings-helper", may_be_called_by=["refagent@v1"])
    assert any("declares an edge and no ceilings" in e for e in edges.check(tree))


# --- golden ids ---------------------------------------------------------------------


def test_this_repository_passes_against_origin_main():
    assert golden_ids.check(ROOT) == []


def test_a_deleted_id_fails_retired_or_not(tree):
    (tree / "evals" / "goldens" / "v1" / "g-005.yaml").unlink()
    errors = golden_ids.check(tree, "origin/main")
    assert any("g-005 is on" in e and "retired is null" in e for e in errors), errors
    path = tree / "evals" / "goldens" / "v1" / "g-006.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("retired: null", "retired: M01"), encoding="utf-8")
    git(tree, "add", "-A")
    git(tree, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "retire")
    git(tree, "fetch", "-q", "origin")
    path.unlink()
    assert any("g-006" in e and "its file stays" in e for e in golden_ids.check(tree, "origin/main"))


def test_the_burned_id_is_refused_anywhere(tree):
    write(tree, "evals/goldens/v1/g-099.yaml", (tree / "evals" / "goldens" / "v1" / "g-005.yaml").read_text(encoding="utf-8").replace("g-005", "g-099"))
    assert any("g-099 is a burned id" in e for e in golden_ids.check(tree, "origin/main"))


def test_no_base_is_an_error_not_a_pass(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    git(root, "init", "-q")
    assert golden_ids.check(root) == ["evals/goldens/: no origin/main to compare the ids against (fetch it)"]


# --- computed semver ------------------------------------------------------------------


def tool(tree: Path) -> Path:
    return tree / "agents" / "refagent" / "tools" / "check_availability.json"


def test_this_repository_passes_semver():
    assert semver.check(ROOT) == []


def test_a_schema_change_without_a_major_bump_fails(tree):
    schema = json.loads(tool(tree).read_text(encoding="utf-8"))
    schema["input"]["properties"]["extra"] = {"type": "string"}
    tool(tree).write_text(json.dumps(schema), encoding="utf-8")
    assert any("input or output changed, which is a major bump" in e for e in semver.check(tree, "origin/main"))
    schema["version"] = "2.0.0"
    tool(tree).write_text(json.dumps(schema), encoding="utf-8")
    manifest(tree, "refagent", version="1.0.0")
    assert any("a tool schema took a major bump" in e for e in semver.check(tree, "origin/main"))
    manifest(tree, "refagent", version="2.0.0")
    assert semver.check(tree, "origin/main") == []


def test_an_edge_change_without_a_major_bump_fails_and_an_edge_names_the_callees_major(tree):
    manifest(tree, "refagent", may_call=["ratings-helper@v1"])
    manifest(tree, "ratings-helper", may_be_called_by=["refagent@v1"])
    errors = semver.check(tree, "origin/main")
    assert any("agents/refagent/manifest.yaml: an edge changed, which is a major bump" in e for e in errors)
    manifest(tree, "refagent", version="2.0.0")
    manifest(tree, "ratings-helper", version="2.0.0", may_be_called_by=["refagent@v2"])
    assert any("may_call ratings-helper@v1 names major 1, and agents/ratings-helper/manifest.yaml is at major 2" in e
               for e in semver.check(tree, "origin/main"))  # fmt: skip


def test_a_version_moved_down_fails(tree):
    manifest(tree, "ratings-helper", version="0.9.0")
    assert any("version moved down, 1.0.0 -> 0.9.0" in e for e in semver.check(tree, "origin/main"))


# --- the live ruleset ---------------------------------------------------------------------


EXPORT = json.loads((ROOT / "infra" / "ruleset" / "main.json").read_text(encoding="utf-8"))


def test_equal_on_what_the_ruleset_does_passes_whatever_the_timestamps_say():
    live = {**EXPORT, "updated_at": "2099-01-01T00:00:00Z", "node_id": "other", "_links": {}}
    assert ruleset.check(ROOT, fetcher=lambda repo, i: (live, "200")) == []


def test_a_bypass_actor_on_the_live_ruleset_is_red():
    live = {**EXPORT, "bypass_actors": [{"actor_id": 1, "actor_type": "Integration", "bypass_mode": "always"}]}
    errors = ruleset.check(ROOT, fetcher=lambda repo, i: (live, "200"))
    assert any("bypass_actors differs" in e for e in errors) and any("somebody can bypass main" in e for e in errors)


def test_a_required_check_removed_from_the_live_ruleset_is_red():
    live = json.loads(json.dumps(EXPORT))
    for rule in live["rules"]:
        if rule["type"] == "required_status_checks":
            rule["parameters"]["required_status_checks"] = rule["parameters"]["required_status_checks"][:1]
    assert any("rules differs from the live ruleset" in e for e in ruleset.check(ROOT, fetcher=lambda repo, i: (live, "200")))


def test_a_bypass_list_the_caller_is_not_shown_is_an_error_not_a_pass():
    """Unauthenticated, GitHub omits bypass_actors (read 2026-09-22): that names the token, never "nobody bypasses"."""
    live = {k: v for k, v in EXPORT.items() if k != "bypass_actors"}
    errors = ruleset.check(ROOT, fetcher=lambda repo, i: (live, "200 with no token"))
    assert len(errors) == 1 and "not shown to this caller (200 with no token)" in errors[0]


def test_an_unreadable_ruleset_is_an_error_not_a_pass():
    errors = ruleset.check(ROOT, fetcher=lambda repo, i: (None, "403"))
    assert errors == ["infra/ruleset/main.json: the live ruleset 23685206 on andaro74/agentkeel could not be read (403); unread is not unchanged"]


def test_the_export_itself_must_say_nobody_bypasses(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "andaro74/agentkeel")
    write(tmp_path, "infra/ruleset/main.json", json.dumps({**EXPORT, "bypass_actors": [{"actor_id": 1}]}))
    errors = ruleset.check(tmp_path, fetcher=lambda repo, i: (EXPORT, "200"))
    assert any("infra/ruleset/main.json: bypass_actors is [{\"actor_id\": 1}], not []" in e for e in errors)


def test_an_edge_at_another_major_is_refused_by_the_edge_check_alone(tree):
    manifest(tree, "refagent", may_call=["ratings-helper@v2"])
    manifest(tree, "ratings-helper", may_be_called_by=["refagent@v1"])
    assert any("names major 2, and agents/ratings-helper/manifest.yaml is at major 1: not the same major" in e for e in edges.check(tree))


def test_a_removed_tool_schema_is_a_major_bump(tree):
    tool(tree).unlink()
    assert any("a tool schema took a major bump (agents/refagent/tools/check_availability.json (removed))" in e
               for e in semver.check(tree, "origin/main"))  # fmt: skip
    manifest(tree, "refagent", version="2.0.0")
    assert semver.check(tree, "origin/main") == []
