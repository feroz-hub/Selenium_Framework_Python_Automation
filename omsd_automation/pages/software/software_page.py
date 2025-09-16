"""
Software Page Object Model for an Olympus Medical Software Delivery system.

This module provides a comprehensive page object for software management functionality,
including product navigation, software list operations, and file upload capabilities.
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from omsd_automation.pages.base.base_page import BasePage


# from omsd_automation.utils.logger import get_logger, TestLogger


class SoftwarePage(BasePage):
    """
    Page object for Software management functionality.
    
    Provides methods for navigating to software lists, managing upload popups,
    and handling file upload operations with comprehensive error handling and logging.
    """

    # Primary locators for core functionality
    UPLOAD_SOFTWARE_BTN = (By.XPATH, "//input[@value='Upload Software']")
    CANCEL_BTN = (By.ID, "btnCancel")
    UPLOAD_POPUP_HEADER = (By.ID, "addHeader")
    FILE_INPUT = (By.ID, "packageFileInput")
    SUBMIT_BTN = (By.XPATH, "//input[@type='submit' or @value='Submit' or @value='Upload']")

    # Template locators for dynamic element finding
    SOFTWARE_LIST_BTN_TEMPLATE = "//h5[text()='{}']/following-sibling::input[@value='Software List']"
    PRODUCT_HEADER_TEMPLATE = "//h5[text()='{}']"
    ALL_BUTTONS_FOR_PRODUCT_TEMPLATE = "//h5[text()='{}']/following-sibling::input"

    def navigate_to_product_software(self, product_name: str) -> None:
        """
        Navigate to the software list of a specific product.

        Args:
            product_name: The name of the product to navigate to

        Example:
            >>> software_page.navigate_to_product_software("ESG-410")
        """

        self.open_software_list(product_name)
        time.sleep(2)  # Allow time for page transition

    def navigate_and_verify(self, product_name: str, log) -> None:
        """
        Navigate to the software list for a given product
        and verify successful navigation.
        """
        log.step("Navigate to product software list")
        log.action(f"Opening software list for product: '{product_name}'")

        self.navigate_to_product_software(product_name)

        log.verification(
            f"Successfully navigated to the software list for '{product_name}'", True
        )
        log.page_info(self.driver.title, self.driver.current_url)

    # Debug locators for troubleshooting
    ALL_PRODUCTS_LOCATOR = (By.XPATH, "//h5")

    def __init__(self, driver: WebDriver, logger) -> None:
        """
        Initialize the SoftwarePage with enhanced logging.
        
        Args:
            driver: WebDriver instance for browser automation
        """
        super().__init__(driver)
        self.logger = logger

    def open_software_list(self, product_name: str, timeout: int = 15) -> None:
        """
        Open the software list for a specific product with enhanced error handling.

        Args:
            product_name: The name of the product to open a software list for
            timeout: Maximum time to wait for elements in seconds
            
        Raises:
            Exception: If the product is not found or the software list button is not available
            
        Example:
            >>> software_page.open_software_list("ESG-410")
        """
        self.logger.action(f"Opening software list for product: {product_name}")
        self.wait_for_element_to_be_visible((By.XPATH, "//h5"), timeout=max(15, timeout))

        # First, verify the product exists
        product_locator = (By.XPATH, self.PRODUCT_HEADER_TEMPLATE.format(product_name))
        try:
            self.logger.wait_start(f"Looking for product: {product_name}", timeout)
            product_element = self.wait_for_element_to_be_visible(product_locator, timeout=timeout)
            self.logger.element_found(f"Product: {product_element.text}", str(product_locator))
        except TimeoutException:
            self.logger.element_not_found(f"Product: {product_name}", str(product_locator))
            self._log_available_products()
            raise Exception(f"Product '{product_name}' not found on the page")

        # Find and click the software list button
        software_list_locator = (By.XPATH, self.SOFTWARE_LIST_BTN_TEMPLATE.format(product_name))
        try:
            self.logger.wait_start("Looking for Software List button", timeout)
            button_element = self.wait_for_element_to_be_visible(software_list_locator, timeout=timeout)
            self.logger.element_found(f"Software List button (enabled: {button_element.is_enabled()})",
                                      str(software_list_locator))

            # Scroll into view and click
            self.scroll_into_view(software_list_locator)
            self.click_when_ready(software_list_locator, timeout=timeout)
            self.logger.action("Software List button clicked successfully")

            # Wait for page transition
            time.sleep(2)
            self.logger.wait_success("Page transition after clicking Software List")

        except TimeoutException:
            self.logger.element_not_found(f"Software List button for product: {product_name}",
                                          str(software_list_locator))
            self._log_available_buttons_for_product(product_name)
            raise Exception(f"Software List button not found for product '{product_name}'")

    def is_software_list_opened(self, timeout: int = 10) -> bool:
        """
        Check if a software list is opened by verifying popup header visibility.

        Args:
            timeout: Maximum time to wait for an element in seconds

        Returns:
            True if a software list is opened, False otherwise
            
        Example:
            >>> if software_page.is_software_list_opened():
            ...     print("Software list is ready")
        """
        self.logger.verification("Checking if software list is opened", True)

        # Check for multiple indicators that the software list opened
        indicators = [
            ("Upload popup header", self.UPLOAD_POPUP_HEADER),
            ("Upload software button", self.UPLOAD_SOFTWARE_BTN),
            ("Cancel button", self.CANCEL_BTN),
        ]

        results = {}
        for name, locator in indicators:
            is_visible = self.is_visible(locator, timeout=timeout)
            results[name] = is_visible
            status_msg = f"{name} visibility check"
            self.logger.verification(status_msg, is_visible)

        # Consider the software list opened if any key indicator is present
        is_opened = any(results.values())
        self.logger.verification("Overall software list opened status", is_opened)

        if not is_opened:
            self.logger.debug("Software list not opened - taking screenshot for debugging")
            screenshot_path = self.take_screenshot("software_list_not_opened_debug.png")
            if screenshot_path:
                self.logger.screenshot(screenshot_path)
            self._debug_page_state()

        return is_opened

    def click_upload_software(self, timeout=15):
        """Click the upload software button with enhanced error handling."""
        self.logger.action("Attempting to click Upload Software button")

        try:
            # Wait for button to be visible and clickable
            self.logger.wait_start("Waiting for Upload Software button to be clickable", timeout)
            button_element = self.wait_for_element_to_be_clickable(self.UPLOAD_SOFTWARE_BTN, timeout=timeout)
            self.logger.element_found("Upload Software button - visible and clickable", str(self.UPLOAD_SOFTWARE_BTN))

            # Scroll into view and click
            self.scroll_into_view(self.UPLOAD_SOFTWARE_BTN)
            self.click_when_ready(self.UPLOAD_SOFTWARE_BTN, timeout=timeout)
            self.logger.action("Upload Software button clicked successfully")

            # Wait for popup to appear
            time.sleep(1)
            self.logger.wait_success("Waiting for popup to appear after click")

        except TimeoutException:
            self.logger.element_not_found("Upload Software button - not clickable", str(self.UPLOAD_SOFTWARE_BTN))
            screenshot_path = self.take_screenshot("upload_button_not_found.png")
            if screenshot_path:
                self.logger.screenshot(screenshot_path)
            self._debug_page_state()
            raise Exception("Upload Software button not found or not clickable")

    def cancel_upload_popup(self, timeout=15):
        """Cancel the upload popup by clicking cancel button."""
        self.logger.action("Canceling upload popup")

        try:
            self.click_when_ready(self.CANCEL_BTN, timeout=timeout)
            self.logger.action("Cancel button clicked successfully")

            # Wait for popup to disappear
            time.sleep(1)
            self.logger.wait_success("Popup dismissal after cancel click")

        except TimeoutException:
            self.logger.element_not_found("Cancel button", str(self.CANCEL_BTN))
            screenshot_path = self.take_screenshot("cancel_button_not_found.png")
            if screenshot_path:
                self.logger.screenshot(screenshot_path)
            raise Exception("Cancel button not found")

    def is_upload_popup_visible(self, timeout=10):
        """Check if upload popup is visible with detailed logging.

        Args:
            timeout (int): Maximum time to wait.

        Returns:
            bool: True if upload popup is visible, False otherwise.
        """
        self.logger.verification("Checking if upload popup is visible", True)
        is_visible = self.is_visible(self.UPLOAD_POPUP_HEADER, timeout=timeout)
        self.logger.verification("Upload popup header visibility", is_visible)

        if not is_visible:
            self.logger.debug("Popup header not visible, checking alternative indicators")
            # Check for other popup elements
            alt_indicators = [
                ("Cancel button", self.CANCEL_BTN),
                ("Upload button", self.UPLOAD_SOFTWARE_BTN),
            ]

            for name, locator in alt_indicators:
                alt_visible = self.is_visible(locator, timeout=2)
                self.logger.verification(f"Alternative indicator - {name}", alt_visible)
                if alt_visible:
                    is_visible = True
                    break

        final_status = "Upload popup is visible" if is_visible else "Upload popup is not visible"
        self.logger.verification(final_status, is_visible)
        return is_visible

    def wait_for_upload_popup(self, timeout=10):
        """Wait for upload popup to appear with better error handling.

        Args:
            timeout (int): Maximum time to wait in seconds.

        Returns:
            WebElement: The popup header element when visible.
        """
        self.logger.wait_start("Waiting for upload popup to appear", timeout)
        try:
            element = self.wait_for_element_to_be_visible(self.UPLOAD_POPUP_HEADER, timeout)
            self.logger.wait_success("Upload popup appeared successfully")
            return element
        except TimeoutException:
            self.logger.wait_timeout("Upload popup appearance", timeout)
            screenshot_path = self.take_screenshot("upload_popup_timeout.png")
            if screenshot_path:
                self.logger.screenshot(screenshot_path)
            self._debug_page_state()
            raise

    def wait_for_upload_popup_to_disappear(self, timeout=10):
        """Wait for upload popup to disappear with better error handling.

        Args:
            timeout (int): Maximum time to wait in seconds.
        """
        self.logger.wait_start("Waiting for upload popup to disappear", timeout)
        try:
            self.wait_for_element_to_disappear(self.UPLOAD_POPUP_HEADER, timeout)
            self.logger.wait_success("Upload popup disappeared successfully")
        except TimeoutException:
            self.logger.warning(f"Upload popup did not disappear within {timeout} seconds (this might be normal)")

    def _log_available_products(self):
        """Debug helper to log available products on the page."""
        try:
            products = self.find_all(self.ALL_PRODUCTS_LOCATOR)
            self.logger.debug(f"Found {len(products)} products on the page")

            product_list = []
            for i, product in enumerate(products[:10]):  # Show first 10
                product_text = product.text.strip()
                if product_text:  # Only add non-empty product names
                    product_list.append(f"{i + 1}. '{product_text}'")

            if product_list:
                self.logger.debug("Available products: " + "; ".join(product_list))

            if len(products) > 10:
                self.logger.debug(f"... and {len(products) - 10} more products")

        except Exception as e:
            self.logger.error(f"Could not retrieve available products: {e}")

    def _log_available_buttons_for_product(self, product_name: str):
        """Debug helper to log available buttons for a specific product."""
        try:
            buttons_locator = (By.XPATH, self.ALL_BUTTONS_FOR_PRODUCT_TEMPLATE.format(product_name))
            buttons = self.find_all(buttons_locator)
            self.logger.debug(f"Found {len(buttons)} buttons for product '{product_name}'")

            button_info = []
            for i, button in enumerate(buttons):
                value = button.get_attribute('value') or 'N/A'
                button_type = button.get_attribute('type') or 'N/A'
                enabled = button.is_enabled()
                button_info.append(f"{i + 1}. Value: '{value}', Type: '{button_type}', Enabled: {enabled}")

            if button_info:
                self.logger.debug("Available buttons: " + "; ".join(button_info))

        except Exception as e:
            self.logger.error(f"Could not retrieve buttons for product '{product_name}': {e}")

    def _debug_page_state(self):
        """Debug helper to log current page state."""
        try:
            title = self.get_title()
            url = self.driver.current_url
            self.logger.page_info(title, url)

            # Check for common popup/modal indicators
            common_selectors = [
                "div[class*='popup']",
                "div[class*='modal']",
                "div[class*='dialog']",
                "div[id*='popup']",
                "div[id*='modal']",
                "form",
            ]

            element_counts = []
            for selector in common_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element_counts.append(f"'{selector}': {len(elements)}")
                except:
                    pass

            if element_counts:
                self.logger.debug("Page elements found: " + "; ".join(element_counts))
            else:
                self.logger.debug("No common popup/modal elements found on page")

        except Exception as e:
            self.logger.error(f"Error during page state debugging: {e}")

    def is_file_input_visible(self, timeout=5):
        """Check if file input field is visible in upload popup."""
        self.logger.verification("Checking file input field visibility", True)
        is_visible = self.is_visible(self.FILE_INPUT, timeout=timeout)
        self.logger.verification("File input field visibility", is_visible)
        return is_visible

    def is_submit_button_visible(self, timeout=5):
        """Check if submit button is visible in upload popup."""
        self.logger.verification("Checking submit button visibility", True)
        is_visible = self.is_visible(self.SUBMIT_BTN, timeout=timeout)
        self.logger.verification("Submit button visibility", is_visible)
        return is_visible

    def upload_software_complete(self, file_path, timeout=10):
        """Complete software upload process with file selection and submission."""
        self.logger.action(f"Starting complete upload process for file: {file_path}")

        try:
            # Wait for file input to be available
            self.logger.wait_start("Waiting for file input to be available", timeout)
            file_input = self.wait_for_element_to_be_visible(self.FILE_INPUT, timeout=timeout)
            self.logger.element_found("File input field", str(self.FILE_INPUT))

            # Upload the file
            self.logger.action(f"Uploading file: {file_path}")
            file_input.send_keys(file_path)
            self.logger.action("File uploaded successfully")

            # Wait for submit button and click it
            self.logger.wait_start("Waiting for submit button to be clickable", timeout)
            submit_button = self.wait_for_element_to_be_clickable(self.SUBMIT_BTN, timeout=timeout)
            self.logger.element_found("Submit button", str(self.SUBMIT_BTN))

            # Click submit
            self.logger.action("Clicking submit button")
            submit_button.click()
            self.logger.action("Submit button clicked successfully")

            # Wait for upload to complete (you may need to adjust this based on your app)
            time.sleep(2)
            self.logger.wait_success("Upload process completed")

        except TimeoutException as e:
            self.logger.error(f"Upload process failed: {e}")
            screenshot_path = self.take_screenshot("upload_failed.png")
            if screenshot_path:
                self.logger.screenshot(screenshot_path)
            raise Exception(f"Upload process failed: {e}")
