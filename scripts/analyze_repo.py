from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import tomllib

try:
    from scripts.common import (
        MANIFEST_FILES,
        ensure_local_repo,
        git_file_at,
        list_manifests,
        list_top_level_dirs,
        remove_paths,
        run_git,
        write_json,
        write_text,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from common import (
        MANIFEST_FILES,
        ensure_local_repo,
        git_file_at,
        list_manifests,
        list_top_level_dirs,
        remove_paths,
        run_git,
        write_json,
        write_text,
    )


PROFILE_CHOICES = ["general", "web-saas", "ai-agent"]
MAX_PATCH_EXCERPT_LINES = 24

QUALITY_PATH_PATTERNS = {
    "tests": ("tests/", "__tests__/", ".spec.", ".test.", "_test.", "test_"),
    "lint": (".eslintrc", "eslint.config", ".prettierrc", "ruff.toml", "flake8", "black"),
    "types": ("tsconfig", "pyright", "mypy", ".d.ts"),
    "ci": (".github/workflows/", ".gitlab-ci", "circleci", "buildkite", "ci/"),
}

CONFIG_PATH_PATTERNS = {
    "deployment": ("Dockerfile", "docker-compose", "vercel.json", "fly.toml", "Procfile"),
    "migration": ("migrations/", "alembic/", "schema.prisma", "schema.sql", "db/migrate"),
    "env": (".env", "config/", "settings/", "infra/"),
}

CAPABILITY_KEYWORDS = {
    "auth": ("auth", "session", "login", "oauth"),
    "billing": ("billing", "stripe", "subscription", "invoice"),
    "workflow": ("workflow", "pipeline", "orchestr", "stage"),
    "tooling": ("tool", "adapter", "cli"),
    "eval": ("eval", "benchmark", "judge"),
    "memory": ("memory", "state", "cache"),
    "prompt": ("prompt", "template", "system prompt"),
    "database": ("db", "database", "schema", "migration", "model"),
    "api": ("api", "route", "endpoint", "rpc"),
}

PROFILE_SIGNAL_MAP = {
    "web-saas": {"auth", "billing", "database", "api"},
    "ai-agent": {"workflow", "tooling", "eval", "memory", "prompt"},
}
PITFALL_PREFIXES = ("fix", "revert", "hotfix", "bugfix")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--profile", choices=PROFILE_CHOICES, default="general")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--allow-clone", action="store_true")
    return parser.parse_args()


def list_commits(repo_path: Path) -> list[dict[str, str]]:
    raw = run_git(
        repo_path,
        "log",
        "--reverse",
        "--format=%H%x1f%P%x1f%an%x1f%aI%x1f%s",
    )
    commits: list[dict[str, str]] = []
    for line in raw.splitlines():
        sha, parents, author, authored_at, message = line.split("\x1f")
        commits.append(
            {
                "sha": sha,
                "parent_sha": parents.split()[0] if parents else "",
                "author": author,
                "authored_at": authored_at,
                "message": message,
            }
        )
    return commits


def parse_numstat(raw: str) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        stats[path] = {
            "additions": 0 if added == "-" else int(added),
            "deletions": 0 if deleted == "-" else int(deleted),
        }
    return stats


def parse_name_status(raw: str) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) == 3:
            files.append({"path": parts[2], "status": "renamed", "previous_path": parts[1]})
            continue
        if status.startswith("C") and len(parts) == 3:
            files.append({"path": parts[2], "status": "copied", "previous_path": parts[1]})
            continue
        if len(parts) >= 2:
            status_map = {"A": "added", "M": "modified", "D": "deleted"}
            files.append({"path": parts[1], "status": status_map.get(status[0], status.lower())})
    return files


def parse_patch_excerpt(patch_text: str) -> str:
    excerpt: list[str] = []
    for line in patch_text.splitlines():
        if line.startswith(("diff --git", "@@")):
            excerpt.append(line)
            continue
        if line.startswith(("+++", "---", "index ")):
            continue
        if line.startswith(("+", "-")):
            excerpt.append(line)
        if len(excerpt) >= MAX_PATCH_EXCERPT_LINES:
            break
    return "\n".join(excerpt)


def parse_package_json_dependencies(text: str) -> set[str]:
    data = json.loads(text)
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps.update(data.get(key, {}).keys())
    return deps


def parse_pyproject_dependencies(text: str) -> set[str]:
    data = tomllib.loads(text)
    deps: set[str] = set()
    project = data.get("project", {})
    for item in project.get("dependencies", []):
        deps.add(re.split(r"[<>=!~ ]", item, maxsplit=1)[0].strip())
    for values in project.get("optional-dependencies", {}).values():
        for item in values:
            deps.add(re.split(r"[<>=!~ ]", item, maxsplit=1)[0].strip())
    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    deps.update(name for name in poetry_deps if name != "python")
    return {dep for dep in deps if dep}


def parse_go_mod_dependencies(text: str) -> set[str]:
    deps: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("module ", "go ", "replace ", "exclude ")):
            continue
        if stripped.startswith("require "):
            stripped = stripped.removeprefix("require ").strip()
        if stripped.startswith("(") or stripped.startswith(")"):
            continue
        parts = stripped.split()
        if parts:
            deps.add(parts[0])
    return deps


def parse_cargo_dependencies(text: str) -> set[str]:
    deps: set[str] = set()
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line.strip("[]")
            continue
        if current_section.endswith("dependencies") and "=" in line:
            deps.add(line.split("=", 1)[0].strip())
    return deps


def parse_manifest_dependencies(file_name: str, text: str | None) -> set[str]:
    if not text:
        return set()
    if file_name == "package.json":
        return parse_package_json_dependencies(text)
    if file_name == "pyproject.toml":
        return parse_pyproject_dependencies(text)
    if file_name == "go.mod":
        return parse_go_mod_dependencies(text)
    if file_name == "Cargo.toml":
        return parse_cargo_dependencies(text)
    return set()


def collect_dependency_changes(repo_path: Path, sha: str, parent_sha: str, touched_files: list[str]) -> list[dict[str, object]]:
    changes: list[dict[str, object]] = []
    for file_name in MANIFEST_FILES:
        if file_name not in touched_files:
            continue
        before = parse_manifest_dependencies(file_name, git_file_at(repo_path, parent_sha, file_name) if parent_sha else None)
        after = parse_manifest_dependencies(file_name, git_file_at(repo_path, sha, file_name))
        added = sorted(after - before)
        removed = sorted(before - after)
        if added or removed:
            changes.append(
                {
                    "manifest": file_name,
                    "added": added,
                    "removed": removed,
                }
            )
    return changes


def tree_dirs(repo_path: Path, revision: str) -> set[str]:
    if not revision:
        return set()
    try:
        raw = run_git(repo_path, "ls-tree", "-d", "--name-only", revision)
    except Exception:  # pragma: no cover - defensive
        return set()
    return {
        name
        for name in raw.splitlines()
        if name and not name.startswith(".") and name not in {"outputs", "tmp", "node_modules"}
    }


def classify_paths(paths: list[str], lowered_message: str, patch_text: str, profile: str) -> dict[str, object]:
    path_blob = "\n".join([lowered_message, *[path.lower() for path in paths]])
    lowered_blob = "\n".join([lowered_message, patch_text.lower(), *[path.lower() for path in paths]])
    quality_signals: list[str] = []
    config_signals: list[str] = []
    capability_signals: list[str] = []

    for label, patterns in QUALITY_PATH_PATTERNS.items():
        if any(pattern in path_blob for pattern in patterns):
            quality_signals.append(label)

    for label, patterns in CONFIG_PATH_PATTERNS.items():
        if any(pattern.lower() in path_blob for pattern in patterns):
            config_signals.append(label)

    for capability, keywords in CAPABILITY_KEYWORDS.items():
        if any(keyword in lowered_blob for keyword in keywords):
            capability_signals.append(capability)

    profile_signals = []
    if profile in PROFILE_SIGNAL_MAP:
        profile_signals = sorted(set(capability_signals) & PROFILE_SIGNAL_MAP[profile])

    return {
        "quality_signals": sorted(set(quality_signals)),
        "config_signals": sorted(set(config_signals)),
        "capability_signals": sorted(set(capability_signals)),
        "profile_signals": profile_signals,
    }


def infer_phase(
    commit: dict[str, str],
    dependency_changes: list[dict[str, object]],
    quality_signals: list[str],
    structure_signals: list[str],
    pitfall_signals: list[str],
) -> str:
    lowered = commit["message"].lower()
    if not commit["parent_sha"] or any(token in lowered for token in ("init", "bootstrap", "scaffold", "skeleton")):
        return "bootstrap"
    if pitfall_signals:
        return "pitfall"
    if structure_signals and ("refactor" in lowered or "rename" in lowered or "split" in lowered):
        return "refactor"
    if quality_signals and any(token in lowered for token in ("test", "ci", "coverage", "lint", "type")):
        return "hardening"
    if lowered.startswith("test") or lowered.startswith("chore: add ci") or (
        quality_signals
        and not dependency_changes
        and not structure_signals
        and not any(token in lowered for token in ("feat", "add auth", "add billing", "workflow", "tool", "agent"))
    ):
        return "hardening"
    if dependency_changes and ("feat" in lowered or "add" in lowered or "introduce" in lowered):
        return "expansion"
    return "expansion"


def build_evidence_summary(
    commit: dict[str, str],
    capability_signals: list[str],
    quality_signals: list[str],
    structure_signals: list[str],
    dependency_changes: list[dict[str, object]],
    pitfall_signals: list[str],
    touched_files: list[str],
) -> str:
    summary_parts: list[str] = []
    if capability_signals:
        summary_parts.append("introduces " + ", ".join(capability_signals))
    if quality_signals:
        summary_parts.append("adds " + ", ".join(quality_signals))
    if structure_signals:
        summary_parts.append("reshapes repository boundaries")
    if dependency_changes:
        manifests = ", ".join(change["manifest"] for change in dependency_changes)
        summary_parts.append(f"changes dependencies in {manifests}")
    if pitfall_signals:
        summary_parts.append("captures a real regression or fix")
    focus_files = ", ".join(touched_files[:3]) or "core files"
    if not summary_parts:
        summary_parts.append("touches meaningful repository surfaces")
    return f"{commit['message']} — " + "; ".join(summary_parts) + f". Key files: {focus_files}."


def build_guardrail(message: str, files: list[str], capability_signals: list[str]) -> str:
    lowered = message.lower()
    if "auth" in lowered or "auth" in capability_signals:
        if "redirect" in lowered:
            return "Protect auth redirects with regression coverage before changing routing or middleware."
        return "Protect auth/session flows with regression coverage before changing routing or middleware."
    if "schema" in lowered or "migration" in lowered:
        return "Keep schema changes and application code in lockstep, and add migration verification."
    if "prompt" in lowered or "tool" in lowered:
        return "Separate orchestration logic from prompts and tool adapters before extending the agent workflow."
    focus = ", ".join(files[:2]) or "the affected boundary"
    return f"Add guardrails around {focus} before the next refactor to avoid repeating the same failure mode."


def derive_candidate_score(
    message: str,
    totals: dict[str, int],
    dependency_changes: list[dict[str, object]],
    quality_signals: list[str],
    config_signals: list[str],
    capability_signals: list[str],
    profile_signals: list[str],
    structure_signals: list[str],
    pitfall_signals: list[str],
) -> tuple[int, list[str]]:
    lowered = message.lower()
    score = 0
    reasons: list[str] = []

    if any(token in lowered for token in ("feat", "introduce", "add", "init", "bootstrap")):
        score += 4
        reasons.append("durable capability")
    if dependency_changes:
        score += 3
        reasons.append("dependency change")
    if structure_signals:
        score += 4
        reasons.append("architecture/boundary change")
    if quality_signals:
        score += 4
        reasons.append("quality mechanism")
    if config_signals:
        score += 2
        reasons.append("config or deploy change")
    if pitfall_signals:
        score += 4
        reasons.append("pitfall or regression")
    if profile_signals:
        score += 3
        reasons.append("profile signal")
    if totals["files_changed"] >= 4:
        score += 1
        reasons.append("wide impact")
    if totals["additions"] + totals["deletions"] >= 80:
        score += 1
        reasons.append("substantial diff")
    if not reasons and capability_signals:
        score += 2
        reasons.append("capability hint")

    return score, reasons


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root)
    repo_path, repo_slug = ensure_local_repo(args.repo, output_root, args.allow_clone)
    analysis_dir = output_root / repo_slug / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    remove_paths(
        [
            analysis_dir / "milestone-review-prompt.md",
            analysis_dir / "milestone-review-packet.md",
            analysis_dir / "reviewed-milestones.md",
            analysis_dir / "reviewed-milestones.json",
            analysis_dir / "distilled-insights.md",
            analysis_dir / "distilled-insights.json",
        ]
    )

    manifests = list_manifests(repo_path)
    top_level_dirs = list_top_level_dirs(repo_path)
    commits = list_commits(repo_path)
    commit_evidence: list[dict[str, object]] = []

    for commit in commits:
        sha = commit["sha"]
        name_status = parse_name_status(
            run_git(repo_path, "show", "--format=", "--name-status", "--find-renames", sha)
        )
        numstat = parse_numstat(run_git(repo_path, "show", "--format=", "--numstat", "--find-renames", sha))
        patch_text = run_git(repo_path, "show", "--format=", "--find-renames", "--unified=3", sha)
        touched_files = [row["path"] for row in name_status]

        before_dirs = tree_dirs(repo_path, commit["parent_sha"]) if commit["parent_sha"] else set()
        after_dirs = tree_dirs(repo_path, sha)
        new_dirs = sorted(after_dirs - before_dirs)
        renamed_paths = [row["path"] for row in name_status if row["status"] in {"renamed", "copied"}]

        dependency_changes = collect_dependency_changes(repo_path, sha, commit["parent_sha"], touched_files)
        lowered_message = commit["message"].lower()
        signal_map = classify_paths(touched_files, lowered_message, patch_text, args.profile)
        pitfall_signals: list[str] = []
        if lowered_message.startswith(PITFALL_PREFIXES):
            pitfall_signals.append("fix-like commit")
        if lowered_message.startswith("regression:"):
            pitfall_signals.append("regression")

        structure_signals: list[str] = []
        if new_dirs:
            structure_signals.append("new directory boundary")
        if renamed_paths:
            structure_signals.append("rename or move")
        if any(part in lowered_message for part in ("refactor", "split", "extract", "modular")):
            structure_signals.append("explicit refactor")

        totals = {
            "files_changed": len(touched_files),
            "additions": sum(stats["additions"] for stats in numstat.values()),
            "deletions": sum(stats["deletions"] for stats in numstat.values()),
        }
        phase_hint = infer_phase(
            commit,
            dependency_changes,
            signal_map["quality_signals"],
            structure_signals,
            pitfall_signals,
        )
        score, reasons = derive_candidate_score(
            commit["message"],
            totals,
            dependency_changes,
            signal_map["quality_signals"],
            signal_map["config_signals"],
            signal_map["capability_signals"],
            signal_map["profile_signals"],
            structure_signals,
            pitfall_signals,
        )

        evidence = {
            **commit,
            "files": [
                {
                    "path": row["path"],
                    "status": row["status"],
                    "previous_path": row.get("previous_path"),
                    "additions": numstat.get(row["path"], {}).get("additions", 0),
                    "deletions": numstat.get(row["path"], {}).get("deletions", 0),
                }
                for row in name_status
            ],
            "totals": totals,
            "new_top_level_dirs": new_dirs,
            "renamed_paths": renamed_paths,
            "dependency_changes": dependency_changes,
            "signals": {
                "quality": signal_map["quality_signals"],
                "config": signal_map["config_signals"],
                "capability": signal_map["capability_signals"],
                "profile": signal_map["profile_signals"],
                "structure": structure_signals,
                "pitfall": pitfall_signals,
            },
            "phase_hint": phase_hint,
            "score": score,
            "reasons": reasons,
            "patch_excerpt": parse_patch_excerpt(patch_text),
            "evidence_summary": build_evidence_summary(
                commit,
                signal_map["capability_signals"],
                signal_map["quality_signals"],
                structure_signals,
                dependency_changes,
                pitfall_signals,
                touched_files,
            ),
        }
        if score > 0:
            commit_evidence.append(evidence)

    candidates = [
        {
            "sha": row["sha"],
            "message": row["message"],
            "authored_at": row["authored_at"],
            "score": row["score"],
            "reasons": row["reasons"],
            "phase_hint": row["phase_hint"],
            "files": [item["path"] for item in row["files"]],
            "evidence_summary": row["evidence_summary"],
            "evidence_refs": [f"commit-evidence.json#{row['sha']}"],
        }
        for row in commit_evidence
        if row["score"] >= 4
    ]

    dependency_events: list[dict[str, object]] = []
    architecture_timeline: list[dict[str, object]] = []
    pitfalls: list[dict[str, object]] = []
    phase_counter = Counter(row["phase_hint"] for row in candidates)

    for row in commit_evidence:
        if row["dependency_changes"]:
            dependency_events.append(
                {
                    "sha": row["sha"],
                    "message": row["message"],
                    "phase_hint": row["phase_hint"],
                    "changes": row["dependency_changes"],
                    "why": row["evidence_summary"],
                    "evidence_refs": [f"commit-evidence.json#{row['sha']}"],
                }
            )
        if row["signals"]["structure"] or row["signals"]["quality"]:
            architecture_timeline.append(
                {
                    "sha": row["sha"],
                    "message": row["message"],
                    "phase_hint": row["phase_hint"],
                    "summary": row["evidence_summary"],
                    "new_top_level_dirs": row["new_top_level_dirs"],
                    "files": [item["path"] for item in row["files"][:5]],
                    "evidence_refs": [f"commit-evidence.json#{row['sha']}"],
                }
            )
        if row["signals"]["pitfall"]:
            pitfalls.append(
                {
                    "sha": row["sha"],
                    "message": row["message"],
                    "files": [item["path"] for item in row["files"][:4]],
                    "guardrail": build_guardrail(
                        row["message"],
                        [item["path"] for item in row["files"]],
                        row["signals"]["capability"],
                    ),
                    "why": row["evidence_summary"],
                    "evidence_refs": [f"commit-evidence.json#{row['sha']}"],
                }
            )

    repo_summary = {
        "root": str(repo_path),
        "repo_slug": repo_slug,
        "profile": args.profile,
        "manifests": manifests,
        "top_level_dirs": top_level_dirs,
        "commit_count": len(commits),
        "candidate_count": len(candidates),
        "phase_distribution": dict(phase_counter),
    }

    architecture_patterns = []
    if any(item["new_top_level_dirs"] for item in architecture_timeline):
        architecture_patterns.append("new top-level directories appear as the repo grows")
    if any(item["phase_hint"] == "hardening" for item in architecture_timeline):
        architecture_patterns.append("quality layers arrive after the first feature slices")
    if any(item["phase_hint"] == "refactor" for item in architecture_timeline):
        architecture_patterns.append("boundary changes happen when feature pressure accumulates")

    stack_patterns = []
    if dependency_events:
        stack_patterns.append("dependencies are introduced incrementally to unlock durable capabilities")
    if any(change["manifest"] == "pyproject.toml" for event in dependency_events for change in event["changes"]):
        stack_patterns.append("Python tooling and quality settings evolve through pyproject.toml")
    if any(change["manifest"] == "package.json" for event in dependency_events for change in event["changes"]):
        stack_patterns.append("JavaScript stack choices are visible through package.json dependency churn")

    pitfall_guardrails = [item["guardrail"] for item in pitfalls]

    write_json(analysis_dir / "repo-summary.json", repo_summary)
    write_json(analysis_dir / "commit-evidence.json", commit_evidence)
    write_json(analysis_dir / "milestone-candidates.json", candidates)
    write_json(
        analysis_dir / "architecture-evolution.json",
        {
            "summary": "Repository boundaries evolved through concrete feature pressure and later hardening work.",
            "patterns": architecture_patterns,
            "timeline": architecture_timeline,
        },
    )
    write_json(
        analysis_dir / "stack-evolution.json",
        {
            "summary": "Dependency changes highlight when the repository introduced durable capabilities.",
            "patterns": stack_patterns,
            "dependency_events": dependency_events,
        },
    )
    write_json(
        analysis_dir / "pitfall-summary.json",
        {
            "summary": "Real fixes and regressions are converted into future guardrails.",
            "pitfalls": pitfalls,
            "guardrails": pitfall_guardrails,
        },
    )

    build_order = [
        phase for phase in ("bootstrap", "expansion", "hardening", "refactor", "pitfall") if phase_counter[phase]
    ]
    if not build_order:
        build_order = ["bootstrap", "expansion", "hardening"]
    architecture_lines = [f"- {pattern}" for pattern in architecture_patterns] or [
        "- no strong architecture pattern extracted yet"
    ]
    stack_lines = [f"- {pattern}" for pattern in stack_patterns] or ["- stack changes are minor or implicit"]
    pitfall_lines = [f"- {guardrail}" for guardrail in pitfall_guardrails[:5]] or [
        "- no major pitfall signals detected"
    ]
    report_lines = [
        f"# Distill Report: {repo_slug}",
        "",
        "## Repository Profile",
        f"- Profile: {args.profile}",
        f"- Commit count: {len(commits)}",
        f"- Manifests: {', '.join(manifests) or 'none'}",
        f"- Top-level directories: {', '.join(top_level_dirs) or 'none'}",
        "",
        "## Suggested Build Order",
        *[f"- {phase}" for phase in build_order],
        "",
        "## Milestone Candidates",
        *[
            f"- {row['message']} | phase={row['phase_hint']} | score={row['score']} | reasons={', '.join(row['reasons'])}"
            for row in candidates[:8]
        ],
        "",
        "## Architecture Signals",
        *architecture_lines,
        "",
        "## Stack Signals",
        *stack_lines,
        "",
        "## Pitfall Guardrails",
        *pitfall_lines,
        "",
        "## Recommended Next Step",
        "- Read commit-evidence.json and milestone-review-packet.md before synthesizing skills.",
    ]
    write_text(analysis_dir / "distill-report.md", "\n".join(report_lines))
    print(str(analysis_dir))


if __name__ == "__main__":
    main()
