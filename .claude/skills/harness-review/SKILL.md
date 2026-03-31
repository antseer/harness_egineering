---
name: harness-review
description: Use weekly or when Claude keeps making the same mistakes - analyzes recent session patterns, identifies recurring failures, and suggests concrete CLAUDE.md improvements to strengthen the harness
argument-hint: "[optional: specific problem pattern, e.g. 总是忘记更新测试]"
---

# Harness Review — Harness 深度改进

## Overview

分析飞轮累积的执行数据（`.harness/phase-journal.jsonl`），识别 Harness 的薄弱环节，实施具体改进。

**核心原则**：Eval 驱动开发——观察失败 → 改进 Harness → 减少未来失败。这是 Harness Engineering 的最高形式。

**飞轮定位**：这是飞轮的**进化引擎**。它消费 harness-resume 积累的执行日志，产出 CLAUDE.md 改进和 review-log.md 更新，供 harness-plan（规划时避坑）和 harness-init（重新初始化时纳入历史经验）消费。

**触发时机**：
- harness-resume 执行中发现严重问题时会建议运行本 Skill
- 用户每周主动运行一次
- 用户观察到 Claude 反复犯同一个错时

**Announce at start:** "正在使用 harness-review 技能分析飞轮数据并改进 Harness。"

## 执行流程

### Step 1：收集数据

1. 读取 `CLAUDE.md`（如果不存在，建议先用 `/harness-init`）
2. 读取 `.claude/settings.json` 或 `.claude/settings.local.json` 查看已有 Hooks
3. 读取 `.harness/phase-journal.jsonl`——**核心数据源**，分析所有 Phase 的执行记录
4. 读取 `.harness/review-log.md`（如果存在）查看历史改进记录
5. 读取 `.harness/config.json`（如果存在）获取技术栈信息
6. 读取 `plan.md`（如果存在）检查计划与实际代码的一致性
7. 如果用户通过 `$ARGUMENTS` 提供了具体问题描述，以此为重点

### Step 2：飞轮数据分析

**从 phase-journal.jsonl 中提取模式**：

```
分析维度：
├── 重试次数趋势：是否越来越少？（飞轮在加速）还是停滞/恶化？
├── 反复出现的问题：哪些 issues 在多个 Phase 中重复？
├── 决策一致性：是否有前后矛盾的决策？
├── CLAUDE.md 更新频率：是否每个 Phase 都需要更新？（说明初始化不够完善）
└── 文件变更模式：是否有被频繁修改但不在 CLAUDE.md 文件对应关系中的文件？
```

**如果没有 phase-journal.jsonl**（飞轮尚未运行）：
- 退回到静态分析模式：只检查 CLAUDE.md 完整性和 Hook 配置
- 建议用户通过 `/harness-resume` 执行几个 Phase 来积累数据

### Step 3：诊断分析

**检查 CLAUDE.md 的完整性**：

| 检查项 | 缺失影响 |
|--------|----------|
| 项目结构 | Claude 需要反复探索目录 → token 浪费 |
| 常用命令 | Claude 猜测命令 → 可能跑错 |
| 架构禁令 | Claude 可能违反架构约束 |
| 文件对应关系 | Claude 改代码忘改测试 |
| 禁止事项 | Claude 可能执行危险操作 |

**检查 Hook 配置**：

| 检查项 | 缺失影响 |
|--------|----------|
| Post-Edit Lint Hook | 语法/风格错误不能及时发现 |
| Post-Edit Test Hook | 功能破坏不能及时发现 |
| Pre-Bash 危险命令拦截 | 可能执行破坏性操作 |

**分析用户反馈的问题模式**：

如果用户描述了具体问题，诊断根因：
- 是 CLAUDE.md 缺少对应规则？→ 补充规则
- 是 Hook 没有自动验证？→ 建议添加 Hook
- 是任务太大上下文丢失？→ 建议用 plan.md 拆分
- 是 plan.md 的步骤不够具体？→ 建议改进规划粒度

### Step 4：生成诊断报告

```
## Harness 诊断报告

### 飞轮健康度

| 指标 | 数值 | 趋势 | 判断 |
|------|------|------|------|
| Phase 总数 | [N] | — | — |
| 平均重试次数 | [X] | ↓/→/↑ | 优秀(<1) / 正常(1-2) / 需改进(3+) |
| 一次通过率 | [Y%] | ↑/→/↓ | 优秀(>80%) / 正常(50-80%) / 需改进(<50%) |
| 反复出现的问题 | [列表] | — | 需要加禁令 |
| CLAUDE.md 更新次数 | [Z] | — | 频繁更新说明初始化不完善 |

### CLAUDE.md 评分

| 维度 | 状态 | 建议 |
|------|------|------|
| 项目结构 | ✅/⚠️/❌ | 具体建议 |
| 常用命令 | ✅/⚠️/❌ | 具体建议 |
| 架构禁令 | ✅/⚠️/❌ | 具体建议 |
| 文件对应关系 | ✅/⚠️/❌ | 具体建议 |
| 禁止事项 | ✅/⚠️/❌ | 具体建议 |

### Hook 配置评分

| Hook 类型 | 状态 | 建议 |
|-----------|------|------|
| Post-Edit Lint | ✅/❌ | 具体配置 |
| Post-Edit Test | ✅/❌ | 具体配置 |
| Pre-Bash 拦截 | ✅/❌ | 具体配置 |

### 具体改进项

| 优先级 | 问题 | 根因 | 修复方案 | 来源 |
|--------|------|------|---------|------|
| P0 | ... | ... | ... | phase-journal / 用户反馈 |
| P1 | ... | ... | ... | 静态分析 |
```

### Step 5：实施改进

向用户展示报告后：

1. **CLAUDE.md 改进**：如果用户同意，直接编辑 CLAUDE.md——将反复出现的问题转化为禁令
2. **Hook 配置**：展示可复制的 JSON，不自动修改 settings.json
3. **更新 review-log.md**——这是飞轮的关键闭环：

```markdown
## [日期] Review #[N]

### 数据摘要
- 分析了 [X] 个 Phase 的执行数据
- 平均重试次数：[Y]（上次 review: [Z]）

### 发现的问题
- [问题1] → [对策]：[已应用到 CLAUDE.md / 建议 Hook]
- [问题2] → [对策]

### CLAUDE.md 更新
- 新增禁令：[具体内容]
- 更新文件对应：[具体内容]

### 效果预期
- 预计下一轮 Phase 的 [问题1] 不再出现
- 待验证：[需要后续确认的改进]
```

4. **清理 phase-journal.jsonl**（可选）：如果日志条目超过 50 条，建议用户归档旧数据

### Step 6：闭环提示

```
Review 完成。改进已应用：
  ✅ CLAUDE.md 新增 [N] 条禁令
  📋 review-log.md 已更新（第 [X] 次 review）
  📊 飞轮健康度：[优秀/正常/需改进]

飞轮效果追踪：
  • 下次 /harness-plan 会自动读取本次发现的教训
  • 下次 /harness-resume 完成 Phase 时会自动检查新禁令是否生效

下一步：
  • 继续开发：/harness-resume
  • 开始新任务：/harness-plan [任务描述]
```

## 注意事项

- 不要自动修改 `.claude/settings.json`——只展示配置建议
- 建议要具体到可操作——不要写"改进架构规则"，要写具体要加什么规则
- 每条建议都要解释**为什么**——帮用户理解因果关系
- 如果飞轮数据不足（<3 个 Phase），告诉用户"数据不足，建议积累更多 Phase 执行数据后再做深度 review"
- 如果 Harness 已经很完善（一次通过率 >90%，无反复问题），明确告诉用户"当前 Harness 运行良好"
- 用中文输出
