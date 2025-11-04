from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import schemas
from app import models

router = APIRouter(prefix="/products", tags=["products"])

# Для клиентов - ограниченная информация
@router.get("/", response_model=list[models.ProductClientResponse])
def get_all_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все товары (клиентская версия)"""
    try:
        products = db.query(schemas.Product).filter(
            schemas.Product.is_active == True
        ).offset(skip).limit(limit).all()
        
        result = []
        for product in products:
            result.append(models.ProductClientResponse(
                id=product.id,
                name=product.name,
                sku=product.sku,
                base_price=product.base_price,
                total_quantity=product.total_quantity,
                category_id=product.category_id
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Для админов - полная информация
@router.get("/admin/", response_model=list[models.ProductAdminResponse])
def get_all_products_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все товары (админская версия)"""
    try:
        products = db.query(schemas.Product).offset(skip).limit(limit).all()
        
        result = []
        for product in products:
            # Проверяем низкий остаток (например, меньше 10)
            low_stock_alert = product.total_quantity < 10
            
            result.append(models.ProductAdminResponse(
                id=product.id,
                name=product.name,
                sku=product.sku,
                base_price=product.base_price,
                total_quantity=product.total_quantity,
                category_id=product.category_id,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at,
                low_stock_alert=low_stock_alert
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID (клиентская версия)"""
    try:
        product = db.query(schemas.Product).filter(
            schemas.Product.id == product_id,
            schemas.Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Получаем информацию о категории
        category = db.query(schemas.Category).filter(
            schemas.Category.id == product.category_id
        ).first()
        
        # Определяем тип товара и получаем атрибуты
        product_data = models.ProductClientResponse(
            id=product.id,
            name=product.name,
            sku=product.sku,
            base_price=product.base_price,
            total_quantity=product.total_quantity,
            category_id=product.category_id
        )
        
        # Добавляем атрибуты в зависимости от категории
        response_data = {"product": product_data}
        
        # Если есть категория, можно добавить логику для атрибутов
        if category:
            response_data["category_name"] = category.name
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/admin/{product_id}")
def get_product_admin(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID (админская версия)"""
    try:
        product = db.query(schemas.Product).filter(
            schemas.Product.id == product_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Получаем информацию о категории
        category = db.query(schemas.Category).filter(
            schemas.Category.id == product.category_id
        ).first()
        
        # Проверяем низкий остаток
        low_stock_alert = product.total_quantity < 10
        
        product_data = models.ProductAdminResponse(
            id=product.id,
            name=product.name,
            sku=product.sku,
            base_price=product.base_price,
            total_quantity=product.total_quantity,
            category_id=product.category_id,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
            low_stock_alert=low_stock_alert
        )
        
        response_data = {"product": product_data}
        
        # Получаем специфичные атрибуты в зависимости от категории
        if category:
            response_data["category_name"] = category.name
            
            # Для серверов
            if "server" in category.name.lower():
                server_attrs = db.query(schemas.ProductAttributesServer).filter(
                    schemas.ProductAttributesServer.product_id == product_id
                ).first()
                if server_attrs:
                    response_data["server_attributes"] = server_attrs
            
            # Для термокружек
            elif "thermocup" in category.name.lower():
                thermocup_attrs = db.query(schemas.ProductAttributesThermocup).filter(
                    schemas.ProductAttributesThermocup.product_id == product_id
                ).first()
                if thermocup_attrs:
                    response_data["thermocup_attributes"] = thermocup_attrs
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search/{product_name}")
def search_product_by_name(product_name: str, db: Session = Depends(get_db)):
    """Поиск товара по названию (клиентская версия)"""
    try:
        product = db.query(schemas.Product).filter(
            func.lower(schemas.Product.name).like(f"%{product_name.lower()}%"),
            schemas.Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "product": models.ProductClientResponse(
                id=product.id,
                name=product.name,
                sku=product.sku,
                base_price=product.base_price,
                total_quantity=product.total_quantity,
                category_id=product.category_id
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/category/{category_name}")
def get_products_by_category(category_name: str, db: Session = Depends(get_db)):
    """Получить товары по категории (клиентская версия)"""
    try:
        # Находим категорию
        category = db.query(schemas.Category).filter(
            func.lower(schemas.Category.name) == func.lower(category_name)
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Находим товары этой категории
        products = db.query(schemas.Product).filter(
            schemas.Product.category_id == category.id,
            schemas.Product.is_active == True
        ).all()
        
        products_data = []
        for product in products:
            products_data.append(models.ProductClientResponse(
                id=product.id,
                name=product.name,
                sku=product.sku,
                base_price=product.base_price,
                total_quantity=product.total_quantity,
                category_id=product.category_id
            ))
        
        return {
            "category": category.name,
            "products": products_data,
            "total_count": len(products_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")