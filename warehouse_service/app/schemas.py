from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
# from sqlalchemy.types import Decimal
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(String)  # Изменяем с Text на String
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    sku = Column(String(100), unique=True)
    base_price = Column(Numeric(10, 2))  # Соответствует decimal(10,2) в БД
    total_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    category = relationship("Category", back_populates="products")
    stocks = relationship("ProductStock", back_populates="product")
    server_attributes = relationship("ProductAttributesServer", back_populates="product", uselist=False)
    thermocup_attributes = relationship("ProductAttributesThermocup", back_populates="product", uselist=False)

class ProductAttributesServer(Base):
    __tablename__ = 'product_attributes_servers'
    
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    ram_gb = Column(Integer)
    cpu_model = Column(String(255))
    cpu_cores = Column(Integer)
    hdd_size_gb = Column(Integer)
    ssd_size_gb = Column(Integer)
    form_factor = Column(String(50))
    manufacturer = Column(String(255))
    
    product = relationship("Product", back_populates="server_attributes")

class ProductAttributesThermocup(Base):
    __tablename__ = 'product_attributes_thermocups'
    
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    volume_ml = Column(Integer)
    color = Column(String(100))
    brand = Column(String(255))
    model = Column(String(255))
    is_hermetic = Column(Boolean)
    material = Column(String(100))
    
    product = relationship("Product", back_populates="thermocup_attributes")

class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    address = Column(String)  # Изменяем с Text на String
    
    stocks = relationship("ProductStock", back_populates="warehouse")

class ProductStock(Base):
    __tablename__ = 'product_stocks'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    quantity = Column(Integer, default=0)
    
    product = relationship("Product", back_populates="stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")