from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from omsd_autmation.pages.base_page import BasePage
# Import the class-level logger utility
from omsd_autmation.utils.logger import get_class_logger

import os
class UploadPage(BasePage):
    """Page object for Upload Software popup."""

    # --- LOCATORS ---
    UPLOAD_SOFTWARE_BTN = (By.XPATH, "//input[@value='Upload Software']")
    FILE_INPUT = (By.ID, "packageFileInput")
    PACKAGE_TYPE_RADIO = (
        By.XPATH,
        "//input[@name='groupPackageType' and following-sibling::span[contains(text(), 'Device Update Executers')]]"
    )
    ON_TOGGLE = (By.XPATH, "//input[@name='groupUseConfirmationCodeType' and following-sibling::span[text()='On']]")
    BY_COUNTRIES_TAB = (
        By.XPATH,
        "//input[@name='groupPublishType' and following-sibling::span[text()='by countries']]"
    )
    MATERIAL_ID_CHECKBOX = (
        By.XPATH, "//label[contains(., 'All material IDs below')]//span"
    )
    REGION_CHECKBOX = (
        By.XPATH, "//div[@id='regions']//label[contains(., 'OMSI')]/span[@class='checkbox-icon']"
    )
    DISPLAY_RADIO = (By.XPATH, "//input[@name='groupIsEnabled' and @value='false']")
    CONFIRM_BTN = (By.ID, "btnAddConfirm")
    UPLOAD_CONFIRM_BTN = (By.ID, "btnAddSave")
    TOAST_CONTAINER = (By.CSS_SELECTOR, "#toast-container .toast")
    UPLOADED_FILE_NAME = (By.CSS_SELECTOR, "#toast-container .toast font[size='3']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        # Initialize a logger specific to this page object
        self.log = get_class_logger(self.__class__.__name__)

    def open_upload_popup(self):
        """Clicks the button to open the upload software modal."""
        self.log.action("Clicking 'Upload Software' button to open the popup.")
        self.click(self.UPLOAD_SOFTWARE_BTN)

    def upload_file(self, file_path: str):
        """Sends the file path to the hidden file input element."""
        self.log.action(f"Uploading file from path: {file_path}")
        self.find(self.FILE_INPUT).send_keys(file_path)

    def fill_upload_details(self):
        """Fills out all the required fields and checkboxes in the upload form."""
        self.log.action("Filling out the software upload details form.")

        self.log.action("Selecting 'Device Update Executers' package type.")
        self.click(self.PACKAGE_TYPE_RADIO)

        self.log.action("Setting Confirmation Code to 'On'.")
        self.click(self.ON_TOGGLE)

        self.log.action("Selecting 'by countries' publish type.")
        self.click(self.BY_COUNTRIES_TAB)

        self.log.action("Waiting for Material ID checkbox to be visible.")
        self.wait_for_element_to_be_visible(self.MATERIAL_ID_CHECKBOX, timeout=20)
        self.log.action("Scrolling to and clicking 'All material IDs below' checkbox.")
        self.scroll_into_view(self.MATERIAL_ID_CHECKBOX)
        self.click(self.MATERIAL_ID_CHECKBOX)

        self.log.action("Waiting for Region checkbox to be clickable.")
        self.wait_for_element_to_be_clickable(self.REGION_CHECKBOX, timeout=15)
        self.log.action("Scrolling to and clicking 'OMSI' region checkbox.")
        self.scroll_into_view(self.REGION_CHECKBOX)
        self.click(self.REGION_CHECKBOX)

        self.log.action("Setting display status radio button.")
        self.click(self.DISPLAY_RADIO)

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

    def wait_for_toast(self, timeout=20):
        """Waits for a toast message and returns its full text."""
        self.log.wait_start("Waiting for a toast message to appear.", timeout)
        try:
            toast_element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.TOAST_CONTAINER)
            )
            message = toast_element.text
            self.log.wait_success(f"Toast message appeared with text: '{message}'")
            return message
        except TimeoutException:
            self.log.wait_timeout("Toast message did not appear.", timeout)
            raise  # Re-raise exception to fail the test

    def submit_upload(self):
        """Clicks the two confirmation buttons to finalize the upload."""
        self.log.action("Clicking 'Confirm' button on the initial upload form.")
        self.click(self.CONFIRM_BTN)
        self.log.wait_start("Waiting for the final 'Upload' confirmation button to be clickable.", 10)
        self.wait_for_element_to_be_clickable(self.UPLOAD_CONFIRM_BTN)
        self.log.action("Clicking the final 'Upload' confirmation button.")
        self.click(self.UPLOAD_CONFIRM_BTN)

    def perform_upload(self, file_path: str):
        """High-level flow that orchestrates the entire upload process."""
        self.log.step(f"Starting the complete software upload process for file: {os.path.basename(file_path)}")
        self.open_upload_popup()
        self.upload_file(file_path)
        self.fill_upload_details()
        self.submit_upload()