"""Exchange class for representing exchange rate data from DolarAPI."""
from typing import Optional


class Exchange:
    """Exchange rate representation from DolarAPI."""

    def __init__(
        self,
        moneda: str,
        nombre: str,
        casa: str,
        compra: float,
        venta: float,
        fechaActualizacion: str
    ) -> None:
        self.moneda = moneda
        self.nombre = nombre
        self.casa = casa
        self.compra = compra
        self.venta = venta
        self.fechaActualizacion = fechaActualizacion

    def __repr__(self):
        return f"<Exchange casa={self.casa} compra={self.compra} venta={self.venta}>"
