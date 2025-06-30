from pathlib import Path
import sys
from loguru import logger


log_path = log_path = Path(__file__).resolve().parent.parent.parent / "logs"
log_path.mkdir(exist_ok=True)

logger.remove()


def formatter(record):
    levelname = record["level"].name + ":"
    record["level"].name = levelname.ljust(9)
    return "<level>{level}</level> {message} | <cyan>{name}:{function}:{line}</cyan> \n"


logger.add(
    sys.stdout,
    level="DEBUG",
    format=formatter,
    colorize=True,
)

logger.add(
    log_path / "app.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} {message} |  {name}:{function}:{line}",
)


# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno
#         logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


# logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
# for name in ("uvicorn", "uvicorn.error", "fastapi"):
#     logger_ = logging.getLogger(name)
#     logger_.handlers = [InterceptHandler()]
#     logger_.propagate = False
