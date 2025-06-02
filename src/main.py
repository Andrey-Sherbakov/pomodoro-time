from fastapi import FastAPI

from src import router
from src.core import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")
