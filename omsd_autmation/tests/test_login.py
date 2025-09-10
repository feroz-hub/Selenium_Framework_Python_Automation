import pytest
from selenium.webdriver.common.by import By

from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging


@pytest.mark.parametrize("case", Config.get("tests.login"))
def test_login(driver, case, login_page, home_page, base_page):
    # Setup logger for this test
    test_logger = setup_test_logging("test_login")

    test_name = f"Login Test ({case['username']})"
    test_logger.test_start(test_name)

    try:
        # Step 1: Perform login
        test_logger.step(f"Attempting login with username: {case['username']}")
        login_page.login(case["username"], case["password"])

        if case["expected"] == "success":
            test_logger.verification("Login expected to succeed", True)

            base_page.accept_cookies()
            test_logger.action("Accepted cookies if present")

            base_page.wait_for_title("Olympus Medical Software Delivery", timeout=15)
            test_logger.wait_success("Page title contains 'Olympus Medical Software Delivery'")

            base_page.wait_for_seconds(2)
            base_page.take_screenshot("STS06_10")
            test_logger.screenshot("screenshots/STS06_10.png")

            test_logger.action("Signing out")
            home_page.sign_out()

            test_logger.wait_start("Waiting for login page to reappear", 10)
            base_page.wait_for_page_to_reappear((By.ID, "signInName"))
            test_logger.wait_success("Login page reappeared")

            assert driver.find_element(By.ID, "signInName").is_displayed()
            test_logger.verification("Login page is displayed after sign out", True)

        elif case["expected"] == "error":
            test_logger.verification("Login expected to fail (wrong credentials)", True)
            error_msg = login_page.get_error_message()
            test_logger.debug(f"Error message: {error_msg}")
            assert "incorrect" in error_msg
            test_logger.verification("Error message contains 'incorrect'", True)

        elif case["expected"] == "invalid_format":
            test_logger.verification("Login expected to fail (invalid email format)", True)
            validation_msg = login_page.get_email_validation_message()
            test_logger.debug(f"Validation message: {validation_msg}")
            assert "@" in validation_msg
            test_logger.verification("Validation message contains '@'", True)

        test_logger.test_end(test_name, success=True)

    except Exception as e:
        test_logger.error(f"Exception during test: {e}")
        base_page.take_screenshot("error_screenshot")
        test_logger.screenshot("screenshots/error_screenshot.png")
        test_logger.test_end(test_name, success=False)
        raise
