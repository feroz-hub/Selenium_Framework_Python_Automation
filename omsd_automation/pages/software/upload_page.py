from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

from omsd_automation.pages.software.country_selection_page import CountrySelectionPage
from omsd_automation.pages.base.base_page import BasePage
# Import the class-level logger utility
import time
import os


class UploadPage(BasePage):
    """Page object for Upload Software popup."""

    # --- LOCATORS ---

    # Edit Software Release Settings Popup locators
    UPLOAD_SOFTWARE_BTN = (By.XPATH, "//input[@value='Upload Software']")
    FILE_INPUT = (By.ID, "packageFileInput")
    PACKAGE_TYPE_RADIO = (By.XPATH,
                          "//input[@name='groupPackageType' and following-sibling::span[contains(text(), 'Device Update Executers')]]")
    ON_TOGGLE = (By.XPATH, "//input[@name='groupUseConfirmationCodeType' and following-sibling::span[text()='On']]")
    BY_COUNTRIES_TAB = (
    By.XPATH, "//input[@name='groupPublishType' and following-sibling::span[text()='by countries']]")
    MATERIAL_ID_CHECKBOX = (By.XPATH, "//label[contains(., 'All material IDs below')]//span")
    CHECK_ALL_REGIONS = (By.XPATH, "//label[contains(., 'All BCs below')]//span")
    REGION_CHECKBOX = (By.XPATH, "//div[@id='regions']//label[contains(., 'OMSI')]/span[@class='checkbox-icon']")
    DO_NOT_DISPLAY_RADIO = (By.XPATH, "//input[@name='groupIsEnabled' and @value='false']")
    DISPLAY_RADIO = (By.XPATH, "//input[@name='groupIsEnabled' and @value='true']")
    BTN_ADD_CONFIRM = (By.ID, "btnAddConfirm")
    BTN_EDIT_CONFIRM = (By.ID, "btnEditConfirm")
    BTN_EDIT_SAVE = (By.ID, "btnEditSave")
    BTN_UPLOAD_CONFIRM = (By.ID, "btnAddSave")
    TOAST_CONTAINER = (By.CSS_SELECTOR, "#toast-container .toast")
    UPLOADED_FILE_NAME = (By.CSS_SELECTOR, "#toast-container .toast font[size='3']")
    CHK_ALL_COUNTRIES = (By.CSS_SELECTOR, "label.bcAllLabel .checkbox-icon")
    ALL_BCS_CHECKBOX = (
        By.CSS_SELECTOR,
        "input#regionAll + span.checkbox-icon"
    )
    COUNTRY_BUTTON = (By.CLASS_NAME, "normal-btn btnIFUCountry")
    # "All countries" checkbox

    all_countries_checkbox = (By.ID, "bc8All")

    # Updated locators based on your HTML structure
    ot_main_checkbox = (By.ID, "bc8")
    countries_section = (By.CLASS_NAME, "countries")
    region_toggle_arrow = (By.CSS_SELECTOR, ".material-icons.small.switching")
    # Select Country for Manual Release Popup locator
    ALL_COUNTRIES_CHECKBOX = (By.ID, "bc8AllIFUCountry")
    OK_BUTTON = (By.ID, "countrySelectedOk")


    def __init__(self, driver: WebDriver, logger):
        super().__init__(driver)
        # # Initialize a logger specific to this page object
        self.log = logger
        self.country_selection=CountrySelectionPage(driver,logger)

    def open_upload_popup(self):
        """Clicks the button to open the upload software modal."""
        self.log.action("Clicking 'Upload Software' button to open the popup.")
        self.click(self.UPLOAD_SOFTWARE_BTN)

    def upload_file(self, file_path: str):
        """Sends the file path to the hidden file input element."""
        self.log.action(f"Uploading file from path: {file_path}")
        self.find(self.FILE_INPUT).send_keys(file_path)

    def fill_upload_details(self):
        page=CountrySelectionPage(self.driver,self.log)
        """Fills out all the required fields and checkboxes in the upload form."""
        self.log.action("Filling out the software upload details form.")

        self.log.action("Selecting 'Device Update Executers' package type.")
        self.click(self.PACKAGE_TYPE_RADIO)

        self.log.action("Setting Confirmation Code to 'On'.")
        self.click(self.ON_TOGGLE)

        self.log.action("Selecting 'by countries' publish type.")
        self.click(self.BY_COUNTRIES_TAB)

        self.log.action("Waiting for Material ID checkbox to be visible.")
        #page.select_all_bcs()
        self.wait_for_element_to_be_visible(self.MATERIAL_ID_CHECKBOX, timeout=20)
        self.log.action("Scrolling to and clicking 'All material IDs below' checkbox.")
        self.scroll_into_view(self.MATERIAL_ID_CHECKBOX)
        self.click(self.MATERIAL_ID_CHECKBOX)

        self.log.action("Waiting for Region checkbox to be clickable.")
        self.wait_for_element_to_be_visible(self.ALL_BCS_CHECKBOX, timeout=15)
        self.log.action("Scrolling to and clicking 'OMSI' region checkbox.")
        self.scroll_into_view(self.ALL_BCS_CHECKBOX)
        self.click(self.ALL_BCS_CHECKBOX)

        # self.log.action("Waiting for Region checkbox to be clickable.")
        # # self.wait_for_element_to_be_visible(self.CHECK_ALL_REGIONS, timeout=15)
        # self.log.action("Scrolling to and clicking 'OMSI' region checkbox.")
        # self.scroll_into_view(self.CHECK_ALL_REGIONS)
        # self.click(self.CHECK_ALL_REGIONS)
        # page.select_all_countries()

        self.log.action("Setting display status radio button.")
        self.click(self.DO_NOT_DISPLAY_RADIO)

    def wait_for_uploaded_file_name(self, timeout=20):
        """Waits for the toast message and extracts the uploaded file name from it."""
        self.log.wait_start("Waiting for the uploaded file name to appear in the toast.", timeout)
        try:
            file_element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.UPLOADED_FILE_NAME)
            )
            file_name = file_element.text
            self.log.wait_success(f"File name found in toast: '{file_name}'")
            return file_name
        except TimeoutException:
            self.log.wait_timeout("File name did not appear in the toast.", timeout)
            raise  # Re-raise exception to fail the test
    #
    # def update_bc_setting(self, timeout=10):
    #     self.log.action("Setting display status radio button.")
    #     self.click(self.DISPLAY_RADIO)
    #     self.log.action("Clicking 'Confirm' button on the initial upload form.")
    #     self.click(self.BTN_EDIT_CONFIRM)
    #     self.log.wait_start("Waiting for the final 'Save' confirmation button to be clickable.", timeout)
    #     self.wait_for_element_to_be_clickable(self.BTN_EDIT_SAVE)
    #     self.log.action("Clicking the final 'Update' confirmation button.")
    #     self.click(self.BTN_EDIT_SAVE)
    def update_bc_setting(self, enable: bool = True, timeout=10):
        value = "true" if enable else "false"
        radio_locator = (By.XPATH, f"//input[@name='groupIsEnabled' and @value='{value}']")

        self.log.action(f"Selecting Public BC = {enable}")
        self.click(radio_locator)

        self.log.action("Clicking 'Confirm' button on the initial upload form.")
        self.click(self.BTN_EDIT_CONFIRM)

        self.log.wait_start("Waiting for the final 'Save' confirmation button to be clickable.", timeout)
        self.wait_for_element_to_be_clickable(self.BTN_EDIT_SAVE)

        self.log.action("Clicking the final 'Update' confirmation button.")
        self.click(self.BTN_EDIT_SAVE)

    # def update_bc_setting(self, timeout=20):
    #     """Update BC setting by selecting 'Display' and saving changes."""
    #     self.log.action("Ensuring 'Display' radio button is visible and clickable.")
    #
    #     # Wait for the radio to be visible
    #     display_radio = WebDriverWait(self.driver, timeout).until(
    #         EC.visibility_of_element_located(self.DISPLAY_RADIO)
    #     )
    #
    #     # Scroll into view
    #     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", display_radio)
    #
    #     # Wait until clickable
    #     WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.DISPLAY_RADIO)
    #     )
    #
    #     # Click safely
    #     display_radio.click()
    #     self.log.action("'Display' radio button selected.")
    #
    #     # Continue with confirm and save flow
    #     self.log.action("Clicking 'Confirm' button on the initial upload form.")
    #     confirm_btn = WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.BTN_EDIT_CONFIRM)
    #     )
    #     confirm_btn.click()
    #
    #     self.log.wait_start("Waiting for the final 'Save' confirmation button to be clickable.", timeout)
    #     save_btn = WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.BTN_EDIT_SAVE)
    #     )
    #     save_btn.click()
    #     self.log.action("Clicked the final 'Update' confirmation button.")

    def update_country_setting(self, timeout=10):
        self.wait_for_page_ready()
        self.ensure_countries_section_visible()
        self.log.action("Clicking 'All BCs below' checkbox.")

        self.click_scroll(self.all_countries_checkbox)
        self.log.action("Clicking 'Confirm' button on the initial upload form.")
        self.click(self.BTN_EDIT_CONFIRM)
        self.log.wait_start("Waiting for the final 'Save' confirmation button to be clickable.", timeout)
        self.wait_for_element_to_be_clickable(self.BTN_EDIT_SAVE)
        self.log.action("Clicking the final 'Update' confirmation button.")
        self.click(self.BTN_EDIT_SAVE)

    # def update_country_setting(self, timeout=10):
    #     self.log.action("Clicking 'All BCs below' checkbox.")
    #     checkbox = WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.CHK_ALL_COUNTRIES)
    #     )
    #     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
    #     self.driver.execute_script("arguments[0].click();", checkbox)  # JS click fallback
    #
    #     self.log.action("Clicking 'Confirm' button on the initial upload form.")
    #     confirm_btn = WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.BTN_EDIT_CONFIRM)
    #     )
    #     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
    #     self.driver.execute_script("arguments[0].click();", confirm_btn)
    #
    #     self.log.wait_start("Waiting for the final 'Save' confirmation button to be clickable.", timeout)
    #     save_btn = WebDriverWait(self.driver, timeout).until(
    #         EC.element_to_be_clickable(self.BTN_EDIT_SAVE)
    #     )
    #     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
    #     self.driver.execute_script("arguments[0].click();", save_btn)

    def wait_for_toast(self, timeout=10, pre_wait=3, post_wait=2, screenshot_prefix="toast"):
        """
        Wait for toast message with optional pre/post waits and take screenshots.
        Args:
            timeout (int): Max time to wait for toast
            pre_wait (int): Seconds to wait before toast appears
            post_wait (int): Seconds to wait after toast appears
            screenshot_prefix (str): prefix for screenshot file
        Returns:
            str: Toast text
        """
        # Wait before toast appears
        # print(f"⏳ Waiting {pre_wait}s before toast appears...")
        time.sleep(pre_wait)
        # self.take_screenshot(f"{screenshot_prefix}_before.png")
        # Wait for toast
        # print("⏳ Waiting for toast message...")
        toast_element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.TOAST_CONTAINER)
        )
        # self.take_screenshot(f"{screenshot_prefix}_appeared.png")
        message = toast_element.text
        # print("📢 Toast message:", message)
        # Wait after toast appears
        # print(f"⏳ Waiting {post_wait}s after toast...")
        time.sleep(post_wait)
        # self.take_screenshot(f"{screenshot_prefix}_after.png")
        return message

    def ensure_countries_section_visible(self):
        """Ensure the countries section is visible before interacting with elements"""
        try:
            # Check if a countries section is hidden
            countries_section = self.driver.find_element(*self.countries_section)
            if not countries_section.is_displayed():
                # Try to click the toggle arrow to expand
                toggle_arrow = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.region_toggle_arrow)
                )
                toggle_arrow.click()
                time.sleep(1)

                # Wait for a countries section to become visible
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of(countries_section)
                )
                print("Expanded countries section")
        except Exception as e:
            print(f"Could not expand countries section: {e}")
            # Continue anyway as the element might be visible through other means
    def wait_for_page_ready(self):
        """Wait for the page to be fully loaded"""
        try:
            # Wait for jQuery to be loaded and ready (if your app uses jQuery)
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.execute_script("return typeof jQuery !== 'undefined' && jQuery.active == 0")
            )
        except:
            # If jQuery is not available, wait for the document ready state
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

    def click_with_retry(self, locator, element_name, max_attempts=3):
        """Click an element with a retry mechanism"""
        for attempt in range(max_attempts):
            try:
                element = self.wait_for_element_clickable(locator)

                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)

                # Try regular click first
                element.click()
                print(f"Successfully clicked {element_name}")
                return

            except ElementNotInteractableException:
                if attempt < max_attempts - 1:
                    print(f"Attempt {attempt + 1}: Element not interactable, trying JavaScript click...")
                    try:
                        element = self.driver.find_element(*locator)
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"Successfully clicked {element_name} with JavaScript")
                        return
                    except:
                        time.sleep(1)
                        continue
                else:
                    raise
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(1)
                else:
                    raise
    def submit_upload(self):
        """Clicks the two confirmation buttons to finalize the upload."""
        self.log.action("Clicking 'Confirm' button on the initial upload form.")
        self.click(self.BTN_ADD_CONFIRM)
        self.log.wait_start("Waiting for the final 'Upload' confirmation button to be clickable.", 10)
        self.wait_for_element_to_be_clickable(self.BTN_UPLOAD_CONFIRM)
        self.log.action("Clicking the final 'Upload' confirmation button.")
        self.click(self.BTN_UPLOAD_CONFIRM)

    def handle_timeout_error(self, error):
        """Handle timeout exceptions with debugging info"""
        print(f"Timeout Error: {error}")
        self.take_screenshot("timeout_error")

        # Debug: Check what elements are actually present
        self.debug_available_elements()

        raise Exception(f"Timeout waiting for country setting elements: {error}")

    def handle_interaction_error(self, error):
        """Handle element interaction errors"""
        print(f"Interaction Error: {error}")
        self.take_screenshot("interaction_error")

        # Try alternative approach
        try:
            print("Trying alternative JavaScript approach...")
            element = self.driver.find_element(*self.all_countries_checkbox)
            self.driver.execute_script("arguments[0].click();", element)
            print("Successfully clicked using JavaScript")
        except Exception as js_error:
            raise Exception(f"Could not interact with country setting element: {error}")

    def handle_general_error(self, error):
        """Handle general errors"""
        print(f"General Error: {error}")
        self.take_screenshot("general_error")
        raise Exception(f"Error updating country setting: {error}")

    def debug_available_elements(self):
        """Debug method to see what elements are available on the page"""
        try:
            # Check for the main container
            containers = self.driver.find_elements(By.CLASS_NAME, "region")
            print(f"Found {len(containers)} region containers")

            # Check for checkboxes
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            print(f"Found {len(checkboxes)} checkboxes")

            for i, checkbox in enumerate(checkboxes[:10]):  # Limit to first 10
                try:
                    checkbox_id = checkbox.get_attribute("id")
                    is_displayed = checkbox.is_displayed()
                    is_enabled = checkbox.is_enabled()
                    print(f"Checkbox {i}: ID={checkbox_id}, Displayed={is_displayed}, Enabled={is_enabled}")
                except:
                    pass

        except Exception as e:
            print(f"Debug failed: {e}")
    def perform_upload(self, file_path: str):
        """High-level flow that orchestrates the entire upload process."""
        self.log.step(f"Starting the complete software upload process for file: {os.path.basename(file_path)}")
        self.open_upload_popup()
        self.upload_file(file_path)
        self.fill_upload_details()
        self.submit_upload()

    # def revert_countries_and_save(self):
    #     # Uncheck the same selection and save again
    #     self.log.step("Revert country selection and save")
    #     self.country_selection.deselect_all_countries()
    #
    #     self.safe_click(self.BTN_EDIT_CONFIRM)
    #     self.wait_for_element_to_be_clickable(self.BTN_EDIT_SAVE, timeout=10)
    #     self.click(self.BTN_EDIT_SAVE)
    def wait_for_uploaded_file_name(self, expected_name, timeout=30, poll_frequency=0.5):
        """
        Waits for the uploaded file name to appear anywhere sensible (toast, table, list).
        Returns the text found. Raises TimeoutException with diagnostics if not found.
        """
        end = time.time() + timeout
        while time.time() < end:
            # 1) Wait for any overlay/spinner to disappear before checking
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner, .overlay"))
                )
            except Exception:
                pass

            # 2) Try a set of XPaths (table cells, anchors, toast, spans)
            xpaths = [
                f"//table//td[normalize-space(text()) = '{expected_name}']",
                f"//table//td[contains(normalize-space(.), '{expected_name}')]",
                f"//tr//a[contains(normalize-space(.), '{expected_name}')]",
                f"//div[contains(@class,'package-list')]//span[contains(normalize-space(.), '{expected_name}')]",
                f"//div[contains(@class,'toast') and contains(., '{expected_name}')]",
                # fallback: any element containing the text
                f"//*[contains(normalize-space(.), '{expected_name}')]"
            ]

            for xp in xpaths:
                try:
                    el = self.driver.find_element(By.XPATH, xp)
                    if el and el.is_displayed():
                        return el.text.strip()
                except Exception:
                    continue

            time.sleep(poll_frequency)

        # Diagnostics on failure
        ts = int(time.time())
        with open(f"upload_wait_diagnostics_{ts}.html", "w", encoding="utf-8") as fh:
            fh.write(self.driver.page_source)
        self.driver.save_screenshot(f"upload_wait_diagnostics_{ts}.png")
        raise TimeoutException(f"Timeout waiting for uploaded file name '{expected_name}'. Diagnostics saved.")
