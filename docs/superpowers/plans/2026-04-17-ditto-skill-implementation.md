# Ditto Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full agreed v1 of `ditto-skill`: accept either a GitHub URL or the current local git repo, analyze git evolution into JSON + Markdown artifacts, require review before synthesis, and generate one master skill plus reusable subskills from the reviewed analysis.

**Architecture:** Put all deterministic work in a small Python package and keep the root `SKILL.md` focused on user interaction rules: confirm before cloning, analyze before synthesis, and load references progressively. Split the implementation into four pipelines that share typed models: repo intake, git-history distillation, analysis artifact writing, and reviewed-artifact synthesis.

**Tech Stack:** Python 3.12, git CLI, pytest, PyYAML, Markdown, JSON, Codex skill metadata helpers

---

## Preparation

- [ ] **Step 1: Initialize version control for the workspace**

Run: `git -C /Users/lhy/Project/Prompt/ditto-skill init`
Expected: `Initialized empty Git repository` appears and `/Users/lhy/Project/Prompt/ditto-skill/.git` exists.

- [ ] **Step 2: Create the local virtualenv**

Run: `python3 -m venv /Users/lhy/Project/Prompt/ditto-skill/.venv`
Expected: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python` exists.

- [ ] **Step 3: Install the development tooling**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pip install --upgrade pip setuptools wheel pytest PyYAML`
Expected: pip completes successfully and reports `pytest` and `PyYAML` installed.

## File Structure

- `/Users/lhy/Project/Prompt/ditto-skill/.gitignore`
  Ignore the virtualenv, caches, generated outputs, and temporary clones.
- `/Users/lhy/Project/Prompt/ditto-skill/pyproject.toml`
  Define editable install metadata and dev dependencies.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/__init__.py`
  Package marker and version.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/models.py`
  Shared dataclasses for repo sources, profiles, commits, artifacts, and synthesis inputs.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/repo_intake.py`
  Parse repo input, gate clone behavior, and profile the active repository.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/git_history.py`
  Extract raw commit history, changed files, and insertion/deletion stats from git.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/heuristics.py`
  Score candidate milestone commits with general, `web-saas`, and `ai-agent` profile weights.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/llm_review.py`
  Build the review packet that the skill uses for the milestone-review phase and load reviewed decisions.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/analysis.py`
  Write `scan` and `analyze` artifacts to `outputs/<slug>/analysis/`.
- `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/synthesis.py`
  Generate the master skill and subskills from reviewed analysis artifacts.
- `/Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py`
  CLI entry point for `scan`, `analyze`, `synthesize`, and `full`.
- `/Users/lhy/Project/Prompt/ditto-skill/SKILL.md`
  Root skill definition with the user-facing workflow.
- `/Users/lhy/Project/Prompt/ditto-skill/references/artifact-schema.md`
  Explain every analysis artifact and when it is written.
- `/Users/lhy/Project/Prompt/ditto-skill/references/milestone-rubric.md`
  Explain the heuristic and LLM review rubric.
- `/Users/lhy/Project/Prompt/ditto-skill/references/profile-general.md`
  Baseline signals that apply across repository types.
- `/Users/lhy/Project/Prompt/ditto-skill/references/profile-web-saas.md`
  Profile-specific signals for web/SaaS repos.
- `/Users/lhy/Project/Prompt/ditto-skill/references/profile-ai-agent.md`
  Profile-specific signals for AI/agent repos.
- `/Users/lhy/Project/Prompt/ditto-skill/references/skill-package-template.md`
  Describe the expected structure of master-skill and subskills.
- `/Users/lhy/Project/Prompt/ditto-skill/agents/openai.yaml`
  UI-facing metadata for the skill.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/helpers.py`
  Reusable temp git repo builder.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py`
  Verify the helper repo builder.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py`
  Cover local-vs-GitHub input, clone gating, and profiling.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py`
  Cover raw commit extraction.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py`
  Cover profile-sensitive milestone scoring.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_llm_review.py`
  Cover review-packet writing and reviewed-decision loading.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_analysis.py`
  Cover scan/analyze artifact writing.
- `/Users/lhy/Project/Prompt/ditto-skill/tests/test_synthesis.py`
  Cover master skill and subskill generation from reviewed artifacts.

### Task 1: Bootstrap the project and git-repo test helper

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/.gitignore`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/pyproject.toml`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/__init__.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/helpers.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py`

- [ ] **Step 1: Write the failing helper test**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py
from pathlib import Path

from tests.helpers import make_git_repo


def test_make_git_repo_creates_expected_history(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "sample",
        [
            ("feat: init", {"README.md": "# sample\n"}),
            ("refactor: add service", {"service.py": "def run():\n    return 'ok'\n"}),
        ],
    )

    assert repo.run_git("rev-list", "--count", "HEAD") == "2"
    assert repo.run_git("log", "--pretty=%s", "-1") == "refactor: add service"
```

- [ ] **Step 2: Run the helper test and verify it fails**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py::test_make_git_repo_creates_expected_history -q`
Expected: FAIL with `ModuleNotFoundError` because `tests.helpers` does not exist yet.

- [ ] **Step 3: Implement the bootstrap files**

```toml
# /Users/lhy/Project/Prompt/ditto-skill/pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "ditto-skill"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.2", "PyYAML>=6.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/helpers.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class TempRepo:
    path: Path

    def run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.path,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()


def make_git_repo(path: Path, commits: list[tuple[str, dict[str, str]]]) -> TempRepo:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Ditto Skill Tests"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "ditto-tests@example.com"], cwd=path, check=True, capture_output=True, text=True)

    for message, files in commits:
        for relpath, content in files.items():
            file_path = path / relpath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, capture_output=True, text=True)

    return TempRepo(path=path)
```

```gitignore
# /Users/lhy/Project/Prompt/ditto-skill/.gitignore
.venv/
__pycache__/
.pytest_cache/
outputs/
tmp/
```

- [ ] **Step 4: Install the package and rerun the helper test**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pip install -e /Users/lhy/Project/Prompt/ditto-skill[dev] && /Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py::test_make_git_repo_creates_expected_history -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the bootstrap**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add .gitignore pyproject.toml ditto_skill/__init__.py tests/helpers.py tests/test_helpers.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "chore: bootstrap ditto skill project"
```

### Task 2: Implement repo intake, GitHub clone gating, and repository profiling

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/models.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/repo_intake.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py`

- [ ] **Step 1: Write the failing repo-intake tests**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py
from pathlib import Path

from ditto_skill.models import RepoSource
from ditto_skill.repo_intake import detect_repo_source, prepare_local_repo, profile_repo
from tests.helpers import make_git_repo


def test_detect_repo_source_defaults_to_current_repo(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path / "current-repo", [("feat: init", {"README.md": "# hi\n"})])
    source = detect_repo_source(None, repo.path)
    assert source == RepoSource(kind="local", value=str(repo.path), slug="current-repo")


def test_detect_repo_source_parses_github_url() -> None:
    source = detect_repo_source("https://github.com/openai/example", Path.cwd())
    assert source.kind == "github"
    assert source.slug == "openai-example"


def test_prepare_local_repo_requires_clone_confirmation(tmp_path: Path) -> None:
    source = RepoSource(kind="github", value="https://github.com/openai/example", slug="openai-example")
    try:
        prepare_local_repo(source, tmp_path / "clones", allow_clone=False)
    except PermissionError as exc:
        assert "Clone confirmation required" in str(exc)
    else:
        raise AssertionError("expected PermissionError")


def test_profile_repo_collects_manifest_and_commit_count(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "profile-repo",
        [("feat: init app", {"package.json": '{"name":"profile"}', "app/page.tsx": "export default function Page() { return null }\n"})],
    )
    profile = profile_repo(repo.path)
    assert "package.json" in profile.manifests
    assert "app" in profile.top_level_dirs
    assert profile.commit_count == 1
```

- [ ] **Step 2: Run the intake tests and verify they fail**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py -q`
Expected: FAIL because `ditto_skill.models` and `ditto_skill.repo_intake` do not exist yet.

- [ ] **Step 3: Implement repo models, input detection, clone gating, profiling, and the CLI shell**

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/models.py
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
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/repo_intake.py
from __future__ import annotations

from pathlib import Path
import re
import subprocess

from ditto_skill.models import RepoProfile, RepoSource


GITHUB_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")


def detect_repo_source(repo_arg: str | None, cwd: Path) -> RepoSource:
    if repo_arg is None:
        return RepoSource(kind="local", value=str(cwd), slug=cwd.name)

    match = GITHUB_RE.match(repo_arg)
    if match:
        owner = match.group("owner")
        repo = match.group("repo").removesuffix(".git")
        return RepoSource(kind="github", value=repo_arg, slug=f"{owner}-{repo}")

    path = Path(repo_arg).expanduser().resolve()
    return RepoSource(kind="local", value=str(path), slug=path.name)


def prepare_local_repo(source: RepoSource, clones_dir: Path, allow_clone: bool) -> Path:
    if source.kind == "local":
        path = Path(source.value)
        if not (path / ".git").exists():
            raise FileNotFoundError(f"{path} is not a git repository")
        return path

    destination = clones_dir / source.slug
    if not allow_clone:
        raise PermissionError(f"Clone confirmation required for {source.value} -> {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", source.value, str(destination)], check=True, text=True)
    return destination


def profile_repo(repo_path: Path, selected_profile: str = "general") -> RepoProfile:
    manifests = [name for name in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod"] if (repo_path / name).exists()]
    top_level_dirs = sorted(child.name for child in repo_path.iterdir() if child.is_dir() and child.name != ".git")
    commit_count = int(
        subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    )
    return RepoProfile(root=repo_path, manifests=manifests, top_level_dirs=top_level_dirs, commit_count=commit_count, profile=selected_profile)
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py
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
```

- [ ] **Step 4: Run the intake tests and a CLI smoke test**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py -q`
Expected: PASS with `4 passed`.

Run: `cd /Users/lhy/Project/Prompt/ditto-skill && .venv/bin/python scripts/distill_repo.py --mode scan --profile general`
Expected: prints `local:<slug>:<commit_count>:general` if the workspace is a git repo, or a clear local-repo error otherwise.

- [ ] **Step 5: Commit repo intake**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add ditto_skill/models.py ditto_skill/repo_intake.py scripts/distill_repo.py tests/test_repo_intake.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: add repo intake and profiling"
```

### Task 3: Extract raw git history and profile-sensitive milestone candidates

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/git_history.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/heuristics.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py`

- [ ] **Step 1: Write the failing history and heuristic tests**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py
from pathlib import Path

from ditto_skill.git_history import collect_commit_history
from tests.helpers import make_git_repo


def test_collect_commit_history_returns_changed_files(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "history-repo",
        [
            ("feat: init app", {"package.json": '{"name":"history"}', "app/page.tsx": "export default function Page() { return null }\n"}),
            ("fix: handle crash", {"app/error.tsx": "export default function Error() { return null }\n"}),
        ],
    )
    history = collect_commit_history(repo.path)
    assert history[0].message == "fix: handle crash"
    assert "app/error.tsx" in history[0].changed_files
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py
from pathlib import Path

from ditto_skill.git_history import collect_commit_history
from ditto_skill.heuristics import collect_milestone_candidates
from tests.helpers import make_git_repo


def test_web_saas_profile_boosts_auth_and_schema_signals(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "saas-repo",
        [
            ("docs: setup", {"README.md": "# docs\n"}),
            ("feat: add auth flow", {"app/auth.ts": "export const auth = true\n"}),
            ("feat: add schema", {"drizzle/schema.ts": "export const users = {}\n"}),
        ],
    )
    history = collect_commit_history(repo.path)
    candidates = collect_milestone_candidates(history, selected_profile="web-saas", limit=2)
    messages = [candidate.message for candidate in candidates]
    assert messages == ["feat: add schema", "feat: add auth flow"]
```

- [ ] **Step 2: Run the history and heuristic tests and verify they fail**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py /Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py -q`
Expected: FAIL because `ditto_skill.git_history` and `ditto_skill.heuristics` do not exist yet.

- [ ] **Step 3: Implement history extraction and heuristic scoring**

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/git_history.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    message: str
    changed_files: list[str]
    insertions: int
    deletions: int


def collect_commit_history(repo_path: Path, limit: int | None = None) -> list[CommitRecord]:
    log_cmd = ["git", "log", "--pretty=format:%H%x1f%s%x1e", "--name-only", "--numstat"]
    if limit is not None:
        log_cmd.insert(2, f"-n{limit}")
    raw = subprocess.run(log_cmd, cwd=repo_path, check=True, text=True, capture_output=True).stdout
    records: list[CommitRecord] = []
    for entry in raw.strip("\n\x1e").split("\x1e"):
        lines = [line for line in entry.splitlines() if line.strip()]
        header = lines[0]
        sha, message = header.split("\x1f", 1)
        changed_files: list[str] = []
        insertions = 0
        deletions = 0
        for line in lines[1:]:
            if "\t" in line and line.split("\t", 1)[0].isdigit():
                added, removed, file_path = line.split("\t", 2)
                insertions += int(added)
                deletions += int(removed)
                changed_files.append(file_path)
            elif "/" in line or "." in line:
                changed_files.append(line)
        records.append(CommitRecord(sha=sha, message=message, changed_files=sorted(set(changed_files)), insertions=insertions, deletions=deletions))
    return records
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/heuristics.py
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
    score = 0
    reasons: list[str] = []
    lowered = commit.message.lower()
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
    if selected_profile == "ai-agent":
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


def collect_milestone_candidates(history: list[CommitRecord], selected_profile: str, limit: int = 12) -> list[MilestoneCandidate]:
    candidates: list[MilestoneCandidate] = []
    for commit in history:
        score, reasons = _base_score(commit)
        bonus, profile_reasons = _profile_bonus(commit, selected_profile)
        total = score + bonus
        if total > 0:
            candidates.append(MilestoneCandidate(sha=commit.sha, message=commit.message, score=total, reasons=reasons + profile_reasons))
    return sorted(candidates, key=lambda item: item.score, reverse=True)[:limit]
```

- [ ] **Step 4: Run the history and heuristic tests**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py /Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py -q`
Expected: PASS with `2 passed`.

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_helpers.py /Users/lhy/Project/Prompt/ditto-skill/tests/test_repo_intake.py /Users/lhy/Project/Prompt/ditto-skill/tests/test_git_history.py /Users/lhy/Project/Prompt/ditto-skill/tests/test_heuristics.py -q`
Expected: PASS with all helper, intake, history, and heuristic tests green.

- [ ] **Step 5: Commit history extraction and heuristics**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add ditto_skill/git_history.py ditto_skill/heuristics.py tests/test_git_history.py tests/test_heuristics.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: add git history extraction and heuristics"
```

### Task 4: Build the LLM review packet and reviewed-milestone loader

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/llm_review.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_llm_review.py`

- [ ] **Step 1: Write the failing LLM-review test**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_llm_review.py
from pathlib import Path
import json

from ditto_skill.heuristics import MilestoneCandidate
from ditto_skill.llm_review import build_review_packet, load_reviewed_milestones


def test_build_review_packet_and_load_reviewed_decisions(tmp_path: Path) -> None:
    candidates = [
        MilestoneCandidate(sha="a1", message="feat: add auth", score=6, reasons=["feature", "web-saas auth"]),
        MilestoneCandidate(sha="b2", message="docs: update readme", score=1, reasons=["low-signal docs/typo"]),
    ]
    analysis_dir = tmp_path / "analysis"
    build_review_packet("sample-repo", candidates, analysis_dir)

    reviewed_path = analysis_dir / "reviewed-milestones.json"
    reviewed_path.write_text(
        json.dumps(
            [
                {"sha": "a1", "message": "feat: add auth", "decision": "keep", "why": "Introduces a durable capability."}
            ],
            indent=2,
        )
    )

    reviewed = load_reviewed_milestones(reviewed_path)
    assert reviewed[0]["decision"] == "keep"
    assert (analysis_dir / "milestone-review-prompt.md").exists()
```

- [ ] **Step 2: Run the review test and verify it fails**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_llm_review.py::test_build_review_packet_and_load_reviewed_decisions -q`
Expected: FAIL because `ditto_skill.llm_review` does not exist yet.

- [ ] **Step 3: Implement review-packet writing and reviewed-milestone loading**

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/llm_review.py
from __future__ import annotations

from pathlib import Path
import json

from ditto_skill.heuristics import MilestoneCandidate


def build_review_packet(repo_slug: str, candidates: list[MilestoneCandidate], analysis_dir: Path) -> None:
    analysis_dir.mkdir(parents=True, exist_ok=True)
    packet = [
        {
            "sha": candidate.sha,
            "message": candidate.message,
            "score": candidate.score,
            "reasons": candidate.reasons,
        }
        for candidate in candidates
    ]
    (analysis_dir / "milestone-candidates.json").write_text(json.dumps(packet, indent=2))

    prompt_lines = [
        f"# Milestone Review Prompt: {repo_slug}",
        "",
        "Review each candidate commit and decide whether it is a true milestone worth distilling into future skills.",
        "",
        "For each kept commit, write one line of reasoning that explains the durable engineering lesson.",
        "",
        "## Candidates",
    ]
    prompt_lines.extend([f"- {candidate.message} | score={candidate.score} | reasons={', '.join(candidate.reasons)}" for candidate in candidates])
    (analysis_dir / "milestone-review-prompt.md").write_text("\n".join(prompt_lines) + "\n")


def load_reviewed_milestones(reviewed_path: Path) -> list[dict[str, str]]:
    if not reviewed_path.exists():
        raise FileNotFoundError(f"reviewed milestones missing: {reviewed_path}")
    return json.loads(reviewed_path.read_text())
```

- [ ] **Step 4: Run the review test**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_llm_review.py -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the review-packet layer**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add ditto_skill/llm_review.py tests/test_llm_review.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: add milestone review packet"
```

### Task 5: Implement `scan` and `analyze` artifacts exactly as agreed

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/analysis.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_analysis.py`
- Modify: `/Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py`

- [ ] **Step 1: Write the failing analysis test**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_analysis.py
from pathlib import Path
import json

from ditto_skill.analysis import run_analysis
from tests.helpers import make_git_repo


def test_run_analysis_writes_full_v1_artifacts(tmp_path: Path) -> None:
    repo = make_git_repo(
        tmp_path / "analysis-repo",
        [
            ("feat: init app", {"package.json": '{"name":"analysis"}', "app/page.tsx": "export default function Page() { return null }\n"}),
            ("feat: add auth", {"app/auth.ts": "export const auth = true\n"}),
            ("refactor: split routes", {"app/routes.ts": "export const routes = []\n"}),
        ],
    )
    analysis_dir = tmp_path / "outputs" / "analysis-repo" / "analysis"

    run_analysis(repo.path, analysis_dir, selected_profile="web-saas", mode="analyze")

    expected_files = {
        "repo-summary.json",
        "milestone-candidates.json",
        "milestone-review-prompt.md",
        "architecture-evolution.json",
        "stack-evolution.json",
        "pitfall-summary.json",
        "distill-report.md",
    }
    assert expected_files.issubset({path.name for path in analysis_dir.iterdir()})
    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    assert repo_summary["profile"] == "web-saas"
    assert "## Recommended Next Step" in (analysis_dir / "distill-report.md").read_text()
```

- [ ] **Step 2: Run the analysis test and verify it fails**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_analysis.py::test_run_analysis_writes_full_v1_artifacts -q`
Expected: FAIL because `ditto_skill.analysis` does not exist yet.

- [ ] **Step 3: Implement scan/analyze artifact writing and extend the CLI**

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/analysis.py
from __future__ import annotations

from pathlib import Path
import json

from ditto_skill.git_history import collect_commit_history
from ditto_skill.heuristics import collect_milestone_candidates
from ditto_skill.llm_review import build_review_packet
from ditto_skill.repo_intake import profile_repo


def run_analysis(repo_path: Path, analysis_dir: Path, selected_profile: str, mode: str) -> None:
    analysis_dir.mkdir(parents=True, exist_ok=True)
    profile = profile_repo(repo_path, selected_profile=selected_profile)
    history = collect_commit_history(repo_path)
    candidates = collect_milestone_candidates(history, selected_profile=selected_profile)

    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": str(profile.root),
                "profile": profile.profile,
                "manifests": profile.manifests,
                "top_level_dirs": profile.top_level_dirs,
                "commit_count": profile.commit_count,
            },
            indent=2,
        )
    )
    build_review_packet(repo_path.name, candidates, analysis_dir)

    if mode == "scan":
        return

    (analysis_dir / "architecture-evolution.json").write_text(
        json.dumps(
            {
                "summary": "Summarize boundary changes from top-level directories and high-scoring refactor commits.",
                "top_level_dirs": profile.top_level_dirs,
                "notable_commits": [candidate.message for candidate in candidates[:5]],
            },
            indent=2,
        )
    )
    (analysis_dir / "stack-evolution.json").write_text(
        json.dumps(
            {
                "manifests": profile.manifests,
                "profile": selected_profile,
                "top_candidate_messages": [candidate.message for candidate in candidates[:5]],
            },
            indent=2,
        )
    )
    (analysis_dir / "pitfall-summary.json").write_text(
        json.dumps(
            {
                "messages": [candidate.message for candidate in candidates if candidate.message.lower().startswith(("fix", "refactor"))],
                "note": "These commits should be reviewed for pitfalls and corrections before synthesis.",
            },
            indent=2,
        )
    )
    report_lines = [
        f"# Distill Report: {repo_path.name}",
        "",
        "## Repository Profile",
        f"- Profile: {selected_profile}",
        f"- Manifests: {', '.join(profile.manifests) or 'none'}",
        f"- Top-level directories: {', '.join(profile.top_level_dirs) or 'none'}",
        f"- Commit count: {profile.commit_count}",
        "",
        "## Milestone Candidates",
        *[f"- {candidate.message} | score={candidate.score} | reasons={', '.join(candidate.reasons)}" for candidate in candidates],
        "",
        "## Recommended Next Step",
        "- Review `milestone-review-prompt.md` and write `reviewed-milestones.json` before synthesis.",
    ]
    (analysis_dir / "distill-report.md").write_text("\n".join(report_lines) + "\n")
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py
from __future__ import annotations

import argparse
from pathlib import Path

from ditto_skill.analysis import run_analysis
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

    if args.mode == "scan":
        analysis_dir = Path(args.output_root) / source.slug / "analysis"
        run_analysis(repo_path, analysis_dir, selected_profile=args.profile, mode="scan")
        print(str(analysis_dir))
        return

    analysis_dir = Path(args.output_root) / source.slug / "analysis"
    run_analysis(repo_path, analysis_dir, selected_profile=args.profile, mode="analyze")
    print(str(analysis_dir))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the analysis tests and a script smoke test**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_analysis.py -q`
Expected: PASS with `1 passed`.

Run: `cd /Users/lhy/Project/Prompt/ditto-skill && .venv/bin/python scripts/distill_repo.py --mode analyze --profile general --repo /Users/lhy/Project/Prompt/ditto-skill`
Expected: creates `outputs/<slug>/analysis` containing `repo-summary.json`, `milestone-candidates.json`, `milestone-review-prompt.md`, `architecture-evolution.json`, `stack-evolution.json`, `pitfall-summary.json`, and `distill-report.md`.

- [ ] **Step 5: Commit the analysis layer**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add ditto_skill/analysis.py scripts/distill_repo.py tests/test_analysis.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: add scan and analyze artifact generation"
```

### Task 6: Implement synthesis from reviewed artifacts into the master skill and five subskills

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/ditto_skill/synthesis.py`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/tests/test_synthesis.py`
- Modify: `/Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py`

- [ ] **Step 1: Write the failing synthesis test**

```python
# /Users/lhy/Project/Prompt/ditto-skill/tests/test_synthesis.py
from pathlib import Path
import json

from ditto_skill.synthesis import synthesize_skill_package


def test_synthesize_skill_package_creates_master_and_expected_subskills(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "outputs" / "sample-repo" / "analysis"
    analysis_dir.mkdir(parents=True)
    (analysis_dir / "repo-summary.json").write_text(
        json.dumps(
            {
                "root": "/tmp/sample-repo",
                "profile": "web-saas",
                "manifests": ["package.json"],
                "top_level_dirs": ["app", "tests", "drizzle"],
                "commit_count": 4,
            },
            indent=2,
        )
    )
    (analysis_dir / "reviewed-milestones.json").write_text(
        json.dumps(
            [
                {"sha": "a1", "message": "feat: add auth", "decision": "keep", "why": "Introduces reusable auth capability."},
                {"sha": "b2", "message": "refactor: split routes", "decision": "keep", "why": "Shows when to separate boundaries."},
            ],
            indent=2,
        )
    )
    (analysis_dir / "stack-evolution.json").write_text(json.dumps({"manifests": ["package.json"], "profile": "web-saas"}, indent=2))
    (analysis_dir / "pitfall-summary.json").write_text(json.dumps({"messages": ["fix: patch auth redirect"]}, indent=2))
    skills_dir = tmp_path / "outputs" / "sample-repo" / "skills"

    synthesize_skill_package("sample-repo", analysis_dir, skills_dir)

    assert (skills_dir / "master-skill" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "bootstrap" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "architecture-evolution" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "quality-hardening" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "stack-specific" / "SKILL.md").exists()
    assert (skills_dir / "subskills" / "pitfall-avoidance" / "SKILL.md").exists()
```

- [ ] **Step 2: Run the synthesis test and verify it fails**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_synthesis.py::test_synthesize_skill_package_creates_master_and_expected_subskills -q`
Expected: FAIL because `ditto_skill.synthesis` does not exist yet.

- [ ] **Step 3: Implement synthesis and extend the CLI**

```python
# /Users/lhy/Project/Prompt/ditto-skill/ditto_skill/synthesis.py
from __future__ import annotations

from pathlib import Path
import json


def _write_skill(path: Path, name: str, description: str, body_lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        + "\n".join(body_lines)
        + "\n"
    )


def synthesize_skill_package(repo_slug: str, analysis_dir: Path, skills_dir: Path) -> None:
    reviewed_path = analysis_dir / "reviewed-milestones.json"
    if not reviewed_path.exists():
        raise FileNotFoundError(f"reviewed milestones missing: {reviewed_path}")

    repo_summary = json.loads((analysis_dir / "repo-summary.json").read_text())
    reviewed = json.loads(reviewed_path.read_text())
    pitfall_summary = json.loads((analysis_dir / "pitfall-summary.json").read_text())

    _write_skill(
        skills_dir / "master-skill" / "SKILL.md",
        f"{repo_slug}-master",
        "Master distilled skill generated from reviewed repository evolution artifacts.",
        [
            "# Master Skill",
            "",
            f"- Project archetype: profile={repo_summary['profile']}, manifests={', '.join(repo_summary['manifests']) or 'none'}",
            f"- Default build order: start from {', '.join(repo_summary['top_level_dirs']) or 'the smallest working slice'}",
            "- Architecture heuristics: use reviewed refactor milestones to decide when to split boundaries.",
            "- Quality rules: add test, lint, and CI layers once the first feature slice stabilizes.",
            "- Pitfalls to avoid: convert reviewed fixes and pitfall messages into explicit guardrails.",
            "",
            "## Reviewed Milestones",
            *[f"- {entry['message']}: {entry['why']}" for entry in reviewed if entry['decision'] == 'keep'],
        ],
    )

    subskill_specs = {
        "bootstrap": "Create the smallest viable skeleton before layering more systems.",
        "architecture-evolution": "Promote boundary changes only when reviewed milestones show real pressure.",
        "quality-hardening": "Add tests, linting, types, and CI in the order implied by reviewed milestones.",
        "stack-specific": f"Prefer stack patterns consistent with profile={repo_summary['profile']}.",
        "pitfall-avoidance": "Avoid reintroducing the mistakes reflected in fixes, reverts, and pitfall summaries.",
    }
    for slug, summary in subskill_specs.items():
        _write_skill(
            skills_dir / "subskills" / slug / "SKILL.md",
            f"{repo_slug}-{slug}",
            summary,
            [
                f"# {slug.replace('-', ' ').title()}",
                "",
                summary,
                "",
                "## Inputs",
                *[f"- {entry['message']}" for entry in reviewed if entry['decision'] == 'keep'],
                "",
                "## Pitfalls",
                *[f"- {message}" for message in pitfall_summary.get('messages', [])],
            ],
        )
```

```python
# /Users/lhy/Project/Prompt/ditto-skill/scripts/distill_repo.py
from __future__ import annotations

import argparse
from pathlib import Path

from ditto_skill.analysis import run_analysis
from ditto_skill.repo_intake import detect_repo_source, prepare_local_repo
from ditto_skill.synthesis import synthesize_skill_package


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
    analysis_dir = Path(args.output_root) / source.slug / "analysis"
    skills_dir = Path(args.output_root) / source.slug / "skills"

    if args.mode == "synthesize":
        synthesize_skill_package(source.slug, analysis_dir, skills_dir)
        print(str(skills_dir))
        return

    repo_path = prepare_local_repo(source, Path(args.clones_dir), allow_clone=args.allow_clone)
    selected_mode = "scan" if args.mode == "scan" else "analyze"
    run_analysis(repo_path, analysis_dir, selected_profile=args.profile, mode=selected_mode)

    if args.mode == "full":
        if not (analysis_dir / "reviewed-milestones.json").exists():
            raise FileNotFoundError(
                f"reviewed milestones missing: {analysis_dir / 'reviewed-milestones.json'}; "
                "finish the review step before using --mode full"
            )
        synthesize_skill_package(source.slug, analysis_dir, skills_dir)
        print(str(skills_dir))
        return

    print(str(analysis_dir))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run synthesis tests and the full test suite**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests/test_synthesis.py -q`
Expected: PASS with `1 passed`.

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python -m pytest /Users/lhy/Project/Prompt/ditto-skill/tests -q`
Expected: PASS with helper, intake, history, heuristics, review, analysis, and synthesis tests all green.

- [ ] **Step 5: Commit synthesis**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add ditto_skill/synthesis.py scripts/distill_repo.py tests/test_synthesis.py
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: synthesize skills from reviewed artifacts"
```

### Task 7: Write the root skill, references, metadata, and end-to-end validation

**Files:**
- Create: `/Users/lhy/Project/Prompt/ditto-skill/SKILL.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/artifact-schema.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/milestone-rubric.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/profile-general.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/profile-web-saas.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/profile-ai-agent.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/references/skill-package-template.md`
- Create: `/Users/lhy/Project/Prompt/ditto-skill/agents/openai.yaml`

- [ ] **Step 1: Write the root skill and every required reference**

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/SKILL.md
---
name: ditto-skill
description: Distill a software repository's git evolution and current structure into reusable coding-agent skills. Use when Codex needs to analyze a local git repo or a GitHub repo, produce JSON and Markdown distillation artifacts, and only after review synthesize one master skill plus reusable subskills.
---

# Ditto Skill

1. If the user provides a GitHub URL, identify the target repo and ask for clone confirmation before running any clone command.
2. If the user does not provide a GitHub URL, default to the current local git repository.
3. Run `scripts/distill_repo.py --mode scan` or `--mode analyze` before discussing skill generation.
4. Ask the user to review `distill-report.md` before synthesis.
5. Use `reviewed-milestones.json` as the synthesis gate. If it is missing, stop and finish the review step first.
6. Use `scripts/distill_repo.py --mode synthesize` after confirmation, or `--mode full` only when the user explicitly wants one-shot execution.

## References

- Read `references/artifact-schema.md` for exact artifact files.
- Read `references/milestone-rubric.md` when milestone selection is ambiguous.
- Read `references/profile-general.md`, `references/profile-web-saas.md`, or `references/profile-ai-agent.md` depending on the chosen profile.
- Read `references/skill-package-template.md` before editing generated master-skill and subskills.
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/artifact-schema.md
# Artifact Schema

- `repo-summary.json`: repo root, profile, manifests, top-level dirs, commit count
- `milestone-candidates.json`: heuristic commit candidates with scores and reasons
- `milestone-review-prompt.md`: prompt used for the review phase
- `reviewed-milestones.json`: decisions created after the review phase and required for synthesis
- `architecture-evolution.json`: structure-focused summary
- `stack-evolution.json`: stack/profile summary
- `pitfall-summary.json`: fixes, reverts, and likely pitfalls
- `distill-report.md`: human review document written before synthesis
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/milestone-rubric.md
# Milestone Rubric

Keep commits that introduce a durable capability, reshape boundaries, add lasting quality controls, or expose a pitfall that future projects should avoid.

Reject commits that are typo-only, docs-only, formatting-only, or too local to teach a reusable engineering lesson.
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/profile-general.md
# General Profile

Use the baseline heuristic signals: features, refactors, quality work, dependency introductions, directory reshaping, and meaningful fixes.
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/profile-web-saas.md
# Web SaaS Profile

Prioritize auth, schema evolution, migrations, billing hooks, deployment config, router boundaries, and testing layers.
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/profile-ai-agent.md
# AI Agent Profile

Prioritize tools, prompts, memory, eval hooks, model adapters, orchestration boundaries, and long-running workflow structure.
```

```markdown
# /Users/lhy/Project/Prompt/ditto-skill/references/skill-package-template.md
# Skill Package Template

- `master-skill/SKILL.md`: archetype, build order, architecture heuristics, quality rules, and pitfalls
- `subskills/bootstrap/SKILL.md`: how to start small
- `subskills/architecture-evolution/SKILL.md`: when and how to split boundaries
- `subskills/quality-hardening/SKILL.md`: when to add tests, linting, types, and CI
- `subskills/stack-specific/SKILL.md`: profile-specific stack patterns
- `subskills/pitfall-avoidance/SKILL.md`: repeated mistakes to avoid
```

- [ ] **Step 2: Generate `agents/openai.yaml` from the actual skill**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python /Users/lhy/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py /Users/lhy/Project/Prompt/ditto-skill --interface display_name="Ditto Skill" --interface short_description="Distill repo evolution into reusable skills" --interface default_prompt="Use $ditto-skill to analyze this repository's git history and synthesize reusable coding-agent skills."`
Expected: `/Users/lhy/Project/Prompt/ditto-skill/agents/openai.yaml` exists and contains those interface fields.

- [ ] **Step 3: Validate the root skill, then run end-to-end smoke checks**

Run: `/Users/lhy/Project/Prompt/ditto-skill/.venv/bin/python /Users/lhy/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/lhy/Project/Prompt/ditto-skill`
Expected: prints `Skill is valid!`

Run: `cd /Users/lhy/Project/Prompt/ditto-skill && .venv/bin/python scripts/distill_repo.py --mode analyze --profile general --repo /Users/lhy/Project/Prompt/ditto-skill`
Expected: rewrites `outputs/<slug>/analysis` with all agreed analysis artifacts.

Run: `python3 - <<'PY'
from pathlib import Path
import json

analysis_root = Path('/Users/lhy/Project/Prompt/ditto-skill/outputs/ditto-skill/analysis')
analysis_root.mkdir(parents=True, exist_ok=True)
reviewed = analysis_root / 'reviewed-milestones.json'
if not reviewed.exists():
    candidates = json.loads((analysis_root / 'milestone-candidates.json').read_text())
    reviewed.write_text(json.dumps([
        {'sha': row['sha'], 'message': row['message'], 'decision': 'keep', 'why': 'Smoke test keep'}
        for row in candidates[:3]
    ], indent=2))
PY`
Expected: `reviewed-milestones.json` exists for the smoke run.

Run: `cd /Users/lhy/Project/Prompt/ditto-skill && .venv/bin/python scripts/distill_repo.py --mode synthesize --repo /Users/lhy/Project/Prompt/ditto-skill`
Expected: creates `outputs/<slug>/skills/master-skill/SKILL.md` and all five expected subskills.

- [ ] **Step 4: Commit the skill package and docs**

```bash
git -C /Users/lhy/Project/Prompt/ditto-skill add SKILL.md references/artifact-schema.md references/milestone-rubric.md references/profile-general.md references/profile-web-saas.md references/profile-ai-agent.md references/skill-package-template.md agents/openai.yaml
git -C /Users/lhy/Project/Prompt/ditto-skill commit -m "feat: add ditto skill package and references"
```

## Self-Review Checklist

- Spec coverage: Task 2 covers both entry rules, Task 3 covers profile-aware commit selection, Task 4 covers the milestone-review layer, Task 5 writes the full agreed artifact set, Task 6 synthesizes the master skill plus five subskills, and Task 7 encodes the user-facing workflow in the root skill.
- Placeholder scan: Search the saved plan for unfinished markers and confirm that only deliberate prose remains.
- Type consistency: Keep `RepoSource`, `RepoProfile`, `CommitRecord`, `MilestoneCandidate`, `run_analysis()`, and `synthesize_skill_package()` signatures exactly as written above across every task.
