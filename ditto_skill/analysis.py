from __future__ import annotations

from pathlib import Path
import json

from ditto_skill.git_history import collect_commit_history
from ditto_skill.heuristics import collect_milestone_candidates
from ditto_skill.llm_review import build_review_packet
from ditto_skill.repo_intake import profile_repo


def run_analysis(repo_path: Path, analysis_dir: Path, selected_profile: str, mode: str) -> None:
    analysis_dir.mkdir(parents=True, exist_ok=True)
    profile = profile_repo(repo_path, selected_profile=selected_profile)
    history = collect_commit_history(repo_path)
    candidates = collect_milestone_candidates(history, selected_profile=selected_profile)

    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": str(profile.root),
                "profile": profile.profile,
                "manifests": profile.manifests,
                "top_level_dirs": profile.top_level_dirs,
                "commit_count": profile.commit_count,
            },
            indent=2,
        )
    )
    build_review_packet(repo_path.name, candidates, analysis_dir)

    if mode == "scan":
        return

    (analysis_dir / "architecture-evolution.json").write_text(
        json.dumps(
            {
                "summary": "Summarize boundary changes from top-level directories and high-scoring refactor commits.",
                "top_level_dirs": profile.top_level_dirs,
                "notable_commits": [candidate.message for candidate in candidates[:5]],
            },
            indent=2,
        )
    )
    (analysis_dir / "stack-evolution.json").write_text(
        json.dumps(
            {
                "manifests": profile.manifests,
                "profile": selected_profile,
                "top_candidate_messages": [candidate.message for candidate in candidates[:5]],
            },
            indent=2,
        )
    )
    (analysis_dir / "pitfall-summary.json").write_text(
        json.dumps(
            {
                "messages": [
                    candidate.message
                    for candidate in candidates
                    if candidate.message.lower().startswith(("fix", "refactor"))
                ],
                "note": "These commits should be reviewed for pitfalls and corrections before synthesis.",
            },
            indent=2,
        )
    )

    report_lines = [
        f"# Distill Report: {repo_path.name}",
        "",
        "## Repository Profile",
        f"- Profile: {selected_profile}",
        f"- Manifests: {', '.join(profile.manifests) or 'none'}",
        f"- Top-level directories: {', '.join(profile.top_level_dirs) or 'none'}",
        f"- Commit count: {profile.commit_count}",
        "",
        "## Milestone Candidates",
        *[
            f"- {candidate.message} | score={candidate.score} | reasons={', '.join(candidate.reasons)}"
            for candidate in candidates
        ],
        "",
        "## Recommended Next Step",
        "- Review `milestone-review-prompt.md` and write `reviewed-milestones.json` before synthesis.",
    ]
    (analysis_dir / "distill-report.md").write_text("\n".join(report_lines) + "\n")
