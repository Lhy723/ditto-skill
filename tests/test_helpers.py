from pathlib import Path

from tests.helpers import build_ai_agent_repo, build_web_saas_repo, make_git_repo


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


def test_build_web_saas_repo_creates_quality_and_fix_history(tmp_path: Path) -> None:
    repo = build_web_saas_repo(tmp_path / "web-saas")
    messages = repo.run_git("log", "--pretty=%s")
    assert "feat: add auth flow" in messages
    assert "fix: prevent auth redirect loop" in messages


def test_build_ai_agent_repo_creates_orchestration_and_eval_history(tmp_path: Path) -> None:
    repo = build_ai_agent_repo(tmp_path / "ai-agent")
    messages = repo.run_git("log", "--pretty=%s")
    assert "feat: add prompt orchestration workflow" in messages
    assert "feat: add eval suite and typed interfaces" in messages
