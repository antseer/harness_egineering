---
name: harness-init
description: Use when starting a new project or entering a project without CLAUDE.md - analyzes the codebase and generates CLAUDE.md with architecture rules, common commands, and Hook configuration for automated guardrails
argument-hint: "[language/framework hint, e.g. python-fastapi, ts-nextjs]"
---

# Harness Init — 为项目初始化 Harness 基础设施

## Overview

分析当前项目，一次性生成 Harness 的三个核心组件：**CLAUDE.md**（导航地图）、**Hooks 配置**（自动化护栏）、**`.harness/` 目录**（飞轮数据中心）。

**核心原则**：`Agent = Model + Harness`。Model 你无法改变，但 Harness（CLAUDE.md + Hooks + .harness/）是你能优化的全部。

**飞轮定位**：本 Skill 是飞轮的**起点**。它产出的 CLAUDE.md 会被 harness-plan/resume 消费，也会被 harness-review 持续改进。

**Announce at start:** "正在使用 harness-init 技能为项目初始化 Harness 基础设施。"

## 执行流程

### Step 1：项目探索（不修改任何文件）

1. 读取项目根目录，识别技术栈：
   - 查看 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`pom.xml` 等
   - 查看目录结构，理解分层架构
   - 查看已有的 README.md、.cursorrules、.github/copilot-instructions.md
   - 查看已有的 CLAUDE.md（如果存在则进入更新模式）
   - 检查是否有 `.gitignore`，如果没有则根据技术栈建议创建
   - 用户提供的参数 `$ARGUMENTS` 作为技术栈提示

2. 识别关键信息：
   - 项目语言和框架
   - 目录结构和分层架构
   - 构建/测试/lint 命令
   - 可用的 linter 和测试框架
   - 明显的架构规则（如分层依赖关系）

3. 检查是否已有 `.harness/` 目录和历史 review 数据：
   - 如果有 `.harness/review-log.md`，读取历史改进建议，在生成 CLAUDE.md 时纳入考虑
   - 如果有 `.harness/phase-journal.jsonl`，读取历史执行数据

### Step 2：生成 CLAUDE.md

**严格遵守以下原则**：

- **100行以内**——是"地图"不是"百科全书"
- **写禁止规则而非建议**——"禁止 X" 而不是 "尽量避免 X"
- **写常用命令**——让 Claude 能直接跑测试验证修改
- **写文件对应关系**——"改 X 必须同步改 Y"
- **不要编造信息**——只写你从项目中实际发现的内容
- **不要写通用开发实践**——不要写 "编写单元测试"、"提供有意义的错误信息" 这种废话
- **如果有历史 review 数据**——将反复出现的问题直接写成禁令

**CLAUDE.md 结构**：

```markdown
# CLAUDE.md

## 项目结构
（只列核心目录和职责，不超过10行）

## 常用命令
（构建、测试、lint、启动开发服务器——只列实际可用的命令）

## 架构规则（必须遵守）
（分层依赖规则、数据流方向、API 约定等——用"禁止"语气）

## 文件对应关系
（改 X 时必须同步改 Y）

## 禁止事项
（从项目结构推断出的危险操作）
```

**如果已存在 CLAUDE.md**：
- 读取现有内容
- 识别缺少的部分（常用命令？架构禁令？文件对应关系？）
- 向用户建议具体的改进点，不要直接覆盖

### Step 3：初始化 .harness/ 目录

创建飞轮数据中心：

```
.harness/
├── config.json          ← Harness 元信息（技术栈、lint/test 命令）
├── review-log.md        ← 累积的改进日志（harness-review 写入）
└── phase-journal.jsonl  ← Phase 执行日志（harness-resume 写入）
```

**config.json 格式**：

```json
{
  "tech_stack": "python-fastapi",
  "lint_cmd": "ruff check",
  "test_cmd": "pytest tests/ -x --tb=short",
  "created_at": "2026-03-30",
  "harness_version": 1
}
```

这个文件让其他 Skill 能自动识别项目的 lint/test 命令，无需每次重新探索。

### Step 4：生成 Hook 配置建议

根据识别的技术栈，生成对应的 Hook 配置。

**技术栈与 Hook 映射**：

| 技术栈 | Lint Hook | Test Hook |
|--------|-----------|-----------|
| Python (ruff) | `ruff check $CLAUDE_FILE_PATH` | `pytest tests/ -x --tb=short` |
| Python (flake8) | `flake8 $CLAUDE_FILE_PATH` | `pytest tests/ -x --tb=short` |
| TypeScript (eslint) | `npx eslint --quiet $CLAUDE_FILE_PATH` | `npx jest --bail --silent` |
| Go | `golangci-lint run $CLAUDE_FILE_PATH` | `go test ./... -count=1` |
| Rust | `cargo clippy -- -W warnings` | `cargo test` |

**输出格式**：生成可直接复制的 JSON 配置，并解释每个 Hook 的作用。

### Step 5：向用户汇报

以清晰的格式汇报：
1. 已生成/建议的 CLAUDE.md 内容（如果是新文件则直接创建，如果已有则展示 diff）
2. 已创建的 `.harness/` 目录结构
3. 推荐的 Hook 配置（展示 JSON，不自动写入——让用户决定）
4. 下一步建议：

```
Harness 基础设施已就绪：
  ✅ CLAUDE.md — 项目导航地图
  ✅ .harness/ — 飞轮数据中心
  📋 Hook 配置 — 请复制到 .claude/settings.json

飞轮已启动。接下来：
  • 有大任务要做？→ /harness-plan [任务描述]
  • 有正在进行的任务？→ /harness-resume
  • 想优化 Harness？→ /harness-review
```

## 注意事项

- 不要自动修改 `.claude/settings.json`——Hook 配置只展示，由用户手动添加
- 如果项目没有 linter 或测试框架，建议安装但不要自动安装
- 如果项目很小（<10个文件），CLAUDE.md 可以更简短（50行以内）
- 用中文输出所有说明和注释
