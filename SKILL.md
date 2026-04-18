---
name: ditto-skill
description: Distill a software repository's git evolution into reusable coding-agent skills. Use when Claude Code, Codex, OpenClaw, or another coding assistant needs to analyze a local repo or GitHub repo, review the evidence, draft the distilled conclusions, compile them into structured artifacts, and synthesize a master skill plus subskills.
---

# Ditto Skill

Treat this as an assistant workflow, not a manual CLI workflow.

## Default Workflow

1. If the user provides a GitHub URL, confirm the target repo before cloning.
2. If the user does not provide a GitHub URL, default to the current local git repository.
3. Call `scripts/analyze_repo.py`.
4. Read the generated evidence artifacts, not just `distill-report.md`.
   Focus on:
   - `repo-summary.json`
   - `commit-evidence.json`
   - `milestone-candidates.json`
   - `architecture-evolution.json`
   - `stack-evolution.json`
   - `pitfall-summary.json`
5. Report a concise analysis summary to the user:
   - what kind of repo this is
   - the likely build order
   - the strongest architecture/stack/pitfall signals
   - the `analysis/` artifact path
6. If the user wants synthesis, call `scripts/review_milestones.py`.
   This generates:
   - `milestone-review-packet.md`
   - `reviewed-milestones.md` (assistant draft template)
7. Read `milestone-review-packet.md` and `references/milestone-rubric.md`, then fill `reviewed-milestones.md`.
8. Call `scripts/compile_review.py` to turn `reviewed-milestones.md` into `reviewed-milestones.json`.
9. Call `scripts/prepare_insights_draft.py` to generate `distilled-insights.md`.
10. Read `references/skill-package-template.md`, then fill `distilled-insights.md`.
11. Call `scripts/compile_insights.py` to turn `distilled-insights.md` into `distilled-insights.json`.
12. Call `scripts/synthesize_skill.py` only after both compiled JSON files exist.

## One-shot Workflow

If the user explicitly asks for one-shot execution, call `scripts/full_distill.py`.

In one-shot mode:

- the script only prepares analysis artifacts and assistant draft templates
- you still must read the packet, complete the drafts, compile them, and then synthesize
- do not rely on any script-generated fallback summary

## Assistant Rules

- Do not summarize the repo as a list of commits.
- Do not treat `reviewed-milestones.md` or `reviewed-milestones.json` as the final output.
- Always turn repository history into future assistant actions.
- Write the drafts using the exact template headings and field names.
- Compile drafts into JSON before synthesis; do not hand-edit the JSON directly unless the user explicitly asks.
- When presenting synthesized skills, prioritize action rules over historical narration.

## References

- Read `references/artifact-schema.md` for the output contract.
- Read `references/milestone-rubric.md` when milestone selection or phase assignment is ambiguous.
- Read `references/profile-general.md`, `references/profile-web-saas.md`, or `references/profile-ai-agent.md` depending on the chosen profile.
- Read `references/skill-package-template.md` before filling `distilled-insights.md` and before checking synthesized skills.
