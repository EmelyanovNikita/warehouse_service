# app/models/schemas.py
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Union

# Базовые схемы для создания
class ProductCreate(BaseModel):
    name: str
    category_id: int
    sku: str
    base_price: Decimal
    total_quantity: int = 0
    is_active: bool = True

# Схемы из БД
class ProductInDB(ProductCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ОТВЕТЫ ДЛЯ КЛИЕНТОВ (минимальная информация)
class ProductClientResponse(BaseModel):
    id: int
    name: str
    sku: str
    base_price: Decimal
    total_quantity: int
    category_id: int

# ОТВЕТЫ ДЛЯ АДМИНОВ (полная информация)
class ProductAdminResponse(ProductClientResponse):
    is_active: bool
    created_at: datetime
    updated_at: datetime
    low_stock_alert: bool = Field(False, description="Флаг низкого остатка")

# Специфичные атрибуты
class ServerAttributes(BaseModel):
    ram_gb: int
    cpu_model: str
    cpu_cores: int
    hdd_size_gb: Optional[int] = None
    ssd_size_gb: Optional[int] = None
    form_factor: str
    manufacturer: str

class ThermocupAttributes(BaseModel):
    volume_ml: int
    color: str
    brand: str
    model: Optional[str] = None
    is_hermetic: bool
    material: Optional[str] = None

# Комбинированные ответы с атрибутами
class ServerProductClientResponse(ProductClientResponse):
    attributes: ServerAttributes

class ServerProductAdminResponse(ProductAdminResponse):
    attributes: ServerAttributes

class ThermocupProductClientResponse(ProductClientResponse):
    attributes: ThermocupAttributes

class ThermocupProductAdminResponse(ProductAdminResponse):
    attributes: ThermocupAttributes