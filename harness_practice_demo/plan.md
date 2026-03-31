# 计划：用户认证功能（注册 + 登录 + JWT）

> 执行方式：每个 Phase 开一个新会话，开头说"读 plan.md，继续"。
> 每个 Phase 结束前更新本文件的进度和决策记录。

**目标**：为任务管理 API 添加用户注册、登录和基于 JWT 的认证保护
**技术方案**：使用 passlib 做密码哈希，python-jose 生成/验证 JWT token，新增 User 模型和认证路由，对现有 Task 路由添加认证依赖
**预估 Phase 数**：3

---

## Phase 1: 用户模型与注册/登录 API [状态: 已完成]

### 任务
- [x] 安装依赖：在 `pyproject.toml` 中添加 `passlib[bcrypt]` 和 `python-jose[cryptography]`
- [x] 创建用户模型 `app/models/user.py`（字段：id, username, email, hashed_password, is_active, created_at）
- [x] 创建用户 Schema `app/schemas/user.py`（UserCreate, UserResponse, Token, TokenData）
- [x] 创建认证工具模块 `app/auth.py`（密码哈希、JWT 生成/验证、当前用户依赖）
- [x] 在 `app/config.py` 中添加 JWT 配置（SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES）
- [x] 创建认证路由 `app/api/auth.py`（POST /register, POST /login）
- [x] 在 `app/main.py` 中注册 auth router
- [x] 编写测试 `tests/test_auth.py`（注册成功、重复注册、登录成功、登录失败）
- [x] 验证：运行 `pytest tests/ -x --tb=short` 确认全部通过（13 passed）

### 交付物
- `app/models/user.py` — User ORM 模型
- `app/schemas/user.py` — 用户相关 Schema
- `app/auth.py` — 认证工具函数
- `app/api/auth.py` — 认证路由
- `tests/test_auth.py` — 认证测试

### 验证标准
- `pytest tests/ -x --tb=short` 全部通过
- `ruff check .` 无错误
- POST `/api/v1/auth/register` 可创建用户
- POST `/api/v1/auth/login` 可返回 JWT token

---

## Phase 2: 任务与用户关联 + 路由保护 [状态: 待做]

### 任务
- [ ] 修改 `app/models/task.py`：添加 `owner_id` 外键关联 User
- [ ] 修改 `app/schemas/task.py`：TaskResponse 添加 `owner_id` 字段
- [ ] 修改 `app/api/tasks.py`：所有路由添加 `current_user` 依赖，任务按用户隔离
- [ ] 更新 `tests/conftest.py`：添加 `authenticated_client` fixture
- [ ] 更新 `tests/test_tasks.py`：所有测试使用认证客户端
- [ ] 验证：运行 `pytest tests/ -x --tb=short` 确认全部通过

### 交付物
- 修改后的 Task 模型（含 owner_id）
- 受保护的 Task 路由
- 更新后的测试

### 验证标准
- `pytest tests/ -x --tb=short` 全部通过
- `ruff check .` 无错误
- 未认证请求 Task API 返回 401
- 用户只能看到自己的任务

---

## Phase 3: 安全加固与收尾 [状态: 待做]

### 任务
- [ ] 添加 token 刷新接口 `POST /api/v1/auth/refresh`
- [ ] 添加获取当前用户信息接口 `GET /api/v1/auth/me`
- [ ] 为敏感接口添加速率限制说明（在 CLAUDE.md 中记录）
- [ ] 补充测试：token 过期、无效 token、refresh 流程
- [ ] 更新 CLAUDE.md 反映新的项目结构
- [ ] 验证：运行 `pytest tests/ -x --tb=short` 确认全部通过

### 交付物
- 完整的认证系统
- 更新后的 CLAUDE.md
- 全面的测试覆盖

### 验证标准
- `pytest tests/ -x --tb=short` 全部通过
- `ruff check .` 无错误
- 所有认证流程（注册→登录→访问受保护资源→刷新 token）可正常运行

---

## 决策记录
- 登录接口使用 JSON body（UserCreate schema）而非 OAuth2 表单 -- 保持 API 风格一致，前端更方便调用 -- 2026-03-29
- 使用 passlib bcrypt 而非 argon2 -- bcrypt 足够安全且依赖更轻 -- 2026-03-29
- JWT secret_key 默认值为 dev-secret-key，通过环境变量 TASK_SECRET_KEY 覆盖 -- 开发便利同时提醒生产需更换 -- 2026-03-29

## 已知问题
- ruff 检查发现未使用的 EmailStr 导入，已修复
- Python 3.9 不支持 `str | None` 语法，需使用 `from __future__ import annotations` + `Optional`

## 文件变更清单
### Phase 1
- 修改: `pyproject.toml`（添加 passlib、python-jose 依赖）
- 修改: `app/config.py`（添加 JWT 配置字段）
- 修改: `app/main.py`（注册 auth router）
- 新增: `app/models/user.py`
- 新增: `app/schemas/user.py`
- 新增: `app/auth.py`
- 新增: `app/api/auth.py`
- 新增: `tests/test_auth.py`
