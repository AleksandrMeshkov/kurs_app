import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Platform
from typing import Optional
from app.schemas.request.platform.platform_schemas import PlatformCreateRequest

class PlatformService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def _save_image(self, file: UploadFile) -> str:
        """Сохраняет изображение на сервере и возвращает имя файла"""
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только изображения"
            )

        try:
            # Генерируем уникальное имя файла
            file_ext = os.path.splitext(file.filename)[-1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_dir, filename)

            # Сохраняем файл
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            return filename
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении изображения: {str(e)}"
            )

    async def _delete_image(self, filename: str):
        """Удаляет файл изображения"""
        if filename:
            try:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при удалении изображения: {str(e)}"
                )

    async def create_platform(
        self,
        platform_data: PlatformCreateRequest,
        image: UploadFile
    ) -> Platform:
        """Создает новую площадку с изображением"""
        try:
            image_filename = await self._save_image(image)

            platform = Platform(
                Name=platform_data.Name,
                City=platform_data.City,
                Address=platform_data.Address,
                Latitude=platform_data.Latitude,
                Longitude=platform_data.Longitude,
                Image=image_filename
            )

            self.session.add(platform)
            await self.session.commit()
            await self.session.refresh(platform)
            return platform
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании площадки: {str(e)}"
            )

    async def get_platform(self, platform_id: int) -> Platform:
        """Получает площадку по ID"""
        try:
            platform = await self.session.get(Platform, platform_id)
            if not platform:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Площадка не найдена"
                )
            return platform
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении площадки: {str(e)}"
            )

    async def get_all_platforms(self) -> list[Platform]:
        """Получает все площадки"""
        try:
            result = await self.session.execute(select(Platform))
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении списка площадок: {str(e)}"
            )

    async def update_platform(
        self,
        platform_id: int,
        platform_data: dict,
        image: Optional[UploadFile] = None
    ) -> Platform:
        """Обновляет информацию о площадке"""
        try:
            platform = await self.get_platform(platform_id)

            # Обновляем изображение если нужно
            if image:
                await self._delete_image(platform.Image)
                platform.Image = await self._save_image(image)

            # Обновляем остальные поля
            if platform_data.get("Name") is not None:
                platform.Name = platform_data["Name"]
            if platform_data.get("City") is not None:
                platform.City = platform_data["City"]
            if platform_data.get("Address") is not None:
                platform.Address = platform_data["Address"]
            if platform_data.get("Latitude") is not None:
                platform.Latitude = platform_data["Latitude"]
            if platform_data.get("Longitude") is not None:
                platform.Longitude = platform_data["Longitude"]

            await self.session.commit()
            await self.session.refresh(platform)
            return platform
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении площадки: {str(e)}"
            )

    async def delete_platform(self, platform_id: int):
        """Удаляет площадку"""
        try:
            platform = await self.get_platform(platform_id)
            await self._delete_image(platform.Image)
            await self.session.delete(platform)
            await self.session.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении площадки: {str(e)}"
            )