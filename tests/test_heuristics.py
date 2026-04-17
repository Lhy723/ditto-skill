from pathlib import Path

from ditto_skill.git_history import collect_commit_history
from ditto_skill.heuristics import collect_milestone_candidates
from tests.helpers import make_git_repo


def test_web_saas_profile_boosts_auth_and_schema_signals(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "saas-repo",
        [
            ("docs: setup", {"README.md": "# docs\n"}),
            ("feat: add auth flow", {"app/auth.ts": "export const auth = true\n"}),
            ("feat: add schema", {"drizzle/schema.ts": "export const users = {}\n"}),
        ],
    )
    history = collect_commit_history(repo.path)
    candidates = collect_milestone_candidates(history, selected_profile="web-saas", limit=2)
    messages = [candidate.message for candidate in candidates]
    assert messages == ["feat: add schema", "feat: add auth flow"]
