from typing import Annotated

from fastapi import Depends

from src.core.database import SessionDep
from src.tasks.repository import TaskRepository


class UnitOfWork:
    def __init__(self, session: SessionDep) -> None:
        self.session = session
        self.tasks = TaskRepository(session)

    async def commit(self) -> None:
        await self.session.commit()


UOWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]
