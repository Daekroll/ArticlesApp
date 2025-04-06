from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import string

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from argon2 import PasswordHasher
from fastapi_mail import ConnectionConfig

from backend.db.session import get_db
from backend.schemas.user import TokenData
from backend.db.models.user import User, Token

SECRET_KEY = '1h23rui1b3oub5o1u4btoo1u4'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# urls config
host = '0.0.0.0'
port = 8000
conf = ConnectionConfig(
    MAIL_USERNAME='test-development@mail.ru',
    MAIL_PASSWORD='ApmHww4udxthsCQgq42P',
    MAIL_FROM='test-development@mail.ru',
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='ArticlesApp',

    TEMPLATE_FOLDER='backend/articles_email/templates',
)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str):
    return ph.verify(hashed_password, plain_password)


def get_password_hash(password: str):
    return ph.hash(password)


async def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    *_, token_exist = token.split()
    result = await db.execute(select(Token).filter(Token.token == token_exist))
    token_db = result.scalars().first()
    if not token_db:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception


    result = await db.execute(select(User).filter(User.email == token_data.email))
    db_user = result.scalars().first()
    if db_user is None:
        raise credentials_exception
    return db_user


def generate_timestamp_link(length=24, expires_hours=1):
    timestamp = int(datetime.now().timestamp())
    rand_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

    return f'{rand_part}_{timestamp}_{expires_hours}'

def verify_timestamp_token(token):
    try:
        rand_part, timestamp_str, expires_hours_str = token.split('_')
        timestamp = int(timestamp_str)
        expires_hours = int(expires_hours_str)

        creation_time = datetime.fromtimestamp(timestamp)
        expiration_time = creation_time + timedelta(hours=expires_hours)

        if datetime.now() > expiration_time:
            return False

        return True

    except (ValueError, AttributeError):
        return False