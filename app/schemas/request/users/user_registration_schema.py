from pydantic import BaseModel
from typing import Optional

class UserRegistration(BaseModel):
    Login: str
    PasswordHash: str  # Переименовали поле
    Email: str
    Name: Optional[str] = None
    Surname: Optional[str] = None
    Patronymic: Optional[str] = None
    City: Optional[str] = None
    Phone: Optional[str] = None
    PhotoURL: Optional[str] = None
