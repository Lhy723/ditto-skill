# Artifact Schema

在需要解释输出目录、检查某一步是否完成、或决定下一步该调用哪个脚本时读取本文件。

## Analysis Layer

- `repo-summary.json`
  用途：提供仓库的最小画像。
  关键字段：`root`、`profile`、`manifests`、`top_level_dirs`、`commit_count`
  读取时回答：这是个什么仓库、当前按哪个 profile 分析、仓库规模大概如何。

- `milestone-candidates.json`
  用途：保存启发式筛出的候选里程碑提交。
  关键字段：`sha`、`message`、`score`、`reasons`
  读取时回答：哪些提交值得进入 review 阶段、候选是因为什么被保留。

- `milestone-review-prompt.md`
  用途：给 assistant 或人工 review 使用的复判材料。
  读取时回答：当前候选提交应该如何被判断、review 的目标是什么。

- `reviewed-milestones.json`
  用途：保存 review 结论。
  关键字段：`sha`、`message`、`decision`、`why`
  读取时回答：哪些提交最终被保留、为什么保留。
  说明：正常 staged 流程里它来自 review；`full` 模式下允许自动生成 fallback。

- `architecture-evolution.json`
  用途：概括目录和边界变化。
  读取时回答：这个仓库是怎样从简单结构长成当前结构的。

- `stack-evolution.json`
  用途：概括技术栈和 profile 相关线索。
  读取时回答：仓库依赖了什么、哪些能力与技术栈选择有关。

- `pitfall-summary.json`
  用途：保存 fix、refactor、regression 一类的风险线索。
  读取时回答：后续生成 skill 时应该提醒 assistant 避开什么坑。

- `distill-report.md`
  用途：给用户看的分析摘要和下一步建议。
  读取时回答：现在应该向用户汇报什么、是否该询问是否继续生成 skill。

## Skills Layer

标准输出目录：

```text
outputs/<repo-slug>/
  analysis/
  skills/
```

- `skills/master-skill/SKILL.md`
  保存整体工程风格。

- `skills/subskills/*/SKILL.md`
  保存可复用的局部能力。

## Assistant Rule

向用户汇报时，优先引用：

1. `distill-report.md` 里的简洁结论
2. `analysis/` 目录路径
3. 当前是否已经具备 `reviewed-milestones.json`
4. 是否可以继续进入 synthesis
