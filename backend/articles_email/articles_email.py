import datetime
import logging

from aiosmtplib import SMTPDataError

from fastapi_mail import FastMail, MessageSchema, MessageType

from core.settings import conf
from schemas.user import UserForEmail

file_logger = logging.getLogger('file_logger')


async def send_email(
        user: UserForEmail,
        subject: str,
        template_name: str,
        activate_link: str
) -> None:
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            template_body={
                'full_name': user.full_name,
                'current_year': datetime.datetime.now().year,
                'confirmation_link':activate_link
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=template_name)
    except SMTPDataError as smtp:
        file_logger.warning(f'Ошибка данных SMTP: {smtp}')
