from __future__ import annotations

from pathlib import Path
import json
import subprocess
from urllib.parse import urlparse

NOISE_DIRS = {
    ".git",
    ".github",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".turbo",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "outputs",
    "tmp",
    "docs",
}

NOISE_SUFFIXES = {
    ".egg-info",
}

MANIFEST_FILES = [
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
]

PHASE_ORDER = ["bootstrap", "expansion", "hardening", "refactor", "pitfall"]


def normalize_repo_slug(repo_value: str) -> str:
    if repo_value.startswith(("https://github.com/", "http://github.com/")):
        path = urlparse(repo_value).path.strip("/")
        owner, repo = path.split("/", 1)
        return f"{owner}-{repo.removesuffix('.git')}"
    if repo_value.startswith("git@github.com:"):
        path = repo_value.split(":", 1)[1].strip("/")
        owner, repo = path.split("/", 1)
        return f"{owner}-{repo.removesuffix('.git')}"
    return Path(repo_value).name


def is_remote_repo(repo_value: str) -> bool:
    return repo_value.startswith(
        ("https://github.com/", "http://github.com/", "git@github.com:")
    )


def run_git(repo_path: Path, *args: str, capture_output: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        text=True,
        capture_output=capture_output,
    )
    return result.stdout.strip() if capture_output else ""


def ensure_local_repo(repo_value: str, output_root: Path, allow_clone: bool) -> tuple[Path, str]:
    if is_remote_repo(repo_value):
        if not allow_clone:
            raise PermissionError(f"Clone confirmation required for {repo_value}")
        slug = normalize_repo_slug(repo_value)
        clone_root = output_root / "_clones"
        repo_path = clone_root / slug
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        if (repo_path / ".git").exists():
            run_git(repo_path, "fetch", "--all", "--prune", capture_output=False)
        else:
            subprocess.run(["git", "clone", repo_value, str(repo_path)], check=True, text=True)
        return repo_path, slug

    repo_path = Path(repo_value).resolve()
    if not (repo_path / ".git").exists():
        raise FileNotFoundError(f"{repo_path} is not a git repository")
    return repo_path, normalize_repo_slug(repo_value)


def git_file_at(repo_path: Path, revision: str, file_path: str) -> str | None:
    try:
        return run_git(repo_path, "show", f"{revision}:{file_path}")
    except subprocess.CalledProcessError:
        return None


def list_top_level_dirs(repo_path: Path) -> list[str]:
    visible_dirs: list[str] = []
    for path in repo_path.iterdir():
        if not path.is_dir():
            continue
        if path.name in NOISE_DIRS:
            continue
        if path.name.startswith("."):
            continue
        if any(path.name.endswith(suffix) for suffix in NOISE_SUFFIXES):
            continue
        visible_dirs.append(path.name)
    return sorted(visible_dirs)


def list_manifests(repo_path: Path) -> list[str]:
    return [name for name in MANIFEST_FILES if (repo_path / name).exists()]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if content.endswith("\n") else content + "\n")


def remove_paths(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def parse_key_value_bullets(lines: list[str], start_index: int) -> tuple[dict[str, object], int]:
    data: dict[str, object] = {}
    index = start_index
    current_key: str | None = None
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("#"):
            break
        if stripped.startswith("- "):
            content = stripped[2:]
            if ": " in content:
                key, value = content.split(": ", 1)
                if value == "[list]":
                    data[key] = []
                    current_key = key
                else:
                    data[key] = value
                    current_key = None
            elif content.endswith(":"):
                key = content.removesuffix(":")
                data[key] = []
                current_key = key
            elif current_key:
                value = content
                existing = data.setdefault(current_key, [])
                if isinstance(existing, list):
                    existing.append(value)
                else:  # pragma: no cover - defensive
                    raise ValueError(f"Field '{current_key}' is not a list")
            else:
                raise ValueError(f"Unexpected bullet without field name: {content}")
            index += 1
            continue
        raise ValueError(f"Unexpected line while parsing bullets: {raw}")
    return data, index
