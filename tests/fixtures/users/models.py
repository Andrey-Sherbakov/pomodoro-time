import factory
import pytest
from faker import Factory as FakerFactory
from pydantic import BaseModel
from pytest_factoryboy import register

from src.users.profile.models import User
from src.users.profile.schemas import UserCreate, UserUpdate, PasswordUpdate

faker = FakerFactory.create()


@register(_name="user_random")
class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(lambda: faker.random_int())
    username = factory.LazyFunction(lambda: faker.user_name())
    email = factory.LazyFunction(lambda: faker.email())
    full_name = factory.LazyFunction(lambda: faker.name())
    age = factory.LazyFunction(lambda: faker.random_int(min=18, max=99))
    is_admin = False


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


@pytest.fixture
def user_create(user_random: User) -> UserCreate:
    return UserCreate(
        username=user_random.username,
        email=user_random.email,
        password="password",
        password_confirm="password",
        full_name=user_random.full_name,
        age=user_random.age,
    )


@pytest.fixture
def user_update(user_random: User) -> UserUpdate:
    return UserUpdate(
        username=user_random.username,
        email=user_random.email,
        full_name=user_random.full_name,
        age=user_random.age,
    )


@pytest.fixture
def password_update(test_user) -> PasswordUpdate:
    return PasswordUpdate(
        old_password=test_user.password,
        new_password="new_password",
        new_password_confirm="new_password",
    )