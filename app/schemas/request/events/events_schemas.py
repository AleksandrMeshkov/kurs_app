from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional

class EventBase(BaseModel):
    Name: str
    City: str
    DateStart: date  # Используем тип date вместо datetime
    DateEnd: date    # Используем тип date вместо datetime
    TimeStart: str   # Используем строку для времени
    TimeEnd: str     # Используем строку для времени
    Description: str
    Address: str

    @validator('TimeStart', 'TimeEnd')
    def validate_time_format(cls, v):
        try:
            hours, minutes, seconds = map(int, v.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError("Неверное время")
            return v
        except ValueError:
            raise ValueError("Время должно быть в формате HH:MM:SS")
        except AttributeError:
            raise ValueError("Время должно быть строкой в формате HH:MM:SS")

class EventCreate(EventBase):
    UserID: int
    PlatformID: int

class EventUpdate(BaseModel):
    UserID: Optional[int] = None
    PlatformID: Optional[int] = None
    Name: Optional[str] = None
    City: Optional[str] = None
    DateStart: Optional[date] = None
    DateEnd: Optional[date] = None
    TimeStart: Optional[str] = None
    TimeEnd: Optional[str] = None
    Description: Optional[str] = None
    Address: Optional[str] = None

    @validator('TimeStart', 'TimeEnd')
    def validate_time_format(cls, v):
        if v is None:
            return v
        try:
            hours, minutes, seconds = map(int, v.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError("Неверное время")
            return v
        except ValueError:
            raise ValueError("Время должно быть в формате HH:MM:SS")
        except AttributeError:
            raise ValueError("Время должно быть строкой в формате HH:MM:SS")

class EventResponse(EventBase):
    EventID: int
    UserID: int
    PlatformID: int