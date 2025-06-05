import factory
import pytest
from faker import Factory as FakerFactory
from pydantic import BaseModel
from pytest_factoryboy import register

from src.users.profile.models import User


faker = FakerFactory.create()


@register(_name="user_random")
class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(lambda: faker.random_int())
    username = factory.LazyFunction(lambda: faker.first_name())
    email = factory.LazyFunction(lambda: faker.email())


class TestUser(BaseModel):
    id: int
    username: str
    password: str
    hashed_password: str
    email: str
    is_admin: bool
    jti: str


@pytest.fixture
def test_user(settings) -> TestUser:
    return TestUser(
        id=1,
        username="user_test",
        password="password_test",
        hashed_password=settings.PWD_CONTEXT.hash("password_test"),
        email="test@user.com",
        is_admin=False,
        jti="test_jti",
    )