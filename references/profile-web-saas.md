# Web SaaS Profile

当仓库明显是 Web app、SaaS、dashboard、后台系统或全栈产品时读取本文件。

## Priority Signals

优先关注：

- auth flows
- schema evolution and migrations
- billing-related integrations
- deployment and CI config
- router and boundary changes
- testing layers around product-critical flows

## What Usually Matters

在这类仓库里，更值得蒸馏的通常不是单个页面代码，而是：

- 登录和会话是何时引入的
- schema / migration 是怎样从无到有建立起来的
- server/client 或 route/module 边界是何时清晰化的
- 部署、环境变量、CI 是何时补齐的
- 哪些关键业务流后来被测试覆盖

## Common Web SaaS Pitfalls

生成总结时，优先留意：

- auth redirect / session 失效
- schema 改动与应用代码不同步
- 配置、环境变量、部署脚本分散失控
- 页面代码和服务端逻辑混在一起导致后期重构

## Reporting Guidance

对用户汇报时，如果仓库匹配本 profile，优先给出：

1. 技术栈引入顺序
2. auth / data / deployment 三条主线
3. 哪些提交最能体现“工程成熟度上升”
