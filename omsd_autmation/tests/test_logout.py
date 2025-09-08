from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.home_page import HomePage
from omsd_autmation.utils.data_loader import load_csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from omsd_autmation.utils.screenshot import take_screenshot
import csv
import pytest


@pytest.mark.parametrize("username,password,expected", load_csv("data/login_test_data.csv"))
def test_sign_out(driver, username, password, expected):
    login = LoginPage(driver)
    login.enter_username(username)
    login.enter_password(password)
    take_screenshot(driver, "before_click_next.png")
    login.click_next()
    take_screenshot(driver, "after_click_next.png")

    if expected == "success":
        WebDriverWait(driver, 10).until(
            EC.title_contains("Olympus Medical Software Delivery")
        )
        take_screenshot(driver, "after_login.png")
        home = HomePage(driver)
        take_screenshot(driver, "before_sign_out.png")
        home.sign_out()
        take_screenshot(driver, "after_sign_out.png")
        # Optional: Verify redirection to login page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signInName"))
        )
        assert driver.find_element(By.ID, "signInName").is_displayed()
        take_screenshot(driver, "login_page.png")
        assert "Sign up or sign in" in driver.title