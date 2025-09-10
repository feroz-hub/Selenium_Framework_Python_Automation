import pytest
from selenium.webdriver.common.by import By
from omsd_autmation.tests import test_config as C
from omsd_autmation.utils.config_reader import Config
from omsd_autmation.utils.logger import setup_test_logging


@pytest.mark.smoke
def test_delete_software(driver, base_page, login_page, software_page, home_page):
    log = setup_test_logging("delete_software")
    log.test_start("test_delete_software")
    test_passed = False

    try:
        # Step 1: Login
        log.step("Step 1: Login to the application")
        username = Config.get(f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.username")
        password = Config.get(f"environments.staging.users.{C.SOFTWARE_UPLOADER_ROLE}.password")

        login_page.login(username, password)
        login_page.wait_for_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT)
        log.page_info(driver.title, driver.current_url)
        log.verification("User successfully logged in", True)
        base_page.accept_cookies()
        base_page.take_screenshot("ST07-01_Login")

        # Step 2: Navigate to Product Software List
        log.step("Step 2: Navigate to the product software list")
        software_page.open_software_list(C.OMSD_ESG_410)
        base_page.wait_for_seconds(2)
        log.page_info(driver.title, driver.current_url)
        base_page.take_screenshot("ST07-02_SoftwareList")

        # Step 3: Select Uploaded Software
        log.step("Step 3: Select the uploaded software to delete")
        file_to_delete = C.TEST_FILE_NAME
        log.action(f"Looking for uploaded software file: {file_to_delete}")

        file_link_locator = (
            By.XPATH,
            f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_delete}']"
        )

        file_element = base_page.wait_for_element_to_be_clickable(file_link_locator, timeout=10)
        file_element.click()
        base_page.take_screenshot("ST07-03_SelectedSoftware")
        log.verification(f"Selected software '{file_to_delete}'", True)

        # Step 4: Delete the Software
        log.step("Step 4: Delete the software")
        delete_btn = base_page.wait_for_element_to_be_clickable((By.ID, "btnDelete"), timeout=5)
        delete_btn.click()
        log.action("Clicked 'Delete this software'")

        delete_ok_btn = base_page.wait_for_element_to_be_clickable((By.ID, "btnDeleteOK"), timeout=5)
        delete_ok_btn.click()
        log.action("Confirmed delete action")

        # Step 5: Verify Deletion via Toast Message
        toast_locator = (By.CSS_SELECTOR, "#toast-container .toast")
        toast_text = base_page.wait_for_element(toast_locator, timeout=20).text
        log.verification("Toast message confirms deletion", "deleted" in toast_text.lower())
        #base_page.take_screenshot("ST07-04_Deleted")

        # Step 6: Verify Software is Removed from List
        log.step("Step 6: Verify the software no longer appears in the list")
        driver.refresh()
        base_page.wait_for_seconds(1)
        try:
            software_page.open_software_list(C.OMSD_ESG_410)
        except Exception:
            log.warning(f"Product '{C.OMSD_ESG_410}' not found after refresh.")

        remaining_files = driver.find_elements(
            By.XPATH,
            f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_delete}']"
        )
        is_deleted = all(not file.is_displayed() for file in remaining_files)

        log.verification(f"Software '{file_to_delete}' deleted successfully", is_deleted)
        assert is_deleted, f"File '{file_to_delete}' still found in software list"

        # Step 7: Sign Out
        log.step("Step 7: Sign out")
        home_page.sign_out()
        base_page.wait_for_seconds(2)
        login_page.wait_for_element((By.ID, "signInName"))
        is_on_login_page = base_page.is_visible((By.ID, "signInName"))
        log.verification("User is redirected to login page after sign out", is_on_login_page)
        assert is_on_login_page

        test_passed = True

    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise

    finally:
        log.test_end("test_delete_software", success=test_passed)
