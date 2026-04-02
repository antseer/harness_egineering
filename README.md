# Harness Engineering

> **Agent = Model + Harness** — 改进 Harness 的 ROI 通常远高于换更大的模型

Harness Engineering 是一个新兴的 AI/LLM 工程学科，研究如何为 AI Agent 构建生产级的"缰绳层"——包括工具编排、约束护栏、反馈循环、可观测性等模型之外的一切基础设施。

本仓库是该学科的**研究与实践文档集合**，包含学术综述、实践指南和 Claude Code 落地手册。

## 核心观点

```
性能提升来源：
  Prompt Engineering   →  5-15%
  Context Engineering  → 15-30%
  Harness Engineering  → 50-80%   ← 最大杠杆点
```

| 阶段 | 聚焦 | 代表概念 |
|------|------|---------|
| 2023-2024 | Prompt Engineering | 为单次查询写好提示词 |
| 2025 | Context Engineering | 动态组织正确的上下文信息 |
| 2026 | **Harness Engineering** | 构建环境、约束和反馈循环 |

## 仓库内容

### 研究报告

| 文件 | 说明 |
|------|------|
| [harness_engineering_research_report.md](harness_engineering_research_report.md) | 57 篇论文的跨领域学术综述（英文） |
| [harness_engineering_research_report_zh.md](harness_engineering_research_report_zh.md) | 上述报告的中文翻译 |
| [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md) | 90+ 来源的实践导向研究发现（英文） |
| [RESEARCH_FINDINGS_zh.md](RESEARCH_FINDINGS_zh.md) | 上述发现的中文翻译 |

### 实践指南

| 文件 | 说明 |
|------|------|
| [HARNESS_ENGINEERING_实践指南.md](HARNESS_ENGINEERING_实践指南.md) | 从零构建 Harness 的 7 周实施路线图，含代码示例 |
| [CLAUDE_CODE_HARNESS_实践指南.md](CLAUDE_CODE_HARNESS_实践指南.md) | 面向 Claude Code 用户的 Harness 落地手册 |
| [HARNESS_SKILLS_使用指南.md](HARNESS_SKILLS_使用指南.md) | Harness Skills 安装与使用指南 |

### 示例项目

| 目录 | 说明 |
|------|------|
| [harness_practice_demo/](harness_practice_demo/) | Harness 实践演示项目（含 CLAUDE.md、测试、计划文件） |

### 其他

- `install-skills.sh` — Harness Skills 全局安装脚本
- `SESSION_*.md` — 研究会话记录
- `memory_export/` — 项目记忆导出

## Harness 五层架构

```
┌─────────────────────────────────────────────────┐
│ Layer 5: 长时间跨度模式 (Long-Horizon Patterns)    │
│   跨 session 记忆、自我反思、渐进式任务分解           │
├─────────────────────────────────────────────────┤
│ Layer 4: 智能增强 (Intelligence Enhancement)       │
│   System Prompt、CoT、Self-critique、Memory        │
├─────────────────────────────────────────────────┤
│ Layer 3: 上下文管理 (Context Management)           │
│   压缩策略、工具输出裁剪、渐进式信息披露              │
├─────────────────────────────────────────────────┤
│ Layer 2: 执行能力 (Execution Capabilities)         │
│   工具定义、沙箱执行、Action Space 设计             │
├─────────────────────────────────────────────────┤
│ Layer 1: 存储与状态 (Storage & State)              │
│   文件系统、Git、检查点、轨迹日志                    │
└─────────────────────────────────────────────────┘
```

## 关键参考来源

- **Anthropic** — GAN-Inspired Generator-Evaluator 三智能体架构
- **OpenAI** — 《Harness engineering: leveraging Codex in an agent-first world》(2026)
- **Mitchell Hashimoto** — Harness 概念的早期提出者
- **Andrej Karpathy** — Context Engineering 概念的推广者

## 快速开始

本仓库为纯文档项目，无需安装依赖。直接阅读上方指南即可。

如需安装 Harness Skills 到 Claude Code：

```bash
./install-skills.sh
```

## License

Research and documentation repository. All content is for educational and reference purposes.
