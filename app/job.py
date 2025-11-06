"""Job module: exposes run_job used by the API and the batch script.
Fetches exchange rates from DolarAPI and stores them in the database.

If a Postgres pool is available in `app.db.pool` the job will insert records
into the exchange_rates table.
"""

try:
  # optional import; db.pool may be None if not initialized
  from . import db as _db
  from .fetch_exchange import fetch_and_store_exchange_rates
except Exception:
  _db = None
  fetch_and_store_exchange_rates = None


def run_job(data=None):
  """Run the exchange rate fetching job and return a dict result.

  Inputs:
    - data: optional payload (not used in this implementation)
  Output:
    - dict with status, inserted count, and exchange data
  """
  # Fetch and store exchange rates from DolarAPI
  try:
    if fetch_and_store_exchange_rates is not None:
      result = fetch_and_store_exchange_rates()
      return result
    else:
      return {"status": "error", "message": "fetch_and_store_exchange_rates not available"}
  except Exception as e:
    return {"status": "error", "message": f"Job failed: {str(e)}"}


def scheduled_task():
  """Task intended to be scheduled by a scheduler (e.g., APScheduler).
  Fetches exchange rates periodically.
  """
  return run_job("scheduled")
