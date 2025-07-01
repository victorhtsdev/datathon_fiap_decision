import logging
import os

LOG_ENABLED = os.getenv("APP_LOG_ENABLED", "true").lower() == "true"
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("APP_LOG_FILE", "app.log")
LOG_CONSOLE = os.getenv("LLM_CONSOLE_LOG", "false").lower() == "true"

logger = logging.getLogger("app")
if LOG_ENABLED:
    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if LOG_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
else:
    logger.addHandler(logging.NullHandler())
