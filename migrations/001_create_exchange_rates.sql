-- Migration: Create exchange_rates table
-- Run this on startup or manually via psql

CREATE TABLE IF NOT EXISTS exchange_rates (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    buy DECIMAL(10, 2),
    sell DECIMAL(10, 2),
    rate DECIMAL(10, 2),
    diff DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional: add index on type for faster queries
CREATE INDEX IF NOT EXISTS idx_exchange_rates_type ON exchange_rates(type);
