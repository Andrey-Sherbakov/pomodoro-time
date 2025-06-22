import json
import uuid
from dataclasses import dataclass

import aio_pika
from aio_pika.abc import AbstractRobustChannel

from src.core.config import Settings
from src.users.profile.schemas import EmailBody


@dataclass
class MailClient:
    channel: AbstractRobustChannel
    settings: Settings

    async def send_welcome_email(self, username: str, email: str) -> None:
        subject = "Добро пожаловать!"

        message = (
            f"Здравствуйте, {username}!\n"
            f"Добро пожаловать в Pomodoro Time!\n"
            f"Ваш аккаунт был успешно создан. Теперь вы можете войти в систему, используя свои "
            f"учетные данные.\n"
            f"Если вы не регистрировались на нашем сервисе, пожалуйста, проигнорируйте это письмо.\n"
            f"С наилучшими пожеланиями,\n"
            f"Команда Pomodoro"
        )

        email_body = EmailBody(
            subject=subject,
            message=message,
            recipients=[email],
        )
        await self._send_email(email_body)

    async def send_password_change_email(self, username: str, email: str) -> None:
        subject = "Ваш пароль был изменен"

        message = (
            f"Здравствуйте, {username}!\n"
            f"Это автоматическое уведомление о том, что пароль для вашего аккаунта в Pomodoro Time "
            f"был успешно изменен.\n"
            f"Если это были не вы, пожалуйста, немедленно свяжитесь с нашей службой поддержки или "
            f"воспользуйтесь формой восстановления пароля.\n"
            f"С уважением,\n"
            f"Команда Pomodoro"
        )

        email_body = EmailBody(
            subject=subject,
            message=message,
            recipients=[email],
        )
        await self._send_email(email_body)

    async def send_goodbye_email(self, username: str, email: str) -> None:
        subject = "Ваш аккаунт был удален"

        message = (
            f"Здравствуйте, {username}.\n"
            f"Это автоматическое уведомление подтверждает, что ваш аккаунт и все связанные с ним "
            f"данные в сервисе Pomodoro Time были успешно удалены согласно вашему запросу.\n"
            f"Нам жаль, что вы уходите. Если вы захотите вернуться, вам нужно будет создать новый "
            f"аккаунт.\n"
            f"Спасибо, что были с нами.\n"
            f"С уважением,\n"
            f"Команда Pomodoro\n"
        )

        email_body = EmailBody(
            subject=subject,
            message=message,
            recipients=[email],
        )
        await self._send_email(email_body)

    async def _send_email(self, email_body: EmailBody) -> None:
        await self.channel.declare_queue(self.settings.BROKER_MAIL_TOPIC, durable=True)

        message = aio_pika.Message(
            body=json.dumps(email_body.model_dump()).encode(),
            correlation_id=str(uuid.uuid4()),
            reply_to=self.settings.BROKER_MAIL_CALLBACK_TOPIC,
        )
        await self.channel.default_exchange.publish(
            message=message,
            routing_key=self.settings.BROKER_MAIL_TOPIC,
        )
