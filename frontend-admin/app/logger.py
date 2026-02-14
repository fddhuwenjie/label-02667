"""日志模块"""
import logging
from pathlib import Path
from datetime import datetime

LOG_DIR = Path.home() / ".sql_manager_logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("sql_manager")


def log_info(msg: str):
    logger.info(msg)


def log_error(msg: str):
    logger.error(msg)


def log_warning(msg: str):
    logger.warning(msg)
