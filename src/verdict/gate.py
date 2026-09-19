"""verdict.gate: the only reader that rules on an envelope (P5).

    python -m src.verdict.gate ENVELOPE      exit 0 GREEN, 1 RED or UNMEASURED, 2 REJECTED
    python -m src.verdict.gate --plants      make plants

The gate does not trust the writer. It rejects an envelope that does not
validate, or whose cards are missing, altered or for another commit; a
hand-written envelope gets no pass for being hand-written (F0.2). Then it
works the lists out again from `goldens` and history and goes RED where the
envelope disagrees with itself or with the gate.

Two shapes, told apart by scope (ADR-0004 amendment 2). A control envelope,
M00's form and from M01 the form of any run where no agent ran, holds
`control` results and names its own run's card in `baseline_card_ref`, with
no `control_card_ref`. An agent envelope holds `agent` results only;
`control_card_ref` names this run's control card, and `baseline_card_ref`
names the card at tag `m00`, whose hash `thresholds.yaml` pins; that hash is
checked on agent envelopes only. The three M00 envelopes still validate,
replay and read.

What it rules on (SPEC/00 §5 `regression`, P7, R2, ADR-0004): RED on an
`agent` result that has ever passed and now fails, on a silent plant among
the `agent` results, on a failed check, and on a run over the token cap
(Threshold Owner, M01 item 22).

**Which cap** (ruling m, `milestones/M01/feasibility.md` §2.6). The cap is
read from `thresholds.yaml` **as it stood at the envelope's commit**
(`git show <commit>:thresholds.yaml`), not from the working tree. The
envelope does not record the cap — ADR-0004 has no amendment left — and a
gate that read today's cap would re-rule an old envelope every time the
Threshold Owner moved the number. A commit git cannot resolve falls back
to the tree, and the gate says so.

The pinned base card hash is read from the tree on purpose, and not this
way. The base is frozen (ADR-0004 amendment 2): if it ever changes, every
envelope that names the old one must be rejected loudly, which is what
reading the tree does. A golden that has never passed reports and
does not gate. A `control` result is the baseline's: it is reported, its
drift is printed as a note, and it never blocks.

F1.4 (SPEC/01 §4), worked out here again, not taken from build: an agent's
ordinary or trap answer passes only if it cites, and `checks.F1_4` fails
when any ordinary answer does not.

What it cannot see: a hand-written envelope that validates, points at real
cards and agrees with itself. Nothing signs an envelope yet.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from src.verdict import (
    ROOT,
    canonical_sha256,
    load_golden_kinds,
    plants,
    replay_history,
    schema_errors,
)

__all__ = ["Rejected", "cap_at", "control_drift", "judge", "measured", "measured_at", "read", "rule",
           "schema_errors", "thresholds_at"]

GOLDENS = ROOT / "evals" / "goldens" / "v1"
HISTORY = ROOT / "evals" / "history"
THRESHOLDS = ROOT / "thresholds.yaml"
CITING_KINDS = {"ordinary", "trap"}


class Rejected(Exception):
    """Not an envelope the gate will rule on."""


def thresholds(path: Path = THRESHOLDS) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def thresholds_at(commit: str, root: Path = ROOT) -> tuple[dict[str, Any], str]:
    """`thresholds.yaml` as it stood at `commit`, and where it was read (ruling m).

    A later cap change must not re-rule an envelope that was written under
    the old one. When git cannot resolve the commit — a test, a shallow
    clone — the tree is used and the caller says so in the output.
    """
    done = subprocess.run(
        ["git", "show", f"{commit}:thresholds.yaml"], cwd=root, capture_output=True, text=True
    )
    if done.returncode != 0:
        return thresholds(root / "thresholds.yaml"), "the working tree"
    loaded = yaml.safe_load(done.stdout)
    return (loaded if isinstance(loaded, dict) else {}), f"{commit[:12]}, the envelope's own commit"


def cap_at(commit: str, root: Path = ROOT) -> tuple[int, str]:
    """The token cap that applied when this envelope was written."""
    bars, where = thresholds_at(commit, root)
    cap = (bars.get("cost_cap") or {}).get("tokens_per_run")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap <= 0:
        # build refuses a missing cap; the gate does not read a deleted bar as "no cap" either
        raise Rejected(f"thresholds.yaml cost_cap.tokens_per_run at {where} "
                       f"must be a positive integer, got {cap!r}")  # fmt: skip
    return cap, where


def card_at(path: Path, ref: Any, root: Path, field: str) -> dict[str, Any]:
    """The card `ref` names, if it resolves, hashes to `ref`, and says scope control."""
    if not isinstance(ref, dict):
        raise Rejected(f"{path}: no {field}")
    card_path = Path(ref["path"]) if Path(ref["path"]).is_absolute() else root / ref["path"]
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Rejected(f"{path}: {field} {ref['path']} does not resolve: {exc}") from exc
    if canonical_sha256(card) != ref["sha256"]:
        raise Rejected(f"{path}: {field} {ref['path']} is not the one the envelope names")
    if card.get("scope") != "control":
        raise Rejected(f"{path}: {field} {ref['path']} does not say scope: control")
    return card


def read(path: Path, root: Path = ROOT) -> dict[str, Any]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Rejected(f"{path}: unreadable: {exc}") from exc
    if errors := schema_errors(envelope):
        raise Rejected(f"{path}: does not validate: " + "; ".join(errors))

    scopes = {result["scope"] for result in envelope["goldens"].values()}
    if "agent" in scopes:
        return read_agent(path, envelope, scopes, root)
    if envelope.get("control_card_ref") is not None:
        raise Rejected(f"{path}: control results beside a control_card_ref: a control envelope's base is its own card")
    if claim_1 := sorted(name for name in envelope["checks"] if name.startswith("F1_")):
        raise Rejected(f"{path}: a control envelope carries {claim_1}: claim 1 is read on an agent envelope only")

    card = card_at(path, envelope["baseline_card_ref"], root, "baseline_card_ref")
    if card.get("commit") != envelope["commit"]:
        raise Rejected(f"{path}: baseline card is for {card.get('commit')}, not {envelope['commit']}")
    # `control` is not a label an envelope can give itself to get out from
    # under the bar. A control result is the card's result, or it is rejected.
    for golden_id, result in envelope["goldens"].items():
        unscoped = {name: value for name, value in result.items() if name != "scope"}
        if unscoped != card.get("goldens", {}).get(golden_id):
            raise Rejected(f"{path}: {golden_id} says scope control and differs from the baseline card")
    return envelope


def read_agent(path: Path, envelope: dict[str, Any], scopes: set[str], root: Path) -> dict[str, Any]:
    """From M01: one subject, two cards (ADR-0004 amendment 2)."""
    if scopes != {"agent"}:
        raise Rejected(f"{path}: an envelope holds one subject; the control is its card, not its results")
    for field in ("control_card_ref", "tokens_in"):
        if envelope.get(field) is None:
            raise Rejected(f"{path}: an agent envelope without {field}")
    pinned = (thresholds(root / "thresholds.yaml").get("baseline_card") or {}).get("sha256")
    if envelope["baseline_card_ref"]["sha256"] != pinned:
        raise Rejected(f"{path}: baseline_card_ref is not the card at tag m00 that thresholds.yaml pins")
    card_at(path, envelope["baseline_card_ref"], root, "baseline_card_ref")
    control = card_at(path, envelope["control_card_ref"], root, "control_card_ref")
    if control.get("commit") != envelope["commit"]:
        raise Rejected(f"{path}: control card is for {control.get('commit')}, not {envelope['commit']}")
    return envelope


def f1_4(results: dict[str, dict[str, Any]]) -> str:
    """The gate's own reading of F1.4 (SPEC/01 §4). build has one too; they are not shared (P5)."""
    uncited = [g for g, r in results.items() if r["scope"] == "agent" and r["kind"] == "ordinary" and r["cites"] is not True]
    return "fail" if uncited else "pass"


def judge(
    envelope: dict[str, Any],
    kinds: dict[str, str],
    history: replay_history.History,
    plant_ids: list[str],
    cap: int | None = None,
) -> tuple[str, list[str]]:
    """The gate's own verdict and its reasons. `envelope` has passed `read`."""
    results = envelope["goldens"]
    reasons: list[str] = []

    if {g: r["kind"] for g, r in results.items()} != kinds:
        reasons.append("the envelope's goldens are not the goldens in the tree")
    for g, r in results.items():
        if r["scope"] == "agent" and r["kind"] in CITING_KINDS:
            if r["pass"] != (r["score"] and r["cites"] is True):
                reasons.append(f"{g}: pass is not score and cites (F1.4)")
        elif r["pass"] != r["score"]:
            reasons.append(f"{g}: pass is not score")

    # Only `agent` results are gated: the bar, and the plants (ADR-0004).
    failing = [g for g in sorted(results) if not results[g]["pass"]]
    passed_before = {g for g in failing if replay_history.ever_passed(history, results[g]["scope"], g)}
    regressed = [g for g in failing if results[g]["scope"] == "agent" and g in passed_before]
    never_passed = [g for g in failing if g not in passed_before]
    plant_ids = [g for g in plant_ids if results.get(g, {}).get("scope") == "agent"]
    fired = sum(results[g]["pass"] for g in plant_ids)

    for name, mine in (("regressed", regressed), ("never_passed", never_passed)):
        if sorted(envelope[name]) != mine:
            reasons.append(f"envelope says {name}={sorted(envelope[name])}, the gate reads {mine}")
    if envelope["plants_expected"] != len(plant_ids):
        reasons.append(
            f"envelope says plants_expected={envelope['plants_expected']}, the plant rule gives {len(plant_ids)}"
        )
    if envelope["plants_fired"] != fired:
        reasons.append(f"envelope says plants_fired={envelope['plants_fired']}, the gate reads {fired}")

    reasons += [f"regressed: {g} has passed before and fails now" for g in regressed]
    if fired != len(plant_ids):
        reasons.append(f"silent plant: expected {len(plant_ids)}, fired {fired}")
    if any(r["scope"] == "agent" for r in results.values()):
        said = envelope["checks"].get("F1_4")
        mine_f1_4 = f1_4(results)
        if said is None:
            reasons.append("checks.F1_4 is missing from an agent envelope")
        elif said["status"] != mine_f1_4:
            reasons.append(f"envelope says F1_4 is {said['status']}, the gate reads {mine_f1_4}")
    reasons += [
        f"check {name} failed: {check['url']}"
        for name, check in sorted(envelope["checks"].items())
        if check["status"] == "fail"
    ]

    # An over-cap run is a recorded RED, whatever else it measured (M01 item 22).
    over_cap = cap is not None and "tokens_in" in envelope and envelope["tokens_in"] + envelope["tokens_out"] > cap
    if over_cap:
        reasons.append(f"cost-cap: {envelope['tokens_in'] + envelope['tokens_out']} over {cap}")
    if envelope["verdict"] == "UNMEASURED" and not over_cap:
        return "UNMEASURED", reasons + ["the run did not measure: a call failed"]
    verdict = "RED" if reasons else "GREEN"
    if envelope["verdict"] != verdict:
        reasons.append(f"build said {envelope['verdict']}, the gate says {verdict}")
        verdict = "RED"
    return verdict, reasons


def control_drift(envelope: dict[str, Any], history: replay_history.History) -> list[str]:
    """Control goldens that passed in a past run and fail in this one. A note, never a reason (F0.4)."""
    return sorted(
        g
        for g, r in envelope["goldens"].items()
        if r["scope"] == "control" and not r["pass"] and replay_history.ever_passed(history, "control", g)
    )


def tallies(label: str, results: dict[str, dict[str, Any]]) -> str:
    """`label: traps a/3 (ids); ordinary b/9; guardrail c/3`, from results keyed by golden id."""

    def tally(kind: str) -> str:
        of_kind = [r for r in results.values() if r["kind"] == kind]
        return f"{sum(r['pass'] for r in of_kind)}/{len(of_kind)}"

    traps = sorted(g for g, r in results.items() if r["kind"] == "trap" and r["pass"])
    return (
        f"{label}: traps {tally('trap')}" + (f" ({', '.join(traps)})" if traps else "")
        + f"; ordinary {tally('ordinary')}; guardrail {tally('guardrail')}"
    )


def measured(envelope: dict[str, Any], verdict: str, control_card: dict[str, Any] | None = None) -> str:
    """The ledger's Measured cell. `verdict` is the gate's own (`rule`), never the envelope's.

    An M00 envelope: its control tallies. From M01: the agent's tallies, then
    this run's control card's, then the base the numbers are a delta against.
    """
    results = envelope["goldens"]
    agent = {g: r for g, r in results.items() if r["scope"] == "agent"}
    if agent:
        if control_card is None:
            raise ValueError("an agent envelope's cell needs its control card")
        heads = [tallies("agent", agent), tallies("control", control_card["goldens"])]
    else:
        heads = [tallies("control", results)]
    parts = [
        *heads,
        f"never_passed {len(envelope['never_passed'])}",
        f"regressed {len(envelope['regressed'])}",
        f"plants {envelope['plants_fired']}/{envelope['plants_expected']}",
        *(f"{name} {c['status']} {c['url']}" for name, c in sorted(envelope["checks"].items())),
        verdict,
        f"envelope `{envelope['commit']}`",
    ]
    if agent:
        parts.append(f"base {envelope['baseline_card_ref']['sha256'][:8]}")
    return "; ".join(parts)


def latest(history_dir: Path = HISTORY) -> Path | None:
    """The envelope for the nearest commit at or behind HEAD."""
    have = {p.stem: p for p in replay_history.envelope_paths(history_dir)}
    commits = subprocess.run(
        ["git", "rev-list", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return next((have[c] for c in commits if c in have), None)


def rule(path: Path, history_dir: Path = HISTORY) -> tuple[str, list[str]]:
    envelope = read(path)
    try:
        history = replay_history.load(history_dir, exclude_commit=envelope["commit"])
    except ValueError as exc:  # a bad file in history: the gate cannot rule, which is not RED
        raise Rejected(f"history cannot be replayed: {exc}") from exc
    kinds = load_golden_kinds(GOLDENS)
    cap, _ = cap_at(envelope["commit"])
    return judge(envelope, kinds, history, plants.plant_ids(kinds, ROOT), cap)


def control_card_of(envelope: dict[str, Any], path: Path, root: Path = ROOT) -> dict[str, Any] | None:
    ref = envelope.get("control_card_ref")
    return card_at(path, ref, root, "control_card_ref") if ref else None


def measured_at(path: Path, history_dir: Path = HISTORY) -> str:
    """What `make ledger` holds a Measured cell to: the envelope's numbers under the gate's verdict."""
    verdict, _ = rule(path, history_dir)
    envelope = read(path)
    return measured(envelope, verdict, control_card_of(envelope, path))


def control_against_base(envelope: dict[str, Any], path: Path, root: Path = ROOT) -> str | None:
    """This run's control card beside the card at tag m00. Printed, never gated (Finding F0.4)."""
    control = control_card_of(envelope, path, root)
    if control is None:
        return None
    base = card_at(path, envelope["baseline_card_ref"], root, "baseline_card_ref")
    return f"{tallies('control this run', control['goldens'])} | {tallies('base at m00', base['goldens'])}"


def print_plants() -> int:
    kinds = load_golden_kinds(GOLDENS)
    plant_ids = plants.plant_ids(kinds, ROOT)
    path = latest()
    try:
        results = read(path)["goldens"] if path else {}
    except Rejected as rejection:
        print(f"REJECTED {rejection}")
        return 2
    print(f"plants_expected = {len(plant_ids)}")
    for g in plant_ids:
        fired = {True: "fired", False: "SILENT", None: "not run"}[results.get(g, {}).get("pass")]
        print(f"  {g} {kinds[g]:<9} {fired}")
    waiting = sorted(g for g, k in kinds.items() if k in ("guardrail", "redteam") and g not in plant_ids)
    if waiting:
        print("not plants until their enforcing control is in the repo (SPEC/00 section 5):")
        print("  " + " ".join(waiting))
    print(f"last run: {path.relative_to(ROOT).as_posix() if path else 'no CI-written envelope yet'}")
    print("seeded cases (SPEC/01 section 5; not plants, not in plants_expected):")
    for seed, (falsifier, planted, reader) in plants.SEEDS.items():
        state = "in the tree" if (ROOT / reader).exists() else "not in the tree yet"
        print(f"  {seed} {falsifier} {planted}")
        print(f"         reader {reader}: {state}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("envelope", nargs="?", type=Path)
    parser.add_argument("--history-dir", type=Path, default=HISTORY)
    parser.add_argument("--plants", action="store_true")
    args = parser.parse_args(argv)
    if args.plants:
        return print_plants()
    if args.envelope is None:
        parser.error("an envelope path, or --plants")
    try:
        verdict, reasons = rule(args.envelope, args.history_dir)
    except Rejected as rejection:
        print(f"REJECTED {rejection}")
        return 2
    print(f"{verdict} {args.envelope}")
    for reason in reasons:
        print(f"  {reason}")
    envelope = read(args.envelope)
    # Which cap ruled this envelope, and where it was read (ruling m).
    cap, where = cap_at(envelope["commit"])
    print(f"  note: cost_cap {cap} read at {where}")
    history = replay_history.load(args.history_dir, exclude_commit=envelope["commit"])
    for golden_id in control_drift(envelope, history):
        print(f"  note: control {golden_id} has passed before and fails now; not gated (Finding F0.4)")
    if against := control_against_base(envelope, args.envelope):
        print(f"  note: {against}; not gated (Finding F0.4)")
    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
