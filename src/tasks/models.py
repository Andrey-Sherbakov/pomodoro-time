from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    pomodoro_count: Mapped[int] = mapped_column(default=10)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="tasks")
