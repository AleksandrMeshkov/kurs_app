from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.platform_service.platform_service import PlatformService
from app.schemas.request.platform.platform_schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from typing import List


router = APIRouter(prefix="/platform", tags=["Platforms"])  # Исправлено на "Platforms"

@router.post("/", response_model=PlatformResponse)
async def create_platform(platform: PlatformCreate, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    return await service.create_platform(platform)

@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(platform_id: int, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platform = await service.get_platform_by_id(platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    return platform

@router.put("/{platform_id}", response_model=PlatformResponse)
async def update_platform(platform_id: int, platform: PlatformUpdate, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    return await service.update_platform(platform_id, platform)

@router.delete("/{platform_id}")
async def delete_platform(platform_id: int, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    return await service.delete_platform(platform_id)

@router.get("/", response_model=List[PlatformResponse])
async def get_all_platforms(session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platforms = await service.get_all_platforms()
    return platforms