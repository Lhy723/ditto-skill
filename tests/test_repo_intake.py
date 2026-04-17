from pathlib import Path

from ditto_skill.models import RepoSource
from ditto_skill.repo_intake import detect_repo_source, prepare_local_repo, profile_repo
from tests.helpers import make_git_repo


def test_detect_repo_source_defaults_to_current_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path / "current-repo", [("feat: init", {"README.md": "# hi\n"})])
    source = detect_repo_source(None, repo.path)
    assert source == RepoSource(kind="local", value=str(repo.path), slug="current-repo")


def test_detect_repo_source_parses_github_url() -> None:
    source = detect_repo_source("https://github.com/openai/example", Path.cwd())
    assert source.kind == "github"
    assert source.slug == "openai-example"


def test_prepare_local_repo_requires_clone_confirmation(tmp_path: Path) -> None:
    source = RepoSource(kind="github", value="https://github.com/openai/example", slug="openai-example")
    try:
        prepare_local_repo(source, tmp_path / "clones", allow_clone=False)
    except PermissionError as exc:
        assert "Clone confirmation required" in str(exc)
    else:
        raise AssertionError("expected PermissionError")


def test_profile_repo_collects_manifest_and_commit_count(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "profile-repo",
        [("feat: init app", {"package.json": '{"name":"profile"}', "app/page.tsx": "export default function Page() { return null }\n"})],
    )
    profile = profile_repo(repo.path)
    assert "package.json" in profile.manifests
    assert "app" in profile.top_level_dirs
    assert profile.commit_count == 1
