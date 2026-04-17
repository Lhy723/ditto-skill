from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class TempRepo:
    path: Path

    def run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.path,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()


def make_git_repo(path: Path, commits: list[tuple[str, dict[str, str]]]) -> TempRepo:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Ditto Skill Tests"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "ditto-tests@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )

    for message, files in commits:
        for relpath, content in files.items():
            file_path = path / relpath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )

    return TempRepo(path=path)
