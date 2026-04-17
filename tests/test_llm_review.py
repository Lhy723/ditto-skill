from pathlib import Path
import json

from ditto_skill.heuristics import MilestoneCandidate
from ditto_skill.llm_review import build_review_packet, load_reviewed_milestones


def test_build_review_packet_and_load_reviewed_decisions(tmp_path: Path) -> None:
    candidates = [
        MilestoneCandidate(sha="a1", message="feat: add auth", score=6, reasons=["feature", "web-saas auth"]),
        MilestoneCandidate(sha="b2", message="docs: update readme", score=1, reasons=["low-signal docs/typo"]),
    ]
    analysis_dir = tmp_path / "analysis"
    build_review_packet("sample-repo", candidates, analysis_dir)

    reviewed_path = analysis_dir / "reviewed-milestones.json"
    reviewed_path.write_text(
        json.dumps(
            [
                {
                    "sha": "a1",
                    "message": "feat: add auth",
                    "decision": "keep",
                    "why": "Introduces a durable capability.",
                }
            ],
            indent=2,
        )
    )

    reviewed = load_reviewed_milestones(reviewed_path)
    assert reviewed[0]["decision"] == "keep"
    assert (analysis_dir / "milestone-review-prompt.md").exists()
