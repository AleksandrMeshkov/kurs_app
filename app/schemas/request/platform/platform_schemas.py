from pydantic import BaseModel
from fastapi import UploadFile
from typing import Optional

class PlatformCreate(BaseModel):
    Name: str
    City: str
    Address: str
    Image: UploadFile
    Latitude: float
    Longitude: float

class PlatformUpdate(BaseModel):
    Name: str = None
    City: str = None
    Address: str = None
    Image: Optional[UploadFile] = None
    Latitude: float = None
    Longitude: float = None

class PlatformResponse(BaseModel):
    PlatformID: int
    Name: str
    City: str
    Address: str
    Image: str
    Latitude: float
    Longitude: float