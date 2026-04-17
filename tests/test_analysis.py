from pathlib import Path
import json

from ditto_skill.analysis import run_analysis
from tests.helpers import make_git_repo


def test_run_analysis_writes_full_v1_artifacts(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "analysis-repo",
        [
            ("feat: init app", {"package.json": '{"name":"analysis"}', "app/page.tsx": "export default function Page() { return null }\n"}),
            ("feat: add auth", {"app/auth.ts": "export const auth = true\n"}),
            ("refactor: split routes", {"app/routes.ts": "export const routes = []\n"}),
        ],
    )
    analysis_dir = tmp_path / "outputs" / "analysis-repo" / "analysis"

    run_analysis(repo.path, analysis_dir, selected_profile="web-saas", mode="analyze")

    expected_files = {
        "repo-summary.json",
        "milestone-candidates.json",
        "milestone-review-prompt.md",
        "architecture-evolution.json",
        "stack-evolution.json",
        "pitfall-summary.json",
        "distill-report.md",
    }
    assert expected_files.issubset({path.name for path in analysis_dir.iterdir()})
    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    assert repo_summary["profile"] == "web-saas"
    assert "## Recommended Next Step" in (analysis_dir / "distill-report.md").read_text()
