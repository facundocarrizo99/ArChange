# WallBit - Argentine Exchange Rates API

A FastAPI-based application that fetches and stores Argentine peso (ARS) exchange rates from multiple sources.

## Features

- 📊 **Real-time Exchange Rates**: Fetch current ARS exchange rates from DolarAPI
- 💾 **PostgreSQL Storage**: Store historical exchange rate data
- 🔄 **Automatic Updates**: Scheduled fetching every 2 hours
- 🚀 **RESTful API**: Well-documented OpenAPI v3 endpoints
- 📈 **Multiple Sources**: Official, Blue, Bolsa, CCL, Mayorista, Cripto, Tarjeta

## Exchange Rate Types

- **Oficial**: Official government exchange rate
- **Blue**: Informal/parallel market rate (most commonly used)
- **Bolsa (MEP)**: Stock market exchange rate
- **Contado con Liquidación (CCL)**: Securities-based exchange mechanism
- **Mayorista**: Wholesale interbank rate
- **Cripto**: Cryptocurrency-based rate
- **Tarjeta**: Credit card exchange rate (includes taxes)

## Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd WallBit
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start PostgreSQL database**:
```bash
docker-compose up -d
```

5. **Run the application**:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit:
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON Schema**: http://localhost:8000/openapi.json

### Main Endpoints

#### GET `/api/exchange`
Get all stored exchange rates from the database.

```bash
curl http://localhost:8000/api/exchange
```

#### POST `/api/exchange/fetch`
Fetch current exchange rates from DolarAPI and store them.

```bash
curl -X POST http://localhost:8000/api/exchange/fetch
```

#### POST `/api/exchange`
Manually create a new exchange rate record.

```bash
curl -X POST http://localhost:8000/api/exchange \
  -H "Content-Type: application/json" \
  -d '{"type": "blue", "buy": 1415, "sell": 1435, "rate": 1425, "diff": 20}'
```

#### POST `/run-job`
Manually trigger the scheduled job to fetch exchange rates.

```bash
curl -X POST http://localhost:8000/run-job
```

## Command Line Usage

### Fetch Exchange Rates (Standalone Script)

Run the standalone script to fetch and store exchange rates:

```bash
python run_fetch.py
```

Output:
```
Connecting to database at localhost:5433/wallbitdb...
Fetching exchange rates from DolarAPI...

==================================================
RESULT:
==================================================
Status: ok
Total fetched: 7
Successfully inserted: 7

Exchange rates fetched:
  - Oficial (oficial): Compra $1425, Venta $1475
  - Blue (blue): Compra $1415, Venta $1435
  - Bolsa (bolsa): Compra $1478.3, Venta $1481.7
  ...
==================================================
```

### Batch Processing Script

Run the batch processing script with custom database parameters:

```bash
python scripts/batch_process.py \
  --db-host localhost \
  --db-port 5433 \
  --db-name wallbitdb \
  --db-user wallbit \
  --db-password wallbitpass
```

## Project Structure

```
WallBit/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application with routes
│   ├── models.py            # Database models (Exchange)
│   ├── schemas.py           # Pydantic schemas for API validation
│   ├── db.py                # Database connection and operations
│   ├── exchange.py          # Exchange data class
│   ├── fetch_exchange.py    # DolarAPI fetching logic
│   └── job.py               # Scheduled job execution
├── migrations/
│   └── 001_create_exchange_rates.sql
├── scripts/
│   └── batch_process.py     # CLI batch processing script
├── tests/
│   ├── test_exchange.py     # Tests for Exchange model
│   ├── test_job.py          # Tests for job execution
│   ├── test_fetch_exchange.py  # Tests for API fetching
│   └── test_batch.py        # Tests for batch script
├── docker-compose.yml       # PostgreSQL container setup
├── requirements.txt         # Python dependencies
├── run_fetch.py            # Standalone fetch script
└── README.md
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Run specific test file:
```bash
pytest tests/test_fetch_exchange.py -v
```

## Database Schema

### `exchange_rates` Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| type | VARCHAR | Exchange type (e.g., 'blue', 'oficial') |
| buy | DECIMAL | Buy price in ARS |
| sell | DECIMAL | Sell price in ARS |
| rate | DECIMAL | Average rate |
| diff | DECIMAL | Difference between sell and buy |
| created_at | TIMESTAMP | Record creation timestamp |

## Environment Variables

Configure the application using environment variables:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=wallbitdb
POSTGRES_USER=wallbit
POSTGRES_PASSWORD=wallbitpass
```

## Scheduled Jobs

The application automatically fetches exchange rates every **2 hours** using APScheduler.

To modify the schedule, edit `app/main.py`:
```python
scheduler.add_job(scheduled_task, "interval", hours=2, ...)
```

## Data Source

Exchange rates are fetched from [DolarAPI](https://dolarapi.com), a free API providing real-time Argentine peso exchange rates.

API Endpoint: `https://dolarapi.com/v1/dolares`

## Development

### Adding New Features

1. Create feature branch
2. Add tests in `tests/`
3. Implement feature in `app/`
4. Update OpenAPI documentation in `app/main.py`
5. Run tests: `pytest`
6. Submit pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions small and focused

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
```bash
# Check if PostgreSQL is running
docker ps

# Restart database
docker-compose restart

# View database logs
docker-compose logs db
```

### Port Already in Use

If port 8000 is already in use:
```bash
# Kill process using port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Or run on different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## License

MIT

