from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from omsd_autmation.pages.base_page import BasePage


class UploadPage(BasePage):
    """Page object for Upload Software popup."""

    # Locators
    UPLOAD_SOFTWARE_BTN = (By.XPATH, "//input[@value='Upload Software']")
    FILE_INPUT = (By.ID, "packageFileInput")
    PACKAGE_TYPE_RADIO = (By.XPATH, "//div[@id='radioPackageType']//*[contains(text(),'Device Update Executers')]")
    ON_TOGGLE = (By.XPATH, "//*[text()='On']")
    BY_COUNTRIES_TAB = (By.XPATH, "//*[text()='by countries']")
    MATERIAL_ID_CHECKBOX = (By.XPATH, "//label[contains(text(),'All material IDs below')]/span[1]")
    REGION_CHECKBOX = (By.XPATH, "//div[@id='regions']//label[contains(text(),'OMSI')]/span[1]")
    DISPLAY_RADIO = (By.XPATH, "//div[@id='radioIsEnabled']//*[contains(text(),'Do not display')]")
    CONFIRM_BTN = (By.XPATH, "//button[text()='Confirm']")
    UPLOAD_CONFIRM_BTN = (By.XPATH, "//button[text()='Upload']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def open_upload_popup(self):
        self.click(self.UPLOAD_SOFTWARE_BTN)

    def upload_file(self, file_path: str):
        self.find(self.FILE_INPUT).send_keys(file_path)

    def fill_upload_details(self):
        self.click(self.PACKAGE_TYPE_RADIO)
        self.click(self.ON_TOGGLE)
        self.click(self.BY_COUNTRIES_TAB)
        self.click(self.MATERIAL_ID_CHECKBOX)
        self.click(self.REGION_CHECKBOX)
        self.click(self.DISPLAY_RADIO)

    def submit_upload(self):
        self.click(self.CONFIRM_BTN)
        self.click(self.UPLOAD_CONFIRM_BTN)

    def perform_upload(self, file_path: str):
        """High-level flow to perform upload."""
        self.open_upload_popup()
        self.upload_file(file_path)
        self.fill_upload_details()
        self.submit_upload()
