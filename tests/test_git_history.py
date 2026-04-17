from pathlib import Path

from ditto_skill.git_history import collect_commit_history
from tests.helpers import make_git_repo


def test_collect_commit_history_returns_changed_files(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "history-repo",
        [
            ("feat: init app", {"package.json": '{"name":"history"}', "app/page.tsx": "export default function Page() { return null }\n"}),
            ("fix: handle crash", {"app/error.tsx": "export default function Error() { return null }\n"}),
        ],
    )
    history = collect_commit_history(repo.path)
    assert history[0].message == "fix: handle crash"
    assert "app/error.tsx" in history[0].changed_files
