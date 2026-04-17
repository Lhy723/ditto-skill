from pathlib import Path
import json
import subprocess


def test_synthesize_skill_script_creates_master_and_subskills(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": "/tmp/sample-repo",
                "profile": "web-saas",
                "manifests": ["package.json"],
                "top_level_dirs": ["app", "tests"],
                "commit_count": 2,
            },
            indent=2,
        )
    )
    (analysis_dir / "reviewed-milestones.json").write_text(
        json.dumps(
            [
                {
                    "sha": "a1",
                    "message": "feat: add auth",
                    "decision": "keep",
                    "why": "Durable capability.",
                }
            ],
            indent=2,
        )
    )
    (analysis_dir / "pitfall-summary.json").write_text(
        json.dumps({"messages": ["fix: redirect loop"]}, indent=2)
    )
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            "/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python",
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/synthesize_skill.py",
            "--repo-slug",
            "sample-repo",
            "--analysis-dir",
            str(analysis_dir),
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    skills_dir = output_root / "sample-repo" / "skills"
    assert (skills_dir / "master-skill" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "pitfall-avoidance" / "SKILL.md").exists()
