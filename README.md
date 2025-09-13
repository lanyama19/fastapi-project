# FastAPI Project

FastAPI + SQLAlchemy + PostgreSQL demo API with JWT auth and vote aggregation. Posts endpoints include vote counts using a LEFT JOIN + GROUP BY.

## Tech Stack
- FastAPI: routing with `APIRouter` and dependency injection
- Starlette: underlying ASGI toolkit
- Pydantic v2: request/response models and validation
- SQLAlchemy 2.x ORM: models and DB access; `func.count` for aggregations
- Psycopg 3: PostgreSQL driver
- Passlib + Bcrypt: password hashing
- Alembic: database migrations (auto-run on container start)
- Uvicorn: ASGI server
- Docker & Docker Compose: local dev and packaging
- Render: optional deployment target (Web Service)

## Features
- Auth: OAuth2 password flow + JWT (login returns an access token)
- Users: register and fetch user
- Posts: CRUD + search/pagination; only published posts listed
- Votes: like/unlike via composite key (user_id, post_id)
- Aggregation: `GET /posts` and `GET /posts/{id}` include a `votes` count
- CORS: permissive defaults for easy local testing
- Migrations: Alembic runs automatically at container start to ensure tables exist
- Dockerized dev: `docker compose up --build` to start API + Postgres

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
- PostWithVotes: `{ "post": Post, "votes": int }` used by posts list and detail responses

## Endpoints (summary)
- Auth
  - POST `/login` -> returns `access_token`
- Users
  - POST `/users` -> register user
  - GET `/users/{id}` -> fetch user
- Posts (requires auth)
  - GET `/posts` -> returns `List[PostWithVotes]`
  - GET `/posts/{id}` -> returns `PostWithVotes`
  - POST `/posts` -> create post
  - PUT `/posts/{id}` -> update post
  - DELETE `/posts/{id}` -> delete post
- Votes (requires auth)
  - POST `/vote` -> body `{ "post_id": int, "dir": 1|0 }` (1=vote, 0=unvote)

## Setup
1) Python env
- Python 3.10+
- Windows: `python -m venv .venv; .venv\Scripts\Activate.ps1`
- Unix/macOS: `python -m venv .venv && source .venv/bin/activate`

2) Install dependencies
- `pip install -r requirements.txt`

Or minimal manual install:
```
pip install fastapi uvicorn sqlalchemy psycopg passlib[bcrypt] python-jose[cryptography] email-validator pydantic-settings alembic
```

3) Configure database
- Use `.env` to provide DB settings consumed by `app/config.py`
- SQLAlchemy URL format: `postgresql+psycopg://user:pass@host:port/dbname`

4) Run
```
uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Deploy on Render (Backend)

1) Create service
- Push code to GitHub. In Render, create a New Web Service and connect this repo.

2) Basic settings
- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `bash ./start.sh`

3) Environment variables (required)
- `database_hostname`, `database_port`, `database_name`, `database_username`, `database_password`
- `secret_key`, `algorithm`, `access_token_expire_minutes`
  These are read by `app/config.py` (Pydantic Settings). UPPERCASE variants also work.

4) Migrations
- Automatically handled by `start.sh` via `alembic upgrade head` with retries (useful for free instances).
- Optional: run manually from Render Shell if needed: `alembic upgrade head`.

5) Verify
- Open the service URL and check `/docs` for the interactive API.

Notes
- Free instance cold starts can delay DB availability. Tune retries via:
  - `ALEMBIC_RETRIES` (default `10`)
  - `ALEMBIC_RETRY_DELAY` seconds (default `3`)

## Alembic: Usage Recommendations

Configuration

- Set DB URL: in `alembic.ini`, either fill `sqlalchemy.url` or leave it blank and provide `DATABASE_URL` via env; both are supported by Alembic.
- Bind models: in `alembic/env.py`, import your metadata and set `target_metadata` to it, e.g. `from app.models import Base; target_metadata = Base.metadata`.
- Autogenerate safety: always review generated diffs in `alembic/versions/*.py` before upgrading; avoid destructive changes in production without backups.

Basic CLI (<= 6 commands)

```
# 1) Initialize (only if starting fresh)
alembic init alembic

# 2) Create a migration from model changes
alembic revision --autogenerate -m "describe change"

# 3) Apply migrations to latest
alembic upgrade head

# 4) Roll back last migration
alembic downgrade -1

# 5) Show migration history
alembic history

# 6) Show current DB revision
alembic current
```

Tips

- One head: keep a single linear history; avoid parallel heads by syncing with main before creating revisions.
- Deterministic migrations: prefer explicit server defaults and non-null backfills to keep online upgrades safe.
- Don't edit applied revisions: instead, add a new corrective migration.

## Recent Changes
- docker: run Alembic on container start before launching Uvicorn
- docker-compose: load `.env` correctly and add `depends_on: [postgres]`
- docs: add Docker setup/commands and Docker Hub push section
- posts: include vote counts; fix vote dependency in queries
- docs: improve Ubuntu VM link rendering

## Ubuntu VM Deployment
- For instructions on configuring this app on an Ubuntu 22.04 VM (GCP), see:
  - [DEPLOYMENT.md](./DEPLOYMENT.md)

## Docker: Setup, Commands, and Push

Prerequisites

- Docker Desktop 4.x+
- Docker Compose v2 (comes with Docker Desktop; use `docker compose` not `docker-compose`)

Configuration

- Environment file: copy `.env` and set your values. When using Compose, set `DATABASE_HOSTNAME=postgres` so the API container can reach the Postgres service by name.
- Compose file: `docker-compose.yml` defines two services:
  - `api`: builds this repo and exposes `8000`.
  - `postgres`: official `postgres:17` with a persistent volume.
- Migrations: the container entrypoint runs `alembic -c alembic.ini upgrade head` before starting Uvicorn, so tables are created/updated automatically.

Build and Run

```
# From the repo root
docker compose up --build

# Run in background
docker compose up -d --build

# Stop and remove containers (keep volume)
docker compose down

# Stop and also remove the postgres volume (clears DB data)
docker compose down -v
```

Verify

- Open docs: http://localhost:8000/docs
- Example request (create user):
```
curl -X POST http://localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret"}'
```

Useful Commands

```
# Show service status
docker compose ps

# Tail API logs
docker compose logs -f api

# Exec into running API container (shell)
docker exec -it fastapi-project-api-1 sh

# Run Alembic inside API container (if needed)
docker exec -it fastapi-project-api-1 alembic -c alembic.ini upgrade head
```

Push Image to Docker Hub

Option A — single-step build and push with your tag:
```
# Log in (once)
docker login

# Build image tagged for Docker Hub
docker build -t <DOCKERHUB_USER>/fastapi-project:latest .

# Push
docker push <DOCKERHUB_USER>/fastapi-project:latest
```

Option B — build via Compose, then tag and push:
```
# Build the api image as defined in compose
docker compose build api

# Find the local image name (commonly 'fastapi-project-api')
docker images | grep fastapi-project

# Tag it for Docker Hub
docker tag fastapi-project-api <DOCKERHUB_USER>/fastapi-project:latest

# Push
docker push <DOCKERHUB_USER>/fastapi-project:latest
```

Notes

- Ports: the API is published on `localhost:8000`.
- Env propagation: Compose reads `.env`; Alembic uses `alembic.ini` + `alembic/env.py` which constructs the DB URL from `app.config.Settings`.
- If the DB starts slowly and migrations fail at first boot, re-run `docker compose up` or use `docker compose logs -f postgres` to ensure readiness.

## License
MIT (or your preferred license)
