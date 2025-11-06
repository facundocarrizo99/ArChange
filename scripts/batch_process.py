#!/usr/bin/env python3
"""Batch/CLI script to fetch exchange rates from DolarAPI and store in database."""
import argparse
import json
import os
import sys

from app import db
from app.fetch_exchange import fetch_and_store_exchange_rates


def main():
    parser = argparse.ArgumentParser(
        description="Fetch exchange rates from DolarAPI and store in PostgreSQL"
    )
    parser.add_argument(
        "--db-host",
        default=os.getenv("POSTGRES_HOST", "localhost"),
        help="PostgreSQL host (default: localhost)",
    )
    parser.add_argument(
        "--db-port",
        default=os.getenv("POSTGRES_PORT", "5433"),
        help="PostgreSQL port (default: 5433)",
    )
    parser.add_argument(
        "--db-name",
        default=os.getenv("POSTGRES_DB", "wallbitdb"),
        help="Database name (default: wallbitdb)",
    )
    parser.add_argument(
        "--db-user",
        default=os.getenv("POSTGRES_USER", "wallbit"),
        help="Database user (default: wallbit)",
    )
    parser.add_argument(
        "--db-password",
        default=os.getenv("POSTGRES_PASSWORD", "wallbitpass"),
        help="Database password",
    )
    args = parser.parse_args()

    # Initialize database connection
    dsn = f"postgresql://{args.db_user}:{args.db_password}@{args.db_host}:{args.db_port}/{args.db_name}"
    
    try:
        db.init_pool(dsn)
        result = fetch_and_store_exchange_rates()
        print(json.dumps(result, indent=2))
        db.close_pool()
        
        # Exit with appropriate code
        sys.exit(0 if result.get("status") == "ok" else 1)
    except Exception as e:
        error_result = {"status": "error", "message": str(e)}
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
