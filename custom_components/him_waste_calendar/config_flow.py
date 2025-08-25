"""Config flow for the HIM Waste Calendar integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_PROPERTY_ID, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HIM Waste Calendar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_PROPERTY_ID])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_PROPERTY_ID], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required(CONF_PROPERTY_ID): str})
        )
