import os

from fastapi import FastAPI

from src.core.logger import setup_loguru
from src.core.config import get_settings
from .middlewares import AccessLogMiddleware


app = FastAPI()

setup_loguru(
    service=os.environ.get("SERVICE_NAME", "fastapi-app"),
    level=get_settings().LOGGING_LEVEL,
    sink="text",  # TODO: switch via env
    settings={
        "backtrace": True,
        "enqueue": True,
        "diagnose": True,
    }
    if get_settings().DEBUG
    else {
        "backtrace": False,
        "enqueue": True,
        "diagnose": False,
    },
)

app.add_middleware(AccessLogMiddleware)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
