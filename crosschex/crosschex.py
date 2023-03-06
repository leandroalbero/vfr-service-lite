from __future__ import annotations

import json
import os
import threading
from typing import Any, List

import requests
from requests.adapters import HTTPAdapter

API_EMPLOYEE_SEARCH = "employee/grid"
API_EMPLOYEE_FACE_UPDATE = "employee/attendance/face/update"
API_USER_LOGIN = "user/login"
API_LIST_COMPANY = "company/list"
API_SELECT_COMPANY = "company/select"
SETTINGS_DIR = os.path.abspath('..')  # This directory
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


class CrossChexCloudAdapter(HTTPAdapter):
    __instance = None
    __lock = threading.Lock()

    # Singleton pattern
    def __new__(cls, *args: Any, **kwargs: Any) -> CrossChexCloudAdapter:
        if not cls.__instance:
            with cls.__lock:
                # Double check because if multithreading another thread
                # could have created the instance
                if not cls.__instance:
                    cls.__instance = super().__new__(cls, *args, **kwargs)
                    cls.__instance._authorize()
                    cls.__instance._list_company()
                    cls.__instance._select_company()

        return cls.__instance

    @property
    def headers(self) -> dict:
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "x-api-version": "2.0",
            "x-token": self.token,
        }

    def _authorize(self) -> None:
        auth_header = {
            "content-type": "application/json",
            "accept": "application/json",
            "x-api-version": "2.0",
        }
        payload = {
            "email": ACCOUNT_EMAIL,
            "password": ACCOUNT_PASSWORD,
        }
        url = f"{API_URL}/{API_USER_LOGIN}"
        response = requests.post(
            url=url,
            headers=auth_header,
            data=json.dumps(payload),
            timeout=API_TIMEOUT,
        )
        self.token = response.json()["data"]["token"]  # JWT token
        self.company_id = int(response.json()["data"]["company_id"])
        print(f"Anviz API Cloud: user token created: {ACCOUNT_NAME}")

    def _list_company(self) -> None:
        payload = {}
        url = f"{API_URL}/{API_LIST_COMPANY}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=API_TIMEOUT,
        )
        self.company_cloud_id = response.json()["data"][0]["id"]  # company cloud id
        print(f"Anviz API Cloud: company list: {self.company_cloud_id}")

    def _select_company(self) -> None:
        payload = {"id": self.company_cloud_id}
        url = f"{API_URL}/{API_SELECT_COMPANY}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=API_TIMEOUT,
        )
        # update token when select company
        self.token = response.json()["data"]["token"]  # JWT token
        print(f"Anviz API Cloud: company select: {self.company_id}")

    def get(self, path: str, **kwargs: Any) -> List:
        raise NotImplementedError

    def post(self, path: str, body: dict = {}) -> dict:
        url = f"{API_URL}/{path}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(body),
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def post_form(self, path: str, fields: dict = {}, files: dict = {}) -> dict:
        headers = {
            "accept": "application/json",
            "x-api-version": "2.0",
            "x-token": self.token,
        }
        url = f"{API_URL}/{path}"
        response = requests.post(
            url=url,
            headers=headers,
            data=fields,
            files=files,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def put(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError

    def patch(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError

    def delete(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError
