# 择栖工作室 2026 招新题 - 用户管理系统 (重构版)

这是一个基于 Python 开发的 RESTful 用户管理系统。在完成必做题的前提下，全面实现了所有的选做题及挑战题（JWT 认证、密码哈希加盐、防并发竞态、分层日志记录）。

##  技术栈
- **Web 框架**：FastAPI
- **数据校验**：Pydantic v2
- **数据库**：SQLite
- **安全认证**：PyJWT, PBKDF2-HMAC-SHA256
- **日志管理**：Python `logging`

##  项目结构
- `main.py`: FastAPI 路由与业务逻辑
- `schemas.py`: Pydantic 数据校验模型
- `database.py`: 数据库初始化与密码安全哈希
- `security.py`: JWT 生成与鉴权依赖注入
- `logger.py`: 全局日志配置模块
- `test_race.py`: 并发抢注测试脚本 (多线程)
- `search.py`: 查询数据库，核对检索结果和检验密码存储方式(非主体业务)
- `requirements.txt`: 项目依赖

##  核心亮点

1. **安全可靠的密码存储**：绝不存储明文。使用 `hashlib.pbkdf2_hmac` 算法配合随机盐值，并使用 `hmac.compare_digest` 防止时序攻击。
2. **JWT 身份认证**：使用 HS256 算法签发 Token。统一拦截鉴权失败（未携带、伪造、过期），对外统一返回 401，对内记录详细日志。
3. **并发控制**：利用数据库 `UNIQUE` 约束和捕获 `IntegrityError` 处理并发注册/改名冲突；通过 `cursor.rowcount == 0` 校验处理并发注销导致的幽灵数据修改。
4. **分层日志**：记录关键业务流转（登录成功/失败、修改密码、鉴权拦截），包含时间戳与用户标识，且绝不包含密码等敏感信息。

