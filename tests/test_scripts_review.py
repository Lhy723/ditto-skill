from pathlib import Path
import json
import subprocess


def test_review_milestones_script_writes_prompt_and_review_file(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "milestone-candidates.json").write_text(
        json.dumps(
            [
                {
                    "sha": "a1",
                    "message": "feat: add auth",
                    "score": 6,
                    "reasons": ["feature", "web-saas auth"],
                }
            ],
            indent=2,
        )
    )

    subprocess.run(
        [
            "/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python",
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/review_milestones.py",
            "--repo-slug",
            "sample-repo",
            "--analysis-dir",
            str(analysis_dir),
            "--auto-keep-top",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    reviewed = json.loads((analysis_dir / "reviewed-milestones.json").read_text())
    assert reviewed[0]["decision"] == "keep"
    assert (analysis_dir / "milestone-review-prompt.md").exists()
