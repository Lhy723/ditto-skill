from pathlib import Path
import json
import subprocess
import sys


def test_review_milestones_script_writes_packet_and_draft_template(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "milestone-candidates.json").write_text(
        json.dumps(
            [
                {
                    "sha": "a1",
                    "message": "feat: add auth flow",
                    "authored_at": "2026-01-01T00:00:00+00:00",
                    "score": 9,
                    "reasons": ["durable capability", "dependency change", "profile signal"],
                    "phase_hint": "expansion",
                    "files": ["app/login/page.tsx", "lib/auth.ts", "middleware.ts"],
                    "evidence_summary": "feat: add auth flow — introduces auth; changes dependencies in package.json.",
                    "evidence_refs": ["commit-evidence.json#a1"],
                }
            ],
            indent=2,
        )
    )

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/review_milestones.py",
            "--repo-slug",
            "sample-repo",
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    packet = (analysis_dir / "milestone-review-packet.md").read_text()
    draft = (analysis_dir / "reviewed-milestones.md").read_text()

    assert "Questions to answer" in packet
    assert "evidence refs" in packet
    assert "## Milestone" in draft
    assert "- decision: keep" in draft
    assert "- capability: TODO" in draft
    assert not (analysis_dir / "reviewed-milestones.json").exists()
