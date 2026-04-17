from __future__ import annotations

from pathlib import Path
import json

from ditto_skill.heuristics import MilestoneCandidate


def build_review_packet(repo_slug: str, candidates: list[MilestoneCandidate], analysis_dir: Path) -> None:
    analysis_dir.mkdir(parents=True, exist_ok=True)
    packet = [
        {
            "sha": candidate.sha,
            "message": candidate.message,
            "score": candidate.score,
            "reasons": candidate.reasons,
        }
        for candidate in candidates
    ]
    (analysis_dir / "milestone-candidates.json").write_text(json.dumps(packet, indent=2))

    prompt_lines = [
        f"# Milestone Review Prompt: {repo_slug}",
        "",
        "Review each candidate commit and decide whether it is a true milestone worth distilling into future skills.",
        "",
        "For each kept commit, write one line of reasoning that explains the durable engineering lesson.",
        "",
        "## Candidates",
    ]
    prompt_lines.extend(
        [
            f"- {candidate.message} | score={candidate.score} | reasons={', '.join(candidate.reasons)}"
            for candidate in candidates
        ]
    )
    (analysis_dir / "milestone-review-prompt.md").write_text("\n".join(prompt_lines) + "\n")


def load_reviewed_milestones(reviewed_path: Path) -> list[dict[str, str]]:
    if not reviewed_path.exists():
        raise FileNotFoundError(f"reviewed milestones missing: {reviewed_path}")
    return json.loads(reviewed_path.read_text())
