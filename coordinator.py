"""Coordinator for the Schluter OJ integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OJApiClient, OJApiError, OJAuthenticationError
from .const import DOMAIN, UPDATE_INTERVAL_SECONDS
from .models import OJGroup, OJThermostat, flatten_group_contents

_LOGGER = logging.getLogger(__name__)


class OJDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, Any]]]
):
    """Coordinate OJ API polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OJApiClient,
        username: str,
        password: str,
    ) -> None:
        self.api = api
        self._username = username
        self._password = password

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            if not self.api.session_id:
                await self.api.async_sign_in(self._username, self._password)

            payload = await self.api.async_get_group_contents()
            thermostats, groups = flatten_group_contents(payload)
            return {
                "thermostats": thermostats,
                "groups": groups,
            }

        except OJAuthenticationError:
            try:
                await self.api.async_sign_in(self._username, self._password)
                payload = await self.api.async_get_group_contents()
                thermostats, groups = flatten_group_contents(payload)
                return {
                    "thermostats": thermostats,
                    "groups": groups,
                }
            except OJAuthenticationError as err:
                raise ConfigEntryAuthFailed from err
            except OJApiError as err:
                raise UpdateFailed(str(err)) from err

        except OJApiError as err:
            raise UpdateFailed(str(err)) from err