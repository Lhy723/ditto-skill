from pathlib import Path
import json
import subprocess
import sys

import pytest


def valid_insights_draft() -> str:
    return "\n".join(
        [
            "# Distilled Insights Draft: sample-repo",
            "",
            "## Project Archetype",
            "- summary: sample-repo is a web-saas repository distilled from git evolution evidence.",
            "- profile: web-saas",
            "- manifests:",
            "  - package.json",
            "- top_level_dirs:",
            "  - app",
            "  - services",
            "",
            "## Build Phases",
            "### Phase",
            "- phase: bootstrap",
            "- when: At project start.",
            "- why: The repo started with a minimal app shell.",
            "- actions:",
            "  - Create the smallest runnable slice first.",
            "- evidence_refs:",
            "  - commit-evidence.json#root",
            "",
            "## Default Build Order",
            "### Step",
            "- phase: bootstrap",
            "- recommendation: Create the smallest runnable slice first.",
            "- why: The repo started with a minimal app shell.",
            "",
            "## Architecture Rules",
            "- items:",
            "  - Split services from routes once shared business logic leaks across request handlers.",
            "",
            "## Stack Patterns",
            "- items:",
            "  - Introduce auth dependencies only when auth becomes durable.",
            "",
            "## Quality Rules",
            "- items:",
            "  - Add regression coverage once auth and routing flows become product-critical.",
            "",
            "## Pitfall Guardrails",
            "- items:",
            "  - Protect auth redirects with regression coverage before changing middleware.",
            "",
            "## Subskill Mapping",
            "### Subskill",
            "- slug: bootstrap",
            "- when_to_use:",
            "  - You are starting a similar SaaS repo from scratch.",
            "- what_to_do:",
            "  - Create the smallest app shell before adding auth or billing.",
            "- what_to_avoid:",
            "  - Do not introduce every service abstraction on day one.",
            "- signals_to_watch:",
            "  - The first working route exists.",
            "- evidence_refs:",
            "  - commit-evidence.json#root",
            "",
            "### Subskill",
            "- slug: architecture-evolution",
            "- when_to_use:",
            "  - Module boundaries start to blur.",
            "- what_to_do:",
            "  - Split services from routes when shared business logic leaks.",
            "- what_to_avoid:",
            "  - Do not refactor only for aesthetics.",
            "- signals_to_watch:",
            "  - Repeated cross-boundary edits.",
            "- evidence_refs:",
            "  - commit-evidence.json#a1",
            "",
            "### Subskill",
            "- slug: quality-hardening",
            "- when_to_use:",
            "  - Core flows have stabilized.",
            "- what_to_do:",
            "  - Add tests and CI around product-critical paths.",
            "- what_to_avoid:",
            "  - Do not postpone verification indefinitely.",
            "- signals_to_watch:",
            "  - Regressions begin to hurt velocity.",
            "- evidence_refs:",
            "  - commit-evidence.json#q1",
            "",
            "### Subskill",
            "- slug: stack-specific",
            "- when_to_use:",
            "  - You want to reuse stack choices intentionally.",
            "- what_to_do:",
            "  - Add dependencies only when they unlock repeated value.",
            "- what_to_avoid:",
            "  - Do not cargo-cult every dependency.",
            "- signals_to_watch:",
            "  - Manifest changes tied to new capabilities.",
            "- evidence_refs:",
            "  - commit-evidence.json#s1",
            "",
            "### Subskill",
            "- slug: pitfall-avoidance",
            "- when_to_use:",
            "  - A real failure mode has been exposed.",
            "- what_to_do:",
            "  - Convert recurring fixes into explicit guardrails.",
            "- what_to_avoid:",
            "  - Do not treat regressions as one-off accidents.",
            "- signals_to_watch:",
            "  - Fix and revert commits touching auth or routing.",
            "- evidence_refs:",
            "  - commit-evidence.json#p1",
            "",
            "## Evidence Refs",
            "- items:",
            "  - commit-evidence.json#root",
            "  - commit-evidence.json#a1",
            "",
        ]
    )


def test_compile_insights_script_turns_draft_into_json(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "distilled-insights.md").write_text(valid_insights_draft())

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/compile_insights.py",
            "--analysis-dir",
            str(analysis_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    insights = json.loads((analysis_dir / "distilled-insights.json").read_text())
    assert insights["project_archetype"]["profile"] == "web-saas"
    assert insights["build_phases"][0]["phase"] == "bootstrap"
    assert insights["subskill_mapping"]["bootstrap"]["what_to_do"]


def test_compile_insights_script_fails_on_missing_section(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "distilled-insights.md").write_text(
        "# Distilled Insights Draft: sample-repo\n\n## Project Archetype\n- summary: x\n- profile: general\n- manifests:\n  - pyproject.toml\n- top_level_dirs:\n  - src\n"
    )

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            [
                sys.executable,
                "/Users/lhy/Project/Prompt/ditto-skill/scripts/compile_insights.py",
                "--analysis-dir",
                str(analysis_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
