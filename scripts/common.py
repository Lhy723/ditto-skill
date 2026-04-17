from __future__ import annotations

from pathlib import Path
import json
import subprocess
from urllib.parse import urlparse


def normalize_repo_slug(repo_value: str) -> str:
    if repo_value.startswith("https://github.com/"):
        path = urlparse(repo_value).path.strip("/")
        owner, repo = path.split("/", 1)
        return f"{owner}-{repo.removesuffix('.git')}"
    return Path(repo_value).name


def run_git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def read_json(path: Path) -> object:
    return json.loads(path.read_text())
