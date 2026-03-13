"""Config flow for Zwift integration."""

import logging
import sys

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME

from .const import CONF_INCLUDE_SELF, CONF_PLAYERS, DOMAIN

# Patch zwift protobuf
from .zwift_patch import zwift_messages_pb2 as new_pb2

sys.modules["zwift.zwift_messages_pb2"] = new_pb2

from zwift import Client as ZwiftClient

_LOGGER = logging.getLogger(__name__)


class ZwiftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zwift."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            # Validate credentials
            try:
                client = ZwiftClient(username, password)
                token = await self.hass.async_add_executor_job(
                    client.auth_token.fetch_token_data
                )
                if "error" in token:
                    errors["base"] = "invalid_auth"
                else:
                    # Parse players list from comma-separated string
                    players_str = user_input.get(CONF_PLAYERS, "")
                    players = [
                        p.strip() for p in players_str.split(",") if p.strip()
                    ]
                    user_input[CONF_PLAYERS] = players

                    await self.async_set_unique_id(username.lower())
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Zwift ({username})",
                        data=user_input,
                    )
            except Exception:
                _LOGGER.exception("Error connecting to Zwift")
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_PLAYERS, default=""): str,
                vol.Optional(CONF_INCLUDE_SELF, default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_data):
        """Handle import from YAML configuration."""
        # Convert players list to comma-separated for unique_id check
        username = import_data[CONF_USERNAME]
        await self.async_set_unique_id(username.lower())
        self._abort_if_unique_id_configured()

        # Ensure players is a list
        players = import_data.get(CONF_PLAYERS, [])
        if isinstance(players, str):
            players = [p.strip() for p in players.split(",") if p.strip()]
        import_data[CONF_PLAYERS] = players

        return self.async_create_entry(
            title=f"Zwift ({username})",
            data=import_data,
        )
