from pydantic import BaseModel
from datetime import datetime
from datetime import datetime, time, date

class EventCreate(BaseModel):
    UserID: int
    PlatformID: int
    Name: str
    City: str
    DateStart: date
    DateEnd: date
    TimeStart: time
    TimeEnd: time
    Description: str
    Address: str

class EventUpdate(BaseModel):
    UserID: int = None
    PlatformID: int = None
    Name: str = None
    City: str = None
    DateStart: date = None
    DateEnd: date = None
    TimeStart: time = None
    TimeEnd: time = None
    Description: str = None
    Address: str = None

class EventResponse(BaseModel):
    EventID: int
    UserID: int
    PlatformID: int
    Name: str
    City: str
    DateStart: date
    DateEnd: date
    TimeStart: time  # Используем тип time
    TimeEnd: time    # Используем тип time
    Description: str
    Address: str