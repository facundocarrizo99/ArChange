#!/usr/bin/env python3
"""Batch/CLI script to fetch exchange rates from DolarAPI and store in database."""
import argparse
import json
import logging
import sys

from app import db
from app.config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from app.fetch_exchange import fetch_and_store_exchange_rates

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch exchange rates from DolarAPI and store in PostgreSQL"
    )
    parser.add_argument(
        "--db-host",
        default=POSTGRES_HOST,
        help="PostgreSQL host (default: localhost)",
    )
    parser.add_argument(
        "--db-port",
        default=POSTGRES_PORT,
        help="PostgreSQL port (default: 5433)",
    )
    parser.add_argument(
        "--db-name",
        default=POSTGRES_DB,
        help="Database name (default: wallbitdb)",
    )
    parser.add_argument(
        "--db-user",
        default=POSTGRES_USER,
        help="Database user (default: wallbit)",
    )
    args = parser.parse_args()

    password = POSTGRES_PASSWORD
    dsn = f"postgresql://{args.db_user}:{password}@{args.db_host}:{args.db_port}/{args.db_name}"

    try:
        db.init_pool(dsn)
        result = fetch_and_store_exchange_rates()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("status") == "ok" else 1)
    except Exception as e:
        logger.exception("Batch process failed")
        error_result = {"status": "error", "message": str(e)}
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)
    finally:
        db.close_pool()


if __name__ == "__main__":
    main()
