from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import read_json, write_json
except ImportError:  # pragma: no cover - direct script execution path
    from common import read_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-slug", required=True)
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--auto-keep-top", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    candidates = read_json(analysis_dir / "milestone-candidates.json")
    prompt_lines = [
        f"# Milestone Review Prompt: {args.repo_slug}",
        "",
        "Review each candidate and decide whether it should be kept as a durable milestone.",
        "",
        "## Candidates",
        *[
            f"- {row['message']} | score={row['score']} | reasons={', '.join(row['reasons'])}"
            for row in candidates
        ],
    ]
    (analysis_dir / "milestone-review-prompt.md").write_text("\n".join(prompt_lines) + "\n")

    if args.auto_keep_top > 0:
        reviewed = [
            {
                "sha": row["sha"],
                "message": row["message"],
                "decision": "keep",
                "why": "Auto-kept from the top-ranked milestone candidates.",
            }
            for row in candidates[: args.auto_keep_top]
        ]
        write_json(analysis_dir / "reviewed-milestones.json", reviewed)

    print(str(analysis_dir / "milestone-review-prompt.md"))


if __name__ == "__main__":
    main()
