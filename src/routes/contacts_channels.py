from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user
from src.schemas import (
    ContactChannelModel,
    ContactChannelResponse,
)
from src.repository import contacts_channels as repository_contacts_channels


router = APIRouter(prefix="/contactsChannels", tags=["contactsChannels"])


@router.get(
    "/",
    response_model=List[ContactChannelResponse],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_contacts_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts_channels = await repository_contacts_channels.get_contacts_channels(
        skip, limit, db, current_user.id
    )
    return contacts_channels


@router.post(
    "/",
    response_model=ContactChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def create_contacts_channels(
    body: ContactChannelModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts_channels = await repository_contacts_channels.create_contacts_channels(
        body, db, current_user.id
    )
    if contacts_channels == 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such channel value already " "exists in the DB",
        )
    elif contacts_channels == 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact or channel name " "is not found",
        )
    return contacts_channels


@router.put(
    "/{contactChannelId}",
    response_model=ContactChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def update_contact_channel(
    contactChannelId: int,
    body: ContactChannelModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_channel = await repository_contacts_channels.update_contact_channel(
        contactChannelId, body, db, current_user.id
    )
    if not contact_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact channel {contactChannelId} " "is not found",
        )
    return contact_channel


@router.delete(
    "/{contactChannelId}",
    response_model=ContactChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def delete_contact_channel(
    contactChannelId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_channel = await repository_contacts_channels.remove_contact_channel(
        contactChannelId, db, current_user.id
    )
    if not contact_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact channel {contactChannelId} " "is not found",
        )
    return contact_channel
