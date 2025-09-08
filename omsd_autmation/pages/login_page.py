# pages/login_page.py
from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME = (By.ID, "signInName")
    PASSWORD = (By.ID, "password")
    NEXT_BTN = (By.ID, "next")
    CANCEL_BTN = (By.ID, "cancel")
    ERROR_MSG = (By.XPATH, "//p[contains(text(),'incorrect')]")

    def enter_username(self, username):
        self.type(self.USERNAME, username)

    def enter_password(self, password):
        self.type(self.PASSWORD, password)

    def click_next(self):
        self.click(self.NEXT_BTN)

    def click_cancel(self):
        self.click(self.CANCEL_BTN)

    def get_error_message(self):
        return self.get_text(self.ERROR_MSG)

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_next()
