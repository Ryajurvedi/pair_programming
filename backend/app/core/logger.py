import logging
import sys

# Define a standard format for log entries
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str = "app", level=logging.INFO):
    """
    Initializes and returns a logger instance. 
    It is initialized only once and shared across all modules.
    """
    # Check if the logger has already been configured
    if logging.getLogger(name).handlers:
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    
    # Add handler if it doesn't exist
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Initialize the main application logger instance
logger = setup_logger()