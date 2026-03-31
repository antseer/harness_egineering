---
name: Harness Engineering Skill 设计与飞轮架构
description: 4个 Claude Code Skill 的设计决策、飞轮联动机制、.harness/ 数据中心架构
type: project
---

## 4 个全局 Skill

位置：`~/.claude/skills/harness-*/SKILL.md`（所有项目可用）

| Skill | 触发 | 消费 | 产出 |
|-------|------|------|------|
| `/harness-init` | 新项目 | review-log.md（历史经验） | CLAUDE.md + .harness/ 目录 + Hook 建议 |
| `/harness-plan` | 大任务开始 | CLAUDE.md + review-log.md | plan.md |
| `/harness-resume` | 新会话 | plan.md + CLAUDE.md + config.json | 代码变更 + phase-journal.jsonl + CLAUDE.md 更新 |
| `/harness-review` | 每周/问题时 | phase-journal.jsonl | CLAUDE.md 改进 + review-log.md |

## .harness/ 共享数据中心

```
.harness/
├── config.json          ← init 写，plan/resume 读（技术栈、命令）
├── phase-journal.jsonl  ← resume 写，review 读（每 Phase 执行数据）
└── review-log.md        ← review 写，plan/init 读（改进记录）
```

## 飞轮联动机制

关键设计：harness-resume 内嵌轻量级 review（Step 5），每个 Phase 完成后自动：
1. 检查 CLAUDE.md 是否需要同步更新（直接更新，不只建议）
2. 执行质量自检（重试次数、禁令违反、未预见问题）
3. 写入 phase-journal.jsonl（供 harness-review 分析趋势）
4. 严重问题时建议用户运行 /harness-review

**Why:** 飞轮能否持续转动的关键在于"观察→改进"步骤是否自动发生。旧版依赖用户手动触发 review，容易断裂。
**How to apply:** 后续如果用户想修改 Skill，必须保持这个联动机制不被破坏。特别是 harness-resume 的 Step 5 是飞轮的核心。
