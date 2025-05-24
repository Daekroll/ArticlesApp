from datetime import timedelta
from typing import List

from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.db.models import User
from backend.schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    UserUpdate
)
from backend.core.security import (
    verify_password,
    create_access_token,
    get_current_user, oauth2_scheme
)
from backend.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.crud.user import (
    create,
    activate,
    get_user,
    add_token,
    del_token
)
from backend.db.session import get_db

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Token)
async def login(
        from_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = await get_user(db=db, email=from_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User does not exist'
        )
    try:
        verify_password(from_data.password, db_user.hashed_password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': db_user.email}, expires_delta=access_token_expires
    )
    await add_token(access_token, db)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/logout')
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    await del_token(token, db)
    return {'message': 'Successful logged out', 'status': status.HTTP_200_OK}


@router.post('/register')
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create(user, db)


@router.get('/reg-confirm/{token}')
async def reg_confirm(token: str, db: Session = Depends(get_db)):
    return await activate(token, db)
