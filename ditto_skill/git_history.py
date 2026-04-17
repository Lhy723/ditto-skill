from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    message: str
    changed_files: list[str]
    insertions: int
    deletions: int


def _numstat(repo_path: Path, sha: str) -> tuple[int, int]:
    output = subprocess.run(
        ["git", "show", "--numstat", "--format=", sha],
        cwd=repo_path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    insertions = 0
    deletions = 0
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, removed, _ = parts
        if added.isdigit():
            insertions += int(added)
        if removed.isdigit():
            deletions += int(removed)
    return insertions, deletions


def _changed_files(repo_path: Path, sha: str) -> list[str]:
    output = subprocess.run(
        ["git", "show", "--name-only", "--format=", sha],
        cwd=repo_path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    return [line for line in output.splitlines() if line.strip()]


def collect_commit_history(repo_path: Path, limit: int | None = None) -> list[CommitRecord]:
    command = ["git", "log", "--pretty=format:%H%x09%s"]
    if limit is not None:
        command.insert(2, f"-n{limit}")
    output = subprocess.run(
        command,
        cwd=repo_path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    records: list[CommitRecord] = []
    for line in output.splitlines():
        sha, message = line.split("\t", 1)
        insertions, deletions = _numstat(repo_path, sha)
        records.append(
            CommitRecord(
                sha=sha,
                message=message,
                changed_files=_changed_files(repo_path, sha),
                insertions=insertions,
                deletions=deletions,
            )
        )
    return records
