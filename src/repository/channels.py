from __future__ import annotations

from typing import List, Type

from sqlalchemy.orm import Session

from src.database.models import Channel, ContactChannel
from src.schemas import (
    ContactChannelResponse,
    ContactResponse,
    ContactModel,
    ChannelModel,
)


async def get_channels(db: Session) -> list[Type[Channel]]:
    return db.query(Channel).all()


async def get_channel(channel_id: int, db: Session) -> Type[Channel] | None:
    return db.query(Channel).filter(Channel.id == channel_id).first()


async def get_channel_by_name(channel_name: str, db: Session) -> Type[Channel] | None:
    return db.query(Channel).filter(Channel.name == channel_name).first()


async def create_channel(body: ChannelModel, db: Session) -> Channel:
    channel = Channel(name=body.name)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


async def update_channel(
    channel_id: int, body: ChannelModel, db: Session
) -> (Channel | None):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.name = body.name
        db.commit()
    return channel


async def remove_channel(channel_id: int, db: Session) -> Channel | None:
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        db.delete(channel)
        db.commit()
    return channel
