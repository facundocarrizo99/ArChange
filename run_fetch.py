#!/usr/bin/env python3
"""
Standalone script to fetch exchange rates from DolarAPI and store in PostgreSQL.
Run from the project root: python -m run_fetch
"""
import logging
import sys

from app import db
from app.config import DATABASE_DSN, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
from app.fetch_exchange import fetch_and_store_exchange_rates

logger = logging.getLogger(__name__)


def main():
    """Initialize DB connection and fetch exchange rates."""
    try:
        logger.info("Connecting to database at %s:%s/%s…", POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)
        db.init_pool(DATABASE_DSN)

        logger.info("Fetching exchange rates from DolarAPI…")
        result = fetch_and_store_exchange_rates()

        print("\n" + "=" * 50)
        print("RESULT:")
        print("=" * 50)
        print(f"Status: {result.get('status')}")
        print(f"Total fetched: {result.get('total', 0)}")
        print(f"Successfully inserted: {result.get('inserted', 0)}")

        if result.get("errors"):
            print(f"\nErrors: {result['errors']}")

        if result.get("exchanges"):
            print("\nExchange rates fetched:")
            for ex in result["exchanges"]:
                print(f"  - {ex['nombre']} ({ex['casa']}): Compra ${ex['compra']}, Venta ${ex['venta']}")

        print("=" * 50)

        sys.exit(0 if result.get("status") == "ok" else 1)

    except Exception as e:
        logger.exception("run_fetch failed")
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close_pool()


if __name__ == "__main__":
    main()
