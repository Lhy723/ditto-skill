from __future__ import annotations

import argparse
from pathlib import Path

from ditto_skill.repo_intake import detect_repo_source, prepare_local_repo, profile_repo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scan", "analyze", "synthesize", "full"], default="scan")
    parser.add_argument("--repo")
    parser.add_argument("--profile", choices=["general", "web-saas", "ai-agent"], default="general")
    parser.add_argument("--clones-dir", default="tmp/clones")
    parser.add_argument("--allow-clone", action="store_true")
    parser.add_argument("--output-root", default="outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = detect_repo_source(args.repo, Path.cwd())
    repo_path = prepare_local_repo(source, Path(args.clones_dir), allow_clone=args.allow_clone)
    profile = profile_repo(repo_path, selected_profile=args.profile)
    print(f"{source.kind}:{source.slug}:{profile.commit_count}:{profile.profile}")


if __name__ == "__main__":
    main()
