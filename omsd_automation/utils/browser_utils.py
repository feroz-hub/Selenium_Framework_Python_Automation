from omsd_automation.tests import test_config as C


def get_download_prefs():
    """
    Returns a dictionary of common download preferences for browsers.
    """
    {
        "download.default_directory": str(C.DOWNLOAD_DIR.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
