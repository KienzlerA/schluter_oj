"""Models for the Schluter OJ integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any


def _to_celsius(value: int | float | None) -> float | None:
    if value is None:
        return None
    return round(float(value) / 100, 2)


def _parse_clock(value: str) -> time:
    hour, minute, second = value.split(":")
    return time(int(hour), int(minute), int(second))


def _weekday_group_no(dt: datetime) -> int:
    # Python Monday=0..Sunday=6  -> API Monday=1..Sunday=7
    return dt.weekday() + 1


@dataclass(slots=True)
class OJGroup:
    group_id: int
    group_name: str
    regulation_mode: int
    comfort_setpoint: float | None
    manual_mode_setpoint: float | None
    boost_end_time: str | None
    comfort_end_time: str | None
    frost_protection_temperature: float | None
    raw_payload: dict[str, Any]

    @property
    def unique_id(self) -> str:
        return str(self.group_id)

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "OJGroup":
        return cls(
            group_id=payload["GroupId"],
            group_name=payload["GroupName"],
            regulation_mode=int(payload.get("RegulationMode", 0)),
            comfort_setpoint=_to_celsius(payload.get("ComfortSetpoint")),
            manual_mode_setpoint=_to_celsius(payload.get("ManualModeSetpoint")),
            boost_end_time=payload.get("BoostEndTime"),
            comfort_end_time=payload.get("ComfortEndTime"),
            frost_protection_temperature=_to_celsius(
                payload.get("FrostProtectionTemperature")
            ),
            raw_payload=payload,
        )

    @property
    def schedule_days(self) -> list[dict[str, Any]]:
        return self.raw_payload.get("Schedule", {}).get("Days", [])

    def _events_for_today(self, now: datetime) -> list[dict[str, Any]]:
        day_no = _weekday_group_no(now)
        for day in self.schedule_days:
            if int(day.get("WeekDayGrpNo", 0)) == day_no:
                return day.get("Events", [])
        return []

    def _active_schedule_event(self, now: datetime) -> dict[str, Any] | None:
        events = [e for e in self._events_for_today(now) if e.get("Active", False)]
        if not events:
            return None

        current_time = now.time()
        parsed = sorted(events, key=lambda e: _parse_clock(e["Clock"]))

        active_event = None
        for event in parsed:
            if _parse_clock(event["Clock"]) <= current_time:
                active_event = event

        # If current time is before first event, use last event of the day
        if active_event is None:
            active_event = parsed[-1]

        return active_event

    def _next_schedule_event(self, now: datetime) -> dict[str, Any] | None:
        events = [e for e in self._events_for_today(now) if e.get("Active", False)]
        if not events:
            return None

        current_time = now.time()
        parsed = sorted(events, key=lambda e: _parse_clock(e["Clock"]))

        for event in parsed:
            if _parse_clock(event["Clock"]) > current_time:
                return event

        # If no event remains today, return first event tomorrow-ish
        return parsed[0]

    def active_setpoint(self, now: datetime) -> float | None:
        """Current target temperature shown by the app."""
        mode = self.regulation_mode

        # schedule
        if mode == 1:
            event = self._active_schedule_event(now)
            if not event:
                return None
            return _to_celsius(event.get("Temperature"))

        # comfort
        if mode == 2:
            return self.comfort_setpoint

        # boost
        if mode == 8:
            return 40.0

        # eco
        if mode == 9:
            return 14.0

        # fallback manual if ever used
        if self.manual_mode_setpoint:
            return self.manual_mode_setpoint

        return None

    def next_schedule_setpoint(self, now: datetime) -> float | None:
        event = self._next_schedule_event(now)
        if not event:
            return None
        return _to_celsius(event.get("Temperature"))

    def next_schedule_time(self, now: datetime) -> str | None:
        event = self._next_schedule_event(now)
        if not event:
            return None
        return event.get("Clock")

    def current_mode_name(self) -> str:
        if self.regulation_mode == 1:
            return "schedule"
        if self.regulation_mode == 2:
            return "comfort"
        if self.regulation_mode == 8:
            return "boost"
        if self.regulation_mode == 9:
            return "eco"
        return "unknown"

    def should_show_return_to_schedule(self) -> bool:
        return self.regulation_mode != 1

    def boost_remaining(self, now: datetime) -> str | None:
        if self.regulation_mode != 8 or not self.boost_end_time:
            return None

        try:
            end = datetime.fromisoformat(self.boost_end_time)
        except ValueError:
            return None

        delta = end - now
        if delta.total_seconds() <= 0:
            return "00:00:00"

        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def status_text(self, now: datetime) -> str:
        mode = self.current_mode_name()

        if mode == "schedule":
            next_temp = self.next_schedule_setpoint(now)
            next_time = self.next_schedule_time(now)
            if next_temp is not None and next_time:
                return f"Programme actif · Passe à {next_temp:.1f}° à {next_time}"
            return "Programme actif"

        if mode == "boost":
            remaining = self.boost_remaining(now)
            current = self.active_setpoint(now)
            fallback = self.next_schedule_setpoint(now)
            if remaining and fallback is not None:
                return (
                    f"En mode Boost · Passe à {fallback:.1f}° après {remaining}"
                )
            if remaining:
                return f"En mode Boost · Fin dans {remaining}"
            return "En mode Boost"

        if mode == "comfort":
            current = self.active_setpoint(now)
            if current is not None:
                return f"En mode Confort · Consigne {current:.1f}°"
            return "En mode Confort"

        if mode == "eco":
            current = self.active_setpoint(now)
            if current is not None:
                return f"En mode Éco · Consigne {current:.1f}°"
            return "En mode Éco"

        return "Mode inconnu"


@dataclass(slots=True)
class OJThermostat:
    thermostat_id: int
    serial_number: str
    thermostat_name: str
    group_id: int
    group_name: str
    customer_id: int
    sw_version: str

    online: bool
    heating: bool
    open_window: bool

    room_temperature: float | None
    floor_temperature: float | None

    regulation_mode: int
    comfort_setpoint: float | None
    manual_mode_setpoint: float | None
    min_setpoint: float | None
    max_setpoint: float | None

    sensor_appl: int | None
    floor_type: int | None
    adaptive_mode: bool
    vacation_enabled: bool
    last_primary_mode_is_auto: bool

    @property
    def unique_id(self) -> str:
        return self.serial_number

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "OJThermostat":
        return cls(
            thermostat_id=payload["Id"],
            serial_number=str(payload["SerialNumber"]),
            thermostat_name=payload["ThermostatName"],
            group_id=payload["GroupId"],
            group_name=payload["GroupName"],
            customer_id=payload["CustomerId"],
            sw_version=payload.get("SWversion", ""),
            online=bool(payload.get("Online", False)),
            heating=bool(payload.get("Heating", False)),
            open_window=bool(payload.get("OpenWindow", False)),
            room_temperature=_to_celsius(payload.get("RoomTemperature")),
            floor_temperature=_to_celsius(payload.get("FloorTemperature")),
            regulation_mode=int(payload.get("RegulationMode", 0)),
            comfort_setpoint=_to_celsius(payload.get("ComfortSetpoint")),
            manual_mode_setpoint=_to_celsius(payload.get("ManualModeSetpoint")),
            min_setpoint=_to_celsius(payload.get("MinSetpoint")),
            max_setpoint=_to_celsius(payload.get("MaxSetpoint")),
            sensor_appl=payload.get("SensorAppl"),
            floor_type=payload.get("FloorType"),
            adaptive_mode=bool(payload.get("AdaptiveMode", False)),
            vacation_enabled=bool(payload.get("VacationEnabled", False)),
            last_primary_mode_is_auto=bool(payload.get("LastPrimaryModeIsAuto", False)),
        )


def flatten_group_contents(
    data: dict[str, Any],
) -> tuple[dict[str, OJThermostat], dict[str, OJGroup]]:
    thermostats: dict[str, OJThermostat] = {}
    groups: dict[str, OJGroup] = {}

    for group_payload in data.get("GroupContents", []):
        group = OJGroup.from_api(group_payload)
        groups[group.unique_id] = group

        for thermostat_payload in group_payload.get("Thermostats", []):
            thermostat = OJThermostat.from_api(thermostat_payload)
            thermostats[thermostat.unique_id] = thermostat

    return thermostats, groups