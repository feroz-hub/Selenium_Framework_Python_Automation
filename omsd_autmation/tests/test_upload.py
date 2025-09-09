import pytest

# Import constants from the test configuration file using alias 'C' for brevity
from omsd_autmation.tests import test_config as C
from omsd_autmation.pages.base_page import BasePage
from omsd_autmation.pages.login_page import LoginPage
from omsd_autmation.pages.software_page import SoftwarePage
from omsd_autmation.pages.upload_page import UploadPage
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging


# The pytest marker is typically a string literal, but it's based on your config constant.
@pytest.mark.smoke
def test_upload_software(driver):
    # --- Logger Setup ---
    log = setup_test_logging("upload_software")
    log.test_start("test_upload_software")

    test_passed = False

    try:
        # --- Step 1: Login ---
        log.step("Step 1: Login to the application")
        login = LoginPage(driver)

        # Get user credentials from Config, using the role constant
        username_path = f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.username"
        password_path = f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.password"
        username = Config.get(username_path)
        password = Config.get(password_path)

        log.action(f"Attempting to log in with user role: {C.SOFTWARE_UPLOADER_ROLE}")
        login.login(username, password)

        # Wait for title using the application title constant
        login.wait_for_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT)
        log.page_info(driver.title, driver.current_url)
        log.verification("User successfully logged in and dashboard page is visible", True)

        # Accept cookies
        base_page = BasePage(driver)
        log.action("Checking for and accepting cookies popup")
        base_page.accept_cookies()

        # --- Step 2: Navigate to product software list ---
        log.step("Step 2: Navigate to product software list")
        software = SoftwarePage(driver)

        # Use the default product constant
        product_name = C.DEFAULT_PRODUCT

        log.action(f"Opening software list for product: '{product_name}'")
        software.open_software_list(product_name)
        log.verification(f"Successfully navigated to the software list for '{product_name}'", True)
        log.page_info(driver.title, driver.current_url)

        # --- Step 3: Upload software ---
        log.step("Step 3: Perform software upload")
        upload_page = UploadPage(driver)

        # Build file path using Pathlib objects from the config file for robustness
        file_to_upload = C.TEST_FILE_NAME
        file_path = C.UPLOAD_DIR / file_to_upload
        log.debug(f"Constructed file path for upload: {file_path}")

        log.action(f"Uploading file: '{file_path.name}'")
        upload_page.perform_upload(str(file_path))  # Convert Path object to string for send_keys

        # --- Step 4: Verify upload success ---
        log.step("Step 4: Verify upload was successful")

        # Verify toast message
        toast_text = upload_page.wait_for_toast(timeout=C.LONG_TIMEOUT)
        expected_toast = "The software has been added."
        toast_verification_result = expected_toast in toast_text
        log.verification(f"Toast message contains '{expected_toast}'", toast_verification_result)
        assert toast_verification_result, f"Toast message was '{toast_text}' but expected '{expected_toast}'"

        # Verify uploaded file name is visible in the list
        file_name = upload_page.wait_for_uploaded_file_name(timeout=C.DEFAULT_TIMEOUT)
        file_name_verification_result = file_name == file_to_upload
        log.verification(f"Uploaded file name in the list is '{file_to_upload}'", file_name_verification_result)
        assert file_name_verification_result, f"File name in list was '{file_name}' but expected '{file_to_upload}'"

        test_passed = True

    except Exception as e:
        log.error(f"An exception occurred during the test: {e}")
        # Optionally, capture a screenshot on failure using the configured directory
        # base_page = BasePage(driver)
        # base_page.save_screenshot(C.SCREENSHOTS_DIR, "upload_failure")
        raise

    finally:
        log.test_end("test_upload_software", success=test_passed)