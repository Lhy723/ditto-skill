from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import PHASE_ORDER, parse_key_value_bullets, write_json
except ImportError:  # pragma: no cover - direct script execution path
    from common import PHASE_ORDER, parse_key_value_bullets, write_json


SUBSKILL_ORDER = [
    "bootstrap",
    "architecture-evolution",
    "quality-hardening",
    "stack-specific",
    "pitfall-avoidance",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--draft", default="distilled-insights.md")
    parser.add_argument("--output", default="distilled-insights.json")
    return parser.parse_args()


def require_fields(block: dict[str, object], fields: list[str]) -> None:
    missing = [field for field in fields if field not in block]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def ensure_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return [str(item).strip() for item in value]


def reject_todo(value: str, field: str) -> str:
    stripped = value.strip()
    if stripped == "TODO" or stripped.startswith("TODO"):
        raise ValueError(f"Field '{field}' still contains TODO")
    return stripped


def reject_todo_list(values: list[str], field: str) -> list[str]:
    cleaned = []
    for value in values:
        cleaned.append(reject_todo(value, field))
    return cleaned


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    draft_path = analysis_dir / args.draft
    output_path = analysis_dir / args.output
    lines = draft_path.read_text().splitlines()

    if not lines or not lines[0].startswith("# Distilled Insights Draft:"):
        raise ValueError("Draft must start with '# Distilled Insights Draft: <repo-slug>'")

    project_archetype: dict[str, object] | None = None
    build_phases: list[dict[str, object]] = []
    default_build_order: list[dict[str, object]] = []
    architecture_rules: list[str] = []
    stack_patterns: list[str] = []
    quality_rules: list[str] = []
    pitfall_guardrails: list[str] = []
    subskill_mapping: dict[str, dict[str, object]] = {}
    evidence_refs: list[str] = []

    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == "## Project Archetype":
            block, index = parse_key_value_bullets(lines, index + 1)
            require_fields(block, ["summary", "profile", "manifests", "top_level_dirs"])
            project_archetype = {
                "summary": reject_todo(str(block["summary"]), "summary"),
                "profile": reject_todo(str(block["profile"]), "profile"),
                "manifests": ensure_list(block["manifests"], "manifests"),
                "top_level_dirs": ensure_list(block["top_level_dirs"], "top_level_dirs"),
            }
            continue
        if stripped == "## Build Phases":
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("## "):
                if lines[index].strip() == "### Phase":
                    block, index = parse_key_value_bullets(lines, index + 1)
                    require_fields(block, ["phase", "when", "why", "actions", "evidence_refs"])
                    phase = str(block["phase"]).strip()
                    if phase not in PHASE_ORDER:
                        raise ValueError(f"Invalid phase '{phase}' in build phases")
                    build_phases.append(
                        {
                            "phase": phase,
                            "when": reject_todo(str(block["when"]), "when"),
                            "why": reject_todo(str(block["why"]), "why"),
                            "actions": reject_todo_list(ensure_list(block["actions"], "actions"), "actions"),
                            "evidence_refs": ensure_list(block["evidence_refs"], "evidence_refs"),
                        }
                    )
                    continue
                index += 1
            continue
        if stripped == "## Default Build Order":
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("## "):
                if lines[index].strip() == "### Step":
                    block, index = parse_key_value_bullets(lines, index + 1)
                    require_fields(block, ["phase", "recommendation", "why"])
                    phase = str(block["phase"]).strip()
                    if phase not in PHASE_ORDER:
                        raise ValueError(f"Invalid phase '{phase}' in default build order")
                    default_build_order.append(
                        {
                            "phase": phase,
                            "recommendation": reject_todo(str(block["recommendation"]), "recommendation"),
                            "why": reject_todo(str(block["why"]), "why"),
                        }
                    )
                    continue
                index += 1
            continue
        if stripped in {
            "## Architecture Rules",
            "## Stack Patterns",
            "## Quality Rules",
            "## Pitfall Guardrails",
            "## Evidence Refs",
        }:
            block, index = parse_key_value_bullets(lines, index + 1)
            require_fields(block, ["items"])
            items = ensure_list(block["items"], "items")
            if stripped == "## Architecture Rules":
                architecture_rules = reject_todo_list(items, "architecture_rules")
            elif stripped == "## Stack Patterns":
                stack_patterns = reject_todo_list(items, "stack_patterns")
            elif stripped == "## Quality Rules":
                quality_rules = reject_todo_list(items, "quality_rules")
            elif stripped == "## Pitfall Guardrails":
                pitfall_guardrails = reject_todo_list(items, "pitfall_guardrails")
            else:
                evidence_refs = items
            continue
        if stripped == "## Subskill Mapping":
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("## "):
                if lines[index].strip() == "### Subskill":
                    block, index = parse_key_value_bullets(lines, index + 1)
                    require_fields(
                        block,
                        [
                            "slug",
                            "when_to_use",
                            "what_to_do",
                            "what_to_avoid",
                            "signals_to_watch",
                            "evidence_refs",
                        ],
                    )
                    slug = str(block["slug"]).strip()
                    if slug not in SUBSKILL_ORDER:
                        raise ValueError(f"Invalid subskill slug '{slug}'")
                    subskill_mapping[slug] = {
                        "when_to_use": reject_todo_list(
                            ensure_list(block["when_to_use"], "when_to_use"), "when_to_use"
                        ),
                        "what_to_do": reject_todo_list(
                            ensure_list(block["what_to_do"], "what_to_do"), "what_to_do"
                        ),
                        "what_to_avoid": reject_todo_list(
                            ensure_list(block["what_to_avoid"], "what_to_avoid"), "what_to_avoid"
                        ),
                        "signals_to_watch": reject_todo_list(
                            ensure_list(block["signals_to_watch"], "signals_to_watch"), "signals_to_watch"
                        ),
                        "evidence_refs": ensure_list(block["evidence_refs"], "evidence_refs"),
                    }
                    continue
                index += 1
            continue
        index += 1

    if project_archetype is None:
        raise ValueError("Missing '## Project Archetype' section")
    if not build_phases:
        raise ValueError("Missing build phases")
    if not default_build_order:
        raise ValueError("Missing default build order")
    if not architecture_rules or not stack_patterns or not quality_rules or not pitfall_guardrails:
        raise ValueError("Missing one of the rule sections")
    missing_subskills = [slug for slug in SUBSKILL_ORDER if slug not in subskill_mapping]
    if missing_subskills:
        raise ValueError(f"Missing subskills: {', '.join(missing_subskills)}")

    write_json(
        output_path,
        {
            "project_archetype": project_archetype,
            "build_phases": build_phases,
            "default_build_order": default_build_order,
            "architecture_rules": architecture_rules,
            "stack_patterns": stack_patterns,
            "quality_rules": quality_rules,
            "pitfall_guardrails": pitfall_guardrails,
            "subskill_mapping": subskill_mapping,
            "evidence_refs": evidence_refs,
        },
    )
    print(str(output_path))


if __name__ == "__main__":
    main()
