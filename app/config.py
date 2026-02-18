"""Centralized configuration loaded from environment variables."""

import os


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB = os.getenv("POSTGRES_DB", "wallbitdb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "wallbit")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "wallbitpass")

DATABASE_DSN = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

SCHEDULER_INTERVAL_HOURS = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "2"))
