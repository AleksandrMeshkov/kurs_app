from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.events_service.events_service import EventService
from app.schemas.request.events.events_schemas import EventCreate, EventUpdate, EventResponse
from typing import List

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate, session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    return await service.create_event(event)

@router.get("/", response_model=List[EventResponse])  
async def get_all_events(session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    events = await service.get_all_events()
    return events

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    event = await service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event: EventUpdate, session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    return await service.update_event(event_id, event)

@router.delete("/{event_id}")
async def delete_event(event_id: int, session: AsyncSession = Depends(get_session)):
    service = EventService(session)
    return await service.delete_event(event_id)