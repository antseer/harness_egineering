---
name: harness-resume
description: Use when resuming work on a multi-session task - reads plan.md, reports progress, identifies next phase, and continues execution with clean context
argument-hint: "[optional: specific phase to execute, e.g. Phase 3]"
---

# Harness Resume — 跨会话任务接力

## Overview

读取 plan.md，汇报当前进度，执行下一个 Phase，**完成后自动触发轻量级 review 并记录执行数据到飞轮**。

**核心原则**：每个新会话都是"干净的大脑 + 完整的地图"。不要靠记忆，靠 plan.md。

**飞轮定位**：这是飞轮的**执行引擎**。它消费 plan.md + CLAUDE.md，产出代码变更 + 执行日志（`.harness/phase-journal.jsonl`），并在每个 Phase 结束时自动执行轻量级 review，让飞轮持续转动而不依赖用户手动触发。

**Announce at start:** "正在使用 harness-resume 技能恢复跨会话任务。"

## 执行流程

### Step 1：读取状态

1. 读取 `plan.md`（如果不存在，告诉用户先用 `/harness-plan` 创建）
2. 读取 `CLAUDE.md`（如果存在）理解项目规则
3. 读取 `.harness/config.json`（如果存在）获取 lint/test 命令
4. 解析 plan.md 中的 checkbox 状态：
   - `[x]` = 已完成
   - `[ ]` = 待做
   - Phase 状态标记

### Step 2：汇报进度

以简洁格式向用户汇报：

```
📋 任务：[任务名称]
📊 进度：Phase [M]/[N] 已完成

✅ 已完成：
  - Phase 1: [名称] — 已完成
  - Phase 2: [名称] — 已完成

⏭️ 下一个：Phase [M+1]: [名称]

📝 决策记录：
  - [列出已有决策，防止本次会话推翻]

⚠️ 已知问题：
  - [列出上次遗留的问题]
```

### Step 3：确认并执行

1. 如果用户通过 `$ARGUMENTS` 指定了特定 Phase，执行该 Phase
2. 否则，提示用户确认执行下一个 Phase
3. 开始执行时，严格按 plan.md 中列出的步骤依次完成
4. 如果执行时发现步骤描述不够具体，可以在 plan.md 中细化当前步骤的描述，但不改变 Phase 整体范围
5. 每完成一个步骤，立即在 plan.md 中标记 `[x]`

### Step 4：Phase 结束 — 更新 plan.md

每个 Phase 执行完毕后，必须更新 plan.md：

1. **标记完成的步骤**：`[ ]` → `[x]`
2. **更新 Phase 状态**：`[状态: 待做]` → `[状态: 已完成]`
3. **记录决策**：本次做了什么重要决策，为什么
4. **记录问题**：遇到什么坑，怎么解决的（或未解决）
5. **更新文件变更清单**：本次改了哪些文件

### Step 5：Phase 结束 — 自动轻量级 Review（飞轮核心）

**这一步是飞轮持续转动的关键。不需要用户手动触发 /harness-review，每个 Phase 完成后自动执行。**

执行以下检查：

#### 5a. CLAUDE.md 漂移检查
- 本 Phase 新增了模块/文件/依赖吗？
- CLAUDE.md 的项目结构、架构规则、文件对应关系是否需要同步更新？
- 如果需要更新，**直接更新 CLAUDE.md**（不只是建议），并告知用户改了什么

#### 5b. 执行质量自检
回答以下问题（内部评估，不需要展示全部细节）：

| 检查项 | 评估 |
|--------|------|
| 本 Phase 重试了几次才通过测试？ | 0次=优秀，1-2次=正常，3+次=有问题 |
| 是否违反了 CLAUDE.md 中的禁令？ | 是/否 |
| 是否有步骤执行顺序与计划不一致？ | 是/否 |
| 是否遇到了计划中未预见的问题？ | 是/否 |

#### 5c. 写入飞轮日志

将执行数据追加到 `.harness/phase-journal.jsonl`（如果 .harness/ 目录不存在则创建）：

```json
{
  "phase": "Phase 1: 数据模型",
  "status": "completed",
  "date": "2026-03-30",
  "retries": 1,
  "files_changed": ["src/models/user.py", "tests/test_models.py"],
  "decisions": ["使用 bcrypt 而非 argon2"],
  "issues": ["发现 SQLAlchemy 版本需要升级"],
  "claude_md_updated": true,
  "quality_notes": "测试一次通过，CLAUDE.md 已同步更新项目结构"
}
```

#### 5d. 发现严重问题时升级为完整 Review

如果自检发现以下情况，**在交接提示中建议用户运行 `/harness-review`**：
- 重试 3 次以上
- 违反了 CLAUDE.md 禁令
- 遇到了计划中完全未预见的重大问题

### Step 6：交接提示

Phase 完成后，根据自检结果给出差异化提示：

**正常情况**：
```
✅ Phase [M+1] 已完成，plan.md 已更新。
📝 CLAUDE.md [已同步更新 / 无需更新]
📊 执行数据已记录到 .harness/phase-journal.jsonl

下一步：
  • 继续本会话：告诉我"继续"
  • 开新会话（推荐）：输入 /harness-resume
```

**发现问题时**：
```
✅ Phase [M+1] 已完成，但执行中发现问题：
  ⚠️ [问题描述，如"重试了4次才通过测试"]

建议：
  • 运行 /harness-review 进行深度分析
  • 或继续执行，问题已记录到飞轮日志
```

## 注意事项

- 严格遵守 plan.md 中的决策记录——不要推翻之前会话做过的决策，除非用户明确要求
- 如果发现 plan.md 中的步骤有问题（比如依赖缺失），先向用户说明再修改计划
- 验证标准中的命令必须实际执行，不能跳过
- Step 5 的轻量级 review 应简洁高效，不要变成完整的 harness-review
- 用中文输出
