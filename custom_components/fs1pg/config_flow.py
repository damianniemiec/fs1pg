from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_MAC_ADDR, CONF_IP_ADDR, CONF_DEVICE_NAME, DOMAIN


class Fs1pgConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(
                str(user_input[CONF_MAC_ADDR]), raise_on_progress=False
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC_ADDR): str,
                    vol.Required(CONF_IP_ADDR): str,
                    vol.Required(CONF_DEVICE_NAME): str,
                }
            ),
        )
