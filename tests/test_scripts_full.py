from pathlib import Path
import subprocess
import sys

from tests.helpers import build_ai_agent_repo
from tests.test_scripts_compile_insights import valid_insights_draft


def test_full_distill_script_prepares_analysis_and_review_drafts(tmp_path: Path) -> None:
    repo = build_ai_agent_repo(tmp_path / "full-repo")
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/full_distill.py",
            "--repo",
            str(repo.path),
            "--profile",
            "ai-agent",
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    analysis_dir = output_root / "full-repo" / "analysis"

    assert (analysis_dir / "commit-evidence.json").exists()
    assert (analysis_dir / "milestone-review-packet.md").exists()
    assert (analysis_dir / "reviewed-milestones.md").exists()
    assert not (analysis_dir / "reviewed-milestones.json").exists()
    assert not (analysis_dir / "distilled-insights.json").exists()


def test_full_assistant_draft_flow_can_reach_synthesis(tmp_path: Path) -> None:
    repo = build_ai_agent_repo(tmp_path / "full-repo")
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/full_distill.py",
            "--repo",
            str(repo.path),
            "--profile",
            "ai-agent",
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    analysis_dir = output_root / "full-repo" / "analysis"
    (analysis_dir / "reviewed-milestones.md").write_text(
        "\n".join(
            [
                "# Reviewed Milestones Draft: full-repo",
                "",
                "## Milestone",
                "- sha: a1",
                "- message: feat: add tool adapter layer",
                "- decision: keep",
                "- phase: expansion",
                "- capability: Expand orchestration and tool-use capability.",
                "- constraint_or_tradeoff: Add a dependency only when it clearly unlocks repeated work.",
                "- why: Introduces a reusable tool adapter surface.",
                "- evidence_refs:",
                "  - commit-evidence.json#a1",
                "",
                "## Milestone",
                "- sha: b2",
                "- message: feat: add eval suite and typed interfaces",
                "- decision: keep",
                "- phase: hardening",
                "- capability: Introduce repository hardening through tests, linting, types, or CI.",
                "- constraint_or_tradeoff: Trade short-term speed for a more verifiable and maintainable codebase.",
                "- why: Adds eval coverage and typed interfaces around the workflow.",
                "- evidence_refs:",
                "  - commit-evidence.json#b2",
                "",
                "## Milestone",
                "- sha: c3",
                "- message: fix: avoid memory state leak across runs",
                "- decision: keep",
                "- phase: pitfall",
                "- capability: Encode a guardrail around a real failure mode.",
                "- constraint_or_tradeoff: Turn a local fix into a reusable repository-level guardrail.",
                "- why: Exposes a memory state leak that future assistants should guard against.",
                "- evidence_refs:",
                "  - commit-evidence.json#c3",
                "",
            ]
        )
    )

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
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/prepare_insights_draft.py",
            "--repo-slug",
            "full-repo",
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    (analysis_dir / "distilled-insights.md").write_text(valid_insights_draft())
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
    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/synthesize_skill.py",
            "--repo-slug",
            "full-repo",
            "--analysis-dir",
            str(analysis_dir),
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    master_skill = (output_root / "full-repo" / "skills" / "master-skill" / "SKILL.md").read_text()
    assert "## Recommended Build Order" in master_skill
    assert "## Evidence from Source Repo" in master_skill
