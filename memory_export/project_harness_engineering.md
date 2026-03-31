---
name: Harness Engineering 研究项目
description: 关于 Harness Engineering 研究与文档仓库的项目背景、核心发现和交付物，含 Claude Code Skill 飞轮架构
type: project
---

## 项目概述

这是一个 **研究与文档仓库**，专注于 Harness Engineering（框架工程）——一个新兴的 AI/LLM 工程学科（2026年）。仓库中没有可执行代码、测试或 CI/CD 流水线。

**核心论点**：`Agent = Model + Harness` —— 改进 Harness（工具、编排、护栏、反馈循环）的 ROI 通常高于更换更大的模型。

**演进路径**：Prompt Engineering (2023) → Context Engineering (2025) → Harness Engineering (2026)

## 已完成的工作

### 会话 1（2026-03-29）
1. 全网文献搜索 — 57+ 篇关键论文和 90+ 个实践来源
2. 概念解析 — 五层架构、五大支柱体系
3. 中英文双语报告
4. 通用实践指南（7周路线图）

### 会话 2（2026-03-30）
1. 实践指南 Phase 1-5 逐步解读（Claude Code 视角）
2. 生成 Claude Code 专用实践指南：`CLAUDE_CODE_HARNESS_实践指南.md`
3. 设计并创建 4 个 Claude Code Skill（harness-init/plan/resume/review）
4. Subagent 实战验证 → 发现并修复 5 个问题
5. 飞轮架构重设计 — 引入 `.harness/` 共享数据中心，Skill 自动联动
6. Skill 已部署到全局 `~/.claude/skills/`

## 三层飞轮模型

```
第一层：项目内 — 需求 → 执行 → 观察失败 → 改进 CLAUDE.md → 下次更好
第二层：跨项目 — 项目 A 经验 → Skill → 项目 B 起点更高
第三层：自举 — 用 Claude Code 写 Skill → Skill 让 Claude 更高效 → 写更好的 Skill
```

飞轮核心：harness-resume 每 Phase 完成后自动轻量 review + 写日志，不依赖用户手动触发。

## 核心发现

- OpenAI 用 Harness Engineering 交付了100万行代码零手写的产品
- Anthropic V2 Harness（Opus 4.6）在3.8小时/$125完成数字音频工作站
- LangChain Deep Agents 仅通过 Harness 优化从52.8%提升到66.5%
- 最小充分工具集（5-13个）优于100+工具
- 单 Agent + 好 Harness 通常优于复杂多 Agent 系统

**Why:** 用户正在系统性研究 Harness Engineering 并构建可复用的 Skill 工具链。
**How to apply:** 后续对话中涉及 AI Agent、Harness 优化、Skill 设计等话题时，基于这些成果提供建议。4 个全局 Skill 可在任何项目中通过 /harness-* 调用。
