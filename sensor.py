"""Sensors for Schluter OJ."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OJRuntimeData
from .const import DOMAIN, MODE_TO_NAME
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
                OJRoomTemperatureSensor(data.coordinator, thermostat_id),
                OJFloorTemperatureSensor(data.coordinator, thermostat_id),
                OJComfortSetpointSensor(data.coordinator, thermostat_id),
                OJManualSetpointSensor(data.coordinator, thermostat_id),
                OJRegulationModeSensor(data.coordinator, thermostat_id),
            ]
        )

    for group_id in group_ids:
        entities.extend(
            [
                OJGroupActiveSetpointSensor(data.coordinator, group_id),
                OJGroupModeSensor(data.coordinator, group_id),
                OJGroupNextSetpointSensor(data.coordinator, group_id),
                OJGroupNextEventTimeSensor(data.coordinator, group_id),                
                OJGroupStatusTextSensor(data.coordinator, group_id),
                OJGroupBoostCountdownSensor(data.coordinator, group_id),
            ]
        )

    async_add_entities(entities)


class _BaseTempSensor(OJEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class OJRoomTemperatureSensor(_BaseTempSensor):
    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_room_temperature"
        self._attr_name = f"{self.thermostat.thermostat_name} Room Temperature"

    @property
    def native_value(self):
        return self.thermostat.room_temperature


class OJFloorTemperatureSensor(_BaseTempSensor):
    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_floor_temperature"
        self._attr_name = f"{self.thermostat.thermostat_name} Floor Temperature"

    @property
    def native_value(self):
        return self.thermostat.floor_temperature


class OJComfortSetpointSensor(_BaseTempSensor):
    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_comfort_setpoint"
        self._attr_name = f"{self.thermostat.thermostat_name} Comfort Setpoint"

    @property
    def native_value(self):
        return self.thermostat.comfort_setpoint


class OJManualSetpointSensor(_BaseTempSensor):
    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_manual_setpoint"
        self._attr_name = f"{self.thermostat.thermostat_name} Manual Setpoint"

    @property
    def native_value(self):
        return self.thermostat.manual_mode_setpoint


class OJRegulationModeSensor(OJEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, thermostat_id: str) -> None:
        super().__init__(coordinator, thermostat_id)
        self._attr_unique_id = f"{self.thermostat.unique_id}_regulation_mode"
        self._attr_name = f"{self.thermostat.thermostat_name} Regulation Mode"
        self._attr_icon = "mdi:thermostat"

    @property
    def native_value(self):
        return self.thermostat.regulation_mode

    @property
    def extra_state_attributes(self):
        return {
            "group_name": self.thermostat.group_name,
            "group_id": self.thermostat.group_id,
            "sensor_appl": self.thermostat.sensor_appl,
            "floor_type": self.thermostat.floor_type,
            "adaptive_mode": self.thermostat.adaptive_mode,
            "vacation_enabled": self.thermostat.vacation_enabled,
            "last_primary_mode_is_auto": self.thermostat.last_primary_mode_is_auto,
            "min_setpoint": self.thermostat.min_setpoint,
            "max_setpoint": self.thermostat.max_setpoint,
        }


class _BaseGroupTempSensor(OJGroupEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class OJGroupActiveSetpointSensor(_BaseGroupTempSensor):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_active_setpoint"
        self._attr_name = f"{self.group.group_name} Active Setpoint"

    @property
    def native_value(self):
        return self.group.active_setpoint(datetime.now())

    @property
    def extra_state_attributes(self):
        return {
            "mode": MODE_TO_NAME.get(self.group.regulation_mode, "unknown"),
            "boost_end_time": self.group.boost_end_time,
            "comfort_end_time": self.group.comfort_end_time,
        }


class OJGroupModeSensor(OJGroupEntity, SensorEntity):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_group_mode"
        self._attr_name = f"{self.group.group_name} Mode"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self):
        return MODE_TO_NAME.get(self.group.regulation_mode, "unknown")


class OJGroupNextSetpointSensor(_BaseGroupTempSensor):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_next_setpoint"
        self._attr_name = f"{self.group.group_name} Next Setpoint"

    @property
    def native_value(self):
        return self.group.next_schedule_setpoint(datetime.now())


class OJGroupNextEventTimeSensor(OJGroupEntity, SensorEntity):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_next_event_time"
        self._attr_name = f"{self.group.group_name} Next Event Time"
        self._attr_icon = "mdi:clock-outline"

    @property
    def native_value(self):
        return self.group.next_schedule_time(datetime.now())

class OJGroupStatusTextSensor(OJGroupEntity, SensorEntity):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_status_text"
        self._attr_name = f"{self.group.group_name} Status"
        self._attr_icon = "mdi:text"

    @property
    def native_value(self):
        return self.group.status_text(datetime.now())


class OJGroupBoostCountdownSensor(OJGroupEntity, SensorEntity):
    def __init__(self, coordinator, group_id: str) -> None:
        super().__init__(coordinator, group_id)
        self._attr_unique_id = f"{self.group.unique_id}_boost_countdown"
        self._attr_name = f"{self.group.group_name} Boost Countdown"
        self._attr_icon = "mdi:timer-outline"

    @property
    def native_value(self):
        return self.group.boost_remaining(datetime.now())