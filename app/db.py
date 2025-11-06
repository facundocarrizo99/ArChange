"""Small DB helper using psycopg connection pool.

Expose:
- pool: the ConnectionPool instance or None
- init_pool(dsn): initialize the pool
- close_pool(): close the pool
- run_migration(sql_file_path): execute a SQL migration file
- insert_exchange / get_exchanges: CRUD helpers for exchange_rates
"""
import os
from pathlib import Path
from typing import Optional, List
from decimal import Decimal

pool = None


def init_pool(dsn: str):
    """Initialize a psycopg ConnectionPool with the provided DSN."""
    global pool
    try:
        from psycopg_pool import ConnectionPool
    except Exception as e:
        raise RuntimeError("psycopg_pool is required to use the DB") from e

    if pool is None:
        pool = ConnectionPool(conninfo=dsn)


def close_pool():
    global pool
    try:
        if pool is not None:
            pool.close()
    finally:
        pool = None


# Helper to get a connection context manager. Usage:
# with get_conn() as conn:
#     with conn.cursor() as cur:
#         cur.execute(...)
# We expose the pool itself so callers can use pool.connection().

def get_pool():
    return pool


def run_migration(sql_file_path: str):
    """Run a SQL migration file. Raises exception if pool is not initialized."""
    if pool is None:
        raise RuntimeError("DB pool not initialized; cannot run migration")
    
    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"Migration file not found: {sql_file_path}")
    
    sql = sql_path.read_text()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()


def insert_exchange(
    type: str,
    buy: Optional[Decimal] = None,
    sell: Optional[Decimal] = None,
    rate: Optional[Decimal] = None,
    diff: Optional[Decimal] = None,
) -> int:
    """Insert a new exchange rate record and return the new ID."""
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO exchange_rates (type, buy, sell, rate, diff)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (type, buy, sell, rate, diff),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id


def get_exchanges(limit: int = 100) -> List[tuple]:
    """Fetch exchange rate records (returns list of tuples)."""
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, type, buy, sell, rate, diff, created_at FROM exchange_rates ORDER BY id DESC LIMIT %s",
                (limit,),
            )
            return cur.fetchall()


def get_exchange_by_id(exchange_id: int) -> Optional[tuple]:
    """Fetch a single exchange rate by ID."""
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, type, buy, sell, rate, diff, created_at FROM exchange_rates WHERE id = %s",
                (exchange_id,),
            )
            return cur.fetchone()
