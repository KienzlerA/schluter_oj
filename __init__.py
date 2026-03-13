"""The Schluter OJ integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OJApiClient
from .const import CONF_API_KEY, CONF_CUSTOMER_ID, CONF_HOST, DOMAIN
from .coordinator import OJDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT]


@dataclass
class OJRuntimeData:
    api: OJApiClient
    coordinator: OJDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    username: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]
    host: str = entry.data[CONF_HOST]
    api_key: str = entry.data[CONF_API_KEY]
    customer_id: int = entry.data[CONF_CUSTOMER_ID]

    session = async_get_clientsession(hass)
    api = OJApiClient(session, host, api_key, customer_id)
    coordinator = OJDataUpdateCoordinator(hass, api, username, password)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = OJRuntimeData(
        api=api,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok