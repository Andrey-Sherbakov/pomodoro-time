from dataclasses import dataclass


from src.core.broker import BrokerClient
from src.users.profile.schemas import EmailBody


@dataclass
class MailClient:
    broker_client: BrokerClient

    async def send_welcome_email(self, username: str, email: str) -> None:
        subject = "Добро пожаловать!"

        body = (
            f"Здравствуйте, {username}!\n"
            f"Добро пожаловать в Pomodoro Time!\n"
            f"Ваш аккаунт был успешно создан. Теперь вы можете войти в систему, используя свои "
            f"учетные данные.\n"
            f"Если вы не регистрировались на нашем сервисе, пожалуйста, проигнорируйте это письмо.\n"
            f"С наилучшими пожеланиями,\n"
            f"Команда Pomodoro"
        )

        await self._send_text_email(subject=subject, body=body, email=email)

    async def send_password_change_email(self, username: str, email: str) -> None:
        subject = "Ваш пароль был изменен"

        body = (
            f"Здравствуйте, {username}!\n"
            f"Это автоматическое уведомление о том, что пароль для вашего аккаунта в Pomodoro Time "
            f"был успешно изменен.\n"
            f"Если это были не вы, пожалуйста, немедленно свяжитесь с нашей службой поддержки или "
            f"воспользуйтесь формой восстановления пароля.\n"
            f"С уважением,\n"
            f"Команда Pomodoro"
        )

        await self._send_text_email(subject=subject, body=body, email=email)

    async def send_goodbye_email(self, username: str, email: str) -> None:
        subject = "Ваш аккаунт был удален"

        body = (
            f"Здравствуйте, {username}.\n"
            f"Это автоматическое уведомление подтверждает, что ваш аккаунт и все связанные с ним "
            f"данные в сервисе Pomodoro Time были успешно удалены согласно вашему запросу.\n"
            f"Нам жаль, что вы уходите. Если вы захотите вернуться, вам нужно будет создать новый "
            f"аккаунт.\n"
            f"Спасибо, что были с нами.\n"
            f"С уважением,\n"
            f"Команда Pomodoro\n"
        )

        await self._send_text_email(subject=subject, body=body, email=email)

    async def _send_text_email(self, subject: str, body: str, email: str) -> None:
        email_body = EmailBody(
            subject=subject,
            body=body,
            recipients=[email],
        )
        await self.broker_client.send_mail(email_body.model_dump())