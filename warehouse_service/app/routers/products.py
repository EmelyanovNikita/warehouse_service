from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from app.models import ProductResponse

# Импортируем зависимости из твоего проекта
from app.database import get_db
# from app.auth import get_current_user_role, require_admin  # если есть своя аутентификация

router = APIRouter()

# ==================== ЗАВИСИМОСТИ ====================

# Временные заглушки (замени на свою систему аутентификации)
def get_current_user_role(request: Request):
    """Заглушка - замени на свою логику аутентификации"""
    # Пример: проверка JWT токена, сессии и т.д.
    return request.headers.get("X-User-Role", "user")  # временно из заголовка

def require_admin(user_role: str = Depends(get_current_user_role)):
    """Зависимость для проверки админских прав"""
    if user_role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user_role

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    include_inactive: bool = Query(False, description="Включать неактивные товары"),
    include_out_of_stock: bool = Query(False, description="Включать товары не в наличии"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: Session = Depends(get_db)
):
    """
    Получить список товаров с фильтрами
    
    - **category**: Фильтр по названию категории
    - **min_price**: Минимальная цена
    - **max_price**: Максимальная цена  
    - **search**: Поиск по названию товара
    - **include_inactive**: Показать неактивные товары (по умолчанию false)
    - **include_out_of_stock**: Показать товары не в наличии (по умолчанию false)
    - **limit**: Количество записей (по умолчанию 50)
    - **offset**: Смещение для пагинации (по умолчанию 0)
    """
    try:
        result = db.execute(
            text("CALL GetProducts(:category, :min_price, :max_price, :search, :include_inactive, :include_out_of_stock, :limit, :offset)"),
            {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'search': search,
                'include_inactive': include_inactive,
                'include_out_of_stock': include_out_of_stock,
                'limit': limit,
                'offset': offset
            }
        )
        
        products = result.fetchall()
        return [dict(product._mapping) for product in products]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить товар по ID
    
    - **product_id**: ID товара
    """
    try:
        result = db.execute(
            text("CALL GetProductById(:product_id)"),
            {'product_id': product_id}
        )
        
        product = result.fetchone()
        
        if not product:
            raise HTTPException(
                status_code=404, 
                detail=f"Product with ID {product_id} not found"
            )
            
        return dict(product._mapping)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/products")
def get_products_admin(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    include_inactive: bool = Query(True, description="Включать неактивные товары"),
    include_out_of_stock: bool = Query(True, description="Включать товары не в наличии"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin_role: str = Depends(require_admin)
):
    """Получить все товары (админская версия)"""
    try:
        result = db.execute(
            text("CALL GetProductsForAdmins(:category, :min_price, :max_price, :search, :include_inactive, :include_out_of_stock, :limit, :offset)"),
            {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'search': search,
                'include_inactive': include_inactive,
                'include_out_of_stock': include_out_of_stock,
                'limit': limit,
                'offset': offset
            }
        )
        products = result.fetchall()
        return [dict(product._mapping) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/admin/products/{product_id}")
def get_product_admin(
    product_id: int,
    db: Session = Depends(get_db),
    admin_role: str = Depends(require_admin)
):
    """Получить товар по ID (админская версия со всеми полями)"""
    try:
        result = db.execute(
            text("CALL GetProductByIdForAdmin(:product_id)"),
            {'product_id': product_id}
        )
        
        product = result.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return dict(product._mapping)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ==================== СПЕЦИАЛИЗИРОВАННЫЕ ФИЛЬТРЫ ====================

@router.get("/category/thermocups")
def get_thermocups(
    volume_min: Optional[int] = Query(None, ge=0),
    volume_max: Optional[int] = Query(None, ge=0),
    color: Optional[str] = None,
    brand: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Получить термокружки с фильтрами (публичная версия)"""
    try:
        # Здесь нужно создать процедуру GetThermocupsForUsers или использовать существующую
        result = db.execute(
            text("CALL GetThermocupsByVolume(:volume_min, :volume_max, :color, :brand, :limit, :offset)"),
            {
                'volume_min': volume_min,
                'volume_max': volume_max,
                'color': color,
                'brand': brand,
                'limit': limit,
                'offset': offset
            }
        )
        products = result.fetchall()
        return [dict(product._mapping) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/category/servers")
def get_servers(
    ram_min: Optional[int] = Query(None, ge=0),
    cpu_cores_min: Optional[int] = Query(None, ge=0),
    form_factor: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Получить серверы с фильтрами (публичная версия)"""
    try:
        # Здесь нужно создать процедуру GetServersForUsers
        result = db.execute(
            text("CALL GetServersBySpecs(:ram_min, :cpu_cores_min, :form_factor, :limit, :offset)"),
            {
                'ram_min': ram_min,
                'cpu_cores_min': cpu_cores_min,
                'form_factor': form_factor,
                'limit': limit,
                'offset': offset
            }
        )
        products = result.fetchall()
        return [dict(product._mapping) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")