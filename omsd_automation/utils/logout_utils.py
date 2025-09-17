from selenium.webdriver.common.by import By
class LogoutUtils:
    @staticmethod
    def sign_out_user(home_page, base_page, login_page, log, driver):
        """
        Signs out the user and verifies redirection to the login page.

        Parameters:
        - home_page: Page object for home/dashboard operations
        - base_page: Page object for base operations like waiting and screenshots
        - login_page: Page object for login operations
        - log: Logger object for logging steps and actions
        - driver: WebDriver instance
        """
        log.step("Step 7: Sign out")
        home_page.sign_out()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("STS06-18")
        login_page.wait_for_element((By.ID, "signInName"))
        is_on_login_page = base_page.is_visible((By.ID, "signInName"))
        log.verification("User is redirected to login page after sign out", is_on_login_page)
        assert is_on_login_page