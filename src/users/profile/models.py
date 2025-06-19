from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    full_name: Mapped[str | None] = mapped_column(String(100))
    age: Mapped[int | None]
    is_admin: Mapped[bool] = mapped_column(default=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="creator")  # noqa: F821
