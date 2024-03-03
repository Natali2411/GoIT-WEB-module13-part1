from __future__ import annotations

from typing import List, Type

from sqlalchemy import and_, extract, cast, Integer
from sqlalchemy.orm import Session

from src.database.models import Contact, ContactChannel
from src.schemas import ContactModel
from src.utils.dates import get_future_dates


async def get_contacts(
    db: Session,
    user_id: int,
    firstName: str = None,
    lastName: str = None,
    email: str = None,
) -> List[Type[Contact]]:
    conditions = [Contact.created_by == user_id]
    if firstName:
        conditions.append(Contact.first_name == firstName)
    if lastName:
        conditions.append(Contact.last_name == lastName)
    if email:
        conditions.append(ContactChannel.channel_value == email)
    contacts = (
        db.query(Contact).outerjoin(ContactChannel).filter(and_(*conditions)).all()
    )
    return contacts


async def get_contacts_birthdays(
    db: Session, days: int, user_id: int
) -> List[Type[Contact]]:
    dates = get_future_dates(days)
    contacts = (
        db.query(Contact)
        .filter(
            (Contact.birthdate.isnot(None))
            & cast((extract("month", Contact.birthdate)), Integer).in_(dates["month"])
            & cast(extract("day", Contact.birthdate), Integer).in_(dates["day"])
            & (Contact.created_by == user_id)
        )
        .all()
    )
    return contacts


async def get_contact(
    contact_id: int, db: Session, user_id: int
) -> Type[Contact] | None:
    return (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.created_by == user_id))
        .first()
    )


async def create_contact(body: ContactModel, db: Session, user_id: int) -> Contact:
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        birthdate=body.birthdate,
        gender=body.gender,
        persuasion=body.persuasion,
        created_by=user_id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactModel, db: Session, user_id: int
) -> Contact | None:
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.created_by == user_id))
        .first()
    )
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.persuasion = body.persuasion
        contact.gender = body.gender
        contact.channels = body.channels
        contact.birthdate = body.birthdate
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session, user_id: int) -> Contact | None:
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.created_by == user_id))
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact
