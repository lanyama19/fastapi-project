# FastAPI Project

A simple CRUD API for managing posts built with FastAPI, SQLAlchemy, and Pydantic, backed by PostgreSQL. It exposes endpoints to create, read, update, and delete posts.

## Tech Stack
- FastAPI: Web framework for building the HTTP API and routing.
- Pydantic (v2-style): Request/response models and validation.
- SQLAlchemy ORM: Database ORM for models and DB interactions.
- Psycopg (psycopg3): PostgreSQL driver used by SQLAlchemy (and a small direct connection in `main.py`).
- PostgreSQL: Relational database.
- Uvicorn: ASGI server to run the app (for local dev).

## Features
- CRUD for posts: create, list, get by id, update, delete.
- Strong typing and validation via Pydantic schemas.
- SQLAlchemy ORM model for the `posts` table with timestamps and defaults.
- Simple demo endpoint for the "latest" in-memory post.

## Project Structure
```
app/
  __init__.py         # Package marker
  main.py             # FastAPI app, routes, table creation, demo code
  models.py           # SQLAlchemy ORM models (Post)
  database.py         # Engine/session setup and `get_db` dependency
  schemas.py          # Pydantic schemas for requests/responses
.vscode/              # Editor settings (optional)
.venv/                # (Local virtualenv, not required in prod)
README.md             # This file
```

## What Each Python File Does
- app/main.py: Defines the FastAPI application and all HTTP endpoints. Uses SQLAlchemy session dependency for DB CRUD. Also creates tables at startup via `models.Base.metadata.create_all(bind=engine)` and contains a tiny in-memory demo list used by `/posts/latest`.
- app/models.py: SQLAlchemy ORM definitions. Contains the `Post` model mapped to the `posts` table with fields: `id`, `title`, `content`, `published`, `created_at`.
- app/database.py: Database configuration for SQLAlchemy. Creates the engine, session factory (`SessionLocal`), base class (`Base`), and the `get_db` dependency used by routes.
- app/schemas.py: Pydantic models that shape and validate API inputs/outputs. `PostBase` (shared fields), `PostCreate` (request body), `Post` (response with `id` and `created_at`, and `orm_mode` enabled).
- app/__init__.py: Empty package initializer.

## API Endpoints (Summary)
- GET `/` → Health/welcome message
- GET `/posts` → List posts
- POST `/posts` → Create a post
- GET `/posts/{id}` → Get a post by id
- PUT `/posts/{id}` → Update a post by id
- DELETE `/posts/{id}` → Delete a post by id
- GET `/posts/latest` → Demo endpoint returning the last in-memory post

Request/response payloads follow the Pydantic models in `app/schemas.py`.

## Local Setup
1) Python env
- Python 3.10+ recommended.
- Create and activate a virtualenv (optional):
  - Windows (PowerShell): `python -m venv .venv; .venv\\Scripts\\Activate.ps1`
  - Unix/macOS: `python -m venv .venv && source .venv/bin/activate`

2) Install dependencies
```
pip install fastapi uvicorn sqlalchemy psycopg
```

3) Configure database
- Ensure a PostgreSQL instance is running and a database named `fastapi` exists.
- The default connection string is in `app/database.py`:
  `postgresql+psycopg://postgres:123@localhost/fastapi`
- Update it if your credentials or DB name differ.

4) Create tables (auto)
- On app start, `models.Base.metadata.create_all(bind=engine)` creates the `posts` table if missing.

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

## Notes
- This project uses SQLAlchemy ORM for CRUD; there is also a minimal direct psycopg connection in `main.py` used only for a connectivity printout.
- For partial updates (PATCH-style), you can adapt the update endpoint to use `exclude_unset=True` with Pydantic.

## License
MIT (or your preferred license).
