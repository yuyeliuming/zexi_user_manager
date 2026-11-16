# 择栖工作室 2026 招新题 - 用户管理系统 (重构版)

这是一个基于 Python 开发的 RESTful 用户管理系统。在完成必做题的前提下，全面实现了所有的选做题及挑战题（JWT 认证、密码哈希加盐、防并发竞态、分层日志记录）。

##  快速启动

### 1. 环境要求

- Python 3.10 及以上（推荐 3.11/3.13）
- 以下命令以 Windows PowerShell 为例，macOS/Linux 使用对应的激活命令

### 2. 安装依赖

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

如果 PowerShell 提示禁止运行脚本，可仅对当前终端临时放开：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

### 3. 配置 JWT 密钥

程序启动时会从 `.env` 读取 `JWT_SECRET_KEY`；未配置会直接抛出 `RuntimeError`，无法启动。`.env` 已被 `.gitignore` 忽略，不要提交真实密钥。

如果项目里还没有 `.env`，从模板复制；**已有 `.env` 时请跳过复制，直接编辑原文件，避免覆盖已有密钥**。

Windows：

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

macOS/Linux：

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

把命令输出的随机字符串填入 `.env` 中 `JWT_SECRET_KEY=` 的后面（不要保留空值）：

```dotenv
JWT_SECRET_KEY=这里替换成刚才生成的随机字符串
```

### 4. 启动服务

保持终端位于项目根目录，执行：

```powershell
python -m uvicorn main:app --reload
```

启动后可访问：

- 服务地址：<http://127.0.0.1:8000>
- Swagger 接口文档：<http://127.0.0.1:8000/docs>

首次启动会自动创建 `user.db` 和 `app.log`。由于数据库使用相对路径，请在项目根目录启动；如果 8000 端口被占用，可加 `--port 8001` 换端口。

### 5. 可选：运行并发抢注脚本

先保持服务运行，再新开一个终端执行：

```powershell
python test_race.py
```

该脚本依赖 `requirements.txt` 中的 `requests`。

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
- `.env.example`: JWT 密钥配置模板（复制为 `.env` 后填写）
- `requirements.txt`: 项目依赖

##  核心亮点

1. **安全可靠的密码存储**：绝不存储明文。使用 `hashlib.pbkdf2_hmac` 算法配合随机盐值，并使用 `hmac.compare_digest` 防止时序攻击。
2. **JWT 身份认证**：使用 HS256 算法签发 Token。统一拦截鉴权失败（未携带、伪造、过期），对外统一返回 401，对内记录详细日志。
3. **并发控制**：利用数据库 `UNIQUE` 约束和捕获 `IntegrityError` 处理并发注册/改名冲突；通过 `cursor.rowcount == 0` 校验处理并发注销导致的幽灵数据修改。
4. **分层日志**：记录关键业务流转（登录成功/失败、修改密码、鉴权拦截），包含时间戳与用户标识，且绝不包含密码等敏感信息。

