import logging
from pathlib import Path

LOG_DIR = Path.home() / "Library/Logs/FolderChecker"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOGFILE = LOG_DIR / "folderchecker.log"

logging.basicConfig(
    filename=str(LOGFILE),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s"
)

logger = logging.getLogger("folderchecker")
