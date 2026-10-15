# URL Shortener — Python & FastAPI

A high-performance, production-ready URL shortener built with FastAPI, PostgreSQL, and Redis.

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 (async via asyncpg + SQLAlchemy 2.0) |
| Cache / Rate Limiter | Redis 7 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Testing | Pytest + pytest-asyncio + httpx |

## Project Structure

```
url_shortner/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point & lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # DB & Redis injectors
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── health.py      # GET /health
│   │           ├── shorten.py     # POST /api/v1/shorten   [Module 3]
│   │           ├── redirect.py    # GET /{short_code}       [Module 4]
│   │           └── analytics.py   # GET /api/v1/stats/...  [Module 5]
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Pydantic BaseSettings (.env loader)
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py             # Async engine, session & Redis client
│   ├── models/
│   │   ├── __init__.py
│   │   └── url.py                 # urls & click_analytics ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── url.py                 # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── keygen.py              # Base62 / Sqids key generator [Module 2]
│   └── utils/
│       ├── __init__.py
│       └── validators.py          # Reserved word & loop-prevention checks
├── alembic/
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   └── test_keygen.py
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Quick Start (Module 1)

### 1. Start services

```bash
docker compose up -d
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to explore the Swagger UI.
Test the health endpoint: http://localhost:8000/health

## Modules

| Module | Focus | Status |
|---|---|---|
| 1 | Foundation & DB Layer | ✅ In Progress |
| 2 | Key Generation Engine | ⏳ Pending |
| 3 | URL Shortening Write API | ⏳ Pending |
| 4 | Redirect & Cache Read Service | ⏳ Pending |
| 5 | Async Click Analytics | ⏳ Pending |
| 6 | Security, Rate Limiting & UI | ⏳ Pending |
