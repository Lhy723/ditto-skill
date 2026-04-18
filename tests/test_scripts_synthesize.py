from pathlib import Path
import json
import subprocess
import sys

from tests.test_scripts_compile_insights import valid_insights_draft


def test_synthesize_skill_script_creates_action_manual_outputs(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": "/tmp/sample-repo",
                "repo_slug": "sample-repo",
                "profile": "web-saas",
                "manifests": ["package.json"],
                "top_level_dirs": ["app", "services", "tests"],
                "commit_count": 6,
                "candidate_count": 4,
                "phase_distribution": {"bootstrap": 1, "expansion": 2, "hardening": 1},
            },
            indent=2,
        )
    )
    (analysis_dir / "reviewed-milestones.md").write_text(
        "\n".join(
            [
                "# Reviewed Milestones Draft: sample-repo",
                "",
                "## Milestone",
                "- sha: a1",
                "- message: feat: add auth flow",
                "- decision: keep",
                "- phase: expansion",
                "- capability: Introduce a durable authentication capability.",
                "- constraint_or_tradeoff: Add a dependency only when it clearly unlocks repeated work.",
                "- why: Introduces auth and middleware boundaries.",
                "- evidence_refs:",
                "  - commit-evidence.json#a1",
                "",
                "## Milestone",
                "- sha: b2",
                "- message: fix: prevent auth redirect loop",
                "- decision: keep",
                "- phase: pitfall",
                "- capability: Encode a guardrail around a real failure mode.",
                "- constraint_or_tradeoff: Turn a local fix into a reusable repository-level guardrail.",
                "- why: Exposes a redirect-loop failure mode.",
                "- evidence_refs:",
                "  - commit-evidence.json#b2",
                "",
            ]
        )
    )
    (analysis_dir / "distilled-insights.md").write_text(valid_insights_draft())

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/compile_review.py",
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/compile_insights.py",
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    output_root = tmp_path / "outputs"
    subprocess.run(
        [
            sys.executable,
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
    master_skill = (skills_dir / "master-skill" / "SKILL.md").read_text()
    pitfall_skill = (skills_dir / "subskills" / "pitfall-avoidance" / "SKILL.md").read_text()

    assert "## Recommended Build Order" in master_skill
    assert "## Architecture Heuristics" in master_skill
    assert "## Evidence from Source Repo" in master_skill
    assert "Reviewed Milestones" not in master_skill
    assert "When to use" in pitfall_skill
    assert "What to do" in pitfall_skill
    assert "What to avoid" in pitfall_skill
    assert "feat: add auth flow" not in pitfall_skill
