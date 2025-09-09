import pytest

from omsd_autmation.pages.base_page import BasePage
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.software_page import SoftwarePage
from omsd_autmation.pages.upload_page import UploadPage
from omsd_autmation.utils.config_reader import Config


@pytest.mark.smoke
def test_upload_software(driver):
    # --- Step 1: Login ---
    login = LoginPage(driver)
    username = Config.get("environments.staging.users.software_uploader.username")
    password = Config.get("environments.staging.users.software_uploader.password")
    login.login(username, password)
    login.wait_for_title("Olympus Medical Software Delivery")

    # Accept cookies if popup appears
    base_page = BasePage(driver)
    base_page.accept_cookies()
    # --- Step 2: Navigate to product software list ---
    software = SoftwarePage(driver)
    software.open_software_list("ESG-410")

    # --- Step 3: Upload software ---
    upload_page = UploadPage(driver)

    import os

    # Build file path
    file_path = os.path.join(os.getcwd(), "omsd_autmation", "uploads", "ESG-410_v01.00.00.00-New")

    upload_page.perform_upload(file_path)


    # --- Step 4: Assert success ---
    # Example: check success message (replace with real locator if different)
    success_message = driver.find_element("xpath", "//*[contains(text(),'uploaded successfully')]")
    assert success_message.is_displayed(), "Upload failed or success message not found"
