from __future__ import annotations

import pickle
from typing import Type

import redis
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from starlette import status

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel


r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


async def get_user_by_email(email: str, db: Session) -> Type[User] | bool:
    # r.delete(f"user:{email}")
    current_user = r.get(f"user:{email}")
    if current_user is None:
        current_user = db.query(User).filter(User.email == email).first()
        if current_user is None:
            return False
        r.set(f"user:{email}", pickle.dumps(current_user))
        r.expire(f"user:{email}", 900)
    else:
        current_user = pickle.loads(current_user)
    return current_user


async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def get_current_user(
    Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)
) -> Type[User]:
    Authorize.jwt_required()

    email = Authorize.get_jwt_subject()

    return await get_user_by_email(email, db)


async def update_avatar(email: str, url: str, db: Session) -> Type[User] | None:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

async def confirm_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
