from pathlib import Path
import json
import subprocess
import sys

import pytest


def test_compile_review_script_turns_draft_into_json(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir(parents=True)
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

    reviewed = json.loads((analysis_dir / "reviewed-milestones.json").read_text())
    assert reviewed[0]["decision"] == "keep"
    assert reviewed[0]["phase"] == "expansion"
    assert reviewed[0]["review_mode"] == "assistant"


def test_compile_review_script_fails_on_invalid_phase(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "reviewed-milestones.md").write_text(
        "\n".join(
            [
                "# Reviewed Milestones Draft: sample-repo",
                "",
                "## Milestone",
                "- sha: a1",
                "- message: feat: add auth flow",
                "- decision: keep",
                "- phase: nope",
                "- capability: x",
                "- constraint_or_tradeoff: y",
                "- why: z",
                "- evidence_refs:",
                "  - commit-evidence.json#a1",
                "",
            ]
        )
    )

    with pytest.raises(subprocess.CalledProcessError):
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
