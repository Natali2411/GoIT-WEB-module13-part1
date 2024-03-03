from __future__ import annotations

from typing import Type

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import ContactChannel, Channel, Contact
from src.schemas import ContactChannelModel


async def get_contacts_channels(
    skip: int, limit: int, db: Session, user_id: int
) -> list[Type[ContactChannel]]:
    return (
        db.query(ContactChannel)
        .filter(ContactChannel.created_by == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


async def create_contacts_channels(
    body: ContactChannelModel, db: Session, user_id: int
) -> (ContactChannel | int):
    contact_channel = (
        db.query(ContactChannel)
        .filter(
            and_(
                ContactChannel.channel_value == body.channel_value,
                ContactChannel.created_by == user_id,
            )
        )
        .first()
    )
    if contact_channel:
        return 1
    channel = db.query(Channel).filter(Channel.id == body.channel_id).first()
    contact = db.query(Contact).filter(Contact.id == body.contact_id).first()
    if channel and contact:
        contact_channel = ContactChannel(
            contact_id=body.contact_id,
            channel_id=channel.id,
            channel_value=body.channel_value,
        )
        db.add(contact_channel)
        db.commit()
        db.refresh(contact_channel)
        return contact_channel
    else:
        return 2


async def update_contact_channel(
    contact_channel_id: int, body: ContactChannelModel, db: Session, user_id: int
) -> [ContactChannel]:
    contact_channel = (
        db.query(ContactChannel)
        .filter(
            and_(
                ContactChannel.id == contact_channel_id,
                ContactChannel.created_by == user_id,
            )
        )
        .first()
    )
    if contact_channel:
        contact_channel.contact_id = body.contact_id
        contact_channel.channel_id = body.channel_id
        contact_channel.channel_value = body.channel_value
        db.commit()
        db.refresh(contact_channel)
        return contact_channel


async def remove_contact_channel(
    contact_channel_id: int,
    db: Session,
    user_id: int,
) -> ContactChannel | None:
    contact_channel = (
        db.query(ContactChannel)
        .filter(
            and_(
                ContactChannel.id == contact_channel_id,
                ContactChannel.created_by == user_id,
            )
        )
        .first()
    )
    if contact_channel:
        db.delete(contact_channel)
        db.commit()
    return contact_channel
