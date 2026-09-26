"""src/gates: ruling-cited and two-key (SPEC/02 §2, §6), on a small repository built for each test.

The seeded cases S1, S2, S3 and S5 are read by tests/test_m02_seeds.py on
this repository's own tree. These tests hold the rules the seeds do not
reach: the self-cover, CODEOWNERS read from the base and not the PR, a
manifest attributed field by field, the bot's exemption under
evals/history/, every uncovered path listed, and the rest of the closed
relaxation list.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from src.gates import Tree, changed, pr_number, ruling_cited, two_key
from src.verdict import ROOT

CODEOWNERS = """\
# seat: Product
/SPEC/ @someone
/milestones/ @someone
# seat: Data Owner
/evals/goldens/ @someone
# seat: Rule Owner
/rules/ @someone
/agents/*/rules/ @someone
# seat: Tool Owner
/agents/*/tools/ @someone
# seat: Threshold Owner
/thresholds.yaml @someone
# seat: Security
/.github/CODEOWNERS @someone
/.github/workflows/ @someone
# seat: Engineering
/src/ @someone
/agents/*/manifest.yaml @someone
/evals/history/ @someone
"""

THRESHOLDS = """\
cost_cap:
  tokens_per_run: 150000
floor:
  min_pass: 10
relaxes:
  cost_cap.tokens_per_run: up
  floor.min_pass: down
"""

MANIFEST = """\
name: refagent
model: {id: m, version: null, profile: us.m, region: us-west-2}
guardrail: {id: g, version: "3"}
may_call: []
may_be_called_by: []
memory: {retention_days: 30, ttl_days: 7, per_user: true}
seats: {product: null}
"""

GOLDEN = """\
id: g-010
kind: trap
question: q
expected:
  table_row: r-009
  clause_id: HS-4
  answer_fields:
    available: false
seat: Data Owner
added: M00
retired: null
"""

# An envelope in which g-010 passed for the agent (M01's PR 4 envelope).
PASSED_G010 = ROOT / "evals" / "history" / "e97125e970ccfc6d044612eb006cdbdbcdb99337.json"


def ruling(seat: str, authorises: list[str], pr: int | str = 12, body: str = "", keys: list[str] = (),
           deletes: list[str] = ()) -> str:  # fmt: skip
    lines = "\n".join(f"  - {a}" for a in authorises)
    extra = "".join(f"{field}:\n" + "".join(f"  - {v}\n" for v in values)
                    for field, values in (("keys", keys), ("deletes", deletes)) if values)  # fmt: skip
    return f"---\nruling: r\nseat: {seat}\nauthorises:\n{lines}\n{extra}evidence:\n  - x\npr: {pr}\n---\n\n{body}\n"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


class Repo:
    """A repository with one base commit, a `base` worktree of it, and edits made in the working tree."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.base = root.parent / "base"

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")

    def delete(self, path: str) -> None:
        (self.root / path).unlink()

    def commit_base(self) -> None:
        git(self.root, "add", "-A")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
        git(self.root, "worktree", "add", "-q", "--detach", str(self.base), "HEAD")

    def commit_as(self, author: str, message: str = "more") -> None:
        git(self.root, "add", "-A")
        git(self.root, "-c", f"user.name={author}", "-c", "user.email=a@b", "commit", "-q", "-m", message)

    def cited(self, pr: int = 12) -> str | None:
        return ruling_cited.refusal(self.root, base=self.base, pr=pr)

    def keys(self, pr: int = 12) -> str | None:
        return two_key.refusal(self.root, base=self.base, pr=pr)


@pytest.fixture
def repo(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    r = Repo(root)
    r.write(".github/CODEOWNERS", CODEOWNERS)
    r.write("thresholds.yaml", THRESHOLDS)
    r.write("agents/refagent/manifest.yaml", MANIFEST)
    r.write("evals/goldens/v1/g-010.yaml", GOLDEN)
    r.write("rules/one.md", "a rule\n")
    r.write("SPEC/00.md", "spec\n")
    (root / "evals" / "history").mkdir(parents=True)
    shutil.copy(PASSED_G010, root / "evals" / "history" / PASSED_G010.name)
    r.commit_base()
    yield r
    git(root, "worktree", "remove", "--force", str(r.base))


# --- what the two trees share ----------------------------------------------


def test_changed_paths_are_added_deleted_and_modified(repo):
    repo.write("SPEC/00.md", "changed\n")
    repo.write("SPEC/new.md", "new, untracked\n")
    repo.delete("rules/one.md")
    assert changed(Tree(repo.base), Tree(repo.root)) == ["SPEC/00.md", "SPEC/new.md", "rules/one.md"]


def test_a_revision_is_a_tree_too(repo):
    repo.write("SPEC/00.md", "changed\n")
    assert changed(Tree("HEAD", repo=repo.root), Tree(repo.root)) == ["SPEC/00.md"]
    assert Tree("HEAD", repo=repo.root).text("SPEC/00.md") == "spec\n"


@pytest.mark.parametrize("value, number", [(12, 12), ("12", 12), ("#12", 12), ("https://github.com/o/r/pull/12", 12), ("x", None), (True, None)])
def test_pr_number_forms(value, number):
    assert pr_number(value) == number


# --- ruling-cited -------------------------------------------------------------


def test_a_seat_owned_path_with_no_ruling_is_refused_naming_the_seat(repo):
    repo.write("SPEC/00.md", "changed\n")
    refused = repo.cited()
    assert refused is not None and "SPEC/00.md" in refused and "Product" in refused and "pr: 12" in refused


def test_a_covering_ruling_passes_and_covers_itself(repo):
    repo.write("SPEC/00.md", "changed\n")
    repo.write("milestones/M02/rulings/pr2.md", ruling("Product", ["SPEC/**"]))
    assert repo.cited() is None  # the ruling file itself is under milestones/**, and needs no second ruling


def test_a_ruling_from_another_seat_does_not_cover(repo):
    repo.write("thresholds.yaml", THRESHOLDS.replace("150000", "100000"))
    repo.write("milestones/M02/rulings/pr2.md", ruling("Engineering", ["thresholds.yaml"]))
    refused = repo.cited()
    assert refused is not None and "thresholds.yaml" in refused and "Threshold Owner" in refused


def test_a_ruling_for_another_pr_does_not_cover(repo):
    repo.write("SPEC/00.md", "changed\n")
    repo.write("milestones/M02/rulings/pr1.md", ruling("Product", ["SPEC/**"], pr=11))
    refused = repo.cited()
    assert refused is not None and "SPEC/00.md" in refused and "milestones/M02/rulings/pr1.md" in refused


def test_every_uncovered_path_is_listed_not_the_first(repo):
    repo.write("SPEC/00.md", "changed\n")
    repo.write("rules/one.md", "changed\n")
    refused = repo.cited() or ""
    assert "uncovered SPEC/00.md" in refused and "uncovered rules/one.md" in refused and "2 uncovered" in refused


def test_codeowners_is_read_from_the_base_not_the_pr(repo):
    """The PR moves thresholds.yaml to Engineering and carries an Engineering ruling. Refused under the base's table."""
    repo.write("thresholds.yaml", THRESHOLDS.replace("150000", "100000"))
    repo.write(".github/CODEOWNERS", CODEOWNERS.replace("# seat: Threshold Owner\n/thresholds.yaml", "# seat: Engineering\n/thresholds.yaml"))
    repo.write("milestones/M02/rulings/pr2.md", ruling("Engineering", ["thresholds.yaml", ".github/CODEOWNERS"]))
    refused = repo.cited() or ""
    assert "thresholds.yaml: owned by Threshold Owner" in refused
    assert ".github/CODEOWNERS: owned by Security" in refused
    assert "read from the base" in refused


def test_the_pr_that_adds_codeowners_is_read_against_its_own_table(repo):
    git(repo.root, "rm", "-q", ".github/CODEOWNERS")
    repo.commit_as("t", "no table")
    git(repo.root, "worktree", "remove", "--force", str(repo.base))
    git(repo.root, "worktree", "add", "-q", "--detach", str(repo.base), "HEAD")
    repo.write(".github/CODEOWNERS", CODEOWNERS)
    refused = repo.cited() or ""
    assert "because the base" in refused and ".github/CODEOWNERS: owned by Security" in refused
    repo.write("milestones/M02/rulings/pr2-security.md", ruling("Security", [".github/CODEOWNERS"]))
    assert repo.cited() is None


def test_a_manifest_is_attributed_field_by_field(repo):
    repo.write("agents/refagent/manifest.yaml", MANIFEST.replace("may_call: []", "may_call: [ratings-helper@v1]"))
    repo.write("milestones/M02/rulings/pr2.md", ruling("Engineering", ["agents/refagent/manifest.yaml"]))
    refused = repo.cited() or ""
    assert "agents/refagent/manifest.yaml (may_call): owned by Tool Owner" in refused
    repo.write("milestones/M02/rulings/pr2-tool-owner.md", ruling("Tool Owner", ["agents/refagent/manifest.yaml"]))
    assert repo.cited() is None


def test_a_manifest_comment_change_is_the_file_owners(repo):
    repo.write("agents/refagent/manifest.yaml", "# a comment\n" + MANIFEST)
    refused = repo.cited() or ""
    assert "agents/refagent/manifest.yaml: owned by Engineering" in refused


def test_a_path_no_seat_owns_is_refused(repo):
    repo.write("stray.txt", "nobody owns this\n")
    refused = repo.cited() or ""
    assert "stray.txt: no seat owns it" in refused


def test_the_bot_is_exempt_under_evals_history_and_a_human_is_not(repo):
    repo.write("evals/history/" + "b" * 40 + ".json", "{}\n")
    repo.commit_as("github-actions[bot]", "evals: CI-written envelope")
    assert repo.cited() is None
    repo.write("evals/history/" + "c" * 40 + ".json", "{}\n")
    repo.commit_as("a human", "hand-written")
    refused = repo.cited() or ""
    assert "c" * 40 in refused and "b" * 40 not in refused


def test_the_command_exits_1_on_a_refusal_and_0_otherwise(repo, capsys):
    repo.write("SPEC/00.md", "changed\n")
    assert ruling_cited.main(["--base", str(repo.base), "--tree", str(repo.root), "--pr", "12"]) == 1
    assert "uncovered SPEC/00.md" in capsys.readouterr().out
    repo.write("milestones/M02/rulings/pr2.md", ruling("Product", ["SPEC/**"]))
    assert ruling_cited.main(["--base", str(repo.base), "--tree", str(repo.root), "--pr", "12"]) == 0


# --- two-key -------------------------------------------------------------------


def relax(repo: Repo) -> None:
    repo.write("thresholds.yaml", THRESHOLDS.replace("150000", "300000"))


def test_a_relaxation_with_no_key_is_refused(repo):
    relax(repo)
    refused = repo.keys() or ""
    assert "thresholds.yaml: cost_cap.tokens_per_run 150000 -> 300000 relaxes it (relaxes: up)" in refused
    assert "no seat holds a key" in refused


def test_one_key_is_refused_and_two_files_from_one_seat_are_one_key(repo):
    relax(repo)
    repo.write("milestones/M02/rulings/a.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    assert "one seat holds a key" in (repo.keys() or "")
    repo.write("milestones/M02/rulings/b.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    refused = repo.keys() or ""
    assert "one seat holds a key" in refused and "Two files from the same seat are one key" in refused


def test_two_distinct_seats_pass_when_the_second_names_the_path_in_its_keys(repo):
    """ADR-0009: the second key names the path, exactly, in `keys:`."""
    relax(repo)
    repo.write("milestones/M02/rulings/a.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    repo.write("milestones/M02/rulings/b.md", ruling("Engineering", ["src/**"], keys=["thresholds.yaml"]))
    assert repo.keys() is None


def test_a_body_mention_or_a_broad_glob_is_no_longer_a_second_key(repo):
    """ADR-0009 (M02 PR 2 security F4): a ruling that argued against the change counted as a key for it."""
    relax(repo)
    repo.write("milestones/M02/rulings/a.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    repo.write("milestones/M02/rulings/b.md", ruling("Engineering", ["**"], body="I refuse thresholds.yaml."))
    assert "one seat holds a key" in (repo.keys() or "")


def test_two_seats_without_the_owners_key_are_refused(repo):
    relax(repo)
    repo.write("milestones/M02/rulings/a.md", ruling("Engineering", ["src/**"], body="thresholds.yaml"))
    repo.write("milestones/M02/rulings/b.md", ruling("Product", ["SPEC/**"], body="thresholds.yaml"))
    assert "the owner seat Threshold Owner holds none" in (repo.keys() or "")


def test_a_tightening_needs_no_second_key(repo):
    repo.write("thresholds.yaml", THRESHOLDS.replace("150000", "100000").replace("min_pass: 10", "min_pass: 12"))
    assert repo.keys() is None


def test_a_bar_with_no_relaxes_entry_cannot_move(repo):
    repo.write("thresholds.yaml", THRESHOLDS.replace("  floor.min_pass: down\n", "") + "extra:\n  bar: 2\n")
    repo.commit_as("t", "a bar with no direction")
    git(repo.root, "worktree", "remove", "--force", str(repo.base))
    git(repo.root, "worktree", "add", "-q", "--detach", str(repo.base), "HEAD")
    repo.write("thresholds.yaml", (repo.root / "thresholds.yaml").read_text(encoding="utf-8").replace("bar: 2", "bar: 1"))
    assert "extra.bar 2 -> 1 with no relaxes: entry" in (repo.keys() or "")


def test_retiring_a_golden_needs_two_keys(repo):
    repo.write("evals/goldens/v1/g-010.yaml", GOLDEN.replace("retired: null", "retired: M02"))
    refused = repo.keys() or ""
    assert "g-010 retired (retired: M02)" in refused
    repo.write("milestones/M02/rulings/a.md", ruling("Data Owner", ["evals/goldens/v1/g-010.yaml"]))
    repo.write("milestones/M02/rulings/b.md", ruling("Threshold Owner", ["thresholds.yaml"], keys=["evals/goldens/v1/g-010.yaml"]))
    assert repo.keys() is None


def test_changing_expected_on_an_id_that_has_passed_needs_two_keys(repo):
    repo.write("evals/goldens/v1/g-010.yaml", GOLDEN.replace("available: false", "available: true"))
    refused = repo.keys() or ""
    assert "expected changed on g-010, which has passed in evals/history (agent)" in refused


def test_changing_expected_on_an_id_that_never_passed_is_not_a_relaxation(repo):
    (repo.root / "evals" / "history" / PASSED_G010.name).unlink()
    repo.commit_as("github-actions[bot]", "history without the pass")
    git(repo.root, "worktree", "remove", "--force", str(repo.base))
    git(repo.root, "worktree", "add", "-q", "--detach", str(repo.base), "HEAD")
    repo.write("evals/goldens/v1/g-010.yaml", GOLDEN.replace("available: false", "available: true"))
    assert repo.keys() is None


def test_deleting_a_rule_and_moving_a_guardrail_down_are_relaxations(repo):
    repo.delete("rules/one.md")
    repo.write("agents/refagent/manifest.yaml", MANIFEST.replace('version: "3"', 'version: "2"'))
    refused = repo.keys() or ""
    assert "rules/one.md: a rule deleted" in refused and "guardrail version 3 -> 2 moved down" in refused


def test_shortening_retention_is_a_relaxation(repo):
    repo.write("agents/refagent/manifest.yaml", MANIFEST.replace("retention_days: 30", "retention_days: 7"))
    assert "memory.retention_days 30 -> 7 shortened" in (repo.keys() or "")
    repo.write("agents/refagent/manifest.yaml", MANIFEST.replace("memory: {retention_days: 30, ttl_days: 7, per_user: true}", "memory: null"))
    assert "memory removed" in (repo.keys() or "")


def test_a_human_commit_under_evals_history_is_a_relaxation(repo):
    repo.write("evals/history/" + "c" * 40 + ".json", "{}\n")
    repo.commit_as("a human", "hand-written")
    refused = repo.keys() or ""
    assert "c" * 40 in refused and "not github-actions[bot]'s" in refused


def test_the_command_exits_1_on_a_refusal_and_0_otherwise_two_key(repo, capsys):
    relax(repo)
    assert two_key.main(["--base", str(repo.base), "--tree", str(repo.root), "--pr", "12"]) == 1
    assert "unkeyed thresholds.yaml" in capsys.readouterr().out
    repo.write("milestones/M02/rulings/a.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    repo.write("milestones/M02/rulings/b.md", ruling("Engineering", ["src/**"], keys=["thresholds.yaml"]))
    assert two_key.main(["--base", str(repo.base), "--tree", str(repo.root), "--pr", "12"]) == 0
    assert "two keys with pr: 12 found" in capsys.readouterr().out


def test_a_ruling_file_is_owned_by_the_seat_in_its_own_front_matter(repo):
    """Product's milestones/** key does not cover an edit to another seat's past ruling (security-reviewer on PR 2, F5)."""
    repo.write("milestones/M01/rulings/old-security.md", ruling("Security", ["infra/**"], pr=7))
    repo.commit_as("t", "a past ruling")
    git(repo.root, "worktree", "remove", "--force", str(repo.base))
    git(repo.root, "worktree", "add", "-q", "--detach", str(repo.base), "HEAD")
    repo.write("milestones/M01/rulings/old-security.md", ruling("Security", ["infra/**"], pr=7, body="edited later"))
    repo.write("milestones/M02/rulings/pr2.md", ruling("Product", ["milestones/**"]))
    refused = repo.cited() or ""
    assert "milestones/M01/rulings/old-security.md (a ruling file, owned by its seat:): owned by Security" in refused
    repo.write("milestones/M02/rulings/pr2-security.md", ruling("Security", ["milestones/M01/rulings/old-security.md"]))
    assert repo.cited() is None


def test_deleting_the_memory_key_outright_is_a_relaxation(repo):
    repo.write("agents/refagent/manifest.yaml", MANIFEST.replace("memory: {retention_days: 30, ttl_days: 7, per_user: true}\n", ""))
    assert "memory removed" in (repo.keys() or "")


def test_a_new_subagent_prompt_is_owned_by_the_seat_in_its_own_front_matter(repo):
    """No CODEOWNERS line on the base names a prompt that did not exist there, so the owner table
    alone would say no seat owns it, and no ruling could cover it (M03 PR 1, security-reviewer B1).
    A prompt is owned by its own `seat:` (SPEC/00 section 5, last row), read from the base when
    the file is there and from the PR only when it is new."""
    prompt = "---\nname: red-teamer\nseat: rule-owner\n---\n\nA prompt.\n"
    repo.write(".claude/agents/red-teamer.md", prompt)
    refused = repo.cited() or ""
    assert "no seat owns it" not in refused
    assert ".claude/agents/red-teamer.md (a subagent prompt, owned by its seat:): owned by Rule Owner" in refused
    repo.write("milestones/M03/rulings/pr1-rule-owner.md", ruling("Rule Owner", [".claude/agents/red-teamer.md"]))
    assert repo.cited() is None


def test_an_existing_prompt_keeps_the_seat_the_base_gives_it(repo):
    """Editing a prompt's `seat:` in the PR does not move it: the base's front matter decides."""
    repo.write(".claude/agents/red-teamer.md", "---\nname: red-teamer\nseat: rule-owner\n---\n\nA prompt.\n")
    repo.commit_as("t", "the prompt on the base")
    git(repo.root, "worktree", "remove", "--force", str(repo.base))
    git(repo.root, "worktree", "add", "-q", "--detach", str(repo.base), "HEAD")
    repo.write(".claude/agents/red-teamer.md", "---\nname: red-teamer\nseat: product\n---\n\nMoved.\n")
    repo.write("milestones/M03/rulings/pr1.md", ruling("Product", [".claude/agents/red-teamer.md"]))
    refused = repo.cited() or ""
    assert "owned by Rule Owner" in refused



# --- ADR-0009 entries 1 to 5, and deletes: (read from M03 PR 2) --------------------

RULES_YAML = """\
plants: [g-013, g-015]
topics_apply_to: input and output
denied_topics:
  - name: embargoed-synopsis
    definition: plot
  - name: third-party
    definition: terms
pii:
  - entity: PHONE
    action: ANONYMIZE
blocks:
  g-016: embargoed-synopsis
"""


@pytest.fixture
def rules_repo(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    r = Repo(root)
    r.write(".github/CODEOWNERS", CODEOWNERS)
    r.write("thresholds.yaml", THRESHOLDS)
    r.write("agents/refagent/manifest.yaml", MANIFEST)
    r.write("agents/refagent/rules/guardrail.yaml", RULES_YAML)
    r.write("rules/one.md", "a rule\n")
    (root / "evals" / "history").mkdir(parents=True)
    r.commit_base()
    yield r
    git(root, "worktree", "remove", "--force", str(r.base))


@pytest.mark.parametrize(("change", "said"), [
    (("  - name: third-party\n    definition: terms\n", ""), "denied_topics[third-party] removed"),
    (("plants: [g-013, g-015]", "plants: [g-013]"), "plants[g-015] removed"),
    (("    action: ANONYMIZE", "    action: NONE"), "pii[PHONE].action ANONYMIZE -> NONE weakened"),
    (("topics_apply_to: input and output", "topics_apply_to: input"), "topics_apply_to 'input and output' -> 'input' narrowed"),
    (("  g-016: embargoed-synopsis", "  g-016: third-party"), "blocks.g-016 embargoed-synopsis -> third-party pointed at another rule"),
    (("  g-016: embargoed-synopsis", "  g-016: null"), "blocks.g-016 embargoed-synopsis -> None pointed at another rule"),
    (("name: third-party", "name: sending-terms"), "denied_topics[third-party] removed"),
])  # fmt: skip
def test_entry_5_a_rule_removed_weakened_or_repointed_needs_two_keys(rules_repo, change, said):
    rules_repo.write("agents/refagent/rules/guardrail.yaml", RULES_YAML.replace(*change))
    assert said in (rules_repo.keys() or ""), rules_repo.keys()


def test_entry_5_a_rule_added_or_tightened_needs_one(rules_repo):
    tighter = RULES_YAML.replace("plants: [g-013, g-015]", "plants: [g-013, g-015, g-014]").replace(
        "    action: ANONYMIZE", "    action: BLOCK")  # fmt: skip
    rules_repo.write("agents/refagent/rules/guardrail.yaml", tighter)
    assert rules_repo.keys() is None


def test_entry_4_a_guardrail_set_to_null_or_its_id_changed(rules_repo):
    guard = 'guardrail: {id: g, version: "3"}'
    assert guard in MANIFEST
    rules_repo.write("agents/refagent/manifest.yaml", MANIFEST.replace(guard, "guardrail: null"))
    assert "guardrail set to null or removed" in (rules_repo.keys() or "")
    rules_repo.write("agents/refagent/manifest.yaml", MANIFEST.replace(guard, 'guardrail: {id: h, version: "3"}'))
    assert "guardrail id g -> h" in (rules_repo.keys() or "")


def test_entry_3_a_budget_raised_set_to_null_or_removed(tmp_path):
    """The Threshold Owner's key on a manifest's max_tokens_per_session and daily_usd."""
    from src.gates import Tree

    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    r = Repo(root)
    r.write(".github/CODEOWNERS", CODEOWNERS)
    r.write("agents/refagent/manifest.yaml", MANIFEST + "max_tokens_per_session: 20000\ndaily_usd: 10\n")
    r.commit_base()
    try:
        r.write("agents/refagent/manifest.yaml", MANIFEST + "max_tokens_per_session: 30000\n")
        found = [x.what for x in two_key.relaxations(Tree(r.root), Tree(r.base))]
        assert "max_tokens_per_session 20000 -> 30000 raised (ADR-0009 entry 3)" in found
        assert "daily_usd 10 set to null or removed (ADR-0009 entry 3)" in found
        assert all(x.seat == "Threshold Owner" for x in two_key.relaxations(Tree(r.root), Tree(r.base)))
    finally:
        git(root, "worktree", "remove", "--force", str(r.base))


def test_entries_1_and_2_a_relaxes_direction_flipped_or_a_bar_deleted(rules_repo):
    import yaml as _yaml

    doc = _yaml.safe_load(THRESHOLDS)
    bar = next(iter(doc["relaxes"]))
    flipped = THRESHOLDS.replace(f"{bar}: {doc['relaxes'][bar]}", f"{bar}: {'down' if doc['relaxes'][bar] == 'up' else 'up'}")
    rules_repo.write("thresholds.yaml", flipped)
    assert f"relaxes.{bar}" in (rules_repo.keys() or "")
    section, name = bar.split(".", 1)
    deleted = "\n".join(line for line in THRESHOLDS.splitlines() if not line.strip().startswith(f"{name}:")) + "\n"
    rules_repo.write("thresholds.yaml", deleted)
    assert f"{bar} deleted" in (rules_repo.keys() or "")


def test_a_deletion_is_covered_only_when_its_seat_names_it_in_deletes(rules_repo):
    """ADR-0009: an authorises: glob that matches a deleted path no longer rules the deletion."""
    rules_repo.delete("rules/one.md")
    rules_repo.write("milestones/M02/rulings/a.md", ruling("Rule Owner", ["rules/**"]))
    assert "rules/one.md: deleted, and no ruling file" in (rules_repo.cited() or "")
    rules_repo.write("milestones/M02/rulings/a.md", ruling("Rule Owner", ["rules/**"], deletes=["rules/one.md"]))
    assert rules_repo.cited() is None


@pytest.mark.parametrize(("after", "said"), [
    ("", "denied_topics[third-party] removed"),
    ("# nothing left\n", "plants[g-015] removed"),
    ("plants: [g-013\n  : : broken", "the file no longer parses: every entry removed"),
])  # fmt: skip
def test_entry_5_an_emptied_or_unparseable_rules_file_is_every_entry_removed(rules_repo, after, said):
    """The second cold read of PR 2, F1: the file stays in the tree, so "a rule deleted" does not fire."""
    rules_repo.write("agents/refagent/rules/guardrail.yaml", after)
    assert said in (rules_repo.keys() or ""), rules_repo.keys()


def test_entry_5_a_switch_off_or_a_filter_level_lowered_is_weakened():
    """The second cold read of PR 2, F2: the prompt-attack filter on -> off, HIGH -> NONE."""
    before = "content_filters:\n  prompt_attack: on\n  hate: HIGH\n"
    assert two_key.rule_relaxations(before, "content_filters:\n  prompt_attack: off\n  hate: HIGH\n") == [
        "content_filters.prompt_attack on -> off weakened"]
    assert two_key.rule_relaxations(before, "content_filters:\n  prompt_attack: on\n  hate: NONE\n") == [
        "content_filters.hate HIGH -> NONE weakened"]
    assert two_key.rule_relaxations(before, "content_filters:\n  prompt_attack: on\n  hate: HIGH\n  sexual: LOW\n") == []
