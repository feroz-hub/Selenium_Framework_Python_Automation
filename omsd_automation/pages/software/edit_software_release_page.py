from selenium.webdriver.common.by import By

from omsd_automation.pages.base.base_page import BasePage


class EditSoftwareReleasePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
    ALL_COUNTRIES_CHECKBOX = (By.ID, "bc8All")
    BTN_ADD_CONFIRM = (By.ID, "btnAddConfirm")
    BTN_EDIT_CONFIRM = (By.ID, "btnEditConfirm")
    BTN_EDIT_SAVE = (By.ID, "btnEditSave")
    BTN_UPLOAD_CONFIRM = (By.ID, "btnAddSave")
    ADD_BUTTON = (By.ID, "labelIfuFileAdd")
    PDF_FILE_INPUT = (By.CSS_SELECTOR, "input.ifuFileInput[data-role='3']")

    def click_add_button(self):
        self.click(self.ADD_BUTTON)

    def upload_pdf(self, file_path: str):
        """Upload a PDF file into the IFU input field."""
        file_path = str(file_path)  # Ensure it’s a string, not Path
        file_input = self.find(self.PDF_FILE_INPUT)
        file_input.send_keys(file_path)