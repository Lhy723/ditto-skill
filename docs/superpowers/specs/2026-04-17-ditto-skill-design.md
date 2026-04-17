# Ditto Skill Design

Date: 2026-04-17
Topic: `ditto-skill`
Status: Draft for user review

## Summary

`ditto-skill` is a repo distillation skill for coding agents. It learns from a software project's git evolution and current structure, then turns that engineering trajectory into reusable skills for future agent-driven project creation.

The core idea is not to copy a repository's final code shape. The goal is to extract how the repository improved over time: what was introduced first, what was reworked later, which architectural boundaries emerged, which quality practices were added, and which mistakes were corrected. That evolution is then distilled into one master skill and a set of optional subskills that a coding agent can reuse when building a similar project with different product requirements.

## Product Goal

Help a coding agent answer this question:

`How should I build a project like this repo, using its engineering taste and evolution logic rather than copying its code?`

`ditto-skill` should let a user:

1. Analyze a repository and understand its evolution.
2. Review structured distillation artifacts.
3. Confirm whether skills should be generated.
4. Generate one master skill and optional subskills from the analysis.

## User Experience

The default experience is two-stage:

1. Analyze first.
2. Generate skills only after user confirmation.

The system supports two entry points:

1. GitHub link
2. Local repository

### Input Rules

If the user provides a GitHub link:

1. Resolve and display the repository that will be cloned and analyzed.
2. Ask for confirmation before cloning.
3. Clone the repository into a local working copy.
4. Run all git-history and code-structure analysis against that local clone.

If the user does not provide a GitHub link:

1. Default to the current local repository.
2. If the current directory is not a git repository, ask for a repo path or GitHub link.

This preserves a simple user experience while keeping the actual analysis workflow consistent: all history inspection runs against a local git checkout.

### Typical Prompts

- `Use ditto-skill to analyze this repository.`
- `Use ditto-skill to analyze https://github.com/org/repo.`
- `Use ditto-skill to distill this repository into a skill.`
- `Based on the last analysis, generate the master skill only.`
- `Based on the last analysis, generate subskills for architecture and testing.`

## Skill Personality

`ditto-skill` should behave in two phases:

1. Research assistant phase
2. Engineering assistant phase

### Research Assistant Phase

The agent studies the repository's current structure and key historical changes. It identifies milestones, reconstructs the improvement path, and forms a grounded understanding of how the project became what it is.

This phase allows careful abstraction and judgment, but the abstractions should remain close to real code and real history.

### Engineering Assistant Phase

The agent converts its understanding into reusable outputs with stable structure and clear boundaries:

- structured JSON artifacts
- readable Markdown report
- one master skill
- optional subskills

The result should be useful to a future coding agent, not merely insightful to a human reader.

## Scope

V1 should be designed to work broadly, but it should be especially effective for:

1. Web and SaaS repositories
2. AI and agent repositories

The design should remain general enough to support other repository types later, but the initial heuristics, references, and examples should prioritize those two families.

## System Shape

V1 should use progressive loading through three components:

1. `SKILL.md`
2. `scripts/`
3. `references/`

### `SKILL.md`

The skill file should stay concise. It should define:

- triggering conditions
- operating modes
- workflow order
- output expectations
- when to read references
- when to run scripts

It should not try to hold every rubric, schema, or example directly in the main skill body.

### `scripts/`

Scripts should do the repeated, deterministic, and heavyweight work:

- collect git history
- extract commit diffs and snapshots
- summarize repository structure
- perform heuristic commit filtering
- produce structured JSON artifacts
- produce readable Markdown reports
- generate initial skill packages from prior artifacts

This also makes long-running analysis easier to package for stronger compute environments later.

### `references/`

References should hold:

- distillation rubrics
- artifact schemas
- output templates
- repository-type guidance
- examples of strong and weak milestone detection

This keeps the main skill small while preserving useful depth for harder tasks.

## Distillation Modes

V1 should expose four modes:

1. `scan`
2. `analyze`
3. `synthesize`
4. `full`

### `scan`

Quick repository scan. Produce a high-level repository profile and candidate milestone commits, but do not attempt full distillation.

### `analyze`

Perform a complete repository analysis and emit the intermediate artifacts. Do not generate skills unless the user explicitly asks or confirms.

### `synthesize`

Consume existing analysis artifacts and generate a master skill and optional subskills without recomputing the entire history analysis.

### `full`

Run the complete pipeline from repository intake through skill generation.

## Distillation Profiles

Profiles do not define the repository absolutely. They only change what the system pays more attention to during analysis.

Initial V1 profiles:

1. `general`
2. `web-saas`
3. `ai-agent`

Examples:

- `web-saas` should emphasize auth, schema evolution, deployment, billing, testing, and app structure.
- `ai-agent` should emphasize prompt orchestration, tools, memory, evaluation surfaces, model interfaces, and agent workflow boundaries.

## Core Pipeline

The distillation flow should be:

1. Repository intake
2. Repository profiling
3. Heuristic commit filtering
4. LLM milestone review
5. Evolution synthesis
6. Artifact generation
7. Skill generation after confirmation

### 1. Repository Intake

Collect:

- repository location
- branch and history availability
- top-level structure
- key manifests and config files
- basic commit timeline summary

### 2. Repository Profiling

Estimate:

- repository type
- major frameworks and dependencies
- likely architectural center of gravity
- history size and time span
- primary code directories

This stage gives the agent enough orientation to read history selectively.

### 3. Heuristic Commit Filtering

This stage reduces noise before deeper reasoning. It should favor commits that are more likely to reveal meaningful engineering evolution.

Likely high-value signals:

- `feat`
- `refactor`
- `perf`
- `test`
- important `fix`
- dependency introductions
- directory reshaping
- major config changes
- schema or migration changes
- deployment or CI changes
- reverts and regression-related commits

Likely low-value signals:

- typo-only changes
- docs-only changes
- mass formatting
- tiny isolated edits with no architectural meaning

The goal is not perfect classification. The goal is to shrink the search space.

### 4. LLM Milestone Review

The LLM reviews heuristic candidates and decides which ones are true milestones.

The model should consider:

- commit message
- diff content
- affected files
- repository context
- the commit's position in the broader timeline

Review questions:

- Did this commit introduce a meaningful new capability?
- Did this commit reshape boundaries or structure?
- Did this commit reveal a recurring engineering constraint?
- Did this commit represent a change future projects should imitate?
- Did this commit expose a pitfall that should become an explicit rule?

### 5. Evolution Synthesis

Convert milestone commits into a coherent repository narrative across a few durable dimensions:

- stack evolution
- architecture evolution
- quality evolution
- pitfall evolution

This should answer not just what changed, but how the repository matured.

### 6. Artifact Generation

Produce two intermediate outputs:

1. machine-readable JSON
2. human-readable Markdown

The artifacts should be stable enough to review and reuse without rerunning the entire analysis.

### 7. Skill Generation After Confirmation

After the user has reviewed the analysis, generate:

1. one master skill
2. optional subskills

Generation should be based on the intermediate artifacts rather than on raw repository history alone.

## Output Model

V1 should produce both `JSON` and `Markdown`.

### Why JSON

JSON supports:

- reproducible intermediate data
- downstream automation
- stable generation inputs
- later comparison across distillation runs

### Why Markdown

Markdown supports:

- human review
- easier editing
- quick repository understanding
- a pleasant checkpoint before skill generation

## Recommended Output Layout

```text
outputs/
  <repo-slug>/
    analysis/
      repo-summary.json
      milestone-commits.json
      architecture-evolution.json
      distill-report.md
    skills/
      master-skill/
      subskills/
```

This directory is a recommendation rather than a rigid contract, but the separation between `analysis/` and `skills/` should remain.

## Final Skill Products

The repository should be distilled into:

1. one master skill
2. zero or more subskills

### Master Skill

The master skill captures the repository's overall engineering taste and evolution logic.

It should include:

1. Project archetype
2. Default build order
3. Architecture heuristics
4. Preferred stack patterns
5. Quality rules
6. Pitfalls to avoid

The master skill should answer:

`If a coding agent wants to build a similar kind of project, how should it think and proceed?`

### Subskills

Subskills should only be created when they represent reusable capabilities with clear independent value.

Suggested V1 subskill families:

1. `bootstrap`
2. `architecture-evolution`
3. `quality-hardening`
4. `stack-specific`
5. `pitfall-avoidance`

Subskills should not be split mechanically by directory. They should be split by portability and reuse value.

## Intermediate Artifact Expectations

The analysis layer should preserve enough structure to support both review and later regeneration.

Recommended artifact categories:

1. repository summary
2. milestone commit set
3. architecture evolution summary
4. stack evolution summary
5. pitfall summary
6. distillation report

The exact filenames can evolve, but the information model should remain stable.

## V1 Success Criteria

V1 is successful if it can do the following reliably:

1. Provide a deeper understanding than reading the final codebase alone.
2. Reveal a plausible build order and evolution path.
3. Identify meaningful architectural and quality transitions.
4. Produce analysis artifacts that a user can review before synthesis.
5. Generate a reusable skill package that helps future coding agents build similar, but not identical, projects.

## Explicit Non-Goals

V1 should not attempt to do the following:

1. Reconstruct every detail of repository history.
2. Depend on GitHub APIs for all understanding.
3. Automatically produce perfect final skills with no review.
4. Optimize equally for every repository type from day one.
5. Become a heavy benchmarking or orchestration framework.

The project should stay lightweight and focused on high-value distillation.

## Design Principles

1. Analyze before generating.
2. Learn from evolution, not just the final state.
3. Favor reusable abstractions over repository-specific trivia.
4. Keep the skill concise and use progressive disclosure.
5. Preserve a reviewable intermediate layer.
6. Prefer a strong first draft over pretending to be fully automatic.

## Open Implementation Questions

These questions belong to the implementation plan rather than the design itself, but they should be tracked:

1. Which scripts should be mandatory in V1 and which can remain conceptual until usage proves demand?
2. What JSON schema is stable enough to support regeneration without creating early rigidity?
3. How should synthesized skills record or omit evidence links back to source commits?
4. How should GitHub clone destinations be chosen for repeated analysis sessions?
5. What is the minimum useful set of repository-type heuristics for `web-saas` and `ai-agent`?

## Project Definition

Chinese version:

`ditto-skill` 是一个面向编程 agent 的仓库蒸馏 skill。它通过学习软件项目的 git 演进历史与当前代码结构，提炼出可迁移的技术栈选择、架构演进路径、工程习惯与避坑经验，并将其整理为一个总 skill 与多个子 skills，供以后构建同类项目时复用。

English version:

`ditto-skill` is a repo distillation skill for coding agents. It learns from a software project's git evolution and current structure, then turns that engineering trajectory into one master skill and optional subskills for future project creation.
