from pathlib import Path
import subprocess

from tests.helpers import make_git_repo


def test_full_distill_script_runs_one_shot(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "full-repo",
        [
            (
                "feat: init app",
                {
                    "pyproject.toml": "[project]\nname='full'\n",
                    "src/main.py": "print('hi')\n",
                },
            ),
            ("feat: add tools", {"src/tools.py": "TOOLS = []\n"}),
        ],
    )
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            "/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python",
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

    assert (output_root / "full-repo" / "analysis" / "repo-summary.json").exists()
    assert (output_root / "full-repo" / "skills" / "master-skill" / "SKILL.md").exists()
