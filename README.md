# Selenium Framework for Olympus Medical Software Delivery (OMSD)

Automated end-to-end UI tests for the Olympus Medical Software Delivery web application using Selenium WebDriver and Pytest. The suite covers login, upload, and software management flows with page objects and reusable utilities.

> Note: This repository currently contains sample/staging credentials in config.yaml that should never be used in production. See Security and secrets section below for remediation steps.

## Tech stack
- Language: Python (version TBD — see TODO)
- Test framework: Pytest
- UI automation: Selenium WebDriver
- Driver management: webdriver-manager (macOS paths auto-managed; Windows paths configurable)
- Configuration: YAML (config.yaml)
- Reporting: pytest-html (self‑contained HTML report)
- Logging & screenshots: Custom utilities under omsd_automation/utils and screenshots directory
- Package manager: pip (requirement.txt)

## Project structure
- config.yaml — environment, base_url, browser options, user credentials, timeouts, driver paths
- requirement.txt — Python dependencies
- pytest.ini — Pytest options, HTML report path, markers
- omsd_automation/
  - pages/ — Page Object Model classes (Base, Login, Home, Software, Upload)
  - tests/ — Tests, logs/, reports/, and test_config constants
  - utils/ — Config reader, browser utils, logger, data loader, element helpers, login/logout helpers, screenshot utils
  - uploads/ — Sample upload payloads
  - downloads/ — Download targets used by tests
  - screenshots/ — Captured images
- data/ — Example test data CSV
- LICENSE — Project license

## Requirements
- Python 3.x (exact version TBD — see TODO)
- Supported browsers: Chrome (primary), Firefox, Edge, Safari (macOS only)
- WebDrivers:
  - Chrome: On macOS auto-installed via webdriver-manager. On Windows, path configured via config.yaml: chrome_driver_path.
  - Firefox/Edge: Placeholders exist in conftest.py for Windows paths. See Setup section to configure.
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
     - environments.<env>.users: credentials per role (software_uploader, distribution_manager)
     - base_url: top-level base URL fallback (kept for backward compatibility)
     - browser: chrome | edge | safari | firefox
     - headless: true|false
     - implicit_wait, explicit_wait
     - chrome_driver_path: Path to your local ChromeDriver (Windows). Example:
       - C:\\Tools\\chromedriver\\chromedriver.exe
   - Windows (Chrome): Ensure chrome_driver_path points to a valid ChromeDriver matching your Chrome version.
   - Windows (Firefox/Edge): conftest.py contains placeholder paths (r"path_to_your_local_geckodriver.exe" / edgedriver.exe). Update these if you plan to run Firefox/Edge.
   - macOS: Chrome/Firefox/Edge drivers are resolved via webdriver-manager when using those browsers.

5. Optional: Remove secrets from config.yaml (recommended)
   - Replace plaintext usernames/passwords with environment variables (see Security and secrets).

## Running tests
Pytest is configured via pytest.ini to generate an HTML report at reports/report.html.

- Run all tests
  - pytest

- Run with verbose output and HTML report (already default via pytest.ini)
  - pytest -v

- Run only login tests (using marker)
  - pytest -m login

- Specify a browser via config.yaml (preferred) or override via environment variable/TODO hook
  - Edit browser: in config.yaml (e.g., chrome, firefox)

- Run a single test file
  - pytest omsd_automation/tests/test_login.py -v

- Generate a fresh report
  - pytest --html=reports/report.html --self-contained-html

Test artifacts
- HTML Report: reports/report.html (also under omsd_automation/tests/reports/report.html from recent runs)
- Logs: omsd_automation/tests/logs
- Screenshots: omsd_automation/screenshots
- Downloads: omsd_automation/downloads

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
      - software_uploader.username / password
      - distribution_manager.username / password
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
- conftest.py provisions the WebDriver based on config.yaml (browser, headless, driver paths), maximizes window, sets implicit wait, and navigates to base_url.
- Fixtures construct Page Objects: BasePage, LoginPage, SoftwarePage, UploadPage, HomePage.
- authenticated_session fixture logs in before each test and logs out after.
- pytest.ini adds default options: -v --tb=short --html=reports/report.html --self-contained-html and defines markers: login, logout, smoke.
- tests use constants from omsd_automation/tests/test_config.py for shared paths and timeouts.

## Security and secrets
- WARNING: config.yaml currently contains plaintext credentials for staging and placeholder prod. Do not commit real credentials.
- Immediate actions recommended:
  - Replace credentials with environment variable references; keep only non-sensitive defaults.
  - Add config.yaml.example without secrets and document required keys.
  - If this repo is public, rotate any exposed credentials immediately.

## Troubleshooting
- ChromeDriver version mismatch on Windows
  - Update chrome_driver_path to point to a driver matching your installed Chrome version.
- Downloads not saving to the expected folder
  - See Chrome prefs in conftest.py; downloads default to omsd_automation/tests/downloads.
- Unsupported browser error
  - Ensure browser in config.yaml is one of chrome|firefox|edge|safari (safari only on macOS).
- Report not generated
  - Ensure pytest-html is installed and pytest.ini is present.

## Tests
- Location: omsd_automation/tests
- Example suites: test_login.py, test_logout.py, test_software_upload.py, product-specific tests (ESG/USG 410)
- Markers: login, logout, smoke
- Run examples:
  - pytest -m smoke
  - pytest omsd_automation/tests/test_ESG_410_software_upload.py -v

## License
This project is licensed under the terms of the LICENSE file included at the repository root. See LICENSE for details.

## TODOs
- Pin and document the exact supported Python version(s).
- Add environment variable overrides in config_reader.py and provide config.yaml.example.
- Unify driver management to use webdriver-manager across platforms (remove hardcoded Windows paths).
- Validate Linux support and document any OS-specific caveats.
- Add CI workflow (e.g., GitHub Actions) to run headless tests and publish HTML report as an artifact.
