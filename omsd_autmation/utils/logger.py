import logging
import os
from datetime import datetime


def get_logger(name: str = "selenium-tests", log_dir: str = "logs") -> logging.Logger:
    """
    Creates and returns a configured logger instance.
    Logs will be saved to a file (with timestamp) and also shown on console.
    """

    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Log file with timestamp
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers in pytest multiple test runs
    if not logger.handlers:
        # File Handler (detailed logs)
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setLevel(logging.DEBUG)

        # Console Handler (info-level logs)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Log format
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
