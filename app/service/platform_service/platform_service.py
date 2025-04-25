from typing import Union
from app.models.models import Platform
from app.schemas.request.platform.platform_schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from sqlalchemy import select, insert, update, delete
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import uuid

class PlatformService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_platform_by_id(self, platform_id: int) -> Union[Platform, None]:
        """
        Получить площадку по ID.
        """
        query = select(Platform).where(Platform.PlatformID == platform_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_platforms(self) -> List[Platform]:
        """
        Получить все площадки.
        """
        query = select(Platform)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_platform(self, request: PlatformCreate):
        """
        Создание новой площадки.
        """
        query = (
            insert(Platform)
            .values(
                Name=request.Name,
                City=request.City,
                Address=request.Address,
                Image=request.Image,
                Latitude=request.Latitude,
                Longitude=request.Longitude
            )
            .returning(Platform)
        )

        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при создании площадки: {str(e)}")


    async def update_platform(self, platform_id: int, data: PlatformUpdate):
        """
        Обновление информации о площадке.
        """
        existing_platform = await self.get_platform_by_id(platform_id)
        if not existing_platform:
            raise HTTPException(status_code=404, detail="Площадка не найдена")

        data_dict = data.dict(exclude_unset=True)

        # Handle image update
        if 'Image' in data_dict and data_dict['Image']:
            # Delete old image if it exists
            if existing_platform.Image:
                old_file_path = os.path.join("uploads", existing_platform.Image)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

        update_fields = {}
        for key, value in data_dict.items():
            if value is not None:
                update_fields[key] = value

        if not update_fields:
            return None

        query = update(Platform).where(Platform.PlatformID == platform_id).values(update_fields).returning(Platform)
        
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении площадки: {str(e)}")

    async def delete_platform(self, platform_id: int):
        """
        Удаление площадки.
        """
        existing_platform = await self.get_platform_by_id(platform_id)
        if not existing_platform:
            raise HTTPException(status_code=404, detail="Площадка не найдена")

        # Delete associated image file
        if existing_platform.Image:
            file_path = os.path.join("uploads", existing_platform.Image)
            if os.path.exists(file_path):
                os.remove(file_path)

        query = delete(Platform).where(Platform.PlatformID == platform_id)
        
        try:
            await self.session.execute(query)
            await self.session.commit()
            return {"message": "Площадка успешно удалена"}
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении площадки: {str(e)}")