import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models.models import Platform
from typing import Union, List, Optional
from app.schemas.request.platform.platform_schemas import (  
    PlatformCreate,
    PlatformUpdate,
    PlatformResponse
)

class PlatformService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def _save_image(self, file: UploadFile) -> str:
        """Приватный метод для сохранения изображения"""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только изображения"
            )

        # Генерируем уникальное имя
        file_ext = os.path.splitext(file.filename)[-1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return filename

    async def _delete_image(self, filename: str):
        """Удаление файла изображения"""
        if filename:
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

    async def create_platform(
        self, 
        platform_data: PlatformCreate,
        image: Optional[UploadFile] = None
    ) -> Platform:
        image_filename = await self._save_image(image) if image else None

        platform = Platform(
            **platform_data.model_dump(),
            Image=image_filename  # Сохраняем только имя файла
        )

        self.session.add(platform)
        await self.session.commit()
        await self.session.refresh(platform)
        return platform

    async def update_platform(
        self,
        platform_id: int,
        platform_data: PlatformUpdate,
        image: Optional[UploadFile] = None
    ) -> Platform:
        platform = await self.session.get(Platform, platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Площадка не найдена"
            )

        # Обновляем изображение если нужно
        if image:
            await self._delete_image(platform.Image)
            platform.Image = await self._save_image(image)

        # Обновляем остальные поля
        update_data = platform_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(platform, field, value)

        await self.session.commit()
        await self.session.refresh(platform)
        return platform

    async def delete_platform(self, platform_id: int) -> None:
        platform = await self.session.get(Platform, platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Площадка не найдена"
            )

        await self._delete_image(platform.Image)
        await self.session.delete(platform)
        await self.session.commit()

    async def get_platform(self, platform_id: int) -> Platform:
        platform = await self.session.get(Platform, platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Площадка не найдена"
            )
        return platform

    async def get_all_platforms(self) -> list[Platform]:
        result = await self.session.execute(select(Platform))
        return result.scalars().all()