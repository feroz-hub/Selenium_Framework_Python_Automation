from selenium.webdriver.common.by import By


# page_url = https://softwaredelivery-stg3.olympusmedical.com
class Page(object):
    def __init__(self, driver):
        self.driver = driver

    def input_sign_name(self):
        return self.driver.find_element(By.CSS_SELECTOR, "input[aria-label^='Email']")

    def input_sign_name2(self):
        return self.driver.find_element(By.ID, "signInName")

    def button_onetrust_accept_handler(self):
        return self.driver.find_element(By.ID, "onetrust-accept-btn-handler")

    def h6_confirm_title(self):
        return self.driver.find_element(By.ID, "confirmTitle")
