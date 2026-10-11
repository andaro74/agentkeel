"""The add-only merge of an agent's rules onto the platform baseline, and its refusals (SPEC/09 §2, §6; ADR-0014 decision 3).

Read by the platform check (`src/validate/agent.evaluate`, "an agent's rules
on the platform baseline, add-only"), by the construct that builds an agent's
guardrail from the merged rules (`infra/construct/governed_agent.py`), by the
bootstrap stack for refagent's (`infra/bootstrap/app.py`) and by `validate`
for the baseline itself. Four names `tests/test_m09_seeds.py` fixes:

- `load(path)`: a rules file as a mapping, or a `ValueError` naming the file.
- `merge(baseline, agent)`: the merged rules. The baseline plus what the
  agent file adds; a key absent from the agent file inherits, an empty list
  adds nothing and removes nothing, an identical entry dedupes, the agent's
  messages replace the baseline's, `topics_apply_to` takes the stricter.
  It merges whatever it is given; `merge_errors` says what is wrong.
- `merge_errors(baseline, agent)`: every way the agent file removes, weakens
  or redefines a baseline rule, naming the rule and the way: a baseline
  topic's name in its `denied_topics` (a redefinition, examples included; by
  case or whitespace too), a baseline PII entity with any action but the
  baseline's (`ANONYMIZE` to `NONE` is seed S2), a `content_filters` key
  that is not the baseline's own (the filters are the baseline's alone), a
  `topics_apply_to` outside the two values, a key this format does not have
  (a misspelled `pii:` cannot add nothing silently), a topic named twice,
  a topic outside Bedrock's limits, or more than 30 topics in the sum,
  naming the file that took it over (R5).
- `rules_errors(agent_dir, rules=None)`: the platform check's reading of
  one agent folder: the baseline's own errors, the merge's, and each
  control's plants: a guardrail-kind plant in `rules/guardrail.yaml` and a
  red-team one in `rules/redteam.yaml`, each with a `blocks` entry naming a
  rule the merged guardrail builds, each a live golden of that kind in the
  agent's `goldens/`. `rules` stands in for the guardrail file's content
  (the seed tests hand S5's two files in this way).

`digest(baseline_bytes, *agent_files)` is the digest a guardrail version's
description carries: sha256 over the baseline and the agent's rule files,
LF line endings, in that order (as `guardrail_spec` has computed refagent's
since M03). The construct writes it; the observer computes it again from
the agent repository's merge commit and `rules/baseline.yaml` on `main`
(SPEC/09 §4, F9.1), through this function on bytes it fetched itself.

Nothing here reads AWS, GitHub or an envelope.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "rules/baseline.yaml"
# The two control files an agent repository may carry, each with the golden kind its plants are.
CONTROLS = {"guardrail.yaml": "guardrail", "redteam.yaml": "redteam"}
BASELINE_KEYS = {"topics_apply_to", "denied_topics", "pii", "content_filters", "messages"}
AGENT_KEYS = {"plants", "blocks", "topics_apply_to", "denied_topics", "pii", "content_filters", "messages"}
REDTEAM_KEYS = {"plants", "blocks"}
APPLIES = ("input", "input and output")  # weakest first; the merge takes the stricter
ACTIONS = ("BLOCK", "ANONYMIZE", "NONE")  # Bedrock's PII actions, strongest first (ADR-0009 entry 5's order)
# Bedrock's limits on a denied topic, as infra/bootstrap/app.py has held refagent's at synth since M03.
TOPIC_NAME = re.compile(r"^[0-9a-zA-Z\-_ !?.]{1,100}$")
TOPIC_DEFINITION_MAX, TOPIC_EXAMPLE_MAX, TOPIC_EXAMPLES_MAX, TOPICS_MAX = 200, 100, 5, 30
GOLDEN_ID = re.compile(r"^g-\d{3}$")


def load(path: Path) -> dict[str, Any]:
    """A rules file as a mapping. Not YAML, or not a mapping, is a `ValueError` naming the file."""
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"{path.as_posix()}: unreadable ({exc.__class__.__name__})") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path.as_posix()}: not a mapping")
    return loaded


def digest(baseline: bytes, *agent_files: bytes) -> str:
    """sha256 over the baseline then each agent file, LF endings, which a built guardrail's version description carries."""
    return hashlib.sha256(b"".join(part.replace(b"\r\n", b"\n") for part in (baseline, *agent_files))).hexdigest()


def _name_key(name: Any) -> str:
    """A topic name as the merge compares it: case and surrounding or repeated whitespace do not make a new name."""
    return " ".join(str(name).split()).lower()


def _topics(doc: dict[str, Any]) -> list[dict[str, Any]]:
    topics = doc.get("denied_topics")
    return [t for t in topics if isinstance(t, dict)] if isinstance(topics, list) else []


def _pii(doc: dict[str, Any]) -> list[dict[str, Any]]:
    entries = doc.get("pii")
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def _stricter(first: Any, second: Any) -> Any:
    """`input and output` over `input`; a value outside the two is left for `merge_errors` to name."""
    ranked = [v for v in (first, second) if v in APPLIES]
    return max(ranked, key=APPLIES.index) if ranked else (second if second is not None else first)


def merge(baseline: dict[str, Any], agent: dict[str, Any]) -> dict[str, Any]:
    """The baseline plus what the agent file adds; nothing of the baseline's is removed or weakened here."""
    merged: dict[str, Any] = {
        "topics_apply_to": _stricter(baseline.get("topics_apply_to"), agent.get("topics_apply_to")),
        "denied_topics": [dict(t) for t in _topics(baseline)],
        "pii": [dict(e) for e in _pii(baseline)],
        "content_filters": dict(baseline.get("content_filters") or {}),
        "messages": {**(baseline.get("messages") if isinstance(baseline.get("messages"), dict) else {}),
                     **(agent.get("messages") if isinstance(agent.get("messages"), dict) else {})},
    }
    base_names = {_name_key(t.get("name")) for t in merged["denied_topics"]}
    for topic in _topics(agent):
        if _name_key(topic.get("name")) not in base_names:  # a redefinition is refused, never merged over
            merged["denied_topics"].append(dict(topic))
            base_names.add(_name_key(topic.get("name")))
    base_entities = {e.get("entity") for e in merged["pii"]}
    for entry in _pii(agent):
        if entry.get("entity") not in base_entities:  # a listed entity dedupes or is refused, never replaced
            merged["pii"].append(dict(entry))
            base_entities.add(entry.get("entity"))
    for key in ("plants", "blocks"):
        if key in agent:
            merged[key] = agent[key]
    return merged


def baseline_errors(baseline: Any, where: str = BASELINE) -> list[str]:
    """What the platform's own file may not do: plant, block, carry a key outside its format, or turn the filter on."""
    if not isinstance(baseline, dict):
        return [f"{where}: not a mapping"]
    errors = []
    for key in sorted(set(baseline) - BASELINE_KEYS):
        errors.append(f"{where}: key {key!r} is not in the format" + (" (a baseline plants nothing; SPEC/09 section 2)"
                                                                        if key in ("plants", "blocks") else ""))
    for key in sorted(BASELINE_KEYS - set(baseline)):
        errors.append(f"{where}: no {key}; the baseline carries every key of the format")
    if baseline.get("topics_apply_to") not in APPLIES:
        errors.append(f"{where}: topics_apply_to is {baseline.get('topics_apply_to')!r}, not one of {list(APPLIES)}")
    if not isinstance(baseline.get("denied_topics"), list):
        errors.append(f"{where}: denied_topics is not a list")
    if not isinstance(baseline.get("pii"), list):
        errors.append(f"{where}: pii is not a list")
    if (baseline.get("content_filters") or {}).get("prompt_attack") is not False:
        errors.append(f"{where}: the prompt-attack filter is off (the Rule Owner, M03 PR 2; R1 at M09 PR 2); say so")
    messages = baseline.get("messages")
    if not isinstance(messages, dict) or set(messages) != {"blocked_input", "blocked_output"}:
        errors.append(f"{where}: messages carries blocked_input and blocked_output")
    errors += _topic_errors(_topics(baseline), where)
    errors += _pii_errors(_pii(baseline), where)
    return errors


def _topic_errors(topics: list[dict[str, Any]], where: str) -> list[str]:
    errors = []
    seen: set[str] = set()
    for topic in topics:
        name = topic.get("name")
        if not isinstance(name, str) or not TOPIC_NAME.match(name):
            errors.append(f"{where}: topic {name!r} is not a name of 1 to 100 of [0-9a-zA-Z-_ !?.]")
            continue
        if _name_key(name) in seen:
            errors.append(f"{where}: topic {name!r} is named twice")
        seen.add(_name_key(name))
        definition, examples = topic.get("definition"), topic.get("examples") or []
        if not isinstance(definition, str) or not 0 < len(definition) <= TOPIC_DEFINITION_MAX:
            errors.append(f"{where}: topic {name!r}: definition is not 1 to {TOPIC_DEFINITION_MAX} characters")
        if not isinstance(examples, list) or len(examples) > TOPIC_EXAMPLES_MAX \
                or not all(isinstance(e, str) and len(e) <= TOPIC_EXAMPLE_MAX for e in examples):  # fmt: skip
            errors.append(f"{where}: topic {name!r}: at most {TOPIC_EXAMPLES_MAX} examples of at most "
                          f"{TOPIC_EXAMPLE_MAX} characters")  # fmt: skip
    return errors


def _pii_errors(entries: list[dict[str, Any]], where: str) -> list[str]:
    errors = []
    seen: set[str] = set()
    for entry in entries:
        entity, action = entry.get("entity"), entry.get("action")
        if not isinstance(entity, str) or not entity:
            errors.append(f"{where}: a pii entry with no entity")
            continue
        if action not in ACTIONS:
            errors.append(f"{where}: pii {entity}: action {action!r} is not one of {list(ACTIONS)}")
        if entity in seen:
            errors.append(f"{where}: pii {entity} is listed twice")
        seen.add(entity)
    return errors


def merge_errors(baseline: dict[str, Any], agent: Any, where: str = "rules/guardrail.yaml") -> list[str]:
    """Every way `agent` removes, weakens or redefines a baseline rule, each naming the rule and the way."""
    if not isinstance(agent, dict):
        return [f"{where}: not a mapping"]
    errors = [f"{where}: key {key!r} is not in the format; an agent file carries {sorted(AGENT_KEYS)} "
              f"and nothing else, so a misspelled key cannot add nothing silently"
              for key in sorted(set(agent) - AGENT_KEYS)]  # fmt: skip
    applies = agent.get("topics_apply_to")
    if applies is not None and applies not in APPLIES:
        errors.append(f"{where}: topics_apply_to is {applies!r}, not one of {list(APPLIES)}")
    if "denied_topics" in agent and not isinstance(agent["denied_topics"], list):
        errors.append(f"{where}: denied_topics is not a list")
    if "pii" in agent and not isinstance(agent["pii"], list):
        errors.append(f"{where}: pii is not a list")
    messages = agent.get("messages")
    if "messages" in agent and (not isinstance(messages, dict) or not set(messages) <= {"blocked_input", "blocked_output"}
                                or not all(isinstance(v, str) and v for v in messages.values())):  # fmt: skip
        errors.append(f"{where}: messages carries blocked_input and blocked_output, each a string, and nothing else")
    if "content_filters" in agent and agent["content_filters"] != baseline.get("content_filters"):
        errors.append(f"{where}: content_filters {agent['content_filters']!r}: the filters are the baseline's alone "
                      f"({baseline.get('content_filters')!r}), and the prompt-attack filter is off (the Rule Owner, M03 "
                      f"PR 2; R1); an agent file may not turn one on or off")  # fmt: skip
    base_topics = {_name_key(t.get("name")): t.get("name") for t in _topics(baseline)}
    for topic in _topics(agent):
        key = _name_key(topic.get("name"))
        if key in base_topics:
            errors.append(f"{where}: denied topic {topic.get('name')!r} names the baseline's {base_topics[key]!r}: "
                          f"a redefinition, examples included, is refused (add-only)")  # fmt: skip
    errors += _topic_errors(_topics(agent), where)
    base_actions = {e.get("entity"): e.get("action") for e in _pii(baseline)}
    for entry in _pii(agent):
        entity, action = entry.get("entity"), entry.get("action")
        if entity in base_actions and action != base_actions[entity]:
            errors.append(f"{where}: pii {entity}: {base_actions[entity]} to {action}: a baseline entity's action may "
                          f"not be changed, lowered or raised, in an agent file (add-only; ADR-0009 entry 5's order "
                          f"{', '.join(ACTIONS)})")  # fmt: skip
    errors += _pii_errors(_pii(agent), where)
    merged = merge(baseline, agent)
    if len(merged["denied_topics"]) > TOPICS_MAX:
        over = TOPICS_MAX - len(_topics(baseline))
        errors.append(f"{where}: {len(merged['denied_topics'])} topics in the sum, over Bedrock's {TOPICS_MAX}: the "
                      f"baseline holds {len(_topics(baseline))}, so {where} may add {max(over, 0)} and adds "
                      f"{len(_topics(agent))} (R5)")  # fmt: skip
    return errors


def _golden_kinds(goldens_dir: Path) -> dict[str, tuple[Any, Any]]:
    """Golden id -> (kind, retired) for the files in `goldens/`, as far as they parse."""
    found: dict[str, tuple[Any, Any]] = {}
    for path in sorted(goldens_dir.glob("g-*.yaml")) if goldens_dir.is_dir() else []:
        try:
            golden = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(golden, dict):
            found[path.stem] = (golden.get("kind"), golden.get("retired"))
    return found


def plant_errors(control: dict[str, Any], kind: str, built: set[str], goldens: dict[str, tuple[Any, Any]],
                 where: str) -> list[str]:  # fmt: skip
    """A control's plants: each named in `blocks` for a rule the merged guardrail builds, each a live golden of its kind."""
    errors = []
    plants = control.get("plants")
    if plants is None:
        plants = []
    if not isinstance(plants, list) or not all(isinstance(p, str) for p in plants):
        return [f"{where}: plants is not a list of golden ids"]
    blocks = control.get("blocks")
    if "blocks" not in control:
        blocks = {}
        if plants:
            errors.append(f"{where}: plants {plants} with no blocks: a plant with no named rule is a plant nobody "
                          f"could see fire (F9.4)")  # fmt: skip
    if not isinstance(blocks, dict):
        return errors + [f"{where}: blocks is not a mapping of golden id to rule"]
    for golden_id in plants:
        if not GOLDEN_ID.match(golden_id):
            errors.append(f"{where}: plants names {golden_id!r}, not a golden id")
            continue
        if golden_id not in goldens:
            errors.append(f"{where}: plants names {golden_id}, which is not in goldens/")
        elif goldens[golden_id][0] != kind:
            errors.append(f"{where}: plants names {golden_id}, a {goldens[golden_id][0]} golden, in the {kind} control")
        elif goldens[golden_id][1] is not None:
            errors.append(f"{where}: plants names {golden_id}, retired at {goldens[golden_id][1]}")
        if golden_id in blocks:
            continue
        if "blocks" in control:
            errors.append(f"{where}: blocks names no rule for {golden_id} (F9.4)")
    for golden_id, rule in blocks.items():
        if golden_id not in plants:
            errors.append(f"{where}: blocks names {golden_id}, which plants does not list")
        if not isinstance(rule, str) or not rule:
            errors.append(f"{where}: blocks names no rule for {golden_id}")
        elif rule not in built:
            errors.append(f"{where}: blocks names {rule!r} for {golden_id}, a rule the merged guardrail does not build "
                          f"(built: {sorted(built)}) (F9.4)")  # fmt: skip
    if len(set(plants)) != len(plants):
        errors.append(f"{where}: plants names an id twice")
    return errors


def rules_errors(agent_dir: Path, rules: dict[str, Any] | None = None, root: Path = ROOT) -> list[str]:
    """The platform check's reading of one agent folder's rules/ against the baseline on `root`.

    `rules` stands in for `rules/guardrail.yaml`'s content. Every error names the file and the way."""
    agent_dir = Path(agent_dir)
    try:
        baseline = load(root / BASELINE)
    except ValueError as exc:
        return [str(exc)]
    errors = baseline_errors(baseline)
    where = "rules/guardrail.yaml"
    if rules is None:
        path = agent_dir / "rules" / "guardrail.yaml"
        if not path.is_file():
            return errors + [f"{where}: missing; an agent with rules/ carries it (SPEC/09 section 2)"]
        try:
            rules = load(path)
        except ValueError as exc:
            return errors + [f"{where}: {str(exc).split(': ', 1)[-1]}"]
    errors += merge_errors(baseline, rules, where)
    merged = merge(baseline, rules)
    built = {t.get("name") for t in _topics(merged) if isinstance(t.get("name"), str)}
    goldens = _golden_kinds(agent_dir / "goldens")
    errors += plant_errors(rules, "guardrail", built, goldens, where)
    redteam_path = agent_dir / "rules" / "redteam.yaml"
    if redteam_path.is_file():
        where = "rules/redteam.yaml"
        try:
            redteam = load(redteam_path)
        except ValueError as exc:
            return errors + [f"{where}: {str(exc).split(': ', 1)[-1]}"]
        errors += [f"{where}: key {key!r} is not in the format; a red-team file carries plants and blocks"
                   for key in sorted(set(redteam) - REDTEAM_KEYS)]  # fmt: skip
        errors += plant_errors(redteam, "redteam", built, goldens, where)
    for golden_id, (kind, retired) in sorted(goldens.items()):
        if kind in CONTROLS.values() and retired is None:
            control = rules if kind == "guardrail" else (load(redteam_path) if redteam_path.is_file() else {})
            if golden_id not in (control.get("plants") or []):
                errors.append(f"goldens/{golden_id}.yaml: a {kind} golden no control plants; name it in "
                              f"rules/{'guardrail' if kind == 'guardrail' else 'redteam'}.yaml plants with a blocks entry")  # fmt: skip
    return errors


def check(root: Path) -> list[str]:
    """`validate`: the baseline is in the tree and in its format, and refagent's rules merge onto it with nothing refused."""
    try:
        baseline = load(root / BASELINE)
    except ValueError as exc:
        return [str(exc)]
    errors = baseline_errors(baseline)
    for path in sorted((root / "agents").glob("*/rules/guardrail.yaml")):
        rel = path.relative_to(root).as_posix()
        try:
            errors += merge_errors(baseline, load(path), rel)
        except ValueError as exc:
            errors.append(str(exc))
    return errors
