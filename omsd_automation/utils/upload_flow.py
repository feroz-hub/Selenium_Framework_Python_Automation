
# omsd_automation/utils/upload_flow.py
import time
from pathlib import Path
from typing import Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


# These helpers centralize common upload verification logic to keep tests DRY.
class UploadFlow:
    def __init__(self, software_page,base_page, upload_page, driver, log):
        self.base_page = base_page
        self.upload_page = upload_page
        self.software_page = software_page
        self.driver = driver
        self.log = log

    def navigate_to_product(self, product_name: str,screenshot_name: str):
        self.log.step("Navigate to product software list")
        self.log.action(f"Opening software list for product: '{product_name}'")
        self.software_page.open_software_list(product_name)
        self.log.verification(
            f"Successfully navigated to the software list for '{product_name}'", True
        )
        self.base_page.wait_for_seconds(3)
        self.base_page.take_screenshot(screenshot_name)
        self.log.page_info(self.driver.title, self.driver.current_url)
    def navigate_to_product_revert(self, product_name: str,screenshot_name: str):
        self.log.step("Navigate to product software list")
        self.log.action(f"Opening software list for product: '{product_name}'")
        self.base_page.wait_for_preloader_to_disappear()
        self.software_page.ensure_on_products_list()
        self.software_page.open_software_list_revert(product_name)
        self.log.verification(
            f"Successfully navigated to the software list for '{product_name}'", True
        )
        self.base_page.wait_for_seconds(3)
        self.base_page.take_screenshot(screenshot_name)
        self.log.page_info(self.driver.title, self.driver.current_url)
    @staticmethod
    def build_upload_path(upload_dir, file_name: str,log) -> Path:
        """
        Ensure a pathlib.Path for the upload directory and compose the full file path.
        Raises FileNotFoundError if the file does not exist.
        """
        base = Path(upload_dir) if not isinstance(upload_dir, Path) else upload_dir
        file_path = base / file_name
        log.debug(f"Constructed file path for upload: {file_path}")
        if not file_path.exists():
            log.error(f"Upload file does not exist: {file_path}")
            raise FileNotFoundError(f"Upload file does not exist: {file_path}")
        return file_path

    def select_uploaded_file(self, file_to_update: str, screenshot_name: str, timeout: int = 10):
        """
        Selects the uploaded software file by clicking its link and takes a screenshot.
        Args:
            file_to_update: The uploaded file name to click.
            screenshot_name: The screenshot filename to save.
            timeout: Wait time for an element to be clickable.
        """
        self.log.action(f"Looking for uploaded software file: {file_to_update}")

        file_link_locator = (
            By.XPATH,
            f"//a[@class='packageNameTitle' and normalize-space(text())='{file_to_update}']"
        )
        file_element = self.base_page.wait_for_element_to_be_clickable(file_link_locator, timeout=timeout)
        file_element.click()

        self.base_page.take_screenshot(screenshot_name)
        self.log.verification(f"Selected software '{file_to_update}'", True)
    def perform_upload_file(self, upload_dir, file_name: str) -> Path:
        """
        Combines building the file path and performing the upload.
        Returns the resolved Path object for further use.
        """
        file_path = self.build_upload_path(upload_dir, file_name, self.log)
        self.log.action(f"Uploading file: '{file_path.name}'")
        self.upload_page.perform_upload(str(file_path))
        return file_path
    def perform_upload_file_usg(self, upload_dir, file_name: str) -> Path:
        """
        Combines building the file path and performing the upload.
        Returns the resolved Path object for further use.
        """
        file_path = self.build_upload_path(upload_dir, file_name, self.log)
        self.log.action(f"Uploading file: '{file_path.name}'")
        self.upload_page.perform_upload_usg(str(file_path))
        return file_path
    def verify_toast(self, expected_substring: str, timeout: int = 10):
        """Wait for toast and check it contains the expected text."""
        try:
            toast_text = self.upload_page.wait_for_toast(timeout=timeout)
            self.base_page.take_screenshot("STS06-14")
            ok = expected_substring.lower() in (toast_text or "").lower()
            self.log.verification(f"Toast contains '{expected_substring}'", ok)
            assert ok, f"Toast was '{toast_text}' but expected '{expected_substring}'"
        except Exception as e:
            ts = int(time.time())
            self.driver.save_screenshot(f"toast_failed_{ts}.png")
            with open(f"toast_failed_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(self.driver.page_source)
            self.log.error(f"Toast verification failed: {e}")
            raise

    def wait_for_toast_to_disappear(self, timeout=10):
        try:
            self.wait_for_element_to_disappear(self.TOAST, timeout=timeout)
        except Exception:
            pass
    def wait_for_uploaded_name_with_fallback(self, expected_name: str, list_timeout: int,
                                             fallback_func) -> str:
        """
        Wait for the uploaded file name via the page object, then fallback to a driver-based search.
        Returns the found text (not strictly equal) or raises TimeoutException with diagnostics.
        """
        try:
            try:
                # Some page objects accept a named expected_name parameter
                return self.upload_page.wait_for_uploaded_file_name(expected_name=expected_name, timeout=list_timeout)
            except TypeError:
                # Others accept it as the first positional argument
                return self.upload_page.wait_for_uploaded_file_name(expected_name, timeout=list_timeout)
        except TimeoutException:
            self.log.warning("Primary wait_for_uploaded_file_name timed out; trying fallback search.")
            return fallback_func(self.driver, expected_name, timeout=list_timeout, log=self.log)

    def normalize_and_assert_filename(self,found_text: Optional[str], expected_name: str,) -> None:
        """
        Check that found_text and expected_name loosely match (containment either direction).
        Save diagnostics and raise TimeoutException if not found.
        """
        if found_text:
            found_stripped = found_text.strip()
            expected_stripped = expected_name.strip()
            ok = (expected_stripped in found_stripped) or (found_stripped in expected_stripped)
            self.log.verification(f"Uploaded file name in the list (found) is '{found_text}'", ok)
            assert ok, (
                f"File name in list was '{found_text}' but expected to contain '{expected_name}'"
            )
            return

        # Diagnostics if not found
        ts = int(time.time())
        try:
            self.driver.save_screenshot(f"upload_file_not_found_{ts}.png")
            with open(f"upload_file_not_found_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(self.driver.page_source)
        except Exception:
            pass
        raise TimeoutException(
            f"Uploaded file name '{expected_name}' not found in UI. Diagnostics saved."
        )

    def click_download_for_filename(driver, base_page, file_name: str, log) -> None:
        """
        Attempt to locate the row containing file_name and click a download button within it.
        Falls back to a global button search if row cannot be located.
        Rises on failure after saving diagnostics.
        """
        escaped = file_name.replace("'", "\\'")
        possible_row_xpaths = [
            f"//tr[td[contains(normalize-space(.), '{escaped}')]]",
            f"//tr[.//a[contains(normalize-space(.), '{escaped}')]]",
            f"//div[contains(@class,'package-list')]//div[contains(., '{escaped}')]",
            f"//*[contains(normalize-space(.), '{escaped}') and (name() = 'li' or name() = 'div' or name() = 'tr')]",
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
            log.warning(
                "Could not locate the row containing the uploaded file; attempting global download button search.")
            try:
                download_button = driver.find_element(
                    By.XPATH,
                    f"//button[contains(@onclick, 'clickDownload') and contains(., '{escaped}')]",
                )
                download_button.click()
                return
            except Exception as e:
                log.error(f"Could not find download button via fallback: {e}")
                ts = int(time.time())
                try:
                    driver.save_screenshot(f"download_button_not_found_{ts}.png")
                    with open(f"download_button_not_found_{ts}.html", "w", encoding="utf-8") as fh:
                        fh.write(driver.page_source)
                except Exception:
                    pass
                raise

        # Search for a download control inside the row
        try:
            download_button = None

            # 1) Button with onclick handler
            try:
                candidate = row.find_element(By.XPATH, ".//button[contains(@onclick, 'clickDownload')]")
                if candidate and candidate.is_displayed():
                    download_button = candidate
            except Exception:
                pass

            # 2) Button with common download classes
            if not download_button:
                try:
                    candidate = row.find_element(By.XPATH,
                                                 ".//button[contains(@class,'download') or contains(@class,'download-btn')]")
                    if candidate and candidate.is_displayed():
                        download_button = candidate
                except Exception:
                    pass

            # 3) Anchor with download href/class
            if not download_button:
                try:
                    candidate = row.find_element(By.XPATH,
                                                 ".//a[contains(@href, 'download') or contains(@class,'download')]")
                    if candidate and candidate.is_displayed():
                        download_button = candidate
                except Exception:
                    pass

            # 4) CSS-based lookup
            if not download_button:
                try:
                    candidate = row.find_element(By.CSS_SELECTOR, "button.download, button.download-btn, a.download")
                    if candidate and candidate.is_displayed():
                        download_button = candidate
                except Exception:
                    pass

            # 5) Any button fallback
            if not download_button:
                try:
                    download_button = row.find_element(By.TAG_NAME, "button")
                except Exception:
                    download_button = None

            if not download_button:
                ts = int(time.time())
                try:
                    driver.save_screenshot(f"download_button_missing_in_row_{ts}.png")
                    with open(f"download_button_missing_in_row_{ts}.html", "w", encoding="utf-8") as fh:
                        fh.write(row.get_attribute("outerHTML"))
                except Exception:
                    pass
                raise NoSuchElementException("No download button found inside the row.")

            log.action(f"Clicking download button for file: '{file_name}'")
            download_button.click()
            base_page.wait_for_seconds(3)
            log.verification(f"Download initiated for file: '{file_name}'", True)
        except Exception as e:
            log.error(f"Download from row failed: {e}")
            raise

    def _xpath_literal(s: str) -> str:
        """Safely wrap any string as an XPath string literal, even if it contains both quotes."""
        if "'" not in s:
            return f"'{s}'"
        if '"' not in s:
            return f'"{s}"'
        parts = s.split("'")
        return "concat(" + ", ".join([f"'{p}'" for p in parts[:-1]] + [f"'{parts[-1]}'"]) + ")"

    def download_uploaded_file(self, file_name: str, wait_seconds: int = 3) -> None:
        """
        Attempts to locate the uploaded file row and click its download button.
        Falls back to a global button search if row not found.
        Raises an exception if download initiation fails.
        """
        self.log.step("Download the uploaded file before sign-out")

        try:
            escaped = file_name.replace("'", "\\'")
            possible_row_xpaths = [
                f"//tr[td[contains(normalize-space(.), '{escaped}')]]",
                f"//tr[.//a[contains(normalize-space(.), '{escaped}')]]",
                f"//div[contains(@class,'package-list')]//div[contains(., '{escaped}')]",
                f"//*[contains(normalize-space(.), '{escaped}') and (name() = 'li' or name() = 'div' or name() = 'tr')]",
            ]

            row = None
            for xp in possible_row_xpaths:
                try:
                    row = self.driver.find_element(By.XPATH, xp)
                    if row and row.is_displayed():
                        break
                except NoSuchElementException:
                    row = None
                    continue

            if not row:
                self.log.warning(
                    "Could not locate the row containing the uploaded file; attempting global download button search.")
                try:
                    download_button = self.driver.find_element(
                        By.XPATH,
                        f"//button[contains(@onclick, 'clickDownload') and contains(., '{escaped}')]"
                    )
                    download_button.click()
                    self.base_page.wait_for_seconds(2)
                    self.base_page.take_screenshot("STS06-15")
                    self.base_page.wait_for_seconds(wait_seconds)
                    self.log.verification(f"Download initiated for file: '{file_name}'", True)
                    return
                except Exception as e:
                    self.log.error(f"Could not find download button via fallback: {e}")
                    ts = int(time.time())
                    self.driver.save_screenshot(f"download_button_not_found_{ts}.png")
                    with open(f"download_button_not_found_{ts}.html", "w", encoding="utf-8") as fh:
                        fh.write(self.driver.page_source)
                    raise

            # Search for a download control inside the row
            selectors = [
                (By.XPATH, ".//button[contains(@onclick, 'clickDownload')]"),
                (By.XPATH, ".//button[contains(@class,'download') or contains(@class,'download-btn')]"),
                (By.XPATH, ".//a[contains(@href, 'download') or contains(@class,'download')]"),
                (By.CSS_SELECTOR, "button.download, button.download-btn, a.download"),
            ]

            download_button = None
            for sel in selectors:
                try:
                    candidate = row.find_element(*sel)
                    if candidate and candidate.is_displayed():
                        download_button = candidate
                        break
                except Exception:
                    continue

            if not download_button:
                try:
                    download_button = row.find_element(By.TAG_NAME, "button")
                except Exception:
                    download_button = None

            if not download_button:
                ts = int(time.time())
                self.driver.save_screenshot(f"download_button_missing_in_row_{ts}.png")
                with open(f"download_button_missing_in_row_{ts}.html", "w", encoding="utf-8") as fh:
                    fh.write(row.get_attribute("outerHTML"))
                raise NoSuchElementException("No download button found inside the row.")

            self.log.action(f"Clicking download button for file: '{file_name}'")
            download_button.click()
            #self.base_page.take_screenshot("STS06-15")
            self.base_page.wait_for_seconds(2)
            self.base_page.take_screenshot("STS06-15")
            self.log.verification(f"Download initiated for file: '{file_name}'", True)
            self.base_page.take_screenshot("STS06-16")
            self.base_page.wait_for_seconds(2)
            self.base_page.take_screenshot("STS06-17")


        except Exception as e:
            self.log.error(f"Failed while initiating download: {e}")
            raise


