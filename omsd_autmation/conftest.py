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
from .utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture
def driver():
    browser = Config.get("browser", "chrome").lower()
    headless = Config.get("headless", False)

    logger.info(f"🚀 Starting browser: {browser}, Headless: {headless}")
    chromedriver_path = 'C:\\Users\\ferozebasha.s\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(
            #service=ChromeService(ChromeDriverManager().install()),
            service=ChromeService(executable_path=chromedriver_path),
            options=options,
        )

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )

    elif browser == "edge":

        options = webdriver.Edge()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=options,
        )

    elif browser == "safari":
        driver = SafariDriver()

    else:
        logger.error(f"❌ Unsupported browser: {browser}")
        raise ValueError(f"❌ Unsupported browser: {browser}")

    driver.maximize_window()
    implicit_wait = Config.get("implicit_wait", 5)
    driver.implicitly_wait(implicit_wait)

    base_url = Config.get("base_url")
    logger.info(f"🌐 Navigating to: {base_url}")
    driver.get(base_url)

    yield driver

    logger.info("🛑 Quitting browser session")
    driver.quit()
