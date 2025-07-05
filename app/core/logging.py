import logging
import os

LOG_ENABLED = os.getenv("APP_LOG_ENABLED", "true").lower() == "true"
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("APP_LOG_FILE", "app.log")
LLM_LOG_ENABLED = os.getenv("LLM_LOG", "false").lower() == "true"

logger = logging.getLogger("app")
if LOG_ENABLED:
    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Sempre mostra no console se LOG_ENABLED
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
else:
    logger.addHandler(logging.NullHandler())

def log_info(msg):
    if LOG_ENABLED:
        logger.info(msg)

def log_warning(msg):
    if LOG_ENABLED:
        logger.warning(msg)

def log_error(msg):
    if LOG_ENABLED:
        logger.error(msg)

def log_debug(msg):
    if LOG_ENABLED:
        logger.debug(msg)

def llm_log(msg):
    if LOG_ENABLED and LLM_LOG_ENABLED:
        logger.info(f"[LLM] {msg}")
