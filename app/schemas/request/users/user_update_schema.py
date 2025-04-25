from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    Login: Optional[str] = None
    Email: Optional[str] = None
    Name: Optional[str] = None
    Surname: Optional[str] = None
    Patronymic: Optional[str] = None
    City: Optional[str] = None
    Phone: Optional[str] = None

class UserResponse(BaseModel):
    UserID: int
    Login: str
    Email: str
    Name: str
    Surname: str
    Patronymic: Optional[str] = None
    City: Optional[str] = None
    Phone: Optional[str] = None
    PhotoURL: Optional[str] = None

    class Config:
        from_attributes = True