from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import products

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске (в продакшене лучше использовать миграции)
    Base.metadata.create_all(bind=engine)
    yield
    # Действия при остановке приложения

app = FastAPI(
    title="Warehouse Goods Service",
    description="Микросервис для управления товарами на складе",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Warehouse Goods Service is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)