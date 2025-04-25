from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.platform_service.platform_service import PlatformService
from app.schemas.request.platform.platform_schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from typing import List, Optional

router = APIRouter(prefix="/platform", tags=["Platforms"])

@router.post("/", response_model=PlatformResponse)
async def create_platform(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    platform_data = PlatformCreate(
        Name=name,
        City=city,
        Address=address,
        Latitude=latitude,
        Longitude=longitude
    )
    return await service.create_platform(platform_data, image)

@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(platform_id: int, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platform = await service.get_platform_by_id(platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    return platform

@router.put("/{platform_id}", response_model=PlatformResponse)
async def update_platform(
    platform_id: int,
    name: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    platform_data = PlatformUpdate(
        Name=name,
        City=city,
        Address=address,
        Latitude=latitude,
        Longitude=longitude
    )
    return await service.update_platform(platform_id, platform_data, image)

@router.delete("/{platform_id}")
async def delete_platform(platform_id: int, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    return await service.delete_platform(platform_id)

@router.get("/", response_model=List[PlatformResponse])
async def get_all_platforms(session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platforms = await service.get_all_platforms()
    return platforms