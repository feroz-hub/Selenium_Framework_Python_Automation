"""
Enhanced Software Upload Test Suite.

This module contains comprehensive tests for software upload functionality
in the Olympus Medical Software Delivery system, including popup management,
file upload operations, and multi-product testing capabilities.
"""

from pathlib import Path
from typing import List, Optional

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from omsd_autmation.pages.base_page import BasePage
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.software_page import SoftwarePage
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging, TestLogger
from test_config import (
    DEFAULT_PRODUCT, TEST_PRODUCTS, UPLOAD_DIR, TEST_FILE_NAME,
    APP_TITLE, SOFTWARE_UPLOADER_ROLE, SMOKE_TEST_MARKER, INTEGRATION_TEST_MARKER
)


class TestSoftwareUpload:
    """
    Comprehensive test suite for software upload functionality.
    
    This class provides optimized, maintainable tests for software upload operations
    including popup management, file uploads, and multi-product testing.
    """

    # Test configuration constants (imported from test_config)
    DEFAULT_PRODUCT: str = DEFAULT_PRODUCT
    TEST_PRODUCTS: List[str] = TEST_PRODUCTS
    UPLOAD_DIR: Path = UPLOAD_DIR
    TEST_FILE_NAME: str = TEST_FILE_NAME

    @pytest.fixture(autouse=True)
    def setup_test_logging(self) -> None:
        """Setup logging for each test method."""
        self.test_logger: TestLogger = setup_test_logging("software_upload")

    @pytest.fixture
    def software_uploader_login(self, driver: WebDriver) -> WebDriver:
        """
        Fixture for logging in as software uploader.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Authenticated WebDriver instance
        """
        self.test_logger.step("Logging in as software uploader")

        login = LoginPage(driver)
        username = Config.get(f"environments.staging.users.{SOFTWARE_UPLOADER_ROLE}.username")
        password = Config.get(f"environments.staging.users.{SOFTWARE_UPLOADER_ROLE}.password")

        login.login(username, password)
        login.wait_for_title(APP_TITLE)

        # Accept cookies if popup appears
        BasePage(driver).accept_cookies()
        self.test_logger.action("Login completed and cookies accepted")
        
        return driver

    @pytest.fixture
    def software_page(self, driver: WebDriver) -> SoftwarePage:
        """
        Fixture for SoftwarePage instance.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Configured SoftwarePage instance
        """
        return SoftwarePage(driver)

    def _navigate_to_upload_popup(self, software_page: SoftwarePage, product_name: Optional[str] = None) -> SoftwarePage:
        """
        Helper method to navigate to upload popup for a product.
        
        Args:
            software_page: SoftwarePage instance
            product_name: Name of the product (defaults to DEFAULT_PRODUCT)
            
        Returns:
            SoftwarePage instance for method chaining
        """
        product = product_name or self.DEFAULT_PRODUCT
        self.test_logger.step(f"Opening software list for {product}")
        software_page.open_software_list(product)
        
        self.test_logger.step("Clicking Upload Software button")
        software_page.click_upload_software()
        
        return software_page

    def _cleanup_upload_popup(self, software_page: SoftwarePage) -> None:
        """
        Helper method to cleanup upload popup.
        
        Args:
            software_page: SoftwarePage instance
        """
        self.test_logger.step("Cleaning up upload popup")
        software_page.cancel_upload_popup()

    def _verify_upload_popup_elements(self, software_page: SoftwarePage) -> bool:
        """
        Helper method to verify all upload popup elements are present.
        
        Args:
            software_page: SoftwarePage instance
            
        Returns:
            True if all elements are present, False otherwise
        """
        self.test_logger.step("Verifying all popup elements are present")

        elements_to_check = [
            ("File input field", software_page.is_file_input_visible()),
            ("Submit button", software_page.is_submit_button_visible()),
            ("Cancel button", software_page.is_visible(software_page.CANCEL_BTN)),
            ("Upload popup header", software_page.is_visible(software_page.UPLOAD_POPUP_HEADER)),
        ]

        all_elements_present = True
        for element_name, is_present in elements_to_check:
            self.test_logger.verification(f"{element_name} present", is_present)
            if not is_present:
                all_elements_present = False

        return all_elements_present

    def _get_test_file_path(self) -> Path:
        """
        Helper method to get test file path.
        
        Returns:
            Path object pointing to the test file
        """
        return self.UPLOAD_DIR / self.TEST_FILE_NAME

    @pytest.mark.smoke
    def test_open_upload_popup(self, software_uploader_login: WebDriver, software_page: SoftwarePage) -> None:
        """
        Test opening and closing the upload popup.
        
        This smoke test verifies that the upload popup can be opened and closed
        successfully, ensuring basic popup functionality is working.
        
        Args:
            software_uploader_login: Authenticated WebDriver instance
            software_page: SoftwarePage instance
        """
        self.test_logger.test_start("test_open_upload_popup")

        # Navigate to upload popup
        self._navigate_to_upload_popup(software_page)

        # Verify popup appeared
        assert software_page.is_upload_popup_visible(), "Upload Software popup did not appear"
        self.test_logger.verification("Upload popup visibility", True)

        # Verify file input is present
        assert software_page.is_file_input_visible(), "File input field is not visible"
        self.test_logger.verification("File input field visibility", True)

        # Cancel popup
        self._cleanup_upload_popup(software_page)

        # Verify we're back to software list
        assert software_page.is_software_list_opened(), "Upload Software Page didn't open properly"
        self.test_logger.verification("Software list page accessibility", True)

        self.test_logger.test_end("test_open_upload_popup", True)

    @pytest.mark.integration
    def test_upload_software_file_complete(self, software_uploader_login: WebDriver, software_page: SoftwarePage) -> None:
        """
        Test complete software file upload process.
        
        This integration test verifies the complete file upload workflow,
        including file selection and submission. If test file is not available,
        it falls back to testing UI element availability.
        
        Args:
            software_uploader_login: Authenticated WebDriver instance
            software_page: SoftwarePage instance
        """
        self.test_logger.test_start("test_upload_software_file_complete")

        # Navigate to upload popup
        self._navigate_to_upload_popup(software_page)

        # Verify popup opened
        assert software_page.is_upload_popup_visible(), "Upload Software popup did not appear"
        self.test_logger.verification("Upload popup opened", True)

        # Get test file path
        test_file_path = self._get_test_file_path()

        if test_file_path.exists():
            # Upload file and submit
            self.test_logger.step(f"Uploading file: {test_file_path}")
            software_page.upload_software_complete(str(test_file_path))
            self.test_logger.verification("File upload completed", True)
        else:
            self.test_logger.warning(f"Test file not found: {test_file_path}")
            # Test file input field availability
            self.test_logger.step("Testing file input field availability")
            assert software_page.is_file_input_visible(), "File input not available"
            assert software_page.is_submit_button_visible(), "Submit button not available"

            # Cancel since we can't upload
            self._cleanup_upload_popup(software_page)

        self.test_logger.test_end("test_upload_software_file_complete", True)

    @pytest.mark.smoke
    def test_upload_popup_elements_present(self, software_uploader_login: WebDriver, software_page: SoftwarePage) -> None:
        """
        Test that all required elements are present in upload popup.
        
        This smoke test verifies that all necessary UI elements are present
        in the upload popup, ensuring the interface is complete and functional.
        
        Args:
            software_uploader_login: Authenticated WebDriver instance
            software_page: SoftwarePage instance
        """
        self.test_logger.test_start("test_upload_popup_elements_present")

        # Navigate to upload popup
        self._navigate_to_upload_popup(software_page)

        # Verify popup is open
        assert software_page.is_upload_popup_visible(), "Upload popup not visible"

        # Check all required elements using helper method
        all_elements_present = self._verify_upload_popup_elements(software_page)
        assert all_elements_present, "Not all required popup elements are present"

        # Clean up
        self._cleanup_upload_popup(software_page)

        self.test_logger.test_end("test_upload_popup_elements_present", True)

    @pytest.mark.parametrize("product_name", TEST_PRODUCTS)
    def test_upload_popup_for_multiple_products(self, software_uploader_login: WebDriver, software_page: SoftwarePage, product_name: str) -> None:
        """
        Test upload popup functionality for multiple products.
        
        This parametrized test verifies that the upload popup works correctly
        for different products, ensuring the functionality is product-agnostic.
        
        Args:
            software_uploader_login: Authenticated WebDriver instance
            software_page: SoftwarePage instance
            product_name: Name of the product being tested
        """
        test_name = f"test_upload_popup_for_{product_name.replace('-', '_')}"
        self.test_logger.test_start(test_name)

        # Test for specific product
        self.test_logger.step(f"Testing upload popup for product: {product_name}")
        self._navigate_to_upload_popup(software_page, product_name)

        # Verify popup functionality
        assert software_page.is_upload_popup_visible(), f"Upload popup not working for {product_name}"
        self.test_logger.verification(f"Upload popup for {product_name}", True)

        # Clean up
        self._cleanup_upload_popup(software_page)

        self.test_logger.test_end(test_name, True)
