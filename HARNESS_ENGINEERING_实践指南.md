# Harness Engineering 实践指南

> 从理论到落地：如何为 AI Agent 构建生产级 Harness

---

## 一、核心公式

```
Agent = Model + Harness

性能提升来源：
  Prompt Engineering   →  5-15%
  Context Engineering  → 15-30%
  Harness Engineering  → 50-80%   ← 最大杠杆点
```

**Harness 不是一个产品，而是一种工程实践。** 它是你围绕 LLM 构建的所有基础设施的总和。

---

## 二、Harness 的五层架构（实践版）

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

---

## 三、实践路线图：从零开始构建 Harness

### Phase 1：最小可行 Harness（1天）

#### 1.1 创建 AGENTS.md（智能体导航文件）

这是 Harness 的"目录"，不是百科全书。约100行即可。

```markdown
# AGENTS.md

## 项目结构
- `src/` — 核心代码
- `tests/` — 测试文件
- `docs/` — 文档

## 架构决策
- 使用 FastAPI + SQLite
- 分层：Types → Config → Service → API
- 所有 API 返回统一信封格式

## 工作约定
- 先写测试，再写实现
- 每个函数不超过50行
- 不允许直接修改数据库，必须通过 Service 层

## 已知约束
- Context Window 限制：读取大文件时分段
- 不要一次性重构超过3个文件
```

**OpenAI 经验**：AGENTS.md 是"地图"不是"百科全书"。100行左右，指向 `docs/` 目录中更深层的信息源。

#### 1.2 定义 Action Space（工具集）

**核心原则：最小充分集（Minimal Sufficient Set）**

```
❌ 错误做法：给 Agent 100个工具
✅ 正确做法：给 Agent 5-13个精选工具

SWE-agent 的研究证明：
  原始 Linux shell (100+ 命令) → 差的表现
  精选 13 个工具              → 显著提升
```

**实践模板**：为你的 Agent 定义工具集

```yaml
# harness/tools.yaml
tools:
  # 文件导航（必须有行号）
  - name: read_file
    description: "读取文件内容，返回带行号的内容。用于理解代码后再修改。"
    params:
      file_path: { type: string, required: true }
      start_line: { type: integer, required: false }
      end_line: { type: integer, required: false }

  # 搜索（提供上下文）
  - name: search_code
    description: "在代码库中搜索关键词。返回匹配行及前后各3行上下文。"
    params:
      pattern: { type: string, required: true }
      path: { type: string, required: false }

  # 编辑（精确替换，非覆盖）
  - name: edit_file
    description: "精确替换文件中的文本。必须先 read_file 再编辑。"
    params:
      file_path: { type: string, required: true }
      old_text: { type: string, required: true }
      new_text: { type: string, required: true }

  # 执行（沙箱化）
  - name: run_command
    description: "在沙箱中执行命令。有超时和资源限制。"
    params:
      command: { type: string, required: true }
      timeout_ms: { type: integer, default: 30000 }

  # 提交
  - name: submit
    description: "提交最终结果。只在确认完成时调用。"
```

#### 1.3 设计 Observation 格式

**关键洞察**：Agent 看到什么，决定了它能做什么。

```
❌ 差的 Observation（原始输出）：
def hello():
    print("hello")
def world():
    print("world")

✅ 好的 Observation（结构化、带元数据）：
[File: src/main.py] [Lines 1-4 of 120] [Language: Python]
   1 | def hello():
   2 |     print("hello")
   3 | def world():
   4 |     print("world")
[Showing 4 of 120 lines. Use scroll_down to see more.]
```

**Observation 格式化清单**：
- [ ] 文件内容始终带行号
- [ ] 显示文件路径和总行数
- [ ] 搜索结果显示上下文行
- [ ] 命令执行显示退出码和耗时
- [ ] 截断时明确告知（"显示前100行，共500行"）
- [ ] 错误信息包含修复建议

---

### Phase 2：约束与护栏（2-3天）

#### 2.1 架构约束（Architectural Constraints）

**OpenAI 的实践**：用 Linter + 结构测试机械化执行架构规则。

```python
# harness/constraints/architecture.py
"""
架构约束验证器
在每次代码修改后自动运行
"""

LAYER_ORDER = ["types", "config", "repo", "service", "runtime", "ui"]

ALLOWED_IMPORTS = {
    "types":   [],                          # types 不依赖任何层
    "config":  ["types"],                   # config 只依赖 types
    "repo":    ["types", "config"],         # repo 依赖 types + config
    "service": ["types", "config", "repo"], # service 可以用 repo
    "runtime": ["types", "config", "service"],
    "ui":      ["types", "config", "service", "runtime"],
}

def validate_imports(file_path: str, imports: list[str]) -> list[str]:
    """验证文件的导入是否违反分层架构"""
    layer = detect_layer(file_path)
    allowed = ALLOWED_IMPORTS.get(layer, [])
    violations = []
    for imp in imports:
        imp_layer = detect_layer(imp)
        if imp_layer and imp_layer not in allowed and imp_layer != layer:
            violations.append(
                f"❌ {file_path} ({layer}) 不允许导入 {imp} ({imp_layer}). "
                f"允许的依赖: {allowed}"
            )
    return violations
```

#### 2.2 Guardrails（护栏系统）

```python
# harness/guardrails.py
"""
多层护栏系统
"""

class HarnessGuardrails:
    """在 Agent 动作执行前/后进行验证"""

    # === Pre-execution 护栏 ===

    def pre_edit(self, file_path: str, old_text: str, new_text: str) -> str | None:
        """编辑前验证"""
        # 1. 确认文件已被读取
        if file_path not in self.read_files:
            return "❌ 必须先 read_file 再编辑。请先阅读该文件。"

        # 2. 语法检查（如果是代码文件）
        if file_path.endswith(".py"):
            try:
                compile(new_text, file_path, "exec")
            except SyntaxError as e:
                return f"❌ 新内容有语法错误: {e}. 请修复后重试。"

        # 3. 敏感文件保护
        protected = [".env", "secrets", "credentials", "private_key"]
        if any(p in file_path.lower() for p in protected):
            return f"⚠️ {file_path} 是敏感文件，需要人工确认。"

        return None  # 通过

    def pre_command(self, command: str) -> str | None:
        """命令执行前验证"""
        dangerous = ["rm -rf", "DROP TABLE", "git push --force", "sudo"]
        for d in dangerous:
            if d in command:
                return f"❌ 检测到危险命令 '{d}'，已阻止。请使用更安全的替代方案。"

        return None

    # === Post-execution 护栏 ===

    def post_edit(self, file_path: str, result: str) -> str | None:
        """编辑后验证"""
        # 自动运行 linter
        lint_result = self.run_linter(file_path)
        if lint_result.errors:
            return f"⚠️ 编辑引入了 {len(lint_result.errors)} 个 lint 错误: {lint_result.errors[:3]}"

        # 检查架构约束
        violations = validate_imports(file_path, extract_imports(file_path))
        if violations:
            return f"❌ 架构违规: {violations[0]}"

        return None
```

#### 2.3 用 Hooks 实现自动化护栏

在 Claude Code 中，通过 `settings.json` 配置 PostToolUse hooks：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "python3 harness/guardrails.py check-edit $FILE_PATH"
      },
      {
        "matcher": "Bash",
        "command": "python3 harness/guardrails.py check-command \"$COMMAND\""
      }
    ]
  }
}
```

---

### Phase 3：反馈循环与自我纠正（3-5天）

#### 3.1 验证循环（Verification Loop）

```
┌─────────────┐
│  Agent 执行  │
│  修改代码    │
└──────┬──────┘
       │
       ▼
┌─────────────┐    失败    ┌─────────────┐
│  自动验证    │──────────→│  生成修复建议 │
│  Lint+Test  │           │  重新执行    │
└──────┬──────┘           └──────┬──────┘
       │ 通过                     │
       ▼                         │
┌─────────────┐                  │
│  架构检查    │←─────────────────┘
│  约束验证    │
└──────┬──────┘
       │ 通过
       ▼
┌─────────────┐
│  提交结果    │
└─────────────┘
```

**实践代码**：

```python
# harness/verification_loop.py

MAX_RETRIES = 3

def verify_and_fix(agent, task_result):
    """验证 Agent 的输出，失败则自动修复"""
    for attempt in range(MAX_RETRIES):
        # Step 1: 运行测试
        test_result = run_tests()
        if test_result.all_passed:
            # Step 2: 架构检查
            arch_result = check_architecture()
            if arch_result.all_passed:
                return Success(task_result)

            # 架构违规 → 要求 Agent 修复
            agent.send(f"""
架构检查失败 (尝试 {attempt + 1}/{MAX_RETRIES}):
{arch_result.violations}

请修复这些架构违规，不要改变功能。
""")
        else:
            # 测试失败 → 要求 Agent 修复
            agent.send(f"""
测试失败 (尝试 {attempt + 1}/{MAX_RETRIES}):
{test_result.failures[:3]}

请修复失败的测试。修改实现代码，不要修改测试。
""")

    return Failure("超过最大重试次数")
```

#### 3.2 Generator-Evaluator 模式（Anthropic 实践）

```
┌──────────────┐         ┌──────────────┐
│  Generator   │────────→│  Evaluator   │
│  生成代码/设计 │         │  用Playwright │
│              │←────────│  测试并打分   │
│  根据反馈迭代  │  反馈    │              │
└──────────────┘         └──────────────┘
     5-15 轮迭代
```

```python
# harness/gen_eval_loop.py

def generator_evaluator_loop(task: str, max_iterations: int = 15):
    """Anthropic 的 Generator-Evaluator 模式"""

    # Generator: 生成代码
    generator = Agent(
        model="claude-sonnet-4-6",
        system_prompt="你是一个全栈开发者。根据需求生成代码。",
        tools=[read_file, edit_file, run_command],
    )

    # Evaluator: 评估结果
    evaluator = Agent(
        model="claude-sonnet-4-6",
        system_prompt="你是一个QA工程师。使用Playwright测试应用并打分(0-10)。",
        tools=[playwright_navigate, playwright_click, playwright_assert, screenshot],
    )

    for i in range(max_iterations):
        # 1. Generator 生成/修改代码
        gen_result = generator.run(task if i == 0 else f"""
上一轮评分: {score}/10
评估反馈: {eval_feedback}
请根据反馈改进代码。
""")

        # 2. Evaluator 测试并打分
        eval_result = evaluator.run(f"""
任务需求: {task}
请测试当前应用并给出评分(0-10)和具体反馈。
""")

        score = eval_result.score
        eval_feedback = eval_result.feedback

        # 3. 达到阈值则完成
        if score >= 8:
            return Success(gen_result, score=score, iterations=i+1)

        # 4. 策略性转向（如果连续3轮没有改善）
        if should_pivot(scores_history):
            generator.reset_context()  # 重置上下文，干净开始
            task = rephrase_task(task, eval_feedback)

    return Failure("未达到质量阈值")
```

---

### Phase 4：可观测性与轨迹记录（持续）

#### 4.1 轨迹日志

```python
# harness/observability.py
import json
from datetime import datetime

class TrajectoryLogger:
    """记录 Agent 的完整执行轨迹"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.trajectory = []
        self.start_time = datetime.now()
        self.total_tokens = 0
        self.total_cost = 0.0

    def log_step(self, step_type: str, data: dict):
        self.trajectory.append({
            "timestamp": datetime.now().isoformat(),
            "step": len(self.trajectory) + 1,
            "type": step_type,  # "think", "tool_call", "tool_result", "error"
            **data
        })

    def log_tool_call(self, tool_name: str, params: dict, result: str,
                      tokens_used: int, duration_ms: int):
        self.log_step("tool_call", {
            "tool": tool_name,
            "params": params,
            "result_preview": result[:500],
            "tokens": tokens_used,
            "duration_ms": duration_ms,
        })
        self.total_tokens += tokens_used

    def save(self):
        report = {
            "task_id": self.task_id,
            "total_steps": len(self.trajectory),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "trajectory": self.trajectory,
        }
        path = f"harness/logs/{self.task_id}.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return path
```

#### 4.2 监控仪表盘指标

```
关键指标（每次 Agent 运行必须记录）：
┌──────────────────────────────────────────┐
│ 任务完成率  │ 成功/总任务数               │
│ Token 消耗  │ 输入 tokens + 输出 tokens   │
│ 成本        │ 美元/任务                   │
│ 步骤数      │ 平均工具调用次数             │
│ 时间        │ 端到端耗时                  │
│ 重试次数    │ 验证循环的平均迭代           │
│ 错误类型    │ 按类型分类的失败原因          │
└──────────────────────────────────────────┘
```

---

### Phase 5：长时运行与跨 Session（持续）

#### 5.1 Anthropic 的双 Agent 模式

```
Session 1                    Session 2
┌──────────────┐            ┌──────────────┐
│ Initializer  │            │ Initializer  │
│ Agent        │            │ Agent        │
│ - 读取代码库  │            │ - 读取上次状态 │
│ - 制定计划    │            │ - 更新计划    │
│ - 写入计划文件│            │ - 传递给Coder │
└──────┬───────┘            └──────┬───────┘
       │                           │
       ▼                           ▼
┌──────────────┐            ┌──────────────┐
│ Coding Agent │            │ Coding Agent │
│ - 执行计划    │            │ - 继续执行    │
│ - 写代码     │            │ - 增量构建    │
│ - 运行测试   │            │ - 验证通过    │
└──────────────┘            └──────────────┘
       │                           │
       ▼                           ▼
  状态持久化到文件              读取持久化状态
  (plan.md, progress.json)    继续工作
```

#### 5.2 持久化状态文件

```markdown
# .harness/state/progress.json
{
  "task": "构建用户认证系统",
  "status": "in_progress",
  "phase": 2,
  "total_phases": 4,
  "completed_steps": [
    "创建数据库模型",
    "实现注册 API",
    "编写注册测试"
  ],
  "next_steps": [
    "实现登录 API",
    "实现 JWT token 生成",
    "编写登录测试"
  ],
  "blockers": [],
  "decisions_made": [
    "使用 bcrypt 而非 argon2（因为依赖更简单）",
    "JWT 过期时间设为 24 小时"
  ],
  "files_modified": [
    "src/models/user.py",
    "src/api/auth.py",
    "tests/test_auth.py"
  ],
  "last_updated": "2026-03-29T10:30:00Z"
}
```

#### 5.3 上下文重置策略

```
Anthropic 的关键发现：
  上下文压缩（Compaction）→ 保留"焦虑感"，Agent 变得犹豫
  上下文重置（Reset）     → 干净的起点，Agent 更果断

实践：
  ✅ 每完成一个 Phase，重置上下文 + 传递状态文件
  ❌ 不要在一个巨大的上下文中完成所有工作
```

---

## 四、Claude Code 中的 Harness Engineering 实践

你当前的 Claude Code 配置已经包含了 Harness 的大部分元素。以下是优化方向：

### 4.1 你已有的 Harness 组件

| Harness 层 | 你的现有实现 | 对应配置 |
|-----------|------------|---------|
| Action Space | Claude Code 内置工具 | Read, Edit, Write, Bash, Grep, Glob |
| 架构约束 | `~/.claude/rules/` | common/coding-style.md, patterns.md |
| 护栏 | rules 中的安全规则 | common/security.md |
| 工具编排 | Agent 子系统 | `~/.claude/agents/` |
| 反馈循环 | TDD 工作流 | common/testing.md |
| 可观测性 | Hooks 系统 | common/hooks.md |
| 长时运行 | Memory 系统 | `~/.claude/projects/*/memory/` |

### 4.2 推荐的增强点

```bash
# 1. 创建项目级 AGENTS.md
cat > AGENTS.md << 'EOF'
# 项目导航

## 目录结构
（简述核心目录和职责）

## 架构决策记录
（关键技术选型和原因）

## 工作约定
（编码规范、提交规范）

## 已知约束与陷阱
（容易出错的地方）
EOF

# 2. 创建 Harness 配置目录
mkdir -p .harness/{constraints,guardrails,logs,state}

# 3. 创建验证脚本
cat > .harness/verify.sh << 'EOF'
#!/bin/bash
# 每次代码修改后自动运行
echo "=== 运行验证循环 ==="
echo "1. Lint 检查..."
# ruff check . || exit 1
echo "2. 类型检查..."
# mypy . || exit 1
echo "3. 单元测试..."
# pytest tests/ -q || exit 1
echo "4. 架构约束..."
# python .harness/constraints/check.py || exit 1
echo "=== 验证通过 ✓ ==="
EOF
chmod +x .harness/verify.sh
```

### 4.3 在 settings.json 中集成 Harness Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "bash .harness/verify.sh"
      }
    ],
    "Stop": [
      {
        "command": "python3 .harness/save_trajectory.py"
      }
    ]
  }
}
```

---

## 五、Harness Engineering 反模式（避坑指南）

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **工具泛滥** | 给 Agent 100个工具 | 精选5-13个核心工具 |
| **原始输出** | 不格式化工具返回 | 结构化所有 Observation |
| **静默失败** | Agent 不知道工具调用失败 | 始终返回明确状态和错误信息 |
| **无限循环** | Agent 无限重试 | 设置步数、时间、成本上限 |
| **一个巨大上下文** | 在一个 session 中做所有事 | 分阶段，每阶段重置上下文 |
| **先改测试** | 测试失败就修改测试 | 修改实现，不修改测试 |
| **过度复杂** | 先建多 Agent 系统 | 从单 Agent + 好工具开始 |
| **忽略轨迹** | 只看最终结果 | 记录并分析完整执行轨迹 |

---

## 六、渐进式复杂度路线图

```
Week 1: 最小 Harness
  ├── AGENTS.md（项目导航）
  ├── 5-8 个精选工具
  ├── 基本 Observation 格式化
  └── 手动运行验证

Week 2-3: 自动化护栏
  ├── Lint/Test 自动验证
  ├── 架构约束检查
  ├── 危险操作拦截
  └── Hooks 集成

Week 4-6: 反馈循环
  ├── 验证循环自动化
  ├── Generator-Evaluator 模式
  ├── 轨迹日志
  └── 基本可观测性

Week 7+: 长时运行
  ├── 跨 Session 状态持久化
  ├── 上下文重置策略
  ├── 成本优化（模型路由）
  └── 持续评估（Eval 驱动开发）
```

---

## 七、Eval 驱动开发（EDD）

Harness Engineering 的最高形式是 **Eval 驱动开发**：

```
传统开发:  需求 → 代码 → 测试 → 部署
TDD:      需求 → 测试 → 代码 → 部署
EDD:      需求 → Eval → Harness → Agent → 自动验证 → 部署

Eval 是你对 Agent 行为的规格说明。
Harness 是让 Agent 满足 Eval 的基础设施。
```

**实践步骤**：

1. **定义 Eval**：明确"成功"是什么样的
   ```python
   eval = {
       "task": "修复 issue #42",
       "success_criteria": [
           "所有现有测试通过",
           "新增测试覆盖该 bug",
           "没有引入新的 lint 错误",
           "代码变更少于 50 行",
       ]
   }
   ```

2. **构建 Harness**：创建让 Agent 能满足 Eval 的环境

3. **运行 Agent**：让 Agent 在 Harness 中执行

4. **评估结果**：自动检查是否满足所有 success_criteria

5. **改进 Harness**：如果失败，改进 Harness（不是换模型）

---

## 八、关键参考资料

| 资源 | 重点 | 链接 |
|------|------|------|
| OpenAI - Harness Engineering | Codex 实践 | https://openai.com/index/harness-engineering/ |
| Anthropic - Effective Harnesses | 长时运行模式 | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| Anthropic - Harness Design | 单 Agent 设计 | https://www.anthropic.com/engineering/harness-design-long-running-apps |
| LangChain - Anatomy of Harness | 五层架构 | https://blog.langchain.com/the-anatomy-of-an-agent-harness/ |
| Martin Fowler - Harness Engineering | 概念分析 | https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html |
| Philipp Schmid - Agent Harness | 三大原则 | https://www.philschmid.de/agent-harness-2026 |
| SWE-agent | Action Space 设计 | https://swe-agent.com/ |
| EleutherAI lm-eval | 评估框架 | https://github.com/EleutherAI/lm-evaluation-harness |

---

*最重要的一句话：**改进 Harness 的 ROI 通常高于换更大的模型。** 先优化 Harness，再考虑升级模型。*
