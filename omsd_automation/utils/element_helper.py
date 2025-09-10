import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------
# Helper: fallback name search with multiple xpaths and diagnostics

# ----------------------

def fallback_find_uploaded_name(driver, expected_name, timeout=60, poll_interval=1.0, log=None):
    """
    Tries multiple XPath strategies to find an element that contains the expected_name.
    Returns the element text if found, otherwise raises TimeoutException after saving diagnostics.
    """
    end = time.time() + timeout
    escaped = expected_name.replace("'", "\\'")

    xpaths = [
        # exact cell match
        f"//table//td[normalize-space(text()) = '{escaped}']",
        # contains in table cell or anchor
        f"//table//td[contains(normalize-space(.), '{escaped}')]",
        f"//tr//a[contains(normalize-space(.), '{escaped}')]",
        # common package-list container
        f"//div[contains(@class,'package-list')]//span[contains(normalize-space(.), '{escaped}')]",
        f"//div[contains(@class,'package-list')]//div[contains(., '{escaped}')]",
        # toast fallback
        f"//div[contains(@class,'toast') and contains(., '{escaped}')]",
        # global fallback: any visible element that contains the text
        f"//*[contains(normalize-space(.), '{escaped}')]"
    ]

    while time.time() < end:
        # optionally wait briefly for spinners to disappear
        try:
            WebDriverWait(driver, 2).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner, .overlay")))
        except Exception:
            pass

        for xp in xpaths:
            try:
                elem = driver.find_element(By.XPATH, xp)
                if elem and elem.is_displayed():
                    text = elem.text.strip()
                    if text:
                        if log:
                            log.debug(f"Found element by xpath '{xp}': '{text[:120]}'")
                        return text
            except Exception:
                continue

        time.sleep(poll_interval)

    # Save diagnostics before raising
    ts = int(time.time())
    try:
        driver.save_screenshot(f"fallback_search_timeout_{ts}.png")
        with open(f"fallback_search_timeout_{ts}.html", "w", encoding="utf-8") as fh:
            fh.write(driver.page_source)
    except Exception:
        pass

    raise TimeoutException(f"Timeout while searching for uploaded file name '{expected_name}'. "
                           f"Diagnostics saved to current directory.")
