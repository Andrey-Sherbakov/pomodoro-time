from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")
