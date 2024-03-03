from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user
from src.schemas import (
    ChannelResponse,
    ContactResponse,
    ContactChannelResponse,
    ContactModel,
)
from src.repository import contacts as repository_contacts

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_contacts(
    firstName: str = None,
    lastName: str = None,
    email: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts = await repository_contacts.get_contacts(
        db, current_user.id, firstName, lastName, email
    )
    return contacts


@router.get(
    "/birthdays",
    response_model=List[ContactResponse],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_contacts_birthdays(
    daysForward: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts = await repository_contacts.get_contacts_birthdays(
        db, daysForward, current_user.id
    )
    return contacts


@router.get(
    "/{contactId}",
    response_model=ContactResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_contact(
    contactId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = await repository_contacts.get_contact(contactId, db, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await repository_contacts.create_contact(body, db, current_user.id)
