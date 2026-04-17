# Skill Package Template

在准备从 analysis 产物进入 synthesis，或者需要检查生成出的 skill 是否结构完整时读取本文件。

## Required Outputs

- `master-skill/SKILL.md`
  必须包含：
  - archetype
  - default build order
  - architecture heuristics
  - quality rules
  - pitfalls

- `subskills/bootstrap/SKILL.md`
  说明如何从最小可行骨架起步。

- `subskills/architecture-evolution/SKILL.md`
  说明何时、为何、如何拆边界。

- `subskills/quality-hardening/SKILL.md`
  说明何时补 tests、lint、types、CI。

- `subskills/stack-specific/SKILL.md`
  保存 profile-sensitive 的栈与模式总结。

- `subskills/pitfall-avoidance/SKILL.md`
  保存历史中真实出现过的错误、修复和反模式。

## Writing Rule

生成 skill 时，不要把 analysis 原文机械拷贝进去。应该把 analysis 转成：

- future assistant 能直接执行的指令
- 可以迁移到相似项目的经验
- 明确的先后顺序和判断标准

## Minimum Quality Check

如果一个生成出的 skill 不满足下列任一条件，就继续改：

1. future assistant 能从中看出先做什么后做什么
2. future assistant 能看出哪些模式值得复用
3. future assistant 能看出哪些坑需要主动规避
4. 内容不是仓库读书笔记，而是行动指令
