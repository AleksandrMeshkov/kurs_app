from typing import Dict, Union, Optional
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.models import Event
from app.schemas.request.events.events_schemas import EventCreate, EventUpdate, EventResponse

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_event_by_id(self, event_id: int) -> Union[Event, None]:
        """
        Получить событие по ID.
        """
        query = select(Event).where(Event.EventID == event_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_event(self, request: EventCreate) -> Event:
        """
        Создание нового события.
        """
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
                    TimeStart=request.TimeStart,
                    TimeEnd=request.TimeEnd,
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
        """
        Обновление информации о событии.
        """
        existing_event = await self.get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        data_dict = data.dict(exclude_unset=True)
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
        """
        Удаление события.
        """
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