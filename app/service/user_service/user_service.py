from typing import Union, Dict, Any
from app.models.models import User
from app.schemas.request.users.user_auth_schema import UserAuth
from app.schemas.request.users.user_registration_schema import UserRegistration
from app.schemas.request.users.user_update_schema import UserUpdate
from app.database.database import *
from app.security.hasher import hash_password
from app.security.hasher import verify_password
from sqlalchemy import select, insert, update
from fastapi import HTTPException, UploadFile, status
import os
import uuid
from fastapi.responses import JSONResponse
from pathlib import Path

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self, **kwargs):
        query = select(User).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_by_login(self, login: str) -> Union[User, None]:
        """Получить пользователя по логину."""
        query = select(User).where(User.Login == login)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        """Получить пользователя по ID."""
        query = select(User).where(User.UserID == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def register(self, request: UserRegistration):
        """Регистрация нового пользователя."""
        existing_user_by_login = await self.get_user_by_login(request.Login)
        if existing_user_by_login:
            raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

        existing_user_by_email = await self.get_profile(Email=request.Email)
        if existing_user_by_email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        # Если при регистрации передается PhotoURL, оставляем как есть
        photo_url = request.PhotoURL
        if photo_url and not photo_url.startswith(('http://', 'https://')):
            photo_url = f"http://212.20.53.169:13299/uploads/{photo_url}"

        query = (
            insert(User)
            .values(
                Login=request.Login,
                Email=request.Email,
                PasswordHash=hash_password(request.PasswordHash),
                Name=request.Name,
                Surname=request.Surname,
                Patronymic=request.Patronymic,
                City=request.City,
                Phone=request.Phone,
                PhotoURL=photo_url
            )
            .returning(User)
        )

        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при регистрации пользователя: {str(e)}")

    async def update_profile(self, UserID: int, data: Dict[str, Any], photo_file: UploadFile = None):
        """Обновление профиля пользователя с возможной загрузкой фото."""
        existing_user = await self.get_user_by_id(UserID)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обработка загружаемого файла
        if photo_file:
            try:
                file_name = await self.save_uploaded_file(photo_file)
                # Сохраняем полный URL в базу данных
                data['PhotoURL'] = f"http://212.20.53.169:13299/uploads/{file_name}"
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при обработке файла: {str(e)}"
                )

        # Если передается пароль, хэшируем его
        if 'Password' in data and data['Password'] is not None:
            data['PasswordHash'] = hash_password(data['Password'])
            del data['Password']

        update_fields = {k: v for k, v in data.items() if v is not None}

        if not update_fields:
            return existing_user  # Возвращаем неизмененного пользователя

        query = update(User).where(User.UserID == UserID).values(**update_fields).returning(User)
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            updated_user = result.scalars().first()
            return updated_user
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении профиля: {str(e)}"
            )

    async def authorize(self, Login: str, PasswordHash: str):
        """Авторизация пользователя."""
        authenticated = await self.authenticate_user(Login, PasswordHash)
        if isinstance(authenticated, str):
            raise HTTPException(
                status_code=401,
                detail="Неправильный логин или пароль"
            )
        return authenticated

    async def authenticate_user(self, Login: str, PasswordHash: str) -> Union[User, str]:
        """Аутентификация пользователя."""
        user = await self.get_user_by_login(Login)
        if not user:
            return "User not found"
        if not verify_password(PasswordHash, user.PasswordHash):
            return "Invalid password"
        return user
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
        """Сохраняет загруженный файл в указанную директорию."""
        # Проверяем и создаем директорию при необходимости
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Генерируем уникальное имя файла с сохранением расширения
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя файла отсутствует"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.gif']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый формат файла"
            )
        
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_path / file_name
        
        # Сохраняем файл
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_name
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении файла: {str(e)}"
            )