from pathlib import Path
import json

from ditto_skill.synthesis import synthesize_skill_package


def test_synthesize_skill_package_creates_master_and_expected_subskills(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": "/tmp/sample-repo",
                "profile": "web-saas",
                "manifests": ["package.json"],
                "top_level_dirs": ["app", "tests", "drizzle"],
                "commit_count": 4,
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
                    "why": "Introduces reusable auth capability.",
                },
                {
                    "sha": "b2",
                    "message": "refactor: split routes",
                    "decision": "keep",
                    "why": "Shows when to separate boundaries.",
                },
            ],
            indent=2,
        )
    )
    (analysis_dir / "stack-evolution.json").write_text(
        json.dumps({"manifests": ["package.json"], "profile": "web-saas"}, indent=2)
    )
    (analysis_dir / "pitfall-summary.json").write_text(
        json.dumps({"messages": ["fix: patch auth redirect"]}, indent=2)
    )
    skills_dir = tmp_path / "outputs" / "sample-repo" / "skills"

    synthesize_skill_package("sample-repo", analysis_dir, skills_dir)

    assert (skills_dir / "master-skill" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "bootstrap" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "architecture-evolution" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "quality-hardening" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "stack-specific" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "pitfall-avoidance" / "SKILL.md").exists()


def test_synthesize_skill_package_autokeeps_candidates_when_review_missing(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": "/tmp/sample-repo",
                "profile": "ai-agent",
                "manifests": ["pyproject.toml"],
                "top_level_dirs": ["src", "evals"],
                "commit_count": 2,
            },
            indent=2,
        )
    )
    (analysis_dir / "milestone-candidates.json").write_text(
        json.dumps(
            [
                {"sha": "a1", "message": "feat: add tools", "score": 6, "reasons": ["feature", "ai-agent tools"]},
                {"sha": "b2", "message": "feat: add evals", "score": 6, "reasons": ["feature", "ai-agent eval/memory"]},
            ],
            indent=2,
        )
    )
    (analysis_dir / "stack-evolution.json").write_text(
        json.dumps({"manifests": ["pyproject.toml"], "profile": "ai-agent"}, indent=2)
    )
    (analysis_dir / "pitfall-summary.json").write_text(
        json.dumps({"messages": ["fix: recover tool timeout"]}, indent=2)
    )
    skills_dir = tmp_path / "outputs" / "sample-repo" / "skills"

    synthesize_skill_package("sample-repo", analysis_dir, skills_dir)

    reviewed = json.loads((analysis_dir / "reviewed-milestones.json").read_text())
    assert reviewed[0]["decision"] == "keep"
    assert reviewed[0]["why"] == "Auto-kept during full mode synthesis."
