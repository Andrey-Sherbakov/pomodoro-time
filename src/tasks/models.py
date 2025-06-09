from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import Base


class Task(Base):
    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    pomodoro_count: Mapped[int] = mapped_column(default=10)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    category: Mapped["Category"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(back_populates="tasks")  # noqa: F821


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")
