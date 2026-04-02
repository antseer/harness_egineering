---
name: harness-plan
description: Use when starting a large task that will span multiple sessions - creates a named plan file (plan-{name}.md) with phased breakdown, decision log, and session handoff structure for cross-session relay. Supports multiple parallel plans in the same project.
argument-hint: "[plan-name] [task description, e.g. auth 实现用户认证系统]"
---

# Harness Plan — 大任务分阶段规划

## Overview

将大任务拆分为多个 Phase，生成 `plan-{name}.md` 作为跨会话接力的"接力棒"。**支持同一目录下多个 Plan 并行推进。**

**核心原则**：一个 Phase 一个会话，每个会话的 Claude 都是"干净的大脑 + 完整的地图"。上下文重置优于上下文压缩。

**飞轮定位**：本 Skill 消费 CLAUDE.md（了解架构）和 `.harness/review-log.md`（避免重蹈覆辙），产出 plan-{name}.md 供 harness-resume 消费。

**Announce at start:** "正在使用 harness-plan 技能为任务制定跨会话执行计划。"

## Plan 命名规则

**`$ARGUMENTS` 解析**：第一个词作为 plan name，其余为任务描述。

- `/harness-plan auth 实现用户认证系统` → name=`auth`，文件=`plan-auth.md`
- `/harness-plan payments 接入 Stripe 支付` → name=`payments`，文件=`plan-payments.md`
- `/harness-plan 实现用户认证系统`（未提供 name）→ 从任务描述自动生成短 name（如 `user-auth`），文件=`plan-user-auth.md`

**命名约束**：name 只允许小写字母、数字、连字符，长度 ≤ 20 字符。

**向后兼容**：如果项目根目录已存在旧的 `plan.md`（无 name 后缀），在汇报时提示用户该文件存在，建议迁移为 `plan-{name}.md` 格式。

## 执行流程

### Step 1：收集上下文

1. 解析 `$ARGUMENTS`，提取 plan name 和任务描述
2. 检查 `plan-{name}.md` 是否已存在——如果存在，**警告用户**并询问是覆盖还是换名
3. 读取 `CLAUDE.md`（如果存在）理解项目架构和禁令
4. 读取 `.harness/config.json`（如果存在）获取技术栈和命令信息
5. 读取 `.harness/review-log.md`（如果存在）——**关键**：了解历史失败模式，在规划时主动规避
6. 读取 `.harness/phase-journal.jsonl`（如果存在）——**只统计 `"plan"` 字段匹配当前 name 的条目**，用于校准本次 Phase 粒度。如无匹配条目，统计全部历史条目作为参考
7. 探索相关代码，理解当前状态
8. 如果任务描述不够清晰，向用户提问以澄清范围

### Step 2：拆分 Phase

**拆分原则**：
- 每个 Phase 可在一个会话中完成（30-60分钟的工作量）
- Phase 之间有明确的交付物和验证标准
- 每个 Phase 结束时代码处于可运行状态（不要留半成品）
- Phase 顺序遵循依赖关系（先基础后上层）

**Phase 粒度参考**：
- 数据模型 + 迁移 = 1个 Phase
- 一个完整的 API 功能（实现 + 测试）= 1个 Phase
- 集成测试 + 收尾 = 1个 Phase

**设计决策点**：
- 对于涉及 API 设计的 Phase，列出关键决策点（如请求格式、错误码、认证方式），标注推荐方案
- 预估每个 Phase 的文件变更数量，帮助用户评估工作量

**基于历史 review 的规避**：
- 如果 review-log.md 中记录了某类反复出现的问题，在相关 Phase 的步骤中**显式标注警告**
- 例如 review-log.md 说"Claude 经常忘记更新测试"，则在每个 Phase 中加醒目的步骤：`⚠️ 同步更新对应测试文件`

### Step 3：生成 plan-{name}.md

**保存位置**：项目根目录 `plan-{name}.md`

**严格使用以下格式**：

```markdown
# 计划：[任务名称]

> **Plan ID**: {name}
> 执行方式：每个 Phase 开一个新会话，输入 `/harness-resume {name}` 即可自动接力。
> 每个 Phase 结束时会自动更新进度、记录决策、触发轻量级 review。

**目标**：[一句话描述]
**技术方案**：[2-3句概述]
**预估 Phase 数**：[N]

### 历史教训（来自 .harness/review-log.md）
- [如果有，列出与本任务相关的历史失败模式和对策]
- [如果没有，写"暂无历史数据"]

---

## Phase 1: [名称] [状态: 待做]

### 任务
- [ ] 具体步骤 1（含文件路径）
- [ ] 具体步骤 2
- [ ] 编写对应测试
- [ ] 验证：运行 [具体命令] 确认通过

### 关键决策
- [决策点1]：推荐方案 A，原因 ...
- [决策点2]：推荐方案 B，原因 ...

### 交付物
- [列出本 Phase 完成后应该存在的文件/功能]

### 验证标准
- [具体的验证命令和期望结果]

---

## Phase 2: [名称] [状态: 待做]
...

---

## 决策记录
（执行过程中积累，格式：决策内容 — 原因 — 日期）

## 已知问题
（执行过程中积累）

## 文件变更清单
（执行过程中积累）
```

### Step 4：向用户汇报

1. 展示生成的计划概要（不要展示全文——用户可以自己读 plan-{name}.md）
2. 列出当前目录下所有活跃的 plan 文件（`plan-*.md`），让用户了解并行状态
3. 如果纳入了历史教训，明确告知用户
4. 提示下一步操作：

```
计划已写入 plan-{name}.md（共 [N] 个 Phase）。

当前活跃计划：
  • plan-{name}.md — [本次任务] (新建)
  • plan-xxx.md — [其他任务] (Phase 2/4)
  ...

执行方式：
  • 当前会话执行：告诉我"执行 Phase 1"
  • 新会话执行（推荐）：输入 /harness-resume {name}

提示：每个 Phase 完成后会自动更新 plan-{name}.md 并记录执行数据。
```

## 注意事项

- plan 文件只写在项目根目录，不要放在子目录
- 文件名格式固定为 `plan-{name}.md`，不允许使用 `plan.md`（无 name 后缀）
- 每个 Phase 的步骤要具体到文件路径，不要写模糊的描述
- 验证标准必须是可执行的命令，不要写"确保正常工作"这种话
- 如果任务太小（预估 <30 分钟），告诉用户不需要 plan，直接做
- 用中文输出
