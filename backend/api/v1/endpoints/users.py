from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.models import User
from backend.schemas.user import (
    UserResponse,
    UserUpdate
)
from backend.core.security import get_current_user
from backend.crud.user import (
    read,
    update,
    delete
)
from backend.db.session import get_db

router = APIRouter(prefix='/user', tags=['users'])


@router.get('/users', response_model=List[UserResponse])
async def users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await read(current_user, db, all=True)


@router.get('/profile', response_model=List[UserResponse])
async def profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await read(current_user, db)


@router.patch('/update/{user_id:int}')
async def updateUser(data: UserUpdate, user_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return await update(user_id, current_user, db, data)


@router.delete('/delete/{user_id:int}')
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await delete(user_id, current_user, db)
