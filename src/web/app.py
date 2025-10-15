import os

from fastapi import FastAPI

from src.core.logger import setup_loguru
from src.core.config import get_settings


app = FastAPI()

setup_loguru(
    service=os.environ.get("SERVICE_NAME", "fastapi-app"),
    level=get_settings().LOGGING_LEVEL,
)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
