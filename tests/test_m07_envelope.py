"""`upgrade` on the envelope, claim 7's checks in the gate, and row 7's reading (SPEC/07 §4; M07 PR 2).

P5: the observer writes raw observations, build rules them into `upgrade` and writes the checks, the
gate holds the checks, and the ledger's row 7 reading reads `upgrade` with the bars of the envelope's
own commit. Each can disagree with the one before it, and a test here shows each doing so.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.verdict import ROOT, build, gate, load_golden_kinds, plants, schema_errors, upgrade
from tests.test_gates import Repo, git, ruling
from tests.test_m07_upgrade import BARS, TEMPLATE, THRESHOLDS, full, observation

from .conftest import GOLDENS_DIR, URL, claim_1_checks, claim_2_checks

HISTORY = ROOT / "evals" / "history"
EVERY_SURFACE_TEST = [name for tests in plants.SURFACE_PLANTS.values() for name in tests]


def junit(tmp_path: Path, names: list[str], failing: tuple[str, ...] = ()) -> Path:
    cases = "".join(f'<testcase classname="tests.t" name="{n}">{"<failure/>" if n in failing else ""}</testcase>' for n in names)
    path = tmp_path / "surfaces.xml"
    path.write_text(f"<testsuites><testsuite>{cases}</testsuite></testsuites>", encoding="utf-8")
    return path


def built(chain, tmp_path: Path, seen: dict[str, Any], *, failing: tuple[str, ...] = (), app: dict[str, Any] | None = None,
          s5: str = "") -> tuple[int, Path]:  # fmt: skip
    """build's command line, as `make evals` calls it from M07 PR 2: --upgrade, --surfaces and F7_5's own case."""
    envelope_path, card_path, _control_raw = chain(agent=True)
    raw_path = tmp_path / f"{envelope_path.stem}.agent-raw.json"
    observed = tmp_path / "upgrade.json"
    observed.write_text(json.dumps(seen), encoding="utf-8")
    surfaces = junit(tmp_path, [*EVERY_SURFACE_TEST, "test_s5_a_silent_surface_plant_is_counted"], failing)
    flags = ["--upgrade", str(observed), "--surfaces", str(surfaces),
             "--check-cases", "F7_5", "test_s5_a_silent_surface_plant_is_counted" + s5, str(surfaces)]  # fmt: skip
    if app is not None:
        stored = tmp_path / "app.json"
        stored.write_text(json.dumps(app), encoding="utf-8")
        flags += ["--app-observation", str(stored)]
    code = build.main(["envelope", "--raw", str(raw_path), "--control-card", str(card_path), "--out", str(envelope_path),
                       "--history-dir", str(tmp_path / "no-history"), "--run-url", URL,
                       *claim_1_checks(tmp_path), *claim_2_checks(tmp_path), *flags])  # fmt: skip
    return code, envelope_path


# --- build writes it -----------------------------------------------------------------


def test_build_writes_upgrade_with_every_live_reading_unread_and_the_surfaces_counted(chain, tmp_path):
    """PR 2's own run in small: nothing attempted, so nothing live is read, and nothing is taken."""
    code, path = built(chain, tmp_path, {k: v for k, v in observation().items() if k != "surfaces"})
    assert code == 0
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert schema_errors(envelope) == []
    reading = envelope["upgrade"]
    assert [reading[name]["read"] for name in gate.UPGRADE_READINGS] == [False, False, False, False, False, True]
    assert reading["surfaces"] == {"plants_expected": 2, "plants_fired": 2, "silent": []}
    assert reading["taken"] == {"n": 0, "of": 3, "platform": None, "model": None, "retirement": None}
    assert envelope["checks"]["F7_5"]["status"] == "pass" and envelope["verdict"] == "GREEN"
    # The surfaces' plants are counted apart: they never enter the golden plants' count.
    assert (envelope["plants_expected"], envelope["plants_fired"]) == (0, 0)


def test_a_silent_surface_plant_is_red_whatever_the_s5_test_said(chain, tmp_path):
    """F7.5: S5's own test passed, and a reader of panel 2's plant did not. Two sources; both must pass."""
    code, path = built(chain, tmp_path, observation(), failing=("test_s4_a_green_row_for_a_red_envelope_is_found_by_build",))
    assert code == 0
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert envelope["upgrade"]["surfaces"] == {"plants_expected": 2, "plants_fired": 1,
                                               "silent": ["tests/fixtures/m07/s4-panel2/"]}  # fmt: skip
    assert envelope["checks"]["F7_5"]["status"] == "fail" and envelope["verdict"] == "RED"
    assert envelope["upgrade"]["F7_5"]["held"] is False


def test_the_counter_alone_does_not_pass_f7_5_when_its_own_test_did_not_run(chain, tmp_path):
    code, path = built(chain, tmp_path, observation(), s5="_renamed")
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert code == 0 and envelope["upgrade"]["surfaces"]["plants_fired"] == 2
    assert envelope["checks"]["F7_5"]["status"] == "fail"  # a name with no case is a fail (SPEC/01 section 4)


def test_build_refuses_an_upgrade_run_with_no_bars_or_an_observation_not_in_shape(tmp_path):
    seen = tmp_path / "u.json"
    seen.write_text(json.dumps(observation()), encoding="utf-8")
    with pytest.raises(build.Refused, match="thresholds.yaml upgrade must give"):
        build.upgrade_record(seen, {"quickstart": {"max_seconds": 1}}, HISTORY, template_reading=None, app=None, surfaces=None)
    seen.write_text(json.dumps({"s0": None}), encoding="utf-8")
    with pytest.raises(build.Refused, match="looked_up_at"):
        build.upgrade_record(seen, THRESHOLDS, HISTORY, template_reading=None, app=None, surfaces=None)


def test_a_stored_observation_that_could_not_be_fetched_is_no_observation(tmp_path):
    path = tmp_path / "app.json"
    assert build.app_observation(None) is None and build.app_observation(path) is None
    path.write_text(json.dumps({"error": "AccessDenied on observations/", "run_id": None}), encoding="utf-8")
    assert build.app_observation(path) is None
    path.write_text(json.dumps({"run_id": "9", "read_at": "t", "key": "observations/9.json", "upgrade": {}}), encoding="utf-8")
    assert build.app_observation(path)["run_id"] == "9"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(build.Refused, match="not an observation"):
        build.app_observation(path)


def test_the_envelope_names_the_stored_observation_it_ruled_on(chain, tmp_path):
    stored = {"run_id": "777", "read_at": "2026-10-06T11:45:00Z", "key": "observations/777.json", "template": {}, "upgrade": {}}
    code, path = built(chain, tmp_path, observation(), app=stored)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert code == 0 and schema_errors(envelope) == []
    assert envelope["upgrade"]["app_observation"] == {"run_id": "777", "read_at": "2026-10-06T11:45:00Z",
                                                      "key": "observations/777.json"}  # fmt: skip


def test_an_envelope_with_every_upgrade_taken_validates():
    recorded = json.loads((HISTORY / "827ee8bc014b28f588e9b8f3e1d4a947be885f26.json").read_text(encoding="utf-8"))
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    assert schema_errors({**recorded, "upgrade": reading}) == []
    assert schema_errors({**recorded, "upgrade": {**reading, "taken": {**reading["taken"], "of": 4}}}) != []
    assert schema_errors(recorded) == []  # optional: no envelope written before it becomes invalid


# --- the gate requires the six checks, and holds F7_5 to the counts ------------------


def test_claim_7s_checks_are_required_from_the_commit_that_wired_them(monkeypatch):
    assert gate.CLAIM_7_CHECKS == ("F7_0", "F7_1", "F7_2", "F7_3", "F7_4", "F7_5")
    monkeypatch.setattr(gate, "before_m02_pr2", lambda commit, root=ROOT: False)
    monkeypatch.setattr(gate, "from_m03_readers", lambda commit, root=ROOT: False)
    monkeypatch.setattr(gate, "from_m04_readers", lambda commit, root=ROOT: False)
    monkeypatch.setattr(gate, "descends_from", lambda commit, anchor, root=ROOT: anchor == gate.M07_READERS)
    assert gate.required_checks("f" * 40)[-6:] == gate.CLAIM_7_CHECKS
    monkeypatch.setattr(gate, "descends_from", lambda commit, anchor, root=ROOT: False)
    assert not set(gate.CLAIM_7_CHECKS) & set(gate.required_checks("f" * 40))


def test_an_agent_envelope_without_claim_7s_checks_is_red_once_they_are_required(chain):
    envelope_path, _, _ = chain(agent=True)
    envelope = gate.read(envelope_path)
    verdict, reasons = gate.judge(envelope, load_golden_kinds(GOLDENS_DIR), {}, [],
                                  required=gate.CLAIM_1_CHECKS + gate.CLAIM_2_CHECKS + gate.CLAIM_7_CHECKS)  # fmt: skip
    assert verdict == "RED"
    assert [r for r in reasons if "F7_" in r] == [f"checks.{name} is missing from an agent envelope" for name in gate.CLAIM_7_CHECKS]


def test_build_says_f7_5_passed_and_the_gate_reads_a_silent_surface_plant(chain, tmp_path):
    """P5: a hand-edited check does not carry. The counts say one plant was silent; the gate says so."""
    code, path = built(chain, tmp_path, observation(), failing=("test_s4_a_green_row_for_a_red_envelope_is_found_by_build",))
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["checks"]["F7_5"]["status"] = "pass"
    envelope["verdict"] = "GREEN"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    verdict, reasons = gate.judge(gate.read(path), load_golden_kinds(GOLDENS_DIR), {}, [], required=())
    assert verdict == "RED"
    assert "silent surface plant: expected 2, fired 1" in reasons
    assert "envelope says F7_5 is pass, and upgrade.surfaces counts a silent plant" in reasons


def test_the_live_readings_gate_nothing(chain, tmp_path):
    """SPEC/07 section 4: an attempt that missed must not turn a pull request's `evals` red."""
    missed = full()
    missed["s2"]["retirement"]["invocation"] = {"answered": True, "error": None, "at": "2026-10-05T10:01:00Z"}
    code, path = built(chain, tmp_path, missed)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert code == 0 and envelope["upgrade"]["F7_2"]["held"] is False and envelope["verdict"] == "GREEN"
    verdict, reasons = gate.judge(gate.read(path), load_golden_kinds(GOLDENS_DIR), {}, [], required=())
    assert verdict == "GREEN" and reasons == []
    # And row 7 reads it RED.
    assert any(m.startswith("F7_2 not held") for m in gate.upgrade_misses(envelope, BARS, "here"))


# --- row 7's reading ---------------------------------------------------------------------


def envelope_with(reading: dict[str, Any] | None, template: dict[str, Any] | None = None) -> dict[str, Any]:
    return {**({"upgrade": reading} if reading is not None else {}), **({"template": template} if template else {})}


def test_row_7_is_red_while_anything_is_unread_and_names_each():
    reading = upgrade.record(observation(), THRESHOLDS, HISTORY)
    misses = gate.upgrade_misses(envelope_with(reading), BARS, "here")
    assert [m.split()[0] for m in misses[:5]] == ["F7_0", "F7_1", "F7_2", "F7_3", "F7_4"] and all("unread" in m for m in misses[:5])
    assert misses[5] == "taken 0 of 3: platform unread, model unread, retirement unread"
    parts = gate.upgrade_reading(envelope_with(reading))
    assert parts == ["taken 0 of 3", "F7_0 unread", "F7_1 unread", "F7_2 unread", "F7_3 unread", "F7_4 unread", "F7_5 held",
                     "surface plants 2/2"]  # fmt: skip
    assert gate.upgrade_misses({}, BARS, "here") == ["upgrade not read: the envelope records no attempt"]
    assert gate.upgrade_reading({}) == []


def test_row_7_has_no_miss_only_at_three_of_three_with_every_falsifier_held():
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    template = {"F6_1": {"read": True, "held": True}, "F6_3": {"read": True, "held": False, "elapsed_s": 30000.0}}
    assert gate.upgrade_misses(envelope_with(reading, template), BARS, "here") == []
    parts = gate.upgrade_reading(envelope_with(reading, template))
    assert parts[:4] == ["taken 3 of 3", "F7_0 held (relaxation refused)", "F7_1 held", "F7_2 held 600 s"]
    # Claim 6's later reading is quoted beside it, and does not decide row 7: a slow quickstart made an agent.
    assert parts[-2:] == ["claim 6 later F6_1 held", "claim 6 later F6_3 not held 30000 s"]


def test_the_bars_are_read_at_the_envelopes_commit_and_build_and_the_gate_can_disagree():
    """P5: build held the retirement at 600 s and the platform upgrade at 1,200 s against the bars it was
    given. A commit whose bars are lower reads them again."""
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    lower = {"arrive_max_seconds": 900.0, "deploy_max_seconds": 3600.0, "retire_max_seconds": 300.0}
    misses = gate.upgrade_misses(envelope_with(reading), lower, "at a later commit")
    assert f"upgrade was read against {BARS}, the commit's bars are {lower} (at a later commit)" in misses
    assert "F7_2: build held 600 s, over the commit's bar 300 s" in misses
    assert "F7_1: build held the platform upgrade at 1200 s, over the commit's bar 900 s" in misses
    assert gate.upgrade_misses(envelope_with(reading), None, "nowhere")[0] == \
        "no upgrade bars in thresholds.yaml at nowhere: the limits cannot be read"  # fmt: skip


def test_a_taken_count_that_is_not_its_kinds_and_a_silent_surface_plant_are_misses():
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    forged = {**reading, "taken": {**reading["taken"], "model": False}}  # still says n: 3
    misses = gate.upgrade_misses(envelope_with(forged), BARS, "here")
    assert "taken: the envelope says 3, its three kinds count 2" in misses and "taken 2 of 3: model not taken" in misses
    silent = {**reading, "surfaces": {"plants_expected": 2, "plants_fired": 1, "silent": ["x"]}}
    assert "surfaces: plants_expected 2, plants_fired 1" in gate.upgrade_misses(envelope_with(silent), BARS, "here")


def test_the_bars_at_this_tree_are_the_three_ruled_on_2026_10_02():
    bars, _where = gate.upgrade_bars_at("HEAD")
    if bars is None:  # HEAD is the commit before the bars; the tree has them
        bars = upgrade.bars_of(build.load_thresholds(ROOT / "thresholds.yaml"))
    assert bars == {"arrive_max_seconds": 4500.0, "deploy_max_seconds": 3600.0, "retire_max_seconds": 3600.0}
    assert gate.READ_THE_UPGRADE == {"M07"} and gate.upgrade_bars_at("0" * 40, ROOT)[0] is not None  # an unknown commit: the tree


def test_row_7s_cell_is_the_envelopes_numbers_under_the_gates_reading(chain, tmp_path, monkeypatch):
    code, path = built(chain, tmp_path, observation())
    monkeypatch.setattr(gate, "shallow", lambda root=ROOT: False)
    cell = gate.measured_at(path, tmp_path / "no-history", milestone="M07")
    assert "; taken 0 of 3; F7_0 unread; F7_1 unread; F7_2 unread; F7_3 unread; F7_4 unread; F7_5 held; surface plants 2/2; " in cell
    assert "; taken 0 of 3: platform unread, model unread, retirement unread; RED; envelope `" in cell
    assert "; GREEN; " in gate.measured_at(path, tmp_path / "no-history")  # the run's own verdict is untouched


# --- the three bars, and the quickstart's, each need two keys to relax (open.md row 23) --------

THE_FOUR = ("quickstart.max_seconds", "upgrade.arrive_max_seconds", "upgrade.deploy_max_seconds", "upgrade.retire_max_seconds")
CODEOWNERS = "# seat: Threshold Owner\n/thresholds.yaml @someone\n# seat: Product\n/milestones/ @someone\n# seat: Engineering\n/src/ @someone\n"


@pytest.fixture
def bars_repo(tmp_path: Path):
    """A repository whose base holds this tree's own thresholds.yaml."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    repo = Repo(root)
    repo.write(".github/CODEOWNERS", CODEOWNERS)
    repo.write("thresholds.yaml", (ROOT / "thresholds.yaml").read_text(encoding="utf-8"))
    (root / "evals" / "history").mkdir(parents=True)
    (root / "evals" / "history" / ".keep").write_text("", encoding="utf-8")
    repo.commit_base()
    yield repo
    git(root, "worktree", "remove", "--force", str(repo.base))


def moved(repo: Repo, bar: str, factor: float) -> tuple[int, int]:
    import yaml

    text = (ROOT / "thresholds.yaml").read_text(encoding="utf-8")
    group, name = bar.split(".")
    value = yaml.safe_load(text)[group][name]
    assert text.count(f"  {name}: {value}\n") == 1, bar
    repo.write("thresholds.yaml", text.replace(f"  {name}: {value}\n", f"  {name}: {int(value * factor)}\n"))
    return value, int(value * factor)


@pytest.mark.parametrize("bar", THE_FOUR)
def test_raising_a_time_bar_needs_two_keys(bars_repo, bar):
    before, after = moved(bars_repo, bar, 2)
    refused = bars_repo.keys() or ""
    assert f"thresholds.yaml: {bar} {before} -> {after} relaxes it (relaxes: up)" in refused and "no seat holds a key" in refused
    bars_repo.write("milestones/M07/rulings/a.md", ruling("Threshold Owner", ["thresholds.yaml"]))
    assert "one seat holds a key" in (bars_repo.keys() or "")
    bars_repo.write("milestones/M07/rulings/b.md", ruling("Product", ["milestones/**"], keys=["thresholds.yaml"]))
    assert bars_repo.keys() is None


@pytest.mark.parametrize("bar", THE_FOUR)
def test_lowering_a_time_bar_needs_no_second_key(bars_repo, bar):
    moved(bars_repo, bar, 0.5)
    assert bars_repo.keys() is None


def test_adding_the_three_bars_was_not_a_relaxation_and_deleting_one_is(bars_repo):
    """ADR-0009: adding a bar is not a relaxation; a bar deleted, or its direction flipped, is."""
    import re

    text = (ROOT / "thresholds.yaml").read_text(encoding="utf-8")
    without = re.sub(r"\nupgrade:\n(  \w+: \d+\n)+", "\n", text)
    without = "".join(line for line in without.splitlines(keepends=True) if not line.startswith("  upgrade."))
    assert "upgrade" not in two_key_bars(without)
    # As PR 2 does: the base has no `upgrade`, the tree adds it.
    bars_repo.write("thresholds.yaml", without)
    bars_repo.commit_as("t", "before the bars")
    git(bars_repo.root, "worktree", "remove", "--force", str(bars_repo.base))
    git(bars_repo.root, "worktree", "add", "-q", "--detach", str(bars_repo.base), "HEAD")
    bars_repo.write("thresholds.yaml", text)
    assert bars_repo.keys() is None
    # And the other way: the base has them, the tree deletes one, or flips its direction.
    bars_repo.commit_as("t", "the bars")
    git(bars_repo.root, "worktree", "remove", "--force", str(bars_repo.base))
    git(bars_repo.root, "worktree", "add", "-q", "--detach", str(bars_repo.base), "HEAD")
    bars_repo.write("thresholds.yaml", text.replace("  retire_max_seconds: 3600\n", "").replace("  upgrade.retire_max_seconds: up\n", ""))
    assert "upgrade.retire_max_seconds" in (bars_repo.keys() or "")
    bars_repo.write("thresholds.yaml", text.replace("  upgrade.arrive_max_seconds: up\n", "  upgrade.arrive_max_seconds: down\n"))
    assert "upgrade.arrive_max_seconds" in (bars_repo.keys() or "")


def two_key_bars(text: str) -> str:
    import yaml

    from src.gates import two_key

    return " ".join(two_key.bars(yaml.safe_load(text)))


# --- after the cold review of M07 PR 2: what the gate counts again (cold review F8; threshold-owner F6) ----


def test_the_gate_counts_each_kind_again_and_holds_the_deploy_bar_again():
    reading = upgrade.record(full(), THRESHOLDS, HISTORY, template=TEMPLATE)
    template = {"F6_1": {"read": True, "held": True}, "F6_3": {"read": True, "held": False, "elapsed_s": 30000.0}}
    assert gate.upgrade_misses(envelope_with(reading, template), BARS, "here") == []

    def misses(change) -> list[str]:
        mine = copy.deepcopy(reading)
        change(mine)
        return gate.upgrade_misses(envelope_with(mine, template), BARS, "here")

    # build says a kind was taken, and F7_1's own list of that kind says it was not held, or not merged.
    said = misses(lambda r: next(u for u in r["F7_1"]["upgrades"] if u["kind"] == "model").update(held=False))
    assert any("the model upgrade was taken, and F7_1 lists it as not held or not merged" in m for m in said)
    said = misses(lambda r: next(u for u in r["F7_1"]["upgrades"] if u["kind"] == "platform").update(merged=False))
    assert any("the platform upgrade was taken" in m for m in said)
    assert any("the retirement was taken, and F7_2 is not held" in m for m in misses(lambda r: r["F7_2"].update(held=False)))
    # F7_0 says held, and one of its parts does not.
    said = misses(lambda r: r["F7_0"]["parts"]["relaxation"].update(read=False, held=None))
    assert any("one of its four parts is unread or not held" in m for m in said)
    # A deploy over the commit's bar that build took.
    said = misses(lambda r: next(u for u in r["F7_1"]["upgrades"] if u["kind"] == "platform").update(deployed_s=3601.0))
    assert any("deployed at 3601 s, over the commit's bar 3600 s" in m for m in said)
    # A count of no plants is not a count that fired.
    said = misses(lambda r: r["surfaces"].update(plants_expected=0, plants_fired=0))
    assert any("no plant is counted" in m for m in said)
