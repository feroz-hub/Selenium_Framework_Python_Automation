"""
Test Configuration Constants.

This module contains all test-related constants and configuration values
used across the test suite for better maintainability and consistency.
"""

from pathlib import Path
from typing import List

# Paths
TEST_BASE_DIR = Path(__file__).parent.parent  # omsd_automation
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # repository root

# Directories under the repository root
UPLOAD_DIR = PROJECT_ROOT / "uploads"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

# Unified logs directory anchored at repo root
LOGS_DIR = PROJECT_ROOT / "logs"

# Product configuration
OMSD_ESG_410 = "ESG-410"
OMSD_USG_410 = "USG-410"
TEST_PRODUCTS: List[str] = ["ESG-410", "ESG-420"]

# Test file configuration
TEST_FILE_NAME = "ESG-410_v01.00.00.00-New_11"

# Timeout configuration (in seconds)
DEFAULT_TIMEOUT = 15
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 30

# Test markers
SMOKE_TEST_MARKER = "smoke"
INTEGRATION_TEST_MARKER = "integration"
REGRESSION_TEST_MARKER = "regression"

# Application configuration
APP_TITLE = "Olympus Medical Software Delivery"
LOGIN_TIMEOUT = 10
POPUP_TIMEOUT = 10

# User roles
SOFTWARE_UPLOADER_ROLE = "software_uploader"
ADMIN_ROLE = "admin"
VIEWER_ROLE = "viewer"
