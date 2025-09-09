import os
import time
import base64
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from omsd_autmation.utils.config_reader import Config


class BasePage:
    def __init__(self, driver, timeout=None):
        self.driver = driver
        # prefer config implicit wait if available
        self.timeout = timeout if timeout is not None else Config.get("implicit_wait", 5)

    # --- Find / basic wrappers ---
    def find(self, locator):
        """Find a single element."""
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))

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

    # --- Screenshots ---
    def take_screenshot(self, name):
        """Take screenshot and save to logs directory."""
        logs_dir = Config.get("logs.dir", "reports")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        path = os.path.join(logs_dir, name)
        self.driver.save_screenshot(path)
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