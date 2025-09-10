from selenium.webdriver.common.by import By
from omsd_automation.pages.base_page import BasePage
from omsd_automation.pages.login_page import LoginPage


class HomePage(BasePage):
    """Page Object for the Home (Dashboard) Page."""
    # Locators
    USER_PROFILE = (By.ID, "sysUserDisplayName")
    SIGN_OUT_LINK = (By.XPATH, "//span[text()='Sign Out']/parent::a")

    def __init__(self, driver):
        super().__init__(driver)

    # Actions
    def open_user_menu(self):
        """Click on the user profile menu."""
        self.click(self.USER_PROFILE)

    def sign_out(self):
        """Sign out of the application and return LoginPage."""
        self.open_user_menu()
        self.click(self.SIGN_OUT_LINK)

        return LoginPage(self.driver)
