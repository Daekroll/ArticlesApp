import logging
from functools import wraps
from typing import Callable, Optional, Type

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from backend.db.models import User
from backend.db.session import Base
from backend.schemas.article import ArticleUpdate
from schemas.user import UserUpdate

file_logger = logging.getLogger('file_logger')

def check_user_permission(model: Type[Base]) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(
                instance_id: int,
                current_user: User,
                db: Session,
                data: Optional[ArticleUpdate] = None):

            result = await db.execute(select(model).filter(model.id == instance_id))
            instance = result.scalars().first()
            if not instance:
                file_logger.warning(f'{model.__name__} not found')
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'{model.__name__} not found'
                )
            if instance.author_id != current_user.id and not current_user.is_staff:
                file_logger.warning('You don`t have permission')
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You don`t have permission'
                )
            if data:
                return await func(instance_id, current_user, db, data)
            return await func(instance_id, current_user, db)

        return wrapper

    return decorator


def check_user_is_active(schema: Type[BaseModel]) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(
                author: User,
                obj: schema,
                db: Session,
                *args,
                **kwargs,
        ):
            if not author.is_active:
                file_logger.warning('You need  to confirm email')
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You need  to confirm email'
                )
            return await func(author, obj, db, *args, **kwargs)

        return wrapper

    return decorator


def check_user_is_staff_or_self(func) -> Callable:
    @wraps(func)
    async def wrapper(
            user_id: int,
            current_user: User,
            db: Session,
            data: Optional[UserUpdate] = None,
            *args,
            **kwargs,
    ):
        if not current_user.is_staff and current_user.id != user_id:
            file_logger.warning('You don`t have permission')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You don`t have permission'
            )
        if data:
            return await func(user_id, current_user, db, data, *args, **kwargs)
        return await func(user_id, current_user, db, *args, **kwargs)
    return wrapper
