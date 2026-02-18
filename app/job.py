"""Job module: exposes run_job used by the API and the batch script.
Fetches exchange rates from DolarAPI and stores them in the database.

If a Postgres pool is available in `app.db.pool` the job will insert records
into the exchange_rates table.
"""
import logging

from . import db as _db
from .fetch_exchange import fetch_and_store_exchange_rates

logger = logging.getLogger(__name__)


def run_job(data=None):
    """Run the exchange rate fetching job and return a dict result.

    Inputs:
        - data: optional payload (not used in this implementation)
    Output:
        - dict with status, inserted count, and exchange data
    """
    try:
        result = fetch_and_store_exchange_rates()
        return result
    except Exception as e:
        logger.exception("Job failed")
        return {"status": "error", "message": f"Job failed: {str(e)}"}


def scheduled_task():
    """Task intended to be scheduled by a scheduler (e.g., APScheduler).
    Fetches exchange rates periodically.
    """
    return run_job("scheduled")
