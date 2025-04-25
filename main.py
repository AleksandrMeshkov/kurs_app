from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from app.routing.main_router import main_router

# Создаем папку для загрузок, если её нет
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="PlayPlace",
    description="Платформа для поиска спортивных площадок",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Подключаем основной роутер
app.include_router(main_router)

# Настраиваем доступ к статическим файлам
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Добавляем middleware для CORS (если нужно)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Для разработки с автоматической перезагрузкой
    )