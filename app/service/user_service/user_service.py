from typing import Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, UploadFile, status
from pathlib import Path
import uuid
from app.models.models import User
from app.security.hasher import hash_password, verify_password

class UserService:
    BASE_URL = "http://212.20.53.169:13299"  # Базовый URL сервера
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        """Получить пользователя по ID."""
        query = select(User).where(User.UserID == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_profile(self, user_id: int, data: Dict[str, Any], photo_file: UploadFile = None) -> User:
        """
        Обновление профиля пользователя с загрузкой фото.
        Сохраняет полный URL фото в формате: http://212.20.53.169:13299/uploads/filename.ext
        """
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обработка загружаемого файла
        if photo_file:
            try:
                file_name = await self.save_uploaded_file(photo_file)
                # Сохраняем полный URL в базу данных
                data['PhotoURL'] = f"{self.BASE_URL}/uploads/{file_name}"
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при обработке файла: {str(e)}"
                )

        # Обработка пароля
        if 'Password' in data and data['Password'] is not None:
            data['PasswordHash'] = hash_password(data['Password'])
            del data['Password']

        # Фильтрация None значений
        update_fields = {k: v for k, v in data.items() if v is not None}
        if not update_fields:
            return existing_user

        # Обновление в базе данных
        query = update(User).where(User.UserID == user_id).values(**update_fields).returning(User)
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении профиля: {str(e)}"
            )

    @staticmethod
    async def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
        """Сохраняет загруженный файл и возвращает только имя файла."""
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
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