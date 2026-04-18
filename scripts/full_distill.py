from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

try:
    from scripts.common import normalize_repo_slug
except ImportError:  # pragma: no cover - direct script execution path
    from common import normalize_repo_slug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--profile", choices=["general", "web-saas", "ai-agent"], default="general")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--allow-clone", action="store_true")
    return parser.parse_args()


def script_path(name: str) -> str:
    return str(Path(__file__).resolve().parent / name)


def main() -> None:
    args = parse_args()
    repo_slug = normalize_repo_slug(args.repo)
    analysis_dir = Path(args.output_root) / repo_slug / "analysis"

    subprocess.run(
        [
            sys.executable,
            script_path("analyze_repo.py"),
            "--repo",
            args.repo,
            "--profile",
            args.profile,
            "--output-root",
            args.output_root,
            *(["--allow-clone"] if args.allow_clone else []),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            script_path("review_milestones.py"),
            "--repo-slug",
            repo_slug,
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
    )
    print(str(analysis_dir))


if __name__ == "__main__":
    main()
