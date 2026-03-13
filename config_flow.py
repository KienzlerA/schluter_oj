"""Config flow for Schluter OJ."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OJApiClient, OJApiError, OJAuthenticationError
from .const import (
    CONF_API_KEY,
    CONF_CUSTOMER_ID,
    CONF_HOST,
    DEFAULT_CUSTOMER_ID,
    DEFAULT_HOST,
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_CUSTOMER_ID, default=DEFAULT_CUSTOMER_ID): int,
    }
)


class SchluterOJConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Schluter OJ."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = OJApiClient(
                session=session,
                host=user_input[CONF_HOST],
                api_key=user_input[CONF_API_KEY],
                customer_id=user_input[CONF_CUSTOMER_ID],
            )

            try:
                await api.async_sign_in(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except OJAuthenticationError:
                errors["base"] = "invalid_auth"
            except OJApiError:
                errors["base"] = "cannot_connect"
            else:
                unique_id = f"{user_input[CONF_HOST]}::{user_input[CONF_USERNAME]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )