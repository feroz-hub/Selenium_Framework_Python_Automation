import pytest
import time
import traceback

from omsd_automation.utils.logger import setup_test_logging
from omsd_automation.utils.login_utils import LoginUtils
from omsd_automation.utils.logout_utils import LogoutUtils
from omsd_automation.utils.element_helper import fallback_find_uploaded_name
from tests import test_config as C


@pytest.mark.usefixtures(
    "driver",
    "upload_flow",
    "base_page",
    "upload_page",
    "login_page",
    "software_page",
    "home_page",
    "search_page",
    "country_page"
)
def test_combined_software_upload(driver, upload_flow, base_page, upload_page, login_page, software_page, home_page, search_page, country_page):
    log = setup_test_logging("combined_upload_flow")
    test_passed = False

    file_to_upload = C.TEST_FILE_NAME
    file_to_update = "ESG-410_v01.00.00.00-Hema"

    try:
        # ====================================================
        # Step 1: Software uploader uploads ESG package
        # ====================================================
        LoginUtils.login_as_role(login_page, base_page, log, driver, "software_uploader")
        log.test_start("upload_software")

        upload_flow.navigate_to_product(C.OMSD_ESG_410, "STS06-11")
        upload_flow.perform_upload_file(C.UPLOAD_DIR, file_to_upload)
        upload_flow.verify_toast("The software has been added.", C.DEFAULT_TIMEOUT)

        list_timeout = getattr(C, "UPLOAD_WAIT_TIMEOUT", max(C.DEFAULT_TIMEOUT, 60))
        found_file_text = upload_flow.wait_for_uploaded_name_with_fallback(
            file_to_upload, list_timeout, fallback_find_uploaded_name
        )
        upload_flow.normalize_and_assert_filename(found_file_text, file_to_upload)
        upload_flow.download_uploaded_file(file_to_upload)

        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        log.test_end("upload_software", success=True)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # ====================================================
        # Step 2: Software uploader updates Public BC setting
        # ====================================================
        LoginUtils.login_as_role(login_page, base_page, log, driver, "software_uploader")
        log.test_start("public_bc_setting")

        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        upload_flow.select_uploaded_file(file_to_upload, "ST07-03")
        upload_page.update_bc_setting(enable=True)
        upload_flow.verify_toast("The software settings have been saved.")
        base_page.take_screenshot("ST07-04_BC_Updated")

        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        log.test_end("public_bc_setting", success=True)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # ====================================================
        # Step 3: Distribution manager updates Public Country setting
        # ====================================================
        log.test_start("public_country_setting")

        # First role
        LoginUtils.login_as_role(login_page, base_page, log, driver, "distribution_manager_without_permission")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        upload_flow.navigate_to_product_revert(C.OMSD_ESG_410, "bc_setting_updated")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # Second role
        LoginUtils.login_as_role(login_page, base_page, log, driver, "distribution_manager")
        upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
        upload_flow.select_uploaded_file(file_to_update, "ST07-03")
        upload_page.update_country_setting()
        upload_flow.verify_toast("The software settings have been saved.", C.DEFAULT_TIMEOUT)
        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)

        log.test_end("public_country_setting", success=True)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # ====================================================
        # Step 4: Customer setting
        # ====================================================
        LoginUtils.login_as_role(login_page, base_page, log, driver, "customer")
        log.test_start("customer_setting")

        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        search_page.search("123456")
        base_page.wait_for_seconds(3)
        search_page.click_download_button_by_software(file_to_update)
        search_page.complete_download_flow()
        search_page.update_and_confirm()
        search_page.enter_confirmation_and_check_unlock("123456", 1)

        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        log.test_end("customer_setting", success=True)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # ====================================================
        # Step 5: Device Update Executor (without permission)
        # ====================================================
        LoginUtils.login_as_role(login_page, base_page, log, driver, "device_update_executor_without_permission")
        log.test_start("device_update_executor_without_permission")

        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        search_page.search("OSTETEST123")
        base_page.wait_for_seconds(3)
        search_page.click_download_button_by_software(file_to_update)
        search_page.complete_download_flow()
        search_page.update_and_confirm()
        search_page.enter_confirmation_and_check_unlock("OSTETEST123", 1)

        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        log.test_end("device_update_executor_without_permission", success=True)
        # ------------------------------------------------------------------
        # Reset before new login
        # ------------------------------------------------------------------
        LoginUtils.reset_to_login_page(login_page, base_page, driver, log)

        # ====================================================
        # Step 6: Device Update Executor (with permission)
        # ====================================================
        LoginUtils.login_as_role(login_page, base_page, log, driver, "device_update_executor")
        log.test_start("device_update_executor")

        upload_flow.navigate_to_product(C.OMSD_ESG_410, "ST06-11")
        search_page.search("OSTETEST123456")
        base_page.wait_for_seconds(3)
        search_page.click_download_button_by_software(file_to_update)
        search_page.complete_download_flow()
        search_page.update_and_confirm()
        search_page.enter_confirmation_and_check_unlock("OSTETEST123456", 1)

        LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
        log.test_end("device_update_executor", success=True)


        test_passed = True

    except Exception as e:
        log.error(f"An exception occurred in combined flow: {e}")
        tb = traceback.format_exc()
        log.debug(tb)
        try:
            ts = int(time.time())
            base_page.save_screenshot(f"test_combined_failure_{ts}.png")
            with open(f"test_combined_failure_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(base_page.page_source)
        except Exception:
            log.warning("Failed to save diagnostics artifacts.")
        pytest.fail(f"Combined software upload flow failed: {e}")

    finally:
        log.test_end("combined_upload_flow", success=test_passed)
