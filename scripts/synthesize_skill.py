from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import read_json, write_text
except ImportError:  # pragma: no cover - direct script execution path
    from common import read_json, write_text


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
    parser.add_argument("--output-root", default="outputs")
    return parser.parse_args()


def write_skill(path: Path, name: str, description: str, body: str) -> None:
    write_text(
        path,
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        + body,
    )


def kept_milestones(reviewed: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in reviewed if row["decision"] == "keep"]


def unique_in_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def default_subskill_mapping(
    insights: dict[str, object],
    reviewed: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    kept = kept_milestones(reviewed)
    phase_to_messages: dict[str, list[str]] = {}
    for row in kept:
        phase_to_messages.setdefault(str(row["phase"]), []).append(str(row["message"]))

    return {
        "bootstrap": {
            "when_to_use": [
                "You are starting a similar repository from scratch.",
                "The project still needs a smallest viable slice before abstractions multiply.",
            ],
            "what_to_do": [
                "Create the smallest runnable skeleton first.",
                "Introduce manifests and one clear source directory before adding optional layers.",
            ],
            "what_to_avoid": [
                "Do not front-load every abstraction before the first working slice exists.",
            ],
            "signals_to_watch": [
                "Early commits introduce the first working files and manifests.",
            ],
            "evidence_refs": [f"reviewed-milestones.json#{msg}" for msg in phase_to_messages.get("bootstrap", [])[:3]],
        },
        "architecture-evolution": {
            "when_to_use": [
                "Feature growth is starting to blur module boundaries.",
            ],
            "what_to_do": list(insights.get("architecture_rules", [])) or [
                "Split boundaries when structural pressure shows up in repeated cross-cutting changes."
            ],
            "what_to_avoid": [
                "Do not refactor only for aesthetics; refactor when the current shape blocks future work.",
            ],
            "signals_to_watch": [
                "Repeated changes across the same directories.",
                "Renames, moves, or new boundary directories appearing in milestone commits.",
            ],
            "evidence_refs": [f"reviewed-milestones.json#{msg}" for msg in phase_to_messages.get("refactor", [])[:3]],
        },
        "quality-hardening": {
            "when_to_use": [
                "The first stable feature slice exists and regressions would now be expensive.",
            ],
            "what_to_do": list(insights.get("quality_rules", [])) or [
                "Layer tests, linting, types, and CI after the first durable feature slice."
            ],
            "what_to_avoid": [
                "Do not postpone all verification until after the project becomes hard to change.",
            ],
            "signals_to_watch": [
                "Commits that add tests, CI, linting, types, or deployment checks.",
            ],
            "evidence_refs": [f"reviewed-milestones.json#{msg}" for msg in phase_to_messages.get("hardening", [])[:3]],
        },
        "stack-specific": {
            "when_to_use": [
                "You want to reuse the source repository's stack decisions without copying code blindly.",
            ],
            "what_to_do": list(insights.get("stack_patterns", [])) or [
                "Introduce dependencies only when they unlock a repeated repository-level need."
            ],
            "what_to_avoid": [
                "Do not copy every dependency from the source repo before you know why it was introduced.",
            ],
            "signals_to_watch": [
                "Manifest changes that align with new capabilities or infrastructure needs.",
            ],
            "evidence_refs": list(insights.get("evidence_refs", []))[:3],
        },
        "pitfall-avoidance": {
            "when_to_use": [
                "The repository has already revealed real regressions, reverts, or recurring fixes.",
            ],
            "what_to_do": list(insights.get("pitfall_guardrails", [])) or [
                "Turn each recurring fix into an explicit future guardrail."
            ],
            "what_to_avoid": [
                "Do not treat a fix commit as a one-off if it reveals a durable engineering constraint.",
            ],
            "signals_to_watch": [
                "Fix, revert, hotfix, and regression commits touching product-critical boundaries.",
            ],
            "evidence_refs": [f"reviewed-milestones.json#{msg}" for msg in phase_to_messages.get("pitfall", [])[:3]],
        },
    }
def render_master_skill(
    repo_slug: str,
    insights: dict[str, object],
    reviewed: list[dict[str, object]],
) -> str:
    archetype = insights["project_archetype"]
    phases = insights["default_build_order"]
    architecture_rules = insights["architecture_rules"]
    stack_patterns = insights["stack_patterns"]
    quality_rules = insights["quality_rules"]
    pitfall_guardrails = insights["pitfall_guardrails"]
    evidence_rows = kept_milestones(reviewed)

    lines = [
        "# Master Skill",
        "",
        "## Project Archetype",
        f"- {archetype['summary']}",
        f"- Profile: {archetype['profile']}",
        f"- Manifests: {', '.join(archetype['manifests']) or 'none'}",
        f"- Top-level dirs: {', '.join(archetype['top_level_dirs']) or 'none'}",
        "",
        "## Recommended Build Order",
    ]
    lines.extend(
        [
            f"{index}. `{phase['phase']}` — {phase['recommendation']} ({phase['why']})"
            for index, phase in enumerate(phases, start=1)
        ]
    )
    lines.extend(
        [
            "",
            "## Architecture Heuristics",
            *[f"- {rule}" for rule in architecture_rules],
            "",
            "## Stack Patterns",
            *[f"- {pattern}" for pattern in stack_patterns],
            "",
            "## Quality Rules",
            *[f"- {rule}" for rule in quality_rules],
            "",
            "## Pitfalls / Guardrails",
            *[f"- {guardrail}" for guardrail in pitfall_guardrails],
            "",
            "## Evidence from Source Repo",
            *[
                f"- {row['message']} ({row['phase']}): {row['why']} | refs={', '.join(row.get('evidence_refs', []))}"
                for row in evidence_rows
            ],
        ]
    )
    return "\n".join(lines)


def render_subskill(title: str, payload: dict[str, object]) -> str:
    evidence_lines = [f"- {line}" for line in payload.get("evidence_refs", [])]
    if not evidence_lines:
        evidence_lines = ["- No explicit evidence refs recorded."]
    return "\n".join(
        [
            f"# {title}",
            "",
            "## When to use",
            *[f"- {line}" for line in payload.get("when_to_use", [])],
            "",
            "## What to do",
            *[f"- {line}" for line in payload.get("what_to_do", [])],
            "",
            "## What to avoid",
            *[f"- {line}" for line in payload.get("what_to_avoid", [])],
            "",
            "## Signals to watch",
            *[f"- {line}" for line in payload.get("signals_to_watch", [])],
            "",
            "## Evidence from source repo",
            *evidence_lines,
        ]
    )


def title_for_subskill(slug: str) -> str:
    return slug.replace("-", " ").title()


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    output_root = Path(args.output_root)
    skills_dir = output_root / args.repo_slug / "skills"

    repo_summary = read_json(analysis_dir / "repo-summary.json")
    reviewed = read_json(analysis_dir / "reviewed-milestones.json")
    insights_path = analysis_dir / "distilled-insights.json"
    if not insights_path.exists():
        raise FileNotFoundError(
            f"{insights_path} is required. Create distilled-insights.md and compile it before synthesis."
        )
    insights = read_json(insights_path)

    write_skill(
        skills_dir / "master-skill" / "SKILL.md",
        f"{args.repo_slug}-master",
        "Action-manual master skill distilled from repository evolution evidence.",
        render_master_skill(args.repo_slug, insights, reviewed),
    )

    subskills = default_subskill_mapping(insights, reviewed)
    subskills.update(insights.get("subskill_mapping", {}))

    for slug in SUBSKILL_ORDER:
        payload = subskills[slug]
        write_skill(
            skills_dir / "subskills" / slug / "SKILL.md",
            f"{args.repo_slug}-{slug}",
            f"Action-manual subskill for {slug}.",
            render_subskill(title_for_subskill(slug), payload),
        )

    print(str(skills_dir))


if __name__ == "__main__":
    main()
