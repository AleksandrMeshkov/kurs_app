from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.platform_service.platform_service import PlatformService
from app.schemas.request.platform.platform_schemas import PlatformResponse, PlatformCreateRequest
from typing import List, Optional

router = APIRouter(prefix="/platforms", tags=["Platforms"])

@router.post("/", response_model=PlatformResponse)
async def create_platform(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    platform_data = PlatformCreateRequest(
        Name=name,
        City=city,
        Address=address,
        Latitude=latitude,
        Longitude=longitude
    )
    platform = await service.create_platform(platform_data, image)
    return PlatformResponse(
        PlatformID=platform.PlatformID,
        Name=platform.Name,
        City=platform.City,
        Address=platform.Address,
        Latitude=platform.Latitude,
        Longitude=platform.Longitude,
        ImageUrl=f"http://212.20.53.169:13299/uploads/{platform.Image}" if platform.Image else None
    )

@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(
    platform_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    platform = await service.get_platform(platform_id)
    return PlatformResponse(
        PlatformID=platform.PlatformID,
        Name=platform.Name,
        City=platform.City,
        Address=platform.Address,
        Latitude=platform.Latitude,
        Longitude=platform.Longitude,
        ImageUrl=f"http://212.20.53.169:13299/uploads/{platform.Image}" if platform.Image else None
    )

@router.get("/", response_model=List[PlatformResponse])
async def get_all_platforms(session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platforms = await service.get_all_platforms()
    return [
        PlatformResponse(
            PlatformID=p.PlatformID,
            Name=p.Name,
            City=p.City,
            Address=p.Address,
            Latitude=p.Latitude,
            Longitude=p.Longitude,
            ImageUrl=f"http://212.20.53.169:13299/uploads/{p.Image}" if p.Image else None
        )
        for p in platforms
    ]

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
    platform_data = {
        "Name": name,
        "City": city,
        "Address": address,
        "Latitude": latitude,
        "Longitude": longitude
    }
    platform = await service.update_platform(platform_id, platform_data, image)
    return PlatformResponse(
        PlatformID=platform.PlatformID,
        Name=platform.Name,
        City=platform.City,
        Address=platform.Address,
        Latitude=platform.Latitude,
        Longitude=platform.Longitude,
        ImageUrl=f"http://212.20.53.169:13299/uploads/{platform.Image}" if platform.Image else None
    )

@router.delete("/{platform_id}")
async def delete_platform(
    platform_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    await service.delete_platform(platform_id)
    return {"message": "Площадка успешно удалена"}