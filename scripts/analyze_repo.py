from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

try:
    from scripts.common import normalize_repo_slug, run_git, write_json
except ImportError:  # pragma: no cover - direct script execution path
    from common import normalize_repo_slug, run_git, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--profile", choices=["general", "web-saas", "ai-agent"], default="general")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--allow-clone", action="store_true")
    return parser.parse_args()


def ensure_repo(repo_value: str, allow_clone: bool, output_root: Path) -> tuple[Path, str]:
    if repo_value.startswith("https://github.com/"):
        slug = normalize_repo_slug(repo_value)
        clone_root = output_root / "_clones"
        repo_path = clone_root / slug
        if not allow_clone:
            raise PermissionError(f"Clone confirmation required for {repo_value}")
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", repo_value, str(repo_path)], check=True, text=True)
        return repo_path, slug

    repo_path = Path(repo_value)
    if not (repo_path / ".git").exists():
        raise FileNotFoundError(f"{repo_path} is not a git repository")
    return repo_path, normalize_repo_slug(repo_value)


def collect_candidates(repo_path: Path, profile: str) -> list[dict[str, object]]:
    history = run_git(repo_path, "log", "--pretty=format:%H%x09%s").splitlines()
    candidates: list[dict[str, object]] = []
    for line in history:
        sha, message = line.split("\t", 1)
        lowered = message.lower()
        score = 0
        reasons: list[str] = []

        if lowered.startswith("refactor"):
            score += 5
            reasons.append("refactor")
        if lowered.startswith("feat"):
            score += 4
            reasons.append("feature")
        if lowered.startswith("fix"):
            score += 2
            reasons.append("fix")
        if profile == "web-saas" and ("auth" in lowered or "schema" in lowered):
            score += 2
            reasons.append("web-saas signal")
        if profile == "ai-agent" and ("tool" in lowered or "eval" in lowered or "agent" in lowered):
            score += 2
            reasons.append("ai-agent signal")
        if score > 0:
            candidates.append({"sha": sha, "message": message, "score": score, "reasons": reasons})

    return sorted(candidates, key=lambda row: row["score"], reverse=True)


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root)
    repo_path, repo_slug = ensure_repo(args.repo, args.allow_clone, output_root)
    analysis_dir = output_root / repo_slug / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    top_level_dirs = sorted(
        path.name for path in repo_path.iterdir() if path.is_dir() and path.name != ".git"
    )
    manifests = [
        name
        for name in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod"]
        if (repo_path / name).exists()
    ]
    commit_count = int(run_git(repo_path, "rev-list", "--count", "HEAD"))
    candidates = collect_candidates(repo_path, args.profile)

    write_json(
        analysis_dir / "repo-summary.json",
        {
            "root": str(repo_path),
            "profile": args.profile,
            "manifests": manifests,
            "top_level_dirs": top_level_dirs,
            "commit_count": commit_count,
        },
    )
    write_json(analysis_dir / "milestone-candidates.json", candidates)
    write_json(
        analysis_dir / "architecture-evolution.json",
        {
            "summary": "Derived from top-level structure and high-signal commits.",
            "notable_commits": [row["message"] for row in candidates[:5]],
        },
    )
    write_json(
        analysis_dir / "stack-evolution.json",
        {
            "profile": args.profile,
            "manifests": manifests,
            "candidate_messages": [row["message"] for row in candidates[:5]],
        },
    )
    write_json(
        analysis_dir / "pitfall-summary.json",
        {
            "messages": [
                row["message"]
                for row in candidates
                if row["message"].lower().startswith(("fix", "refactor"))
            ]
        },
    )
    (analysis_dir / "distill-report.md").write_text(
        "\n".join(
            [
                f"# Distill Report: {repo_slug}",
                "",
                "## Repository Profile",
                f"- Profile: {args.profile}",
                f"- Commit count: {commit_count}",
                "",
                "## Milestone Candidates",
                *[f"- {row['message']} | score={row['score']}" for row in candidates],
                "",
                "## Recommended Next Step",
                "- Review the analysis and decide whether to synthesize the skill package.",
            ]
        )
        + "\n"
    )
    print(str(analysis_dir))


if __name__ == "__main__":
    main()
