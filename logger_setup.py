import logging
import os

LOGFILE = os.path.expanduser("~/folderchecker.log")

logging.basicConfig(
    filename=LOGFILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s"
)

logger = logging.getLogger("folderchecker")
