---
name: ditto-skill
description: Distill a software repository's git evolution and current structure into reusable coding-agent skills. Use when Codex needs to analyze a local git repo or a GitHub repo, produce JSON and Markdown distillation artifacts, and only after review synthesize one master skill plus reusable subskills. If the user explicitly asks for one-shot execution, use full mode to analyze and generate in a single run.
---

# Ditto Skill

1. If the user provides a GitHub URL, identify the target repo and ask for clone confirmation before running any clone command.
2. If the user does not provide a GitHub URL, default to the current local git repository.
3. Run `scripts/distill_repo.py --mode scan` or `scripts/distill_repo.py --mode analyze` before discussing skill generation.
4. Ask the user to review `distill-report.md` before synthesis in the normal flow.
5. Use `scripts/distill_repo.py --mode synthesize` after analysis when the user wants skill generation from saved artifacts.
6. Use `scripts/distill_repo.py --mode full` only when the user explicitly wants one-shot analysis plus generation.

## References

- Read `references/artifact-schema.md` for the exact analysis artifact contract.
- Read `references/milestone-rubric.md` when milestone selection is ambiguous.
- Read `references/profile-general.md`, `references/profile-web-saas.md`, or `references/profile-ai-agent.md` depending on the chosen profile.
- Read `references/skill-package-template.md` before editing generated master-skill and subskills.
