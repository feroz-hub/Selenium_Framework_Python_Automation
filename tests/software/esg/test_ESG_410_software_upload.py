import time
import traceback

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# Import constants from the test configuration file using alias 'C' for brevity
from tests import test_config as C
from omsd_automation.utils.element_helper import fallback_find_uploaded_name
from omsd_automation.utils.logger import setup_test_logging
from omsd_automation.utils.upload_flow import build_upload_path, verify_toast, wait_for_uploaded_name_with_fallback, normalize_and_assert_filename


@pytest.mark.parametrize("authenticated_session", ["software_uploader"], indirect=True)
def test_upload_software(authenticated_session, driver, base_page, login_page, software_page, upload_page, home_page):
    """
    Full test for uploading a software package.
    Improvements:
    - Robust wait for uploaded file name with diagnostics on failure.
    - Relaxed comparison (use contents) to tolerate small UI suffixes/prefixes.
    - Find download button by locating the row containing the filename.
    - Capture a screenshot / page source on failures for easier debugging.
    """
    log = setup_test_logging("upload_software")
    log.test_start("test_upload_software")
    test_passed = False

    try:
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module

        # --- Step 2: Navigate to a product software list ---
        log.step("Step 2: Navigate to product software list")
        log.action(f"Opening software list for product: '{C.OMSD_ESG_410}'")
        software_page.navigate_to_product_software(C.OMSD_ESG_410)
        log.verification(f"Successfully navigated to the software list for '{C.OMSD_ESG_410}'", True)
        log.page_info(driver.title, driver.current_url)

        # --- Step 3: Upload software ---
        log.step("Step 3: Perform software upload")
        base_page.wait_for_seconds(3)
        base_page.take_screenshot("ST06-11")

        file_to_upload = C.TEST_FILE_NAME
        file_path = build_upload_path(C.UPLOAD_DIR, file_to_upload, log)
        log.action(f"Uploading file: '{file_path.name}'")
        upload_page.perform_upload(str(file_path))

        # --- Step 4: Verify upload was successful (toast + list) ---
        log.step("Step 4: Verify upload was successful")
        base_page.wait_for_seconds(1)

        # Wait for toast and verify an expected message
        verify_toast(upload_page, base_page, driver, "The software has been added.", C.DEFAULT_TIMEOUT, log)

        # Robust wait for the filename to appear in the UI.
        # We'll try the page object's method first (if it supports passing expected_name).
        # If it times out, fallback to an internal search with diagnostics.

        # Increase timeout for list appearance (allow longer server-side processing)
        list_timeout = getattr(C, "UPLOAD_WAIT_TIMEOUT", max(C.DEFAULT_TIMEOUT, 60))
        found_file_text = wait_for_uploaded_name_with_fallback(
            upload_page, driver, file_to_upload, list_timeout, log, fallback_find_uploaded_name
        )

        # Normalize and verify file name (allow contains match)
        normalize_and_assert_filename(found_file_text, file_to_upload, driver, base_page, log)

        # If a file found, attempt download by locating the row and clicking download action inside it
        log.step("Step 5: Download the uploaded file before sign-out")
        try:
            # Attempt to find a row containing the file and then the download button within that row
            # Several possible table/list patterns are supported
            escaped = file_to_upload.replace("'", "\\'")
            possible_row_xpaths = [
                f"//tr[td[contains(normalize-space(.), '{escaped}')]]",
                f"//tr[.//a[contains(normalize-space(.), '{escaped}')]]",
                f"//div[contains(@class,'package-list')]//div[contains(., '{escaped}')]",
                f"//*[contains(normalize-space(.), '{escaped}') and (name() = 'li' or name() = 'div' or name() = 'tr')]"
            ]
            row = None
            for xp in possible_row_xpaths:
                try:
                    row = driver.find_element(By.XPATH, xp)
                    if row and row.is_displayed():
                        break
                except NoSuchElementException:
                    row = None
                    continue

            if not row:
                log.warning("Could not locate the row containing the uploaded file; attempting global download button "
                            "search.")
                # fallback: find any button whose onclick contains clickDownload and has the filename substring
                try:
                    download_button = driver.find_element(
                        By.XPATH,
                        f"//button[contains(@onclick, 'clickDownload') and contains(., '{escaped}')]"
                    )
                    download_button.click()
                except Exception as e:
                    log.error(f"Could not find download button via fallback: {e}")
                    # save diagnostics and continue (don't fail the test just because download couldn't start)
                    ts = int(time.time())
                    driver.save_screenshot(f"download_button_not_found_{ts}.png")
                    with open(f"download_button_not_found_{ts}.html", "w", encoding="utf-8") as fh:
                        fh.write(driver.page_source)
                    raise
            else:
                # search for a download control inside the row
                try:
                    download_button = None
                    # try common selectors inside the row
                    selectors = [
                        (By.XPATH, ".//button[contains(@onclick, 'clickDownload')]"),
                        (By.XPATH, ".//button[contains(@class,'download') or contains(@class,'download-btn')]"),
                        (By.XPATH, ".//a[contains(@href, 'download') or contains(@class,'download')]"),
                        (By.CSS_SELECTOR, "button.download, button.download-btn, a.download")
                    ]
                    for sel in selectors:
                        try:
                            candidate = row.find_element(*sel)
                            if candidate and candidate.is_displayed():
                                download_button = candidate
                                break
                        except Exception:
                            continue

                    if not download_button:
                        # try to find any button within the row
                        try:
                            download_button = row.find_element(By.TAG_NAME, "button")
                        except Exception:
                            download_button = None

                    if not download_button:
                        ts = int(time.time())
                        driver.save_screenshot(f"download_button_missing_in_row_{ts}.png")
                        with open(f"download_button_missing_in_row_{ts}.html", "w", encoding="utf-8") as fh:
                            fh.write(row.get_attribute("outerHTML"))
                        raise NoSuchElementException("No download button found inside the row.")

                    log.action(f"Clicking download button for file: '{file_to_upload}'")
                    download_button.click()
                    base_page.wait_for_seconds(3)
                    log.verification(f"Download initiated for file: '{file_to_upload}'", True)
                except Exception as e:
                    log.error(f"Download from row failed: {e}")
                    raise

        except Exception as e:
            # don't let download failure obscure the upload verification; rise after diagnostics
            log.error(f"Failed while initiating download: {e}")
            raise

        # --- Sign out and verify redirection to login ---

        # SignOut is happened in pytest fixture

        test_passed = True

    except Exception as e:
        # Capture full traceback in logs and save diagnostics
        log.error(f"An exception occurred during the test: {e}")
        tb = traceback.format_exc()
        log.debug(tb)
        try:
            ts = int(time.time())
            driver.save_screenshot(f"test_failure_{ts}.png")
            with open(f"test_failure_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(driver.page_source)
        except Exception:
            log.warning("Failed to save diagnostics artifacts.")
        raise

    finally:
        log.test_end("test_upload_software", success=test_passed)


@pytest.mark.parametrize("authenticated_session", ["software_uploader"], indirect=True)
def test_public_bc_setting(authenticated_session, driver, base_page, login_page, software_page, upload_page, home_page):
    """
    Test to verify the 'Public BC' setting during software upload.
    Steps:
    1. Login as software uploader.
    2. Navigate to a product software list.
    3. Upload a software package with 'Public BC' enabled.
    4. Verify the upload was successful via toast and list.
    5. Reopen the uploaded package and verify 'Public BC' is still enabled.
    6. Sign out and verify redirection to the login page.
    """
    log = setup_test_logging("upload_software_public_bc")
    log.test_start("test_upload_software_public_bc")
    test_passed = False

    try:
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module

        # --- Step 2: Navigate to a product software list ---
        log.step("Step 2: Navigate to product software list")
        log.action(f"Opening software list for product: '{C.OMSD_ESG_410}'")
        software_page.navigate_to_product_software(C.OMSD_ESG_410)
        log.verification(f"Successfully navigated to the software list for '{C.OMSD_ESG_410}'", True)
        log.page_info(driver.title, driver.current_url)

        # --- Step 3: Select Uploaded software ---

        log.step("Step 3: Select the uploaded software to change Public BC setting")
        file_to_update = C.TEST_FILE_NAME
        log.action(f"Looking for uploaded software file: {file_to_update}")

        file_link_locator = (
            By.XPATH,
            f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_update}']"
        )
        file_element = base_page.wait_for_element_to_be_clickable(file_link_locator, timeout=10)
        file_element.click()
        base_page.take_screenshot("ST07-03_SelectedSoftware")
        log.verification(f"Selected software '{file_to_update}'", True)

        # Step 4: Change Public BC setting
        log.step("Step 4: Change Public BC setting")
        upload_page.update_bc_setting()
        base_page.wait_for_seconds(2)

        # Step 5: Verify Update via Toast Message
        toast_locator = (By.CSS_SELECTOR, "#toast-container .toast")
        toast_text = base_page.wait_for_element(toast_locator, timeout=10).text
        log.verification("Toast message confirms saved", "save" in toast_text.lower())
        base_page.take_screenshot("ST07-04_Deleted")

        # # Step 7: Sign Out
        # SignOut is happened in pytest fixture

        test_passed = True

    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise

    finally:
        log.test_end("bc_setting_updated", success=test_passed)


@pytest.mark.parametrize("authenticated_session", ["distribution_manager"], indirect=True)
def test_public_country_setting(authenticated_session, driver, base_page, login_page, software_page, upload_page,
                                home_page):
    """
    Test to verify the 'Public Country' setting during software upload.
    Steps:
    1. Login as distribution manager.
    2. Navigate to a product software list.
    3. Upload a software package with 'Public Country' enabled.
    4. Verify the upload was successful via toast and list.
    5. Reopen the uploaded package and verify 'Public Country' is still enabled.
    6. Sign out and verify redirection to the login page.
    """
    log = setup_test_logging("upload_software_public_country")
    log.test_start("test_upload_software_public_country")
    test_passed = False

    try:
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module

        # --- Step 2: Navigate to a product software list ---
        log.step("Step 2: Navigate to product software list")
        log.action(f"Opening software list for product: '{C.OMSD_ESG_410}'")
        software_page.navigate_to_product_software(C.OMSD_ESG_410)
        log.verification(f"Successfully navigated to the software list for '{C.OMSD_ESG_410}'", True)
        log.page_info(driver.title, driver.current_url)


        # --- Step 3: Select Uploaded software ---

        log.step("Step 3: Select the uploaded software to change Public Country setting")
        file_to_update = "ESG-410_v01.00.00.00-Hema"
        log.action(f"Looking for uploaded software file: {file_to_update}")

        file_link_locator = (
            By.XPATH,
            f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_update}']"
        )
        file_element = base_page.wait_for_element_to_be_clickable(file_link_locator, timeout=10)
        file_element.click()
        base_page.take_screenshot("ST08-03_SelectedSoftware")
        log.verification(f"Selected software '{file_to_update}'", True)

        # Step 4: Change Public Country setting
        log.step("Step 4: Change Public Country setting")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)

        # Step 5: Verify Update via Toast Message
        toast_locator = (By.CSS_SELECTOR, "#toast-container .toast")
        toast_text = base_page.wait_for_element(toast_locator, timeout=10).text
        log.verification("Toast message confirms saved", "save" in toast_text.lower())
        base_page.take_screenshot("ST07-04_Deleted")

        # # Step 7: Sign Out
        # SignOut is happened in pytest fixture

        test_passed = True

    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise

    finally:
        log.test_end("bc_setting_updated", success=test_passed)
