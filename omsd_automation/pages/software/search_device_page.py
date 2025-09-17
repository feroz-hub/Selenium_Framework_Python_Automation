import time

from selenium.common import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from omsd_automation.pages.base.base_page import BasePage
from omsd_automation.utils.db_utils import DBUtils


class SearchDevicePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    SERIAL_NUMBER = (By.ID, "txtSerialNumber")
    BTN_SEARCH = (By.ID, "searchButton")
    CHK_AGREE = (By.ID, "agreeCheckbox")
    BTN_OK = (By.ID, "btnDownload")
    BTN_DOWNLOAD_SOFTWARE = (By.CSS_SELECTOR, "input[value='Download Software']")
    BTN_UPDATE = (By.ID, "btnUpdate")
    BTN_UPDATE_OK = (By.XPATH, "//input[@value='OK' and contains(@class, 'primary-btn')]")
    BTN_NEXT = (By.ID, "btnNext")
    BTN_UNLOCK = (By.CSS_SELECTOR, "input[type='image'][src*='unlock_icon.svg']")
    MODAL_UNLOCK_CODE = (By.CSS_SELECTOR, "h3.unlockCodeModalContent")
    MODAL_OK_BUTTON = (By.CSS_SELECTOR, "div.modal-footer input[value='OK']")
    # ... existing locators ...
    TXT_UNLOCK_CODE = (By.ID, "txtUnlockCode")
    BTN_FINISH = (By.ID, "btnFinish")
    def search(self, serialnumber):
        self.type(self.SERIAL_NUMBER, serialnumber)
        self.click(self.BTN_SEARCH)

    TXT_CONFIRMATION_CODE = (By.ID, "txtConfirmationCode")

    def click_download_button_by_software(self, software_name):
        xpath = f"//button[contains(@onclick, \"clickDownload('{software_name}'\")]"

        # Single wait for element presence and clickability
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

        # Wait for the overlay to disappear (with a shorter timeout for efficiency)
        try:
            WebDriverWait(self.driver, 2).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "container"))
            )
        except TimeoutException:
            pass

        # Scroll into view and attempt to click in one flow
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'}); "
            "arguments[0].click();",
            element
        )

    def _wait_and_get_element(self, locator, condition=EC.element_to_be_clickable):
        """Standard helper for element interaction"""
        try:
            return self.wait.until(condition(locator))
        except TimeoutException:
            # Provide clear, actionable error message
            raise TimeoutException(
                f"Element with locator {locator} not found within {self.timeout}s. "
                f"Check if element exists and is in expected state."
            )

    def set_checkbox_state(self, check):
        """Standard checkbox handling with custom styling support"""
        try:
            # First, try to get the checkbox directly
            checkbox = self._wait_and_get_element(self.CHK_AGREE, EC.presence_of_element_located)

            # For custom-styled checkboxes, use the parent label
            clickable_element = checkbox
            if not checkbox.is_displayed() or checkbox.size['width'] == 0:
                # This is likely a hidden checkbox with custom styling
                clickable_element = checkbox.find_element(By.XPATH, "./parent::label")

            # Ensure it's clickable
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(clickable_element))

            # Check the current state and click if needed
            if checkbox.is_selected() != check:
                clickable_element.click()

                # Verify state changed (with a brief wait for UI updates)
                WebDriverWait(self.driver, 2).until(
                    lambda d: checkbox.is_selected() == check
                )

        except TimeoutException:
            raise Exception(f"Failed to set checkbox to {check}. Element may not be present or interactable.")

    def click_ok_button(self):
        """Standard OK button click"""
        button = self._wait_and_get_element(self.BTN_OK)
        button.click()

        # Wait for any UI changes after click
        time.sleep(0.5)

    def click_download_software_button(self):
        """Download button click with the appropriate timing"""
        # The download button may appear after the OK click, so use a fresh wait
        button = self._wait_and_get_element(self.BTN_DOWNLOAD_SOFTWARE)
        button.click()

    def complete_download_flow(self):
        """Complete flow with proper sequencing"""
        self.set_checkbox_state(True)
        self.click_ok_button()
        self.click_download_software_button()

    def update_and_confirm(self):
        """Ultra-simple update and confirm method."""
        # Click Update button
        button = self._wait_and_get_element(self.BTN_UPDATE)
        button.click()

        # Wait and click OK with JavaScript
        time.sleep(2)
        self.click_update_ok_button_simple()
    def click_update_button(self):
        """Click the Update button"""
        button = self._wait_and_get_element(self.BTN_UPDATE)
        button.click()

    def click_update_ok_button_simple(self):
        """
        Simple direct JavaScript approach to click Update OK button.
        Targets the specific button with onclick="thisPage.changeUpdate(true)"
        """
        print("Clicking Update OK button with simple JavaScript...")

        # Wait for modal to appear
        time.sleep(2)

        # JavaScript targeting the exact button based on your HTML
        js_code = """
        // Target the specific OK button with changeUpdate onclick
        var okButton = document.querySelector('input[value="OK"][onclick*="changeUpdate"]') ||
                       document.querySelector('input[value="OK"][class="primary-btn"]') ||
                       document.querySelector('input[type="button"][value="OK"]');

        if (okButton) {
            // Check if button is visible
            var style = window.getComputedStyle(okButton);
            var isVisible = okButton.offsetParent !== null && 
                           style.display !== 'none' && 
                           style.visibility !== 'hidden';

            if (isVisible) {
                console.log('Found OK button, clicking...');
                okButton.scrollIntoView({behavior: 'instant', block: 'center'});

                // Try regular click first
                try {
                    okButton.click();
                    console.log('OK button clicked with regular click');
                    return true;
                } catch (e) {
                    // Fallback to calling the onclick handler directly
                    console.log('Regular click failed, trying onclick handler...');
                    if (typeof thisPage !== 'undefined' && typeof thisPage.changeUpdate === 'function') {
                        thisPage.changeUpdate(true);
                        console.log('Called thisPage.changeUpdate(true) directly');
                        return true;
                    }

                    // Last resort - dispatch event
                    var event = new MouseEvent('click', {bubbles: true, cancelable: true});
                    okButton.dispatchEvent(event);
                    console.log('OK button clicked with dispatchEvent');
                    return true;
                }
            } else {
                console.log('OK button found but not visible');
            }
        } else {
            console.log('OK button not found in DOM');

            // Debug: log all buttons on page
            var allButtons = document.querySelectorAll('input[type="button"], button');
            console.log('Found ' + allButtons.length + ' buttons on page:');
            for (var i = 0; i < allButtons.length; i++) {
                console.log('  Button ' + i + ': value="' + allButtons[i].value + 
                           '", class="' + allButtons[i].className + 
                           '", onclick="' + (allButtons[i].onclick ? allButtons[i].onclick.toString() : 'none') + '"');
            }
        }

        return false;
        """

        result = self.driver.execute_script(js_code)

        if not result:
            # Additional debugging - check browser console logs
            try:
                logs = self.driver.get_log('browser')
                print("Browser console logs:")
                for log in logs[-5:]:  # Last 5 entries
                    print(f"  {log['level']}: {log['message']}")
            except:
                pass

            raise Exception("Could not find or click Update OK button")

        print("Update OK button clicked successfully")

    def enter_confirmation_code(self, serial_number: str, product_id: int):
        """
        Fetch confirmation code from DB and enter it in the confirmation textbox.
        """
        from omsd_automation.utils.db_utils import DBUtils  # import here to avoid circular dependency

        code = DBUtils.get_confirmation_code(serial_number, product_id)

        if not code:
            raise Exception(
                f"Confirmation code not found for SerialNumber={serial_number}, ProductId={product_id}"
            )

        confirmation_input = self._wait_and_get_element(self.TXT_CONFIRMATION_CODE)
        confirmation_input.clear()
        confirmation_input.send_keys(code)
        """Click the Update button"""
        button = self._wait_and_get_element(self.BTN_NEXT)
        button.click()
        # Wait briefly for the Unlock button to appear
        unlock_button = self._wait_and_get_element(self.BTN_UNLOCK)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", unlock_button
        )
        unlock_button.click()

    def click_unlock_button_and_verify(self, serial_number: str, product_id: int):
        """
        Click unlock button, fetch unlock code from modal,
        compare with DB unlock code, then close the modal.
        """
        from omsd_automation.utils.db_utils import DBUtils  # avoid circular import

        # Click unlock button
        unlock_button = self._wait_and_get_element(self.BTN_NEXT)
        unlock_button.click()

        # Wait for modal to appear and fetch unlock code
        modal_code_el = self._wait_and_get_element(self.MODAL_UNLOCK_CODE, EC.visibility_of_element_located)
        modal_code = modal_code_el.text.strip()
        print(f"Unlock code from modal: {modal_code}")

        # Fetch UnlockCode from DB
        db_code = DBUtils.get_unlock_code(serial_number, product_id)  # You'll add this method in DBUtils
        print(f"Unlock code from DB: {db_code}")

        if modal_code != db_code:
            raise AssertionError(
                f"Unlock code mismatch! Modal={modal_code}, DB={db_code}"
            )
        print("✅ Unlock code matches with DB")

        # Close modal by clicking OK
        ok_button = self._wait_and_get_element(self.MODAL_OK_BUTTON)
        ok_button.click()

    def enter_confirmation_and_check_unlock(self, serial_number, product_id):
        # Fetch both codes in one go
        confirmation_code, db_unlock_code = DBUtils.get_confirmation_and_unlock(serial_number, product_id)

        if not confirmation_code:
            raise AssertionError(f"❌ No ConfirmationCode found for Serial={serial_number}, Product={product_id}")

        if not db_unlock_code:
            raise AssertionError(f"❌ No UnlockCode found for Serial={serial_number}, Product={product_id}")

        # Enter confirmation code into UI
        self._wait_and_get_element(self.TXT_CONFIRMATION_CODE).send_keys(confirmation_code)
        self._wait_and_get_element(self.BTN_NEXT).click()

        # Wait for UI unlock code
        ui_unlock_code = self._wait_and_get_element(self.TXT_UNLOCK_CODE).text.strip()
        print(f"UI Unlock Code: {ui_unlock_code}, DB Unlock Code: {db_unlock_code}")

        # Validate
        if ui_unlock_code != db_unlock_code:
            raise AssertionError(f"❌ Unlock code mismatch! UI={ui_unlock_code}, DB={db_unlock_code}")

        print(f"✅ Unlock code matched: {ui_unlock_code}")

        # Finish flow
        self._wait_and_get_element(self.BTN_FINISH).click()

