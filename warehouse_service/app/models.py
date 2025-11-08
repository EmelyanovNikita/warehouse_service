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

class ProductCreateBase(BaseModel):
    name: str
    category_id: int
    base_price: float
    # description: Optional[str] = None
    initial_quantity: Optional[int] = None  # Может быть не указано
    warehouse_id: Optional[int] = None      # Может быть не указано
    path_to_photo: Optional[str] = None

# Модель для создания термокружки
class ProductCreateThermocup(ProductCreateBase):
    attributes: ThermocupAttributes

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    category_name: str
    base_price: float

    total_quantity: int #удалить
    is_active: bool

    # Time of create/update of product
    created_at: datetime
    updated_at: Optional[datetime] = None

    # check
    volume_ml: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    ram_gb: Optional[int] = None
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    form_factor: Optional[str] = None
    manufacturer: Optional[str] = None

    class Config:
        from_attributes = True