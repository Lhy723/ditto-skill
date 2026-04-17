---
name: ditto-skill
description: Distill a software repository's git evolution and current structure into reusable coding-agent skills. Use when Claude Code, Codex, OpenClaw, or another coding assistant needs to analyze the current repo or a GitHub repo, summarize the findings, and optionally synthesize a master skill plus subskills. Default to analysis first; use one-shot distillation only when the user explicitly asks for it.
---

# Ditto Skill

Treat this as an assistant workflow, not a manual CLI workflow.

1. If the user provides a GitHub URL, confirm the target repo before cloning.
2. If the user does not provide a GitHub URL, default to the current local git repository.
3. For normal use, call `scripts/analyze_repo.py` first.
4. Report a concise analysis summary and point to the generated `analysis/` artifact path.
5. Ask the user whether to continue into skill synthesis.
6. If the user confirms, call `scripts/review_milestones.py` if review decisions do not already exist, then call `scripts/synthesize_skill.py`.
7. If the user explicitly asks for one-shot execution, call `scripts/full_distill.py`.

## References

- Read `references/artifact-schema.md` for the output contract.
- Read `references/milestone-rubric.md` when milestone selection is ambiguous.
- Read `references/profile-general.md`, `references/profile-web-saas.md`, or `references/profile-ai-agent.md` depending on the chosen profile.
- Read `references/skill-package-template.md` before editing generated skills.
