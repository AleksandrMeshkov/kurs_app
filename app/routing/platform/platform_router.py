from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.platform_service.platform_service import PlatformService
from app.schemas.request.platform.platform_schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from typing import List
import os
import uuid

router = APIRouter(prefix="/platform", tags=["Platforms"])

@router.post("/", response_model=PlatformResponse)
async def create_platform(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    session: AsyncSession = Depends(get_session)
):
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    try:
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    
    # Create platform with file path
    platform_data = PlatformCreate(
        Name=name,
        City=city,
        Address=address,
        Image=unique_filename,  # Store the filename in the database
        Latitude=latitude,
        Longitude=longitude
    )
    
    service = PlatformService(session)
    return await service.create_platform(platform_data)

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
    name: str = Form(None),
    city: str = Form(None),
    address: str = Form(None),
    image: UploadFile = File(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    session: AsyncSession = Depends(get_session)
):
    service = PlatformService(session)
    
    # Handle image upload if provided
    image_filename = None
    if image:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_extension = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, image_filename)
        
        try:
            contents = await image.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    
    # Create update data
    update_data = PlatformUpdate(
        Name=name,
        City=city,
        Address=address,
        Image=image_filename,
        Latitude=latitude,
        Longitude=longitude
    )
    
    return await service.update_platform(platform_id, update_data)

@router.delete("/{platform_id}")
async def delete_platform(platform_id: int, session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    return await service.delete_platform(platform_id)

@router.get("/", response_model=List[PlatformResponse])
async def get_all_platforms(session: AsyncSession = Depends(get_session)):
    service = PlatformService(session)
    platforms = await service.get_all_platforms()
    return platforms