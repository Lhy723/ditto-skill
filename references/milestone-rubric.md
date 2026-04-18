# Milestone Rubric

在填写 `reviewed-milestones.md` 时读取本文件。

## What To Keep

优先保留这些提交：

- 引入了持久能力
- 改变了架构或边界
- 引入了 tests / lint / types / CI / deployment checks
- 揭示了真实 pitfall
- 能清楚说明 future assistant 为什么应该模仿

## What To Drop

默认 drop 或明显降权：

- typo-only
- docs-only
- formatting-only
- 只改局部实现细节、没有迁移价值
- 只能说“改动挺大”，却说不出工程意义

## Required Fields In `reviewed-milestones.md`

每个 `## Milestone` block 必须填写：

- `sha`
- `message`
- `decision`
- `phase`
- `capability`
- `constraint_or_tradeoff`
- `why`
- `evidence_refs`

不要留 `TODO`，不要缺字段。

## Phase Rules

合法 phase 只有：

- `bootstrap`
- `expansion`
- `hardening`
- `refactor`
- `pitfall`

默认理解：

- `bootstrap`
  仓库最小骨架、manifest、首个可运行切片
- `expansion`
  新能力、新依赖、新模块
- `hardening`
  tests、lint、types、CI、deploy verification
- `refactor`
  目录重组、模块抽取、边界整理
- `pitfall`
  fix / revert / hotfix 暴露出的真实 guardrail

## Writing Rules

- `capability`
  写 future assistant 能复用的能力，不写“这个 commit 做了 X”
- `constraint_or_tradeoff`
  写这一步带来的工程取舍
- `why`
  写为什么保留或 drop
- `evidence_refs`
  只写结构化证据引用，例如 `commit-evidence.json#<sha>`

## Common Mistakes

- 不要把 review 写成 repo 历史笔记
- 不要把 commit message 原样重写成 `capability`
- 不要在没有证据时猜 phase
- 不要让 `why` 只剩“score 高，所以 keep”
