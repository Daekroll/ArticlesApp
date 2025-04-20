
from asgiref.sync import sync_to_async

from backend.schemas.user import UserForEmail
from celery_app import celery_app
from backend.articles_email.articles_email import send_email

@celery_app.task(name='send_email_task')
def send_email_task(user: UserForEmail, subject: str, template_name: str, link: str):
    async def _send():
        await send_email(user, subject, template_name, link)

    return sync_to_async(_send)()