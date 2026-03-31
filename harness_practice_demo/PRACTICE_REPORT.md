# Harness Engineering Skill 实践报告

> 日期：2026-03-29
> 项目：Task Manager API（FastAPI + SQLAlchemy + JWT 认证）

---

## 一、各 Phase 执行记录

### Phase A：/harness-init（项目初始化）

**执行内容**：
1. 探索项目目录结构、pyproject.toml、技术栈（Python 3.9 + FastAPI + SQLAlchemy + ruff + pytest）
2. 生成 CLAUDE.md（44 行，包含项目结构、常用命令、架构规则、文件对应关系、禁止事项）
3. 生成 Hook 配置建议（PostEditFile lint、PostEditFile test、PreBash 危险命令拦截）

**结果**：CLAUDE.md 已创建，Hook 配置以 JSON 形式展示但未自动写入 settings.json（符合 Skill 要求）。

**遇到的问题**：无明显问题，流程清晰。

**Skill 指引评价**：
- 清晰度：★★★★★ — Step 1-4 逻辑清楚，100 行以内、写禁令等原则非常实用
- 遗漏：Skill 未提到 .gitignore 的检查和生成建议，对于新项目这很重要

---

### Phase B：/harness-plan（任务规划）

**执行内容**：
1. 理解任务：为 Task API 添加用户认证（注册 + 登录 + JWT）
2. 拆分为 3 个 Phase：用户模型与认证 API → 任务与用户关联 → 安全加固与收尾
3. 生成 plan.md，包含每个 Phase 的具体步骤、交付物、验证标准

**结果**：plan.md 已创建，格式严格遵循 Skill 模板。

**遇到的问题**：无。

**Skill 指引评价**：
- 清晰度：★★★★★ — 拆分原则和 plan.md 模板非常具体
- 亮点：「每个 Phase 结束时代码处于可运行状态」这条原则非常关键，防止留半成品
- 建议：可以补充"估计每个 Phase 的文件变更数量"帮助评估工作量

---

### Phase C：/harness-resume（执行 Phase 1）

**执行内容**：
1. 读取 plan.md，汇报进度（0/3 已完成）
2. 执行 Phase 1 全部 9 个步骤：
   - 添加 passlib + python-jose 依赖
   - 创建 User 模型、Schema、认证工具模块、认证路由
   - 注册 auth router
   - 编写 6 个认证测试
3. 验证：13 个测试全部通过，ruff 检查通过
4. 更新 plan.md：标记完成、记录 3 条决策、2 条已知问题、8 个文件变更

**结果**：Phase 1 完全完成，代码可运行，测试全部通过。

**遇到的问题**：
1. **Python 3.9 兼容性**：最初用了 `str | None` 语法导致语法错误，需要改为 `Optional[str]` + `from __future__ import annotations`。CLAUDE.md 中已有规则但第一次写代码时仍然犯错——说明 Harness 规则需要在代码模板层面强制执行。
2. **ruff 发现未使用导入**：最初在 schemas/user.py 中导入了 `EmailStr` 但未使用。如果有 PostEditFile lint hook，可以立即发现。
3. **登录接口设计**：plan.md 中未指定登录接口的请求格式（表单 vs JSON），执行时需要自行决策并记录。

**Skill 指引评价**：
- 清晰度：★★★★☆ — Step 1-5 覆盖了完整的读取→汇报→执行→更新→交接流程
- 遗漏：Skill 没有提到"执行步骤时如果发现 plan.md 的步骤描述不够具体怎么办"——实际执行中经常需要补充细节
- 建议：增加一条"执行时可以细化步骤描述，但不改变 Phase 整体范围"

---

### Phase D：/harness-review（Harness 审查）

**执行内容**：
1. 读取 CLAUDE.md（存在）、.claude/settings.json（不存在）、.harness/ 目录（不存在）
2. 诊断分析：
   - CLAUDE.md 缺少认证模块说明（⚠️）
   - 缺少认证相关架构规则（⚠️）
   - Hook 完全未配置（❌）
   - 缺少 .gitignore（⚠️）
3. 生成具体改进建议表格
4. 应用改进：
   - 更新 CLAUDE.md（补充 auth.py、认证规则、安全禁令）
   - 创建 .gitignore
   - 创建 .harness/weekly-review.md 记录本次审查

**结果**：CLAUDE.md 从 44 行优化为 46 行（结构更紧凑、信息更完整），新增 .gitignore 和审查日志。

**遇到的问题**：无。

**Skill 指引评价**：
- 清晰度：★★★★★ — 检查项表格和诊断报告模板非常实用，不需要猜该查什么
- 亮点：「每条建议都要解释为什么」这条要求确保建议不是空话
- 建议：可以增加"检查 plan.md 与实际代码是否一致"的步骤，因为计划和执行经常有偏差

---

## 二、4 个 Skill 的整体使用体验评价

| Skill | 实用性 | 清晰度 | 完整度 | 总评 |
|-------|--------|--------|--------|------|
| harness-init | ★★★★★ | ★★★★★ | ★★★★☆ | 非常实用，开箱即用 |
| harness-plan | ★★★★★ | ★★★★★ | ★★★★★ | 模板设计优秀，plan.md 格式实战性强 |
| harness-resume | ★★★★☆ | ★★★★☆ | ★★★★☆ | 核心流程清晰，但细节处理需补充 |
| harness-review | ★★★★★ | ★★★★★ | ★★★★☆ | 诊断框架完善，推动持续改进 |

**整体评价**：四个 Skill 组成了完整的工程闭环：初始化 → 规划 → 执行 → 回顾。这个闭环的最大价值在于将 Agent 的隐性知识（该怎么组织项目、该遵守什么规则）显式化为可检查、可改进的配置文件。

---

## 三、发现的问题和改进建议

### 跨 Skill 的问题

1. **CLAUDE.md 漂移问题**：harness-init 生成的 CLAUDE.md 在 harness-resume 执行完后已过时。目前只有 harness-review 会修复，但如果用户不主动运行 review，CLAUDE.md 会持续漂移。
   - **建议**：在 harness-resume 的 Step 4 中增加"检查 CLAUDE.md 是否需要更新"的提示。

2. **Hook 配置的"最后一公里"**：harness-init 和 harness-review 都只展示 Hook JSON 而不写入。这符合安全原则，但用户很容易忘记手动配置。
   - **建议**：增加一个提醒，如"如果你还没配置 Hook，可以运行 `/harness-init hooks` 查看推荐配置"。

3. **plan.md 的步骤粒度问题**：plan.md 中"创建认证路由"这样的步骤，在实际执行时包含了大量隐含决策（用表单还是 JSON？错误码用什么？）。
   - **建议**：在 harness-plan 中增加"对关键接口列出备选方案和推荐选择"。

### 单 Skill 的建议

| Skill | 建议 |
|-------|------|
| harness-init | 增加 .gitignore 检查和生成建议 |
| harness-plan | 增加"预估文件变更数量"帮助评估工作量；增加接口设计决策点 |
| harness-resume | 增加"步骤描述不够具体时可细化但不改 Phase 范围"的指导；增加"Phase 完成后检查 CLAUDE.md 是否需要更新"的步骤 |
| harness-review | 增加"检查 plan.md 与实际代码一致性"的步骤 |

---

## 四、对 Skill 文件本身的修改建议

### harness-init/SKILL.md

在 Step 1 末尾增加：
```
3. 检查项目是否有 `.gitignore`，如果没有根据技术栈建议创建
```

### harness-plan/SKILL.md

在 Step 2 拆分原则中增加：
```
- 对于涉及 API 设计的 Phase，列出关键设计决策点（如请求格式、错误码、认证方式）
```

### harness-resume/SKILL.md

在 Step 4 末尾增加第 6 条：
```
6. **检查 CLAUDE.md**：本 Phase 新增或修改了模块/文件吗？如果是，检查 CLAUDE.md 的项目结构是否需要更新
```

在 Step 3 第 3 条后增加：
```
3.5 如果执行时发现步骤描述不够具体，可以在 plan.md 中细化当前步骤的描述，但不改变 Phase 整体范围
```

### harness-review/SKILL.md

在 Step 2 检查项中增加：
```
**检查 plan.md 一致性**（如果存在 plan.md）：
- plan.md 中的文件变更清单是否与实际文件一致
- 决策记录是否完整反映了实际做出的决策
```

---

## 五、最终项目文件清单

```
harness_practice_demo/
├── CLAUDE.md                 # Harness 导航地图（harness-init 生成，harness-review 优化）
├── plan.md                   # 跨会话任务计划（harness-plan 生成，harness-resume 更新）
├── pyproject.toml            # 项目依赖和工具配置
├── .gitignore                # harness-review 建议后创建
├── .harness/
│   └── weekly-review.md      # harness-review 审查日志
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 入口
│   ├── config.py             # 配置（含 JWT 参数）
│   ├── database.py           # 数据库连接
│   ├── auth.py               # 认证工具（Phase 1 新增）
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tasks.py          # 任务 CRUD 路由
│   │   └── auth.py           # 认证路由（Phase 1 新增）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── user.py           # Phase 1 新增
│   └── schemas/
│       ├── __init__.py
│       ├── task.py
│       └── user.py           # Phase 1 新增
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_tasks.py          # 7 个测试
    └── test_auth.py           # 6 个测试（Phase 1 新增）
```

测试结果：13 passed, ruff check 0 errors
