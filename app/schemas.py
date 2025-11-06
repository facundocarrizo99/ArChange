"""Pydantic schemas for API request/response validation and OpenAPI documentation."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ExchangeResponse(BaseModel):
    """Exchange rate record response schema."""
    
    id: int = Field(..., description="Unique identifier for the exchange rate record")
    type: str = Field(..., description="Exchange rate type (e.g., 'oficial', 'blue', 'bolsa')")
    buy: Optional[float] = Field(None, description="Buy price/rate in ARS")
    sell: Optional[float] = Field(None, description="Sell price/rate in ARS")
    rate: Optional[float] = Field(None, description="Average rate between buy and sell")
    diff: Optional[float] = Field(None, description="Difference between sell and buy")
    created_at: Optional[str] = Field(None, description="Timestamp when the record was created")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "type": "blue",
                "buy": 1415.0,
                "sell": 1435.0,
                "rate": 1425.0,
                "diff": 20.0,
                "created_at": "2025-11-06T19:58:00.000Z"
            }
        }


class ExchangeCreate(BaseModel):
    """Schema for creating a new exchange rate record."""
    
    type: str = Field(..., description="Exchange rate type", min_length=1)
    buy: Optional[float] = Field(None, description="Buy price/rate in ARS", ge=0)
    sell: Optional[float] = Field(None, description="Sell price/rate in ARS", ge=0)
    rate: Optional[float] = Field(None, description="Average rate", ge=0)
    diff: Optional[float] = Field(None, description="Price difference")

    class Config:
        schema_extra = {
            "example": {
                "type": "blue",
                "buy": 1415.0,
                "sell": 1435.0,
                "rate": 1425.0,
                "diff": 20.0
            }
        }


class ExchangeData(BaseModel):
    """Exchange data from DolarAPI."""
    
    moneda: str = Field(..., description="Currency code (e.g., 'USD')")
    nombre: str = Field(..., description="Exchange rate name")
    casa: str = Field(..., description="Exchange house type")
    compra: float = Field(..., description="Buy price")
    venta: float = Field(..., description="Sell price")
    fechaActualizacion: str = Field(..., description="Last update timestamp")


class FetchExchangeResponse(BaseModel):
    """Response from fetching exchange rates from external API."""
    
    status: str = Field(..., description="Operation status ('ok' or 'error')")
    inserted: Optional[int] = Field(None, description="Number of records successfully inserted")
    total: Optional[int] = Field(None, description="Total number of records fetched")
    exchanges: Optional[List[ExchangeData]] = Field(None, description="List of fetched exchange rates")
    errors: Optional[List[str]] = Field(None, description="List of errors if any occurred")
    message: Optional[str] = Field(None, description="Error message if status is 'error'")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "inserted": 7,
                "total": 7,
                "exchanges": [
                    {
                        "moneda": "USD",
                        "nombre": "Blue",
                        "casa": "blue",
                        "compra": 1415.0,
                        "venta": 1435.0,
                        "fechaActualizacion": "2025-11-06T19:58:00.000Z"
                    }
                ],
                "errors": None
            }
        }


class ExchangeListResponse(BaseModel):
    """Response containing a list of exchange rates."""
    
    status: str = Field(..., description="Operation status")
    data: List[ExchangeResponse] = Field(..., description="List of exchange rate records")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "data": [
                    {
                        "id": 1,
                        "type": "blue",
                        "buy": 1415.0,
                        "sell": 1435.0,
                        "rate": 1425.0,
                        "diff": 20.0,
                        "created_at": "2025-11-06T19:58:00.000Z"
                    }
                ]
            }
        }


class ExchangeCreateResponse(BaseModel):
    """Response after creating an exchange rate."""
    
    status: str = Field(..., description="Operation status")
    data: ExchangeResponse = Field(..., description="The created exchange rate record")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    status: str = Field("error", description="Status will be 'error'")
    message: str = Field(..., description="Error message describing what went wrong")

    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Database connection failed"
            }
        }
