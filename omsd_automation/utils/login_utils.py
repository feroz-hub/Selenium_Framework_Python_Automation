from omsd_automation.utils.config_reader import Config
from omsd_automation.tests import test_config as C


class LoginUtils:
    @staticmethod
    def login_as_software_uploader(login_page, base_page, log, driver):
        """
        Logs into the application using the SOFTWARE_UPLOADER_ROLE credentials.

        Parameters:
        - login_page: Page object for login operations
        - base_page: Page object for base operations like accepting cookies
        - log: Logger object for logging steps and actions
        - driver: WebDriver instance
        """
        log.step("Step 1: Login to the application")

        username_path = f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.username"
        password_path = f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.password"
        username = Config.get(username_path)
        password = Config.get(password_path)

        log.action(f"Attempting to log in with user role: {C.SOFTWARE_UPLOADER_ROLE}")
        login_page.login(username, password)

        login_page.wait_for_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT)

        log.page_info(driver.title, driver.current_url)
        log.verification("User successfully logged in and dashboard page is visible", True)
        log.action("Checking for and accepting cookies popup")

        base_page.accept_cookies()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-10")
