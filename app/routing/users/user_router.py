from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.user_service.user_service import UserService
from app.security.jwtmanager import JWTManager
from app.security.hasher import verify_password
from app.models.models import User
from app.security.jwttype import JWTType
from app.schemas.request.users.user_registration_schema import UserRegistration
from app.schemas.request.users.user_update_schema import UserUpdate

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register(
    login: str,
    email: str,
    PasswordHash: str,
    name: str = None,
    surname: str = None,
    patronymic: str = None,
    city: str = None,
    phone: str = None,
    photourl: str = None,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    # Проверяем, существует ли пользователь с таким логином
    existing_user = await user_service.get_user_by_login(login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    
    # Создаём объект UserRegistration
    user_data = UserRegistration(
        Login=login,
        Email=email,
        PasswordHash=PasswordHash,
        Name=name,
        Surname=surname,
        Patronymic=patronymic,
        City=city,
        Phone=phone,
        PhotoURL = photourl
    )
    
    # Регистрируем пользователя
    user = await user_service.register(user_data)
    return {"message": "User created successfully", "user_id": user.UserID}

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    # Аутентифицируем пользователя
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if isinstance(user, str):  # Если возвращается строка, это ошибка
        raise HTTPException(status_code=400, detail=user)
    
    # Создаём JWT-токен
    jwt_manager = JWTManager()
    access_token = jwt_manager.create_token(user.UserID, JWTType.ACCESS)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    # Получаем пользователя по ID
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    name: str = None,
    surname: str = None,
    patronymic: str = None,
    city: str = None,
    phone: str = None,
    photourl: str = None,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    # Создаём объект UserUpdate
    update_data = UserUpdate(
        Name=name,
        Surname=surname,
        Patronymic=patronymic,
        City=city,
        Phone=phone,
        PhotoURL=photourl
    )
    
    # Обновляем данные пользователя
    user = await user_service.update_profile(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}