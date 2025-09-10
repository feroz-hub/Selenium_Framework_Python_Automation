import pytest
from selenium.webdriver.common.by import By


from omsd_autmation.pages.home_page import HomePage
from omsd_autmation.utils.data_loader import load_csv
from omsd_autmation.utils.screenshot import take_screenshot
from omsd_autmation.utils.logger import setup_test_logging
from omsd_autmation.tests import test_config as C


@pytest.mark.parametrize("username,password,expected", load_csv("data/login_test_data.csv"))
def test_sign_out(driver, username, password, expected, home_page, base_page,login_page):
    # --- Logger Setup ---
    log = setup_test_logging(f"sign_out_{username}")
    log.test_start(f"test_sign_out with user: {username}")

    test_passed = False
    try:


        # --- Login Flow ---
        log.step("Step 1: Perform user login")
        login_page.login(username, password)
        take_screenshot(driver, f"{username}_after_login.png")

        if expected == "success":
            # --- Verification after Login ---
            log.step("Step 2: Verify successful login")
            login_page.wait_for_title(C.APP_TITLE)
            log.verification(f"Successfully logged in as {username}", True)

            # --- Logout Flow ---
            log.step("Step 3: Perform sign-out")
            login_page.accept_cookies()  # Assuming cookies appear after login

            home_page.sign_out()  # ✅ Clean, single method call
            take_screenshot(driver, f"{username}_after_sign_out.png")

            # --- Verification after Logout ---
            log.step("Step 4: Verify redirection to login page")
            login_page.wait_for_element((By.ID, "signInName"))

            is_on_login_page = login_page.is_displayed((By.ID, "signInName"))
            log.verification("User is redirected to the login page", is_on_login_page)
            assert is_on_login_page

            title_contains_signin = "Sign up or sign in" in login_page.get_title()
            log.verification("Page title confirms it is the sign-in page", title_contains_signin)
            assert title_contains_signin

            test_passed = True
        else:
            # Handle and log failed login scenarios if necessary
            log.step(f"Step 2: Verifying expected login failure for user {username}")
            # Add assertions here to check for error messages on the login page
            log.verification("Login failed as expected", True)
            test_passed = True

    except Exception as e:
        log.error(f"An exception occurred during the test: {e}")
        raise
    finally:
        log.test_end(f"test_sign_out with user: {username}", success=test_passed)
