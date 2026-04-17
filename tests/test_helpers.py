from pathlib import Path

from tests.helpers import make_git_repo


def test_make_git_repo_creates_expected_history(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "sample",
        [
            ("feat: init", {"README.md": "# sample\n"}),
            ("refactor: add service", {"service.py": "def run():\n    return 'ok'\n"}),
        ],
    )

    assert repo.run_git("rev-list", "--count", "HEAD") == "2"
    assert repo.run_git("log", "--pretty=%s", "-1") == "refactor: add service"
