from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from omsd_automation.pages.base.base_page import BasePage


class SearchDevicePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    SERIAL_NUMBER = (By.ID, "txtSerialNumber")
    BTN_SEARCH = (By.ID, "searchButton")
    BTN_DOWNLOAD = (By.XPATH, "//button[contains(@onclick, \"clickDownload('ESG-410_v01.00.00.00-Hema'\")]")

    def search(self, serialNumber):
        self.type(self.SERIAL_NUMBER, serialNumber)
        self.click(self.BTN_SEARCH)

    def click_download_button_by_software(self, software_name):
        xpath = f"//button[contains(@onclick, \"clickDownload('{software_name}'\")]"
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        # Wait for any overlay to disappear
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "container")))
        except:
            pass
        # Scroll into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

        # Try clicking
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        except ElementClickInterceptedException:
            # Fallback to JS click
            self.driver.execute_script("arguments[0].click();", element)

