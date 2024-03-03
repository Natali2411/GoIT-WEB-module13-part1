from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

from src.schemas import ChannelType

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False, insert_default="Test")
    last_name: Mapped[str] = mapped_column(String(50), nullable=False, insert_default="Test")
    email = mapped_column(String(250), nullable=False, unique=True)
    password = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime, default=func.now())
    avatar = mapped_column(String(255), nullable=True)
    refresh_token = mapped_column(String(1255), nullable=True)
    confirmed = mapped_column(Boolean, default=False)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    birthdate: Mapped[str] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    persuasion: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    channels = relationship("ContactChannel", backref="contacts", passive_deletes=True)


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[ChannelType] = mapped_column(String(50), nullable=False, unique=True)


class ContactChannel(Base):
    __tablename__ = "contacts_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id"))
    channel_value: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id",
                                                                ondelete="CASCADE"))
