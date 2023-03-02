import os


class Config(object):
    """Base configuration."""

    SETTINGS_DIR = os.path.abspath('.')  # This directory
    APP_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, os.pardir))  # Parent dir
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))  # Parent dir
    SERVICE_NAME = os.environ.get("APP_NAME", "vfr")

    API_HOST = "eu.crosschexcloud.com"
    API_URL = f"https://{API_HOST}/api"
    API_TIMEOUT = 120
    # get token from collab secrets
    ACCOUNT_EMAIL = os.environ.get("ACCOUNT_EMAIL", "")
    ACCOUNT_PASSWORD = os.environ.get("ACCOUNT_PASSWORD", "")
    ACCOUNT_NAME = 'test'

    PATH_DOWNLOAD_JSON = f"data/downloads/{ACCOUNT_NAME}.json"
    PATH_EXPORT_CSV = f"data/exports/{ACCOUNT_NAME}.csv"

    DELAY_SECONDS = 5


def get_settings():  # type: ignore
    return Config
