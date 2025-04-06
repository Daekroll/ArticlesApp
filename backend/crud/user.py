from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from backend.db.models.user import User, Token
from backend.schemas.user import UserResponse, UserUpdate
from backend.core.security import get_password_hash
# from backend.email.email import send_email


async def get_user(db: Session, user_id: int = None, email: str = None):
    if user_id is not None:
        query = await db.execute(select(User).filter(User.id == user_id))
        result = query.scalars().first()
    elif email is not None:
        query = await db.execute(select(User).filter(User.email == email))
        result = query.scalars().first()
    else:
        query = await db.execute(select(User).order_by(User.id))
        result = query.scalars().all()
    return result


async def get_token(token: str, db: Session):
    token = await db.execute(select(Token).filter(Token.token == token))
    return token.scalars().first()


async def add_token(token: str, db: Session):
    token_exist = await get_token(token, db)
    if token_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This token already exist'
        )
    token = Token(
        token=token,
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=30)).replace(tzinfo=None)
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)


async def del_token(token: str, db: Session):
    token = await get_token(token, db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token not found'
        )
    await db.delete(token)
    await db.commit()


async def create(user, db: Session):
    db_user = await get_user(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email alredy registered'
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # await send_email(
    #     new_user,
    #     'Registration confirm',
    #     'reg_confirm.html'
    # )
    return {'message': 'Successfully registered', 'status': status.HTTP_201_CREATED}


async def read(db: Session):
    users = await get_user(db=db)
    user_response = [
        UserResponse(
            id=user.id,
            full_name=user.full_name,
            avatar_url=user.avatar,
            email=user.email,
            is_active=user.is_active,
            is_staff=user.is_staff,
            create_at=user.created_at,
        ) for user in users
    ]
    return user_response


async def update(data: UserUpdate, user_id: int, db: Session):
    user = await get_user(db=db, user_id=user_id)
    print(user.id)
    if not user:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {'message': 'Update successfully', 'status': status.HTTP_200_OK}


async def delete(user_id: int, db: Session):
    user = await get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    await db.delete(user)
    await db.commit()
    return {'message': 'User deleted', 'status': status.HTTP_200_OK}
