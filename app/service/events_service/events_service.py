from typing import Dict, Union, Optional, List
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.models import Event
from app.schemas.request.events.events_schemas import EventCreate, EventUpdate, EventResponse
from datetime import time

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_event_by_id(self, event_id: int) -> Union[Event, None]:
        query = select(Event).where(Event.EventID == event_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_events(self) -> List[Event]:
        result = await self.session.execute(select(Event))
        return result.scalars().all()

    async def create_event(self, request: EventCreate) -> Event:
        # Конвертируем строки времени в объекты time
        time_start = self._parse_time_str(request.TimeStart)
        time_end = self._parse_time_str(request.TimeEnd)

        try:
            query = (
                insert(Event)
                .values(
                    UserID=request.UserID,
                    PlatformID=request.PlatformID,
                    Name=request.Name,
                    City=request.City,
                    DateStart=request.DateStart,
                    DateEnd=request.DateEnd,
                    TimeStart=time_start,
                    TimeEnd=time_end,
                    Description=request.Description,
                    Address=request.Address
                )
                .returning(Event)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании события: {str(e)}"
            )

    async def update_event(self, event_id: int, data: EventUpdate) -> Optional[Event]:
        existing_event = await self.get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        data_dict = data.dict(exclude_unset=True)
        
        # Конвертируем строки времени в объекты time, если они есть
        if 'TimeStart' in data_dict and data_dict['TimeStart'] is not None:
            data_dict['TimeStart'] = self._parse_time_str(data_dict['TimeStart'])
        if 'TimeEnd' in data_dict and data_dict['TimeEnd'] is not None:
            data_dict['TimeEnd'] = self._parse_time_str(data_dict['TimeEnd'])

        if not data_dict:
            return None

        query = (
            update(Event)
            .where(Event.EventID == event_id)
            .values(**data_dict)
            .returning(Event)
        )

        try:
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении события: {str(e)}"
            )

    async def delete_event(self, event_id: int) -> Dict[str, str]:
        existing_event = await self.get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        query = delete(Event).where(Event.EventID == event_id)

        try:
            await self.session.execute(query)
            await self.session.commit()
            return {"message": "Событие успешно удалено"}
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении события: {str(e)}"
            )

    @staticmethod
    def _parse_time_str(time_str: str) -> time:
        """Конвертирует строку времени в объект time."""
        hours, minutes, seconds = map(int, time_str.split(':'))
        return time(hour=hours, minute=minutes, second=seconds)