"""Select entities for Schluter OJ group modes."""

from __future__ import annotations

from copy import deepcopy

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OJRuntimeData
from .const import DOMAIN, MODE_TO_NAME, NAME_TO_MODE
from .entity import OJGroupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data: OJRuntimeData = hass.data[DOMAIN][entry.entry_id]
    group_ids = list(data.coordinator.data["groups"].keys())

    async_add_entities(
        OJGroupModeSelect(data, group_id) for group_id in group_ids
    )


class OJGroupModeSelect(OJGroupEntity, SelectEntity):
    _attr_options = ["schedule", "comfort", "boost", "eco"]
    _attr_icon = "mdi:thermostat-auto"

    def __init__(self, data: OJRuntimeData, group_id: str) -> None:
        super().__init__(data.coordinator, group_id)
        self._runtime_data = data
        self._attr_unique_id = f"{self.group.unique_id}_group_mode"
        self._attr_name = f"{self.group.group_name} Mode"

    @property
    def current_option(self) -> str | None:
        return MODE_TO_NAME.get(self.group.regulation_mode)

    async def async_select_option(self, option: str) -> None:
        mode = NAME_TO_MODE[option]

        updated_group = deepcopy(self.group.raw_payload)
        updated_group["RegulationMode"] = mode

        await self._runtime_data.api.async_update_group(updated_group)
        await self.coordinator.async_request_refresh()