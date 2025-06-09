import emails
from celery import Celery

from src.core import get_settings

settings = get_settings()

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.task(name="send_email_task")
def send_email_task(recipients: list[str], subject: str, body: str):
    smtp_config = {
        "host": settings.MAIL_HOST,
        "port": settings.MAIL_PORT,
        "user": settings.MAIL_USER,
        "password": settings.MAIL_PASSWORD,
        "tls": settings.MAIL_TLS,
    }

    message = emails.Message(
        subject=subject, text=body, mail_from=(settings.MAIL_USERNAME, settings.MAIL_USER)
    )
    message.send(to=recipients, smtp=smtp_config)
