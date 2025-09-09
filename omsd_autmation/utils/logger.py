import logging
import os
import sys
from datetime import datetime
from typing import Optional


def get_logger(
        name: str = "selenium-tests",
        log_dir: str = "logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file_prefix: Optional[str] = None
) -> logging.Logger:
    """
    Creates and returns a configured logger instance with enhanced features.
    Logs will be saved to a file (with timestamp) and also shown on console.

    Args:
        name (str): Logger name
        log_dir (str): Directory to store log files
        console_level (int): Log level for console output
        file_level (int): Log level for file output
        log_file_prefix (str, optional): Prefix for log file name

    Returns:
        logging.Logger: Configured logger instance
    """

    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Log file with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_prefix = f"{log_file_prefix}_" if log_file_prefix else ""
    log_file = os.path.join(log_dir, f"{file_prefix}{timestamp}.log")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers in pytest multiple test runs
    if not logger.handlers:
        # File Handler (detailed logs)
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(file_level)

        # Console Handler (info-level logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)

        # Enhanced log format with colors for console
        detailed_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Log the log file location
        logger.info(f"📁 Log file created: {log_file}")

    return logger


class TestLogger:
    """Helper class for test-specific logging with emojis and structured output."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def test_start(self, test_name: str):
        """Log test start with formatting."""
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 STARTING TEST: {test_name}")
        self.logger.info("=" * 80)

    def test_end(self, test_name: str, success: bool = True):
        """Log test end with result."""
        status = "✅ PASSED" if success else "❌ FAILED"
        self.logger.info(f"🏁 TEST COMPLETED: {test_name} - {status}")
        self.logger.info("=" * 80)

    def step(self, step_description: str):
        """Log a test step."""
        self.logger.info(f"📋 STEP: {step_description}")

    def action(self, action_description: str):
        """Log an action being performed."""
        self.logger.info(f"🎬 ACTION: {action_description}")

    def verification(self, verification_description: str, result: bool):
        """Log a verification result."""
        status = "✅" if result else "❌"
        self.logger.info(f"🔍 VERIFICATION: {verification_description} - {status}")

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(f"⚠️ WARNING: {message}")

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(f"❌ ERROR: {message}")

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(f"🔧 DEBUG: {message}")

    def screenshot(self, screenshot_path: str):
        """Log screenshot capture."""
        self.logger.info(f"📸 SCREENSHOT: {screenshot_path}")

    def page_info(self, title: str, url: str):
        """Log current page information."""
        self.logger.info(f"🌐 PAGE INFO: Title='{title}', URL='{url}'")

    def element_found(self, element_description: str, locator: str = ""):
        """Log when an element is found."""
        loc_info = f" (Locator: {locator})" if locator else ""
        self.logger.info(f"✅ ELEMENT FOUND: {element_description}{loc_info}")

    def element_not_found(self, element_description: str, locator: str = ""):
        """Log when an element is not found."""
        loc_info = f" (Locator: {locator})" if locator else ""
        self.logger.info(f"❌ ELEMENT NOT FOUND: {element_description}{loc_info}")

    def wait_start(self, wait_description: str, timeout: int):
        """Log start of a wait operation."""
        self.logger.info(f"⏳ WAITING: {wait_description} (timeout: {timeout}s)")

    def wait_success(self, wait_description: str):
        """Log successful wait completion."""
        self.logger.info(f"✅ WAIT COMPLETED: {wait_description}")

    def wait_timeout(self, wait_description: str, timeout: int):
        """Log wait timeout."""
        self.logger.warning(f"⏰ WAIT TIMEOUT: {wait_description} after {timeout}s")


def setup_test_logging(test_name: str, log_dir: str = "logs") -> TestLogger:
    """
    Convenience function to set up logging for a test.

    Args:
        test_name (str): Name of the test
        log_dir (str): Directory for log files

    Returns:
        TestLogger: Configured test logger instance
    """
    logger = get_logger(
        name=f"test_{test_name}",
        log_dir=log_dir,
        log_file_prefix=test_name
    )
    return TestLogger(logger)


def get_class_logger(test_class_name: str, log_dir: str = "logs") -> TestLogger:
    """
    Get a logger for an entire test class (useful for pytest class-based tests).

    Args:
        test_class_name (str): Name of the test class
        log_dir (str): Directory for log files

    Returns:
        TestLogger: Configured test logger instance
    """
    return setup_test_logging(test_class_name.lower().replace('test', ''), log_dir)


def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 7):
    """
    Clean up old log files to prevent disk space issues.

    Args:
        log_dir (str): Directory containing log files
        days_to_keep (int): Number of days of logs to keep
    """
    if not os.path.exists(log_dir):
        return

    import time
    from pathlib import Path

    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

    for log_file in Path(log_dir).glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Deleted old log file: {log_file}")
            except OSError:
                pass


# Example usage and integration helpers
if __name__ == "__main__":
    # Example usage
    test_logger = setup_test_logging("software_upload_test")

    test_logger.test_start("test_upload_functionality")
    test_logger.step("Opening software list")
    test_logger.action("Clicking Software List button for ESG-410")
    test_logger.verification("Software list opened", True)
    test_logger.screenshot("/path/to/screenshot.png")
    test_logger.test_end("test_upload_functionality", True)