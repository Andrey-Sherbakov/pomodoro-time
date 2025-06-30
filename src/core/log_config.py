from pathlib import Path
import sys
import logging


log_path = log_path = Path(__file__).resolve().parent.parent.parent / "logs"
log_path.mkdir(exist_ok=True)


logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(module)10s:%(lineno)-3d %(levelname)-8s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f"{log_path}/app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
