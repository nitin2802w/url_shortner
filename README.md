# ✂️ SHRINK — URL Shortener

A full-stack, production-ready URL shortener built with **FastAPI**, **PostgreSQL**, **Redis**, and **React**. Shortens long URLs into clean branded links, tracks click analytics per redirect, and enforces rate limiting — all without slowing down the user's redirect experience.

**Live Demo:**
- 🌐 Frontend: [Vercel](https://vercel.com) *(deploy your own — see below)*
- ⚙️ Backend API: `https://url-shortner-kexm.onrender.com`
- 📖 Swagger Docs: `https://url-shortner-kexm.onrender.com/docs`

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Local Development](#-local-development)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)

---

## 🛠 Tech Stack

### Backend
| Layer | Technology | Purpose |
|---|---|---|
| Web Framework | **FastAPI** + Uvicorn | Async HTTP server, OpenAPI docs |
| Database | **PostgreSQL 16** (asyncpg + SQLAlchemy 2.0) | Persistent URL & analytics storage |
| Cache | **Redis 7** | Sub-millisecond redirect lookups |
| Migrations | **Alembic** | Schema versioning |
| Validation | **Pydantic v2** | Request/response validation & settings |
| Rate Limiting | **SlowAPI** | 10 requests/min per IP on shorten endpoint |
| Containerisation | **Docker** + Docker Compose | Local dev environment |
| Testing | **Pytest** + pytest-asyncio | Unit tests |

### Frontend
| Layer | Technology | Purpose |
|---|---|---|
| UI Framework | **React 18** | Component-based UI |
| Build Tool | **Vite** | Fast dev server & production bundler |
| Routing | **React Router v6** | SPA client-side routing |
| Styling | **Vanilla CSS** | Custom neo-brutalist dark design |
| HTTP | **Fetch API** | API calls to FastAPI backend |

### Infrastructure
| Service | Provider |
|---|---|
| Frontend Hosting | **Vercel** (static + SPA routing) |
| Backend Hosting | **Render** (Docker web service) |
| Managed Database | **Render PostgreSQL** |
| Managed Cache | **Render Redis** |
| CI/CD | **GitHub Actions** |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                        │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
   ┌───────────────────┐      ┌───────────────────────┐
   │   Vercel (CDN)    │      │   Render Web Service  │
   │   React + Vite    │─────▶│   FastAPI + Uvicorn   │
   │   (Static SPA)    │      │   (Docker container)  │
   └───────────────────┘      └──────────┬────────────┘
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                   ┌────────────┐ ┌──────────┐ ┌──────────────┐
                   │ PostgreSQL │ │  Redis   │ │  Background  │
                   │  (Render)  │ │ (Render) │ │  Analytics   │
                   └────────────┘ └──────────┘ └──────────────┘
```

**Request flow for a redirect:**
1. Browser hits `GET /{short_code}` on the FastAPI backend
2. FastAPI checks **Redis** first (cache hit → instant redirect in < 5ms)
3. On cache miss, queries **PostgreSQL**, caches the result, then redirects
4. Click analytics are recorded **asynchronously** as a `BackgroundTask` — the user is already redirected before any DB write happens

---

## ✨ Features

- 🔗 **URL Shortening** — Paste any URL, get a short branded link instantly
- 🎨 **Custom Aliases** — Choose your own slug (e.g. `/my-link`)
- 📊 **Click Analytics** — Total clicks, device breakdown, browser stats per link
- ⚡ **Redis Caching** — Redirects served from memory, not DB
- 🚦 **Rate Limiting** — 10 shortening requests / minute / IP (429 on breach)
- 🔒 **Security Headers** — `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`
- 🛡 **Input Validation** — URL format checking, reserved word blocking, loop prevention
- 🔄 **Async Analytics** — Click tracking never slows down the redirect path

---

## 📁 Project Structure

```
url_shortner/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── main.py                 # App entry point, middleware, router registration
│   │   ├── api/
│   │   │   ├── dependencies.py     # DB session & Redis dependency injectors
│   │   │   └── v1/routes/
│   │   │       ├── health.py       # GET /health
│   │   │       ├── shorten.py      # POST /api/v1/shorten
│   │   │       ├── redirect.py     # GET /{short_code}
│   │   │       └── analytics.py    # GET /api/v1/stats/{short_code}
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic BaseSettings (.env loader)
│   │   │   └── limiter.py          # SlowAPI rate limiter instance
│   │   ├── db/
│   │   │   └── session.py          # Async SQLAlchemy engine + Redis client
│   │   ├── models/
│   │   │   └── url.py              # ORM models: Url, ClickAnalytic
│   │   ├── schemas/
│   │   │   └── url.py              # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── keygen.py           # Base62 short-code generator
│   │   │   ├── url_service.py      # Business logic: create, lookup, cache
│   │   │   └── analytics_service.py# Click recording & stats aggregation
│   │   └── utils/
│   │       └── validators.py       # URL validation helpers
│   ├── alembic/                    # Database migration scripts
│   ├── tests/                      # Pytest unit tests
│   ├── Dockerfile                  # Production container image
│   ├── docker-compose.yml          # Local dev: PostgreSQL + Redis
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                       # React + Vite application
│   ├── src/
│   │   ├── App.jsx                 # Router setup
│   │   ├── main.jsx                # React entry point
│   │   ├── index.css               # Global design system (dark, neo-brutalist)
│   │   ├── components/
│   │   │   ├── Header.jsx          # Top navigation bar
│   │   │   ├── UrlForm.jsx         # URL input + custom alias form
│   │   │   ├── ResultCard.jsx      # Short URL result + copy button
│   │   │   └── ErrorBanner.jsx     # Inline error display
│   │   ├── pages/
│   │   │   ├── HomePage.jsx        # Main shortener page
│   │   │   └── StatsPage.jsx       # Analytics dashboard for a short code
│   │   └── services/
│   │       └── api.js              # Fetch wrappers for all API calls
│   ├── index.html
│   ├── vite.config.js
│   └── .env.example
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions: test → preview → production
├── vercel.json                     # Vercel frontend deployment config
├── render.yaml                     # Render backend + DB + Redis IaC config
└── COMMANDS.txt                    # Quick reference commands
```

---

## 🔄 How It Works

### Key Generation (Module 2)
Short codes are generated using **Base62 encoding** (`[0-9A-Za-z]`):
1. A random 8-character code is generated from the Base62 alphabet
2. The code is checked against the database for collisions
3. On collision (extremely rare), a new code is generated
4. Custom aliases bypass generation and are validated against reserved words

### URL Shortening (Module 3)
```
POST /api/v1/shorten  { "long_url": "https://...", "custom_alias": "optional" }

1. Validate URL format (must be http/https, reachable scheme)
2. Check for self-referencing (loop prevention)
3. Generate or validate short code
4. Check for alias conflicts (409 if taken)
5. INSERT into PostgreSQL urls table
6. Return { short_url, short_code, long_url, clicks, created_at }
```

### Redirect with Caching (Module 4)
```
GET /{short_code}

1. Check Redis: GET shrink:{short_code}
   ├── Cache HIT  → 307 redirect instantly (< 5ms)
   └── Cache MISS → Query PostgreSQL
                    ├── Not found → 404
                    └── Found → SET Redis (TTL 24h)
                               → 307 redirect
                               → BackgroundTask: record_click()
```

### Click Analytics (Module 5)
Every redirect fires a `BackgroundTask` **after** the response is sent:
```python
background_tasks.add_task(record_click, short_code, user_agent, ip_hash, referrer)
```
This inserts a row into `click_analytics` with:
- `short_code` — which URL was clicked
- `device_type` — mobile / desktop / tablet (parsed from User-Agent)
- `browser` — Chrome / Firefox / Safari / etc.
- `ip_hash` — SHA-256 of IP (privacy-safe, not reversible)
- `referrer` — where the user came from
- `clicked_at` — timestamp

### Rate Limiting (Module 6)
`POST /api/v1/shorten` is rate-limited to **10 requests per minute per IP** using SlowAPI (backed by Redis). Exceeding the limit returns `429 Too Many Requests`.

---

## 💻 Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker Desktop

### 1. Clone the repo
```bash
git clone https://github.com/nitin2802w/url_shortner.git
cd url_shortner
```

### 2. Start PostgreSQL & Redis (Docker)
```bash
cd backend
docker compose up -d
```

### 3. Set up the backend
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```
API is now running at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 4. Set up the frontend
```bash
cd ../frontend
npm install

# Copy env file
copy .env.example .env.local
# VITE_API_URL=http://localhost:8000  (default for local dev)

npm run dev
```
Frontend is now running at `http://localhost:5173`

### 5. Run tests
```bash
cd backend
pytest tests/ -v
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```env
PROJECT_NAME="SHRINK URL Shortener"
BASE_URL="http://localhost:8000"
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener"
REDIS_URL="redis://localhost:6379/0"
```

### Frontend (`frontend/.env.local`)
```env
# Leave blank for local dev (defaults to localhost:8000)
VITE_API_URL=https://url-shortner-kexm.onrender.com
```

---

## 📡 API Reference

### `GET /health`
Check if the service is running.
```json
{ "status": "ok", "service": "SHRINK URL Shortener" }
```

### `POST /api/v1/shorten`
Shorten a URL.
```json
// Request
{ "long_url": "https://example.com/very/long/path", "custom_alias": "my-link" }

// Response 201
{
  "short_url": "https://url-shortner-kexm.onrender.com/my-link",
  "short_code": "my-link",
  "long_url": "https://example.com/very/long/path",
  "clicks": 0,
  "created_at": "2024-11-01T12:00:00Z"
}
```
**Errors:** `409` alias taken · `422` invalid URL · `429` rate limit exceeded

### `GET /{short_code}`
Redirect to the original URL.
- `307 Temporary Redirect` → original URL
- `404` → short code not found

### `GET /api/v1/stats/{short_code}`
Get click analytics for a short link.
```json
{
  "short_code": "my-link",
  "long_url": "https://example.com/very/long/path",
  "total_clicks": 42,
  "created_at": "2024-11-01T12:00:00Z",
  "devices": { "mobile": 28, "desktop": 12, "tablet": 2 },
  "browsers": { "Chrome": 20, "Safari": 15, "Firefox": 7 }
}
```

---

## 🚀 Deployment

### Backend → Render
The repo includes a [`render.yaml`](render.yaml) for one-click Infrastructure-as-Code deployment:
```yaml
# Automatically provisions:
# - FastAPI web service (Docker)
# - Managed PostgreSQL database
# - Managed Redis cache
```
1. Go to [render.com](https://render.com) → **New → Blueprint**
2. Connect the GitHub repo → Render reads `render.yaml` automatically
3. After deploy, open the **Shell** tab and run: `alembic upgrade head`

### Frontend → Vercel
1. Go to [vercel.com](https://vercel.com) → **Add New Project** → Import repo
2. In **Settings → General → Build & Development Settings**:
   - Root Directory: `frontend`
   - Output Directory: `dist`
3. Add Environment Variable: `VITE_API_URL` = `https://url-shortner-kexm.onrender.com`
4. Deploy ✅

---

## ⚙️ CI/CD Pipeline

GitHub Actions runs automatically on every push:

```
Push to main
     │
     ▼
┌─────────────┐
│ Unit Tests  │  pytest tests/test_keygen.py tests/test_analytics.py
│  (Python)   │
└──────┬──────┘
       │ passes
       ▼
┌──────────────────┐
│ Production Deploy│  vercel deploy --prod
│   (Vercel)       │
└──────────────────┘

Pull Request
     │
     ▼
┌─────────────┐    ┌─────────────────┐
│ Unit Tests  │───▶│ Preview Deploy  │  vercel deploy (preview URL)
└─────────────┘    └─────────────────┘
```

**Required GitHub Secrets:**
| Secret | Where to get it |
|---|---|
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens |
| `VERCEL_ORG_ID` | `vercel link` → `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | Same `.vercel/project.json` |

Render deploys automatically via its own GitHub integration — no extra secrets needed.

---

## 📄 License

MIT — feel free to fork and build on this.
