from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Account(Base):
    __tablename__ = "accounts"

    email: Mapped[str] = mapped_column(String(120), primary_key=True)
    password: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20))
    nickname: Mapped[str] = mapped_column(String(80))


class SessionToken(Base):
    __tablename__ = "tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(120), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Guest(Base):
    __tablename__ = "guests"

    email: Mapped[str] = mapped_column(String(120), primary_key=True)
    nickname: Mapped[str] = mapped_column(String(80))
    preference_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    portrait_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    floor: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(40))
    occupied: Mapped[bool] = mapped_column(Boolean, default=False)
    guest_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    scene_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    env_json: Mapped[str] = mapped_column(Text)
    devices_json: Mapped[str] = mapped_column(Text)
    history_json: Mapped[str] = mapped_column(Text)


class HotelMeta(Base):
    __tablename__ = "hotel_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    simulating: Mapped[bool] = mapped_column(Boolean, default=True)
    trend_json: Mapped[str] = mapped_column(Text, default="[]")
