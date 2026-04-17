# AI Agent Profile

当仓库明显在做 agent、tool use、workflow orchestration、prompt pipeline 或 eval 系统时读取本文件。

## Priority Signals

优先关注：

- prompts and prompt orchestration
- tools and tool adapters
- memory surfaces
- evaluation hooks
- model interfaces
- workflow boundaries for long-running or multi-step agents

## What Usually Matters

这类仓库真正值得蒸馏的，通常包括：

- prompt 是如何从单次调用演进为有结构的流程
- tools 是何时被抽象成统一接口的
- memory / state 是怎样进入系统的
- eval 是后补的，还是从早期就有
- multi-step workflow 是什么时候从线性脚本变成有边界的模块

## Common AI Agent Pitfalls

重点观察：

- prompt 与代码逻辑强耦合，后期难维护
- tool adapter 不统一，导致 agent 能力扩展困难
- memory / eval 只是临时补丁，无法形成稳定机制
- workflow 过长但没有清晰阶段边界

## Reporting Guidance

对用户汇报时，优先提炼：

1. orchestration 是如何演化的
2. tools / memory / eval 三条主线
3. 哪些提交最能体现“从 demo 到 system”的变化
