# URL Shortener API

A production-ready URL shortening service built with FastAPI, PostgreSQL, and Redis — similar to Bitly.

Supports custom aliases, link expiration, click analytics (device + geolocation), rate limiting, and Redis caching to minimize database load.

🔗 **Live demo**: [url-shortener-sg93.onrender.com/static/index.html](https://url-shortener-sg93.onrender.com/static/index.html)

---

## Features

- **Shorten URLs** with auto-generated Base62 keys or custom aliases
- **Redirect** with 301 response and collision-safe key generation
- **Link expiration** — auto-expires after 30 days by default, configurable per link
- **Click analytics** — tracks click count, device (User-Agent), and geolocation per redirect
- **Redis caching** — cached redirects avoid hitting the database on repeated requests
- **Rate limiting** — atomic Lua-based rate limit (10 requests/hour per IP)
- **URL validation** — rejects malformed URLs at the schema level via Pydantic

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Cache | Redis 7 |
| Validation | Pydantic v2 |
| Containerization | Docker + Docker Compose |
| Deploy | Render |
| Language | Python 3.14 |

---

## Architecture

```
Client
  │
  ├── POST /links ──────────► FastAPI
  │                               │
  │                               ├── Rate limit (Redis Lua atomic)
  │                               ├── Validate URL (Pydantic)
  │                               ├── Generate Base62 key / custom alias
  │                               └── Save to PostgreSQL
  │
  └── GET /{short_key} ──────► FastAPI
                                  │
                                  ├── Check Redis cache
                                  │     ├── HIT  → redirect 301
                                  │     └── MISS → query PostgreSQL → cache → redirect 301
                                  │
                                  └── Background task (async)
                                        ├── Sync click_count → PostgreSQL
                                        └── Log device + geolocation → clicks table
```

---

## Project Structure

```
url_shortener/
├── app/
│   ├── main.py           # App entry point, table creation
│   ├── database.py       # SQLAlchemy engine, session, Base
│   ├── cache.py          # Redis connection
│   ├── models/
│   │   ├── link.py       # Link model
│   │   └── click.py      # Click analytics model
│   ├── schemas/
│   │   └── link.py       # Pydantic request/response schemas
│   ├── routes/
│   │   └── link.py       # API endpoints
│   ├── services/
│   │   └── shortener.py  # Base62 key generation, geolocation
│   └── static/
│       └── index.html    # Frontend UI
├── docker-compose.yml
├── Procfile
├── requirements.txt
└── .env
```

---

## Local Setup

### Prerequisites

- Docker Desktop
- Python 3.14

### Run locally

```bash
# Clone repo
git clone <your-repo-url>
cd url_shortener

# Create virtual environment
python -m venv venv
source venv/Scripts/activate     # Git Bash
# or
venv\Scripts\Activate.ps1        # PowerShell

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis containers
docker-compose up -d

# Start server
uvicorn app.main:app --reload
```
---

## Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5433
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=url_shortener_db

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=your_secret_key_here
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/links` | Create a short link |
| `GET` | `/{short_key}` | Redirect to original URL |

### POST /links

Request body:

```json
{
  "original_url": "https://example.com/very/long/url",
  "custom_alias": "my-link",
  "expire_date": "2026-12-31T00:00:00"
}
```

`custom_alias` and `expire_date` are optional. If `expire_date` is omitted, the link expires after 30 days.

Response:

```json
{
  "short_key": "aB3kP9",
  "original_url": "https://example.com/very/long/url",
  "expire_date": "2026-12-31T00:00:00",
  "created_at": "2026-05-14T10:00:00"
}
```

---

## Deploy (Render)

This project is deployed on [Render](https://render.com) with 4 services:

| Service | Type | Description |
|---|---|---|
| `url_shortener` | Web Service (Python) | FastAPI backend |
| `url_db` | PostgreSQL 18 | Database |
| `url_cache` | Valkey 8 | Redis-compatible cache |
| `url_shortener_frontend` | Static Site | Frontend UI |

### Environment variables on Render

```env
DB_HOST=<render-postgres-internal-host>
DB_PORT=5432
DB_USER=<render-postgres-user>
DB_PASSWORD=<render-postgres-password>
DB_NAME=<render-postgres-db-name>

REDIS_HOST=<render-valkey-internal-host>
REDIS_PORT=6379
```

---

## Architecture Notes

**Caching strategy** — on first redirect, the original URL is fetched from PostgreSQL and cached in Redis with a 1-hour TTL. Subsequent requests are served directly from Redis without touching the database.

**Rate limiting** — uses a Lua script executed atomically in Redis to prevent race conditions when multiple requests arrive simultaneously from the same IP.

**Click tracking** — each redirect records device info (parsed from User-Agent) and geolocation (via ip-api.com) to the `clicks` table. Click counts are maintained in Redis and synced back to PostgreSQL asynchronously via FastAPI background tasks.

**Collision handling** — key generation uses a retry loop that checks uniqueness in the database before returning, with a `UNIQUE` constraint on `short_key` as an additional safeguard.
