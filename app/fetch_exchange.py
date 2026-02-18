"""Fetch exchange rate data from external API and store in database."""
import logging
import httpx
from decimal import Decimal
from typing import List, Dict, Any
from . import db
from .dolar_api import DolarApiRate

logger = logging.getLogger(__name__)


def fetch_and_store_exchange_rates() -> Dict[str, Any]:
    """
    Fetch exchange rates from dolarapi.com and store them in the database.
    
    Returns a dict with status and count of records inserted.
    """
    try:
        # Fetch data from external API
        response = httpx.get("https://dolarapi.com/v1/dolares", timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        inserted_count = 0
        errors = []
        exchanges = []
        
        # Create Exchange objects and insert each exchange rate into the database
        for item in data:
            try:
                # Create Exchange object with API data
                exchange = DolarApiRate(
                    moneda=item.get("moneda", "USD"),
                    nombre=item.get("nombre", ""),
                    casa=item.get("casa", "unknown"),
                    compra=item.get("compra", 0),
                    venta=item.get("venta", 0),
                    fechaActualizacion=item.get("fechaActualizacion", "")
                )
                exchanges.append(exchange)
                
                # Map Exchange object to DB schema
                # type = casa (official, blue, etc.)
                # buy = compra
                # sell = venta
                # rate = average of buy/sell
                # diff = sell - buy
                
                buy = Decimal(str(exchange.compra))
                sell = Decimal(str(exchange.venta))
                rate = (buy + sell) / 2
                diff = sell - buy
                
                db.insert_exchange(exchange.casa, buy, sell, rate, diff)
                inserted_count += 1
                
            except Exception as e:
                logger.warning("Failed to insert rate for %s: %s", item.get("casa", "unknown"), e)
                errors.append(f"Error inserting {item.get('casa', 'unknown')}: {str(e)}")
        
        return {
            "status": "ok",
            "inserted": inserted_count,
            "total": len(data),
            "exchanges": [
                {
                    "moneda": ex.moneda,
                    "nombre": ex.nombre,
                    "casa": ex.casa,
                    "compra": ex.compra,
                    "venta": ex.venta,
                    "fechaActualizacion": ex.fechaActualizacion
                }
                for ex in exchanges
            ],
            "errors": errors if errors else None
        }
        
    except httpx.HTTPError as e:
        return {
            "status": "error",
            "message": f"HTTP error fetching data: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }
