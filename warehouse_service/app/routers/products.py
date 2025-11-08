from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from app.models import ProductResponse
from app.models import ProductCreateThermocup

# Импортируем зависимости из твоего проекта
from app.database import get_db

router = APIRouter()

# ==================== PUBLIC ENDPOINTS ====================

# ==================== Получение всех товаров (в том числе и с категорями/спецификациями) =====================

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

# ==================== Получение товара по ID =====================

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

# ==================== СПЕЦИАЛИЗИРОВАННЫЕ ФИЛЬТРЫ ====================

# ==================== Запрос на создание Termos =====================

@router.post("/thermocups/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_thermocup(
    product_data: ProductCreateThermocup,
    db: Session = Depends(get_db)
):
    print("LOG: create_thermocup: запрос получен: %s", product_data.name)
    """
    Создать новую термокружку
    
    - **name**: Название термокружки
    - **category_id**: ID категории (должна быть категория 'thermocups')
    - **base_price**: Базовая цена
    - **initial_quantity**: Начальное количество (опционально)
    - **warehouse_id**: ID склада для начального размещения (опционально)
    - **attributes**: Специфичные атрибуты термокружки
        - **volume_ml**: Объем в миллилитрах
        - **color**: Цвет
        - **brand**: Бренд
        - **model**: Модель (опционально)
        - **is_hermetic**: Герметичность (по умолчанию true)
        - **material**: Материал (опционально)
        - **path_to_photo**:  Путь к фото (url-link) (опционально)
    """
    try:
        print("LOG: create_thermocup: try: %s", product_data.name)
        # Вызываем хранимую процедуру для создания термокружки
        result = db.execute(
            text("CALL CreateThermos(:name, :category_id, :base_price, :initial_quantity, :warehouse_id, :volume_ml, :color, :brand, :model, :is_hermetic, :material, :path_to_photo)"),
            {
                'name': product_data.name,
                'category_id': product_data.category_id,
                'base_price': product_data.base_price,
                # 'description': product_data.description,
                'initial_quantity': product_data.initial_quantity,
                'warehouse_id': product_data.warehouse_id,
                'volume_ml': product_data.attributes.volume_ml,
                'color': product_data.attributes.color,
                'brand': product_data.attributes.brand,
                'model': product_data.attributes.model or '',
                'is_hermetic': 1 if product_data.attributes.is_hermetic else 0,
                'material': product_data.attributes.material or '',
                'path_to_photo': product_data.path_to_photo or ''
            }
        )
        
        print("LOG: create_thermocup: Получаем созданный товар: %s", product_data.name)
        # Получаем созданный товар
        new_product = result.fetchone()
        
        # Фиксируем изменения в БД
        db.commit()
        
        print("LOG: create_thermocup: thermocup added: ", product_data.name)
        return dict(new_product._mapping)
        
    except Exception as e:
        # Откатываем изменения в случае ошибки
        db.rollback()
        
        # Обрабатываем возможные ошибки БД
        error_msg = str(e)
        if "Duplicate entry" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким названием уже существует"
            )
        elif "Category not found" in error_msg or "foreign key constraint fails" in error_msg and "category_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанная категория не существует"
            )
        elif "foreign key constraint fails" in error_msg and "warehouse_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Указанный склад не существует"
            )
        elif "thermocups" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверная категория для термокружки. Убедитесь что category_id соответствует категории 'thermocups'"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании термокружки: {error_msg}"
            )