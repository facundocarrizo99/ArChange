#!/usr/bin/env python3
"""
Standalone script to fetch exchange rates from DolarAPI and store in PostgreSQL.
Run this directly from the terminal: python run_fetch.py
"""
import sys
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from app import db
from app.config import DATABASE_DSN, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
from app.fetch_exchange import fetch_and_store_exchange_rates


def main():
    """Initialize DB connection and fetch exchange rates."""
    try:
        print(f"Connecting to database at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}...")
        db.init_pool(DATABASE_DSN)
        
        print("Fetching exchange rates from DolarAPI...")
        result = fetch_and_store_exchange_rates()
        
        print("\n" + "="*50)
        print("RESULT:")
        print("="*50)
        print(f"Status: {result.get('status')}")
        print(f"Total fetched: {result.get('total', 0)}")
        print(f"Successfully inserted: {result.get('inserted', 0)}")
        
        if result.get('errors'):
            print(f"\nErrors: {result['errors']}")
        
        if result.get('exchanges'):
            print(f"\nExchange rates fetched:")
            for ex in result['exchanges']:
                print(f"  - {ex['nombre']} ({ex['casa']}): Compra ${ex['compra']}, Venta ${ex['venta']}")
        
        print("="*50)
        
        db.close_pool()
        
        if result.get('status') == 'ok':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
