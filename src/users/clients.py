from worker.celery import send_email_task


class MailClient:
    @staticmethod
    async def send_welcome_email(username: str, email: str) -> None:
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

        send_email_task.delay(recipients=[email], subject=subject, body=message)

    @staticmethod
    async def send_password_change_email(username: str, email: str) -> None:
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

        send_email_task.delay(recipients=[email], subject=subject, body=message)

    @staticmethod
    async def send_goodbye_email(username: str, email: str) -> None:
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

        send_email_task.delay(recipients=[email], subject=subject, body=message)