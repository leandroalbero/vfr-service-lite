from __future__ import annotations

import json
import threading
from typing import Any, List

import requests
from config import get_settings
from requests.adapters import HTTPAdapter

API_EMPLOYEE_SEARCH = "employee/grid"
API_EMPLOYEE_FACE_UPDATE = "employee/attendance/face/update"
API_USER_LOGIN = "user/login"
API_LIST_COMPANY = "company/list"
API_SELECT_COMPANY = "company/select"


class CrossChexCloudAdapter(HTTPAdapter):
    __instance = None
    __lock = threading.Lock()

    # Singleton pattern
    def __new__(cls, *args: Any, **kwargs: Any) -> CrossChexCloudAdapter:
        cls.config = get_settings()
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
            "email": self.config.ACCOUNT_EMAIL,
            "password": self.config.ACCOUNT_PASSWORD,
        }
        url = f"{self.config.API_URL}/{API_USER_LOGIN}"
        response = requests.post(
            url=url,
            headers=auth_header,
            data=json.dumps(payload),
            timeout=self.config.API_TIMEOUT,
        )
        self.token = response.json()["data"]["token"]  # JWT token
        self.company_id = int(response.json()["data"]["company_id"])
        print(f"Anviz API Cloud: user token created: {self.config.ACCOUNT_NAME}")

    def _list_company(self) -> None:
        payload = {}
        url = f"{self.config.API_URL}/{API_LIST_COMPANY}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=self.config.API_TIMEOUT,
        )
        self.company_cloud_id = response.json()["data"][0]["id"]  # company cloud id
        print(f"Anviz API Cloud: company list: {self.company_cloud_id}")

    def _select_company(self) -> None:
        payload = {"id": self.company_cloud_id}
        url = f"{self.config.API_URL}/{API_SELECT_COMPANY}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=self.config.API_TIMEOUT,
        )
        # update token when select company
        self.token = response.json()["data"]["token"]  # JWT token
        print(f"Anviz API Cloud: company select: {self.company_id}")

    def get(self, path: str, **kwargs: Any) -> List:
        raise NotImplementedError

    def post(self, path: str, body: dict = {}) -> dict:
        url = f"{self.config.API_URL}/{path}"
        response = requests.post(
            url=url,
            headers=self.headers,
            data=json.dumps(body),
            timeout=self.config.API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def post_form(self, path: str, fields: dict = {}, files: dict = {}) -> dict:
        headers = {
            "accept": "application/json",
            "x-api-version": "2.0",
            "x-token": self.token,
        }
        url = f"{self.config.API_URL}/{path}"
        response = requests.post(
            url=url,
            headers=headers,
            data=fields,
            files=files,
            timeout=self.config.API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def put(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError

    def patch(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError

    def delete(self, path: str, **kwargs: Any) -> dict:
        raise NotImplementedError
