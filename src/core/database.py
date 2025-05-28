from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings


# postgresql connection
engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
