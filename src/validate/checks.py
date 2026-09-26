"""`make validate` (SPEC/00 §5). Each check returns a list of error strings; empty means it passed.

M00 PR 1 (ADR-0001 amendment 1 item 22): golden front matter, ruling front
matter, and that every ordinary and trap golden cites a rights-table row and
a clause that exist. M01 PR 1 (Security, M01 open item 29): the workflow
file hash. M01 PR 2 (SPEC/01 §6): the manifest schema, and cdk-nag over
both stacks. M02 PR 2 (SPEC/02 §6): CODEOWNERS complete and single-owner
with real logins; `relaxes:` on every bar; edges two-sided, no cycle,
ceilings within bounds; golden ids against `origin/main`; computed semver;
the live `main` ruleset equal to its export with `bypass_actors: []`. The
ledger header (milestones/README.md) says which of these held at each tag.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from src.gates import pattern_regex, two_key
from src.validate import codeowners, controls, corpus, edges, golden_ids, overlap, ruleset, semver

GOLDEN_FIELDS = {"id", "kind", "question", "expected", "seat", "added", "retired"}
GOLDEN_ID = re.compile(r"^g-\d{3}$")
MILESTONE_ID = re.compile(r"^M\d{2}$")  # added/retired: dates are in git
KINDS = {"ordinary", "trap", "guardrail", "redteam"}
CITING_KINDS = {"ordinary", "trap"}
CITING_EXPECTED = {"table_row", "clause_id", "answer_fields"}
BLOCK_EXPECTED = {"guardrail": {"BLOCKED", "MASKED"}, "redteam": {"BLOCKED"}}
RULING_FIELDS = {"ruling", "seat", "authorises", "evidence", "pr"}


def _is_milestone_id(value: Any) -> bool:
    return isinstance(value, str) and bool(MILESTONE_ID.match(value))


def load_goldens(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Goldens by file name, plus errors for files that are not a YAML mapping."""
    goldens: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted((root / "evals" / "goldens").glob("v*/*")):
        rel = path.relative_to(root).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: not YAML: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{rel}: not a mapping")
            continue
        goldens[rel] = doc
    return goldens, errors


def check_goldens(root: Path) -> list[str]:
    goldens, errors = load_goldens(root)
    if not goldens and not errors:
        return ["evals/goldens/: no goldens found"]
    seen: dict[str, str] = {}
    for rel, g in goldens.items():
        stem = Path(rel).stem
        if Path(rel).suffix != ".yaml" or not GOLDEN_ID.match(stem):
            errors.append(f"{rel}: file name is not g-NNN.yaml")
        if set(g) != GOLDEN_FIELDS:
            missing, extra = (
                sorted(GOLDEN_FIELDS - set(g)),
                sorted(set(g) - GOLDEN_FIELDS),
            )
            errors.append(
                f"{rel}: fields differ from SPEC/00 section 6 (missing {missing}, extra {extra})"
            )
            continue
        if g["id"] != stem:
            errors.append(f"{rel}: id {g['id']!r} does not equal the file name")
        if g["id"] in seen:
            errors.append(f"{rel}: id {g['id']!r} already used by {seen[g['id']]}")
        seen[g["id"]] = rel
        if g["kind"] not in KINDS:
            errors.append(f"{rel}: kind {g['kind']!r} not in {sorted(KINDS)}")
            continue
        expected = g["expected"]
        if g["kind"] in CITING_KINDS:
            if not isinstance(expected, dict) or set(expected) != CITING_EXPECTED:
                errors.append(
                    f"{rel}: expected must have exactly {sorted(CITING_EXPECTED)}"
                )
            elif (
                not isinstance(expected["answer_fields"], dict)
                or not expected["answer_fields"]
            ):
                errors.append(
                    f"{rel}: expected.answer_fields must be a non-empty mapping"
                )
        elif expected not in BLOCK_EXPECTED[g["kind"]]:
            errors.append(
                f"{rel}: expected must be one of {sorted(BLOCK_EXPECTED[g['kind']])}"
            )
        for field in ("question", "seat"):
            if not isinstance(g[field], str) or not g[field].strip():
                errors.append(f"{rel}: {field} must be a non-empty string")
        if not _is_milestone_id(g["added"]):
            errors.append(f"{rel}: added must be a milestone id (MNN)")
        if g["retired"] is not None and not _is_milestone_id(g["retired"]):
            errors.append(f"{rel}: retired must be null or a milestone id (MNN)")
    return errors


def check_golden_citations(root: Path) -> list[str]:
    rows = {
        r["table_row"]
        for r in json.loads(
            (root / "data" / "rights_table.json").read_text(encoding="utf-8")
        )
    }
    clauses = set(
        json.loads((root / "data" / "clause_index.json").read_text(encoding="utf-8"))
    )
    goldens, _ = load_goldens(root)
    errors = []
    for rel, g in goldens.items():
        expected = g.get("expected")
        if g.get("kind") not in CITING_KINDS or not isinstance(expected, dict):
            continue
        if expected.get("table_row") not in rows:
            errors.append(
                f"{rel}: table_row {expected.get('table_row')!r} is not in data/rights_table.json"
            )
        if expected.get("clause_id") not in clauses:
            errors.append(
                f"{rel}: clause_id {expected.get('clause_id')!r} is not in data/clause_index.json"
            )
    return errors


def front_matter(text: str) -> dict[str, Any] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    doc = yaml.safe_load("\n".join(lines[1:end]))
    return doc if isinstance(doc, dict) else None


def deleted_paths(root: Path) -> set[str]:
    """Every path deleted from the tree somewhere in HEAD's history. Empty when git cannot say.

    A ruling is a record of the PR it merged with, and the paths it named can
    be deleted later (`infra/eval-role/` at M02 PR 3, authorised by four M00
    and M01 rulings). The front-matter check exists to catch a glob that
    names nothing; a glob that names something the tree once had is not
    that, and a past ruling is not edited to keep a check green.
    """
    done = subprocess.run(["git", "log", "--diff-filter=D", "--name-only", "--format="], cwd=root,
                          capture_output=True, text=True)  # fmt: skip
    return set(done.stdout.split()) if done.returncode == 0 else set()


def check_rulings(root: Path) -> list[str]:
    paths = sorted((root / "milestones").glob("*/rulings/*.md"))
    if not paths:
        return ["milestones/*/rulings/: no ruling files found"]
    errors = []
    gone: set[str] | None = None  # read once, only if a glob matches nothing in the tree
    for path in paths:
        rel = path.relative_to(root).as_posix()
        fm = front_matter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rel}: no front matter")
            continue
        missing = sorted(f for f in RULING_FIELDS if fm.get(f) in (None, "", []))
        if missing:
            errors.append(f"{rel}: front matter missing or empty: {missing}")
        for field in ("authorises", "evidence"):
            if fm.get(field) and not isinstance(fm[field], list):
                errors.append(f"{rel}: {field} must be a list")
        if isinstance(fm.get("authorises"), list):
            for pattern in fm["authorises"]:
                if glob.glob(str(pattern), root_dir=root, recursive=True):
                    continue
                if gone is None:
                    gone = deleted_paths(root)
                regex = pattern_regex(str(pattern), anchored=True)
                if any(regex.match(path) for path in gone):
                    continue  # named something the tree once had (M02 PR 3)
                errors.append(
                    f"{rel}: authorises path {pattern!r} matches nothing in the tree, nor anything deleted from it"
                )
    return errors


WORKFLOW_HASHES = "infra/workflows.sha256"
HASH_LINE = re.compile(r"^([0-9a-f]{64})  (\.github/workflows/[^/]+)$")


def file_sha256(path: Path) -> str:
    """sha256 of the file with LF line endings: a CRLF working copy hashes as the repo does."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_workflow_hashes(root: Path) -> list[str]:
    """Every workflow is listed in infra/workflows.sha256 with its hash, and nothing else is.

    What this does not do until M02: a PR that edits a workflow can edit this
    file too (infra/ruleset/README.md).
    """
    listing = root / WORKFLOW_HASHES
    if not listing.is_file():
        return [f"{WORKFLOW_HASHES}: missing"]
    listed: dict[str, str] = {}
    errors = []
    for number, line in enumerate(listing.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        if not (match := HASH_LINE.match(line)):
            errors.append(f"{WORKFLOW_HASHES}:{number}: not '<sha256>  .github/workflows/<file>'")
            continue
        listed[match[2]] = match[1]
    present = {
        p.relative_to(root).as_posix()
        for p in (root / ".github" / "workflows").glob("*")
        if p.is_file()
    }
    errors += [f"{rel}: a workflow file not listed in {WORKFLOW_HASHES}" for rel in sorted(present - set(listed))]
    errors += [f"{rel}: listed in {WORKFLOW_HASHES} and not in the tree" for rel in sorted(set(listed) - present)]
    errors += [
        f"{rel}: sha256 {file_sha256(root / rel)[:12]} is not the {listed[rel][:12]} listed in {WORKFLOW_HASHES}"
        for rel in sorted(present & set(listed))
        if file_sha256(root / rel) != listed[rel]
    ]
    return errors


def check_manifests(root: Path) -> list[str]:
    """Every agents/*/manifest.yaml validates against src/manifest/schema.json (M01 PR 2)."""
    from src import manifest as manifest_module

    paths = manifest_module.paths(root)
    if not paths:
        return ["agents/*/manifest.yaml: none found"]
    errors = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: not YAML: {exc}")
            continue
        errors += [f"{rel}: {error}" for error in manifest_module.schema_errors(doc)]
    return errors


# The two CDK apps, and where each one's committed NagReport lives. The
# report in the tree is the one the synth here just wrote: a suppression a
# reader can see, next to the code that suppressed it.
STACKS = {
    "AgentkeelBootstrap": "infra/bootstrap",
    "AgentkeelRefagent": "infra/construct",
    "AgentkeelIngest": "infra/ingest",  # M03 PR 2
}
NAG_REPORT = "AwsSolutions--{stack}-NagReport.csv"


def check_cdk_nag(root: Path) -> list[str]:
    """Both stacks synthesise, cdk-nag finds nothing non-compliant, and the committed report matches.

    cdk-nag runs as an aspect inside each app, so a Non-Compliant error
    fails the synth and this check reads a non-zero exit. What this adds is
    the report: `make validate` re-writes it and compares, so a suppression
    cannot be added without the CSV beside it changing in the same commit.

    Every suppression must name a seeded case (S3, S4, S5, S6, S8) or a
    SPEC/01 §6 line. One that names neither is a finding, not a
    suppression (Security, M01 PR 2), and this check fails on it.
    """
    errors: list[str] = []
    for stack, folder in STACKS.items():
        app = root / folder / "app.py"
        if not app.is_file():
            errors.append(f"{folder}/app.py: not in the tree")
            continue
        out = root / folder / "cdk.out"
        done = subprocess.run(
            [sys.executable, "-c", f"import runpy; runpy.run_path({str(app)!r}, run_name='__main__')"],
            cwd=root, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(root), "CDK_OUTDIR": str(out)},
        )  # fmt: skip
        if done.returncode != 0:
            tail = (done.stderr.strip().splitlines() or ["no output"])[-1]
            errors.append(f"{folder}/app.py: synth failed: {tail}")
            continue
        written, committed = out / NAG_REPORT.format(stack=stack), root / folder / NAG_REPORT.format(stack=stack)
        if not written.is_file():
            errors.append(f"{folder}: the synth wrote no {written.name}; is cdk-nag still an aspect of the app?")
            continue
        errors += _nag_rows(written, f"{folder}/{written.name}")
        if not committed.is_file():
            errors.append(f"{folder}/{committed.name}: not committed. Copy the one the synth just wrote.")
        elif _rows(committed) != _rows(written):
            errors.append(f"{folder}/{committed.name}: not the report this synth wrote. Copy it and commit it.")
    return errors


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return sorted((dict(row) for row in csv.DictReader(handle)), key=lambda row: sorted(row.items()))


def _nag_rows(path: Path, rel: str) -> list[str]:
    """Nothing non-compliant, and every suppression names what it serves."""
    errors = []
    for row in _rows(path):
        where = f"{rel}: {row['Rule ID']} on {row['Resource ID']}"
        if row["Compliance"] == "Non-Compliant":
            errors.append(f"{where}: non-compliant")
        elif row["Compliance"] == "Suppressed" and not _names_its_case(row["Exception Reason"]):
            errors.append(f"{where}: the suppression names no seeded case (S3, S4, S5, S6, S8) and no "
                          f"SPEC/01 §6 line. That is a finding, not a suppression.")  # fmt: skip
    return errors


def _names_its_case(reason: str) -> bool:
    """`seed S3`, not `the S3 gateway endpoint`: the service name is not the seed.

    From M03 PR 2 a line of SPEC/03 §6 serves as SPEC/01 §6's does, for the ingest stack.
    """
    return bool(re.search(r"\bseeds? S[34568]\b", reason) or "SPEC/01 §6" in reason or "SPEC/03 §6" in reason)


THRESHOLDS = "thresholds.yaml"


def check_relaxes(root: Path) -> list[str]:
    """Every bar in thresholds.yaml has a `relaxes:` entry, up or down, and every entry names a bar (M02 PR 2).

    `two-key` reads the entry to tell a relaxation from a tightening. A
    bar with no entry cannot be moved with one key either, but the
    Threshold Owner is asked to say the direction here, not leave it to
    the gate to refuse both ways.
    """
    try:
        thresholds = yaml.safe_load((root / THRESHOLDS).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"{THRESHOLDS}: unreadable: {exc}"]
    if not isinstance(thresholds, dict):
        return [f"{THRESHOLDS}: not a mapping"]
    bars = two_key.bars(thresholds)
    relaxes = thresholds.get("relaxes")
    if not isinstance(relaxes, dict):
        return [f"{THRESHOLDS}: no relaxes: mapping (Threshold Owner, M02 PR 2)"]
    errors = [f"{THRESHOLDS}: bar {bar} has no relaxes: entry" for bar in sorted(set(bars) - set(relaxes))]
    errors += [f"{THRESHOLDS}: relaxes: names {name}, which is not a bar" for name in sorted(set(relaxes) - set(bars))]
    errors += [f"{THRESHOLDS}: relaxes.{name} is {value!r}, not up or down" for name, value in sorted(relaxes.items())
               if value not in ("up", "down")]  # fmt: skip
    return errors


CHECKS = {
    "golden front matter": check_goldens,
    "golden citations exist in data/": check_golden_citations,
    "ruling front matter": check_rulings,
    "workflow-hash": check_workflow_hashes,
    "manifest schema": check_manifests,
    "cdk-nag, both stacks": check_cdk_nag,
    # M02 PR 2 (SPEC/02 section 6)
    "CODEOWNERS complete, single-owner, logins real": codeowners.check,
    "relaxes: on every bar": check_relaxes,
    "edges two-sided, no cycle, ceilings within bounds": edges.check,
    "golden ids against origin/main": golden_ids.check,
    "computed semver": semver.check,
    "live main ruleset equals its export, bypass_actors []": ruleset.check,
    # M03 PR 2 (SPEC/03 section 6)
    "plant controls name live goldens of their kind": controls.check,
    "golden/corpus overlap (12 words), no row id in the corpus": overlap.check,
    "admitted.yaml is the corpus, byte for byte, under a Data Owner ruling": corpus.check,
}
