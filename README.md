# Selenium Framework for Medical Software Delivery (MSD)

Automated end-to-end UI tests for the Medical Software Delivery web application using Selenium WebDriver and Pytest. The suite covers login, upload, and software management flows with page objects and reusable utilities.

> Note: This repository currently contains sample/staging credentials in config.yaml that should never be used in production. See Security and secrets section below for remediation steps.

## Tech stack
- Language: Python (version TBD — see TODO)
- Test framework: Pytest
- UI automation: Selenium WebDriver
- Driver management: webdriver-manager for macOS; explicit driver paths for Windows via config.yaml
- Configuration: YAML (config.yaml)
- Reporting: pytest-html (self‑contained HTML report) and Allure (results only)
- Logging & screenshots: Custom utilities under omsd_automation/utils; artifacts saved under project-level logs/ and screenshots/
- Package manager: pip (requirement.txt)

## Project structure
- config.yaml — environment, base_url, browser options, user credentials, timeouts, driver paths
- requirement.txt — Python dependencies
- pytest.ini — Pytest options, report paths, markers
- omsd_automation/
  - pages/ — Page Object Model classes (Base, Login, Home, Software, Upload, etc.)
  - utils/ — Config reader, browser utils, logger, data loader, element helpers, login/logout helpers, screenshot utils
- tests/ — Test suites and fixtures (conftest.py, login/, software/, etc.)
- uploads/ — Sample upload payloads
- downloads/ — Download targets used by tests
- screenshots/ — Captured images
- data/ — Example test data CSV
- reports/ — Test reports (pytest HTML, Allure results)
- logs/ — Run logs
- LICENSE — Project license

## Requirements
- Python 3.x (exact version TBD — see TODO)
- Supported browsers: Chrome (primary), Firefox, Edge, Safari (macOS only)
- WebDrivers:
  - Chrome: On macOS auto-installed via webdriver-manager. On Windows, path configured via config.yaml: chrome_driver_path.
  - Firefox/Edge: Placeholders exist in tests/conftest.py for Windows paths. Update these if you plan to run Firefox/Edge.
- OS: Windows, macOS (Linux not validated — TODO)

## Setup
1. Clone the repository
   - git clone <repo-url>
   - cd Selenium_Framework_Python_Automation

2. Create and activate a virtual environment
   - Python venv (example):
     - Windows: python -m venv .venv && .\.venv\Scripts\activate
     - macOS: python3 -m venv .venv && source .venv/bin/activate

3. Install dependencies
   - pip install -r requirement.txt

4. Configure environments and drivers
   - Open config.yaml and review:
     - env: active environment key (staging or prod)
     - environments.<env>.base_url: target URL
     - environments.<env>.users: credentials per role (software_uploader, distribution_manager, etc.)
     - base_url: top-level base URL fallback (kept for backward compatibility)
     - browser: chrome | edge | safari | firefox
     - headless: true|false
     - implicit_wait, explicit_wait
     - chrome_driver_path (Windows): Path to your local ChromeDriver. Example:
       - C:\\Tools\\chromedriver\\chromedriver.exe
   - Windows (Chrome): Ensure chrome_driver_path points to a valid ChromeDriver matching your Chrome version.
   - Windows (Firefox/Edge): tests/conftest.py contains placeholder paths (r"path_to_your_local_geckodriver.exe" / r"path_to_your_local_edgedriver.exe"). Update these if you plan to run Firefox/Edge.
   - macOS: Chrome/Firefox/Edge drivers are resolved via webdriver-manager when using those browsers.

5. Optional: Remove secrets from config.yaml (recommended)
   - Replace plaintext usernames/passwords with environment variables (see Security and secrets).

## Running tests
Pytest is configured via pytest.ini to generate:
- HTML report at reports/pytest/report.html
- Allure results at reports/allure-results

- Run all tests
  - pytest

- Run with verbose output
  - pytest -v

- Run a specific test file
  - pytest tests/login/test_login.py -v

- Run smoke or regression sets (see markers)
  - pytest -m smoke
  - pytest -m regression

- Regenerate HTML report manually (if needed)
  - pytest --html=reports/pytest/report.html --self-contained-html

Test artifacts
- HTML Report: reports/pytest/report.html
- Allure results: reports/allure-results
- Logs: logs/
- Screenshots: screenshots/
- Downloads: downloads/

## Scripts
No custom CLI scripts are defined. Use pytest commands as shown above.

## Configuration and environment variables
Configuration is primarily loaded from config.yaml via omsd_automation.utils.config_reader.Config. Active environment is set by the top-level key env.

Important keys in config.yaml
- env: active environment name (e.g., staging, prod)
- environments:
  - <env>:
    - base_url: string
    - users:
      - software_uploader.username / password, etc.
- base_url (top-level): fallback URL (legacy)
- browser: chrome | edge | safari | firefox
- headless: boolean
- implicit_wait, explicit_wait: integers (seconds)
- chrome_driver_path: Windows path to chromedriver.exe
- tests.login: example credentials and expectations (for sample data-driven tests)
- upload_files.esg_410: sample upload directory name

Recommended environment variables (not implemented yet — TODO)
- OMSD_ENV: active environment override (maps to env)
- OMSD_SOFTWARE_UPLOADER_USERNAME / OMSD_SOFTWARE_UPLOADER_PASSWORD
- OMSD_DISTRIBUTION_MANAGER_USERNAME / OMSD_DISTRIBUTION_MANAGER_PASSWORD
- OMSD_BASE_URL, OMSD_BROWSER, OMSD_HEADLESS

These would require small code changes in config_reader.py to read from os.environ before falling back to YAML.

## How it works
- tests/conftest.py provisions the WebDriver based on config.yaml (browser, headless, driver paths), maximizes window, sets implicit wait, and navigates to base_url. It also sets browser download locations to the project downloads/ folder.
- Fixtures construct Page Objects: BasePage, LoginPage, SoftwarePage, UploadPage, HomePage, etc.
- authenticated_session fixture logs in before each test and logs out after.
- pytest.ini adds default options including parallelization (-n auto), HTML report path, Allure results path, and defines markers: smoke, regression, esg.
- tests use constants from tests/test_config.py for shared paths and timeouts.

## Security and secrets
- WARNING: config.yaml currently contains plaintext credentials for staging and placeholder prod. Do not commit real credentials.
- Immediate actions recommended:
  - Replace credentials with environment variable references; keep only non-sensitive defaults.
  - Add config.yaml.example without secrets and document required keys.
  - If this repo is public, rotate any exposed credentials immediately.

## Screenshots: how to use them

Where screenshots are saved
- Base directory: screenshots/ (configured by tests/test_config.py as SCREENSHOTS_DIR)
- Organized automatically by product and test case when possible, e.g.:
  - screenshots/ESG-410/upload_software/ESG-410_upload_software_ST06-11_20250101_121314.png
- If product or test case cannot be detected, screenshots are saved directly under screenshots/.

Taking screenshots in tests (recommended)
- Using BasePage (most convenient):
  - path = base_page.take_screenshot("ST07-03_SelectedSoftware")
  - log.screenshot(path)  # optional: record the saved path in the test log
- BasePage.take_screenshot uses the organized saver and returns the absolute file path.

Taking screenshots directly (advanced)
- from omsd_automation.utils.screenshot import take_screenshot
- Auto-detect product/test case from the call stack:
  - take_screenshot(driver, "after_login")
- Manually override product and/or test case:
  - take_screenshot(driver, "grid_open", product="ESG-410", test_case="software_upload")
- Add an extra subfolder for finer grouping (e.g., setup/teardown):
  - take_screenshot(driver, "before_toggle", extra_subfolder="setup")

Filename format
- <product>_<test_case>_<step>_<timestamp>.png (prefixes omitted if unknown)
- Invalid characters are sanitized. If step includes .png, it is stripped.

Tips
- Pair screenshots with logger entries for easier triage: log.screenshot(path)
- Look in the run log (logs/testrun_*.log) for the exact saved path — the utility prints it as well.

## Troubleshooting
- ChromeDriver version mismatch on Windows
  - Update chrome_driver_path to point to a driver matching your installed Chrome version.
- Downloads not saving to the expected folder
  - See Chrome/Edge/Firefox prefs in tests/conftest.py; downloads default to downloads/.
- Unsupported browser error
  - Ensure browser in config.yaml is one of chrome|firefox|edge|safari (safari only on macOS).
- Report not generated
  - Ensure pytest-html is installed and pytest.ini is present.

## Tests
- Location: tests/
- Example suites: tests/login/test_login.py, tests/login/test_logout.py, tests/software/esg/test_ESG_410_software_upload.py, product-specific tests (ESG/USG 410)
- Markers: smoke, regression, esg
- Run examples:
  - pytest -m smoke
  - pytest tests/software/esg/test_ESG_410_software_upload.py -v

## License
This project is licensed under the terms of the LICENSE file included at the repository root. See LICENSE for details.

## TODOs
- Pin and document the exact supported Python version(s).
- Add environment variable overrides in config_reader.py and provide config.yaml.example.
- Unify driver management to use webdriver-manager across platforms (remove hardcoded Windows paths).
- Validate Linux support and document any OS-specific caveats.
- Add CI workflow (e.g., GitHub Actions) to run headless tests and publish HTML report as an artifact.
