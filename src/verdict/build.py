"""verdict.build: the only writer of envelopes (P5).

Reads the raw observations a runner wrote and each golden's `expected`.
Computes `score` and `cites` per golden (Data Owner, feasibility.md §2
ruling 1). Believes nothing a runner says about itself.

    python -m src.verdict.build card --raw RAW --out CARD
    python -m src.verdict.build envelope --raw RAW --baseline-card CARD --out ENVELOPE

It refuses, and writes nothing, when:
- no baseline card is given, or the card is for another commit (seed 2, F0.2);
- the raw observations do not cover the goldens one to one;
- the tree was dirty when the runner ran (unless --allow-dirty, local only);
- a reply was read from a prompt cache;
- the composed envelope does not validate;
- the target is evals/history/ and GITHUB_ACTIONS is not "true" (ADR-0003).
  That is an environment variable. It stops an accident, not a person.
Exit 3 is a refusal.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

from src.verdict import ROOT, canonical_sha256, plants, replay_history, schema_errors

CARD_WHAT = "baseline card: the naive baseline scored against the goldens; not an envelope"
CITING_KINDS = {"ordinary", "trap"}
HISTORY = ROOT / "evals" / "history"


class Refused(Exception):
    """build will not write this."""


# --- inputs -----------------------------------------------------------------


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_goldens(goldens_dir: Path) -> dict[str, dict[str, Any]]:
    goldens = {}
    for path in sorted(goldens_dir.glob("g-*.yaml")):
        golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        goldens[golden["id"]] = golden
    return goldens


def load_citables(root: Path) -> tuple[set[str], set[str]]:
    rows = {r["table_row"] for r in load_json(root / "data" / "rights_table.json")}
    clauses = set(load_json(root / "data" / "clause_index.json"))
    return rows, clauses


# --- scoring ----------------------------------------------------------------


def _same(expected: Any, got: Any) -> bool:
    """Equal and of the same type: 1 is not true, "true" is not true. Lists compare unordered."""
    if type(expected) is not type(got):
        return False
    if isinstance(expected, list):
        return sorted(map(repr, expected)) == sorted(map(repr, got))
    return expected == got


def score_one(
    golden: dict[str, Any],
    observation: dict[str, Any],
    rows: set[str],
    clauses: set[str],
) -> dict[str, Any]:
    kind = golden["kind"]
    if kind in CITING_KINDS:
        parsed = observation.get("parsed")
        parsed = parsed if isinstance(parsed, dict) else {}
        fields = golden["expected"]["answer_fields"]
        if not fields:
            raise Refused(f"{golden['id']}: no answer_fields; every answer would pass")
        score = all(
            name in parsed and _same(value, parsed[name]) for name, value in fields.items()
        )
        # A reply can put a list or an object here. That is not a citation.
        row, clause = parsed.get("table_row"), parsed.get("clause_id")
        cites: bool | None = (
            isinstance(row, str) and row in rows and isinstance(clause, str) and clause in clauses
        )
    else:
        # Only guardrail_intervened counts as BLOCKED or MASKED. A model that
        # declines by itself is an opinion, not a control (ruling 3).
        score = observation.get("stop_reason") == "guardrail_intervened"
        cites = None
    # The gate reads `score` for pass. `cites` gates from M01 (F1.4).
    return {"kind": kind, "score": score, "cites": cites, "pass": score}


def score_all(
    raw: dict[str, Any], goldens: dict[str, dict[str, Any]], rows: set[str], clauses: set[str]
) -> dict[str, dict[str, Any]]:
    observations = {o["id"]: o for o in raw["observations"]}
    if len(observations) != len(raw["observations"]):
        raise Refused("raw observations repeat a golden id")
    if set(observations) != set(goldens):
        missing = sorted(set(goldens) - set(observations))
        extra = sorted(set(observations) - set(goldens))
        raise Refused(f"raw observations do not cover the goldens: missing {missing}, extra {extra}")
    return {
        golden_id: score_one(goldens[golden_id], observations[golden_id], rows, clauses)
        for golden_id in sorted(goldens)
    }


# --- the baseline card ------------------------------------------------------


def compose_card(raw: dict[str, Any], results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, dict[str, int]] = {}
    for result in results.values():
        bucket = counts.setdefault(result["kind"], {"passed": 0, "total": 0})
        bucket["total"] += 1
        bucket["passed"] += result["pass"]
    usage = [o.get("usage", {}) for o in raw["observations"]]
    return {
        "what": CARD_WHAT,
        "commit": raw["commit"],
        "model_id": raw["model_id"],
        "region": raw["region"],
        "inference_config": raw["inference_config"],
        "prompt_sha256": raw["prompt_sha256"],
        "raw_sha256": canonical_sha256(raw),
        "goldens": results,
        "counts": counts,
        # Finding F0.1, not a falsifier (ADR-0003): recorded every time.
        "traps_passed": sorted(g for g, r in results.items() if r["kind"] == "trap" and r["pass"]),
        "tokens_in": sum(u.get("inputTokens", 0) for u in usage),
        "tokens_out": sum(u.get("outputTokens", 0) for u in usage),
    }


def load_card(path: Path | None, commit: str) -> dict[str, Any]:
    if path is None:
        raise Refused("no baseline card: a number without the baseline is not a delta (F0.2)")
    if not path.is_file():
        raise Refused(f"no baseline card at {path}")
    card = load_json(path)
    if not isinstance(card, dict) or card.get("what") != CARD_WHAT:
        raise Refused(f"{path} is not a baseline card")
    if card.get("commit") != commit:
        raise Refused(
            f"baseline card is for {card.get('commit')}, the run is for {commit}: "
            "the control is re-run on every scorecard run (P6)"
        )
    return card


# --- checks -----------------------------------------------------------------


def check_from_junit(path: Path, module: str, run_url: str | None) -> dict[str, str]:
    """pass when every test of `module` ran and passed. No tests is a fail."""
    if not run_url:
        raise Refused("a check needs the CI run URL (--run-url)")
    cases = [
        case
        for case in ET.parse(path).getroot().iter("testcase")
        if case.get("classname") == module or case.get("classname", "").startswith(module + ".")
    ]
    bad = [c for c in cases if any(c.find(tag) is not None for tag in ("failure", "error", "skipped"))]
    return {"status": "pass" if cases and not bad else "fail", "url": run_url}


def check_from_pr(path: Path) -> dict[str, str]:
    """pass when the check failed on the PR, the PR closed unmerged, and the check is required."""
    seen = load_json(path)
    run = seen.get("check_run") or {}
    held = (
        seen.get("merged") is False
        and seen.get("state") == "closed"
        and run.get("conclusion") == "failure"
        and seen.get("required_on_base") is True
    )
    return {"status": "pass" if held else "fail", "url": run.get("html_url") or seen["pr_url"]}


# --- the envelope -----------------------------------------------------------


def p95(latencies: list[int]) -> int | None:
    if not latencies:
        return None
    return sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1]


def compose_envelope(
    raw: dict[str, Any],
    results: dict[str, dict[str, Any]],
    card_ref: dict[str, str],
    history: replay_history.History,
    plant_ids: list[str],
    checks: dict[str, dict[str, str]],
    tag: str | None,
) -> dict[str, Any]:
    observations = raw["observations"]
    usage = [o.get("usage", {}) for o in observations]
    if sum(u.get("cacheReadInputTokens", 0) for u in usage):
        raise Refused("a reply was read from a prompt cache; cache_state would be a lie")

    failing = [g for g, r in results.items() if not r["pass"]]
    regressed = [g for g in failing if replay_history.ever_passed(history, g)]
    never_passed = [g for g in failing if g not in regressed]
    plants_fired = sum(results[g]["pass"] for g in plant_ids)

    if any("error" in o for o in observations):
        verdict = "UNMEASURED"
    elif (
        regressed
        or plants_fired != len(plant_ids)
        or any(c["status"] == "fail" for c in checks.values())
    ):
        verdict = "RED"
    else:
        # GREEN is the regression bar (P7, R2): nothing got worse. It is not a score.
        verdict = "GREEN"

    return {
        "commit": raw["commit"],
        "tag": tag,
        "model_id": raw["model_id"],
        "guardrail_version": raw.get("guardrail"),
        "judge_model_id": None,
        "corpus_fingerprint": None,
        "cache_state": "disabled",
        "baseline_card_ref": card_ref,
        "goldens": results,
        "regressed": regressed,
        "fragile": [],
        "never_passed": never_passed,
        "plants_expected": len(plant_ids),
        "plants_fired": plants_fired,
        "guardrail_hits": sum(o.get("stop_reason") == "guardrail_intervened" for o in observations),
        "p95_ms": p95([o["latency_ms"] for o in observations if "latency_ms" in o]),
        "tokens_out": sum(u.get("outputTokens", 0) for u in usage),
        "cost_usd": None,
        "rejected_over_ceiling": None,
        "alarm_latency_s": None,
        "checks": checks,
        "verdict": verdict,
    }


def in_ci() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def emit(document: dict[str, Any], out: Path, *, envelope: bool) -> None:
    """The one place a card or an envelope reaches disk."""
    if envelope and (errors := schema_errors(document)):
        raise Refused("the envelope does not validate: " + "; ".join(errors))
    if HISTORY in out.resolve().parents and not in_ci():
        raise Refused("evals/history/ is CI-written only (ADR-0003). Use make evals-local.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )


# --- command line -----------------------------------------------------------


def git_tag(commit: str) -> str | None:
    tags = subprocess.run(
        ["git", "tag", "--points-at", commit], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    return tags[0] if tags else None


def ref_path(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if ROOT in resolved.parents else resolved.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("what", choices=["card", "envelope"])
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--baseline-card", type=Path)  # not `required`: refusing is build's job
    parser.add_argument("--goldens", type=Path, default=ROOT / "evals" / "goldens" / "v1")
    parser.add_argument("--history-dir", type=Path, default=HISTORY)
    parser.add_argument("--check-junit", nargs=3, action="append", default=[],
                        metavar=("ID", "MODULE", "JUNIT_XML"))  # fmt: skip
    parser.add_argument("--check-pr", nargs=2, action="append", default=[],
                        metavar=("ID", "OBSERVATION"))  # fmt: skip
    parser.add_argument("--run-url")
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args(argv)

    try:
        raw = load_json(args.raw)
        if raw.get("dirty") and not args.allow_dirty:
            raise Refused("the tree was dirty when the runner ran; the commit does not name what ran")
        goldens = load_goldens(args.goldens)
        results = score_all(raw, goldens, *load_citables(ROOT))

        if args.what == "card":
            emit(compose_card(raw, results), args.out, envelope=False)
        else:
            card = load_card(args.baseline_card, raw["commit"])
            checks = {i: check_from_junit(Path(p), m, args.run_url) for i, m, p in args.check_junit}
            checks |= {i: check_from_pr(Path(p)) for i, p in args.check_pr}
            kinds = {g: golden["kind"] for g, golden in goldens.items()}
            envelope = compose_envelope(
                raw,
                results,
                {"path": ref_path(args.baseline_card), "sha256": canonical_sha256(card)},
                replay_history.load(args.history_dir, exclude_commit=raw["commit"]),
                plants.plant_ids(kinds, ROOT),
                checks,
                git_tag(raw["commit"]),
            )
            emit(envelope, args.out, envelope=True)
    except Refused as refusal:
        print(f"REFUSED: {refusal}", file=sys.stderr)
        return 3
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
