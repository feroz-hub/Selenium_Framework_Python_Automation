# pages/login_page.py
from selenium.webdriver.common.by import By
from omsd_automation.pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "signInName")
    PASSWORD = (By.ID, "password")
    NEXT_BTN = (By.ID, "next")

    def __init__(self, driver):
        super().__init__(driver)  # <-- This initializes BasePage attributes

    def login(self, username, password):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.NEXT_BTN)
