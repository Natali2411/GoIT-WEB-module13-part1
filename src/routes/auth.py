import pickle
from datetime import datetime, timedelta
from typing import Optional

# from redis.asyncio import Redis
import redis
from fastapi import Header, UploadFile, File
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import (
    HTTPBearer,
)
from fastapi_jwt_auth import AuthJWT
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import and_
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user, get_user_by_email
from src.schemas import UserModel, UserResponse, TokenModel, UserDb
from src.repository import users as repository_users
from src.services.auth import get_password_hash, get_email_from_token
from src.conf.config import settings
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request,
                 Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with the email {body.email} already exists",
        )
    body.password = get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, f"{new_user.first_name} {new_user.last_name}",
        request.base_url)
    return {"user": new_user,
            "detail": "User successfully created. Check your email for confirmation."}


@router.delete(
    "/users/{email}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def remove_user(email: str, db: Session = Depends(get_db),
                      _: User = Depends(get_current_user),):
    exist_user = await repository_users.get_user_by_email(email, db)
    if exist_user:
        db.query(User).delete()
        db.commit()


@router.post(
    "/access_token",
    response_model=Optional[TokenModel],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per "
    f"minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def create_session(
    user: UserModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)
):
    user = await get_user_by_email(user.email, db)
    if user:
        if not user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
            )
        access_token = Authorize.create_access_token(subject=user.email)
        refresh_token = Authorize.create_refresh_token(subject=user.email)

        user.refresh_token = refresh_token
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get(
    "/refresh_token",
    response_model=TokenModel,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def refresh_token(
    refresh_token: str = Header(..., alias="Authorization"),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    Authorize.jwt_refresh_token_required()
    # Check if refresh token is in DB
    user_email = Authorize.get_jwt_subject()
    user = db.query(User).filter(and_(user_email == User.email)).first()
    if f"Bearer {user.refresh_token}" == refresh_token:
        access_token = Authorize.create_access_token(subject=user_email)
        new_refresh_token = Authorize.create_refresh_token(subject=user_email)

        user.refresh_token = new_refresh_token
        db.commit()
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirm_email(email, db)
    return {"message": "Email confirmed"}

@router.patch(
    "/avatar",
    response_model=UserDb,
    description=f"No more than"
    f" {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.email}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"ContactsApp/{current_user.email}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
