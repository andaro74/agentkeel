"""M10 PR 2's readers beyond the seed tests (SPEC/10 §4, §6).

The seed tests (`test_m10_seeds.py`) say each planted fault is refused for its
planted reason. These say what the readers do with what was not planted: every
way `callers_errors` refuses a field, and the platform check naming that reader
over the fixture agent; the raw record to the read shape (`from_raw`) for both
raw sources and the credential it refuses; the whole reading on a run not made
and on one held; row 10's reading of it; the observer on a run not made.
Nothing here calls AWS, GitHub or a model.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from src.validate import agent as platform_check
from src.validate.callers import FIELD, callers_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "m10"
M09_AGENT = ROOT / "tests" / "fixtures" / "m09" / "s1-festival-desk"
CALLERS_CHECK = "an agent's manifest says who may call it, even if nobody (callers)"


def manifest(**override: Any) -> dict[str, Any]:
    doc = yaml.safe_load((FIXTURES / "s2-manifest-no-callers" / "with_callers.yaml").read_text(encoding="utf-8"))
    return {**doc, **override}


# --- callers_errors: every refusal names the field (SPEC/10 §2, §6; S2's reader) -------------------


def test_an_empty_list_says_nobody_and_is_admitted():
    assert callers_errors(manifest(callers=[])) == []
    assert callers_errors(manifest()) == []  # one subject, issuer self


def test_a_missing_key_is_refused_naming_the_field_and_the_default():
    doc = manifest()
    del doc["callers"]
    (error,) = callers_errors(doc)
    assert error.startswith(f"{FIELD}: missing") and "callers: []" in error


def test_platform_is_reserved_and_refused_by_name():
    errors = callers_errors(manifest(callers=[{"subject": "platform", "issuer": "self"}]))
    assert len(errors) == 1 and "'platform' is reserved" in errors[0] and "goldens caller" in errors[0]


def test_an_issuer_that_is_not_self_is_refused():
    errors = callers_errors(manifest(callers=[{"subject": "lantern-desk", "issuer": "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_x"}]))
    assert len(errors) == 1 and "issuer" in errors[0] and "'self'" in errors[0]


def test_a_duplicate_subject_is_refused_naming_both_entries():
    errors = callers_errors(manifest(callers=[{"subject": "lantern-desk", "issuer": "self"},
                                              {"subject": "box-office", "issuer": "self"},
                                              {"subject": "lantern-desk", "issuer": "self"}]))  # fmt: skip
    assert errors == [f"{FIELD}[2]: subject 'lantern-desk' is already {FIELD}[0]'s; one entry per subject"]


def test_a_malformed_entry_is_refused_part_by_part():
    errors = callers_errors(manifest(callers=[{"subject": "Lantern Desk", "issuer": "self", "scope": "x"}, "box-office", {"issuer": "self"}]))
    assert any("unknown key(s) ['scope']" in e for e in errors)
    assert any("'Lantern Desk' is not a name" in e for e in errors)
    assert f"{FIELD}[1]: not a mapping of subject and issuer" in errors
    assert f"{FIELD}[2]: no subject" in errors
    assert callers_errors(manifest(callers="lantern-desk")) == [f"{FIELD}: not a list of {{subject, issuer}} entries (str)"]
    assert callers_errors("not a mapping")[0].startswith(FIELD)


# --- the platform check names the reader (SPEC/10 §6) -------------------------------------------------


def door_layout(tmp_path: Path, callers: list[dict[str, str]] | None) -> tuple[Path, Path]:
    """agentkeel's root as the deploy's checkout holds it, with the fixture agent placed at agents/<name>/ and
    `callers` as given (None: the key left out, as festival-desk's repository held it at 19864419)."""
    root = tmp_path / "agentkeel"
    for name in ("refagent", "ratings-helper"):
        (root / "agents" / name).mkdir(parents=True)
        shutil.copy2(ROOT / "agents" / name / "manifest.yaml", root / "agents" / name / "manifest.yaml")
    shutil.copy2(ROOT / "thresholds.yaml", root / "thresholds.yaml")
    (root / "rules").mkdir()
    shutil.copy2(ROOT / "rules" / "baseline.yaml", root / "rules" / "baseline.yaml")
    bundle = root / "agents" / "festival-desk"
    shutil.copytree(M09_AGENT, bundle)
    if callers is not None:
        with (bundle / "manifest.yaml").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(yaml.safe_dump({"callers": callers}, sort_keys=False))
    return root, bundle


def test_the_platform_check_refuses_a_manifest_with_no_callers_under_the_named_check_and_admits_one_with(tmp_path):
    from .test_m06_seeds import stand_in_lookup

    root, bundle = door_layout(tmp_path, None)
    refused = platform_check.evaluate(bundle, "agentkeel-studio/festival-desk", root=root, lookup=stand_in_lookup)
    assert {name for name, errs in refused.items() if errs} == {CALLERS_CHECK}, refused
    assert refused[CALLERS_CHECK][0].startswith(f"{FIELD}: missing")
    root, bundle = door_layout(tmp_path / "with", [{"subject": "lantern-desk", "issuer": "self"}])
    admitted = platform_check.evaluate(bundle, "agentkeel-studio/festival-desk", root=root, lookup=stand_in_lookup)
    assert {name for name, errs in admitted.items() if errs} == set(), admitted


# --- two-key entry 7 (ADR-0016), beyond the seed's four cases --------------------------------------------


def test_entry_7_reads_subjects_not_bytes():
    from src.gates.two_key import caller_relaxations

    one = [{"subject": "lantern-desk", "issuer": "self"}]
    two = one + [{"subject": "box-office", "issuer": "self"}]
    assert caller_relaxations({}, {"callers": []}) == []  # absent to [] (the two manifests of this PR)
    assert caller_relaxations({"callers": two}, {"callers": one}) == []  # a subject removed
    assert caller_relaxations({"callers": one}, {"callers": one[::-1] + []}) == []  # the same list
    assert caller_relaxations({}, {"callers": one}) == ["callers: subject 'lantern-desk' admitted (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {"callers": two}) == ["callers: subject 'box-office' admitted (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {}) == ["callers removed from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": one}, {"callers": None}) == ["callers removed from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({"callers": []}, {"callers": "lantern-desk"}) == ["callers no longer a list from a value (ADR-0016 entry 7)"]
    assert caller_relaxations({}, {}) == []
