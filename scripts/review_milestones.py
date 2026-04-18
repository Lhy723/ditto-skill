from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import read_json, remove_paths, write_text
except ImportError:  # pragma: no cover - direct script execution path
    from common import read_json, remove_paths, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-slug", required=True)
    parser.add_argument("--analysis-dir", required=True)
    return parser.parse_args()


def build_review_packet(repo_slug: str, candidates: list[dict[str, object]]) -> str:
    lines = [
        f"# Milestone Review Packet: {repo_slug}",
        "",
        "Review every candidate as a future engineering lesson, not as a historical note.",
        "",
        "## Questions to answer",
        "1. What durable capability or durable constraint did this change introduce?",
        "2. Does it change the engineering path, or only local code details?",
        "3. Should a future assistant imitate this move in a similar repository?",
        "4. What phase does it belong to: bootstrap / expansion / hardening / refactor / pitfall?",
        "5. If you drop it, what important evolution signal would be lost?",
        "",
        "## Candidates",
    ]
    for candidate in candidates:
        lines.extend(
            [
                f"### {candidate['message']}",
                f"- sha: {candidate['sha']}",
                f"- phase hint: {candidate['phase_hint']}",
                f"- score: {candidate['score']}",
                f"- reasons: {', '.join(candidate['reasons'])}",
                f"- files: {', '.join(candidate['files'][:6]) or 'none'}",
                f"- summary: {candidate['evidence_summary']}",
                f"- evidence refs: {', '.join(candidate['evidence_refs']) or 'none'}",
                "",
            ]
        )
    return "\n".join(lines)


def build_review_draft(repo_slug: str, candidates: list[dict[str, object]]) -> str:
    lines = [
        f"# Reviewed Milestones Draft: {repo_slug}",
        "",
        "Fill every milestone block below. Keep the field names exactly as written.",
        "",
    ]
    for candidate in candidates:
        lines.extend(
            [
                "## Milestone",
                f"- sha: {candidate['sha']}",
                f"- message: {candidate['message']}",
                "- decision: keep",
                f"- phase: {candidate['phase_hint']}",
                "- capability: TODO",
                "- constraint_or_tradeoff: TODO",
                f"- why: {candidate['evidence_summary']}",
                "- evidence_refs:",
                *[f"  - {ref}" for ref in candidate["evidence_refs"]],
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    remove_paths(
        [
            analysis_dir / "milestone-review-prompt.md",
            analysis_dir / "reviewed-milestones.json",
            analysis_dir / "distilled-insights.md",
            analysis_dir / "distilled-insights.json",
        ]
    )
    candidates = read_json(analysis_dir / "milestone-candidates.json")
    write_text(
        analysis_dir / "milestone-review-packet.md",
        build_review_packet(args.repo_slug, candidates),
    )
    write_text(
        analysis_dir / "reviewed-milestones.md",
        build_review_draft(args.repo_slug, candidates),
    )
    print(str(analysis_dir / "milestone-review-packet.md"))


if __name__ == "__main__":
    main()
