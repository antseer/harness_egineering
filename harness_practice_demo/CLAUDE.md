# CLAUDE.md

## 项目结构

- `app/main.py` — FastAPI 入口，注册路由
- `app/config.py` — 配置（Pydantic Settings，环境变量前缀 `TASK_`）
- `app/database.py` — SQLAlchemy 引擎、Session、Base
- `app/auth.py` — 认证工具（密码哈希、JWT 生成/验证、get_current_user 依赖）
- `app/models/` — SQLAlchemy ORM 模型（task.py, user.py）
- `app/schemas/` — Pydantic 请求/响应 Schema（task.py, user.py）
- `app/api/` — 路由模块：tasks.py（任务 CRUD）、auth.py（注册/登录）
- `tests/` — pytest 测试，conftest.py 提供 client fixture 和独立测试数据库

## 常用命令

```bash
uvicorn app.main:app --reload          # 启动开发服务器
pytest tests/ -x --tb=short            # 运行全部测试
pytest tests/test_auth.py -x --tb=short  # 运行单个测试文件
ruff check .                           # Lint 检查
ruff check . --fix                     # Lint 自动修复
```

## 架构规则（必须遵守）

- 禁止在 `app/api/` 路由中直接写数据库查询逻辑超过 3 行——复杂查询抽到 service 层
- 禁止在 Schema 中导入 ORM 模型——Schema 层不依赖 Model 层
- 禁止在 models/ 中导入 fastapi 或 schemas——Model 层不依赖 API 层
- 所有 API 路由通过 `app.include_router()` 注册，前缀统一 `/api/v1`
- 禁止在 `app/auth.py` 以外的地方创建 JWT 或操作密码哈希
- 需要当前用户的路由必须使用 `Depends(get_current_user)` 而非自行解析 token

## 文件对应关系

- 新增 Model → 必须同步新增 Schema + 路由 + 测试
- 新增路由文件 → 必须在 `app/main.py` 中注册 router
- 修改 Model 字段 → 必须同步更新对应 Schema 和测试
- 新增/删除模块文件 → 必须更新本文件（CLAUDE.md）的项目结构部分

## 禁止事项

- 禁止提交 `*.db` 数据库文件（已在 .gitignore）
- 禁止硬编码数据库连接字符串或 JWT secret_key——通过 `app/config.py` Settings 读取
- 禁止在日志或错误信息中输出密码、token、secret_key
- 禁止使用 `str | None` 语法——Python 3.9 必须用 `from __future__ import annotations` + `Optional[str]`
