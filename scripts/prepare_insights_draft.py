from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import PHASE_ORDER, read_json, write_text
except ImportError:  # pragma: no cover - direct script execution path
    from common import PHASE_ORDER, read_json, write_text


SUBSKILL_ORDER = [
    "bootstrap",
    "architecture-evolution",
    "quality-hardening",
    "stack-specific",
    "pitfall-avoidance",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-slug", required=True)
    parser.add_argument("--analysis-dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    repo_summary = read_json(analysis_dir / "repo-summary.json")
    reviewed = read_json(analysis_dir / "reviewed-milestones.json")
    architecture = read_json(analysis_dir / "architecture-evolution.json")
    stack = read_json(analysis_dir / "stack-evolution.json")
    pitfall_summary = read_json(analysis_dir / "pitfall-summary.json")

    kept = [row for row in reviewed if row["decision"] == "keep"]
    phase_refs: dict[str, list[str]] = {}
    for row in kept:
        phase_refs.setdefault(row["phase"], []).extend(row.get("evidence_refs", []))

    lines = [
        f"# Distilled Insights Draft: {args.repo_slug}",
        "",
        "Fill every section below. Keep the headings and field names exactly as written.",
        "",
        "## Project Archetype",
        f"- summary: {repo_summary['repo_slug']} is a {repo_summary['profile']} repository distilled from git evolution evidence.",
        f"- profile: {repo_summary['profile']}",
        "- manifests:",
        *[f"  - {item}" for item in repo_summary["manifests"]],
        "- top_level_dirs:",
        *[f"  - {item}" for item in repo_summary["top_level_dirs"]],
        "",
        "## Build Phases",
    ]

    phases = [phase for phase in PHASE_ORDER if phase in phase_refs]
    if not phases:
        phases = ["bootstrap", "expansion", "hardening"]
    for phase in phases:
        lines.extend(
            [
                "### Phase",
                f"- phase: {phase}",
                f"- when: TODO for {phase}",
                f"- why: TODO for {phase}",
                "- actions:",
                "  - TODO",
                "- evidence_refs:",
                *[f"  - {ref}" for ref in dict.fromkeys(phase_refs.get(phase, []))],
                "",
            ]
        )

    lines.extend(["## Default Build Order", ""])
    for phase in phases:
        lines.extend(
            [
                "### Step",
                f"- phase: {phase}",
                "- recommendation: TODO",
                "- why: TODO",
                "",
            ]
        )

    def list_section(title: str, items: list[str]) -> list[str]:
        return [title, "- items:", *[f"  - {item}" for item in items], ""]

    lines.extend(list_section("## Architecture Rules", architecture.get("patterns", []) or ["TODO"]))
    lines.extend(list_section("## Stack Patterns", stack.get("patterns", []) or ["TODO"]))
    lines.extend(
        list_section(
            "## Quality Rules",
            [
                "TODO: describe when tests, linting, typing, and CI should be introduced.",
            ],
        )
    )
    lines.extend(
        list_section(
            "## Pitfall Guardrails",
            pitfall_summary.get("guardrails", []) or ["TODO"],
        )
    )

    subskill_phase_map = {
        "bootstrap": "bootstrap",
        "architecture-evolution": "refactor",
        "quality-hardening": "hardening",
        "stack-specific": "expansion",
        "pitfall-avoidance": "pitfall",
    }

    lines.extend(["## Subskill Mapping", ""])
    for slug in SUBSKILL_ORDER:
        ref_phase = subskill_phase_map[slug]
        ref_values = list(dict.fromkeys(phase_refs.get(ref_phase, [])))
        evidence_lines = [f"  - {ref}" for ref in ref_values] if ref_values else ["  - TODO"]
        lines.extend(
            [
                "### Subskill",
                f"- slug: {slug}",
                "- when_to_use:",
                "  - TODO",
                "- what_to_do:",
                "  - TODO",
                "- what_to_avoid:",
                "  - TODO",
                "- signals_to_watch:",
                "  - TODO",
                "- evidence_refs:",
                *evidence_lines,
                "",
            ]
        )

    all_refs = [ref for row in kept for ref in row.get("evidence_refs", [])]
    lines.extend(list_section("## Evidence Refs", list(dict.fromkeys(all_refs)) or ["TODO"]))
    write_text(analysis_dir / "distilled-insights.md", "\n".join(lines))
    print(str(analysis_dir / "distilled-insights.md"))


if __name__ == "__main__":
    main()
