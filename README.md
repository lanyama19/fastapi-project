# FastAPI Project

A simple CRUD API built with FastAPI, SQLAlchemy, and Pydantic (v2), backed by PostgreSQL. It exposes posts and users endpoints, with password hashing for users.

## Tech Stack
- FastAPI: HTTP API and routing with `APIRouter`.
- Pydantic v2: Request/response models and validation.
- SQLAlchemy ORM: Database models and DB interactions.
- Psycopg (psycopg3): PostgreSQL driver (plus a small direct check in `main.py`).
- Passlib + Bcrypt: Password hashing for users.
- PostgreSQL: Relational database.
- Uvicorn: ASGI server for local development.

## Features
- Posts CRUD: create, list, get by id, update, delete.
- Users: create user with hashed password, get user by id.
- Router-based structure with prefixes: `/posts` and `/users`.
- Strong typing and validation via Pydantic schemas.
- Demo endpoint for the latest in-memory post.

## Project Structure
```
app/
  __init__.py         # Package marker
  main.py             # FastAPI app, includes routers, table creation, demo
  models.py           # SQLAlchemy ORM models (Post, User)
  database.py         # Engine/session setup and `get_db` dependency
  schemas.py          # Pydantic schemas for requests/responses
  utils.py            # Password hashing via Passlib (bcrypt)
  routers/
    post.py           # Posts endpoints (CRUD)
    user.py           # Users endpoints (create, get)
README.md             # This file
```

## What Each Python File Does
- `app/main.py`: Creates the FastAPI app, includes `routers.post` and `routers.user`, defines `/` and demo `/posts/latest`, and creates tables via `models.Base.metadata.create_all(bind=engine)`.
- `app/routers/post.py`: Posts CRUD implemented with SQLAlchemy session dependency.
- `app/routers/user.py`: User creation with hashed password and fetch-by-id.
- `app/utils.py`: Password hashing using Passlib’s `CryptContext` with bcrypt.
- `app/models.py`: ORM models for `posts` and `users` with timestamps/defaults.
- `app/database.py`: SQLAlchemy engine, `SessionLocal`, `Base`, and the `get_db` dependency.
- `app/schemas.py`: Pydantic models for posts and users (e.g., `PostCreate`, `Post`, `UserCreate`, `UserOut`).

## API Endpoints (Summary)
- GET `/` — Health/welcome message
- Posts
  - GET `/posts` — List posts
  - POST `/posts` — Create a post
  - GET `/posts/{id}` — Get a post by id
  - PUT `/posts/{id}` — Update a post by id
  - DELETE `/posts/{id}` — Delete a post by id
  - GET `/posts/latest` — Demo endpoint returning the last in-memory post
- Users
  - POST `/users` — Create user (password hashed)
  - GET `/users/{id}` — Get user by id

Request/response payloads follow the Pydantic models in `app/schemas.py`.

## Local Setup
1) Python env
- Python 3.10+ recommended.
- Create and activate a virtualenv (optional):
  - Windows (PowerShell): `python -m venv .venv; .venv\Scripts\Activate.ps1`
  - Unix/macOS: `python -m venv .venv && source .venv/bin/activate`

2) Install dependencies
- Using pinned versions: `pip install -r requirements.txt`
- Or minimal manual install:
```
pip install fastapi uvicorn sqlalchemy psycopg passlib[bcrypt]
```

3) Configure database
- Ensure a PostgreSQL instance is running and a database named `fastapi` exists.
- Default SQLAlchemy URL in `app/database.py`:
  `postgresql+psycopg://postgres:123@localhost/fastapi`
- Update it if your credentials or DB name differ.

4) Create tables (auto)
- On app start, `models.Base.metadata.create_all(bind=engine)` creates missing tables.

## Run
- Start the server (auto-reload in dev):
```
uvicorn app.main:app --reload
```
- Open docs: http://127.0.0.1:8000/docs

## Example Payloads
- Create/Update post body:
```
{
  "title": "Hello",
  "content": "World",
  "published": true
}
```
- Create user body:
```
{
  "email": "user@example.com",
  "password": "supersecret"
}
```

## Recent Changes
- Split routes into `app/routers/{post,user}.py` with `APIRouter` prefixes.
- Added `User` model and user endpoints.
- Added password hashing via Passlib (bcrypt) in `app/utils.py`.
- Consolidated CRUD on SQLAlchemy ORM and fixed update behavior.

## Notes
- Uses SQLAlchemy ORM for CRUD; `main.py` also contains a minimal direct psycopg connection for connectivity check.
- For PATCH-like partial updates, adapt the update endpoint to use `exclude_unset=True` with Pydantic.

## License
MIT (or your preferred license).
