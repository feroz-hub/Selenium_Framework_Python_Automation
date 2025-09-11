from pathlib import Path
import time
from typing import Optional

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

# These helpers centralize common upload verification logic to keep tests DRY.


def build_upload_path(upload_dir, file_name: str, log) -> Path:
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


def verify_toast(upload_page, base_page, driver, expected_substring: str, timeout: int, log) -> None:
    """
    Wait for a toast via the page object and ensure it contains expected_substring.
    Captures diagnostics on failure and re-raises.
    """
    try:
        toast_text = upload_page.wait_for_toast(timeout=timeout)
        base_page.take_screenshot("ST06-12")
        ok = expected_substring in (toast_text or "")
        log.verification(f"Toast message contains '{expected_substring}'", ok)
        assert ok, f"Toast message was '{toast_text}' but expected to contain '{expected_substring}'"
    except Exception as e:
        log.error(f"Failed to read toast: {e}")
        ts = int(time.time())
        try:
            driver.save_screenshot(f"toast_failed_{ts}.png")
            with open(f"toast_failed_{ts}.html", "w", encoding="utf-8") as fh:
                fh.write(driver.page_source)
        except Exception:
            pass
        raise


def wait_for_uploaded_name_with_fallback(upload_page, driver, expected_name: str, list_timeout: int, log,
                                          fallback_func) -> str:
    """
    Wait for the uploaded file name via the page object, then fallback to a driver-based search.
    Returns the found text (not strictly equal) or raises TimeoutException with diagnostics.
    """
    try:
        try:
            # Some page objects accept a named expected_name parameter
            return upload_page.wait_for_uploaded_file_name(expected_name=expected_name, timeout=list_timeout)
        except TypeError:
            # Others accept it as the first positional argument
            return upload_page.wait_for_uploaded_file_name(expected_name, timeout=list_timeout)
    except TimeoutException:
        log.warning("Primary wait_for_uploaded_file_name timed out; trying fallback search.")
        return fallback_func(driver, expected_name, timeout=list_timeout, log=log)


def normalize_and_assert_filename(found_text: Optional[str], expected_name: str, driver, base_page, log) -> None:
    """
    Check that found_text and expected_name loosely match (containment either direction).
    Save diagnostics and raise TimeoutException if not found.
    """
    if found_text:
        found_stripped = found_text.strip()
        expected_stripped = expected_name.strip()
        ok = (expected_stripped in found_stripped) or (found_stripped in expected_stripped)
        log.verification(f"Uploaded file name in the list (found) is '{found_text}'", ok)
        assert ok, (
            f"File name in list was '{found_text}' but expected to contain '{expected_name}'"
        )
        return

    # Diagnostics if not found
    ts = int(time.time())
    try:
        driver.save_screenshot(f"upload_file_not_found_{ts}.png")
        with open(f"upload_file_not_found_{ts}.html", "w", encoding="utf-8") as fh:
            fh.write(driver.page_source)
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
        log.warning("Could not locate the row containing the uploaded file; attempting global download button search.")
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
                candidate = row.find_element(By.XPATH, ".//button[contains(@class,'download') or contains(@class,'download-btn')]")
                if candidate and candidate.is_displayed():
                    download_button = candidate
            except Exception:
                pass

        # 3) Anchor with download href/class
        if not download_button:
            try:
                candidate = row.find_element(By.XPATH, ".//a[contains(@href, 'download') or contains(@class,'download')]")
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
