from __future__ import annotations

from pathlib import Path
import re
import subprocess

from ditto_skill.models import RepoProfile, RepoSource


GITHUB_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")


def detect_repo_source(repo_arg: str | None, cwd: Path) -> RepoSource:
    if repo_arg is None:
        return RepoSource(kind="local", value=str(cwd), slug=cwd.name)

    match = GITHUB_RE.match(repo_arg)
    if match:
        owner = match.group("owner")
        repo = match.group("repo").removesuffix(".git")
        return RepoSource(kind="github", value=repo_arg, slug=f"{owner}-{repo}")

    path = Path(repo_arg).expanduser().resolve()
    return RepoSource(kind="local", value=str(path), slug=path.name)


def prepare_local_repo(source: RepoSource, clones_dir: Path, allow_clone: bool) -> Path:
    if source.kind == "local":
        path = Path(source.value)
        if not (path / ".git").exists():
            raise FileNotFoundError(f"{path} is not a git repository")
        return path

    destination = clones_dir / source.slug
    if not allow_clone:
        raise PermissionError(f"Clone confirmation required for {source.value} -> {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", source.value, str(destination)], check=True, text=True)
    return destination


def profile_repo(repo_path: Path, selected_profile: str = "general") -> RepoProfile:
    manifests = [
        name
        for name in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod"]
        if (repo_path / name).exists()
    ]
    top_level_dirs = sorted(child.name for child in repo_path.iterdir() if child.is_dir() and child.name != ".git")
    commit_count = int(
        subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    )
    return RepoProfile(
        root=repo_path,
        manifests=manifests,
        top_level_dirs=top_level_dirs,
        commit_count=commit_count,
        profile=selected_profile,
    )
