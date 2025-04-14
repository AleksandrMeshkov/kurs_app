from fastapi import FastAPI, APIRouter
from app.routing.users.user_router import router as user_router
from app.routing.platform.platform_router import router as platform_router
from app.routing.events.events_router import router as event_router  # Импортируем роутер для событий

# Создаем главный роутер с префиксом /v1
main_router = APIRouter(
    prefix="/v1"
)

# Включаем роутер для пользователей
main_router.include_router(user_router, tags=["Users"])

# Включаем роутер для площадок
main_router.include_router(platform_router, tags=["Platforms"])

# Включаем роутер для событий
main_router.include_router(event_router, tags=["Events"])  # Добавляем роутер для событий