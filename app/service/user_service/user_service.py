from typing import Union
from app.models.models import User
from app.schemas.request.users.user_auth_schema import UserAuth
from app.schemas.request.users.user_registration_schema import UserRegistration
from app.schemas.request.users.user_update_schema import UserUpdate
from app.database.database import *
from app.security.hasher import hash_password
from app.security.hasher import verify_password
from sqlalchemy import select, insert, update
from fastapi import HTTPException

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self, **kwargs):
        query = select(User).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_by_login(self, login: str) -> Union[User, None]:
        """
        Получить пользователя по логину.
        """
        query = select(User).where(User.Login == login)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        """
        Получить пользователя по ID.
        """
        query = select(User).where(User.UserID == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def register(self, request: UserRegistration):
        """
        Регистрация нового пользователя.
        """
        # Проверяем, существует ли пользователь с таким логином
        existing_user_by_login = await self.get_user_by_login(request.Login)
        if existing_user_by_login:
            raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

        # Проверяем, существует ли пользователь с таким email
        existing_user_by_email = await self.get_profile(Email=request.Email)
        if existing_user_by_email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        query = (
            insert(User)
            .values(
                Login=request.Login,
                Email=request.Email,
                PasswordHash=hash_password(request.PasswordHash),  # Хэшируем пароль
                Name=request.Name,
                Surname=request.Surname,
                Patronymic=request.Patronymic,
                City=request.City,
                Phone=request.Phone,
                PhotoURL =request.PhotoURL
    

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

    async def update_profile(self, UserID: int, data: UserUpdate):
        """
        Обновление профиля пользователя.
        """
        # Проверяем, существует ли пользователь
        existing_user = await self.get_user_by_id(UserID)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        data_dict = data.dict(exclude_unset=True)

        update_fields = {}
        for key, value in data_dict.items():
            if value is not None:
                update_fields[key] = value

        if not update_fields:
            return None

        query = update(User).where(User.UserID == UserID).values(update_fields).returning(User)
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении профиля: {str(e)}")

    async def authorize(self, Login: str, PasswordHash: str):
        """
        Авторизация пользователя.
        """
        authenticated = await self.authenticate_user(Login, PasswordHash)
        if isinstance(authenticated, str):
            raise HTTPException(
                status_code=401,
                detail="Неправильный логин или пароль"
            )
        return authenticated

    async def authenticate_user(self, Login: str, PasswordHash: str) -> Union[User, str]:
        """
        Аутентификация пользователя.
        """
        user = await self.get_user_by_login(Login)
        if not user:
            return "User not found"
        if not verify_password(PasswordHash, user.PasswordHash):
            return "Invalid password"
        return user