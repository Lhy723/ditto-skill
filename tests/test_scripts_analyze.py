from pathlib import Path
import json
import subprocess
import sys

from scripts.common import normalize_repo_slug
from tests.helpers import build_web_saas_repo


def test_normalize_repo_slug_uses_repo_name_for_local_paths() -> None:
    assert normalize_repo_slug("/tmp/example-repo") == "example-repo"


def test_analyze_repo_script_extracts_real_evidence(tmp_path: Path) -> None:
    repo = build_web_saas_repo(tmp_path / "analysis-repo")
    output_root = tmp_path / "outputs"

    subprocess.run(
        [
            sys.executable,
            "/Users/lhy/Project/Prompt/ditto-skill/scripts/analyze_repo.py",
            "--repo",
            str(repo.path),
            "--profile",
            "web-saas",
            "--output-root",
            str(output_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    analysis_dir = output_root / "analysis-repo" / "analysis"
    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    commit_evidence = json.loads((analysis_dir / "commit-evidence.json").read_text())
    candidates = json.loads((analysis_dir / "milestone-candidates.json").read_text())
    architecture = json.loads((analysis_dir / "architecture-evolution.json").read_text())
    stack = json.loads((analysis_dir / "stack-evolution.json").read_text())
    pitfalls = json.loads((analysis_dir / "pitfall-summary.json").read_text())
    report = (analysis_dir / "distill-report.md").read_text()

    assert repo_summary["profile"] == "web-saas"
    assert ".pytest_cache" not in repo_summary["top_level_dirs"]
    assert "services" in repo_summary["top_level_dirs"]

    auth_commit = next(row for row in commit_evidence if row["message"] == "feat: add auth flow")
    assert auth_commit["dependency_changes"][0]["manifest"] == "package.json"
    assert "next-auth" in auth_commit["dependency_changes"][0]["added"]
    assert "auth" in auth_commit["signals"]["capability"]
    assert auth_commit["patch_excerpt"]

    hardening_candidate = next(
        row for row in candidates if row["message"] == "feat: add ci and regression coverage"
    )
    assert hardening_candidate["phase_hint"] == "hardening"
    assert "quality mechanism" in hardening_candidate["reasons"]
    assert "tests/auth_redirect.test.ts" in hardening_candidate["files"]

    assert architecture["timeline"]
    assert "boundary" in " ".join(architecture["patterns"])
    assert stack["dependency_events"]
    assert any("stripe" in change["added"] for event in stack["dependency_events"] for change in event["changes"])
    assert pitfalls["pitfalls"]
    assert "redirect" in pitfalls["pitfalls"][0]["guardrail"].lower()
    assert "Suggested Build Order" in report
