import logging
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from backend.db.models.user import User, Token
from backend.schemas.user import UserResponse, UserUpdate, UserForEmail
from backend.core.security import get_password_hash, generate_timestamp_link, verify_timestamp_token
from backend.core.settings import HOST, PORT
from backend.articles_email.articles_email import send_email
from backend.tasks.email_tasks import send_email_task
from core.decorators import check_user_is_staff_or_self

console_logger = logging.getLogger('console_logger')
file_logger = logging.getLogger('file_logger')

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
        file_logger.warning('This token exists')
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
    console_logger.info('Token add')


async def del_token(token: str, db: Session):
    token = await get_token(token, db)
    if not token:
        file_logger.warning('This token don`t exists')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token not found'
        )
    await db.delete(token)
    await db.commit()
    console_logger.info('Token delete')

async def create(user, db: Session):
    db_user = await get_user(db=db, email=user.email)
    if db_user:
        file_logger.warning('Email alredy registered')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email alredy registered'
        )

    hashed_password = get_password_hash(user.password)
    full_link=generate_timestamp_link()
    rand_part, *_ = full_link.split('_')
    confirmation_url = f'http://{HOST}:{PORT}/auth/reg-confirm/{full_link}'
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        activate_link=rand_part
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    console_logger.info('User register')
    user_data = UserForEmail.model_validate(new_user)
    await send_email_task(
        user_data,
        confirmation_url,
        'Registration confirm',
        'reg_confirm.html'
    )
    return {'message': 'Successfully registered', 'status': status.HTTP_201_CREATED}


async def read(current_user: User,db: Session, user_list=False):
    if current_user.is_staff and user_list:
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
    elif not all:
        user = await get_user(db=db,user_id=current_user.id)
        user_response = UserResponse.model_validate(user)
    else:
        file_logger.warning('You don`t have permission')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='You don`t have permission'
        )
    return user_response

@check_user_is_staff_or_self
async def update(
        user_id: int,
        current_user: User,
        db: Session,
        data: UserUpdate
):
    user = await get_user(db=db, user_id=user_id)
    print(user.id)
    if not user:
        file_logger.warning('User not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    console_logger.info('Update successfully')
    return {'message': 'Update successfully', 'status': status.HTTP_200_OK}

@check_user_is_staff_or_self
async def delete(
        user_id: int,
        current_user: User,
        db: Session
):
    user = await get_user(db=db, user_id=user_id)
    if not user:
        file_logger.warning('User not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    await db.delete(user)
    await db.commit()
    console_logger.info('User deleted')
    return {'message': 'User deleted', 'status': status.HTTP_200_OK}


async def activate(token: str, db: Session):
    rand_part, *_ = token.split('_')
    query = await db.execute(select(User).filter(User.activate_link == rand_part))
    user = query.scalars().first()

    if not user:
        file_logger.warning('Confirm token invalid')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Confirm token invalid'
        )

    if not verify_timestamp_token(token):
        file_logger.warning('Token expired')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token expired'
        )

    user.is_active = True
    user.activate_link = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    console_logger.info('User activate!')
    return {'message':'User activate!'}