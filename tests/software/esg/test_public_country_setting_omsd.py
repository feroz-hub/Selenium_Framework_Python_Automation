# import pytest
# from selenium.webdriver.common.by import By
#
# from tests import test_config as C
# from omsd_automation.utils.logger import setup_test_logging
# from omsd_automation.utils.login_utils import LoginUtils
# from omsd_automation.utils.logout_utils import LogoutUtils
#
#
# @pytest.mark.parametrize("roles", [("end_user", "distribution_manager")])
# def test_public_country_setting_omsd(roles, driver, base_page, login_page, software_page, upload_page, home_page):
#     """
#     End-to-end test for updating the Countries of publication setting for a software package
#     for two different roles in sequence. Flow based on the issue description:
#
#     1) Login as end_user
#        - Open Software List for the target product
#        - Open Available Version (target software)
#        - Check Countries of publication (any country; here we toggle "All Countries") and Confirm Change
#        - Click Save and verify toast "Software settings has been saved"
#        - Revert changes before sign out: open package, uncheck Countries, Confirm, Save
#        - Sign out and verify login page appears
#
#     2) Login as distribution_manager
#        - Repeat: navigate, open software, check Countries, Confirm, Save
#        - Verify toast, and sign out
#     """
#     log = setup_test_logging("public_country_setting_omsd")
#     log.test_start("test_public_country_setting_omsd")
#
#     def open_target_package():
#         # Navigate to the product software list
#         log.step("Navigate to product software list")
#         log.action(f"Opening software list for product: '{C.OMSD_ESG_410}'")
#         software_page.navigate_to_product_software(C.OMSD_ESG_410)
#         # Select the uploaded/target software by the exact name
#         file_to_update = C.TEST_FILE_NAME
#         log.action(f"Selecting target software: {file_to_update}")
#         file_link_locator = (
#             By.XPATH,
#             f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_update}']"
#         )
#         el = base_page.wait_for_element_to_be_clickable(file_link_locator, timeout=15)
#         el.click()
#         base_page.take_screenshot("OMSD-Country-Select-Package")
#
#     def select_countries_and_save():
#         # Check Countries of publication: toggle All Countries, Confirm, then Save
#         log.step("Select countries and save")
#         upload_page.click_scroll(upload_page.CHK_ALL_COUNTRIES)
#         base_page.wait_for_seconds(1)
#         upload_page.click(upload_page.BTN_EDIT_CONFIRM)
#         base_page.wait_for_element_to_be_clickable(upload_page.BTN_EDIT_SAVE, timeout=10)
#         upload_page.click(upload_page.BTN_EDIT_SAVE)
#         # Verify toast
#         toast_locator = (By.CSS_SELECTOR, "#toast-container .toast")
#         toast_text = base_page.wait_for_element(toast_locator, timeout=15).text
#         log.verification("Toast confirms saved", "save" in toast_text.lower())
#         base_page.take_screenshot("OMSD-Country-Toast")
#
#     def revert_countries_and_save():
#         # Uncheck the same selection and save again
#         log.step("Revert country selection and save")
#         upload_page.click_scroll(upload_page.CHK_ALL_COUNTRIES)
#         base_page.wait_for_seconds(1)
#         upload_page.click(upload_page.BTN_EDIT_CONFIRM)
#         base_page.wait_for_element_to_be_clickable(upload_page.BTN_EDIT_SAVE, timeout=10)
#         upload_page.click(upload_page.BTN_EDIT_SAVE)
#         # Verify toast
#         toast_locator = (By.CSS_SELECTOR, "#toast-container .toast")
#         toast_text = base_page.wait_for_element(toast_locator, timeout=15).text
#         log.verification("Toast confirms saved after revert", "save" in toast_text.lower())
#         base_page.take_screenshot("OMSD-Country-Toast-Revert")
#
#     try:
#         # 1) Login as end_user
#         LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
#         open_target_package()
#         select_countries_and_save()
#
#         # Note: revert before sign-out for other test cases safety
#         open_target_package()
#         revert_countries_and_save()
#
#         # Sign out
#         LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
#
#         # 2) Login as distribution_manager
#         LoginUtils.login_as_role(login_page, base_page, log, driver, roles[1])
#         open_target_package()
#         select_countries_and_save()
#
#         # Sign out again
#         LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
#
#     finally:
#         log.test_end("test_public_country_setting_omsd", success=True)
# @pytest.mark.parametrize("roles", [("distribution_manager_without_permission", "distribution_manager")])
# def test_public_manual_settings_multi_user(roles,driver, upload_flow, base_page, login_page, software_page, upload_page,
#                                 home_page,edit_software_release_page):
#     """
#     Test to verify the 'Public Country' setting during software upload.
#     Steps:
#     1. Login as distribution manager.
#     2. Navigate to a product software list.
#     3. Upload a software package with 'Public Country' enabled.
#     4. Verify the upload was successful via toast and list.
#     5. Reopen the uploaded package and verify 'Public Country' is still enabled.
#     6. Sign out and verify redirection to the login page.
#     """
#     # 1) Login as end_user
#     log = setup_test_logging("upload_software_public_country")
#
#
#     log.test_start("test_upload_software_public_country")
#     test_passed = False
#     file_to_update = "ESG-410_v01.00.00.00-Hema"
#     file_to_upload = C.TEST_MANUAL_NAME
#     try:
#         # --- Step 1: Login ---
#         LoginUtils.login_as_role(login_page, base_page, log, driver, roles[0])
#
#         # --- Step 2: Navigate to a product software list ---
#         log.step("Step 2: Navigate to product software list")
#         upload_flow.navigate_to_product(C.OMSD_ESG_410, "bc_setting_updated")
#         # --- Step 3: Select Uploaded software ---
#         log.step("Step 3: Select the uploaded software to change Public Country setting")
#         upload_flow.select_uploaded_file(file_to_update, "ST07-03")
#         log.action(f"Looking for uploaded software file: {file_to_update}")
#         file_path = upload_flow.build_upload_path(C.MANUALS_DIR, file_to_upload, log)
#
#         time.sleep(3)
#         # edit_software_release_page.click_add_button()
#         edit_software_release_page.upload_pdf(file_path)
#         test_passed = True
#         LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
#     except Exception as e:
#         log.error(f"Exception occurred during test: {e}")
#         base_page.take_screenshot("ST07_Error")
#         raise
#     finally:
#         log.test_end("bc_setting_updated", success=test_passed)
