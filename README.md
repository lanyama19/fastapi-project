# FastAPI Project

FastAPI + SQLAlchemy + PostgreSQL demo API with JWT auth and vote aggregation. Posts endpoints include vote counts using a LEFT JOIN + GROUP BY.

## Tech Stack
- FastAPI: routing with `APIRouter` and dependency injection
- Pydantic v2: request/response models and validation
- SQLAlchemy ORM: models and DB access; `func.count` for aggregations
- Psycopg (psycopg3): PostgreSQL driver
- Passlib + Bcrypt: password hashing
- Alembic: database migrations
- Uvicorn: ASGI server for development

## Features
- Auth: OAuth2 password flow + JWT (login returns an access token)
- Users: register and fetch user
- Posts: CRUD + search/pagination; only published posts listed
- Votes: like/unlike via composite key (user_id, post_id)
- Aggregation: `GET /posts` and `GET /posts/{id}` include a `votes` count

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

## Alembic (optional)
Initialize and run migrations:
```
alembic init alembic
# configure alembic.ini and alembic/env.py to use your SQLAlchemy URL and models Base
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Recent Changes
- posts: include vote counts; fix vote dependency
- docs: add alembic and install instructions
- docs: polish README content

## License
MIT (or your preferred license)
