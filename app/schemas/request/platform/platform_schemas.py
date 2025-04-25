from pydantic import BaseModel
from fastapi import UploadFile
from typing import Optional, Union

# Существующие классы (без изменений)
class PlatformCreate(BaseModel):
    Name: str
    City: str
    Address: str
    Image: str  # Ожидается строка (путь/URL)
    Latitude: float
    Longitude: float

class PlatformUpdate(BaseModel):
    Name: str = None
    City: str = None
    Address: str = None
    Image: str = None  # Ожидается строка (путь/URL)
    Latitude: float = None
    Longitude: float = None

class PlatformResponse(BaseModel):
    PlatformID: int
    Name: str
    City: str
    Address: str
    Image: str  # Возвращается строка (путь/URL)
    Latitude: float
    Longitude: float

# Новые классы для работы с загрузкой файлов
class PlatformCreateWithFile(BaseModel):
    Name: str
    City: str
    Address: str
    Image: UploadFile  # Принимает файл напрямую
    Latitude: float
    Longitude: float

class PlatformUpdateWithFile(BaseModel):
    Name: Optional[str] = None
    City: Optional[str] = None
    Address: Optional[str] = None
    Image: Optional[UploadFile] = None  # Принимает файл или None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None