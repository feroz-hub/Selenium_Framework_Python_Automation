import pytest
import time
from selenium.webdriver.common.by import By

from omsd_autmation.pages.base_page import BasePage
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.software_page import SoftwarePage
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging


class TestSoftwareUploadDiagnostic:
    """Diagnostic test suite for software upload functionality with enhanced logging."""

    @pytest.fixture(autouse=True)
    def setup_test(self, driver):
        """Setup test environment - login and accept cookies."""
        self.driver = driver
        self.base_page = BasePage(driver)
        self.login_page = LoginPage(driver)
        self.software_page = SoftwarePage(driver)

        # Setup logging
        self.test_logger = setup_test_logging("software_upload_diagnostic")

        # Perform login
        username = Config.get("environments.staging.users.software_uploader.username")
        password = Config.get("environments.staging.users.software_uploader.password")

        self.test_logger.action(f"Logging in with username: {username}")
        self.login_page.login(username, password)
        self.login_page.wait_for_title("Olympus Medical Software Delivery")
        self.test_logger.verification("Login successful", True)

        # Accept cookies if popup appears
        self.test_logger.action("Accepting cookies")
        self.base_page.accept_cookies()

        # Log current page info
        self.test_logger.page_info(self.driver.title, self.driver.current_url)

    @pytest.mark.smoke
    def test_diagnostic_software_list_opening(self):
        """Diagnostic test to understand why software list is not opening."""
        test_name = "diagnostic_software_list_opening"
        self.test_logger.test_start(test_name)

        product_name = "ESG-410"

        try:
            # Step 1: Take initial screenshot
            self.test_logger.step("Taking initial screenshot")
            screenshot_path = self.base_page.take_screenshot("01_initial_page_state.png")
            self.test_logger.screenshot(screenshot_path)

            # Step 2: Check if the product exists on the page
            self.test_logger.step(f"Checking if product '{product_name}' exists on page")
            try:
                product_locator = (By.XPATH, f"//h5[text()='{product_name}']")
                self.test_logger.wait_start(f"Looking for product header", 10)
                product_element = self.base_page.find(product_locator)
                self.test_logger.element_found(f"Product '{product_name}'", str(product_locator))
                self.test_logger.debug(f"Product element text: '{product_element.text}'")
            except Exception as e:
                self.test_logger.element_not_found(f"Product '{product_name}'", str(product_locator))
                self.test_logger.error(f"Product search failed: {e}")

                # Log available products
                self.test_logger.step("Discovering available products on page")
                self._log_available_products()

                screenshot_path = self.base_page.take_screenshot("02_product_not_found.png")
                self.test_logger.screenshot(screenshot_path)
                raise Exception(f"Product '{product_name}' not found on page")

            # Step 3: Check if the Software List button exists
            self.test_logger.step(f"Checking Software List button for '{product_name}'")
            try:
                software_list_btn_locator = (By.XPATH,
                                             f"//h5[text()='{product_name}']/following-sibling::input[@value='Software List']")
                self.test_logger.wait_start("Looking for Software List button", 10)
                software_list_btn = self.base_page.find(software_list_btn_locator)

                self.test_logger.element_found("Software List button", str(software_list_btn_locator))
                self.test_logger.debug(f"Button enabled: {software_list_btn.is_enabled()}")
                self.test_logger.debug(f"Button displayed: {software_list_btn.is_displayed()}")

            except Exception as e:
                self.test_logger.element_not_found("Software List button", str(software_list_btn_locator))
                self.test_logger.error(f"Software List button search failed: {e}")

                # Log available buttons for this product
                self.test_logger.step(f"Discovering available buttons for '{product_name}'")
                self._log_available_buttons_for_product(product_name)

                screenshot_path = self.base_page.take_screenshot("03_software_list_button_not_found.png")
                self.test_logger.screenshot(screenshot_path)
                raise Exception(f"Software List button not found for '{product_name}'")

            # Step 4: Click the software list button
            self.test_logger.step(f"Clicking Software List button for '{product_name}'")
            try:
                self.test_logger.action("Clicking Software List button")
                self.software_page.open_software_list(product_name)
                self.test_logger.verification("Software List button clicked", True)
            except Exception as e:
                self.test_logger.error(f"Failed to click Software List button: {e}")
                screenshot_path = self.base_page.take_screenshot("04_failed_to_click_software_list.png")
                self.test_logger.screenshot(screenshot_path)
                raise

            # Step 5: Wait and analyze page state after clicking
            self.test_logger.step("Analyzing page state after clicking Software List")
            self.test_logger.wait_start("Waiting for page transition", 3)
            time.sleep(3)  # Give page time to load

            screenshot_path = self.base_page.take_screenshot("05_after_clicking_software_list.png")
            self.test_logger.screenshot(screenshot_path)

            # Log current page info
            self.test_logger.page_info(self.driver.title, self.driver.current_url)

            # Step 6: Check for expected elements
            self.test_logger.step("Checking for expected popup elements")

            # Check for popup header
            popup_header_present = self.base_page.is_visible(self.software_page.UPLOAD_POPUP_HEADER, timeout=5)
            self.test_logger.verification("Upload popup header present", popup_header_present)

            if popup_header_present:
                try:
                    header_element = self.base_page.find(self.software_page.UPLOAD_POPUP_HEADER)
                    self.test_logger.debug(f"Popup header text: '{header_element.text}'")
                except Exception as e:
                    self.test_logger.error(f"Could not get header text: {e}")

            # Check for upload button
            upload_btn_present = self.base_page.is_visible(self.software_page.UPLOAD_SOFTWARE_BTN, timeout=5)
            self.test_logger.verification("Upload Software button present", upload_btn_present)

            # Check for cancel button
            cancel_btn_present = self.base_page.is_visible(self.software_page.CANCEL_BTN, timeout=5)
            self.test_logger.verification("Cancel button present", cancel_btn_present)

            # Step 7: Detailed page analysis
            self.test_logger.step("Performing detailed page analysis")
            self._analyze_page_elements()

            # Step 8: Final assertion
            self.test_logger.step("Final verification of software list opening")
            is_opened = self.software_page.is_software_list_opened()
            self.test_logger.verification("Software list opened successfully", is_opened)

            if not is_opened:
                screenshot_path = self.base_page.take_screenshot("06_final_failure_state.png")
                self.test_logger.screenshot(screenshot_path)
                self.test_logger.error("Software list did not open as expected")
                # Don't fail here for diagnostic purposes

            self.test_logger.test_end(test_name, is_opened)

        except Exception as e:
            self.test_logger.error(f"Diagnostic test failed: {e}")
            self.test_logger.test_end(test_name, False)
            raise

    @pytest.mark.smoke
    def test_simple_page_analysis(self):
        """Simple test to analyze page content and structure."""
        test_name = "simple_page_analysis"
        self.test_logger.test_start(test_name)

        product_name = "ESG-410"

        try:
            self.test_logger.step("Analyzing page content and structure")

            # Check page source for key content
            page_source = self.driver.page_source
            content_checks = [
                (product_name, f"Product '{product_name}'"),
                ("Software List", "Software List text"),
                ("Upload Software", "Upload Software text"),
                ("addHeader", "addHeader element"),
                ("btnCancel", "btnCancel element"),
            ]

            for content, description in content_checks:
                present = content in page_source
                self.test_logger.verification(f"Page contains {description}", present)

            # Try alternative locator strategies
            self.test_logger.step("Testing alternative locator strategies")
            try:
                # Case-insensitive search
                alt_locator = (By.XPATH,
                               f"//h5[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{product_name.lower()}')]")
                alt_element = self.base_page.find(alt_locator)
                self.test_logger.element_found(f"Product with case-insensitive search", str(alt_locator))
                self.test_logger.debug(f"Alternative locator found: {alt_element.text}")
            except Exception as e:
                self.test_logger.element_not_found("Product with case-insensitive search", str(alt_locator))
                self.test_logger.debug(f"Alternative locator failed: {e}")

            # Wait for potential dynamic content
            self.test_logger.step("Waiting for potential dynamic content loading")
            self.test_logger.wait_start("Dynamic content load", 5)
            time.sleep(5)

            # Re-check after waiting
            try:
                product_locator = (By.XPATH, f"//h5[text()='{product_name}']")
                product_element = self.base_page.find(product_locator)
                self.test_logger.verification(f"Product found after wait", True)
                self.test_logger.debug(f"Product text after wait: {product_element.text}")
            except Exception as e:
                self.test_logger.verification(f"Product found after wait", False)
                self.test_logger.debug(f"Product still not found after wait: {e}")

            self.test_logger.test_end(test_name, True)

        except Exception as e:
            self.test_logger.error(f"Page analysis failed: {e}")
            self.test_logger.test_end(test_name, False)
            raise

    def _log_available_products(self):
        """Helper method to log available products with enhanced logging."""
        try:
            products = self.driver.find_elements(By.XPATH, "//h5")
            self.test_logger.debug(f"Found {len(products)} product elements")

            if products:
                self.test_logger.debug("Available products:")
                for i, product in enumerate(products[:10]):  # Show first 10
                    self.test_logger.debug(f"   {i + 1}. '{product.text}'")
                if len(products) > 10:
                    self.test_logger.debug(f"   ... and {len(products) - 10} more products")
            else:
                self.test_logger.warning("No product elements (h5 tags) found on page")

        except Exception as e:
            self.test_logger.error(f"Could not retrieve available products: {e}")

    def _log_available_buttons_for_product(self, product_name: str):
        """Helper method to log available buttons for a product."""
        try:
            buttons_locator = (By.XPATH, f"//h5[text()='{product_name}']/following-sibling::input")
            buttons = self.driver.find_elements(*buttons_locator)

            self.test_logger.debug(f"Found {len(buttons)} button elements for '{product_name}'")

            if buttons:
                self.test_logger.debug(f"Available buttons for '{product_name}':")
                for i, button in enumerate(buttons):
                    value = button.get_attribute('value')
                    button_type = button.get_attribute('type')
                    enabled = button.is_enabled()
                    visible = button.is_displayed()
                    self.test_logger.debug(
                        f"   {i + 1}. Value: '{value}', Type: '{button_type}', Enabled: {enabled}, Visible: {visible}")
            else:
                self.test_logger.warning(f"No button elements found for product '{product_name}'")

        except Exception as e:
            self.test_logger.error(f"Could not retrieve buttons for product '{product_name}': {e}")

    def _analyze_page_elements(self):
        """Helper method to analyze various page elements."""
        try:
            # Check for common popup/modal indicators
            selectors_to_check = [
                ("div[class*='popup']", "popup divs"),
                ("div[class*='modal']", "modal divs"),
                ("div[class*='dialog']", "dialog divs"),
                ("div[id*='popup']", "popup IDs"),
                ("div[id*='modal']", "modal IDs"),
                ("form", "form elements"),
                ("input[type='button']", "button inputs"),
                ("input[type='submit']", "submit inputs"),
            ]

            for selector, description in selectors_to_check:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.test_logger.debug(f"Found {len(elements)} {description}")
                        # Log first few elements
                        for i, el in enumerate(elements[:3]):
                            try:
                                tag_info = f"{el.tag_name}"
                                if el.get_attribute('id'):
                                    tag_info += f" id='{el.get_attribute('id')}'"
                                if el.get_attribute('class'):
                                    tag_info += f" class='{el.get_attribute('class')}'"
                                if el.get_attribute('value'):
                                    tag_info += f" value='{el.get_attribute('value')}'"
                                self.test_logger.debug(f"   {i + 1}. {tag_info}")
                            except:
                                pass
                    else:
                        self.test_logger.debug(f"No {description} found")
                except Exception as e:
                    self.test_logger.debug(f"Error checking {description}: {e}")

        except Exception as e:
            self.test_logger.error(f"Error during page element analysis: {e}")