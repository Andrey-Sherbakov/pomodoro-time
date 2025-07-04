import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI

log_path = Path(__file__).resolve().parent.parent.parent.parent / "logs" / "pomodoro-time"
log_path.mkdir(exist_ok=True, parents=True)

# formatters
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)-50s | %(filename)s:%(funcName)s:%(lineno)d"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)


class ColorFormatter(logging.Formatter):
    COLOR_MAP = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m\033[97m",
    }
    RESET = "\033[0m"

    def __init__(self, datefmt: str = DATE_FORMAT):
        super().__init__(datefmt=datefmt)
        self.datefmt = datefmt

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLOR_MAP.get(record.levelname, self.RESET)
        levelname = f"{color}{record.levelname:<8}{self.RESET}"
        asctime = self.formatTime(record, self.datefmt)
        message = record.getMessage()
        return (
            f"{asctime} | {levelname} | {message:<50} "
            f"| {record.filename}:{record.funcName}:{record.lineno}"
        )


# getting logger
logger = logging.getLogger("pomodoro")
logger.setLevel(logging.DEBUG)

# console handler setup
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter())
logger.addHandler(console_handler)

# file handlers setup
debug_file_handler = RotatingFileHandler(
    log_path / "debug.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)
debug_file_handler.setLevel(logging.DEBUG)
debug_file_handler.setFormatter(formatter)
logger.addHandler(debug_file_handler)

info_file_handler = RotatingFileHandler(
    log_path / "info.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(formatter)
logger.addHandler(info_file_handler)

warning_file_handler = RotatingFileHandler(
    log_path / "warning.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)
warning_file_handler.setLevel(logging.WARNING)
warning_file_handler.setFormatter(formatter)
logger.addHandler(warning_file_handler)


# custom handlers setup
class TelegramHandler(logging.Handler):
    def __init__(self, broker_client) -> None:
        super().__init__(level=logging.ERROR)
        self.broker_client = broker_client

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
            msg = f"{record.asctime} | {record.levelname:<8} | {message:<50}"
            asyncio.create_task(self.broker_client.send_tg_message(msg))
        except Exception:
            self.handleError(record)


def logger_startup(app: FastAPI) -> None:
    telegram_handler = TelegramHandler(broker_client=app.state.broker_client)
    logger.addHandler(telegram_handler)
