from omsd_automation.pages.base.base_page import BasePage
from omsd_automation.pages.login_page import LoginPage
from omsd_automation.utils.config_reader import Config
from tests import test_config as C


class LoginUtils:
    @staticmethod
    def login_as_role(login_page, base_page, log, driver, role: str):
        """Login to the application using credentials for a specified user role.

        Parameters:
        - login_page: Page object for login operations
        - base_page: Page object for base operations like accepting cookies
        - log: Logger object for logging steps and actions
        - driver: WebDriver instance
        """
        log.step("Step 1: Login to the application")
        creds = Config.get_user(role)
        username = creds.get("username")
        password = creds.get("password")

        log.action(f"Attempting to log in with user role: {role}")
        login_page.login(username, password)

        login_page.wait_for_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT)

        log.page_info(driver.title, driver.current_url)
        log.verification("User successfully logged in and dashboard page is visible", True)
        log.action("Checking for and accepting cookies popup")

        base_page.accept_cookies()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("STS06-10")

    @staticmethod
    def reset_to_login_page(login_page: LoginPage, base_page: BasePage, driver, log, timeout: int = 20):
        """
        Reset back to the login page and wait for the username input to appear.
        """
        log.info("🔄 Resetting to login page before new login attempt")
        driver.get("https://softwaredelivery-stg3.olympusmedical.com")
        base_page.wait_for_element_to_be_visible(login_page.USERNAME, timeout=timeout)
        log.info("✅ Successfully reset to login page")
