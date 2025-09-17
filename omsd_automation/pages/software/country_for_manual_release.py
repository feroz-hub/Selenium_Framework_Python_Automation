

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from omsd_automation.pages.base.base_page import BasePage


class CountryForManualReleasePage(BasePage):
    """Page Object for the 'Country For Manual Release' popup."""

    # --- LOCATORS ---
    COUNTRY_BUTTON = (By.CSS_SELECTOR, "button.normal-btn.btnIFUCountry")
    ALL_COUNTRIES_CHECKBOX = (By.ID, "bc8AllIFUCountry")
    PDF_FILE_INPUT = (By.CSS_SELECTOR, "input.ifuFileInput[data-role='3']")
    COUNTRY_DIALOG_OK_BUTTON = (By.ID, "countrySelectedOk")
    EDIT_CONFIRM_BUTTON = (By.ID, "btnEditConfirm")
    def __init__(self, driver: WebDriver, log):
        super().__init__(driver)
        self.log = log

    # --- ACTIONS ---
    def select_all_countries(self):
        """Select the 'All Countries' checkbox."""
        self.log.action("Selecting 'All Countries' checkbox for manual release.")
        self.click_scroll(self.ALL_COUNTRIES_CHECKBOX)
        self.click(self.ALL_COUNTRIES_CHECKBOX)
        self.log.action("Selected 'All Countries' checkbox for manual release.")

    def upload_pdf(self, file_path: str):
        """Upload a PDF file into the IFU input field."""
        file_path = str(file_path)  # Ensure it’s a string, not Path
        self.log.action(f"Uploading PDF file: {file_path}")
        file_input = self.find(self.PDF_FILE_INPUT)
        file_input.send_keys(file_path)

    def confirm_country_selection(self):
        """Click the country confirmation button."""
        self.log.action("Clicking the 'Confirm Country' button.")
        self.click(self.COUNTRY_BUTTON)

    def click_ok_button(self):
        """Click the OK button in the country selection dialog."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.element_to_be_clickable(self.COUNTRY_DIALOG_OK_BUTTON)).click()

    def click_confirm_changes(self):
        """Click the Confirm Changes button in the edit dialog."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.element_to_be_clickable(self.EDIT_CONFIRM_BUTTON)).click()

    # --- HIGH LEVEL FLOW ---
    def perform_manual_release(self, pdf_path: str):
        """
        Complete manual release setup:
        1. Select all countries
        2. Upload PDF
        3. Confirm
        """
        self.log.step("Starting manual release setup.")
        self.select_all_countries()
        self.click_ok_button()
        self.upload_pdf(pdf_path)
        self.confirm_country_selection()
        self.log.step("Manual release setup completed.")
