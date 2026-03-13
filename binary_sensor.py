"""Binary sensors for Schluter OJ."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OJRuntimeData
from .const import DOMAIN
from .entity import OJEntity, OJGroupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data: OJRuntimeData = hass.data[DOMAIN][entry.entry_id]
    thermostat_ids = list(data.coordinator.data["thermostats"].keys())
    group_ids = list(data.coordinator.data["groups"].keys())

    entities = []
    for thermostat_id in thermostat_ids:
        entities.extend(
            [
                OJOnlineBinarySensor(data.coordinator, thermostat_id),
                OJHeatingBinarySensor(data.coordinator, thermostat_id),
                OJOpenWindowBinarySensor(data.coordinator, thermostat_id),
            ]
        )
    
    for group_id in group_ids:
        entities.append(
            OJGroupReturnToScheduleBinarySensor(data.coordinator, group_id)
        )

    async_add_entities(entities)


class OJOnlineBinarySensor(OJEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_online"
        self._attr_name = f"{self.thermostat.thermostat_name} Online"

    @property
    def is_on(self):
        return self.thermostat.online


class OJHeatingBinarySensor(OJEntity, BinarySensorEntity):
    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_heating"
        self._attr_name = f"{self.thermostat.thermostat_name} Heating"
        self._attr_icon = "mdi:radiator"

    @property
    def is_on(self):
        return self.thermostat.heating


class OJOpenWindowBinarySensor(OJEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.WINDOW

    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_open_window"
        self._attr_name = f"{self.thermostat.thermostat_name} Open Window"

    @property
    def is_on(self):
        return self.thermostat.open_window

class OJGroupReturnToScheduleBinarySensor(OJGroupEntity, BinarySensorEntity):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_show_return_to_schedule"
        self._attr_name = f"{self.group.group_name} Show Return To Schedule"
        self._attr_icon = "mdi:calendar-refresh"

    @property
    def is_on(self):
        return self.group.should_show_return_to_schedule()