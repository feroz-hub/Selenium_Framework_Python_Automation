import pytest
import hashlib
from selenium.webdriver.common.by import By
from omsd_autmation.tests import test_config as C
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging


def calculate_checksum(file_path):
    """Helper: Return SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.mark.smoke
def test_upload_software(driver, base_page, login_page, software_page, upload_page, home_page):
    log = setup_test_logging("upload_software")
    log.test_start("test_upload_software")
    test_passed = False

    try:
        # --- Step 1: Login ---
        log.step("Step 1: Login to the application")
        username = Config.get(f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.username")
        password = Config.get(f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.password")

        login_page.login(username, password)
        login_page.wait_for_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT)
        base_page.accept_cookies()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-10")  # [SC004] Product Category

        # --- Step 2: Navigate to product software list ---
        log.step("Step 2: Navigate to product software list")
        software_page.open_software_list(C.DEFAULT_PRODUCT)
        base_page.wait_for_seconds(3)
        base_page.take_screenshot("ST06-11")  # [SC012] Package List

        # --- Step 3: Upload software ---
        log.step("Step 3: Upload new package")
        file_to_upload = C.TEST_FILE_NAME
        file_path = C.UPLOAD_DIR / file_to_upload

        upload_page.open_upload_popup()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-12")  # [D005-1] Add New Package

        upload_page.upload_file(str(file_path))
        upload_page.fill_upload_details()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-13")  # Filled upload form

        upload_page.submit_upload()
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-14")  # [D005-3_Add] Package Confirm

        # --- Step 4: Verify toast ---
        toast_text = upload_page.wait_for_toast(timeout=3)
        assert "The software has been added." in toast_text, f"Unexpected toast: {toast_text}"
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-15")  # Toast

        # --- Step 5: Verify uploaded file name ---
        file_name = upload_page.wait_for_uploaded_file_name(timeout=5)
        assert file_name == file_to_upload, f"File name mismatch: got '{file_name}', expected '{file_to_upload}'"
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-16")  # Uploaded file in list

        # --- Step 6: Download uploaded file ---
        log.step("Step 6: Download uploaded file")
        download_button = driver.find_element(
            By.XPATH,
            f"//button[contains(@onclick, \"clickDownload('{file_to_upload}')\")]"
        )
        download_button.click()
        base_page.wait_for_seconds(3)  # Wait for download to start
        base_page.take_screenshot("ST06-17")  # [SC033] Download Progress

        # --- Step 7: Verify file integrity ---
        downloaded_file_path = C.DOWNLOAD_DIR / file_to_upload
        assert downloaded_file_path.exists(), "Downloaded file not found"

        upload_checksum = calculate_checksum(file_path)
        download_checksum = calculate_checksum(downloaded_file_path)
        assert upload_checksum == download_checksum, "Uploaded and downloaded files differ"

        # --- Step 8: (Optional) Verify settings persist ---
        # If you have a UI screen to reopen the package and check settings,
        # implement it in UploadPage and call here.

        # --- Step 9: Sign out ---
        log.step("Step 9: Sign out")
        home_page.sign_out()
        login_page.wait_for_element((By.ID, "signInName"))

        assert base_page.is_visible((By.ID, "signInName")), "Not redirected to login page"
        assert "Sign up or sign in" in login_page.get_title(), "Sign-in page title mismatch"
        base_page.wait_for_seconds(2)
        base_page.take_screenshot("ST06-19")  # [SC001-2] Sign In

        test_passed = True

    except Exception as e:
        log.error(f"Test failed: {e}")
        base_page.take_screenshot("upload_failure")
        raise

    finally:
        log.test_end("test_upload_software", success=test_passed)
