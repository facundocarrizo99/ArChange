"""Models for the application."""
from typing import Optional
from decimal import Decimal
from datetime import datetime


class Exchange:
    """Exchange rate model mapping to exchange_rates table."""

    def __init__(
        self,
        id: Optional[int] = None,
        type: str = "",
        buy: Optional[Decimal] = None,
        sell: Optional[Decimal] = None,
        rate: Optional[Decimal] = None,
        diff: Optional[Decimal] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.type = type
        self.buy = buy
        self.sell = sell
        self.rate = rate
        self.diff = diff
        self.created_at = created_at

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "buy": float(self.buy) if self.buy is not None else None,
            "sell": float(self.sell) if self.sell is not None else None,
            "rate": float(self.rate) if self.rate is not None else None,
            "diff": float(self.diff) if self.diff is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row):
        """Create an Exchange instance from a DB row tuple."""
        if not row:
            return None
        return cls(
            id=row[0],
            type=row[1],
            buy=row[2],
            sell=row[3],
            rate=row[4],
            diff=row[5],
            created_at=row[6] if len(row) > 6 else None,
        )

    def __repr__(self):
        return f"<Exchange id={self.id} type={self.type} rate={self.rate}>"
