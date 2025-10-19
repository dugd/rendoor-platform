import json
import sys
import logging
import traceback
import io
from typing import Any, Dict

from loguru import logger


class InterceptHandler(logging.Handler):
    """Redirect messages stdlib logging to loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        filter_filenames = {__file__}
        _logging_file = getattr(logging, "__file__", None)
        if _logging_file:
            filter_filenames.add(_logging_file)

        frame = logging.currentframe()
        depth = 0
        while frame and frame.f_back and frame.f_code.co_filename in filter_filenames:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _json_sink(message):
    """Custom JSON sink"""
    r = message.record

    payload = {
        "timestamp": r["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": r["level"].name,
        "logger": r["name"],
        "message": r["message"],
    }

    payload.update(r.get("extra") or {})
    if r["exception"]:
        payload["exc_info"] = str(r["exception"])
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _text_sink(message):
    """Custom text sink"""
    r = message.record
    ts = r["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    level = r["level"].name
    logger_name = r["name"]
    msg = r["message"]

    extra = r.get("extra") or {}
    service = extra.get("service")
    tail_extras = {k: v for k, v in extra.items() if k != "service"}

    head = f"{ts} | {level:<8} | {logger_name} | {service}"
    parts = [head, "-", msg]

    if tail_extras:
        kv = ", ".join(f"{k}={v}" for k, v in tail_extras.items())
        parts.append(f"| {kv}")

    if r["exception"]:
        output = io.StringIO()
        traceback.print_exc(file=output)
        parts.append(f"\n{output.getvalue()}")

    sys.stderr.write(" ".join(str(p) for p in parts) + "\n")


def setup_loguru(
    service: str = "app",
    level: str = "INFO",
    settings: Dict[str, Any] | None = None,
    sink: str = "json",  # 'json', 'text', 'both'
):
    """Clear and intercept default loggers and setup custom

    Parameters:
    - service: service name to include in `extra`
    - level: minimum log level
    - settings: loguru .add settings (shared across sinks)
    - sink: choose output sink: 'json' (default) or 'text'
    """
    if settings is None:
        settings = {
            "backtrace": False,
            "enqueue": True,
            "diagnose": False,
        }
    for handlers in logging.root.handlers[:]:
        logging.root.removeHandler(handlers)
    logging.root.setLevel(logging.NOTSET)

    intercept = InterceptHandler()
    logging.basicConfig(handlers=[intercept], level=logging.NOTSET)
    for name in (
        "uvicorn",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "celery",
        "kombu",
        "asyncio",
    ):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True

    logger.remove()

    selected = sink.lower()
    if selected not in {"json", "text"}:
        selected = "json"

    def _serialize(record):
        subset = {
            "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record["level"].name,
            "logger": record["name"],
            "service": service,
            "exception": str(record["exception"]) if record["exception"] else None,
            "message": record["message"],
            "extra": record.get("extra") or [],
        }
        return json.dumps(subset)

    def _patcher_json(record):
        record["extra"]["serialized"] = _serialize(record)

    def _patcher_text(record):
        record["service"] = service

    if selected == "json":
        # logger.add(_json_sink, level=level, **settings)
        logger.add(
            sys.stdout,
            format="{extra[serialized]}",
            level=level,
            **settings,
        )
        logger.configure(patcher=_patcher_json)

    if selected == "text":
        # logger.add(_text_sink, level=level, **settings)
        logger.add(
            sys.stderr,
            format="{time:YYYY-M-D HH:mm:ss.SSS} | {level} | {name} | {service} | {message} | {extra}",
            level=level,
            **settings,
        )
        logger.configure(patcher=_patcher_text)

    return logger


if __name__ == "__main__":
    log = setup_loguru(
        sink="json",
        level="DEBUG",
        service="my-service",
        settings={"backtrace": True, "diagnose": True},
    )
    log = log.bind(user="me", ip="0.0.0.0")
    log.info("Hello world!")
    try:
        (lambda x: 1 / 0)(1)
    except ZeroDivisionError:
        log.exception("Something went wrong")
    log.debug("Debug message")
