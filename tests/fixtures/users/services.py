import pytest

from src.users.auth.services import SecurityService, TokenBlacklistService


class FakeTokenBlacklistService:
    async def blacklist_tokens(self, *args, **kwargs) -> None:
        pass

    async def is_blacklisted(self, *args, **kwargs) -> bool:
        return False

    async def set_logout_timestamp(self, *args, **kwargs) -> None:
        pass

    async def get_logout_timestamp(self, *args, **kwargs) -> int | None:
        pass


@pytest.fixture()
def fake_blacklist_service():
    return FakeTokenBlacklistService()


@pytest.fixture()
def test_security_service(fake_blacklist_service: TokenBlacklistService, settings):
    return SecurityService(token_bl=fake_blacklist_service, settings=settings)
