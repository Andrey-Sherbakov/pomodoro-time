import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.profile.repository import UserRepository


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)
