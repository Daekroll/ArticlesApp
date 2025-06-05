import os
from logging.config import dictConfig
from pathlib import Path
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

#main settings

SECRET_KEY = os.getenv('SECRET_KEY','test_secret_key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

HOST = '0.0.0.0'
PORT = 8080



#database settings
DATABASE_HOST=os.getenv('DATABASE_HOST','localhost')
DATABASE_NAME=os.getenv('POSTGRES_DB','test_db')
DATABASE_USER=os.getenv('POSTGRES_USER','test_user')
DATABASE_PASSWORD=os.getenv('POSTGRES_PASSWORD','1234')

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'

#email settings
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME','TEST@MAIL.RU'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD','TEST@MAIL.RU'),
    MAIL_FROM=os.getenv('MAIL_USERNAME','TEST@MAIL.RU'),
    MAIL_PORT=465,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM_NAME='ArticlesApp',

    TEMPLATE_FOLDER=(BASE_DIR / 'templates/'),
    SUPPRESS_SEND=os.getenv('SUPPRESS_SEND','1') == '1'
)

#password validation
PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
PATTERN_EMAIL = r'[1-9a-zA-Z._%+-]+@[a-zA-Z]+\.[a-zA-Z]{2,}$'

logs_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs', 'articles_app.log'),
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        'console_logger': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'file_logger': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

dictConfig(logging_config)
