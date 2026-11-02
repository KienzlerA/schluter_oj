"""Constants for the Schluter OJ integration."""

from __future__ import annotations

from datetime import datetime, timedelta

DOMAIN = "schluter_oj"

CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_CUSTOMER_ID = "customer_id"

DEFAULT_HOST = "owd5-sl003-app.ojelectronics.com"
DEFAULT_CUSTOMER_ID = 3

UPDATE_INTERVAL_SECONDS = 60
CLIENT_SW_VERSION = 1

REGULATION_MODE_SCHEDULE = 1
REGULATION_MODE_COMFORT = 2
REGULATION_MODE_BOOST = 8
REGULATION_MODE_ECO = 9

# OJ reverts Comfort to the week schedule when ComfortEndTime is the sentinel
# 1900-01-01. Microline uses 4 h; night setback and day-away need longer.
COMFORT_DURATION_MINUTES = 24 * 60


def format_comfort_end_time(now: datetime) -> str:
    """API expects local wall time without timezone suffix."""
    end = now + timedelta(minutes=COMFORT_DURATION_MINUTES)
    return end.strftime("%Y-%m-%dT%H:%M:%S")

MODE_TO_NAME = {
    REGULATION_MODE_SCHEDULE: "schedule",
    REGULATION_MODE_COMFORT: "comfort",
    REGULATION_MODE_BOOST: "boost",
    REGULATION_MODE_ECO: "eco",
}

NAME_TO_MODE = {value: key for key, value in MODE_TO_NAME.items()}
