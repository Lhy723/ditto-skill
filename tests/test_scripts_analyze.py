from pathlib import Path
import json
import subprocess

from scripts.common import normalize_repo_slug
from tests.helpers import make_git_repo


def test_normalize_repo_slug_uses_repo_name_for_local_paths() -> None:
    assert normalize_repo_slug("/tmp/example-repo") == "example-repo"


def test_analyze_repo_script_writes_analysis_artifacts(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "analysis-repo",
        [
            (
                "feat: init app",
                {
                    "package.json": '{"name":"analysis"}',
                    "app/page.tsx": "export default function Page() { return null }\n",
                },
            ),
            ("feat: add auth", {"app/auth.ts": "export const auth = true\n"}),
        ],
    )
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            "/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python",
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/analyze_repo.py",
            "--repo",
            str(repo.path),
            "--profile",
            "web-saas",
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    analysis_dir = output_root / "analysis-repo" / "analysis"
    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    assert repo_summary["profile"] == "web-saas"
    assert (analysis_dir / "distill-report.md").exists()
