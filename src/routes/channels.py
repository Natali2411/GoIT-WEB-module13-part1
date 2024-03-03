from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user
from src.schemas import ChannelResponse, ChannelModel
from src.repository import channels as repository_channels

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get(
    "/",
    response_model=List[ChannelResponse],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_channels(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    channels = await repository_channels.get_channels(db)
    return channels


@router.get(
    "/{channelId}",
    response_model=ChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def read_channel(
    channelId: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    channel = await repository_channels.get_channel(channelId, db)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    return channel


@router.post(
    "/",
    response_model=ChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def create_channel(
    body: ChannelModel,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    channel = await repository_channels.get_channel_by_name(body.name, db)
    if channel:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Channel with the name '" f"{body.name}' already exists",
        )
    return await repository_channels.create_channel(body, db)


@router.put(
    "/{channelId}",
    response_model=ChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def update_channel(
    channelId: int,
    body: ChannelModel,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    channel = await repository_channels.update_channel(channelId, body, db)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    return channel


@router.delete(
    "/{channelId}",
    response_model=ChannelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def delete_channel(
    channelId: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    channel = await repository_channels.remove_channel(channelId, db)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    return channel
