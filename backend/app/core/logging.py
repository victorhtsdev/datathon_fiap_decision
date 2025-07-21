"""
Centralized logging configuration module.

This module provides a centralized logging system for the application,
supporting both file and console output with configurable levels.
Follows software engineering best practices for logging in production applications.
"""

import logging
import os

# Configuration from environment variables
LOG_ENABLED = os.getenv("APP_LOG_ENABLED", "true").lower() == "true"
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("APP_LOG_FILE", "app.log")
LLM_LOG_ENABLED = os.getenv("LLM_LOG", "false").lower() == "true"

# Configure main application logger
logger = logging.getLogger("app")
if LOG_ENABLED:
    logger.setLevel(LOG_LEVEL)
    
    # File handler for persistent logging
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Console handler for development and debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
else:
    # Disable logging by adding null handler
    logger.addHandler(logging.NullHandler())

# Logging utility functions
def log_info(msg):
    """Log informational message."""
    if LOG_ENABLED:
        logger.info(msg)

def log_warning(msg):
    """Log warning message."""
    if LOG_ENABLED:
        logger.warning(msg)

def log_error(msg):
    """Log error message."""
    if LOG_ENABLED:
        logger.error(msg)

def log_debug(msg):
    """Log debug message."""
    if LOG_ENABLED:
        logger.debug(msg)

def llm_log(msg):
    """Log LLM-specific operations when enabled."""
    if LOG_ENABLED and LLM_LOG_ENABLED:
        logger.info(f"[LLM] {msg}")
