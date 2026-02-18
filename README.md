# ArChange — Argentine Exchange Rates API

> Fetch, store, and serve real-time Argentine peso (ARS) exchange rates via a simple REST API.

ArChange connects to [DolarAPI](https://dolarapi.com), persists historical rates in PostgreSQL, and exposes them through documented FastAPI endpoints. A built-in scheduler keeps the data fresh automatically.

---

## Key Features

- **7 exchange-rate types** — Oficial, Blue, Bolsa (MEP), CCL, Mayorista, Cripto, Tarjeta
- **Automatic updates** — APScheduler fetches rates every 2 hours (configurable)
- **PostgreSQL storage** — full history with connection pooling via psycopg 3
- **OpenAPI docs** — Swagger UI & ReDoc out of the box
- **CLI tools** — standalone fetch script and batch processor

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.99 + Uvicorn |
| Database | PostgreSQL 15 (Docker) |
| HTTP client | httpx |
| Scheduler | APScheduler |
| Driver | psycopg 3 + psycopg-pool |
| Tests | pytest |

---

## Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose

### 1. Clone & install

```bash
git clone https://github.com/facundocarrizo99/ArChange.git
cd ArChange
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the database

```bash
docker compose up -d
```

### 3. Configure environment (optional)

```bash
cp .env.example .env   # edit values if needed
```

### 4. Run the server

```bash
python -m app.main
```

The API is now live at **http://localhost:8000**.

---

## API Overview

Interactive docs: [localhost:8000/docs](http://localhost:8000/docs) · [localhost:8000/redoc](http://localhost:8000/redoc)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/exchange` | Retrieve the last 100 stored exchange rates |
| `POST` | `/api/exchange/fetch` | Fetch current rates from DolarAPI and store them |
| `POST` | `/run-job` | Manually trigger the scheduled fetch job |

### Example

```bash
# Fetch and store latest rates
curl -X POST http://localhost:8000/api/exchange/fetch

# Query stored rates
curl http://localhost:8000/api/exchange
```

<details>
<summary>Sample response — <code>GET /api/exchange</code></summary>

```json
{
  "status": "ok",
  "data": [
    {
      "id": 1,
      "type": "blue",
      "buy": 1415.0,
      "sell": 1435.0,
      "rate": 1425.0,
      "diff": 20.0,
      "created_at": "2025-11-06T19:58:00"
    }
  ]
}
```
</details>

---

## Environment Variables

All variables have sensible defaults for local development. Override them via `.env` or shell exports.

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5433` | Database port |
| `POSTGRES_DB` | `wallbitdb` | Database name |
| `POSTGRES_USER` | `wallbit` | Database user |
| `POSTGRES_PASSWORD` | `wallbitpass` | Database password |
| `SCHEDULER_INTERVAL_HOURS` | `2` | Hours between automatic fetches |

---

## Project Structure

```
ArChange/
├── app/
│   ├── config.py            # Centralized environment configuration
│   ├── main.py              # FastAPI application & routes
│   ├── models.py            # Database model (Exchange)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── db.py                # Connection pool & CRUD helpers
│   ├── dolar_api.py         # DolarAPI response data class
│   ├── fetch_exchange.py    # Fetch from DolarAPI → store in DB
│   └── job.py               # Scheduled job wrapper
├── migrations/
│   └── 001_create_exchange_rates.sql
├── scripts/
│   └── batch_process.py     # CLI batch processor with custom DB args
├── tests/
│   ├── test_exchange.py
│   ├── test_fetch_exchange.py
│   ├── test_job.py
│   └── test_batch.py
├── run_fetch.py             # Standalone fetch script
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── .env.example
└── .editorconfig
```

## Architecture

```
DolarAPI ──► fetch_exchange.py ──► db.py ──► PostgreSQL
                 ▲                              │
                 │                              ▼
            job.py / scheduler            GET /api/exchange
                 ▲
                 │
            POST /run-job
            POST /api/exchange/fetch
```

`config.py` feeds database credentials and scheduler settings to every layer, ensuring a single source of truth.

---

## Database Schema

Migrations run automatically on startup.

```sql
CREATE TABLE IF NOT EXISTS exchange_rates (
    id         BIGSERIAL PRIMARY KEY,
    type       VARCHAR(50) NOT NULL,   -- 'blue', 'oficial', …
    buy        DECIMAL(10,2),
    sell       DECIMAL(10,2),
    rate       DECIMAL(10,2),          -- (buy + sell) / 2
    diff       DECIMAL(10,2),          -- sell − buy
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## CLI Scripts

```bash
# Standalone fetch (uses env vars)
python run_fetch.py

# Batch processor with explicit DB args
python scripts/batch_process.py --db-host localhost --db-port 5433
```

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Single file
pytest tests/test_fetch_exchange.py -v
```

---

## Deployment Notes

1. Set environment variables for your production database.
2. Run `docker compose up -d` (or point to a managed PostgreSQL instance).
3. Start the app: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
4. The scheduler will begin fetching automatically on startup.

---

## Contributing

1. Fork the repo & create a feature branch.
2. Write tests in `tests/`.
3. Ensure `pytest` passes.
4. Submit a pull request.

## License

MIT

