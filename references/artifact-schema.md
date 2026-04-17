# Artifact Schema

- `repo-summary.json`: repo root, selected profile, manifests, top-level directories, commit count
- `milestone-candidates.json`: heuristic milestone candidates with scores and reasons
- `milestone-review-prompt.md`: prompt-like review packet for milestone confirmation
- `reviewed-milestones.json`: explicit review decisions used by synthesis, or auto-generated during `full`
- `architecture-evolution.json`: summary of structural changes and notable commits
- `stack-evolution.json`: profile-aware stack summary
- `pitfall-summary.json`: fixes, refactors, and regression-like signals worth carrying into pitfall guidance
- `distill-report.md`: human-readable checkpoint written before normal synthesis
