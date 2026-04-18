# Ditto Skill 🧬

[English](./README.en.md)

<p align="center">
  <img src="assets/banner.png" alt="Ditto Skill banner" width="100%" />
</p>

<p align="center">
  <strong>Distill a software repository's git evolution into reusable skills for coding assistants.</strong><br>
  <em>让你的 AI 编程助手完美克隆任意代码仓库的演进基因。</em>
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://github.com/Lhy723/ditto-skill/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome" /></a>
</p>

## 🧬 什么是 Ditto Skill？

Ditto Skill 是专为 **Claude Code、Cursor、Codex** 等 AI 编程助手设计的“仓库蒸馏”技能包（Skill）。

就像宝可梦里的“百变怪（Ditto）”看一眼就能复制对方的技能一样，Ditto Skill 不仅能让 AI 看到一个优秀仓库**现在长什么样**，还能让 AI 深入 Git 历史，理解这个仓库是**如何一步步演进成现在这样的**。

它会提取目标仓库的：
- 📦 **技术栈引入顺序**（什么时候引入了什么库，解决了什么问题）
- 🏗️ **架构演进路径**（目录结构如何随着复杂度增加而重构）
- ✍️ **工程习惯与肌肉记忆**（命名规范、错误处理、状态管理模式）
- 🕳️ **真实踩坑与修复经验**（通过 `fix` 和 `revert` 提取避坑指南）

最终将这些宝贵经验蒸馏成后续可复用的 `Master Skill` 和 `Subskills`。

---

## 💡 为什么这件事重要？

目前大多数 AI 编程助手更容易看到“结果”，但缺乏“演进思维”。一个优秀开源仓库的真正价值，往往隐藏在它的演进轨迹里。

❌ **传统的 AI 编程（Snapshot 模式）：** 
从最终代码复制。AI 只能照猫画虎，不懂架构为什么这么设计，不懂哪些机制是后来打补丁加上的。

✅ **Ditto Skill 赋能（Evolution 模式）：** 
从仓库演进中蒸馏经验。当 Assistant 在做相似项目时，不再是生硬地照抄代码，而是**复用经过实践验证的工程路径**，像原作者一样思考。

---

## 🚀 如何使用

你不需要手动运行复杂的命令，只需在你的 AI 编程助手（如 Claude Code）中直接用自然语言唤醒它：

> **💬 你可以这样对 AI 助手说：**
> - *"用 ditto-skill 分析当前仓库，看看能提取出什么工程规范。"*
> - *"用 ditto-skill 分析这个 GitHub 仓库的演进历史。"*
> - *"基于刚才的分析结果，帮我生成一套 skill。"*
> - *"用 ditto-skill 一键蒸馏这个仓库，然后用提取出的技能帮我建一个新项目。"*

**默认工作流：**
1. 🔍 **深度分析**：AI 调用脚本分析仓库 Git 历史。
2. 📝 **审核草稿**：AI 基于 evidence packet 填写 `reviewed-milestones.md` 和 `distilled-insights.md` 草稿。
3. 🧬 **编译与合成**：脚本把草稿编译成结构化 JSON，再生成可复用的 Skill 文件。

---

## 它是怎么工作的？

Ditto Skill 采用 **Scripts-first (脚本优先)** 架构。执行层的脚本专为 Assistant 在 Skill Workflow 中稳定调用而设计，无需人类手动干预：

- `scripts/analyze_repo.py` —— 负责降噪并提取 Git 历史中的里程碑 Commit。
- `scripts/review_milestones.py` —— 负责生成 review packet 和 `reviewed-milestones.md` 草稿模板。
- `scripts/compile_review.py` —— 负责把 assistant 填好的 review 草稿编译成 JSON。
- `scripts/prepare_insights_draft.py` —— 负责生成 `distilled-insights.md` 草稿模板。
- `scripts/compile_insights.py` —— 负责把 insights 草稿编译成 JSON。
- `scripts/synthesize_skill.py` —— 负责将编译后的 insights 转化为高度结构化的 Skill Markdown。
- `scripts/full_distill.py` —— 一键准备分析与草稿环境，后续提炼仍由 assistant 完成。

---

## 仓库结构

```text
ditto-skill/
├── SKILL.md
├── README.md
├── README.en.md
├── LICENSE
├── agents/
│   └── openai.yaml                       # Skill 在 UI 中显示用的元数据
├── scripts/
│   ├── analyze_repo.py                   # 分析仓库结构与 Git 历史，产出 analysis artifacts
│   ├── review_milestones.py              # 生成 review packet 和 reviewed-milestones.md 草稿
│   ├── compile_review.py                 # 将 reviewed-milestones.md 编译成 JSON
│   ├── prepare_insights_draft.py         # 生成 distilled-insights.md 草稿
│   ├── compile_insights.py               # 将 distilled-insights.md 编译成 JSON
│   ├── synthesize_skill.py               # 基于编译后的 JSON 生成 master skill 和 subskills
│   ├── full_distill.py                   # 一键准备分析与草稿环境
│   └── common.py                         # 脚本共享的工具函数，如路径、JSON、git 调用封装
├── references/
│   ├── artifact-schema.md                # analysis 产物和 skill 产物的结构约定
│   ├── milestone-rubric.md               # 判断哪些 commit 值得保留为里程碑的标准
│   ├── profile-general.md                # 通用仓库的蒸馏关注点
│   ├── profile-web-saas.md               # Web SaaS 类型仓库的蒸馏关注点
│   ├── profile-ai-agent.md               # AI Agent 类型仓库的蒸馏关注点
│   └── skill-package-template.md         # 生成 master skill / subskills 时参考的模板
└── assets/
    └── banner.png
```

---

## Star History

<a href="https://www.star-history.com/?type=date&repos=Lhy723%2Fditto-skill">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=Lhy723/ditto-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=Lhy723/ditto-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=Lhy723/ditto-skill&type=date&legend=top-left" />
 </picture>
</a>

---

## License

本项目基于 [MIT License](./LICENSE) 开源。
