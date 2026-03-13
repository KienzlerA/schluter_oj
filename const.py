"""Constants for the Schluter OJ integration."""

from __future__ import annotations

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

MODE_TO_NAME = {
    REGULATION_MODE_SCHEDULE: "schedule",
    REGULATION_MODE_COMFORT: "comfort",
    REGULATION_MODE_BOOST: "boost",
    REGULATION_MODE_ECO: "eco",
}

NAME_TO_MODE = {value: key for key, value in MODE_TO_NAME.items()}