# Claude Code Harness Engineering 实践指南

> 面向 Claude Code 用户的 Harness Engineering 落地手册
> 不需要写框架代码，用好 Claude Code 内置能力 + 配置即可

---

## 核心公式

```
Agent = Model + Harness

在 Claude Code 中：
  Model   = Claude（你无法改变）
  Harness = CLAUDE.md + Hooks + Memory + 你的工作习惯

→ 你能优化的全部是 Harness
```

**核心观点**：改进 Harness 的 ROI 通常高于换更大的模型。在 Claude Code 中，这意味着——写好 CLAUDE.md、配好 Hooks、养成正确的工作习惯，比期待模型更聪明有效得多。

---

## Claude Code 已经内置了什么？

在开始之前，先了解 Claude Code 已经帮你做了哪些 Harness 工作：

| Harness 能力 | Claude Code 内置实现 | 你需要额外做的 |
|-------------|---------------------|--------------|
| Action Space（工具集） | Read, Edit, Write, Bash, Grep, Glob（精选6个核心工具） | 无需额外配置 |
| Observation 格式化 | 所有工具输出自带行号、上下文、截断提示 | 无需额外配置 |
| 工具编排 | Agent 子系统可并行调度子任务 | 无需额外配置 |
| 权限护栏 | 危险操作自动弹出确认提示 | 无需额外配置 |
| Token/成本统计 | 每次会话结束显示用量和费用 | 无需额外配置 |
| 会话恢复 | `claude --resume <id>` 回溯历史会话 | 无需额外配置 |
| **导航文件** | — | **需要你写 CLAUDE.md** |
| **架构约束** | — | **需要你写禁令规则** |
| **自动验证** | — | **需要你配 Hooks** |
| **跨会话状态** | Memory 系统（自动读取，半自动写入） | **需要你主动触发保存** |
| **任务接力** | — | **需要你用 plan.md 管理** |

**结论**：你只需要做5件事——写 CLAUDE.md、写禁令、配 Hooks、管理 Memory、用 plan.md 拆分大任务。

---

## Phase 1：项目导航文件（10分钟）

### 目标

给 Claude 一张"地图"，让它进入项目时立刻知道：代码在哪、规则是什么、什么不能做。

### 你要做的

在项目根目录创建 `CLAUDE.md`，约100行。

### 模板

```markdown
# CLAUDE.md

## 项目结构
- `src/api/` — API 路由层
- `src/services/` — 业务逻辑层
- `src/models/` — 数据模型层
- `tests/` — 测试文件，与 src/ 目录结构镜像

## 常用命令
- 启动开发服务器: `uvicorn src.main:app --reload`
- 运行全部测试: `pytest tests/ -v`
- 运行单个测试: `pytest tests/test_auth.py::test_login -v`
- Lint 检查: `ruff check src/`
- 类型检查: `mypy src/`

## 架构规则（必须遵守）
- 分层顺序: models → services → api，禁止反向依赖
- api 层不允许直接操作数据库，必须通过 services 层
- 所有 API 返回统一格式: `{"data": ..., "error": ...}`
- 修改 src/api/*.py 时必须同步更新 tests/test_*.py 对应测试

## 禁止事项
- 不要一次重构超过3个文件
- 不要修改 alembic 迁移文件，只能新建迁移
- 不要删除或修改已有测试来让测试通过，应该修改实现代码
```

### 关键原则

1. **是"地图"不是"百科全书"** — 100行左右，指向更深层的文档
2. **写禁止规则而非建议** — "禁止 X" 比 "尽量避免 X" 约束力强得多
3. **写常用命令** — 让 Claude 能直接跑测试验证自己的修改
4. **写文件对应关系** — "改 X 必须同步改 Y" 防止遗漏

### 验证

创建后开一个新的 Claude Code 会话，让它描述项目结构和规则。如果它能准确复述，说明 CLAUDE.md 写得到位。

---

## Phase 2：自动化护栏（20分钟）

### 目标

用机制自动拦截错误，而不是靠"拜托 Claude 别犯错"。

### 2.1 在 CLAUDE.md 中写架构禁令

这是最低成本的护栏。在 Phase 1 的 CLAUDE.md 基础上，重点强化"禁止"部分：

```markdown
## 架构禁令
- 禁止: service 层导入 api 层或 ui 层的任何模块
- 禁止: 在 api 层直接写 SQL 或调用 ORM
- 禁止: 修改 .env 或任何 credentials 文件
- 禁止: 使用 rm -rf、git push --force、DROP TABLE
- 禁止: 在没有对应测试的情况下提交新功能
```

Claude 会严格遵守这些规则。如果它违反了，你在 Phase 4（回顾）中将这个案例补充为更明确的禁令即可。

### 2.2 配置 Hooks — 自动验证

Hooks 是 Claude Code 的核心 Harness 机制。在 `.claude/settings.json` 中配置：

#### 第一级：Post-Edit 自动 Lint（最推荐，先配这个）

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "cd $PROJECT_DIR && ruff check $CLAUDE_FILE_PATH 2>&1 | head -20"
      }
    ]
  }
}
```

**效果**：Claude 每次编辑文件后自动跑 Linter。如果有问题，错误信息回传给 Claude，它会自行修复。

#### 第二级：Post-Edit 自动跑测试

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "cd $PROJECT_DIR && ruff check $CLAUDE_FILE_PATH 2>&1 | head -10; python -m pytest tests/ -x --tb=short 2>&1 | tail -15"
      }
    ]
  }
}
```

**效果**：编辑后自动 Lint + 测试。双重验证。

#### 第三级：Pre-Bash 阻止危险命令

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "echo \"$CLAUDE_BASH_COMMAND\" | grep -qE 'rm -rf|DROP TABLE|git push --force' && echo 'BLOCKED: 危险命令被拦截' && exit 1 || exit 0"
      }
    ]
  }
}
```

**效果**：Claude 执行 bash 前自动检查，危险操作直接拦截。

### 根据你的技术栈选择

| 技术栈 | Lint 命令 | 测试命令 |
|--------|----------|---------|
| Python | `ruff check $CLAUDE_FILE_PATH` | `pytest tests/ -x --tb=short` |
| TypeScript | `npx eslint --quiet $CLAUDE_FILE_PATH` | `npx jest --bail --silent` |
| Go | `golangci-lint run $CLAUDE_FILE_PATH` | `go test ./... -count=1` |
| Rust | `cargo clippy -- -W warnings` | `cargo test` |

把上面对应的命令替换到 Hook 配置中即可。

---

## Phase 3：反馈循环（10分钟）

### 目标

让 Claude 形成"改代码 → 验证 → 发现问题 → 自己修 → 再验证"的闭环。

### 3.1 在 CLAUDE.md 中写工作流规则

如果你在 Phase 2 已经配了 Hooks，反馈循环其实**已经自动形成了**：

```
Claude 编辑文件
  → Hook 自动跑 lint + 测试
  → 结果回传给 Claude
  → 有错误 → Claude 自动修复 → 再次触发 Hook
  → 通过 → 继续下一步
```

为了让这个循环更可靠，在 CLAUDE.md 中补充：

```markdown
## 工作流程（必须遵守）
- 每次修改代码后，必须运行测试验证
- 如果测试失败，修复实现代码，不要修改测试
- 如果连续修复3次仍失败，停下来向我说明问题和尝试过的方案
- 完成功能后，自我审查：检查是否有安全隐患、性能问题、遗漏的边界条件
```

### 3.2 Generator-Evaluator 模式在 Claude Code 中的应用

Anthropic 的双 Agent 模式（Generator 写代码 + Evaluator 打分迭代），在 Claude Code 中有三种落地方式：

#### 方式一：你当 Evaluator（零成本，日常使用）

```
你：实现用户登录功能
Claude：[写代码]
你：测试了，登录成功但没返回 token。评分 5/10，请修复
Claude：[修复]
你：token 有了但过期时间太短。7/10
Claude：[调整]
你：完美，通过
```

你的反馈就是 Evaluator 的输出。每轮给一个评分 + 具体问题，Claude 会针对性迭代。

#### 方式二：Claude 自我评估（推荐写入 CLAUDE.md）

```markdown
## 完成检查清单
每次完成一个功能后，在交付前自我检查：
1. 所有现有测试是否通过？
2. 是否为新功能编写了测试？
3. 是否有未处理的错误路径？
4. 修改是否影响了其他模块？
5. 代码变更是否简洁（无冗余代码）？
```

Claude 会在完成编码后自动走这个清单，相当于既当 Generator 又当 Evaluator。

#### 方式三：用 Subagent 做 Code Review

对于重要的修改，可以在对话中要求：

```
你：用一个 agent 审查刚才的所有改动，检查安全性和架构合规性
```

Claude 会启动一个子 Agent 专门审查代码，然后汇报问题。

### 3.3 策略性转向（重要习惯）

如果 Claude 连续修了3次还没改好，**不要继续在同一个对话里纠缠**：

```bash
# 1. 让 Claude 总结失败原因
你：总结一下目前的问题和你尝试过的方案

# 2. 退出，开新会话
claude

# 3. 换个角度重新描述
你：之前尝试用 X 方案实现登录但失败了，原因是 Y。请换一个思路。
```

**为什么**：Anthropic 的研究发现，上下文越长 Agent 越"焦虑犹豫"。新会话 = 干净的大脑，更果断。

---

## Phase 4：观察与持续改进（每周10分钟）

### 目标

观察 Claude 的失败模式，将对策写入 CLAUDE.md，形成 Harness 的持续进化。

### 4.1 你已有的可观测数据

| 数据 | 来源 | 操作 |
|------|------|------|
| Token 消耗和费用 | 会话结束时自动显示 | 留意异常高的会话 |
| 完整对话历史 | `claude --resume <id>` | 回溯问题会话 |
| 工具调用记录 | 对话中每步的输入/输出 | 观察重复失败 |

### 4.2 可选：用 Hook 记录结构化日志

如果你想跨会话分析 Claude 的行为模式：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "echo '{\"time\":\"'$(date -Iseconds)'\",\"event\":\"edit\",\"file\":\"'$CLAUDE_FILE_PATH'\"}' >> $PROJECT_DIR/.harness/trajectory.jsonl"
      }
    ]
  }
}
```

这会生成 `.harness/trajectory.jsonl`，每行一条记录，方便后续统计分析。

### 4.3 核心实践：每周回顾（最重要的10分钟）

每周花10分钟问自己3个问题：

```
1. Claude 本周反复犯了什么错？
   → 把对策加到 CLAUDE.md 的禁令中

2. 哪些任务重试次数最多？
   → 这些任务缺少上下文，补充到 CLAUDE.md

3. 哪些会话 token 消耗异常高？
   → 可能需要拆分任务或补充关键信息
```

**举例**：

```
观察：Claude 每次改 API 代码都忘了更新测试
原因：CLAUDE.md 没有说明文件对应关系
修复：在 CLAUDE.md 加——"修改 src/api/*.py 时必须同步更新 tests/test_*.py"
效果：下次不再遗漏
```

```
观察：Claude 在处理数据库迁移时总是直接修改旧迁移文件
原因：CLAUDE.md 没有禁止这个操作
修复：加——"禁止修改已有迁移文件，只能新建迁移"
效果：问题消失
```

这就是 **Eval 驱动开发**的最简形式：观察失败 → 改进 Harness → 减少未来失败。

### 4.4 可选：维护回顾日志

```markdown
# .harness/weekly-review.md

## 2026-W13 (3/24 - 3/30)

### 发现的问题
- Claude 改 service 层时直接导入了 ui 层 → 已加架构禁令
- 跑测试前忘了启动 dev server → 已加到 CLAUDE.md 常用命令

### CLAUDE.md 本周更新
- 新增禁令：service 层不允许导入 ui 层
- 新增命令：启动 dev server 的完整命令

### 效果
- 一次通过率：70%（上周 50%）
- 平均重试次数：1.5 次（上周 2.3 次）
```

不需要搭仪表盘，一个 Markdown 文件足够追踪 Harness 的进化效果。

---

## Phase 5：大任务跨会话接力（按需使用）

### 目标

解决 Claude Code 的根本限制——单次会话的上下文窗口有限。大任务需要拆分到多个会话中接力完成。

### 5.1 核心原则：上下文重置优于上下文压缩

Anthropic 的关键发现：

```
❌ 上下文压缩（一个长对话做完所有事）→ Claude 越来越慢、越来越犹豫
✅ 上下文重置（多个短对话 + 状态文件接力）→ 每次都果断高效
```

**实操规则**：一个 Phase 一个会话，超过 20-30 轮对话就开新会话。

### 5.2 plan.md — 会话间的接力棒

大任务开始前，先让 Claude 制定计划：

```
你：分析项目，把实现用户认证系统的计划写到 plan.md，不要动代码
```

`plan.md` 应该长这样：

```markdown
# 计划：用户认证系统

## Phase 1: 数据模型 [状态: 待做]
- [ ] 创建 User model (src/models/user.py)
- [ ] 创建数据库迁移
- [ ] 编写 model 层单元测试

## Phase 2: 注册功能 [状态: 待做]
- [ ] 实现注册 API (POST /api/auth/register)
- [ ] 密码用 bcrypt 加密
- [ ] 输入验证（邮箱格式、密码强度）
- [ ] 编写注册测试

## Phase 3: 登录功能 [状态: 待做]
- [ ] 实现登录 API (POST /api/auth/login)
- [ ] JWT token 生成，过期时间24小时
- [ ] 编写登录测试

## Phase 4: 认证中间件 [状态: 待做]
- [ ] 实现 JWT 验证中间件
- [ ] 保护需要登录的路由
- [ ] 集成测试

## 决策记录
- （执行过程中积累）

## 已知问题
- （执行过程中积累）
```

### 5.3 分会话执行流程

```
会话 1（规划）
  你：分析项目，制定 plan.md，不要写代码
  Claude：[生成 plan.md]
  结束

会话 2（Phase 1）
  你：读 plan.md，执行 Phase 1
  Claude：[创建模型、迁移、测试]
  你：更新 plan.md 进度，记录做过的决策和遇到的问题
  Claude：[更新 plan.md，Phase 1 标记 ✅]
  结束

会话 3（Phase 2）
  你：读 plan.md，继续
  Claude：[读 plan.md → 知道 Phase 1 已完成 → 从 Phase 2 开始]
  ...
  结束

会话 N（收尾）
  你：读 plan.md，完成剩余工作
  Claude：[全部完成]
  你：删除 plan.md（或移到 docs/ 归档）
  结束
```

**每个会话的 Claude 都是"干净的大脑 + 完整的地图"**。

### 5.4 会话结束前的标准操作

每次会话结束前，让 Claude 做三件事：

```
你：更新 plan.md，要包含：
1. 标记已完成的步骤
2. 记录做过的重要决策和原因
3. 记录遇到的问题和未解决的事项
```

这样下一个会话的 Claude 不会推翻旧决策，也不会踩同样的坑。

### 5.5 什么时候该开新会话？

| 信号 | 操作 |
|------|------|
| 一个 Phase 完成了 | 更新 plan.md → 开新会话 |
| Claude 响应明显变慢 | 上下文太长了 → 开新会话 |
| Claude 反复犯同一个错 | 思维定式 → 开新会话并换思路 |
| 对话超过 20-30 轮 | 预防性重置 → 开新会话 |
| 话题切换（从写代码到 debug） | 不同任务类型 → 开新会话 |

### 5.6 Memory 系统 — 长期记忆

plan.md 是**短期任务状态**（任务完成就删），Memory 是**长期项目记忆**（持续有效）。

#### Memory 的隔离机制

```
~/.claude/projects/<目录路径编码>/memory/

你在 /home/user/project-A 启动 claude → 读 project-A 的记忆
你在 /home/user/project-B 启动 claude → 读 project-B 的记忆
互不可见、互不干扰
```

#### Memory 的三层层级

| 层级 | 位置 | 作用域 |
|------|------|--------|
| 全局 | `~/.claude/memory/` | 所有项目共享（如"用户偏好中文"） |
| 项目级 | `~/.claude/projects/<编码>/memory/` | 仅当前目录（如"用 bcrypt 不用 argon2"） |
| CLAUDE.md | 项目根目录 | 仅当前目录（架构规则、命令等） |

#### 什么时候用 Memory vs plan.md

| | plan.md | Memory |
|--|---------|--------|
| 内容 | 当前任务进度和步骤 | 长期规则、偏好、决策 |
| 生命周期 | 任务完成即删除 | 长期保留 |
| 触发方式 | 你手动让 Claude 读/写 | 保存后每次新会话自动加载 |
| 示例 | "Phase 2 完成，Phase 3 待做" | "该项目用 bcrypt" |

#### 触发 Memory 保存

```
你：记住这个项目用 bcrypt 做密码加密，不要用 argon2
Claude：[自动写入记忆文件，下次会话自动生效]
```

---

## 反模式避坑指南

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **CLAUDE.md 写成百科全书** | Claude 信息过载，抓不住重点 | 100行以内，只写规则和命令 |
| **只写建议不写禁令** | "尽量避免" 约束力太弱 | 用"禁止"、"必须"、"不允许" |
| **一个会话做完所有事** | 上下文爆炸，Claude 变慢变犹豫 | 分 Phase，每个 Phase 一个会话 |
| **不跑测试就提交** | 错误累积，后面越来越难修 | Hooks 自动验证，每次编辑后跑测试 |
| **测试失败就改测试** | 掩盖 bug | 改实现代码，不改测试 |
| **不记录决策** | 新会话推翻旧决策，反复横跳 | plan.md 中维护决策记录 |
| **Claude 修3次还没好就继续催** | 陷入死循环 | 开新会话，换思路 |
| **从不回顾优化 CLAUDE.md** | Harness 停止进化 | 每周10分钟回顾，持续改进 |

---

## 渐进式执行路线图

```
第 1 天：最小 Harness
  └── 写 CLAUDE.md（项目结构 + 常用命令 + 架构禁令）

第 2-3 天：自动化护栏
  ├── 配置 Post-Edit Hook（自动 Lint）
  ├── 配置 Post-Edit Hook（自动测试）
  └── 可选：Pre-Bash Hook（拦截危险命令）

第 1-2 周：反馈循环
  ├── 在 CLAUDE.md 写工作流规则和完成检查清单
  ├── 养成习惯：修3次不好就开新会话
  └── 第一次周回顾：根据 Claude 的错误模式优化 CLAUDE.md

第 2-4 周：大任务管理
  ├── 开始用 plan.md 管理多阶段任务
  ├── 养成习惯：一个 Phase 一个会话
  └── 用 Memory 保存长期有效的项目决策

持续：Eval 驱动开发
  ├── 每周回顾 Claude 失败模式 → 改进 CLAUDE.md
  ├── 观察重试次数和 token 消耗趋势
  └── CLAUDE.md 随项目进化持续更新
```

---

## 关键参考资料

| 资源 | 重点 | 链接 |
|------|------|------|
| OpenAI - Harness Engineering | AGENTS.md 实践、工具设计 | https://openai.com/index/harness-engineering/ |
| Anthropic - Effective Harnesses | 上下文重置、双 Agent 模式 | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| Anthropic - Harness Design | 单 Agent 设计、Generator-Evaluator | https://www.anthropic.com/engineering/harness-design-long-running-apps |
| LangChain - Anatomy of Harness | 五层架构、Observation 设计 | https://blog.langchain.com/the-anatomy-of-an-agent-harness/ |
| SWE-agent | Action Space 精选工具集研究 | https://swe-agent.com/ |
| Martin Fowler - Harness Engineering | 概念分析与演进 | https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html |

---

*一句话总结：**CLAUDE.md 是地图，Hooks 是护栏，plan.md 是接力棒，Memory 是长期记忆，每周回顾是进化引擎。** 做好这5件事，你的 Claude Code Harness 就会越来越强。*
