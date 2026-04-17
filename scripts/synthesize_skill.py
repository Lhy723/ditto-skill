from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import read_json
except ImportError:  # pragma: no cover - direct script execution path
    from common import read_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-slug", required=True)
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--output-root", default="outputs")
    return parser.parse_args()


def write_skill(path: Path, name: str, description: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        + "\n".join(lines)
        + "\n"
    )


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    output_root = Path(args.output_root)
    skills_dir = output_root / args.repo_slug / "skills"

    repo_summary = read_json(analysis_dir / "repo-summary.json")
    reviewed = read_json(analysis_dir / "reviewed-milestones.json")
    pitfall_summary = read_json(analysis_dir / "pitfall-summary.json")

    write_skill(
        skills_dir / "master-skill" / "SKILL.md",
        f"{args.repo_slug}-master",
        "Master distilled skill generated from reviewed repository artifacts.",
        [
            "# Master Skill",
            "",
            f"- Project archetype: profile={repo_summary['profile']}, manifests={', '.join(repo_summary['manifests']) or 'none'}",
            f"- Default build order: start from {', '.join(repo_summary['top_level_dirs']) or 'the smallest working slice'}",
            "- Architecture heuristics: split boundaries when reviewed milestones show repeated structural pressure.",
            "- Quality rules: add tests, linting, types, and CI after the first stable feature slice.",
            "- Pitfalls to avoid: turn fixes and refactors into explicit guardrails.",
            "",
            "## Reviewed Milestones",
            *[f"- {row['message']}: {row['why']}" for row in reviewed if row["decision"] == "keep"],
        ],
    )

    subskills = {
        "bootstrap": "Start from the smallest viable repository skeleton.",
        "architecture-evolution": "Split boundaries only when milestones show real structural pressure.",
        "quality-hardening": "Layer tests, linting, and CI after the initial working slice.",
        "stack-specific": f"Prefer patterns consistent with profile={repo_summary['profile']}.",
        "pitfall-avoidance": "Carry forward the fixes and anti-patterns discovered in history.",
    }

    for slug, summary in subskills.items():
        write_skill(
            skills_dir / "subskills" / slug / "SKILL.md",
            f"{args.repo_slug}-{slug}",
            summary,
            [
                f"# {slug.replace('-', ' ').title()}",
                "",
                summary,
                "",
                "## Inputs",
                *[f"- {row['message']}" for row in reviewed if row["decision"] == "keep"],
                "",
                "## Pitfalls",
                *[f"- {message}" for message in pitfall_summary.get("messages", [])],
            ],
        )

    print(str(skills_dir))


if __name__ == "__main__":
    main()
