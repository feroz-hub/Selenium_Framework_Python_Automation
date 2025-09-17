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
