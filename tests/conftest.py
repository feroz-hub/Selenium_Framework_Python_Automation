import platform
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from omsd_automation.pages.software.country_for_manual_release import CountryForManualReleasePage
from omsd_automation.pages.software.search_device_page import SearchDevicePage
from omsd_automation.pages.software.software_check import SoftwareCheckPage
from omsd_automation.utils.config_reader import Config
from omsd_automation.utils.logger import get_logger, reset_logger_state
from omsd_automation.utils.upload_flow import UploadFlow
from tests import test_config as C  # import dirs (UPLOAD_DIR, DOWNLOAD_DIR)
from omsd_automation.utils.login_utils import LoginUtils
from omsd_automation.utils.logout_utils import LogoutUtils
# Import page objects
from omsd_automation.pages.base.base_page import BasePage
from omsd_automation.pages.login_page import LoginPage
from omsd_automation.pages.software.software_page import SoftwarePage
from omsd_automation.pages.software.upload_page import UploadPage
from omsd_automation.pages.home_page import HomePage
from omsd_automation.utils.logger import setup_test_logging

# Ensure a clean logging state at the very start of the test session
reset_logger_state()
logger = get_logger(__name__)


# ----------------------------
# Driver Fixture
# ----------------------------
@pytest.fixture
def driver():
    browser = Config.get("browser", "chrome").lower()
    headless = Config.get("headless", False)
    implicit_wait = Config.get("implicit_wait", 5)
    base_url = Config.get("base_url")

    logger.info(f"🚀 Starting browser: {browser}, Headless: {headless}")
    system_os = platform.system().lower()

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            # ✅ force downloads into project downloads folder
        prefs = {
                "download.default_directory": str(C.DOWNLOAD_DIR.resolve()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
        options.add_experimental_option("prefs", prefs)

        if system_os == "darwin":
            service = ChromeService(ChromeDriverManager().install())
        else:
            chromedriver_path = Config.get("chrome_driver_path", None)

            service = ChromeService(executable_path=chromedriver_path)

        driver = webdriver.Chrome(service=service, options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)  # custom dir
        profile.set_preference("browser.download.dir", str(C.DOWNLOAD_DIR.resolve()))
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream,application/zip,application/pdf"
        )

        if system_os == "darwin":
            service = FirefoxService(GeckoDriverManager().install())
        else:
            geckodriver_path = r"path_to_your_local_geckodriver.exe"
            service = FirefoxService(executable_path=geckodriver_path)

        driver = webdriver.Firefox(service=service, options=options)

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")

        prefs = {
            "download.default_directory": str(C.DOWNLOAD_DIR.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)

        if system_os == "darwin":
            service = EdgeService(EdgeChromiumDriverManager().install())
        else:
            edgedriver_path = r"path_to_your_local_edgedriver.exe"
            service = EdgeService(executable_path=edgedriver_path)

        driver = webdriver.Edge(service=service, options=options)

    elif browser == "safari":
        if system_os != "darwin":
            raise ValueError("Safari is only supported on macOS")
        driver = webdriver.Safari()

    else:
        logger.error(f"❌ Unsupported browser: {browser}")
        raise ValueError(f"❌ Unsupported browser: {browser}")

    driver.maximize_window()
    driver.implicitly_wait(implicit_wait)
    logger.info(f"🌐 Navigating to: {base_url}")
    driver.get(base_url)

    yield driver

    logger.info("🛑 Quitting browser session")
    driver.quit()


# ----------------------------
# Page Fixtures
# ----------------------------
@pytest.fixture
def base_page(driver):
    return BasePage(driver)
@pytest.fixture
def software_check_page(driver):
    return SoftwareCheckPage(driver)

@pytest.fixture
def login_page(driver):
    return LoginPage(driver)
@pytest.fixture
def search_page(driver):
    return SearchDevicePage(driver)

@pytest.fixture
def software_page(driver):
    return SoftwarePage(driver, setup_test_logging("software_page"))


@pytest.fixture
def upload_page(driver):
    return UploadPage(driver, setup_test_logging("upload_page"))


@pytest.fixture
def home_page(driver):
    return HomePage(driver)

@pytest.fixture
def country_page(driver):
    return CountryForManualReleasePage(driver, setup_test_logging("country_page"))

@pytest.fixture
def log():
    return setup_test_logging()

# Fixture for UploadFlow
@pytest.fixture
def upload_flow(software_page,base_page, upload_page, driver):
    log = setup_test_logging()
    return UploadFlow(software_page,base_page, upload_page, driver, log)
@pytest.fixture(scope="function")
def authenticated_session(driver, request):
    """
    Pytest fixture to handle login before a test and logout after the test.
    Use like:
    @pytest.mark.parametrize("authenticated_session", ["software_uploader"], indirect=True)
    Parameters:
    - driver: WebDriver instance
    - login_page: Page object for login operations
    - base_page: Page object for base operations
    - home_page: Page object for home page operations
    - log: Logger object
    """
    # Login before test
    role = getattr(request, "param", "software_uploader")
    log = setup_test_logging(f"login_session[{role}]")
    login_page = LoginPage(driver)
    base_page = BasePage(driver)
    home_page = HomePage(driver)
    LoginUtils.login_as_role(login_page, base_page, log, driver, role)
    yield home_page
    # Logout after the test
    LogoutUtils.sign_out_user(home_page, base_page, login_page, log, driver)
