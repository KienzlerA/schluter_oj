"""Base entity for Schluter OJ."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import OJDataUpdateCoordinator


class OJEntity(CoordinatorEntity[OJDataUpdateCoordinator]):
    def __init__(self, coordinator: OJDataUpdateCoordinator, thermostat_id: str) -> None:
        super().__init__(coordinator)
        self._thermostat_id = thermostat_id

    @property
    def thermostat(self):
        return self.coordinator.data["thermostats"][self._thermostat_id]

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.thermostat.online

    @property
    def device_info(self):
        return {
            "identifiers": {("schluter_oj", self.thermostat.unique_id)},
            "name": self.thermostat.thermostat_name,
            "manufacturer": "Schluter / OJ Electronics",
            "model": "DITRA-HEAT / OWD5",
            "sw_version": self.thermostat.sw_version,
        }


class OJGroupEntity(CoordinatorEntity[OJDataUpdateCoordinator]):
    def __init__(self, coordinator: OJDataUpdateCoordinator, group_id: str) -> None:
        super().__init__(coordinator)
        self._group_id = group_id

    @property
    def group(self):
        return self.coordinator.data["groups"][self._group_id]

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return {
            "identifiers": {("schluter_oj_group", self.group.unique_id)},
            "name": self.group.group_name,
            "manufacturer": "Schluter / OJ Electronics",
            "model": "DITRA-HEAT Group",
        }