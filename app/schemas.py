from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: Optional[str] = Field(None, max_length=50, description="Codice prodotto")
    name: str = Field(..., min_length=1, max_length=255, description="Nome del prodotto")
    category: Optional[str] = Field(None, max_length=255, description="Categoria del prodotto")
    lot_number: Optional[str] = Field(None, max_length=100, description="Numero lotto")
    unit: Optional[str] = Field(None, max_length=50, description="Unità di misura")
    current_stock: float = Field(0.0, ge=0, description="Quantità attuale in magazzino")
    reorder_point: Optional[float] = Field(None, ge=0, description="Soglia di riordino")
    expiry_date: Optional[date] = Field(None, description="Data di scadenza opzionale")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Il nome del prodotto non può essere vuoto")
        return cleaned


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=255)
    lot_number: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    current_stock: Optional[float] = Field(None, ge=0)
    reorder_point: Optional[float] = Field(None, ge=0)
    expiry_date: Optional[date] = Field(None)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Il nome del prodotto non può essere vuoto")
        return cleaned


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime


class StockMovementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movement_type: Literal["carico", "scarico"] = Field(..., description="Tipo di movimento")
    quantity: float = Field(..., gt=0, description="Quantità del movimento")
    movement_date: date = Field(..., description="Data del movimento")
    note: Optional[str] = Field(None, max_length=500, description="Nota opzionale")

    @field_validator("movement_date")
    @classmethod
    def validate_movement_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La data del movimento non può essere futura")
        return value


class StockMovementCreate(StockMovementBase):
    product_id: int = Field(..., gt=0, description="Identificativo del prodotto")


class StockMovementResponse(StockMovementBase):
    id: int
    product_id: int
    created_at: datetime
    name: str | None = None
    unit: str | None = None
    current_stock: float | None = None


class ProductStockStatus(BaseModel):
    product_id: int
    current_stock: float
    reorder_point: Optional[float]
    needs_reorder: bool
    suggested_order_quantity: Optional[float]
    data_insufficient: bool = False


class ProductDetailResponse(ProductResponse):
    stock_status: ProductStockStatus


class AlertResponse(BaseModel):
    product_id: int
    name: str
    current_stock: float
    reorder_point: float
    suggested_order_quantity: float
    urgency_ratio: float
    data_insufficient: bool = False
