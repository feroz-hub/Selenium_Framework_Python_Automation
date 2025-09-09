import pytest
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.home_page import HomePage
from omsd_autmation.utils.data_loader import load_csv
from omsd_autmation.utils.screenshot import take_screenshot
from selenium.webdriver.common.by import By


@pytest.mark.parametrize("username,password,expected", load_csv("data/login_test_data.csv"))
def test_sign_out(driver, username, password, expected):
    login = LoginPage(driver)

    # --- Login Flow ---
    login.login(username, password)   # ✅ one method call
    take_screenshot(driver, "after_login.png")

    if expected == "success":
        login.wait_for_title("Olympus Medical Software Delivery")

        # --- Logout Flow ---
        home = HomePage(driver)
        take_screenshot(driver, "before_sign_out.png")
        home.sign_out()
        take_screenshot(driver, "after_sign_out.png")

        # --- Verify redirected to login page ---
        login.wait_for_element((By.ID, "signInName"))
        assert login.is_displayed((By.ID, "signInName"))
        take_screenshot(driver, "login_page.png")
        assert "Sign up or sign in" in login.get_title()
