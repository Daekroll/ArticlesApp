from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os
load_dotenv()

#main settings
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HOST = '0.0.0.0'
PORT = 8000

#password validation
PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'


#database settings
DATABASE_HOST=os.getenv('DATABASE_HOST')
DATABASE_NAME=os.getenv('DATABASE_NAME')
DATABASE_USER=os.getenv('DATABASE_USER')
DATABASE_PASSWORD=os.getenv('DATABASE_PASSWORD')
SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}]:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'

#email settings
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_USERNAME'),
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='ArticlesApp',

    TEMPLATE_FOLDER='backend/articles_email/templates',
)