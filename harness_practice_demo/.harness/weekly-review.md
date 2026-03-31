## 2026-03-29

### 发现的问题
- CLAUDE.md 在 Phase 1 执行后未同步更新项目结构 → 在文件对应关系中新增"改模块需更新 CLAUDE.md"规则
- ruff 发现未使用导入，缺少自动 lint hook → 建议配置 PostEditFile lint hook
- 缺少认证模块的架构规则 → 补充 JWT/密码哈希集中到 auth.py 的规则
- 缺少 .gitignore → 新增 .gitignore 防止数据库文件提交

### CLAUDE.md 更新
- 新增：`app/auth.py` 到项目结构
- 新增：认证相关架构规则（JWT 集中管理、get_current_user 依赖）
- 新增：安全相关禁止事项（禁止日志输出敏感信息）
- 新增：文件对应关系中"改模块需更新 CLAUDE.md"
- 修改：Python 3.9 兼容性规则更具体

### Hook 更新
- 建议配置 PostEditFile lint hook（ruff check），尚未落地到 settings.json
- 建议配置 PostEditFile test hook（pytest），尚未落地到 settings.json
