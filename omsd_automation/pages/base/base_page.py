import base64
import os
import time

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from omsd_automation.utils.config_reader import Config


class BasePage:
    DEFAULT_TIMEOUT = 5

    def __init__(self, driver, timeout=None):
        self.driver = driver
        # prefer config implicit wait if available
        self.timeout = timeout if timeout is not None else Config.get("implicit_wait", 5)

    # --- Find / basic wrappers ---
    def find(self, locator):
        """Find a single element."""
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))

    def wait_for_seconds(self, seconds):
        time.sleep(seconds)

    def find_all(self, locator):
        """Find all elements matching the locator."""
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        """Click an element safely with retry logic."""
        el = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

        # Scroll element into view
        self.scroll_into_view(locator)

        try:
            el.click()
        except ElementClickInterceptedException:
            # Fallback: JS click
            self.driver.execute_script("arguments[0].click();", el)
    def find_element(self, locator):
        """Find a single element."""
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))
    def click_scroll(self, locator):
        el = self.find_element(locator)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
            el.click()
        except Exception:
            self.log.warning(f"Normal click failed, retrying with JS click: {locator}")
            self.driver.execute_script("arguments[0].click();", el)
    def click_when_ready(self, locator, timeout=15, poll_frequency=0.5):
        """Click an element safely after overlay disappears and retry if intercepted."""
        end_time = time.time() + timeout
        while True:
            try:
                # Wait for overlay to disappear (if it exists)
                if hasattr(self, "OVERLAY"):
                    self.wait_for_element_to_disappear(self.OVERLAY, timeout=timeout)

                # Wait until element is clickable
                el = WebDriverWait(self.driver, timeout, poll_frequency).until(
                    EC.element_to_be_clickable(locator)
                )
                el.click()
                return  # Click succeeded, exit
            except ElementClickInterceptedException:
                if time.time() > end_time:
                    raise  # Timeout exceeded
                time.sleep(poll_frequency)  # Retry after a short wait
            except TimeoutException:
                raise

    def type(self, locator, text):
        """Type text into an element after clearing it."""
        el = WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        """Get text from an element."""
        el = WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(locator))
        return el.text

    def get_attribute(self, locator, attr):
        """Get attribute value from an element."""
        el = self.find(locator)
        return el.get_attribute(attr)

    def is_visible(self, locator, timeout=None):
        """Return True if element is visible within timeout, else False."""
        t = timeout or self.timeout
        try:
            WebDriverWait(self.driver, t).until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False

    def is_element_visible(self, locator, timeout=10):
        """Return True if element is visible after overlay disappears, else False."""
        if hasattr(self, "OVERLAY"):
            self.wait_for_element_to_disappear(self.OVERLAY, timeout)
        return self.is_visible(locator, timeout)

    # --- Wait methods ---
    def wait_for_element(self, locator, timeout=None):
        """Wait for element to be present."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.presence_of_element_located(locator))

    def wait_for_element_to_be_clickable(self, locator, timeout=None):
        """Wait until the element is clickable and return it."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.element_to_be_clickable(locator))

    def wait_for_element_to_be_visible(self, locator, timeout=None):
        """Wait until the element is visible and return it."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.visibility_of_element_located(locator))

    def wait_for_element_to_disappear(self, locator, timeout=None):
        """Wait until the element disappears from the page."""
        t = timeout or self.timeout
        WebDriverWait(self.driver, t).until(EC.invisibility_of_element_located(locator))

    def wait_for_title(self, title_text, timeout=None):
        """Wait for page title to contain specific text."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.title_contains(title_text))

    def wait_for_text(self, locator, text, timeout=None):
        """Wait for element to contain specific text."""
        t = timeout or self.timeout
        return WebDriverWait(self.driver, t).until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_preloader_to_disappear(self, timeout=15):
        """Wait until preloader overlay disappears."""
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((By.ID, "preloader-overlay"))
            )
        except:
            pass  # ignore timeout, maybe overlay already gone

    # --- JS / scroll / actions ---
    def execute_js(self, script, *args):
        """Execute JavaScript code."""
        return self.driver.execute_script(script, *args)

    def scroll_into_view(self, locator):
        """Scroll element into view."""
        el = self.find(locator)
        self.execute_js("arguments[0].scrollIntoView({block: 'center'});", el)

    def hover(self, locator):
        """Hover over an element."""
        el = self.find(locator)
        ActionChains(self.driver).move_to_element(el).perform()

    # --- Select / toggles ---
    def select_by_visible_text(self, locator, text):
        """Select option by visible text from dropdown."""
        el = self.find(locator)
        select = Select(el)
        select.select_by_visible_text(text)

    def select_by_value(self, locator, value):
        """Select option by value from dropdown."""
        el = self.find(locator)
        select = Select(el)
        select.select_by_value(value)

    def toggle_checkbox(self, locator, should_be_checked=True):
        """Toggle checkbox to desired state."""
        el = self.find(locator)
        current = el.is_selected()
        if current != should_be_checked:
            el.click()

    # --- File upload helpers ---
    def upload_file(self, file_input_locator, file_path):
        """
        Standard send_keys for <input type='file'>. Most reliable.
        """
        if not os.path.isabs(file_path):
            # allow relative paths from project root
            base = os.getcwd()
            file_path = os.path.join(base, file_path)
        assert os.path.exists(file_path), f"Upload file does not exist: {file_path}"
        el = self.find(file_input_locator)
        el.send_keys(file_path)

    def drag_and_drop_upload(self, drop_locator, file_path):
        """
        Drag-n-drop simulation by constructing a File in JS (uses base64 transfer).
        Use when site expects a drag/drop event instead of file input.
        """
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        script = """
        var target = arguments[0];
        var filename = arguments[1];
        var content = atob(arguments[2]);
        var arr = new Uint8Array(content.length);
        for (var i = 0; i < content.length; i++) { arr[i] = content.charCodeAt(i); }
        var blob = new Blob([arr]);
        var file = new File([blob], filename);
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        var event = new DragEvent('drop', { dataTransfer: dataTransfer, bubbles: true, cancelable: true });
        target.dispatchEvent(event);
        """
        el = self.find(drop_locator)
        self.execute_js(script, el, os.path.basename(file_path), b64)

    # --- Download verification ---
    def wait_for_file_download(self, download_dir, filename_substring, timeout=30):
        """Wait for file download to complete."""
        end = time.time() + timeout
        download_dir = os.path.expanduser(download_dir)
        while time.time() < end:
            try:
                for f in os.listdir(download_dir):
                    if filename_substring in f and not f.endswith(".crdownload"):
                        return os.path.join(download_dir, f)
            except FileNotFoundError:
                pass
            time.sleep(0.7)
        raise TimeoutException(f"File containing '{filename_substring}' not found in {download_dir} within {timeout}s")

    def take_screenshot(self, step_name: str):
        """Take a screenshot organized under product/test case folders.
        Returns the saved absolute path.
        """
        from omsd_automation.utils.screenshot import take_screenshot as _take
        path = _take(self.driver, step_name)
        return path

    # --- Misc utility methods ---
    def get_title(self):
        """Get current page title."""
        return self.driver.title

    def accept_cookies(self):
        """Accept cookies popup if present."""
        try:
            cookie_btn = (By.ID, "onetrust-accept-btn-handler")  # update if your site has diff id/class
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(cookie_btn)
            ).click()
        except (NoSuchElementException, TimeoutException):
            # no popup appeared, continue
            pass

    def switch_to_frame(self, locator: tuple, timeout: int = 10):
        """Waits for an iframe to be available and switches to it."""
        WebDriverWait(self.driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it(locator)
        )

    def switch_to_default_content(self):
        """Switches the context back to the main document."""
        self.driver.switch_to.default_content()

    # Add these methods to your BasePage class

    def click_checkbox(self, locator, timeout=10):
        """
        Click a checkbox (select/unselect based on current state).

        Args:
            locator: Tuple of (By, selector) for the checkbox
            timeout: Maximum time to wait for element
        """
        element = self.wait_for_element_to_be_clickable(locator, timeout)
        element.click()

    def check_checkbox(self, locator, timeout=10):
        """
        Check (select) a checkbox if it's not already checked.

        Args:
            locator: Tuple of (By, selector) for the checkbox
            timeout: Maximum time to wait for element
        """
        element = self.wait_for_element_to_be_clickable(locator, timeout)
        if not element.is_selected():
            element.click()

    def uncheck_checkbox(self, locator, timeout=10):
        """
        Uncheck (deselect) a checkbox if it's currently checked.

        Args:
            locator: Tuple of (By, selector) for the checkbox
            timeout: Maximum time to wait for element
        """
        element = self.wait_for_element_to_be_clickable(locator, timeout)
        if element.is_selected():
            element.click()

    def is_checkbox_checked(self, locator, timeout=10):
        """
        Check if a checkbox is currently selected/checked.

        Args:
            locator: Tuple of (By, selector) for the checkbox
            timeout: Maximum time to wait for element

        Returns:
            bool: True if checkbox is checked, False otherwise
        """
        element = self.wait_for_element_to_be_visible(locator, timeout)
        return element.is_selected()

    def toggle_checkbox(self, locator, timeout=10):
        """
        Toggle a checkbox (opposite of current state).

        Args:
            locator: Tuple of (By, selector) for the checkbox
            timeout: Maximum time to wait for element

        Returns:
            bool: New state after toggle (True if now checked, False if unchecked)
        """
        element = self.wait_for_element_to_be_clickable(locator, timeout)
        element.click()
        return element.is_selected()

    def set_checkbox_state(self, locator, desired_state, timeout=10):
        """
        Set checkbox to a specific state (checked/unchecked).

        Args:
            locator: Tuple of (By, selector) for the checkbox
            desired_state: bool - True to check, False to uncheck
            timeout: Maximum time to wait for element

        Returns:
            bool: Final state of checkbox
        """
        element = self.wait_for_element_to_be_clickable(locator, timeout)
        current_state = element.is_selected()

        if current_state != desired_state:
            element.click()

        return element.is_selected()

    def check_multiple_checkboxes(self, locators, timeout=10):
        """
        Check multiple checkboxes at once.

        Args:
            locators: List of tuples [(By, selector), (By, selector), ...]
            timeout: Maximum time to wait for each element
        """
        for locator in locators:
            self.check_checkbox(locator, timeout)

    def uncheck_multiple_checkboxes(self, locators, timeout=10):
        """
        Uncheck multiple checkboxes at once.

        Args:
            locators: List of tuples [(By, selector), (By, selector), ...]
            timeout: Maximum time to wait for each element
        """
        for locator in locators:
            self.uncheck_checkbox(locator, timeout)

    def get_all_checked_checkboxes(self, container_locator=None, timeout=10):
        """
        Get all currently checked checkboxes in a container or entire page.

        Args:
            container_locator: Optional container to search within
            timeout: Maximum time to wait for container (if specified)

        Returns:
            list: List of WebElements that are checked checkboxes
        """
        if container_locator:
            container = self.wait_for_element_to_be_visible(container_locator, timeout)
            checkboxes = container.find_elements(By.XPATH, ".//input[@type='checkbox']")
        else:
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")

        return [cb for cb in checkboxes if cb.is_selected()]

    def get_checkbox_by_label(self, label_text, timeout=10):
        """
        Find and return checkbox by its associated label text.

        Args:
            label_text: Text content of the label associated with checkbox
            timeout: Maximum time to wait for element

        Returns:
            WebElement: The checkbox element
        """
        # Try different common patterns for label-checkbox association
        patterns = [
            f"//label[contains(text(), '{label_text}')]/input[@type='checkbox']",
            f"//input[@type='checkbox']/following-sibling::label[contains(text(), '{label_text}')]/../input[@type='checkbox']",
            f"//label[contains(text(), '{label_text}')]/@for",  # for ID association
        ]

        for pattern in patterns:
            try:
                if pattern.endswith('/@for'):
                    # Handle label 'for' attribute case
                    label_for_id = self.driver.find_element(By.XPATH, pattern).get_attribute('for')
                    return self.wait_for_element_to_be_visible((By.ID, label_for_id), timeout)
                else:
                    return self.wait_for_element_to_be_visible((By.XPATH, pattern), timeout)
            except:
                continue

        raise NoSuchElementException(f"Checkbox with label '{label_text}' not found")

    def click_checkbox_by_label(self, label_text, timeout=10):
        """
        Click checkbox by its associated label text.

        Args:
            label_text: Text content of the label associated with checkbox
            timeout: Maximum time to wait for element
        """
        checkbox = self.get_checkbox_by_label(label_text, timeout)
        checkbox.click()

    def verify_checkbox_state(self, locator, expected_state, timeout=10):
        """
        Verify that a checkbox is in the expected state.

        Args:
            locator: Tuple of (By, selector) for the checkbox
            expected_state: bool - True if should be checked, False if unchecked
            timeout: Maximum time to wait for element

        Returns:
            bool: True if checkbox is in expected state, False otherwise
        """
        actual_state = self.is_checkbox_checked(locator, timeout)
        return actual_state == expected_state

    def wait_for_checkbox_state(self, locator, expected_state, timeout=10):
        """
        Wait for a checkbox to reach a specific state.

        Args:
            locator: Tuple of (By, selector) for the checkbox
            expected_state: bool - True to wait for checked, False for unchecked
            timeout: Maximum time to wait

        Returns:
            bool: True if state reached within timeout, False otherwise
        """
        from selenium.webdriver.support.ui import WebDriverWait

        try:
            if expected_state:
                # Wait for checkbox to be selected
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.find_element(*locator).is_selected()
                )
            else:
                # Wait for checkbox to be unselected
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: not driver.find_element(*locator).is_selected()
                )
            return True
        except TimeoutException:
            return False

    # Helper method for checkbox groups (like terms & conditions, preferences, etc.)
    def handle_checkbox_group(self, checkboxes_config, timeout=10):
        """
        Handle a group of checkboxes based on configuration.

        Args:
            checkboxes_config: Dict with checkbox locators as keys and desired states as values
                              Example: {
                                  (By.ID, "terms"): True,
                                  (By.ID, "newsletter"): False,
                                  (By.ID, "notifications"): True
                              }
            timeout: Maximum time to wait for each element
        """
        for locator, desired_state in checkboxes_config.items():
            self.set_checkbox_state(locator, desired_state, timeout)

    def wait_for_page_to_reappear(self, locator, timeout=10):
        """
        Wait for a specific element (usually from login or landing page)
        to reappear after logout/session expiration.

        Args:
            locator: Tuple (By, selector) for the element that identifies the page
            timeout: Max wait time
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
