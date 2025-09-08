import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from .utils.config_reader import Config

# --- Load config once per test session ---
@pytest.fixture(scope="session")
def config():
    cfg = Config()
    cfg.load_config("config.yaml")
    return cfg


# --- Driver setup ---
@pytest.fixture
def driver(config):
    browser = config.get("browser.type", "chrome").lower()
    headless = config.get("browser.headless", False)
    base_url = config.get("app.base_url")
    implicit_wait = config.get("app.implicit_wait", 5)

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    elif browser == "safari":
        # SafariDriver is built into macOS (enable "Allow Remote Automation" in Safari > Develop menu)
        driver = SafariDriver()

    else:
        raise ValueError(f"❌ Unsupported browser: {browser}")

    driver.maximize_window()
    driver.implicitly_wait(Config.get("implicit_wait", 5))

    driver.get(Config.get("base_url"))

    yield driver
    driver.quit()
