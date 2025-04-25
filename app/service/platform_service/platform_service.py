from typing import Union, List
from app.models.models import Platform
from app.schemas.request.platform.platform_schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from sqlalchemy import select, insert, update, delete
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
from fastapi import status

class PlatformService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def get_platform_by_id(self, platform_id: int) -> Union[Platform, None]:
        """Получить площадку по ID."""
        query = select(Platform).where(Platform.PlatformID == platform_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_platforms(self) -> List[Platform]:
        """Получить все площадки."""
        query = select(Platform)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def save_image(self, file: UploadFile) -> str:
        """Сохраняет изображение на сервере и возвращает имя файла."""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением!"
            )

        # Генерируем уникальное имя файла
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return filename

    async def create_platform(self, platform_data: PlatformCreate, image: UploadFile = None):
        """Создание новой площадки с загрузкой изображения."""
        image_filename = None

        if image:
            image_filename = await self.save_image(image)

        query = (
            insert(Platform)
            .values(
                Name=platform_data.Name,
                City=platform_data.City,
                Address=platform_data.Address,
                Image=image_filename,  # Сохраняем только имя файла
                Latitude=platform_data.Latitude,
                Longitude=platform_data.Longitude
            )
            .returning(Platform)
        )
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании площадки: {str(e)}"
            )

    async def update_platform(self, platform_id: int, platform_data: PlatformUpdate, image: UploadFile = None):
        """Обновление информации о площадке с возможной заменой изображения."""
        existing_platform = await self.get_platform_by_id(platform_id)
        if not existing_platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Площадка не найдена"
            )

        # Удаляем старое изображение, если загружается новое
        image_filename = existing_platform.Image
        if image:
            # Удаляем старый файл
            if image_filename:
                old_file_path = os.path.join(self.upload_dir, image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Сохраняем новое изображение
            image_filename = await self.save_image(image)

        # Подготавливаем данные для обновления
        update_data = platform_data.dict(exclude_unset=True)
        if image_filename is not None:
            update_data["Image"] = image_filename

        if not update_data:
            return existing_platform

        query = (
            update(Platform)
            .where(Platform.PlatformID == platform_id)
            .values(**update_data)
            .returning(Platform)
        )
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении площадки: {str(e)}"
            )

    async def delete_platform(self, platform_id: int):
        """Удаление площадки с удалением связанного изображения."""
        existing_platform = await self.get_platform_by_id(platform_id)
        if not existing_platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Площадка не найдена"
            )

        # Удаляем изображение, если оно есть
        if existing_platform.Image:
            file_path = os.path.join(self.upload_dir, existing_platform.Image)
            if os.path.exists(file_path):
                os.remove(file_path)

        query = delete(Platform).where(Platform.PlatformID == platform_id)
        
        try:
            await self.session.execute(query)
            await self.session.commit()
            return {"message": "Площадка успешно удалена"}
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении площадки: {str(e)}"
            )