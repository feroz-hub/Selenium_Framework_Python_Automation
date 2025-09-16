from omsd_automation.pages.base import base_page

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from omsd_automation.pages.base.base_page import BasePage


class SoftwareCheckPage(BasePage):
    def __init__(self, driver:WebDriver):
       super().__init__(driver)
       self.wait = None

    def select_software(self, name):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{name}']"))).click()

    def toggle_public_country_setting(self, enable=True):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:nth-child(11) .bcsTitle .bcTitle .bcAllLabel .checkbox-icon"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Confirm Changes']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))).click()

    def reopen_software(self, name):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//tr[contains(@aria-label, '{name}')]//a"))).click()
