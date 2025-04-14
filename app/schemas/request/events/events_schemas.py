from pydantic import BaseModel
from datetime import datetime
from datetime import datetime, time

class EventCreate(BaseModel):
    UserID: int
    PlatformID: int
    Name: str
    City: str
    DateStart: datetime
    DateEnd: datetime
    TimeStart: time
    TimeEnd: time
    Description: str
    Address: str

class EventUpdate(BaseModel):
    UserID: int = None
    PlatformID: int = None
    Name: str = None
    City: str = None
    DateStart: datetime = None
    DateEnd: datetime = None
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
    DateStart: datetime
    DateEnd: datetime
    TimeStart: time  # Используем тип time
    TimeEnd: time    # Используем тип time
    Description: str
    Address: str