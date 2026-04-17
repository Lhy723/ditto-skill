from __future__ import annotations

from pathlib import Path
import json


def _write_skill(path: Path, name: str, description: str, body_lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        + "\n".join(body_lines)
        + "\n"
    )


def _load_reviewed_milestones(analysis_dir: Path) -> list[dict[str, str]]:
    reviewed_path = analysis_dir / "reviewed-milestones.json"
    if reviewed_path.exists():
        return json.loads(reviewed_path.read_text())

    candidates_path = analysis_dir / "milestone-candidates.json"
    if not candidates_path.exists():
        raise FileNotFoundError(f"missing reviewed or candidate milestones in {analysis_dir}")

    candidates = json.loads(candidates_path.read_text())
    reviewed = [
        {
            "sha": row["sha"],
            "message": row["message"],
            "decision": "keep",
            "why": "Auto-kept during full mode synthesis.",
        }
        for row in candidates
    ]
    reviewed_path.write_text(json.dumps(reviewed, indent=2))
    return reviewed


def synthesize_skill_package(repo_slug: str, analysis_dir: Path, skills_dir: Path) -> None:
    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    reviewed = _load_reviewed_milestones(analysis_dir)
    pitfall_summary = json.loads((analysis_dir / "pitfall-summary.json").read_text())

    _write_skill(
        skills_dir / "master-skill" / "SKILL.md",
        f"{repo_slug}-master",
        "Master distilled skill generated from reviewed repository evolution artifacts.",
        [
            "# Master Skill",
            "",
            f"- Project archetype: profile={repo_summary['profile']}, manifests={', '.join(repo_summary['manifests']) or 'none'}",
            f"- Default build order: start from {', '.join(repo_summary['top_level_dirs']) or 'the smallest working slice'}",
            "- Architecture heuristics: use reviewed refactor milestones to decide when to split boundaries.",
            "- Quality rules: add test, lint, and CI layers once the first feature slice stabilizes.",
            "- Pitfalls to avoid: convert reviewed fixes and pitfall messages into explicit guardrails.",
            "",
            "## Reviewed Milestones",
            *[f"- {entry['message']}: {entry['why']}" for entry in reviewed if entry["decision"] == "keep"],
        ],
    )

    subskill_specs = {
        "bootstrap": "Create the smallest viable skeleton before layering more systems.",
        "architecture-evolution": "Promote boundary changes only when reviewed milestones show real pressure.",
        "quality-hardening": "Add tests, linting, types, and CI in the order implied by reviewed milestones.",
        "stack-specific": f"Prefer stack patterns consistent with profile={repo_summary['profile']}.",
        "pitfall-avoidance": "Avoid reintroducing the mistakes reflected in fixes, reverts, and pitfall summaries.",
    }
    for slug, summary in subskill_specs.items():
        _write_skill(
            skills_dir / "subskills" / slug / "SKILL.md",
            f"{repo_slug}-{slug}",
            summary,
            [
                f"# {slug.replace('-', ' ').title()}",
                "",
                summary,
                "",
                "## Inputs",
                *[f"- {entry['message']}" for entry in reviewed if entry["decision"] == "keep"],
                "",
                "## Pitfalls",
                *[f"- {message}" for message in pitfall_summary.get("messages", [])],
            ],
        )
