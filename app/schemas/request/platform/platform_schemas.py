from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class PlatformBase(BaseModel):
    Name: str
    City: str
    Address: str
    Latitude: float
    Longitude: float

class PlatformCreate(PlatformBase):
    """Используется для валидации данных без файла"""
    pass

class PlatformCreateRequest(PlatformBase):
    """Используется для приёма данных с фронтенда"""
    pass  # Файл передаётся отдельно через FormData

class PlatformUpdate(BaseModel):
    Name: Optional[str] = None
    City: Optional[str] = None
    Address: Optional[str] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None

class PlatformResponse(PlatformBase):
    PlatformID: int
    ImageUrl: Optional[str] = None  # Полный URL к изображению

    class Config:
        from_attributes = True