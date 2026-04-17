from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoSource:
    kind: str
    value: str
    slug: str


@dataclass(frozen=True)
class RepoProfile:
    root: Path
    manifests: list[str]
    top_level_dirs: list[str]
    commit_count: int
    profile: str
