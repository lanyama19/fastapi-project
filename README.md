# FastAPI Project

FastAPI + SQLAlchemy + PostgreSQL demo API with JWT auth and vote aggregation. Posts endpoints now return vote counts via a LEFT JOIN + GROUP BY.

## Tech Stack
- FastAPI: routing with `APIRouter` and dependency injection.
- Pydantic v2: request/response models and validation.
- SQLAlchemy ORM: models and DB access; `func.count` for aggregations.
- Psycopg (psycopg3): PostgreSQL driver.
- Passlib + Bcrypt: password hashing.
- Alembic: migrations (installed; optional setup below).
- Uvicorn: ASGI server for development.

## Features
- Auth: OAuth2 password flow + JWT（登录获取 token）
- Users: register and fetch user
- Posts: CRUD + search/pagination; only published posts listed
- Votes: like/unlike via composite key（user_id, post_id）
- Aggregation: `GET /posts` 与 `GET /posts/{id}` 返回投票数（`votes`）

## Project Structure
```
app/
  __init__.py
  main.py
  models.py
  database.py
  schemas.py
  utils.py
  config.py
  routers/
    post.py
    user.py
    auth.py
    vote.py
alembic/
  env.py
  script.py.mako
  versions/
README.md
requirements.txt
alembic.ini
```

## Data Models & Responses
- PostWithVotes: `{ "post": Post, "votes": int }` 用于帖子列表与详情响应。

## Endpoints（摘要）
- Auth
  - POST `/login` → 返回 `access_token`
- Users
  - POST `/users` → 注册
  - GET `/users/{id}` → 查询
- Posts（需认证）
  - GET `/posts` → 返回 `List[PostWithVotes]`
  - GET `/posts/{id}` → 返回 `PostWithVotes`
  - POST `/posts` → 创建帖子
  - PUT `/posts/{id}` → 更新帖子
  - DELETE `/posts/{id}` → 删除帖子
- Votes（需认证）
  - POST `/vote` → `{"post_id": int, "dir": 1|0}`（1=投票，0=取消）

## Setup
1) Python env
- Python 3.10+
- Windows: `python -m venv .venv; .venv\Scripts\Activate.ps1`
- Unix/macOS: `python -m venv .venv && source .venv/bin/activate`

2) Install deps
- `pip install -r requirements.txt`

Or minimal manual install:
```
pip install fastapi uvicorn sqlalchemy psycopg passlib[bcrypt] python-jose[cryptography] email-validator pydantic-settings alembic
```

3) Configure DB
- 使用环境变量（`.env`）配置数据库连接（见 `app/config.py`）。
- SQLAlchemy 连接格式：`postgresql+psycopg://user:pass@host:port/dbname`

4) Run
```
uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Alembic（可选）
初始化并生成迁移：
```
alembic init alembic
# 配置 alembic.ini 与 env.py 指向 SQLAlchemy URL 和 Base
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Recent Changes
- posts: include vote counts; fix vote dependency

## License
MIT (or your preferred license)
