# Harness Skills 使用指南

> 安装一套 Skills，让 Claude Code 自带项目初始化、跨会话接力、持续自我改进能力

---

## 第一部分：Harness Engineering 工程思想

### 核心公式

```
Agent = Model + Harness
```

**Model** 是 Claude 本身——你无法改变它。**Harness** 是围绕模型的一切基础设施——导航文件、自动验证、约束护栏、跨会话记忆——这是你能优化的全部。

改进 Harness 的 ROI 远高于换更大的模型。研究数据显示：

| 优化层级 | 性能提升 |
|---------|---------|
| Prompt Engineering | 5-15% |
| Context Engineering | 15-30% |
| **Harness Engineering** | **50-80%** |

### 演进路径

| 阶段 | 聚焦 | 代表概念 |
|------|------|---------|
| 2023-2024 | Prompt Engineering | 为单次查询写好提示词 |
| 2025 | Context Engineering | 动态组织正确的上下文信息 |
| 2026 | **Harness Engineering** | 构建环境、约束和反馈循环 |

### 在 Claude Code 中 Harness 是什么

```
Harness = CLAUDE.md + Hooks + Skills + Memory + 工作习惯

其中：
  CLAUDE.md  → 导航地图（告诉 Claude 项目结构、规则、禁令）
  Hooks      → 自动护栏（编辑后自动 lint/test，拦截危险命令）
  Skills     → 可复用能力（本仓库提供的4个 Skill）
  Memory     → 跨会话记忆（积累的经验和偏好）
  工作习惯    → 你与 Claude 的协作模式
```

### 核心设计原则

1. **写禁令而非建议** —— "禁止 X" 比 "尽量避免 X" 有效 10 倍
2. **地图而非百科** —— CLAUDE.md 100 行以内，指向更深信息源
3. **机械验证优于自觉** —— 用 Hook 自动 lint/test，不要靠 Claude "记得"
4. **上下文重置优于压缩** —— 新会话 + plan.md 比拖长一个会话可靠
5. **飞轮驱动改进** —— 执行数据自动积累，定期 review 转化为更强的 Harness

---

## 第二部分：四个 Harness Skills

### 飞轮关系

```
harness-init ──→ 产出 CLAUDE.md + .harness/
     │
     ▼
harness-plan ──→ 消费 CLAUDE.md，产出 plan.md
     │
     ▼
harness-resume ──→ 消费 plan.md，产出代码 + 执行日志
     │                  │
     │                  ▼ (每个 Phase 结束自动轻量 review)
     │
     ▼
harness-review ──→ 消费执行日志，改进 CLAUDE.md
     │
     └──→ 回到 harness-plan（更强的 Harness 指导下一轮规划）
```

---

### 1. `/harness-init` — 项目初始化

**何时用**：进入一个新项目，或项目还没有 CLAUDE.md 时。

**做什么**：
- 自动分析项目技术栈、目录结构、构建/测试命令
- 生成 100 行以内的 CLAUDE.md（项目结构 + 常用命令 + 架构禁令 + 文件对应关系）
- 创建 `.harness/` 飞轮数据目录
- 推荐 Hook 配置（展示 JSON，不自动写入）

**用法**：
```
/harness-init python-fastapi
/harness-init ts-nextjs
/harness-init              # 不带参数，自动检测
```

**产出**：
```
项目根/
├── CLAUDE.md                    ← 项目导航地图
└── .harness/
    ├── config.json              ← 技术栈元信息
    ├── review-log.md            ← 改进日志（后续 review 写入）
    └── phase-journal.jsonl      ← 执行日志（后续 resume 写入）
```

---

### 2. `/harness-plan` — 大任务规划

**何时用**：任务预估超过 30 分钟，需要多个会话才能完成时。

**做什么**：
- 读取 CLAUDE.md 理解架构，读取历史 review 数据避免重蹈覆辙
- 将大任务拆分为多个 Phase（每个 Phase = 一个会话的工作量）
- 生成 `plan.md` 作为跨会话接力的"接力棒"

**用法**：
```
/harness-plan 实现用户认证系统
/harness-plan 重构订单模块，支持多币种
```

**plan.md 结构**：
```markdown
# 计划：实现用户认证系统

**目标**：一句话描述
**预估 Phase 数**：3

## Phase 1: 数据模型 + 迁移 [状态: 待做]
### 任务
- [ ] 创建 User model (src/models/user.py)
- [ ] 编写迁移脚本
- [ ] 编写对应测试
- [ ] 验证：运行 pytest tests/test_models.py

## Phase 2: API 实现 [状态: 待做]
...

## 决策记录
（执行过程中积累）
```

**核心原则**：
- 每个 Phase 结束时代码处于可运行状态，不留半成品
- 步骤具体到文件路径，验证标准是可执行的命令
- 如果历史 review 记录了某类反复出现的问题，会在相关步骤中显式标注警告

---

### 3. `/harness-resume` — 跨会话接力

**何时用**：开新会话继续上一次未完成的任务时。

**做什么**：
- 读取 plan.md，汇报当前进度
- 执行下一个 Phase，每完成一步立即标记 `[x]`
- Phase 结束后自动执行轻量级 review（检查 CLAUDE.md 漂移、记录执行数据）

**用法**：
```
/harness-resume          # 自动执行下一个未完成的 Phase
/harness-resume Phase 3  # 指定执行某个 Phase
```

**自动行为**（每个 Phase 结束后）：
1. 更新 plan.md 中的 checkbox 和状态
2. 检查 CLAUDE.md 是否需要同步更新（新增了模块/依赖？）
3. 写入执行日志到 `.harness/phase-journal.jsonl`
4. 如果重试超过 3 次或违反禁令，建议运行 `/harness-review`

**交接提示示例**：
```
✅ Phase 2 已完成，plan.md 已更新。
📝 CLAUDE.md 已同步更新（新增了 auth 模块）
📊 执行数据已记录到 .harness/phase-journal.jsonl

下一步：
  • 继续本会话：告诉我"继续"
  • 开新会话（推荐）：输入 /harness-resume
```

---

### 4. `/harness-review` — 深度改进

**何时用**：
- 每周主动运行一次
- Claude 反复犯同一个错误时
- `/harness-resume` 建议运行时

**做什么**：
- 分析 `.harness/phase-journal.jsonl` 中的执行数据
- 识别反复出现的问题模式
- 生成诊断报告（飞轮健康度 + CLAUDE.md 评分 + Hook 配置评分）
- 将反复出现的问题转化为 CLAUDE.md 中的禁令
- 更新 `.harness/review-log.md`

**用法**：
```
/harness-review
/harness-review 总是忘记更新测试文件
```

**诊断报告示例**：
```
飞轮健康度：
  Phase 总数: 12
  平均重试次数: 1.2 (↓ 上次 2.1)
  一次通过率: 75% (↑ 上次 58%)

具体改进：
  P0: Claude 经常忘记更新 i18n 文件
      → CLAUDE.md 新增禁令："修改任何用户可见文本时必须同步更新 locales/"
```

---

## 第三部分：安装与使用

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/antseer/harness_egineering.git

# 2. 运行安装脚本（复制 Skills 到 ~/.claude/skills/）
cd harness_egineering
./install-skills.sh
```

安装后 Skills 全局生效，在任何项目中都可以使用。

### 典型工作流

```
┌─ 新项目 ─────────────────────────────────────────────┐
│                                                       │
│  /harness-init python-fastapi                         │
│  → 生成 CLAUDE.md + .harness/ + Hook 建议             │
│                                                       │
├─ 大任务 ─────────────────────────────────────────────┤
│                                                       │
│  /harness-plan 实现支付模块                            │
│  → 生成 plan.md（3个 Phase）                          │
│                                                       │
│  Session 1: /harness-resume → 执行 Phase 1            │
│  Session 2: /harness-resume → 执行 Phase 2            │
│  Session 3: /harness-resume → 执行 Phase 3            │
│                                                       │
├─ 定期维护 ────────────────────────────────────────────┤
│                                                       │
│  /harness-review                                      │
│  → 分析执行数据，改进 CLAUDE.md                        │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 最佳实践

1. **每个新项目先 `/harness-init`** —— 10 分钟投入，后续每个会话都受益
2. **超过 30 分钟的任务用 `/harness-plan`** —— 跨会话接力比拖长会话可靠
3. **每个 Phase 开一个新会话** —— 干净上下文 + plan.md 比压缩的旧上下文好
4. **每周跑一次 `/harness-review`** —— 让飞轮持续转动，Harness 越用越强
5. **不要手动编辑 `.harness/` 下的文件** —— 让 Skills 自动维护

### 不需要 Skills 的场景

- 任务很小（< 30 分钟）：直接做，不需要 plan.md
- 一次性脚本或探索性工作：不需要 harness-init
- 项目已有完善的 CLAUDE.md：直接用 harness-plan/resume

---

## 第四部分：原理简述

### 为什么是"飞轮"

```
执行（resume）→ 积累数据（phase-journal）→ 分析改进（review）
     ↑                                            │
     └── 更强的 CLAUDE.md ← ─── ─── ─── ─── ────┘
```

每次执行都在积累数据，每次 review 都在改进 Harness，改进后的 Harness 让下次执行更顺畅。这个循环不需要你手动推动——resume 自动记录数据，review 自动提取教训。

### 为什么用 plan.md 而不是一个长会话

LLM 的上下文窗口有两个问题：
- **压缩损失**：长会话被压缩时会丢失关键细节
- **累积焦虑**：之前的失败尝试留在上下文中，影响后续决策

plan.md 的解法：每个新会话都是"干净的大脑 + 完整的地图"。Claude 不需要记住之前做了什么——plan.md 里全部写着。

### 这套 Skills 的来源

基于 Anthropic、OpenAI、LangChain 等团队在 2025-2026 年发表的 Harness Engineering 研究和实践，提炼为适配 Claude Code 原生能力的 4 个 Skills。详细研究报告见本仓库的 `RESEARCH_FINDINGS.md` 和 `harness_engineering_research_report.md`。
