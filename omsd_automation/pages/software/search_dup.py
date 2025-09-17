# import time
#
# from selenium.common import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
#
# from omsd_automation.pages.base.base_page import BasePage
#
#
# class SearchDevicePage(BasePage):
#     def __init__(self, driver):
#         super().__init__(driver)
#
#     SERIAL_NUMBER = (By.ID, "txtSerialNumber")
#     BTN_SEARCH = (By.ID, "searchButton")
#     CHK_AGREE = (By.ID, "agreeCheckbox")
#     BTN_OK = (By.ID, "btnDownload")
#     BTN_DOWNLOAD_SOFTWARE = (By.CSS_SELECTOR, "input[value='Download Software']")
#     def search(self, serialnumber):
#         self.type(self.SERIAL_NUMBER, serialnumber)
#         self.click(self.BTN_SEARCH)
#
#
#     def click_download_button_by_software(self, software_name):
#         xpath = f"//button[contains(@onclick, \"clickDownload('{software_name}'\")]"
#
#         # Single wait for element presence and clickability
#         element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
#
#         # Wait for the overlay to disappear (with a shorter timeout for efficiency)
#         try:
#             WebDriverWait(self.driver, 2).until(
#                 EC.invisibility_of_element_located((By.CLASS_NAME, "container"))
#             )
#         except TimeoutException:
#             pass
#
#         # Scroll into view and attempt to click in one flow
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'}); "
#             "arguments[0].click();",
#             element
#         )
#
#     # def set_checkbox_state(self, check):
#     #     """
#     #     Set the state of the agreed checkbox to check (True) or unchecked (False).
#     #     Optimized for label-wrapped checkbox with custom styling.
#     #     """
#     #     try:
#     #         # Wait for the checkbox input to be present
#     #         checkbox_input = WebDriverWait(self.driver, self.timeout).until(
#     #             EC.presence_of_element_located((By.ID, "agreeCheckbox"))
#     #         )
#     #
#     #         # Find the parent label for clicking (more reliable than clicking input directly)
#     #         parent_label = checkbox_input.find_element(By.XPATH, "./parent::label")
#     #
#     #         # Scroll the label into view
#     #         self.driver.execute_script(
#     #             "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
#     #             parent_label
#     #         )
#     #
#     #         # Wait for an element to be clickable
#     #         WebDriverWait(self.driver, 3).until(
#     #             EC.element_to_be_clickable((By.XPATH, "//label[.//input[@id='agreeCheckbox']]"))
#     #         )
#     #
#     #         # Check current state
#     #         is_currently_checked = checkbox_input.is_selected()
#     #
#     #         # Click only if we need to change the state
#     #         if is_currently_checked != check:
#     #             try:
#     #                 # Try clicking the label first (most reliable for custom checkboxes)
#     #                 parent_label.click()
#     #             except ElementClickInterceptedException:
#     #                 # Fallback: click using JavaScript
#     #                 self.driver.execute_script("arguments[0].click();", parent_label)
#     #
#     #             # Verify the state changed
#     #             time.sleep(0.3)  # Brief wait for any animations
#     #             new_state = checkbox_input.is_selected()
#     #
#     #             if new_state != check:
#     #                 # If normal click didn't work, try JavaScript with event triggering
#     #                 self.driver.execute_script(f"""
#     #                     var checkbox = document.getElementById('agreeCheckbox');
#     #                     checkbox.checked = {str(check).lower()};
#     #
#     #                     // Trigger the onchange event
#     #                     checkbox.dispatchEvent(new Event('change', {{bubbles: true}}));
#     #
#     #                     // Call the onchange handler directly as backup
#     #                     if (typeof thisPage !== 'undefined' && thisPage.clickAgree) {{
#     #                         thisPage.clickAgree(checkbox);
#     #                     }}
#     #                 """)
#     #
#     #         print(f"Checkbox state successfully set to {check}")
#     #
#     #     except TimeoutException:
#     #         raise Exception(f"Checkbox with ID 'agreeCheckbox' not found within {self.timeout} seconds")
#     #     except Exception as e:
#     #         raise Exception(f"Failed to set checkbox state to {check}: {str(e)}")
#
#     # def set_checkbox_state(self, check):
#     #     """
#     #     Set the state of the agreed checkbox to check (True) or unchecked (False).
#     #     Optimized for label-wrapped checkbox with custom styling.
#     #     """
#     #     try:
#     #         # Wait for the checkbox label to be clickable
#     #         parent_label = WebDriverWait(self.driver, self.timeout).until(
#     #             EC.element_to_be_clickable((By.XPATH, "//label[.//input[@id='agreeCheckbox']]"))
#     #         )
#     #
#     #         # Scroll into view
#     #         self.driver.execute_script(
#     #             "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
#     #             parent_label
#     #         )
#     #
#     #         # Get the checkbox input
#     #         checkbox_input = parent_label.find_element(By.ID, "agreeCheckbox")
#     #
#     #         # Check the current state and click only if needed
#     #         if checkbox_input.is_selected() != check:
#     #             try:
#     #                 parent_label.click()
#     #             except ElementClickInterceptedException:
#     #                 # Fallback: JavaScript click with event dispatch
#     #                 self.driver.execute_script(
#     #                     f"arguments[0].click(); "
#     #                     f"var checkbox = document.getElementById('agreeCheckbox'); "
#     #                     f"checkbox.checked = {str(check).lower()}; "
#     #                     f"checkbox.dispatchEvent(new Event('change', {{bubbles: true}}));",
#     #                     parent_label
#     #                 )
#     #
#     #             # Brief pause to allow state change
#     #             time.sleep(0.1)  # Verify state
#     #             if checkbox_input.is_selected() != check:
#     #                 raise Exception(f"Failed to set checkbox state to {check}")
#     #
#     #         print(f"Checkbox state set to {check}")
#     #
#     #     except TimeoutException:
#     #         raise Exception(f"Checkbox with ID 'agreeCheckbox' not found within {self.timeout} seconds")
#     #     except Exception as e:
#     #         raise Exception(f"Failed to set checkbox state to {check}: {str(e)}")
#     #
#     # def _click_ok_with_js(self):
#     #     """Click the OK button using JavaScript and trigger the onclick handler."""
#     #     js_code = """
#     #     var button = document.getElementById('btnDownload');
#     #
#     #     if (button && !button.disabled) {
#     #         // Try clicking the button
#     #         button.click();
#     #
#     #         // If that doesn't work, call the onclick handler directly
#     #         if (typeof thisPage !== 'undefined' && typeof thisPage.judgeShowPrecautionPreview === 'function') {
#     #             thisPage.judgeShowPrecautionPreview(true);
#     #         }
#     #
#     #         return true;
#     #     }
#     #
#     #     return false;
#     #     """
#     #
#     #     result = self.driver.execute_script(js_code)
#     #     if not result:
#     #         raise Exception("OK button not found or is disabled")
#     #
#     #     print("OK button clicked using JavaScript")
#
#     def _wait_and_get_element(self, locator, condition=EC.element_to_be_clickable):
#         """Standard helper for element interaction"""
#         try:
#             return self.wait.until(condition(locator))
#         except TimeoutException:
#             # Provide clear, actionable error message
#             raise TimeoutException(
#                 f"Element with locator {locator} not found within {self.timeout}s. "
#                 f"Check if element exists and is in expected state."
#             )
#
#     def set_checkbox_state(self, check):
#         """Standard checkbox handling with custom styling support"""
#         try:
#             # First, try to get the checkbox directly
#             checkbox = self._wait_and_get_element(self.CHK_AGREE, EC.presence_of_element_located)
#
#             # For custom-styled checkboxes, use the parent label
#             clickable_element = checkbox
#             if not checkbox.is_displayed() or checkbox.size['width'] == 0:
#                 # This is likely a hidden checkbox with custom styling
#                 clickable_element = checkbox.find_element(By.XPATH, "./parent::label")
#
#             # Ensure it's clickable
#             WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(clickable_element))
#
#             # Check the current state and click if needed
#             if checkbox.is_selected() != check:
#                 clickable_element.click()
#
#                 # Verify state changed (with a brief wait for UI updates)
#                 WebDriverWait(self.driver, 2).until(
#                     lambda d: checkbox.is_selected() == check
#                 )
#
#         except TimeoutException:
#             raise Exception(f"Failed to set checkbox to {check}. Element may not be present or interactable.")
#
#     def click_ok_button(self):
#         """Standard OK button click"""
#         button = self._wait_and_get_element(self.BTN_OK)
#         button.click()
#
#         # Wait for any UI changes after click
#         time.sleep(0.5)
#
#     def click_download_software_button(self):
#         """Download button click with the appropriate timing"""
#         # The download button may appear after the OK click, so use a fresh wait
#         button = self._wait_and_get_element(self.BTN_DOWNLOAD_SOFTWARE)
#         button.click()
#
#     def complete_download_flow(self):
#         """Complete flow with proper sequencing"""
#         self.set_checkbox_state(True)
#         self.click_ok_button()
#         self.click_download_software_button()