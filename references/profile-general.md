# General Profile

当仓库类型不明显，或用户没有指定更强的 profile 时读取本文件。

## What To Look For

优先观察这些通用信号：

- features
- refactors
- test and perf work
- dependency introductions
- directory reshaping
- meaningful fixes and regressions

## Questions To Answer

分析时重点回答：

1. 仓库是先做出最小可运行版本，还是一开始就搭了完整骨架？
2. 什么时候开始出现结构化目录或模块边界？
3. 质量机制是早期引入，还是后期补齐？
4. 有没有反复出现的修复模式？

## Reporting Guidance

如果 profile 仍不明确：

- 继续使用 `general`
- 不要强行归类
- 在汇报里明确写“当前按 general profile 处理”
