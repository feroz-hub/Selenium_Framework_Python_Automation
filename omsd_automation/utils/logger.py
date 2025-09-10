# omsd_autmation/utils/logger.py
import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Module-level state for single-run logfile / root config
_RUN_LOG_FILE: Optional[str] = None
_ROOT_CONFIGURED: bool = False


def _ensure_root_logger(
        log_dir: str = "logs",
        log_file_prefix: Optional[str] = None,
        file_level: int = logging.DEBUG,
        console_level: int = logging.INFO,
):
    """
   Configure the root logger once per test run. All child loggers will
   propagate to this root logger so that a single file collects everything.
   """
    global _RUN_LOG_FILE, _ROOT_CONFIGURED
    if _ROOT_CONFIGURED:
        return
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{log_file_prefix}_" if log_file_prefix else "testrun_"
    _RUN_LOG_FILE = os.path.join(log_dir, f"{prefix}{timestamp}.log")
    root = logging.getLogger()  # root logger
    root.setLevel(logging.DEBUG)
    # File handler -> captures DEBUG+ to file
    file_handler = logging.FileHandler(_RUN_LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(file_level)
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(name)s] | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    # Console handler -> INFO+ to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(name)s] | %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_fmt)
    # Attach handlers to root logger (single place)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    # Log the run file location (with emoji)
    root.info(f"📁 Unified log file for this run: {_RUN_LOG_FILE}")
    _ROOT_CONFIGURED = True

    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(
        name: str = "selenium-tests",
        log_dir: str = "logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file_prefix: Optional[str] = None,
) -> logging.Logger:
    """
   Return a named logger. All named loggers propagate to the single run log file.
   Usage: logger = get_logger("LoginPage")
   """
    # Ensure root configured once per process/run
    _ensure_root_logger(log_dir=log_dir, log_file_prefix=log_file_prefix, file_level=file_level,
                        console_level=console_level)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # allow child-level filtering if required
    # Do NOT add handlers to named loggers — they will propagate to root handlers
    return logger


class TestLogger:
    """Helper wrapper around a named Python logger with emoji-rich helpers."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def test_start(self, test_name: str):
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 STARTING TEST: {test_name}")
        self.logger.info("=" * 80)

    def test_end(self, test_name: str, success: bool = True):
        status = "✅ PASSED" if success else "❌ FAILED"
        self.logger.info(f"🏁 TEST COMPLETED: {test_name} - {status}")
        self.logger.info("=" * 80)

    def step(self, step_description: str):
        self.logger.info(f"📋 STEP: {step_description}")

    def action(self, action_description: str):
        self.logger.info(f"🎬 ACTION: {action_description}")

    def verification(self, verification_description: str, result: bool):
        status = "✅" if result else "❌"
        self.logger.info(f"🔍 VERIFICATION: {verification_description} - {status}")

    def warning(self, message: str):
        self.logger.warning(f"⚠️ WARNING: {message}")

    def error(self, message: str):
        self.logger.error(f"❌ ERROR: {message}")

    def debug(self, message: str):
        self.logger.debug(f"🔧 DEBUG: {message}")

    def screenshot(self, screenshot_path: str):
        self.logger.info(f"📸 SCREENSHOT: {screenshot_path}")

    def page_info(self, title: str, url: str):
        self.logger.info(f"🌐 PAGE INFO: Title='{title}', URL='{url}'")

    def element_found(self, element_description: str, locator: str = ""):
        loc_info = f" (Locator: {locator})" if locator else ""
        self.logger.info(f"✅ ELEMENT FOUND: {element_description}{loc_info}")

    def element_not_found(self, element_description: str, locator: str = ""):
        loc_info = f" (Locator: {locator})" if locator else ""
        self.logger.info(f"❌ ELEMENT NOT FOUND: {element_description}{loc_info}")

    def wait_start(self, wait_description: str, timeout: int):
        self.logger.info(f"⏳ WAITING: {wait_description} (timeout: {timeout}s)")

    def wait_success(self, wait_description: str):
        self.logger.info(f"✅ WAIT COMPLETED: {wait_description}")

    def wait_timeout(self, wait_description: str, timeout: int):
        self.logger.warning(f"⏰ WAIT TIMEOUT: {wait_description} after {timeout}s")


def setup_test_logging(test_name: str, log_dir: str = "logs") -> TestLogger:
    """Convenience: returns a TestLogger for a test (logger name = test_<test_name>)."""
    logger = get_logger(name=f"test_{test_name}", log_dir=log_dir, log_file_prefix=test_name)
    return TestLogger(logger)


def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 7):
    """Remove old logs older than `days_to_keep` (keeps the latest)."""
    if not os.path.exists(log_dir):
        return
    import time
    from pathlib import Path
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    for log_file in Path(log_dir).glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
            except OSError:
                pass
