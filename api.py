"""Async API client for the Schluter OJ backend."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import CLIENT_SW_VERSION

_LOGGER = logging.getLogger(__name__)


class OJApiError(Exception):
    """Generic OJ API error."""


class OJAuthenticationError(OJApiError):
    """Authentication failed."""


class OJApiClient:
    def __init__(
        self,
        session: ClientSession,
        host: str,
        api_key: str,
        customer_id: int,
    ) -> None:
        self._session = session
        self._host = host
        self._api_key = api_key
        self._customer_id = customer_id
        self._session_id: str | None = None

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def base_url(self) -> str:
        return f"https://{self._host}"

    async def async_sign_in(self, username: str, password: str) -> str:
        url = f"{self.base_url}/api/UserProfile/SignIn"
        payload = {
            "APIKEY": self._api_key,
            "CustomerId": str(self._customer_id),
            "UserName": username,
            "ClientSWVersion": str(CLIENT_SW_VERSION),
            "Password": password,
        }

        try:
            async with self._session.post(url, data=payload, timeout=15) as response:
                response.raise_for_status()
                data = await response.json()
        except ClientError as err:
            raise OJApiError(f"Unable to sign in: {err}") from err

        error_code = int(data.get("ErrorCode", -1))
        if error_code != 0:
            raise OJAuthenticationError(
                f"Authentication failed with ErrorCode={error_code}"
            )

        session_id = data.get("SessionId")
        if not session_id:
            raise OJAuthenticationError("No SessionId returned by API")

        self._session_id = session_id
        return session_id

    async def async_get_group_contents(self) -> dict[str, Any]:
        if not self._session_id:
            raise OJAuthenticationError("No active session id")

        url = f"{self.base_url}/api/Group/GroupContents"
        params = {
            "APIKEY": self._api_key,
            "sessionid": self._session_id,
        }

        try:
            async with self._session.get(url, params=params, timeout=15) as response:
                response.raise_for_status()
                data = await response.json()
        except ClientError as err:
            raise OJApiError(f"Unable to fetch group contents: {err}") from err

        error_code = int(data.get("ErrorCode", -1))
        if error_code != 0:
            raise OJApiError(f"GroupContents failed with ErrorCode={error_code}")

        return data

    async def async_update_group(self, group_payload: dict[str, Any]) -> dict[str, Any]:
        if not self._session_id:
            raise OJAuthenticationError("No active session id")

        url = f"{self.base_url}/api/Group/UpdateGroup"
        params = {
            "sessionid": self._session_id,
        }
        payload = {
            "APIKEY": self._api_key,
            "SetGroup": group_payload,
        }

        try:
            async with self._session.post(
                url,
                params=params,
                json=payload,
                timeout=15,
            ) as response:
                response.raise_for_status()
                data = await response.json()
        except ClientError as err:
            raise OJApiError(f"Unable to update group: {err}") from err

        error_code = int(data.get("ErrorCode", -1))
        if error_code != 0:
            raise OJApiError(f"UpdateGroup failed with ErrorCode={error_code}")

        return data