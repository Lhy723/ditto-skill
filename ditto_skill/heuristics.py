from __future__ import annotations

from dataclasses import dataclass

from ditto_skill.git_history import CommitRecord


@dataclass(frozen=True)
class MilestoneCandidate:
    sha: str
    message: str
    score: int
    reasons: list[str]


def _base_score(commit: CommitRecord) -> tuple[int, list[str]]:
    lowered = commit.message.lower()
    score = 0
    reasons: list[str] = []

    if lowered.startswith("refactor"):
        score += 5
        reasons.append("refactor")
    if lowered.startswith("feat"):
        score += 4
        reasons.append("feature")
    if lowered.startswith("perf") or lowered.startswith("test"):
        score += 3
        reasons.append("quality/perf")
    if lowered.startswith("fix"):
        score += 2
        reasons.append("fix")
    if "revert" in lowered or "regression" in lowered:
        score += 3
        reasons.append("revert/regression")
    if lowered.startswith("docs") or "typo" in lowered:
        score -= 2
        reasons.append("low-signal docs/typo")
    if commit.insertions + commit.deletions > 40:
        score += 1
        reasons.append("non-trivial diff")

    return score, reasons


def _profile_bonus(commit: CommitRecord, selected_profile: str) -> tuple[int, list[str]]:
    files = " ".join(commit.changed_files).lower()
    message = commit.message.lower()
    bonus = 0
    reasons: list[str] = []

    if selected_profile == "web-saas":
        if "auth" in files or "auth" in message:
            bonus += 2
            reasons.append("web-saas auth")
        if "schema" in files or "migration" in files or "drizzle" in files:
            bonus += 3
            reasons.append("web-saas schema")
        if "ci" in files or "deploy" in files:
            bonus += 2
            reasons.append("web-saas deploy")
    elif selected_profile == "ai-agent":
        if "prompt" in files or "prompt" in message:
            bonus += 2
            reasons.append("ai-agent prompt")
        if "tool" in files or "agent" in files:
            bonus += 2
            reasons.append("ai-agent tools")
        if "eval" in files or "memory" in files:
            bonus += 2
            reasons.append("ai-agent eval/memory")

    return bonus, reasons


def collect_milestone_candidates(
    history: list[CommitRecord],
    selected_profile: str,
    limit: int = 12,
) -> list[MilestoneCandidate]:
    candidates: list[MilestoneCandidate] = []
    for commit in history:
        score, reasons = _base_score(commit)
        bonus, profile_reasons = _profile_bonus(commit, selected_profile)
        total = score + bonus
        if total > 0:
            candidates.append(
                MilestoneCandidate(
                    sha=commit.sha,
                    message=commit.message,
                    score=total,
                    reasons=reasons + profile_reasons,
                )
            )
    return sorted(candidates, key=lambda item: item.score, reverse=True)[:limit]
