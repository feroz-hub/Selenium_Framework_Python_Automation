import pytest
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.home_page import HomePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



@pytest.mark.parametrize("case", Config.get("tests.login"))
def test_login(driver, case):
    login = LoginPage(driver)
    login.login(case["username"], case["password"])

    if case["expected"] == "success":
        WebDriverWait(driver, 10).until(
            EC.title_contains("Olympus Medical Software Delivery")
        )
        home = HomePage(driver)
        home.sign_out()
        # ✅ wait for login page to reappear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signInName"))
        )
        assert driver.find_element(By.ID, "signInName").is_displayed()

    elif case["expected"] == "error":
        assert "incorrect" in login.get_error_message()

    elif case["expected"] == "invalid_format":
        validation_msg = login.get_email_validation_message()
        assert "@" in validation_msg
