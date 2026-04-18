# Artifact Schema

在需要解释输出目录、检查某一步是否完成、或决定下一步该调用哪个脚本时读取本文件。

## Analysis Layer

- `repo-summary.json`
  清洗后的仓库画像。

- `commit-evidence.json`
  高信号提交的结构化证据。

- `milestone-candidates.json`
  进入 review 阶段的候选里程碑。

- `milestone-review-packet.md`
  assistant 审核时必须阅读的 packet。

- `reviewed-milestones.md`
  assistant 填写的强模板草稿。
  每个 `## Milestone` block 必须包含：
  - `sha`
  - `message`
  - `decision`
  - `phase`
  - `capability`
  - `constraint_or_tradeoff`
  - `why`
  - `evidence_refs`

- `reviewed-milestones.json`
  由 `scripts/compile_review.py` 从 `reviewed-milestones.md` 编译得到。

- `architecture-evolution.json`
  结构与边界变化总结。

- `stack-evolution.json`
  技术栈引入顺序与依赖事件总结。

- `pitfall-summary.json`
  fix / revert / hotfix 暴露出的 guardrails。

- `distill-report.md`
  给用户看的分析摘要。

- `distilled-insights.md`
  assistant 填写的强模板草稿。
  必须包含这些顶级 section：
  - `## Project Archetype`
  - `## Build Phases`
  - `## Default Build Order`
  - `## Architecture Rules`
  - `## Stack Patterns`
  - `## Quality Rules`
  - `## Pitfall Guardrails`
  - `## Subskill Mapping`
  - `## Evidence Refs`

- `distilled-insights.json`
  由 `scripts/compile_insights.py` 从 `distilled-insights.md` 编译得到。

## Compile Steps

- `scripts/compile_review.py`
  输入：`reviewed-milestones.md`
  输出：`reviewed-milestones.json`
  规则：缺字段、非法 phase、非法 decision 都要直接报错。

- `scripts/compile_insights.py`
  输入：`distilled-insights.md`
  输出：`distilled-insights.json`
  规则：缺 section、非法 phase、非法 subskill slug 都要直接报错。

## Skills Layer

标准输出目录：

```text
outputs/<repo-slug>/
  analysis/
  skills/
```

- `skills/master-skill/SKILL.md`
  保存整体工程风格与推荐 build order。

- `skills/subskills/*/SKILL.md`
  保存可复用的局部能力，必须是行动手册格式。

## Assistant Rule

向用户汇报时，优先引用：

1. `distill-report.md`
2. `milestone-review-packet.md`
3. `reviewed-milestones.md`
4. `distilled-insights.md`

只有当两个 Markdown 草稿都已经编译成 JSON 后，才算可以进入 synthesis。
