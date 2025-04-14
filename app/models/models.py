from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, DateTime, Time, Boolean, Text, ForeignKey
from datetime import time, datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    UserID: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    Login: Mapped[str] = mapped_column(String(255), unique=True)
    Email: Mapped[str] = mapped_column(String(255), unique=True)
    PasswordHash: Mapped[str] = mapped_column(String(256))
    Name: Mapped[str] = mapped_column(String(255), nullable=True)
    Surname: Mapped[str] = mapped_column(String(255), nullable=True)
    Patronymic: Mapped[str] = mapped_column(String(255), nullable=True)
    City: Mapped[str] = mapped_column(String(255), nullable=True)
    Phone: Mapped[str] = mapped_column(String(20), nullable=True)
    PhotoURL: Mapped[str] = mapped_column(String(255), nullable=True)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="user")


class Event(Base):
    __tablename__ = "Events"

    EventID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(Integer, ForeignKey("Users.UserID"), nullable=False)
    PlatformID: Mapped[int] = mapped_column(Integer, ForeignKey("Platforms.PlatformID"), nullable=False)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    City: Mapped[str] = mapped_column(String(255), nullable=True)
    DateStart: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    DateEnd: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    TimeStart: Mapped[time] = mapped_column(Time, nullable=True)  # Используем тип time
    TimeEnd: Mapped[time] = mapped_column(Time, nullable=True)    # Используем тип time
    Description: Mapped[str] = mapped_column(String(500), nullable=True)
    Address: Mapped[str] = mapped_column(String(255), nullable=True)

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="events")
    platform: Mapped["Platform"] = relationship("Platform", back_populates="events")


class Platform(Base):
    __tablename__ = "Platforms"

    PlatformID: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    City: Mapped[str] = mapped_column(String(255), nullable=True)
    Address: Mapped[str] = mapped_column(String(255), nullable=True)
    Image: Mapped[str] = mapped_column(String(255), nullable=True)
    Latitude: Mapped[float] = mapped_column(Float, nullable=True)
    Longitude: Mapped[float] = mapped_column(Float, nullable=True)

    # Связи
    events: Mapped[list["Event"]] = relationship("Event", back_populates="platform")