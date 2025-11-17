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

# ====================== Create =========================
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

# ==================== Update ===============================
class ProductUpdateBase(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    base_price: Optional[float] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None
    path_to_photo: Optional[str] = None
    num_reserved_goods: Optional[int] = 0

class ThermocupAttributesUpdate(BaseModel):
    volume_ml: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    is_hermetic: Optional[bool] = None
    material: Optional[str] = None

class ProductUpdateThermocup(ProductUpdateBase):
    attributes: Optional[ThermocupAttributesUpdate] = None

class UpdateReservedGoodsRequest(BaseModel):
    quantity_change: int

class UpdateStockQuantityRequest(BaseModel):
    warehouse_id: int
    quantity_change: int

class ReservedGoodsResponse(BaseModel):
    id: int
    name: str
    reserved_quantity: int
    total_quantity: int
    available_quantity: int

class StockQuantityResponse(BaseModel):
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    current_quantity: int
    total_quantity_all_warehouses: int

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    category_name: str
    base_price: float

    total_quantity: int
    num_reserved_goods: Optional[int] = 0
    is_active: bool

    # Time of create/update of product
    created_at: datetime
    updated_at: Optional[datetime] = None
    path_to_photo: Optional[str] = None

    class Config:
        from_attributes = True

class ThermocupResponse(ProductResponse):
    # Специфичные атрибуты термокружки
    volume_ml: int
    color: str
    brand: str
    model: Optional[str] = None
    is_hermetic: bool
    material: Optional[str] = None
    # Информация по складам
    warehouse_info: Optional[str] = None