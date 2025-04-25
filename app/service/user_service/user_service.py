import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from app.models.models import User
from typing import Union, Optional
from pathlib import Path
from app.security.hasher import hash_password, verify_password

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads/users"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def _save_image(self, file: UploadFile) -> str:
        """Сохраняет изображение на сервере и возвращает имя файла"""
        try:
            if not file.content_type.startswith("image/"):
                raise ValueError("Поддерживаются только изображения")

            file_ext = Path(file.filename).suffix
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_dir, filename)

            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            return filename
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении изображения: {str(e)}"
            )

    async def _delete_image(self, filename: str):
        """Удаляет файл изображения"""
        try:
            if filename:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении изображения: {str(e)}"
            )

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        """Получает пользователя по ID"""
        try:
            result = await self.session.execute(select(User).where(User.UserID == user_id))
            return result.scalars().first()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении пользователя: {str(e)}"
            )

    async def get_user_by_login(self, login: str) -> Union[User, None]:
        """Получает пользователя по логину"""
        try:
            result = await self.session.execute(select(User).where(User.Login == login))
            return result.scalars().first()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении пользователя: {str(e)}"
            )

    async def register_user(self, user_data: dict, image: Optional[UploadFile] = None) -> User:
        """Регистрация нового пользователя"""
        try:
            existing_user = await self.get_user_by_login(user_data["Login"])
            if existing_user:
                raise ValueError("Пользователь с таким логином уже существует")

            photo_url = None
            if image:
                filename = await self._save_image(image)
                photo_url = f"/uploads/users/{filename}"

            hashed_password = hash_password(user_data["PasswordHash"])

            user = User(
                Login=user_data["Login"],
                PasswordHash=hashed_password,
                Email=user_data["Email"],
                Name=user_data["Name"],
                Surname=user_data["Surname"],
                Patronymic=user_data.get("Patronymic"),
                City=user_data.get("City"),
                Phone=user_data.get("Phone"),
                PhotoURL=photo_url
            )

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        except ValueError as ve:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при регистрации пользователя: {str(e)}"
            )

    async def update_profile(
        self,
        user_id: int,
        update_data: dict,
        image: Optional[UploadFile] = None
    ) -> User:
        """Обновляет профиль пользователя с фото"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ValueError("Пользователь не найден")

            if image:
                filename = await self._save_image(image)
                update_data["PhotoURL"] = f"/uploads/users/{filename}"
                
                if user.PhotoURL:
                    old_file = user.PhotoURL.split('/')[-1]
                    await self._delete_image(old_file)

            if "PasswordHash" in update_data:
                update_data["PasswordHash"] = hash_password(update_data["PasswordHash"])

            for key, value in update_data.items():
                if value is not None:
                    setattr(user, key, value)

            await self.session.commit()
            await self.session.refresh(user)
            return user

        except ValueError as ve:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if "не найден" in str(ve) 
                else status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении профиля: {str(e)}"
            )

    async def authenticate_user(self, login: str, password: str) -> Union[User, None]:
        """Аутентификация пользователя"""
        try:
            user = await self.get_user_by_login(login)
            if not user:
                return None
            
            if not verify_password(password, user.PasswordHash):
                return None
                
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при аутентификации: {str(e)}"
            )