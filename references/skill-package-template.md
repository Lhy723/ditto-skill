# Skill Package Template

在填写 `distilled-insights.md`，或检查 synthesized skill 是否还是“行动手册”而不是“提交列表”时读取本文件。

## Draft Structure

`distilled-insights.md` 必须使用固定 section：

- `## Project Archetype`
- `## Build Phases`
- `## Default Build Order`
- `## Architecture Rules`
- `## Stack Patterns`
- `## Quality Rules`
- `## Pitfall Guardrails`
- `## Subskill Mapping`
- `## Evidence Refs`

其中：

- `## Build Phases`
  每个 phase 用 `### Phase`
- `## Default Build Order`
  每个步骤用 `### Step`
- `## Subskill Mapping`
  每个 subskill 用 `### Subskill`

## Required Fields

### Project Archetype

- `summary`
- `profile`
- `manifests`
- `top_level_dirs`

### Phase

- `phase`
- `when`
- `why`
- `actions`
- `evidence_refs`

### Step

- `phase`
- `recommendation`
- `why`

### Subskill

- `slug`
- `when_to_use`
- `what_to_do`
- `what_to_avoid`
- `signals_to_watch`
- `evidence_refs`

## Writing Rule

生成 future rules 时：

- 主体写动作，不写提交回放
- 先写 build order，再写 heuristics
- commit 只允许在 `Evidence` 相关字段里出现
- `subskill_mapping` 也必须是行动手册，不是摘要笔记

## Forbidden Output Shape

如果草稿或最终 skill 出现这些问题，就继续改：

- 主体是 commit 列表
- 只有总结，没有动作
- 只有动作，没有 evidence refs
- 看完后 future assistant 仍然不知道先做什么、后做什么
