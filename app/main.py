"""FastAPI app exposing an API to fetch and manage exchange rates.

This application provides endpoints to:
- Fetch exchange rates from DolarAPI (https://dolarapi.com)
- Store exchange rates in PostgreSQL database
- Query stored exchange rates
- Schedule automatic fetching every 2 hours
"""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from .config import DATABASE_DSN, SCHEDULER_INTERVAL_HOURS
from .job import run_job, scheduled_task
from . import db
from .models import Exchange
from .fetch_exchange import fetch_and_store_exchange_rates
from .schemas import (
    ExchangeListResponse,
    FetchExchangeResponse,
    ErrorResponse,
)

# OpenAPI metadata
app = FastAPI(
    title="WallBit Exchange Rates API",
    description="""
# WallBit Exchange Rates API

This API provides real-time Argentine peso (ARS) exchange rates from multiple sources.

## Features

* 📊 **Real-time Data**: Fetch current exchange rates from DolarAPI
* 💾 **Persistent Storage**: Store historical exchange rates in PostgreSQL
* 🔄 **Automatic Updates**: Scheduled fetching every 2 hours
* 📈 **Multiple Exchange Houses**: Official, Blue, Bolsa, CCL, Mayorista, Cripto, Tarjeta

## Exchange Rate Types

- **Oficial**: Official government exchange rate
- **Blue**: Informal/parallel market rate
- **Bolsa**: Stock market exchange rate (MEP)
- **Contado con Liquidación (CCL)**: Securities-based exchange mechanism
- **Mayorista**: Wholesale interbank rate
- **Cripto**: Cryptocurrency-based rate
- **Tarjeta**: Credit card exchange rate (official + taxes)

## Data Source

Exchange rates are fetched from [DolarAPI](https://dolarapi.com), a free API providing
real-time Argentine peso exchange rates.
    """,
    version="1.0.0",
    contact={
        "name": "WallBit API Support",
        "email": "support@wallbit.example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Exchange Rates",
            "description": "Operations for managing and querying exchange rates",
        },
        {
            "name": "Data Fetching",
            "description": "Endpoints to fetch exchange rates from external APIs",
        },
        {
            "name": "Jobs",
            "description": "Background job execution endpoints",
        },
    ],
)

# scheduler for periodic tasks
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    # Initialize DB pool if environment variables are present (or defaults)
    try:
        db.init_pool(DATABASE_DSN)

        # Run migrations after pool initialization
        migrations_dir = Path(__file__).parent.parent / "migrations"
        migration_file = migrations_dir / "001_create_exchange_rates.sql"
        if migration_file.exists():
            db.run_migration(str(migration_file))
    except Exception as e:
        # If DB isn't available during startup (e.g., no docker running), continue
        print(f"DB startup warning: {e}")

    # Schedule the periodic job
    try:
        scheduler.add_job(
            scheduled_task,
            "interval",
            hours=SCHEDULER_INTERVAL_HOURS,
            id="scheduled_exchange_fetch",
            replace_existing=True,
        )
        scheduler.start()
    except Exception:
        # Scheduler may already be started in some reload scenarios; ignore errors
        pass


@app.on_event("shutdown")
def shutdown_event():
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass

    try:
        db.close_pool()
    except Exception:
        pass


@app.get(
    "/api/exchange",
    response_model=ExchangeListResponse,
    tags=["Exchange Rates"],
    summary="Get all exchange rates",
    description="""
    Retrieve all stored exchange rates from the database.
    
    Returns the most recent 100 exchange rate records, ordered by ID (most recent first).
    Each record includes buy/sell prices, average rate, and timestamp.
    """,
    responses={
        200: {
            "description": "Successfully retrieved exchange rates",
            "model": ExchangeListResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
def get_exchange():
    """Get all exchange rates from the database."""
    try:
        rows = db.get_exchanges(limit=100)
        exchanges = [Exchange.from_row(row).to_dict() for row in rows]
        return {"status": "ok", "data": exchanges}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post(
    "/run-job",
    response_model=FetchExchangeResponse,
    tags=["Jobs"],
    summary="Execute the exchange rate fetching job",
    description="""
    Manually trigger the exchange rate fetching job.
    
    This endpoint executes the same job that runs automatically every 2 hours.
    It fetches exchange rates from DolarAPI and stores them in the database.
    
    **Use Cases**:
    - Testing the job execution
    - Forcing an immediate update
    - Initial data population
    
    **Returns**: Status, number of records inserted, and list of fetched exchanges.
    """,
    responses={
        200: {
            "description": "Job executed successfully",
            "model": FetchExchangeResponse,
        },
        500: {
            "description": "Job execution failed",
            "model": ErrorResponse,
        },
    },
)
def run_job_endpoint(payload: Optional[dict] = None):
    """Run the job synchronously with optional JSON payload."""
    result = run_job(payload)
    return result


@app.post(
    "/api/exchange/fetch",
    response_model=FetchExchangeResponse,
    tags=["Data Fetching"],
    summary="Fetch exchange rates from DolarAPI",
    description="""
    Fetch current exchange rates from DolarAPI and store them in the database.
    
    This endpoint connects to https://dolarapi.com/v1/dolares and retrieves
    all available exchange rates including:
    
    - **Oficial**: Official government rate
    - **Blue**: Informal market rate
    - **Bolsa**: Stock market rate (MEP)
    - **CCL**: Contado con Liquidación
    - **Mayorista**: Wholesale rate
    - **Cripto**: Cryptocurrency-based rate
    - **Tarjeta**: Credit card rate
    
    Each rate is stored with buy/sell prices, calculated average, and timestamp.
    
    **Response includes**:
    - Total number of rates fetched
    - Number successfully inserted
    - Detailed information for each exchange rate
    - Any errors encountered during processing
    """,
    responses={
        200: {
            "description": "Exchange rates fetched and stored successfully",
            "model": FetchExchangeResponse,
        },
        500: {
            "description": "Failed to fetch or store exchange rates",
            "model": ErrorResponse,
        },
    },
)
def fetch_exchange_rates():
    """Fetch exchange rates from dolarapi.com and store them in the database."""
    result = fetch_and_store_exchange_rates()
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
