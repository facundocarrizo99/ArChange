"""Tests for Exchange model and DB operations."""
from decimal import Decimal
from app.models import Exchange


def test_exchange_model_creation():
    """Test creating an Exchange instance."""
    ex = Exchange(
        id=1,
        type="USD",
        buy=Decimal("100.50"),
        sell=Decimal("101.00"),
        rate=Decimal("100.75"),
        diff=Decimal("0.50"),
    )
    assert ex.id == 1
    assert ex.type == "USD"
    assert ex.buy == Decimal("100.50")


def test_exchange_to_dict():
    """Test Exchange.to_dict() serialization."""
    ex = Exchange(
        id=2,
        type="EUR",
        buy=Decimal("85.00"),
        sell=Decimal("86.00"),
        rate=Decimal("85.50"),
        diff=Decimal("1.00"),
    )
    data = ex.to_dict()
    assert data["id"] == 2
    assert data["type"] == "EUR"
    assert data["buy"] == 85.0
    assert data["sell"] == 86.0
    assert data["rate"] == 85.5
    assert data["diff"] == 1.0


def test_exchange_from_row():
    """Test Exchange.from_row() creates instance from DB row."""
    row = (3, "GBP", Decimal("120.00"), Decimal("121.00"), Decimal("120.50"), Decimal("1.50"), None)
    ex = Exchange.from_row(row)
    assert ex.id == 3
    assert ex.type == "GBP"
    assert ex.buy == Decimal("120.00")
    assert ex.sell == Decimal("121.00")
