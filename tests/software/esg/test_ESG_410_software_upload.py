import time
import traceback

import pytest
from selenium.webdriver.common.by import By

from omsd_automation.utils.element_helper import fallback_find_uploaded_name
from omsd_automation.utils.logger import setup_test_logging
from omsd_automation.utils.login_utils import LoginUtils
from omsd_automation.utils.logout_utils import LogoutUtils
# Import constants from the test configuration file using alias 'C' for brevity
from tests import test_config as C
from tests.conftest import country_page


@pytest.mark.parametrize("authenticated_session", ["software_uploader"], indirect=True)
def test_upload_software(authenticated_session, upload_flow, base_page):
    log = setup_test_logging("upload_software")
    file_to_upload = C.TEST_FILE_NAME
    test_passed = False
    """
        Test: Software uploader uploads ESG package successfully.
        Steps:
        1. Navigate to an ESG product software list.
        2. Upload a package.
        3. Verify toast and file presence.
        4. Verify the file can be downloaded.
    """
    try:
        log.test_start("test_upload_software")
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module

        # --- Step 2: Navigate to a product software list ---
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "STS06-11")

        # --- Step 3: Upload software ---
        log.step("Step 3: Perform software upload")
        upload_flow.perform_upload_file(C.UPLOAD_DIR, file_to_upload)

        # --- Step 4: Verify upload was successful (toast + list) ---
        log.step("Step 4: Verify upload was successful")
        # Wait for toast and verify an expected message
        upload_flow.verify_toast("The software has been added.", C.DEFAULT_TIMEOUT)

        # Increase timeout for list appearance (allow longer server-side processing)
        list_timeout = getattr(C, "UPLOAD_WAIT_TIMEOUT", max(C.DEFAULT_TIMEOUT, 60))
        found_file_text = upload_flow.wait_for_uploaded_name_with_fallback(file_to_upload, list_timeout,fallback_find_uploaded_name)
        # --- Step 5: Download an uploaded file---
        log.step("Step 5: Download an uploaded file")
        # Normalize and verify file name (allow contains match)
        upload_flow.normalize_and_assert_filename(found_file_text, file_to_upload)
        upload_flow.download_uploaded_file(file_to_upload)
        base_page.take_screenshot("STS06-17")

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
            base_page.save_screenshot(f"test_failure_{ts}.png")
            with open(f"test_failure_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(base_page.page_source)
        except Exception:
            log.warning("Failed to save diagnostics artifacts.")
        raise

    finally:
        log.test_end("test_upload_software", success=test_passed)


@pytest.mark.parametrize("authenticated_session", ["software_uploader"], indirect=True)
def test_public_bc_setting(authenticated_session, upload_flow, upload_page, base_page):
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

    file_to_update = C.TEST_FILE_NAME
    test_passed = False

    try:
        log.test_start("test_upload_software_public_bc")
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module
        # --- Step 2: Navigate to a product software list ---
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        # --- Step 3: Select Uploaded software ---
        log.step("Step 3: Select the uploaded software to change Public BC setting")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        # Step 4: Change Public BC setting
        log.step("Step 4: Change Public BC setting")
        upload_page.update_bc_setting(enable=False)
        # Step 5: Verify Update via Toast Message (common helper)
        upload_flow.verify_toast("The software settings have been saved.")
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


@pytest.mark.parametrize("authenticated_session", ["end_user"], indirect=True)
def test_public_country_setting(authenticated_session, upload_flow, base_page, login_page, software_page, upload_page,
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
    file_to_update = "ESG-410_v01.00.00.00-Hema"
    try:
        # --- Step 1: Login ---
        # authenticated_session is a pytest fixture that logs in once per module

        # --- Step 2: Navigate to a product software list ---
        log.step("Step 2: Navigate to product software list")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
        # --- Step 3: Select Uploaded software ---
        log.step("Step 3: Select the uploaded software to change Public Country setting")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        log.action(f"Looking for uploaded software file: {file_to_update}")
        # Step 4: Change Public Country setting
        log.step("Step 4: Change Public Country setting")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)
        # Step 5: Verify Update via Toast Message (common helper)
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-04_Deleted")
        base_page.wait_for_toast_to_disappear()
        #base_page.refresh_page()
        #software_page.click_back_to_software_list()

        upload_flow.navigate_to_product_revert(C.OMSD_ESG_410, "bc_setting_updated")

        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        # # Step 7: Sign Out
        # SignOut is happened in pytest fixture
        test_passed = True
    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise
    finally:
        log.test_end("bc_setting_updated", success=test_passed)

@pytest.mark.parametrize("roles", [("software_uploader", "distribution_manager")])
def test_public_country_settings_multiuser(roles, driver, upload_flow, base_page, login_page, software_page,upload_page, home_page):
    """
    End-to-end test for updating the Countries of publication setting for a software package
    for two different roles in sequence. Flow based on the issue description:

    1) Login as end_user
        - Open Software List for the target product
        - Open Available Version (target software)
        - Check Countries of publication (any country; here we toggle "All Countries") and Confirm Change
        - Click Save and verify toast "Software settings have been saved"
        - Revert changes before sign out: open package, uncheck Countries, Confirm, Save
        - Sign out and verify login page appears

    2) Login as distribution_manager
        - Repeat: navigate, open software, check Countries, Confirm, Save
        - Verify toast, and sign out
    """

    def open_target_package():
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "Login")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")

    def select_countries_and_save():
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)

    def revert_countries_and_save():
        upload_page.click_scroll(upload_page.CHK_ALL_COUNTRIES)
        base_page.wait_for_seconds(1)
        upload_page.click(upload_page.BTN_EDIT_CONFIRM)
        base_page.wait_for_element_to_be_clickable(upload_page.BTN_EDIT_SAVE, timeout=10)
        upload_page.click(upload_page.BTN_EDIT_SAVE)

    log = setup_test_logging("public_country_setting_multiuser")
    log.test_start("test_public_country_setting_multiuser")
    file_to_update = C.TEST_FILE_NAME
    test_passed = False
    try:
        # 1) Login as end_user
        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
        base_page.wait_for_element_to_be_visible((By.XPATH, "//h5"), timeout=20)
        open_target_package()
        select_countries_and_save()

        # Note: revert before sign-out for other test cases safety
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        select_countries_and_save()

        # Sign out
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)

        # 2) Login as distribution_manager
        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[1])
        base_page.wait_for_element_to_be_visible((By.XPATH, "//h5"), timeout=15)
        open_target_package()
        select_countries_and_save()

        # Sign out again
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)

        # # 1) Login as end_user
        # LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
        #
        # upload_flow.navigate_to_product(C.OMSD_ESG_410, "Login")
        # upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        # upload_page.update_country_setting()
        # base_page.wait_for_seconds(2)
        # upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        # upload_page.revert_countries_and_save()
        # upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        # # Sign out
        # LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        # # 2) Login as distribution_manager
        # LoginUtils.login_as_role(login_page, base_page, log, driver, roles[1])
        # upload_flow.navigate_to_product(C.OMSD_ESG_410, "Login")
        # upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        # upload_page.update_country_setting()
        # upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        #
        # # Sign out again
        # LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        #
        # test_passed = True



    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise
    finally:
        log.test_end("bc_setting_updated", success=test_passed)


@pytest.mark.parametrize("roles", [("software_uploader", "distribution_manager")])
def test_public_country_setting_multi_login(roles,base_page, driver,login_page, software_page, upload_page, upload_flow, home_page):
    """
    Test to verify the 'Public Country' setting with multiple user roles.
    Steps:
    1. Login as software_uploader and update country setting, then revert and sign out.
    2. Login as distribution_manager and change country setting, then sign out.
    3. Verify all operations are successful via toast messages.
    """
    log = setup_test_logging("upload_software_public_country_multi_login")
    log.test_start("test_upload_software_public_country_multi_login")
    test_passed = False
    file_to_update = "ESG-410_v01.00.00.00-Hema"

    try:
        # --- Phase 1: Software Uploader Operations ---
        log.step("Phase 1: Software Uploader Operations")

        # Step 1: Login as software_uploader
        log.step("Step 1: Login as software_uploader")
        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
        base_page.wait_for_seconds(2)

        # Step 2: Navigate to a product software list
        log.step("Step 2: Navigate to product software list (software_uploader)")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_software_uploader")

        # Step 3: Select uploaded software
        log.step("Step 3: Select uploaded software (software_uploader)")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03-SU")
        log.action(f"Software uploader looking for file: {file_to_update}")

        # Step 4: Update country setting
        log.step("Step 4: Update country setting (software_uploader)")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)

        # Step 5: Verify update via toast
        log.step("Step 5: Verify update toast (software_uploader)")
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-04_SoftwareUploader_Updated")

        # Step 6: Revert the country setting
        log.step("Step 6: Revert country setting (software_uploader)")
        upload_page.update_country_setting()  # Revert the changes
        base_page.wait_for_seconds(2)

        # Step 7: Verify revert via toast
        log.step("Step 7: Verify revert toast (software_uploader)")
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-05_SoftwareUploader_Reverted")

        # Step 8: Sign out software_uploader
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        base_page.take_screenshot("ST07-06_SoftwareUploader_SignedOut")

        # --- Phase 2: Distribution Manager Operations ---
        log.step("Phase 2: Distribution Manager Operations")

        # Step 9: Login as distribution_manager
        log.step("Step 9: Login as distribution_manager")
        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[1])
        base_page.wait_for_seconds(2)

        # Step 10: Navigate to a product software list
        log.step("Step 10: Navigate to product software list (distribution_manager)")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_distribution_manager")

        # Step 11: Select uploaded software
        log.step("Step 11: Select uploaded software (distribution_manager)")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03-DM")
        log.action(f"Distribution manager looking for file: {file_to_update}")

        # Step 12: Change country setting
        log.step("Step 12: Change country setting (distribution_manager)")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)

        # Step 13: Verify change via toast
        log.step("Step 13: Verify change toast (distribution_manager)")
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-07_DistributionManager_Updated")

        # Step 14: Sign out distribution_manager
        log.step("Step 14: Sign out distribution_manager")
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        base_page.take_screenshot("ST07-08_DistributionManager_SignedOut")

        test_passed = True

    except Exception as e:
        log.error(f"Exception occurred during multi-login test: {e}")
        base_page.take_screenshot("ST07_MultiLogin_Error")
        raise
    finally:
        log.test_end("bc_setting_multi_login_updated", success=test_passed)
@pytest.mark.parametrize("roles", [("end_user", "distribution_manager")])
def test_public_country_setting_multi_user(roles,driver, upload_flow, base_page, login_page, software_page, upload_page,
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
    # 1) Login as end_user
    log = setup_test_logging("upload_software_public_country")


    log.test_start("test_upload_software_public_country")
    test_passed = False
    file_to_update = "ESG-410_v01.00.00.00-Hema"
    try:
        # --- Step 1: Login ---
        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])

        # --- Step 2: Navigate to a product software list ---
        log.step("Step 2: Navigate to product software list")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
        # --- Step 3: Select Uploaded software ---
        log.step("Step 3: Select the uploaded software to change Public Country setting")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        log.action(f"Looking for uploaded software file: {file_to_update}")
        # Step 4: Change Public Country setting
        log.step("Step 4: Change Public Country setting")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)
        # Step 5: Verify Update via Toast Message (common helper)
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-04_Deleted")
        base_page.wait_for_toast_to_disappear()
        #base_page.refresh_page()
        #software_page.click_back_to_software_list()

        upload_flow.navigate_to_product_revert(C.OMSD_ESG_410, "bc_setting_updated")

        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        # # Step 7: Sign Out
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)

        LoginUtils.login_as_role(login_page, base_page, log, driver, roles[1])
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
        # --- Step 3: Select Uploaded software ---
        log.step("Step 3: Select the uploaded software to change Public Country setting")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        log.action(f"Looking for uploaded software file: {file_to_update}")
        # Step 4: Change Public Country setting
        log.step("Step 4: Change Public Country setting")
        upload_page.update_country_setting()
        base_page.wait_for_seconds(2)
        # Step 5: Verify Update via Toast Message (common helper)
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        base_page.take_screenshot("ST07-04_Deleted")
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        test_passed = True
    except Exception as e:
        log.error(f"Exception occurred during test: {e}")
        base_page.take_screenshot("ST07_Error")
        raise
    finally:
        log.test_end("bc_setting_updated", success=test_passed)
@pytest.mark.parametrize("authenticated_session", ["distribution_manager"], indirect=True)
def test_manual_setting(authenticated_session, upload_flow, upload_page, base_page, country_page):
    log = setup_test_logging("update_manual_setting")
    file_to_update = "ESG-410_v01.00.00.00-Hema"
    file_to_upload=C.TEST_MANUAL_NAME
    test_passed= False

    try:
        log.test_start("test_update_manual_setting")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        file_path=upload_flow.build_upload_path(C.MANUALS_DIR, file_to_upload,log)
        country_page.perform_manual_release(file_path)
        upload_page.submit_upload()
        base_page.take_screenshot("ST07-04_Deleted")
        test_passed = True
    except Exception as e:
        log.error(f"Exception occurred during multi-login test: {e}")
        base_page.take_screenshot("ST07_MultiLogin_Error")
        raise
    finally:
        log.test_end("test_update_manual_setting", success=test_passed)
@pytest.mark.parametrize("roles", [("customer", "device_update_executor_without_permission", "device_update_executor")])
def test_customer_setting(roles, upload_flow, upload_page, driver,login_page, base_page, country_page,search_page):
    log = setup_test_logging("update_manual_setting")
    file_to_update = "ESG-410_v01.00.00.00-Hema"
    LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
    test_passed= False
    upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
    search_page.search(123456)
    base_page.wait_for_seconds(3)
    search_page.click_download_button_by_software(file_to_update)
    search_page.complete_download_flow()
    search_page.update_and_confirm()
    search_page.enter_confirmation_and_check_unlock("123456",1)
    LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
    test_passed = True


# Helper functions
def login_user(role, login_page, base_page, log, driver):
    LoginUtils.login_as_role(login_page, base_page, log, driver, role)

def logout_user(home_page, base_page, login_page, log, driver):
    LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)

# Parametrize with tuples of (role, serial_number)
@pytest.mark.parametrize("role, serial_number", [
    ("customer", "123456"),
    ("device_update_executor_without_permission", "OSTETEST123"),
    ("device_update_executor", "OSTETEST123456")
])
def test_customer_setting(role, serial_number, upload_flow, upload_page, driver, login_page, base_page, country_page, search_page, home_page):
    log = setup_test_logging("update_manual_setting")
    file_to_update = "ESG-410_v01.00.00.00-Hema"
    test_passed = False

    login_user(role, login_page, base_page, log, driver)

    upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
    search_page.search(serial_number)
    base_page.wait_for_seconds(3)
    search_page.click_download_button_by_software(file_to_update)
    search_page.complete_download_flow()
    search_page.update_and_confirm()
    search_page.enter_confirmation_and_check_unlock(serial_number, 1)

    logout_user(home_page, base_page, login_page, log, driver)

    test_passed = True

# @pytest.mark.parametrize("authenticated_session", ["end_user"], indirect=True)
# def test_public_country_setting(authenticated_session, upload_flow, software_check_page ):
#     log = setup_test_logging("update_manual_setting")
#     # Step 3: Select software package
#     software_check_page.select_software("ESG-410_v01.00.00.00-Hema")
#
#     # Step 4: Enable Public Country setting
#     software_check_page.toggle_public_country_setting(enable=True)
#
#     # Step 5: Reopen and revert Public Country setting
#     software_check_page.reopen_software("ESG-410_v01.00.00.00-Hema")
#     software_check_page.toggle_public_country_setting(enable=False)




