

class FakeBrokerClient:
    async def send_mail(self, message: dict) -> None:
        pass


def fake_broker_client():
    return FakeBrokerClient()