from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class HomePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def sign_out(self):
        # self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        self.wait.until(EC.element_to_be_clickable((By.ID, "sysUserDisplayName"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Sign Out']/parent::a"))).click()