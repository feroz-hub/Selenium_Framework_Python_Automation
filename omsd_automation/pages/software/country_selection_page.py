from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

class CountrySelectionPage:
    """
    Page Object Model for BC (Business Categories) and Country selection.
    Supports individual + bulk (all) selections.
    """



    # --- Package Type Radio Buttons ---
    PACKAGE_TYPE_EXECUTERS_AND_CUSTOMERS = (
        By.XPATH, "//label[contains(., 'Device Update Executers and Customers')]/input"
    )
    PACKAGE_TYPE_EXECUTERS_ONLY = (
        By.XPATH, "//label[contains(., 'Device Update Executers only')]/input"
    )

    # --- Generic dynamic locators ---
    @staticmethod
    def bc_checkbox_by_code(code: str):
        return (
            By.XPATH,
            f"//input[@class='bc']/following-sibling::span//span[normalize-space(text())='{code}']"
        )

    @staticmethod
    def country_checkbox_by_name(name: str):
        return (
            By.XPATH,
            f"//span[@class='omsd-checkbox-label' and normalize-space(text())='{name}']/preceding-sibling::input[@type='checkbox']"
        )

    @staticmethod
    def bc_checkbox_label(code: str):
        return (
            By.XPATH,
            f"//label[.//span[normalize-space(text())='{code}']]//span[@class='checkbox-icon']"
        )

    @staticmethod
    def country_checkbox_label(name: str):
        return (
            By.XPATH,
            f"//label[.//span[normalize-space(text())='{name}']]//span[@class='checkbox-icon']"
        )

    ALL_BC_LABELS = (By.CSS_SELECTOR, "label[for^='bc'] span.checkbox-icon")
    ALL_COUNTRY_LABELS = (By.CSS_SELECTOR, "label[for^='country'] span.checkbox-icon")

    # --- Bulk selection methods ---
    def __init__(self, driver: WebDriver, log):
        self.driver = driver
        self.log = log

    def select_all_bcs(self):
        """Click all BC visible labels instead of hidden inputs."""
        bcs = self.driver.find_elements(*self.ALL_BC_LABELS)
        for bc in bcs:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bc)
            if bc.is_displayed():
                bc.click()
        self.log.action(f"Selected ALL {len(bcs)} BCs (via labels).")

    def select_all_countries(self):
        """Click all Country visible labels instead of hidden inputs."""
        countries = self.driver.find_elements(*self.ALL_COUNTRY_LABELS)
        for country in countries:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country)
            if country.is_displayed():
                country.click()
        self.log.action(f"Selected ALL {len(countries)} Countries (via labels).")
    def deselect_all_bcs(self):
        """Uncheck all BCs."""
        bcs = self.driver.find_elements(*self.ALL_BC_LABELS)
        for bc in bcs:
            if bc.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", bc)
                bc.click()
        self.log.action("Deselected all BCs.")

    def deselect_all_countries(self):
        """Uncheck all Countries."""
        countries = self.driver.find_elements(*self.ALL_COUNTRY_LABELS)
        for country in countries:
            if country.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", country)
                country.click()
        self.log.action("Deselected all Countries.")
