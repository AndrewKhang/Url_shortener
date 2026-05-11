# URL Shortener API

A URL shortening service built with FastAPI and PostgreSQL, similar to Bitly.

## Tech Stack
- FastAPI
- PostgreSQL (via Docker)
- SQLAlchemy ORM
- Redis (caching)
- Python 3.14

## Setup

### Prerequisites
- Docker
- Python 3.14
- Git Bash

### Run locally
```bash
# Clone repo
git clone <your-repo-url>
cd url_shortener

# Create virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Start Docker containers
docker-compose up -d

# Start server
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/links` | Create short link |
| GET | `/{short_key}` | Redirect to original URL |

## Environment Variables
Create a `.env` file:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=mysecretpassword
DB_NAME=url_shortener_db
```