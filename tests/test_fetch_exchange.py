"""Tests for exchange rate fetching from DolarAPI."""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from app.fetch_exchange import fetch_and_store_exchange_rates
from app.exchange import Exchange


class TestFetchExchange:
    """Test suite for exchange rate fetching functionality."""

    @patch('app.fetch_exchange.httpx.get')
    @patch('app.fetch_exchange.db.insert_exchange')
    def test_fetch_and_store_success(self, mock_insert, mock_get):
        """Test successful fetch and store of exchange rates."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "moneda": "USD",
                "casa": "blue",
                "nombre": "Blue",
                "compra": 1415,
                "venta": 1435,
                "fechaActualizacion": "2025-11-06T19:58:00.000Z"
            },
            {
                "moneda": "USD",
                "casa": "oficial",
                "nombre": "Oficial",
                "compra": 1425,
                "venta": 1475,
                "fechaActualizacion": "2025-11-05T17:00:00.000Z"
            }
        ]
        mock_get.return_value = mock_response
        mock_insert.return_value = 1

        result = fetch_and_store_exchange_rates()

        assert result["status"] == "ok"
        assert result["inserted"] == 2
        assert result["total"] == 2
        assert len(result["exchanges"]) == 2
        assert result["errors"] is None
        
        # Verify API was called correctly
        mock_get.assert_called_once_with(
            "https://dolarapi.com/v1/dolares",
            timeout=10.0
        )
        
        # Verify insert was called twice
        assert mock_insert.call_count == 2

    @patch('app.fetch_exchange.httpx.get')
    @patch('app.fetch_exchange.db.insert_exchange')
    def test_fetch_with_partial_errors(self, mock_insert, mock_get):
        """Test fetching when some inserts fail."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "moneda": "USD",
                "casa": "blue",
                "nombre": "Blue",
                "compra": 1415,
                "venta": 1435,
                "fechaActualizacion": "2025-11-06T19:58:00.000Z"
            },
            {
                "moneda": "USD",
                "casa": "oficial",
                "nombre": "Oficial",
                "compra": 1425,
                "venta": 1475,
                "fechaActualizacion": "2025-11-05T17:00:00.000Z"
            }
        ]
        mock_get.return_value = mock_response
        
        # First insert succeeds, second fails
        mock_insert.side_effect = [1, Exception("DB error")]

        result = fetch_and_store_exchange_rates()

        assert result["status"] == "ok"
        assert result["inserted"] == 1
        assert result["total"] == 2
        assert len(result["errors"]) == 1
        assert "oficial" in result["errors"][0]

    @patch('app.fetch_exchange.httpx.get')
    def test_fetch_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        import httpx
        mock_get.side_effect = httpx.HTTPError("Connection failed")

        result = fetch_and_store_exchange_rates()

        assert result["status"] == "error"
        assert "HTTP error" in result["message"]
        assert "Connection failed" in result["message"]

    @patch('app.fetch_exchange.httpx.get')
    def test_fetch_json_parse_error(self, mock_get):
        """Test handling of JSON parsing errors."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = fetch_and_store_exchange_rates()

        assert result["status"] == "error"
        assert "Invalid JSON" in result["message"]

    @patch('app.fetch_exchange.httpx.get')
    @patch('app.fetch_exchange.db.insert_exchange')
    def test_exchange_object_creation(self, mock_insert, mock_get):
        """Test that Exchange objects are created correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "moneda": "USD",
                "casa": "blue",
                "nombre": "Blue",
                "compra": 1415.5,
                "venta": 1435.5,
                "fechaActualizacion": "2025-11-06T19:58:00.000Z"
            }
        ]
        mock_get.return_value = mock_response
        mock_insert.return_value = 1

        result = fetch_and_store_exchange_rates()

        assert result["status"] == "ok"
        exchange_data = result["exchanges"][0]
        assert exchange_data["moneda"] == "USD"
        assert exchange_data["casa"] == "blue"
        assert exchange_data["nombre"] == "Blue"
        assert exchange_data["compra"] == 1415.5
        assert exchange_data["venta"] == 1435.5

    @patch('app.fetch_exchange.httpx.get')
    @patch('app.fetch_exchange.db.insert_exchange')
    def test_rate_calculation(self, mock_insert, mock_get):
        """Test that rate and diff are calculated correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "moneda": "USD",
                "casa": "blue",
                "nombre": "Blue",
                "compra": 1400,
                "venta": 1600,
                "fechaActualizacion": "2025-11-06T19:58:00.000Z"
            }
        ]
        mock_get.return_value = mock_response
        mock_insert.return_value = 1

        result = fetch_and_store_exchange_rates()

        # Verify insert was called with correct calculated values
        call_args = mock_insert.call_args[0]
        buy = call_args[1]
        sell = call_args[2]
        rate = call_args[3]
        diff = call_args[4]
        
        assert buy == Decimal("1400")
        assert sell == Decimal("1600")
        assert rate == Decimal("1500")  # (1400 + 1600) / 2
        assert diff == Decimal("200")   # 1600 - 1400


class TestExchangeModel:
    """Test suite for the Exchange model."""

    def test_exchange_initialization(self):
        """Test Exchange object initialization."""
        exchange = Exchange(
            moneda="USD",
            nombre="Blue",
            casa="blue",
            compra=1415,
            venta=1435,
            fechaActualizacion="2025-11-06T19:58:00.000Z"
        )

        assert exchange.moneda == "USD"
        assert exchange.nombre == "Blue"
        assert exchange.casa == "blue"
        assert exchange.compra == 1415
        assert exchange.venta == 1435
        assert exchange.fechaActualizacion == "2025-11-06T19:58:00.000Z"

    def test_exchange_repr(self):
        """Test Exchange string representation."""
        exchange = Exchange(
            moneda="USD",
            nombre="Blue",
            casa="blue",
            compra=1415,
            venta=1435,
            fechaActualizacion="2025-11-06T19:58:00.000Z"
        )

        repr_str = repr(exchange)
        assert "blue" in repr_str
        assert "1415" in repr_str
        assert "1435" in repr_str
