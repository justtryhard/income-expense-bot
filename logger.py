import logging
import os
from logging.handlers import RotatingFileHandler

# todo!

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "bot.log")

logger = logging.getLogger("bot")
logger.setLevel(logging.ERROR)

handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,  # 1 MB
    backupCount=3,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)